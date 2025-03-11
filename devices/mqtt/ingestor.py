import json
import time
from queue import Empty, Queue

from log import logger
from paho.mqtt.client import Client as MQTTClient


class Ingestor:
    def __init__(self, queue: Queue, host="0.0.0.0", port=1883) -> None:
        self.client = MQTTClient()
        self.client.on_connect = self.on_connect
        self.host, self.port = host, port
        self.queue = queue
        self._stop_flag = False

    def start(self):
        logger.info("Starting ingestor..")
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        while not self._stop_flag:
            try:
                data = self.queue.get(block=False)
            except Empty:
                time.sleep(5)
                continue
            topic = json.loads(data).pop("topic")
            self.send(data, topic)

    def stop(self):
        logger.info("Stopping ingestor..")
        self._stop_flag = True
        self.client.loop_stop()

    def send(self, data, topic):
        logger.info(f"Ingesting {data} {topic}")
        self.client.publish(topic, data)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected to server with resulted code {str(rc)}")
