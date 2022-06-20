from paho.mqtt.client import Client as MQTTClient
import time
import logging

logger = logging.getLogger()


DATA = '{"timestamp": 1651245772319,"metrics": [{"name": "Celda9/EDAG/Contingencia Detectada","timestamp": 1651245855707,"dataType": "Int",  "value": 10},{"name": "Celda9/Interruptor/Error","timestamp": 1651175644480,"dataType": "Boolean",  "value": false}]}'
HOST, PORT = 'localhost', 1883
SLEEP_TIME = 5


class MQTTPublisher:
    def __init__(self, host, port) -> None:
        self.client = MQTTClient()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        # attempt connection multiple times
        self.client.connect(host, port)
        self.client.loop_start()

    def send(self, data):
        self.client.publish('/data', data)
        logger.info('Published data')

    @staticmethod
    def on_message(client, userdata, message):
        pass

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected to client with resulted code {str(rc)}")


if __name__ == '__main__':
    client = MQTTPublisher(HOST, PORT)
 
    try:
        while True:
            client.publish('/data', DATA)
            logger.info('published data')
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        exit()