import json
import os
from functools import lru_cache

from fastapi.params import Query

from app import logger

DATA_FILE = "data.json"
ENV = os.getenv("ENVIRONMENT", "DEV")

logger.debug(f"Environment is {ENV}")


@lru_cache(maxsize=None)
def read_data_file(filename):
    data_filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(data_filepath) as fp:
        data = json.load(fp)

    # check for REGISTRY_DATA_JSON in env and loads the JSON if exists
    data_json_env = os.getenv("REGISTRY_DATA_JSON")

    if data_json_env:
        logger.info(
            f"REGISTRY_DATA_JSON env var exists, trying to load JSON @ {data_json_env}"
        )
        data = read_registry_data(data_json_env)

    logger.info(f"Loaded data JSON: {DATA_FILE}")
    return data


def read_registry_data(data_json_env):

    import requests

    try:
        request_data = requests.get(data_json_env)
        if request_data.status_code == 200:
            data = request_data.json()
        else:
            raise Exception
    except Exception:
        logger.info("Registry JSON cannot be retrieved, fallback to default data.json")
    return data


def get_services(
    service_type: str = None, provider: Query = None, exclude_provider: Query = None
):
    """Returns a list of services available.

    Args:
        service_type (str, optional): A type of service.
        provider (Query, optional): A provider.
        exclude_provider (Query, optional): Provider to exclude.
    Returns:
        list: A list of services based on the parameters passed.
    """
    data_file = DATA_FILE
    data = read_data_file(data_file)
    results = []

    # assuming all services to be returned when no service_type and provider is passed
    if not service_type and not provider and not exclude_provider:
        return data["services"]

    # filter services for a service type
    if service_type:
        results = list(
            filter(
                lambda x: x["serviceType"] == service_type,
                [x for x in data["services"]],
            )
        )

    # filter services for a provider
    if provider:
        results = list(
            filter(lambda x: x["provider"] == provider, [x for x in results])
        )

    if exclude_provider:
        results = list(
            filter(lambda x: x["provider"] != exclude_provider, [x for x in results])
        )

    return results


@lru_cache(maxsize=None)
def get_providers():
    data_file = DATA_FILE
    data = read_data_file(data_file)

    return data["providers"]


def get_base_service_url(provider: str) -> str:
    url_key = "baseServiceUrl"

    if ENV == "DEV":
        url_key = "devBaseServiceUrl"

    providers = get_providers()
    return list(filter(lambda x: x["providerId"] == provider, providers))[0][url_key]


@lru_cache(maxsize=None)
def load_data_file():
    data_file = DATA_FILE
    read_data_file(data_file)
    return
