import os
import redis.asyncio as redis


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)


async def get_cached_result(key: str):
    return await redis_client.get(key)


async def set_cached_result(key: str, value: str, expire: int = 600):
    await redis_client.set(key, value, ex=expire)