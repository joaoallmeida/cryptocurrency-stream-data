from twelvedata import TDClient
from dotenv import load_dotenv
from os import environ
from kafka import KafkaProducer

import requests
import json
import time
import logging

load_dotenv()

API_KEY = environ.get('API_KEY')
BOOSTRAP_SERVER = '192.168.15.14:9093'
TOPIC_NAME = 'financial-data'
URL_BASE = 'https://api.twelvedata.com'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -> %(message)s',datefmt='%y-%m-%d %H:%M:%S')

producer = KafkaProducer(
                    bootstrap_servers=BOOSTRAP_SERVER
                    ,value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )

logging.info('Getting all symbols available')

symbols = [a['symbol'] for a in json.loads(requests.get(F'{URL_BASE}/stocks').content)['data']]

for symbol in symbols:   
    
    logging.info(f'Getting general information to symbol: {symbol}')
        
    try:      
        response = requests.get(f'{URL_BASE}/time_series?symbol={symbol}&intervel=30min&apikey={API_KEY}')
        dataMessage = json.loads(response.content)
        
        logging.info(f'Send data to kafka topic - {TOPIC_NAME}')
        logging.info(f'Data from symbol - {symbol}')
        
        producer.send(TOPIC_NAME,  dataMessage)
    
    except Exception as e:
        logging.error(f'Data message failed.')
        raise e
    
    time.sleep(60)