import logging
import logging.config as logging_config
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging_config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if os.getenv("DEBUG"):
    logger.setLevel(logging.DEBUG)

REDIS_URL = os.getenv("REDIS_URL", "localhost:6379")
