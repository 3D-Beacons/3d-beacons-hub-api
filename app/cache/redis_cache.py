from aioredis import Redis


class RedisCache:
    """RedisCache class gives access to aioredis functionality"""

    redis_client = None

    @classmethod
    def init_redis(cls, url: str, encoding: str):
        if cls.redis_client is None:
            cls.redis_client = Redis.from_url(
                f"redis://{url}", encoding=encoding, decode_responses=False
            )

    @classmethod
    async def get(cls, key: str) -> str:
        return await cls.redis_client.get(key)

    @classmethod
    async def set(cls, key: str, value: str):
        return await cls.redis_client.set(key, value)

    @classmethod
    async def hget(cls, prefix: str, key: str) -> str:
        return await cls.redis_client.hget(prefix, key)

    @classmethod
    async def hset(cls, prefix: str, key: str, value: str):
        return await cls.redis_client.hset(prefix, key, value)

    @classmethod
    async def hdel(cls, prefix: str, key: str):
        return await cls.redis_client.hdel(prefix, key)

    @classmethod
    async def flush(cls):
        return await cls.redis_client.flushall()
