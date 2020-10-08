from functools import lru_cache
import json
import os

from fastapi.params import Query

from app import logger

DATA_FILE = "data.json"


@lru_cache(maxsize=None)
def read_data_file(filename):
    data_filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(data_filepath) as fp:
        data = json.load(fp)
    logger.info(f"Loaded data JSON: {DATA_FILE}")
    return data


def get_services(service_type: str = None, provider: Query = None):
    """ Returns a list of services available.

    Args:
        service_type (str, optional): A type of service.
        provider (Query, optional): A provider.

    Returns:
        list: A list of services based on the parameters passed.
    """
    data_file = DATA_FILE
    data = read_data_file(data_file)
    results = []

    # assuming all services to be returned when no service_type and provider is passed
    if not service_type and not provider:
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

    return results


@lru_cache(maxsize=None)
def get_providers():
    data_file = DATA_FILE
    data = read_data_file(data_file)

    return data["providers"]


def get_base_service_url(provider: str) -> str:
    providers = get_providers()
    return list(filter(lambda x: x["providerId"] == provider, providers))[0][
        "baseServiceUrl"
    ]


@lru_cache(maxsize=None)
def load_data_file():
    data_file = DATA_FILE
    read_data_file(data_file)
    return
