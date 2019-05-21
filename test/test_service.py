import unittest
import unittest.mock

import os
import json

import service


class MockRedis(object):

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.channel = None
        self.messages = []

    def pubsub(self):

        return self

    def subscribe(self, channel):

        self.channel = channel

    def get_message(self):

        return self.messages.pop(0)


class TestService(unittest.TestCase):

    @unittest.mock.patch.dict(os.environ, {
        "CHANNEL": "stuff",
        "SLEEP": "0.7"
    })
    @unittest.mock.patch("redis.StrictRedis", MockRedis)
    def setUp(self):

        self.daemon = service.Daemon()

    @unittest.mock.patch.dict(os.environ, {
        "CHANNEL": "stuff",
        "SLEEP": "0.7"
    })
    @unittest.mock.patch("redis.StrictRedis", MockRedis)
    def test___init___(self):

        daemon = service.Daemon()

        self.assertEqual(daemon.redis.host, "host.docker.internal")
        self.assertEqual(daemon.redis.port, 6379)
        self.assertEqual(daemon.channel, "stuff")
        self.assertEqual(daemon.sleep, 0.7)

    def test_subscribe(self):

        self.daemon.subscribe()

        self.assertEqual(self.daemon.redis, self.daemon.pubsub)
        self.assertEqual(self.daemon.redis.channel, "stuff")


    def test_process(self):

        self.daemon.subscribe()

        self.daemon.redis.messages = [
            None,
            {"data": 1},
            {"data": '{"a": 1}'}
        ]

        self.assertIsNone(self.daemon.process())

        self.assertIsNone(self.daemon.process())

        self.assertEqual(self.daemon.process(), {"a": 1})

    @unittest.mock.patch("service.time.sleep")
    def test_run(self, mock_sleep):

        self.daemon.redis.messages = [
            None
        ]

        mock_sleep.side_effect = [Exception("whoops")]

        self.assertRaisesRegex(Exception, "whoops", self.daemon.run)

        mock_sleep.assert_called_with(0.7)
