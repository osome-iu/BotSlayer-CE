import pandas as pd
import numpy as np
import datetime

# By using several heuristics, BotRuler is able to generate a bot score for
# every user which serves as a feature to detect bot campaign.
# BotRuler is estimated to have AUC 0.65 to 0.70 when tested on annotated
# datasets while state-of-the-art machine learning based bot detection tools
# typically have AUC over 0.95 in the same tests.
# According to the tests, BotRuler is capable to provide some useful signals for bot
# detection, but more advanced bot detection tools might be adavisible
# depending on the research area.
# BotRuler is included as a placeholder so the users can have a taste of
# BotSlayer and add new features to it.
#
# Users with the need for professional bot detection ability can 1) replace
# BotRuler with other more advanced bot detection tools or 2) choose BotSlayer-Pro
# at https://osome.iuni.iu.edu/tools/botslayer/botslayer . BotSlayer-Pro
# includes proprietary bot detection software owned by Indiana University and
# other advanced features.

def parse_date(timestamp_str):
    """
    Function to parse the date str from Twitter and remove the timezone
    """
    timestamp = datetime.datetime.strptime(
        timestamp_str, '%a %b %d %H:%M:%S %z %Y'
    )
    return timestamp.replace(tzinfo=None)


def extract_raw_features_from_tweet_obj(tweet_obj):
    """
    Function to extract the raw features from tweet_obj
        This function is useful when the tweet object is available
    input:
        tweet_obj::dict: Twitter tweet object
    output:
        ::dict: all the raw features plus the tweet id
    """
    if 'id_str' in tweet_obj:
        tid = tweet_obj['id_str']
    else:
        tid = tweet_obj['id']
    probe_timestamp = parse_date(tweet_obj['created_at'])
    user_obj = tweet_obj['user']
    user_created_at = parse_date(user_obj['created_at'])

    raw_feature_dict = {
        'tid': tid,
        'probe_timestamp': probe_timestamp, # 1
        'user_id': int(user_obj['id_str']), # 2
        'screen_name': user_obj['screen_name'], # 3
        'name': user_obj['name'], # 4
        'description': user_obj.get('description'), # 5
        'user_created_at': user_created_at, # 6
        'url': user_obj.get('url'), # 7
        'lang': user_obj['lang'], # 8
        'protected': user_obj.get('protected'), # 9
        'verified': user_obj['verified'], # 10
        'profile_use_background_image': user_obj['profile_use_background_image'], # 12
        'default_profile': user_obj['default_profile'], # 13
        'followers_count': user_obj['followers_count'], # 14
        'friends_count': user_obj['friends_count'], # 15
        'listed_count': user_obj['listed_count'], # 16
        'favourites_count': user_obj['favourites_count'], # 17
        'statuses_count': user_obj['statuses_count'] # 18
    }

    return raw_feature_dict


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def extract_feature(raw_feature_dict):
    user_age_td = raw_feature_dict['probe_timestamp'] - raw_feature_dict['user_created_at']
    user_age = user_age_td.total_seconds() / 86400 # in days

    friends_growth_rate = raw_feature_dict['friends_count'] / user_age

    tweet_freq = raw_feature_dict['statuses_count'] / user_age
    if raw_feature_dict['followers_count'] > 0:
        friends_followers_ratio = raw_feature_dict['friends_count'] / raw_feature_dict['followers_count']
    else:
        friends_followers_ratio = raw_feature_dict['friends_count']
    return [
        raw_feature_dict['tid'],
        raw_feature_dict['user_id'],
        raw_feature_dict['probe_timestamp'],
        friends_growth_rate,
        friends_followers_ratio,
        tweet_freq,
        1 if raw_feature_dict['profile_use_background_image'] else 0,
        1 if raw_feature_dict['default_profile'] else 0,
        1 if raw_feature_dict['verified'] else 0
    ]


class BotRuler():
    def __init__(self):
        self.feature_cols = [
            'friends_growth_rate',
            'friends_followers_ratio',
            'tweet_freq',
            'profile_use_background_image',
            'default_profile',
            'verified'
        ]
        self.cols = ['tid', 'user_id', 'probe_timestamp'] + self.feature_cols

    def detect_on_tweet_objects(self, tweet_objects):
        raw_feature_dicts = []
        for tweet in tweet_objects:
            raw_feature_dict = extract_raw_features_from_tweet_obj(tweet)
            raw_feature_dicts.append(raw_feature_dict)

        df = self.detect_on_raw_feature_dicts(raw_feature_dicts)
        return df

    def detect_on_raw_feature_dicts(self, raw_feature_dicts):
        feature_list = []
        for raw_feature_dict in raw_feature_dicts:
            temp_feature_list = extract_feature(raw_feature_dict)
            feature_list.append(temp_feature_list)

        feature_df = pd.DataFrame(feature_list, columns=self.cols)

        raw_score = self.bot_detection(feature_df)
        feature_df['bot_score_lite'] = raw_score
        cols = ['tid', 'user_id', 'probe_timestamp', 'bot_score_lite']
        return feature_df[cols]

    def bot_detection(self, feature_df):
        feature_df['friends_growth_rate'] = sigmoid(feature_df['friends_growth_rate']-1)
        feature_df['friends_followers_ratio'] = sigmoid(feature_df['friends_followers_ratio']-7.4)
        feature_df['tweet_freq'] = sigmoid(feature_df['tweet_freq']-33)
        feature_df['profile_use_background_image'] = 1 - feature_df['profile_use_background_image']
        feature_df['verified'] = 1 - feature_df['verified']

        scores = feature_df[self.feature_cols].mean(axis=1)
        scores = scores/scores.max()

        return scores
