from typing import Optional

from redis import Redis


class RedisCache:
    """RedisCache class gives access to aioredis functionality"""

    redis_client: Optional[Redis] = None

    @classmethod
    def init_redis(cls, url: str, encoding: str) -> None:
        if cls.redis_client is None:
            cls.redis_client = Redis.from_url(
                url,
                encoding=encoding,
                decode_responses=False,
            )

    @classmethod
    def get(cls, key: str) -> Optional[bytes]:
        return cls.redis_client.get(key)

    @classmethod
    def set(cls, key: str, value: str) -> bool:
        return bool(cls.redis_client.set(key, value))

    @classmethod
    def hget(cls, prefix: str, key: str, decode: bool = True) -> Optional[bytes | str]:
        value = cls.redis_client.hget(prefix, key)
        if not value:
            return None
        if decode:
            return value.decode()
        return value

    @classmethod
    def hset(cls, prefix: str, key: str, value: str) -> int:
        return int(cls.redis_client.hset(prefix, key, value))

    @classmethod
    def hdel(cls, prefix: str, key: str) -> int:
        return int(cls.redis_client.hdel(prefix, key))

    @classmethod
    def flush(cls) -> None:
        if cls.redis_client:
            cls.redis_client.flushall()
