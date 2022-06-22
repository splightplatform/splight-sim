import logging
from paho.mqtt.client import Client as MQTTClient

logger = logging.getLogger()


class MQTTPublisher:
    def __init__(self, host, port) -> None:
        self.client = MQTTClient()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        # attempt connection multiple times
        self.client.connect(host, port)
        self.client.loop_start()

    def send(self, data, topic):
        self.client.publish(topic, data)
        logger.info(f'Published data in {topic}')

    @staticmethod
    def on_message(client, userdata, message):
        pass

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected to client with resulted code {str(rc)}")
