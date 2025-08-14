from google.cloud import pubsub_v1
import os
import json
import time
from streaming.kafka_storage import add_kafka_message

project_id = os.getenv("GCP_PROJECT_ID", "amiable-octane-468912-t1")
subscription_id = "operation-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)


def callback(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        add_kafka_message(data)
        print(f"Received message: {data}")
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()


def consume():
    subscriber.subscribe(subscription_path, callback=callback)
    print("Listening for messages on", subscription_path)

    # keep thread alive
    while True:
        time.sleep(60)


if __name__ == "__main__":
    consume()
