import asyncio
from aiokafka import AIOKafkaProducer
import json
import os

producer = None

async def start_kafka():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    for attempt in range(5):
        try:
            await producer.start()
            print("Kafka connected")
            break
        except Exception as e:
            print(f"Kafka connect failed: {e} (retry {attempt + 1}/5)")
            await asyncio.sleep(5)
    else:
        raise RuntimeError("Kafka failed to start after retries")


async def stop_kafka():
    global producer
    if producer:
        await producer.stop()


async def send_message(topic: str, message: dict):
    global producer
    if not producer:
        raise RuntimeError("Kafka producer is not started")

    try:
        await producer.send_and_wait(topic, json.dumps(message).encode('utf-8'))
    except Exception as e:
        print(f"Failed to send message: {e}")
        raise