import json

import pytest

from app.worker.helper import (
    JobResultsNotFoundException,
    filter_json_results,
    get_job_dispatcher_json_results,
    prepare_accession_list,
    prepare_hit_dictionary,
)
from app.worker.schema import AccessionListRequest
from tests.utils import StubHttpResponse


def test_prepare_accession_list():
    accessions = ["P12345", "P23456", "P34567"]
    assert prepare_accession_list(accessions) == AccessionListRequest(
        accessions=accessions
    )


def test_filter_json_results_90(seq_search_response):
    assert len(filter_json_results(seq_search_response.data, 90)) == 6


def test_filter_json_results_95(seq_search_response):
    assert len(filter_json_results(seq_search_response.data, 95)) == 4


def test_prepare_hit_dictionary(seq_search_response):
    filtered_hits = filter_json_results(seq_search_response.data, 95)
    expected_hit_dictionary = {}

    with open("tests/stubs/hit_dictionary.json", "r") as f:
        expected_hit_dictionary = json.loads(f.read())

    assert prepare_hit_dictionary(filtered_hits) == expected_hit_dictionary


@pytest.mark.asyncio
async def test_get_job_dispatcher_json_results_valid(mocker, sample_sequence_hash):
    mocker.patch(
        "app.worker.helper.requests.get",
        return_value=StubHttpResponse(status_code=200, data={"results": "results"}),
    )

    assert get_job_dispatcher_json_results(sample_sequence_hash) == {
        "results": "results"
    }


@pytest.mark.asyncio
async def test_get_job_dispatcher_json_results_invalid(mocker, sample_sequence_hash):

    mocker.patch("app.worker.helper.requests.get", return_value=None)

    with pytest.raises(JobResultsNotFoundException):
        assert get_job_dispatcher_json_results(sample_sequence_hash)
