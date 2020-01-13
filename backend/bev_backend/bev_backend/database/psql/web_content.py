import logging
import asyncio
import asyncpg
from datetime import datetime
from datetime import timedelta
from bev_backend.database.psql.common import run_query



score_query_base= '''
WITH latter_window AS (
    SELECT
        lwb.entity_id AS entity_id,
        lwb.twt_cnt AS twt_cnt,
        lwb.acc_cnt AS acc_cnt,
        lwb.mean_bs AS mean_bs,
        lwb.last_tid AS last_tid,
        lwb.last_seen AS last_seen,
        tj.tweet->'extended_entities'->'media'->0->>'media_url' AS media_link,
        ety.entity_type As entity_type,
        ety.entity_text AS entity_text
    FROM (
        SELECT
            et.entity_id AS entity_id,
            COUNT(et.tid) AS twt_cnt,
            COUNT(DISTINCT et.user_id) AS acc_cnt,
            AVG(et.bot_score::decimal) AS mean_bs,
            MAX(et.tid) AS last_tid,
            MAX(et.tweet_date) AS last_seen
        FROM entitytwt et
        WHERE
            et.tweet_date BETWEEN
                ({ref_time}-INTERVAL '{interval_value} {interval_unit}')::timestamp AND
                {ref_time}::timestamp
        GROUP BY et.entity_id
    ) lwb
        INNER JOIN twtjson tj ON lwb.last_tid=tj.tid
        INNER JOIN entity ety ON lwb.entity_id=ety.entity_id
)
SELECT
    entity_id AS entity_id,
    entity_type As entity_type,
    entity_text AS entity_text,
    last_seen AS last_seen,
    media_link AS media_link,
    acc_cnt AS acc_cnt,
    twt_cnt AS twt_cnt,
    trend AS trend,
    mean_bs AS mean_bs,
    1.0/(
       1.0+exp(
          -1.0*(
              1.91356533*(1.0 - trend_rank/max(trend_rank) over ()) +
              2.8811564*(1.0 - twt_cnt_rank/max(twt_cnt_rank) over ()) +
              7.09627534*(1.0 - mean_bs_rank/max(mean_bs_rank) over ()) -
              0.0889277*(1.0 - norm_usr_cnt_rank/max(norm_usr_cnt_rank) over ()) -
              10.3836869
          )
       )
    ) AS coord_score
FROM (
    SELECT
        entity_id AS entity_id,
        entity_type As entity_type,
        entity_text AS entity_text,
        last_seen AS last_seen,
        media_link AS media_link,
        acc_cnt AS acc_cnt,
        twt_cnt AS twt_cnt,
        trend AS trend,
        mean_bs AS mean_bs,
        RANK() OVER (ORDER BY bm.twt_cnt DESC) - 1.0 AS twt_cnt_rank,
        RANK() OVER (ORDER BY bm.norm_usr_cnt DESC) - 1.0 AS norm_usr_cnt_rank,
        RANK() OVER (ORDER BY bm.trend DESC) - 1.0 AS trend_rank,
        RANK() OVER (ORDER BY bm.mean_bs DESC) - 1.0 AS mean_bs_rank
    FROM (
        SELECT
            lw.entity_id AS entity_id,
            lw.entity_type As entity_type,
            lw.entity_text AS entity_text,
            lw.last_seen::timestamp AS last_seen,
            lw.media_link AS media_link,
            lw.acc_cnt AS acc_cnt,
            lw.twt_cnt AS twt_cnt,
            (lw.acc_cnt::decimal+1.0) / (lw.twt_cnt::decimal+1.0) AS norm_usr_cnt,
            CASE WHEN fw.twt_cnt IS NULL
                THEN lw.twt_cnt::decimal+1.0
                ELSE (lw.twt_cnt::decimal+1.0) / (fw.twt_cnt::decimal+1.0)
            END AS trend,
            lw.mean_bs AS mean_bs
        FROM latter_window lw
        LEFT JOIN (
            SELECT
                entity_id AS entity_id,
                COUNT(tid) AS twt_cnt
            FROM entitytwt
            WHERE
                entitytwt.tweet_date BETWEEN
            ({ref_time}-INTERVAL '{double_interval_value} {interval_unit}')::timestamp AND
            ({ref_time}-INTERVAL '{interval_value} {interval_unit}')::timestamp
            GROUP BY entity_id
        ) fw ON fw.entity_id=lw.entity_id
    ) bm
) rank_metrics
ORDER BY coord_score DESC LIMIT {nrows};
'''
async def coord_score_fetching(conn, format_dict):
    score_query = score_query_base.format(**format_dict)
    return await conn.fetch(score_query)

def get_coord_score_report(ref_time,
            interval_value=4, interval_unit='hours', nrows=1000):
    format_dict = {
        'ref_time'      : "(TIMESTAMP '%s')" % ref_time,
        'interval_unit' : interval_unit,
        'interval_value': interval_value,
        'double_interval_value': 2*interval_value,
        'nrows' : nrows
    }
    conn_args = { 'timeout': 60, 'command_timeout': 20 }

    try:
        results = asyncio.run(
            run_query(coord_score_fetching, {'format_dict': format_dict}, conn_args=conn_args)
        )
    except asyncpg.exceptions.DivisionByZeroError as e:
        # pass the error upward
        raise e
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching coord scores")
        logging.error("query args : {}".format(format_dict))
        raise e
    return results


hoaxy_query = '''
WITH arranged_info AS (
    SELECT
        tid AS tid,
        CASE
            WHEN retweeted_id IS NOT NULL
                THEN retweeted_id::bigint
            WHEN quote_user IS NOT NULL
                THEN quote_user::bigint
            ELSE true_user_id::bigint
        END AS from_user_id,
        CASE
            WHEN retweeted_screenname IS NOT NULL
                THEN retweeted_screenname
            WHEN quote_screenname IS NOT NULL
                THEN quote_screenname
            ELSE user_screenname
        END AS from_user_screenname,
        CASE
            WHEN quote_user IS NOT NULL OR retweeted_id IS NOT NULL
                THEN true_user_id::bigint
            WHEN reply_user IS NOT NULL
                THEN reply_user::bigint
            ELSE true_user_id::bigint
        END AS to_user_id,
        CASE
            WHEN quote_screenname IS NOT NULL OR retweeted_screenname IS NOT NULL
                THEN user_screenname
            WHEN reply_user IS NOT NULL
                THEN reply_screenname
            ELSE user_screenname
        END AS to_user_screenname,
        CASE
            WHEN retweeted_id IS NOT NULL
                THEN 'retweet'
            WHEN quote_user IS NOT NULL
                THEN 'quote'
            WHEN reply_user IS NOT NULL
                THEN 'reply'
            ELSE 'origin'
        END AS tweet_type
    FROM (
        SELECT
            nt.tid AS tid,
            t.tweet->'user'->>'id' AS true_user_id,
            t.tweet->'user'->>'screen_name' AS user_screenname,
            t.tweet->'retweeted_status'->'user'->>'id' AS retweeted_id,
            t.tweet->'retweeted_status'->'user'->>'screen_name' AS retweeted_screenname,
            t.tweet->>'in_reply_to_user_id' AS reply_user,
            t.tweet->>'in_reply_to_screen_name' AS reply_screenname,
            t.tweet->'quoted_status'->'user'->>'id' AS quote_user,
            t.tweet->'quoted_status'->'user'->>'screen_name' AS quote_screenname
        FROM (
                SELECT
                    DISTINCT tid AS tid
                FROM entitytwt
                    WHERE
                        ({entitytwt_entity_id_matching_str}) AND
                        tweet_date BETWEEN
                           ({ref_time}-INTERVAL '{interval_value} {interval_unit}')::timestamp AND
                           {ref_time}::timestamp
        ) nt LEFT JOIN twtjson t ON nt.tid=t.tid
    )tweet_info
)
SELECT
    ai.tid::text AS tid,
    ai.tweet_type AS tweet_type,
    from_user_et.tweet_date AS tweet_date,
    ai.from_user_id::text AS from_user_id,
    ai.from_user_screenname AS from_user_screenname,
    from_user_et.bot_score AS from_user_botscore,
    ai.to_user_id::text AS to_user_id,
    ai.to_user_screenname AS to_user_screenname,
    to_user_et.bot_score AS to_user_botscore
FROM arranged_info ai
    INNER JOIN entitytwt from_user_et
        ON
            ai.tid=from_user_et.tid AND
            ai.from_user_id=from_user_et.user_id
    INNER JOIN entitytwt to_user_et
        ON
            ai.tid=to_user_et.tid AND
            ai.to_user_id=to_user_et.user_id
WHERE
    ({from_user_et_entity_id_matching_str}) AND
    ({to_user_et_entity_id_matching_str});
'''

async def hoaxy_fetching(conn, format_dict):
    formatted_hoaxy_query = hoaxy_query.format(**format_dict)
    return await conn.fetch(formatted_hoaxy_query)

def get_hoaxy_data(entity_ids, ref_time, interval_value=4, interval_unit='hours'):
    format_dict = {
        'entitytwt_entity_id_matching_str'    :
            ' OR '.join(['entitytwt.entity_id=%s' % eid for eid in entity_ids]),
        'from_user_et_entity_id_matching_str' :
            ' OR '.join(['from_user_et.entity_id=%s' % eid for eid in entity_ids]),
        'to_user_et_entity_id_matching_str' :
            ' OR '.join(['to_user_et.entity_id=%s' % eid for eid in entity_ids]),
        'ref_time'              : "(TIMESTAMP '%s')" % ref_time,
        'interval_unit'         : interval_unit,
        'interval_value'        : interval_value
    }
    conn_args = { 'timeout': 60, 'command_timeout': 20 }

    try:
        results = asyncio.run(
            run_query(hoaxy_fetching, {'format_dict': format_dict}, conn_args=conn_args)
        )
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching hoaxy data")
        logging.error("query args : {}".format(format_dict))
        return None
    return results




score_query_extended_base= '''
SELECT
    entity_id, tid, user_id, tweet_date
FROM entitytwt
WHERE
    tweet_date BETWEEN
        (NOW()-INTERVAL '{double_interval_value} {interval_unit}')::timestamp AND
        NOW()::timestamp
    AND
    entity_id={target_entity_id};
'''
async def coord_score_fetching_extended(conn, target_entity_ids, format_dict):
    output = dict()
    for target_entity_id in target_entity_ids:
        format_dict['target_entity_id'] = target_entity_id
        score_query_extended = score_query_extended_base.format(**format_dict)
        output[target_entity_id] = await conn.fetch(score_query_extended)
    return output


def get_coord_score_report_extended(target_entity_ids,
        interval_value=4, interval_unit='hours'):
    format_dict = {
        'interval_unit' : interval_unit,
        'double_interval_value': 2*interval_value
    }
    args = {
        'target_entity_ids': target_entity_ids,
        'format_dict'      : format_dict
    }
    conn_args = { 'timeout': 60, 'command_timeout': 20 }

    try:
        results = asyncio.run(
            run_query(coord_score_fetching_extended, args, conn_args=conn_args)
        )
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching coord scores extension")
        logging.error("query args : {}".format(target_entities))
        return None
    return results



async def entity_count_fetch(conn, format_dict):
    return await conn.fetchval('''
SELECT COUNT( DISTINCT entity_id ) FROM entitytwt
    WHERE tweet_date BETWEEN
        (NOW()-INTERVAL '{double_interval_value} {interval_unit}')::timestamp AND
        NOW()::timestamp
    '''.format(**format_dict))

def get_entity_count(interval_value=4, interval_unit='hours'):
    format_dict = {
        'interval_unit' : interval_unit,
        'double_interval_value': 2*interval_value
    }
    conn_args = { 'timeout': 60, 'command_timeout': 20 }

    try:
        results = asyncio.run(
            run_query(entity_count_fetch, {'format_dict': format_dict}, conn_args=conn_args)
        )
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching entity count")
        return None
    return results


async def timeline_fetch(conn, format_dict):
    return await conn.fetch('''
WITH former_window AS (
    SELECT
        entity_id AS entity_id,
        COUNT(tid) AS twt_cnt
    FROM entitytwt
    WHERE
        entitytwt.tweet_date BETWEEN
            ({ref_time}-INTERVAL '{double_interval_value} {interval_unit}')::timestamp AND
            ({ref_time}-INTERVAL '{interval_value} {interval_unit}')::timestamp
        AND ({entity_id_matching_str})
    GROUP BY entity_id
), latter_window AS (
    SELECT
        entity_id AS entity_id,
        COUNT(tid) AS twt_cnt,
        COUNT(DISTINCT user_id) AS acc_cnt,
        AVG(bot_score::decimal) AS mean_bs,
        MAX(tid) AS last_tid,
        MAX(tweet_date) AS last_seen
    FROM entitytwt
    WHERE
        entitytwt.tweet_date BETWEEN
            ({ref_time}-INTERVAL '{interval_value} {interval_unit}')::timestamp AND
            {ref_time}::timestamp
        AND ({entity_id_matching_str})
    GROUP BY entity_id
), basic_metrics AS (
    SELECT
        lw.entity_id AS entity_id,
        lw.twt_cnt AS twt_cnt,
        (lw.acc_cnt::decimal+1.0) / (lw.twt_cnt::decimal+1.0) AS norm_usr_cnt,
        CASE WHEN fw.twt_cnt IS NULL
            THEN lw.twt_cnt::decimal+1.0
            ELSE (lw.twt_cnt::decimal+1.0) / (fw.twt_cnt::decimal+1.0)
        END AS trend,
        lw.mean_bs AS mean_bs
    FROM latter_window lw
    LEFT JOIN former_window fw ON fw.entity_id=lw.entity_id
)
SELECT
    bm.entity_id AS entity_id,
    bm.twt_cnt AS twt_cnt,
    lw.acc_cnt AS acc_cnt,
    bm.trend AS trend,
    bm.mean_bs AS mean_bs
FROM latter_window lw
    INNER JOIN basic_metrics bm ON lw.entity_id=bm.entity_id
    '''.format(**format_dict))


def get_timeline(entity_ids, ref_time, interval_value=4, interval_unit='hours'):
    format_dict = {
        'entity_id_matching_str':
            ' OR '.join(['entity_id=%s' % eid for eid in entity_ids]),
        'interval_unit' : interval_unit,
        'interval_value': interval_value,
        'double_interval_value': 2*interval_value
    }
    conn_args = { 'timeout': 60, 'command_timeout': 20 }

    results = dict()
    try:
        for i in range(25): # past 24 hours
            data_point_time = ref_time - timedelta(hours=i)
            # force hourly data points
            data_point_time = data_point_time.replace(minute=0, second=0, microsecond=0)
            data_point_time = datetime.strftime(data_point_time, '%Y-%m-%d %H:%M:%S')

            ref_time_str = "(TIMESTAMP '%s')" % data_point_time
            format_dict['ref_time'] = ref_time_str

            hour_stats = asyncio.run(
                run_query(timeline_fetch, {'format_dict': format_dict}, conn_args=conn_args)
            )
            num_hour_stats = len(hour_stats)
            if num_hour_stats > 0:
                for stat in range(num_hour_stats):
                    record = hour_stats[stat]
                    line_stats = results.get(data_point_time, list())
                    line_stats.append({
                        'twt_cnt': record['twt_cnt'],
                        'acc_cnt': record['acc_cnt'],
                        'trend'  : (float)(record['trend']),
                        'mean_bs': (float)(record['mean_bs'])
                    })
                    results[data_point_time] = line_stats
            elif num_hour_stats == 0:
                # sparsity in data
                results[data_point_time] = None
            else:
                raise ValueError("timeline_fetch returned more than one entity")

    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching timeline")
        logging.error("query args : {}".format(format_dict))
        raise e
    return results
