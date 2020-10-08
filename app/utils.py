import asyncio

import httpx

from app import logger

REQUEST_TIMEOUT = 30


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
        except httpx.ReadTimeout:
            logger.info(f"Timeout for {url}")


async def send_async_requests(endpoints):
    tasks = [asyncio.create_task(request_get(call)) for call in endpoints]
    return await asyncio.gather(*tasks)
