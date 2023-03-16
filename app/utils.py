import asyncio
import re

import httpx

from app import logger

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
        except httpx.TimeoutException:
            logger.error(f"Timeout for {url}")
        except httpx.HTTPError:
            logger.error(f"Error while making a request to {url}", exc_info=True)


async def send_async_requests(endpoints):
    tasks = [asyncio.create_task(request_get(call)) for call in endpoints]
    return await asyncio.gather(*tasks)


def get_final_service_url(*parts):
    """Returns a final service URL."""
    url = "/".join(parts)
    result = re.sub(r"([^:])//", r"\1/", url)
    return result
