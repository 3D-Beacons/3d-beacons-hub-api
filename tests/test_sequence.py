import asyncio

import msgpack
import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app
from app.exception import (
    JobNotFoundException,
    JobResultsNotFoundException,
    JobStatusNotFoundException,
    RequestSubmissionException,
)
from app.sequence.helper import (
    get_job_id,
    get_job_json_results,
    prepare_dictionary_of_summary_results,
    submit_sequence_search_job,
)
from app.sequence.sequence import prepare_finished_job
from tests.utils import StubHttpResponse

client = TestClient(app)


@pytest.mark.asyncio
async def test_search_job_id_from_cache(
    mocker,
    sample_sequence,
    sample_sequence_hash,
):

    future = asyncio.Future()
    future.set_result("job_12jkjskjk")
    mocker.patch("app.sequence.sequence.get_job_id", return_value=future)

    response = await client.post("/sequence/search", json={"sequence": sample_sequence})

    assert response.json() == {"job_id": sample_sequence_hash}
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_result_api_no_job_id(
    mocker,
):

    future = asyncio.Future()
    future.set_result(None)
    mocker.patch("app.sequence.sequence.get_job_id", side_effect=JobNotFoundException)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": "No search request found for this sequence"}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_no_job_result_in_cache(
    mocker,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.get_job_id", return_value=future)

    # no job results in cache
    mocker.patch(
        "app.sequence.sequence.get_job_results_from_cache",
        side_effect=JobResultsNotFoundException,
    )

    # not a valid JD job id
    mocker.patch(
        "app.sequence.sequence.get_job_status", side_effect=JobStatusNotFoundException
    )

    delete_future = asyncio.Future()
    delete_future.set_result(None)
    delete_mock = mocker.patch(
        "app.sequence.sequence.delete_from_cache", return_value=delete_future
    )

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    # should call delete_from_cache twice
    assert delete_mock.call_count == 2

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": "No search request found for this sequence"}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_running(
    mocker,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.get_job_id", return_value=future)

    # job results in cache
    mocker.patch(
        "app.sequence.sequence.get_job_results_from_cache",
        side_effect=JobResultsNotFoundException,
        return_value=None,
    )

    delete_future = asyncio.Future()
    delete_future.set_result(None)
    mocker.patch("app.sequence.sequence.delete_from_cache", return_value=delete_future)

    job_status_future = asyncio.Future()
    job_status_future.set_result("RUNNING")
    mocker.patch("app.sequence.sequence.get_job_status", return_value=job_status_future)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "message": "Search in progress, please try after sometime!"
    }


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_not_found(
    mocker,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.get_job_id", return_value=future)

    # job results in cache
    mocker.patch(
        "app.sequence.sequence.get_job_results_from_cache",
        side_effect=JobResultsNotFoundException,
        return_value=None,
    )

    delete_future = asyncio.Future()
    delete_future.set_result(None)
    delete_mock = mocker.patch(
        "app.sequence.sequence.delete_from_cache", return_value=delete_future
    )

    job_status_future = asyncio.Future()
    job_status_future.set_result("NOT_FOUND")
    mocker.patch("app.sequence.sequence.get_job_status", return_value=job_status_future)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    # should call delete_from_cache twice
    assert delete_mock.call_count == 2

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": "No search request found for this sequence"}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_finished(
    mocker,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.get_job_id", return_value=future)

    # job results in cache
    mocker.patch(
        "app.sequence.sequence.get_job_results_from_cache",
        side_effect=JobResultsNotFoundException,
        return_value=None,
    )

    delete_future = asyncio.Future()
    delete_future.set_result(None)
    mocker.patch("app.sequence.sequence.delete_from_cache", return_value=delete_future)

    job_status_future = asyncio.Future()
    job_status_future.set_result("FINISHED")
    mocker.patch("app.sequence.sequence.get_job_status", return_value=job_status_future)

    prepare_job_result_future = asyncio.Future()
    prepare_job_result_future.set_result(None)
    prepare_job_result_mock = mocker.patch(
        "app.sequence.sequence.prepare_finished_job",
        return_value=prepare_job_result_future,
    )

    await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    prepare_job_result_mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_job_id_valid_job(mocker, sample_sequence_hash):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.helper.RedisCache.hget", return_value=future)

    assert await get_job_id(sample_sequence_hash) == "ncbiblast-2021-01-01-12-12-12"


@pytest.mark.asyncio
async def test_get_job_id_invalid_job(mocker, sample_sequence_hash):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("2021-01-01-12-12-12"))
    mocker.patch("app.sequence.helper.RedisCache.hget", return_value=future)

    with pytest.raises(JobNotFoundException):
        await get_job_id(sample_sequence_hash)


@pytest.mark.asyncio
async def test_get_job_json_results_valid(mocker, sample_sequence_hash):

    future = asyncio.Future()
    future.set_result(StubHttpResponse(status_code=200, data={"results": "results"}))
    mocker.patch("app.sequence.helper.request_get", return_value=future)

    assert await get_job_json_results(sample_sequence_hash) == {"results": "results"}


@pytest.mark.asyncio
async def test_get_job_json_results_invalid(mocker, sample_sequence_hash):

    future = asyncio.Future()
    future.set_result(None)
    mocker.patch("app.sequence.helper.request_get", return_value=future)

    with pytest.raises(JobResultsNotFoundException):
        assert await get_job_json_results(sample_sequence_hash)


@pytest.mark.asyncio
async def test_submit_sequence_search_job_valid(mocker, sample_sequence):

    future = asyncio.Future()
    future.set_result(
        StubHttpResponse(status_code=200, data="ncbiblast-2021-01-01-12-12-12")
    )
    mocker.patch("app.sequence.helper.request_post", return_value=future)

    assert (
        await submit_sequence_search_job(sample_sequence)
        == "ncbiblast-2021-01-01-12-12-12"
    )


@pytest.mark.asyncio
async def test_submit_sequence_search_job_invalid(mocker, sample_sequence):

    future = asyncio.Future()
    future.set_result(None)
    mocker.patch("app.sequence.helper.request_post", return_value=future)

    with pytest.raises(RequestSubmissionException):
        assert await submit_sequence_search_job(sample_sequence)


@pytest.mark.asyncio
async def test_prepare_dictionary_of_summary_results(mocker, uniprot_summary_obj_list):
    future = asyncio.Future()
    future.set_result(uniprot_summary_obj_list)
    mocker.patch(
        "app.sequence.helper.get_list_of_uniprot_summary_helper", return_value=future
    )

    response = await prepare_dictionary_of_summary_results(
        ["P07550", "P07551", "P07552", "A0A8I5KS94", "A0A8I5KWH8"]
    )

    assert len(response.keys()) == 5
    assert not response["P07551"]
    assert not response["P07552"]


@pytest.mark.asyncio
async def test_prepare_finished_job_no_job_results(
    mocker,
):

    future = asyncio.Future()
    future.set_result(None)
    mocker.patch("app.sequence.sequence.get_job_json_results", return_value=future)

    response = await prepare_finished_job("ncbiblast-2021-01-01-12-12-12", 0)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_prepare_finished_job_with_job_results_and_no_summary(
    mocker, seq_search_response
):

    future = asyncio.Future()
    future.set_result(seq_search_response.json())
    mocker.patch("app.sequence.sequence.get_job_json_results", return_value=future)

    set_cache_future = asyncio.Future()
    set_cache_future.set_result(None)
    set_cache_mock = mocker.patch(
        "app.sequence.sequence.set_job_results_in_cache", return_value=set_cache_future
    )

    prepare_summary_future = asyncio.Future()
    prepare_summary_future.set_result(None)
    mocker.patch(
        "app.sequence.sequence.prepare_summary_result",
        return_value=prepare_summary_future,
    )

    response = await prepare_finished_job("ncbiblast-2021-01-01-12-12-12", 0)

    # should set the job results in cache
    set_cache_mock.assert_called_once()

    assert response.status_code == status.HTTP_404_NOT_FOUND
