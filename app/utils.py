import asyncio
import functools
import re

import httpx

from app import logger
from app.version import __version__

REQUEST_TIMEOUT = 5


async def request_get(url: str):
    """Makes an HTTP/HTTPS request and returns a response.

    Args:
        url (str): A request URL.

    Returns:
        Response: A Response object.
    """
    async with httpx.AsyncClient() as client:
        try:
            return await client.get(url, timeout=REQUEST_TIMEOUT)
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            logger.error(f"Timeout for {url}")
            # raise RequestTimeoutException("Request timeout!")
        except httpx.HTTPError:
            logger.error(f"Error for {url}")
            # raise RequestSubmissionException("Request submission error!")


async def request_post(url: str, data):
    async with httpx.AsyncClient() as client:
        try:
            return await client.post(url, timeout=REQUEST_TIMEOUT, data=data)
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            logger.error(f"Timeout for {url}")
            # raise RequestTimeoutException("Request timeout!")
        except httpx.HTTPError:
            logger.error(f"Error for {url}")
            # raise RequestSubmissionException("Request submission error!")


async def send_async_requests(endpoints):
    tasks = [asyncio.create_task(request_get(call)) for call in endpoints]
    return await asyncio.gather(*tasks)


def get_final_service_url(*parts):
    """Returns a final service URL."""
    url = "/".join(parts)
    result = re.sub(r"([^:])//", r"\1/", url)
    return result + f"?version={__version__}"


def clean_args():
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            cleaned_args = []
            for x in args:
                cleaned_args.append(x.strip(" ") if x else x)
            return func(*cleaned_args, **kwargs)

        return inner

    return wrapper
