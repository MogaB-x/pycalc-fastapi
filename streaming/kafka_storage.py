from collections import deque

kafka_messages = deque(maxlen=100)

def add_kafka_message(message: dict):
    kafka_messages.append(message)

def get_kafka_messages():
    return list(kafka_messages)
