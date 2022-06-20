import json
import time
import pandas as pd
import argparse
from datetime import datetime, timedelta
from splight_models import *
from splight_lib import logging
from mqtt.publisher import MQTTPublisher


logger = logging.getLogger()


class CSVIngestor():
    def __init__(self, file, client, tz='UTC', asset_id=12345, delay=None) -> None:
        # Params
        self.file = file
        self.tz = tz
        self.asset_id = asset_id
        self.delay = delay

        # Comm Client
        self.client = client

        # Data
        self.df = self.read(file)

    def read(self, file):
        df = pd.read_csv(file, parse_dates=['timestamp'])
        return df

    def ingest(self):
        delay = 0
        for index, row in self.df.iterrows():
            if index > 0:
                delay = (row['timestamp'] - prev_timestamp).total_seconds() if not self.delay else self.delay
                logger.info(f"Delaying {delay} seconds. Next value at {datetime.now() + timedelta(seconds=delay)}")
                time.sleep(delay)
            prev_timestamp = row['timestamp']
            data = {
                "timestamp": row.timestamp,
                "metrics": [
                    {
                        
                        "name": row.attribute_id,
                        "timestamp": row.timestamp,
                        "dataType": "Float",
                        "value": row.value
                    }
                ]
            }
            data = json.dumps(data, default=str)
            logger.info(f"Ingesting {data}")
            self.client.send(data=data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest a csv with same distribution in MQTT broker.')
    parser.add_argument('file', metavar='FILE', type=str, nargs=1,
                        help='path of csv file to ingest')
    parser.add_argument('--host', dest='host', type=str, nargs=1,
                        default=['localhost'],
                        help='MQTT host')
    parser.add_argument('--port', dest='port', type=int, nargs=1,
                        default=[1883],
                        help='MQTT port')
    parser.add_argument('--delay', dest='delay', type=int, nargs=1,
                        default=[None],
                        help='fixed delay in secs')

    args = parser.parse_args()
    file = args.file[0]
    client = MQTTPublisher(
        host=args.host[0],
        port=args.port[0]
    )
    csv_ingestor = CSVIngestor(
        client=client,
        file=file,
        delay=args.delay[0]
    )
    
    while True:
        csv_ingestor.ingest()
