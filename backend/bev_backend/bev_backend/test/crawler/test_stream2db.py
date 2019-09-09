import unittest
from bev_backend.crawler.stream2db import parse_query



class TestParseQuery(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty(self):
        self.assertListEqual( parse_query(''), list() )

    def test_singleton(self):
        query = '#cat'
        self.assertSetEqual( set(parse_query(query)), {'#cat'} )

    def test_compound(self):
        query = '#cat,#dog'
        # order doesn't matter
        self.assertSetEqual( set(parse_query(query)), {'#cat', '#dog'} )

    def test_mixed(self):
        query = '#cat,@helloworld'
        # order doesn't matter
        self.assertSetEqual( set(parse_query(query)), {'#cat', '@helloworld'} )

    def test_repeated(self):
        query = '#cat,#cat'
        self.assertSetEqual( set(parse_query(query)), {'#cat'} )



if __name__ == '__main__':
    unittest.main()
