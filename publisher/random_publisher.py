import random
import time
from splight_lib import logging
import json
import argparse
from clients.mqtt import MQTTPublisher


logger = logging.getLogger()


class RandomIngestor():
    def __init__(self, client, topic, tz='UTC', delay=5) -> None:
        # Params
        self.tz = tz
        self.delay = delay
        self.topic = topic

        # Comm Client
        self.client = client

    def ingest(self):
        data = {
            "timestamp": 1651245772319,
            "metrics": [
                {
                    "name": "Celda9/EDAG/Contingencia Detectada",
                    "timestamp": 1651245855707,
                    "dataType": "Int",
                    "value": random.randint(1, 10)
                },
                {
                    "name": "Celda9/Interruptor/Error",
                    "timestamp": 1651175644480,
                    "dataType": "Boolean",
                    "value": random.choice([True, False])
                }
            ]
        }
        data = json.dumps(data, default=str)
        logger.info(f"Ingesting {data}")
        self.client.send(data=data, topic=self.topic)
        time.sleep(self.delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest a random number with fixed distribution in MQTT broker.')
    parser.add_argument('--host', dest='host', type=str, nargs=1,
                        default=['localhost'],
                        help='MQTT host')
    parser.add_argument('--port', dest='port', type=int, nargs=1,
                        default=[1883],
                        help='MQTT port')
    parser.add_argument('--delay', dest='delay', type=int, nargs=1,
                        default=[5],
                        help='fixed delay in secs')
    parser.add_argument('--topic', dest='topic', type=str, nargs=1,
                        default=['/data'],
                        help='topic to send info')

    args = parser.parse_args()
    client = MQTTPublisher(
        host=args.host[0],
        port=args.port[0]
    )
    ingestor = RandomIngestor(
        client=client,
        delay=args.delay[0],
        topic=args.topic[0]
    )
    
    while True:
        ingestor.ingest()