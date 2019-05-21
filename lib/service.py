"""
Main module for daemon
"""

import os
import time
import json
import yaml
import redis

class Daemon(object):
    """
    Main class for daemon
    """

    def __init__(self):

        self.sleep = float(os.environ['SLEEP'])

        with open("/opt/service/subscriptions/redis.yaml", "r") as redis_file:
            redis_config = yaml.safe_load(redis_file)

        self.redis = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"])

        self.channel = os.environ['CHANNEL']

        self.pubsub = None

    def subscribe(self):
        """
        Subscribes to the channel on Redis
        """

        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel) 

    def process(self):
        """
        Processes a message from the channel if later than the daemons start time
        """

        message = self.pubsub.get_message()

        if not message or not isinstance(message["data"], str):
            return

        data = json.loads(message['data'])

        return data
            
    def run(self):
        """
        Runs the daemon
        """

        self.subscribe()

        while True:
            self.process()
            time.sleep(self.sleep)
