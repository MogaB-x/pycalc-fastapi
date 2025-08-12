from aiokafka import AIOKafkaConsumer
import asyncio, os, json
from collections import defaultdict

from streaming.kafka_storage import add_kafka_message

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
stats = {
    "count_per_minute": defaultdict(int),
    "operation_freq": defaultdict(int)
}

async def consume():
    consumer = AIOKafkaConsumer(
        "operation_stream",
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset="earliest"
    )
    for attempt in range(5):
        try:
            await consumer.start()
            print("Kafka consumer connected")
            break
        except Exception as e:
            print(f"Kafka consumer failed to connect: {e} (retry {attempt + 1}/5)")
            await asyncio.sleep(5)
    else:
        raise RuntimeError("Kafka consumer failed to connect after retries")

    try:
        async for msg in consumer:
            try:
                event = json.loads(msg.value.decode())
                add_kafka_message(msg.value)

            except Exception as e:
                print(f"Failed to decode message: {e}")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")

if __name__ == "__main__":
    asyncio.run(consume())