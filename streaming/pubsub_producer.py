import os
import json
from google.cloud import pubsub_v1

project_id = os.getenv("GCP_PROJECT_ID", "amiable-octane-468912-t1")
topic_id = "operation_stream"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def send_message(message: dict):
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    future.result()
