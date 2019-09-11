import unittest
import datetime
from bev_backend.crawler.BotRuler import parse_date
from bev_backend.crawler.BotRuler import sigmoid
from bev_backend.crawler.BotRuler import extract_raw_features_from_tweet_obj
from bev_backend.crawler.BotRuler import extract_feature


class TestParseDate(unittest.TestCase):
    def setUp(self):
        pass

    def test_tz_removal(self):
        self.assertEqual(
            parse_date('Wed Oct 10 20:19:24 +0000 2018'),
            datetime.datetime.strptime('Wed Oct 10 20:19:24 2018',
                                       '%a %b %d %H:%M:%S %Y')
        )


class TestSigmoid(unittest.TestCase):
    def setUp(self):
        pass

    def test_zero(self):
        self.assertAlmostEqual(sigmoid(0.0), 0.5)

    def test_one(self):
        self.assertAlmostEqual(sigmoid(1.0), 0.73105858)

    def test_negone(self):
        self.assertAlmostEqual(sigmoid(-1.0), 0.26894142)

    def test_verybig(self):
        self.assertAlmostEqual(sigmoid(100), 1.0)

    def test_verysmall(self):
        self.assertAlmostEqual(sigmoid(-100), 0.0)


class TestExtractRawFeaturesFromTweetObj(unittest.TestCase):
    def setUp(self):
        pass

    def test_raw_feature_extraction(self):
        test_tweet_obj = {
            'user': {
                'created_at': 'Tue Sep 16 07:27:37 +0000 2014',
                'default_profile': True,
                'favourites_count': 5141,
                'friends_count': 2210,
                'profile_use_background_image': True,
                'description': 'This is a made up profile',
                'followers_count': 315,
                'listed_count': 1,
                'verified': False,
                'screen_name': 'TestScreenName',
                'id_str': '28129663',
                'statuses_count': 6251,
                'default_profile_image': True,
                'profile_background_tile': False,
                'name': 'TestName',
                'lang': 'en'
            },
            'created_at': 'Tue Sep 16 07:27:37 +0000 2014',
            'id_str': '2014523499'
        }

        extracted_raw_features = extract_raw_features_from_tweet_obj(test_tweet_obj)

        self.assertEqual(extracted_raw_features['tid'], '2014523499')
        self.assertEqual(
            extracted_raw_features['probe_timestamp'],
            datetime.datetime.strptime(
                'Tue Sep 16 07:27:37 2014',
                '%a %b %d %H:%M:%S %Y'
            )
        )
        self.assertEqual(extracted_raw_features['user_id'], 28129663)
        self.assertEqual(extracted_raw_features['screen_name'], 'TestScreenName')
        self.assertEqual(extracted_raw_features['name'], 'TestName')
        self.assertEqual(
            extracted_raw_features['description'],
            'This is a made up profile'
        )
        self.assertEqual(
            extracted_raw_features['user_created_at'],
            datetime.datetime.strptime(
                'Tue Sep 16 07:27:37 2014',
                '%a %b %d %H:%M:%S %Y'
            )
        )
        self.assertIsNone(extracted_raw_features['url'])
        self.assertEqual(extracted_raw_features['lang'], 'en')
        self.assertIsNone(extracted_raw_features['protected'])
        self.assertFalse(extracted_raw_features['verified'])
        self.assertTrue(extracted_raw_features['profile_use_background_image'])
        self.assertTrue(extracted_raw_features['default_profile'])
        self.assertEqual(extracted_raw_features['followers_count'], 315)
        self.assertEqual(extracted_raw_features['friends_count'], 2210)
        self.assertEqual(extracted_raw_features['listed_count'], 1)
        self.assertEqual(extracted_raw_features['favourites_count'], 5141)
        self.assertEqual(extracted_raw_features['statuses_count'], 6251)


class TestExtractFeature(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_features(self):
        test_tweet_obj = {
            'user': {
                'created_at': 'Tue Sep 16 07:27:37 +0000 2014',
                'default_profile': True,
                'favourites_count': 5141,
                'friends_count': 2210,
                'profile_use_background_image': True,
                'description': 'This is a made up profile',
                'followers_count': 315,
                'listed_count': 1,
                'verified': False,
                'screen_name': 'TestScreenName',
                'id_str': '28129663',
                'statuses_count': 6251,
                'default_profile_image': True,
                'profile_background_tile': False,
                'name': 'TestName',
                'lang': 'en'
            },
            'created_at': 'Tue Sep 18 07:27:37 +0000 2014',
            'id_str': '2014523499'
        }

        extracted_raw_features = extract_raw_features_from_tweet_obj(test_tweet_obj)
        extracted_features = extract_feature(extracted_raw_features)
        self.assertEqual(extracted_features[3], 1105)
        self.assertAlmostEqual(extracted_features[4], 7.01587301)
        self.assertAlmostEqual(extracted_features[5], 3125.5)
        self.assertEqual(extracted_features[6], 1)
        self.assertEqual(extracted_features[7], 1)
        self.assertEqual(extracted_features[8], 0)

    def test_extract_features_follower_zero(self):
        test_tweet_obj = {
            'user': {
                'created_at': 'Tue Sep 16 07:27:37 +0000 2014',
                'default_profile': True,
                'favourites_count': 5141,
                'friends_count': 2210,
                'profile_use_background_image': True,
                'description': 'This is a made up profile',
                'followers_count': 0,
                'listed_count': 1,
                'verified': False,
                'screen_name': 'TestScreenName',
                'id_str': '28129663',
                'statuses_count': 6251,
                'default_profile_image': True,
                'profile_background_tile': False,
                'name': 'TestName',
                'lang': 'en'
            },
            'created_at': 'Tue Sep 18 07:27:37 +0000 2014',
            'id_str': '2014523499'
        }

        extracted_raw_features = extract_raw_features_from_tweet_obj(test_tweet_obj)
        extracted_features = extract_feature(extracted_raw_features)
        self.assertAlmostEqual(extracted_features[4], 2210)


if __name__ == '__main__':
    unittest.main()
