import hashlib
import json
from typing import List

import pytest

from app.uniprot.schema import UniprotSummary
from tests.utils import StubResponse


class AsyncResult:
    def __init__(self, status, result):
        self.result = result
        self.status = status


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
def valid_uniprot_structures_summary():
    valid_structures = []
    valid_structures.append(StubResponse(status_code=200, stub_for="uniprot_summary"))
    return valid_structures


@pytest.fixture(scope="session")
def registry():
    with open("tests/stubs/registry.json") as fp:
        data = json.load(fp)
        return data


@pytest.fixture(scope="session")
def valid_gifts_response():
    with open("tests/stubs/gifts_response.json") as fp:
        data = json.load(fp)
        return data


@pytest.fixture(scope="session")
def valid_uniprot_list_summary():
    return StubResponse(status_code=200, stub_for="uniprot_list_summary")


@pytest.fixture(scope="session")
def seq_search_response():
    return StubResponse(status_code=200, stub_for="seq_search_response")


@pytest.fixture(scope="session")
def sample_sequence():
    return "MVLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSH"


@pytest.fixture(scope="session")
def sample_sequence_hash():
    return hashlib.md5("MVLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSH".encode()).hexdigest()


@pytest.fixture(scope="session")
def uniprot_summary_obj_list():
    summary_results: List[UniprotSummary] = []

    with open("tests/stubs/uniprot_list_summary.json") as f:
        for item in json.load(f):
            summary_results.append(UniprotSummary(**item))

    return summary_results


@pytest.fixture(scope="session")
def uniprot_details():
    with open("tests/stubs/uniprot.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def uniprot_summary():
    with open("tests/stubs/uniprot_summary.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def pending_async_result():
    return AsyncResult("PENDING", None)


@pytest.fixture(scope="session")
def failed_async_result():
    return AsyncResult("FAILURE", None)


@pytest.fixture(scope="session")
def finished_none_async_result():
    return AsyncResult("SUCCESS", None)
