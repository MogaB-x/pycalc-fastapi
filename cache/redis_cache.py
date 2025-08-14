import os
import redis.asyncio as redis


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)


async def get_cached_result(key: str):
    result = await redis_client.get(key)
    print(f"GET cache: {key} -> {result}")
    return result


async def set_cached_result(key: str, value: str, expire: int = 600):
    await redis_client.set(key, value, ex=expire)
    print(f"SET cache: {key} -> {value} (expire={expire})")
