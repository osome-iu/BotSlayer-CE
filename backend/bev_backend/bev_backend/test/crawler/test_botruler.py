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

    def test_X(self):
        # TODO: yang
        pass



class TestExtractFeature(unittest.TestCase):

    def setUp(self):
        pass

    def test_Y(self):
        # TODO: yang
        pass



if __name__ == '__main__':
    unittest.main()
