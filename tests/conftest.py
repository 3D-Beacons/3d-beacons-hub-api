import json

import pytest
from tests.utils import StubResponse


@pytest.fixture(scope="session")
def invalid_uniprot():
    return "X0"


@pytest.fixture(scope="session")
def valid_uniprot():
    return "P0DTD1"


@pytest.fixture(scope="session")
def valid_uniprot_structures():
    valid_structures = []
    valid_structures.append(StubResponse(status_code=200, stub_for="uniprot"))
    return valid_structures


@pytest.fixture(scope="session")
def services():
    with open("app/config/data.json") as fp:
        data = json.load(fp)
        return data["services"]
