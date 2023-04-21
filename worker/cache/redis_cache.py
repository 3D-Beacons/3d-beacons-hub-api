from redis import Redis


class RedisCache:
    """RedisCache class gives access to aioredis functionality"""

    redis_client = None

    @classmethod
    def init_redis(cls, url: str, encoding: str):
        if cls.redis_client is None:
            cls.redis_client = Redis.from_url(
                url,
                encoding=encoding,
                decode_responses=False,
            )

    @classmethod
    def get(cls, key: str) -> str:
        return cls.redis_client.get(key)

    @classmethod
    def set(cls, key: str, value: str):
        return cls.redis_client.set(key, value)

    @classmethod
    def hget(cls, prefix: str, key: str, decode: bool = True) -> str:
        value = cls.redis_client.hget(prefix, key)
        if not value:
            return None
        if decode:
            return value.decode()
        return value

    @classmethod
    def hset(cls, prefix: str, key: str, value: str):
        return cls.redis_client.hset(prefix, key, value)

    @classmethod
    def hdel(cls, prefix: str, key: str):
        return cls.redis_client.hdel(prefix, key)

    @classmethod
    def flush(cls):
        return cls.redis_client.flushall()
