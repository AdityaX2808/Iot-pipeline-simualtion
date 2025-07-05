import json
import os
import time
import boto3
import logging
from kafka import KafkaConsumer
from botocore.exceptions import ClientError


BOOTSTRAP = os.getenv("BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("TOPIC", "iot_pipeline")
STREAM = os.getenv("STREAM", "my-stream")
REGION = os.getenv("REGION", "ap-south-1")
BATCH = int(os.getenv("BATCH", "50")) 
FLUSH_INTERVAL = 10 


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


try:
    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    logging.info("Running as AWS identity: %s", identity["Arn"])
except ClientError as e:
    logging.error("Failed to get AWS identity: %s", e)


consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[BOOTSTRAP],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id="iot_to_kinesis_debug",
    value_deserializer=lambda b: b.decode("utf-8"),
)


kinesis = boto3.client("kinesis", region_name=REGION)

batch = []
last_flush = time.time()


def flush():
    global batch
    if not batch:
        return

    try:
        resp = kinesis.put_records(StreamName=STREAM, Records=batch)
        failed = resp["FailedRecordCount"]
        logging.info("Sent %d records (failed=%d)", len(batch), failed)

        if failed > 0:
            logging.warning("WARNING: %d records failed to put into Kinesis", failed)
            logging.debug("Full response: %s", json.dumps(resp, indent=2))

    except ClientError as e:
        logging.error("AWS error: %s", e)

    batch = []  


logging.info("Started forwarder Kafka → Kinesis  (%s → %s)", TOPIC, STREAM)

try:
    for msg in consumer:
        logging.info("Consumed message: %s", msg.value)

        batch.append({
            "Data": msg.value.encode("utf-8"),
            "PartitionKey": "pk"
        })

        
        if len(batch) >= BATCH or (time.time() - last_flush >= FLUSH_INTERVAL):
            flush()
            last_flush = time.time()

except KeyboardInterrupt:
    logging.info("Stopping…")
    flush()
