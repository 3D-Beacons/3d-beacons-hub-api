import logging
import logging.config as logging_config
import os

logging_config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if os.getenv("DEBUG"):
    logger.setLevel(logging.DEBUG)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
