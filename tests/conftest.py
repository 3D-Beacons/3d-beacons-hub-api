import pytest


@pytest.fixture(scope="session")
def invalid_uniprot():
    return "X0"


@pytest.fixture(scope="session")
def valid_uniprot():
    return "P0DTD1"
