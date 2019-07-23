#!/usr/bin/env python3
from datetime import datetime
strptime = datetime.strptime
try:
    import simplejson as json
except ImportError:
    import json



delete_query_base = '''
WITH earliest_ts AS (
    SELECT MIN(created_at) AS t FROM twtjson
)
DELETE FROM twtjson
    USING  earliest_ts ets
    WHERE created_at BETWEEN
        ets.t AND
        ets.t + INTERVAL '{} {}'
RETURNING tid;
'''
async def batch_psql_tweet_delete(conn, interval_value=168, interval_unit="hours"):
    '''
        delete the oldest X hours of rows from tweet table only
        X by default is 24*7 hours == 168 hours == 1 week

        returns tids of the deleted tweets
    '''
    delete_query = delete_query_base.format(interval_value, interval_unit)
    return await conn.fetch(delete_query)



async def batch_psql_tweet_insert(conn, json_objs):
    batch_values = [
        (
            twt['id'], # tid
            json.dumps(twt).replace('\\u0000', '') # tweet
        ) for twt in json_objs
    ]

    return await conn.copy_records_to_table(
        table_name="twtjson", records=batch_values, columns=["tid", "tweet"] )



async def entity_extract(target_name, target_key,
                         entities, dt, bs, tid, uid):
    if target_name not in entities:
        return list()
    return [
        {
            'entity_type': target_name,
            'entity_text': entity[target_key] if target_name == "urls"
                                else entity[target_key].lower(),
            'tweet_date' : dt,
            'bot_score'  : bs,
            'tid'        : tid,
            'user_id'    : uid
        }
        for entity in entities[target_name]
    ]

raw_entity_event_query_str = '''
WITH input_rows(tid, entity_text, entity_type, user_id, bot_score, tweet_date) AS (
    VALUES
    ($1, $2, $3, $4, $5, $6)
), enter_rows AS (
    INSERT INTO entity(entity_text, entity_type)
    SELECT
        entity_text AS entity_text,
        entity_type AS entity_type
    FROM input_rows
    ON CONFLICT (entity_text, entity_type) DO NOTHING
    RETURNING entity_id, entity_text, entity_type
)
INSERT INTO entitytwt(tid, entity_id, user_id, bot_score, tweet_date)
SELECT
    i.tid::bigint AS tid,
    e.entity_id AS entity_id,
    i.user_id::bigint AS user_id,
    i.bot_score::float AS bot_score,
    i.tweet_date::timestamp with time zone AS tweet_date
FROM entity e JOIN input_rows i
    ON e.entity_text=i.entity_text AND e.entity_type=i.entity_type;
'''

async def batch_psql_entity_insert(conn, json_objs, bot_scores):
    data = list()
    for jobj, bs in zip(json_objs, bot_scores):
        arg_dict = {
            'dt': str(strptime(jobj['created_at'], '%a %b %d %H:%M:%S %z %Y')),
            'tid': jobj['id_str'],
            'uid': jobj['user']['id_str'],
            'entities': jobj['entities'],
            'bs': str(bs)
        }

        data += await entity_extract('hashtags', 'text', **arg_dict)
        data += await entity_extract('user_mentions', 'screen_name', **arg_dict)
        data += await entity_extract('urls', 'expanded_url', **arg_dict)
        data += await entity_extract('media', 'expanded_url', **arg_dict)
        data += await entity_extract('symbols', 'text', **arg_dict)

    return await conn.executemany(
        command=raw_entity_event_query_str,
        args=[
            (
                atom['tid'],
                atom['entity_text'],
                atom['entity_type'],
                atom['user_id'],
                atom['bot_score'],
                atom['tweet_date']
            )
            for atom in data
        ]
    )
