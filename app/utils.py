import json

import httpx

from app import logger


REQUEST_TIMEOUT = 30


async def request_get(url: str):
    """ Makes an HTTP/HTTPS request and returns a response.

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


async def request_get_stub(url: str):
    """ Returns an object with stub response.

    Args:
        url (str): A request URL.

    Returns:
        StubResponse: A StubResponse object.
    """
    return StubResponse()


class StubResponse:
    """ A Stub response class to return a response from JSON.
    """
    def __init__(self) -> None:
        self.status_code = 200
        self.data = {}

        with open("stub.json") as f:
            self.data = json.load(f)

    def json(self):
        return self.data
