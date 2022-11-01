import functools
from typing import List

import msgpack
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.cache.redis_cache import RedisCache


def cache(
    cache_key: str,
    prefix: str,
    non_cache_keys: List[str],
):
    def wrapper(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            copy_kwargs = kwargs.copy()

            # check if any non cache keys are present, then make actual API call
            for key in non_cache_keys:
                if copy_kwargs.get(key):
                    return await func(*args, **kwargs)

            key = copy_kwargs.get(cache_key)

            response = await RedisCache.hget(prefix, key)

            # check if there is a response in cache, if so return it
            if response:
                return msgpack.loads(response)

            response = await func(*args, **kwargs)

            # don't cache empty responses
            if (
                isinstance(response, JSONResponse)
                and response.status_code == HTTP_404_NOT_FOUND
            ):
                return response

            packed_response = msgpack.dumps(jsonable_encoder(response))
            await RedisCache.hset(prefix=prefix, key=key, value=packed_response)

            return response

        return inner

    return wrapper
