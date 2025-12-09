import asyncio
import functools
import os
import re
import time

import httpx

from app import logger
from app.version import __major__version__

REQUEST_TIMEOUT = 5


def timeit(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        logger.info(f"{fn.__name__} took {end - start} seconds")
        logger.info(args)
        return result

    return wrapper


# @timeit
async def request_get(url: str):
    """Makes an HTTP/HTTPS request and returns a response.

    Args:
        url (str): A request URL.

    Returns:
        Response: A Response object.
    """
    response = None
    # Explicitly ignore env proxies; k8s envs often inject HTTP(S)_PROXY which can
    # return 503 from the proxy rather than the upstream service.
    async with httpx.AsyncClient(trust_env=False) as client:
        try:
            response = await client.get(url, timeout=REQUEST_TIMEOUT)
        except httpx.TimeoutException:
            logger.error(f"Timeout for {url}")
        except httpx.HTTPError:
            logger.error(f"Error while making a request to {url}", exc_info=True)
        except Exception:
            logger.error(
                f"Unknown error while making a request to {url}", exc_info=True
            )
        finally:
            await client.aclose()
            return response


async def request_post(url: str, data):
    response = None
    async with httpx.AsyncClient(trust_env=False) as client:
        try:
            response = await client.post(url, timeout=REQUEST_TIMEOUT, data=data)
        except httpx.TimeoutException:
            logger.error(f"Timeout for {url}")
        except httpx.HTTPError:
            logger.error(f"Error while making a request to {url}", exc_info=True)
        except Exception:
            logger.error(
                f"Unknown error while making a request to {url}", exc_info=True
            )
        finally:
            await client.aclose()
            return response


async def send_async_requests(endpoints):
    tasks = [asyncio.create_task(request_get(call)) for call in endpoints]
    return await asyncio.gather(*tasks)


def get_final_service_url(*parts):
    """Returns a final service URL, handling existing query parameters."""
    url = "/".join(parts)
    url = re.sub(r"([^:])//", r"\1/", url)

    # remove / before query params
    url = url.replace("/?", "?")

    # Check if there is already a query string
    if "?" in url:
        return url + f"&version={__major__version__}"
    else:
        return url + f"?version={__major__version__}"


def clean_args():
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            cleaned_args = []
            for x in args:
                if x and not isinstance(x, str):
                    x = str(x)
                cleaned_args.append(x.strip(" ") if x else x)
            return func(*cleaned_args, **kwargs)

        return inner

    return wrapper


def include_in_schema() -> bool:
    """Returns if the endpoint should be included in the OpenAPI schema.
    Returns:
        bool: True if ENVIRONMENT envvar is not PROD or not set, otherwise False.
    """
    env = os.environ.get("ENVIRONMENT", None)

    if env == "DEV" or env == "dev":
        return True
    return False
