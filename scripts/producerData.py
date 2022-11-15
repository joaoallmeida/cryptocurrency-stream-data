from os import environ
from kafka import KafkaProducer

import requests
import json
import time
import logging
from websocket import create_connection


BOOSTRAP_SERVER = 'localhost:9093'
TOPIC_NAME = 'financial-data'
URL_BASE = 'https://api.coincap.io/v2'
SOCKET_BASE = 'wss://ws.coincap.io/prices?assets=ALL'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -> %(message)s',datefmt='%y-%m-%d %H:%M:%S')

producer = KafkaProducer(
                    bootstrap_servers=BOOSTRAP_SERVER
                    ,value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )

statusCode = 200

while statusCode == 200 :
    
    logging.info('Getting data from source!')
    
    try:      
            
        response = requests.get(f'{URL_BASE}/assets?limit=2000',stream=True)
        
        response.raise_for_status()
        
        statusCode = response.status_code
        
        for line in response.iter_lines():
            if line:
                
                logging.info('Data is available for consume!')
                dataMessage = json.loads(line)

                logging.info(f'Send data to kafka topic - {TOPIC_NAME}')

                producer.send(TOPIC_NAME,  dataMessage)
        
    except Exception as e:
        logging.error(f'Data message failed.')
        raise e

    logging.warning('Waiting 1 minute to place a new request!')
    time.sleep(60)