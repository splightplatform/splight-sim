from paho.mqtt.client import Client
import time

data = '{"timestamp": 1651245772319,"metrics": [{"name": "Celda9/EDAG/Contingencia Detectada","timestamp": 1651245855707,"dataType": "Int",  "value": 10},{"name": "Celda9/Interruptor/Error","timestamp": 1651175644480,"dataType": "Boolean",  "value": false}]}'

SLEEP_TIME = 5

def on_message(client, userdata, message):
    pass

def on_connect(client, userdata, flags, rc):
    print("connected to client with resulted code ", str(rc))

if __name__ == '__main__':
    client = Client()
    client.on_message = on_message
    client.on_connect = on_connect
    # attempt connection multiple times
    client.connect('localhost', 1883)
    client.loop_start()
    
    try:
        while True:
            client.publish('/data', data)
            print('published data')
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        exit()