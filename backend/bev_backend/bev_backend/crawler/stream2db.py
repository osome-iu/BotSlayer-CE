import time
import shutil
import logging
import asyncio
# dependencies
import twython
from bev_backend.database.psql.common import run_query
from bev_backend.database.psql.common import run_transaction
from bev_backend.database.psql.user_setting import get_user_settings
from bev_backend.database.psql.tweet_insert import batch_psql_tweet_insert
from bev_backend.database.psql.tweet_insert import batch_psql_entity_insert
from bev_backend.database.psql.tweet_insert import batch_psql_tweet_delete
from bev_backend.crawler.BotRuler import BotRuler


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    level=logging.INFO
)



def check_disk_space():
    total, used, avail = shutil.disk_usage("/")
    percent = avail * 1.0 / total * 100.0
    logging.info("currently {} percent of space left".format(percent))

    if percent < 20.0:
        deleted_tweets = list()
        try:
            deleted_tweets = asyncio.run(run_query(batch_psql_tweet_delete, {}))
        except Exception as e:
            logging.exception("transaction failed")
            logging.error("failed at deleting data")

        logging.info("{} tweets deleted".format(len(deleted_tweets)))

        total, used, avail = shutil.disk_usage("/")
        percent = avail * 1.0 / total * 100.0
        logging.info("now {} percent of space left".format(percent))



class BatchedStream(twython.TwythonStreamer):

    def __init__(self, *args, batch_size=100, batch_time=60, **kwargs):
        super().__init__(*args, **kwargs)

        self._count = 0
        self._time = time.time()
        self._buffer = [None for _ in range(batch_size)]

        self._batch_size = batch_size
        self._batch_time = batch_time

        self._botometer = BotRuler()
        self._queries = [batch_psql_tweet_insert, batch_psql_entity_insert]

    def on_success(self, data):
        if 'id_str' not in data:
            return

        self._buffer[self._count] = data
        # progress counters
        self._count += 1
        cur_time = time.time()
        # batch trigger
        if (self._count >= self._batch_size) or \
                (cur_time - self._time > self._batch_time):
            # will trigger tweet deletion once when disk is 90%+ full
            check_disk_space()

            json_objs = self._buffer[:self._count]
            retweets = [
                json_obj['retweeted_status']
                for json_obj in json_objs
                if 'retweeted_status' in json_obj
            ]
            if len(retweets) > 0:
                retweets_users = [
                    [ idx ,
                    (
                        json_obj['created_at'], # probe timestamp
                        json_obj['retweeted_status']#['user']
                    )
                    ]
                    for idx, json_obj in enumerate(json_objs)
                    if 'retweeted_status' in json_obj
                ]
                # obtain bot score for retweet users
                retweet_user_scores = self._botometer.detect_on_tweet_objects(
                    [indexed_user[1] for indexed_user in retweets_users]
                )
                retweet_user_scores = {
                    indexed_user[0] : retweet_user_score
                    for indexed_user, retweet_user_score in
                        zip(retweets_users, retweet_user_scores.bot_score_lite)
                }
            else:
                retweet_user_scores = dict()

            # obtain bot score from old pickle
            bot_scores = self._botometer.detect_on_tweet_objects(json_objs)
            bot_scores = bot_scores.bot_score_lite

            # insert rows
            query_args = [
                {'json_objs': json_objs+retweets}, # batch_psql_tweet_insert
                {
                    'json_objs': json_objs,
                    'bot_scores': bot_scores,
                    'rt_user_scores': retweet_user_scores
                } # batch_psql_entity_insert
            ]
            try:
                asyncio.run(run_transaction(self._queries, query_args))
            except Exception as e:
                logging.exception("transaction failed")
                logging.error("failed at inserting tweets")

            # log and clean up
            logging.info('processed {ntwt} tweets'.format(ntwt=self._count))
            self._count = 0
            self._time = cur_time
            #ENDIF

    def on_error(self, status_code, data):
        logging.error("Error, code {}".format(status_code))
        if status_code == 420:
            logging.error("This is a rate limit error, sleeping")
            time.sleep(300)
            logging.error("Waking up from sleep")



def get_stream(consumerKey, consumerSecret, accessToken, accessTokenSecret):
    # create stream
    stream = BatchedStream(
        consumerKey, consumerSecret, accessToken, accessTokenSecret
    )
    return stream



def parse_query(query_name, settings):
    if query_name not in settings:
        return list()

    query_str = settings[query_name]
    if len(query_str) == 0:
        return list()

    if (query_name == 'location'):
        return list(query_str.split(','))

    # remove duplicates
    query = list(set(query_str.split(',')))
    return query



def main():
    # fetch query along with other settings
    settings = get_user_settings()

    # get tracking query
    seed_query = parse_query("seed", settings)
    pinned_query = parse_query("pinned", settings)
    query = seed_query + pinned_query

    # get side spec
    user_query = parse_query("user", settings)
    location_query = parse_query("location", settings)

    # format input
    query = seed_query + pinned_query + user_query + location_query
    query_dict = {
        'track': seed_query + pinned_query,
        'follow': user_query,
        'locations': location_query
    }
    query_dict = {k:v for k,v in query_dict.items() if len(v) > 0}

    # get stream
    stream = get_stream(
        consumerKey=settings["consumerKey"],
        consumerSecret=settings["consumerSecret"],
        accessToken=settings["accessToken"],
        accessTokenSecret=settings["accessTokenSecret"]
    )

    # delete information from RAM
    del settings

    # start streaming
    while True:
        try:
            if len(query) > 0:
                # there is something to track
                logging.info("filtering with the following parameters : {}".format(query_dict))
                stream.statuses.filter(tweet_mode='extended', **query_dict)
            else:
                # nothing to track, do random 1% sample
                logging.info("no parameter given, sleeping for 10s...")
                time.sleep(10)
        except Exception as e:
            logging.exception("exception fall through all catches")
            continue





if __name__ == '__main__': main()
