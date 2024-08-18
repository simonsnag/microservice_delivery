import aioredis
import json
from typing import Optional
from settings import redis_settings


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def initialize(self):
        self.redis = await aioredis.from_url(self.redis_url)

    async def close(self):
        await self.redis.close()

    async def set(self, key: str, value: dict, expire: int = 180):
        json_value = json.dumps(value)
        await self.redis.set(key, json_value, ex=expire)

    async def get(self, key: str) -> Optional[dict]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def delete(self, key: str):
        await self.redis.delete(key)


redis_cache = RedisCache(redis_settings.url)
