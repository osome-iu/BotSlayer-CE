import logging
import asyncio
import asyncpg
from bev_backend.database.psql.common import singleton_query



score_query_base= '''
WITH former_window AS (
    SELECT
        entity_id AS entity_id,
        COUNT(tid) AS twt_cnt
    FROM entitytwt
    WHERE
        entitytwt.tweet_date BETWEEN
            (NOW()-INTERVAL '{double_interval_value} {interval_unit}')::timestamp AND
            (NOW()-INTERVAL '{interval_value} {interval_unit}')::timestamp
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
            (NOW()-INTERVAL '{interval_value} {interval_unit}')::timestamp AND
            NOW()::timestamp
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
), rank_metrics AS (
    SELECT
        bm.entity_id AS entity_id,
        RANK() OVER (ORDER BY bm.twt_cnt DESC) - 1.0 AS twt_cnt_rank,
        RANK() OVER (ORDER BY bm.norm_usr_cnt DESC) - 1.0 AS norm_usr_cnt_rank,
        RANK() OVER (ORDER BY bm.trend DESC) - 1.0 AS trend_rank,
        RANK() OVER (ORDER BY bm.mean_bs DESC) - 1.0 AS mean_bs_rank
    FROM basic_metrics bm
), coord_rank_max AS (
    SELECT
        MAX(rm.trend_rank) AS max_trend_rank,
        MAX(rm.twt_cnt_rank) AS max_twt_cnt_rank,
        MAX(rm.mean_bs_rank) AS max_mean_bs_rank,
        MAX(rm.norm_usr_cnt_rank) AS max_norm_usr_cnt_rank
    FROM rank_metrics rm
), coord_rank_metrics AS (
    SELECT
        rm.entity_id AS entity_id,
        10.0*(1.0 - rm.trend_rank/crmax.max_trend_rank) +
          10.0*(1.0 - rm.twt_cnt_rank/crmax.max_twt_cnt_rank) +
          10.0*(1.0 - rm.mean_bs_rank/crmax.max_mean_bs_rank) +
          1.0*(1.0 - rm.norm_usr_cnt_rank/crmax.max_norm_usr_cnt_rank) -
          20.0 AS coord_rank_sum
    FROM rank_metrics rm, coord_rank_max crmax
), coord_score_metrics AS (
    SELECT
        crm.entity_id AS entity_id,
        1.0/(1.0+exp(-1.0*crm.coord_rank_sum)) AS coord_score
    FROM coord_rank_metrics crm
)
SELECT
    lw.last_seen::timestamp with time zone AS last_seen,
    ety.entity_type As entity_type,
    ety.entity_text AS entity_text,
    bm.twt_cnt AS twt_cnt,
    lw.acc_cnt AS acc_cnt,
    bm.trend AS trend,
    bm.mean_bs AS mean_bs,
    csm.coord_score AS coord_score,
    RANK() OVER (ORDER BY csm.coord_score DESC) AS coord_score_rank,
    tj.tweet->'extended_entities'->'media'->0->>'media_url' AS media_link
FROM latter_window lw
    INNER JOIN entity ety ON lw.entity_id=ety.entity_id
    INNER JOIN basic_metrics bm ON lw.entity_id=bm.entity_id
    INNER JOIN rank_metrics rm ON lw.entity_id=rm.entity_id
    INNER JOIN coord_score_metrics csm ON lw.entity_id=csm.entity_id
    INNER JOIN twtjson tj ON lw.last_tid=tj.tid
ORDER BY coord_score DESC LIMIT {nrows};
'''


async def coord_score_fetching(conn, format_dict):
    score_query = score_query_base.format(**format_dict)
    return await conn.fetch(score_query)


def get_coord_score_report(interval_value=4, interval_unit='hours',
            nrows=1000, loop=None):
    format_dict = {
        'interval_unit' : interval_unit,
        'interval_value': interval_value,
        'double_interval_value': 2*interval_value,
        'nrows' : nrows
    }

    if loop is None:
        loop = asyncio.get_event_loop()

    try:
        results = loop.run_until_complete(
            singleton_query(coord_score_fetching,
                            {'format_dict': format_dict})  )
    except asyncpg.exceptions.DivisionByZeroError as e:
        # pass the error upward
        raise e
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at fetching coord scores")
        logging.error("query args : {}".format(format_dict))
        return None
    return results
