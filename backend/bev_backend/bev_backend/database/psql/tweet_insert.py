#!/usr/bin/env python3
import logging
from collections import Counter

from datetime import datetime
strptime = datetime.strptime
import pytz

try:
    import simplejson as json
except ImportError:
    import json

import spacy
from bev_backend.utils.tweet_tokenize import get_twitter_tokenizer
nlp = spacy.load('en')
nlp.tokenizer = get_twitter_tokenizer(nlp)




delete_query_base = '''
WITH earliest_ts AS (
    SELECT percentile_disc({})
        within GROUP (ORDER BY twtjson.created_at) AS t
    FROM twtjson
)
DELETE FROM twtjson
    USING  earliest_ts ets
    WHERE created_at < ets.t
RETURNING tid;
'''
async def batch_psql_tweet_delete(conn, percentile=0.25):
    '''
        delete X percent of tweets, cascading to other references
        returns tids of the deleted tweets
    '''
    delete_query = delete_query_base.format(percentile)
    output = await conn.fetch(delete_query)
    await conn.execute("VACUUM FULL")
    await conn.execute("CLUSTER")
    return output



raw_twtjson_query_str = '''
INSERT INTO twtjson(tid, tweet)
VALUES ($1, $2)
ON CONFLICT DO NOTHING;
'''
async def batch_psql_tweet_insert(conn, json_objs):
    batch_values = [
        (
            twt['id'], # tid
            json.dumps(twt).replace('\\u0000', '') # tweet
        ) for twt in json_objs
    ]

    return await conn.executemany(
        command=raw_twtjson_query_str,
        args=batch_values
    )



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



async def get_text_entities(conn):
    records = await conn.fetch(
    '''
SELECT
    entity_text
from entity
WHERE entity_type = 'intext'
    ''')
    return { record['entity_text'] for record in records }



async def text_entity_extract(tweet_text, text_entities,
                         entities, dt, bs, tid, uid):
    return [
        {
            'entity_type': 'intext',
            'entity_text': token,
            'tweet_date' : dt,
            'bot_score'  : bs,
            'tid'        : tid,
            'user_id'    : uid
        }
        for token in tweet_text
        if token in text_entities
    ]

async def get_text(data):
    # Try for extended text of original tweet, if RT'd (streamer)
    text = ''
    try: text = data['retweeted_status']['extended_tweet']['full_text']
    except:
        # Try for extended text of an original tweet, if RT'd (REST API)
        try: text = data['retweeted_status']['full_text']
        except:
            # Try for extended text of an original tweet (streamer)
            try: text = data['extended_tweet']['full_text']
            except:
                # Try for extended text of an original tweet (REST API)
                try: text = data['full_text']
                except:
                    # Try for basic text of original tweet if RT'd
                    try: text = data['retweeted_status']['text']
                    except:
                        # Try for basic text of an original tweet
                        try: text = data['text']
                        except:
                            # Nothing left to check for
                            text = ''
    return text


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
    i.tweet_date::timestamp without time zone AS tweet_date
FROM entity e JOIN input_rows i
    ON e.entity_text=i.entity_text AND e.entity_type=i.entity_type
ON CONFLICT DO NOTHING;
'''

async def batch_psql_entity_insert(conn, json_objs, bot_scores, rt_user_scores):

    # tweet parsing
    # START for batch of tweets
    tweets = list()
    for tweet in json_objs:
        phrase_idx = None
        phrase_container = ''
        tweet_tokens = list()
        # START for one tweet
        text = await get_text(tweet)
        for token_idx, token in enumerate(nlp(text)):
            tag = token.tag_
            if (tag != 'NNP') and (phrase_idx is not None):
                # look back to close a phrase
                tweet_tokens.append(phrase_container)
                phrase_idx = None
                phrase_container = ''

            lemma = token.lemma_.lower()

            if ( len(lemma) <= 2 ) or \
                ( token.is_stop ) or \
                ( lemma == 'amp' ):
                # stopword
                continue

            if (len(lemma) >= 4 and lemma[:4] == 'http') or \
                (lemma[0] == '@') or (lemma[0] == '#') or (lemma[0] == '$'):
                # token is an entity
                continue

            if tag == 'NN':
                # token is a noun with one word
                tweet_tokens.append(lemma)
            if tag == 'NNP':
                if phrase_idx is None:
                    # token is the start of a noun phrase
                    phrase_idx = token_idx
                    phrase_container = lemma
                elif phrase_idx == (token_idx - 1):
                    # token is a continuation of a phrase
                    phrase_idx = token_idx
                    phrase_container = phrase_container + ' ' + lemma
        #END for one tweet
        tweets.append(tweet_tokens)
    #END for batch of tweets

    # convert sentences into corpus of tokens and count them
    corpus = [token
        for tweet in tweets
        for token in set(tweet)
    ]
    token_counts = Counter(corpus)
    top_words = token_counts.most_common(20) # cap selection of each batch at 20
    # take max count as selection criteria
    max_cnt = top_words[0][1]

    # select text to be indexed
    added_entities = {word for word, cnt in top_words if cnt == max_cnt}
    # log the new text entities to be indexed
    logging.info("indexing entities from text : {}".format(added_entities))

    # get existing text entities and merge them
    text_entities = await get_text_entities(conn)
    text_entities = text_entities | added_entities

    data = list()
    for idx in range(len(json_objs)):

        jobj = json_objs[idx]
        bs = bot_scores[idx]
        tweet_text = tweets[idx]

        arg_dict = {
            'dt': strptime(
                jobj['created_at'], '%a %b %d %H:%M:%S %z %Y'
            ).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
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
        data += await text_entity_extract(tweet_text, text_entities, **arg_dict)

        if 'retweeted_status' in jobj:
            rt = jobj['retweeted_status']

            arg_dict = {
                'dt': strptime(
                    rt['created_at'], '%a %b %d %H:%M:%S %z %Y'
                ).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                'tid': jobj['id_str'], # use the tid from retweet
                'uid': rt['user']['id_str'],
                'entities': jobj['entities'],
                'bs': str(rt_user_scores[rt['user']['id']])
            }

            data += await entity_extract('hashtags', 'text', **arg_dict)
            data += await entity_extract('user_mentions', 'screen_name', **arg_dict)
            data += await entity_extract('urls', 'expanded_url', **arg_dict)
            data += await entity_extract('media', 'expanded_url', **arg_dict)
            data += await entity_extract('symbols', 'text', **arg_dict)
            data += await text_entity_extract(tweet_text, text_entities, **arg_dict)


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
