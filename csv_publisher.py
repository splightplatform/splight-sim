import json
import time
import pandas as pd
import argparse
from datetime import datetime, timedelta
from splight_models import *
from splight_lib import logging
from paho.mqtt.client import Client as MQTTClient


logger = logging.getLogger()


class Client():
    def send():
        raise NotImplementedError


class MQTTPublisher(Client):
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


class CSVIngestor():
    def __init__(self, file: str, client: Client, tz='UTC', asset_id=12345) -> None:
        # Params
        self.file = file
        self.tz = tz
        self.asset_id = asset_id

        # Comm Client
        self.client = client

        # Data
        self.df = self.read(file)
        self.df = self.filter(self.df)
        self.df = self.prepare(self.df)

    def read(self, file):
        df = pd.read_csv(file, parse_dates=['timestamp'])
        return df

    def filter(self, df):
        # TODO Avail filters for segmentation        
        # df = df[df.embalse == "Rapel"]
        # df = df.drop('embalse', axis=1)
        return df

    def prepare(self, df):
        df.timestamp = pd.to_datetime(df['timestamp']).dt.tz_localize(self.tz)
        df = df.set_index('timestamp')
        df = VariableDataFrame.unfold(df, asset_id=self.asset_id)
        return df

    def ingest(self):
        delay = 0
        for index, row in self.df.iterrows():
            if index > 0:
                delay = (row['timestamp'] - prev_timestamp).total_seconds()
                logger.info(f"Delaying {delay} seconds. Next value at {datetime.now() + timedelta(seconds=delay)}")
                time.sleep(10)
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

    args = parser.parse_args()
    file = args.file[0]
    client = MQTTPublisher(
        host=args.host[0],
        port=args.port[0]
    )
    csv_ingestor = CSVIngestor(
        client=client,
        file=file
        
    )
    while True:
        csv_ingestor.ingest()
