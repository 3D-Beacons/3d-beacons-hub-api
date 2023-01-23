import asyncio

import msgpack
import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app
from app.constants import (
    JOB_FAILED_ERROR_MESSAGE,
    NO_JOB_FOUND_MESSAGE,
    SEARCH_IN_PROGRESS_MESSAGE,
)
from app.exception import (
    JobNotFoundException,
    JobResultsNotFoundException,
    RequestSubmissionException,
)
from app.sequence.helper import submit_sequence_search_job
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
    mocker.patch("app.sequence.sequence.RedisCache.hget", return_value=future)

    response = await client.post("/sequence/search", json={"sequence": sample_sequence})

    assert response.json() == {"job_id": sample_sequence_hash}
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_result_api_no_job_id(
    mocker,
):

    future = asyncio.Future()
    future.set_result(None)
    mocker.patch(
        "app.sequence.sequence.RedisCache.hget", side_effect=JobNotFoundException
    )

    mocker.patch("app.sequence.sequence.RedisCache.hdel", return_value=future)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": NO_JOB_FOUND_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_issue_in_celery_job(
    mocker,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.RedisCache.hget", return_value=future)

    mocker.patch("app.sequence.sequence.RedisCache.hdel", return_value=future)

    mocker.patch(
        "app.sequence.sequence.AsyncResult",
        side_effect=JobResultsNotFoundException,
    )

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": NO_JOB_FOUND_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_pending(mocker, pending_async_result):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.RedisCache.hget", return_value=future)

    mocker.patch("app.sequence.sequence.AsyncResult", return_value=pending_async_result)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": SEARCH_IN_PROGRESS_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_not_found(
    mocker,
    failed_async_result,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.RedisCache.hget", return_value=future)

    mocker.patch(
        "app.sequence.sequence.AsyncResult",
        return_value=failed_async_result,
    )

    delete_future = asyncio.Future()
    delete_future.set_result(None)
    delete_mock = mocker.patch(
        "app.sequence.sequence.RedisCache.hdel", return_value=delete_future
    )

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    # must be called twice
    delete_mock.call_count == 2

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": JOB_FAILED_ERROR_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_finished(
    mocker,
    finished_none_async_result,
):

    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch("app.sequence.sequence.RedisCache.hget", return_value=future)

    mocker.patch(
        "app.sequence.sequence.AsyncResult", return_value=finished_none_async_result
    )

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {}


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
