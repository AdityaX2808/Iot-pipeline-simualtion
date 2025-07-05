from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    acks='all',
    retries=3,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = "sensor-data"

def on_success(metadata):
    logging.info(f"Sent to {metadata.topic} partition={metadata.partition} offset={metadata.offset}")

def on_error(excp):
    logging.error(f" Failed to send: {excp}")


with open("output.json", "r") as file:
    for line in file:
        try:
            data = json.loads(line)
            future = producer.send(topic_name, value=data)
            future.add_callback(on_success)
            future.add_errback(on_error)
            time.sleep(0.1)  
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON line: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

producer.flush()
producer.close()