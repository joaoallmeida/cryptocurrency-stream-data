from kafka import KafkaProducer
import requests
import json
import time
import logging
import os 

BOOSTRAP_SERVER = os.getenv('KAFKA_CLUSTER')
TOPIC_NAME = 'crypto-data-stream'
URL_BASE = 'https://api.coincap.io/v2'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -> %(message)s',datefmt='%y-%m-%d %H:%M:%S')
logConf = logging.getLogger()
logConf.setLevel(logging.INFO)

def producerDataStream():

    try:      
        producer = KafkaProducer(
                            bootstrap_servers=BOOSTRAP_SERVER
                            ,value_serializer=lambda v: json.dumps(v).encode('utf-8')
                        )

        statusCode = 200

        while statusCode == 200 :
            
            logging.info('Getting data from source!')
              
            response = requests.get(f'{URL_BASE}/assets?limit=100',stream=True)
            response.raise_for_status()
            statusCode = response.status_code
            
            for line in response.iter_lines():
                if line:
                    
                    logging.info('Data is available for producer!')
                    dataMessage = json.loads(line)

                    logging.info(f'Send data to kafka topic - {TOPIC_NAME}')

                    producer.send(TOPIC_NAME,  dataMessage)
                    producer.flush()
            
            logging.warning('Waiting 5 minutes to place a new request!')
            time.sleep(300)
            
    except Exception as e:
        logging.error(f'Failed to capture API data!')
        raise e
        
if __name__=="__main__":
    
    producerDataStream()