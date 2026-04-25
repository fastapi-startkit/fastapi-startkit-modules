import os
import unittest

from config.redis import RedisConfig


class TestCase(unittest.TestCase):
    def setUp(self):
        os.environ.pop('PYTEST_CURRENT_TEST', None)
        from bootstrap.application import app
        self.app = app

    def test_app_loads_env_data(self):
        self.assertEqual(RedisConfig().host, "host.default")
        self.assertEqual(RedisConfig().port, 0000)
        self.assertEqual(RedisConfig().db, 0)

        self.app.set_environment('testing')
        self.app.load_environment()
        self.assertEqual(RedisConfig().host, "host.testing")
        self.assertEqual(RedisConfig().port, 2222)
        self.assertEqual(RedisConfig().db, 2)

        self.app.set_environment('production')
        self.app.load_environment()

        self.assertEqual(RedisConfig().host, "host.production")
        self.assertEqual(RedisConfig().port, 1111)
        self.assertEqual(RedisConfig().db, 1)
