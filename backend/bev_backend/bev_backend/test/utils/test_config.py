import unittest
from bev_backend.utils.config import get_config



class TestGetConfig(unittest.TestCase):

    def setUp(self):
        self._config = get_config()

    def test_dbname(self):
        self.assertEqual(self._config['DB']['dbname'], 'bev')

    def test_dbuser(self):
        self.assertEqual(self._config['DB']['user'], 'bev')

    def test_dbpw(self):
        self.assertEqual(self._config['DB']['password'], 'bev')

    def test_middleware_debug(self):
        self.assertTrue(self._config['MIDDLEWARE']['debug'])

    def test_middleware_port(self):
        self.assertEqual(self._config['MIDDLEWARE']['port'], 5000)

    def test_middleware_host(self):
        self.assertEqual(self._config['MIDDLEWARE']['host'], '0.0.0.0')





if __name__ == '__main__':
    unittest.main()
