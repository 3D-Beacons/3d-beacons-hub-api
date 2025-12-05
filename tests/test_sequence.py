import asyncio

import msgpack
import pytest
from async_asgi_testclient import TestClient
from pydantic import ValidationError
from starlette import status

from app.app import app
from app.constants import (
    JOB_FAILED_ERROR_MESSAGE,
    NO_JOB_FOUND_MESSAGE,
    SEARCH_IN_PROGRESS_MESSAGE,
)
from app.exception import RequestSubmissionException
from app.sequence.helper import submit_sequence_search_job
from app.sequence.schema import SequenceIdType, SequenceOverview
from app.sequence.sequence import fetch_sequence_summary
from tests.utils import StubHttpResponse

client = TestClient(app)


@pytest.mark.asyncio
async def test_search_job_id_from_cache(
    mocker,
    sample_sequence,
    sample_sequence_hash,
):
    mocker.patch(
        "app.sequence.sequence.get_jobdispatcher_id", return_value="non-existing-job-id"
    )

    response = await client.post("/sequence/search", json={"sequence": sample_sequence})

    assert response.json() == {"job_id": sample_sequence_hash}
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_result_api_no_job_id(
    mocker,
):
    mocker.patch("app.sequence.sequence.get_celery_task_id", return_value=None)
    clear_mock = mocker.patch("app.sequence.helper.clear_jobdispatcher_id")

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    clear_mock.assert_called_once()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": NO_JOB_FOUND_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_issue_in_celery_job(
    mocker,
    failed_async_result,
):
    mocker.patch(
        "app.sequence.sequence.get_celery_task_id", return_value="valid-job-id"
    )
    mocker.patch("app.sequence.sequence.AsyncResult", return_value=failed_async_result)
    clear_mock_one = mocker.patch("app.sequence.sequence.clear_jobdispatcher_id")
    clear_mock_two = mocker.patch("app.sequence.sequence.clear_celery_task_id")

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    clear_mock_one.assert_called_once()
    clear_mock_two.assert_called_once()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"message": JOB_FAILED_ERROR_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_pending(mocker, pending_async_result):
    mocker.patch(
        "app.sequence.sequence.get_celery_task_id", return_value="valid-job-id"
    )

    mocker.patch("app.sequence.sequence.AsyncResult", return_value=pending_async_result)

    response = await client.get(
        "/sequence/result?job_id=ncbiblast-2021-01-01-12-12-12",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": SEARCH_IN_PROGRESS_MESSAGE}


@pytest.mark.asyncio
async def test_result_api_valid_job_id_and_job_finished(
    mocker,
    finished_none_async_result,
):
    future = asyncio.Future()
    future.set_result(msgpack.dumps("ncbiblast-2021-01-01-12-12-12"))
    mocker.patch(
        "app.sequence.sequence.get_celery_task_id", return_value="valid-job-id"
    )

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

    with pytest.raises(RequestSubmissionException):
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
        async def test_fetch_sequence_summary_success(mocker):
            # Mock get_services to return a single service
            mocker.patch(
                "app.sequence.sequence.get_services",
                return_value=[
                    {"provider": "test_provider", "accessPoint": "test_access"}
                ],
            )
            # Mock get_base_service_url to return a base url
            mocker.patch(
                "app.sequence.sequence.get_base_service_url",
                return_value="http://test-service",
            )
            # Mock get_final_service_url to return a final url
            mocker.patch(
                "app.sequence.sequence.get_final_service_url",
                return_value="http://test-service/test_access?id=abc&type=sequence",
            )
            # Prepare a valid response
            valid_json = {
                "entry": {"id": "abc", "name": "test_entry"},
                "structures": [
                    {"id": "str1", "provider": "test_provider", "other_field": "value"}
                ],
            }

            # Patch send_async_requests to return a list with a mock response
            class MockResponse:
                status_code = 200

                def json(self):
                    return valid_json

            mocker.patch(
                "app.sequence.sequence.send_async_requests",
                return_value=[MockResponse()],
            )
            # Patch SequenceOverview and Entry to accept the test dicts
            mocker.patch(
                "app.sequence.sequence.SequenceOverview",
                side_effect=lambda **kwargs: type("S", (), kwargs)(),
            )
            mocker.patch(
                "app.sequence.sequence.Entry",
                side_effect=lambda **kwargs: type("E", (), kwargs)(),
            )
            # Patch SequenceSummary to accept the test dicts
            mocker.patch(
                "app.sequence.sequence.SequenceSummary",
                side_effect=lambda **kwargs: type("SS", (), kwargs)(),
            )

            result = await fetch_sequence_summary("abc", SequenceIdType.SEQUENCE)
            assert result is not None

        @pytest.mark.asyncio
        async def test_fetch_sequence_summary_no_services(mocker):
            mocker.patch("app.sequence.sequence.get_services", return_value=[])
            result = await fetch_sequence_summary("abc", SequenceIdType.SEQUENCE)
            assert result is None

        @pytest.mark.asyncio
        async def test_fetch_sequence_summary_no_valid_responses(mocker):
            mocker.patch(
                "app.sequence.sequence.get_services",
                return_value=[
                    {"provider": "test_provider", "accessPoint": "test_access"}
                ],
            )
            mocker.patch(
                "app.sequence.sequence.get_base_service_url",
                return_value="http://test-service",
            )
            mocker.patch(
                "app.sequence.sequence.get_final_service_url",
                return_value="http://test-service/test_access?id=abc&type=sequence",
            )

            # Mock send_async_requests to return a response with non-200 status
            class MockResponse:
                status_code = 404

                def json(self):
                    return {}

            mocker.patch(
                "app.sequence.sequence.send_async_requests",
                return_value=[MockResponse()],
            )
            result = await fetch_sequence_summary("abc", SequenceIdType.SEQUENCE)
            assert result is None

        @pytest.mark.asyncio
        async def test_fetch_sequence_summary_invalid_structure_response(mocker):
            mocker.patch(
                "app.sequence.sequence.get_services",
                return_value=[
                    {"provider": "test_provider", "accessPoint": "test_access"}
                ],
            )
            mocker.patch(
                "app.sequence.sequence.get_base_service_url",
                return_value="http://test-service",
            )
            mocker.patch(
                "app.sequence.sequence.get_final_service_url",
                return_value="http://test-service/test_access?id=abc&type=sequence",
            )
            # Prepare a response with an invalid structure (will raise ValidationError)
            invalid_json = {
                "entry": {"id": "abc", "name": "test_entry"},
                "structures": [
                    {
                        "provider": "test_provider"
                        # missing required fields for SequenceOverview
                    }
                ],
            }

            class MockResponse:
                status_code = 200

                def json(self):
                    return invalid_json

            mocker.patch(
                "app.sequence.sequence.send_async_requests",
                return_value=[MockResponse()],
            )
            # Patch SequenceOverview to raise ValidationError
            mocker.patch(
                "app.sequence.sequence.SequenceOverview",
                side_effect=ValidationError([], model=SequenceOverview),
            )
            result = await fetch_sequence_summary("abc", SequenceIdType.SEQUENCE)
            assert result is None
