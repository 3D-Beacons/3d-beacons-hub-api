from app.cache.redis_cache import RedisCache


async def delete_from_cache(key_category: str, key: str):
    """Delete a sequence from the cache.

    Args:
        seq_hash (str): A protein sequence hash
    """
    await RedisCache.hdel(key_category, key)
