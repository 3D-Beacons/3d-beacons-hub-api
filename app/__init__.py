import logging
import logging.config as logging_config
import os

import httpx

logging_config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
httpx_async_client = httpx.AsyncClient()

if os.getenv("DEBUG"):
    logger.setLevel(logging.DEBUG)

REDIS_URL = os.environ.get("REDIS_URL")
