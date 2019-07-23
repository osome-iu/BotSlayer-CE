import os
import time
import logging
import asyncio
import subprocess
# dependencies
import tweepy
from BotRuler import BotRuler
from bev_backend.database.psql.common import singleton_query
from bev_backend.database.psql.common import run_sync_transaction
from bev_backend.database.psql.user_setting import get_user_settings
from bev_backend.database.psql.tweet_insert import batch_psql_tweet_insert
from bev_backend.database.psql.tweet_insert import batch_psql_entity_insert
from bev_backend.database.psql.tweet_insert import batch_psql_tweet_delete



logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    level=logging.INFO
)



def check_disk_space():
    st = os.statvfs('/')
    avail = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    percent = avail * 1.0 / total * 100.0

    if percent < 10.0:
        logging.info("currently {} percent of space left".format(percent))

        loop = asyncio.get_event_loop()
        deleted_tweets = list()
        try:
            deleted_tweets = loop.run_until_complete(
                singleton_query(batch_psql_tweet_delete, {})  )
        except Exception as e:
            logging.exception("transaction failed")
            logging.error("failed at deleting data")
        logging.info("{} tweets deleted".format(len(deleted_tweets)))

        st = os.statvfs('/')
        avail = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        percent = avail * 1.0 / total * 100.0
        logging.info("now {} percent of space left".format(percent))



class BatchedStreamListener(tweepy.StreamListener):

    def __init__(self, *args, batch_size=10, batch_time=10, **kwargs):
        super().__init__(*args, **kwargs)

        self._count = 0
        self._time = time.time()
        self._remote_timer = self._time
        self._buffer = [None for _ in range(batch_size)]

        self._batch_size = batch_size
        self._batch_time = batch_time

        self._botometer = BotRuler()
        self._queries = [batch_psql_tweet_insert, batch_psql_entity_insert]

    def on_status(self, status):
        self._buffer[self._count] = status
        # progress counters
        self._count += 1
        cur_time = time.time()
        # batch trigger
        if (self._count >= self._batch_size) or \
                (cur_time - self._time > self._batch_time):
            # will trigger tweet deletion once when disk is 90%+ full
            check_disk_space()

            statuses = self._buffer[:self._count]
            json_objs = [status._json for status in statuses]
            # obtain bot score from old pickle
            bot_scores = self._botometer.detect_on_tweet_objects(json_objs)
            bot_scores = bot_scores.bot_score_lite
            # insert rows
            loop = asyncio.get_event_loop()
            query_args = [
                {'json_objs': json_objs},
                {'json_objs': json_objs, 'bot_scores': bot_scores}
            ]
            try:
                loop.run_until_complete(
                    run_sync_transaction(self._queries, query_args)  )
            except Exception as e:
                ## run_sync_transaction catches all errors internally
                # this is a dead block to ensure closed loop
                logging.exception("transaction failed")
                logging.error("failed at inserting tweets")

            # log and clean up
            logging.info('processed {ntwt} tweets'.format(ntwt=self._count))
            self._count = 0
            self._time = cur_time
            #ENDIF

    def on_error(self, status_code):
        logging.error("Error, code {}".format(status_code))
        if status_code == 420:
            logging.error("This is a rate limit error, sleeping")
            time.sleep(300)
            logging.error("Waking up from sleep")



def get_stream(consumerKey, consumerSecret, accessToken, accessTokenSecret):
    # create auth object
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)

    # create stream
    listener = BatchedStreamListener()
    stream = tweepy.Stream(auth=auth, listener=listener, tweet_mode='extended')

    return listener, stream



def parse_query(query_str):
    if len(query_str) == 0:
        return list()
    # remove duplicates
    seed_query = list(set(query_str.split(',')))
    return seed_query



def main():
    # entry point, create global event loop
    loop = asyncio.get_event_loop()

    # fetch query along with other settings
    settings = get_user_settings()
    seed_query = parse_query(settings["seed"])

    # retry until there is something to filter
    while len(seed_query) == 0:
        logging.info("no seed input, waiting for user setting")
        time.sleep(10)

        settings = get_user_settings()
        seed_query = parse_query(settings["seed"])

    # get stream
    del settings["seed"]
    listener, stream = get_stream(**settings)

    # start streaming
    try:
        stream.filter(track=seed_query, languages=['en'])
    except Exception as e:
        logging.exception("exception fall through all catches, closing loop")
    finally:
        loop.close()





if __name__ == '__main__': main()
