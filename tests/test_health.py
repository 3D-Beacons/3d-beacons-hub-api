from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, status
from starlette.testclient import TestClient

from app.health.health import health_route

app = FastAPI()
app.include_router(health_route, prefix="/health")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
@patch("app.health.health.get_services")
@patch("app.health.health.get_base_service_url")
@patch("app.health.health.get_final_service_url")
@patch("app.health.health.send_async_requests", new_callable=AsyncMock)
async def test_health_check_success(
    mock_send_async_requests,
    mock_get_final_service_url,
    mock_get_base_service_url,
    mock_get_services,
    client,
):
    # Mock service discovery
    mock_get_services.return_value = [
        {"provider": "pdbe", "accessPoint": "/api/health"}
    ]
    mock_get_base_service_url.return_value = "http://mocked"
    mock_get_final_service_url.return_value = "http://mocked/api/health"

    # Mock response from downstream service
    class MockResponse:
        status_code = status.HTTP_200_OK

        def json(self):
            return [
                {
                    "status": "pass",
                    "service_id": "pdbe",
                    "beacons_api_version": "2.7.0",
                    "output": "",
                }
            ]

    mock_send_async_requests.return_value = [MockResponse()]

    response = client.get("/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("application/health+json")
    assert response.json() == [
        {
            "status": "pass",
            "service_id": "pdbe",
            "beacons_api_version": "2.7.0",
            "output": "",
        }
    ]


@pytest.mark.asyncio
@patch("app.health.health.get_services")
@patch("app.health.health.get_base_service_url")
@patch("app.health.health.get_final_service_url")
@patch("app.health.health.send_async_requests", new_callable=AsyncMock)
async def test_health_check_failure(
    mock_send_async_requests,
    mock_get_final_service_url,
    mock_get_base_service_url,
    mock_get_services,
    client,
):
    mock_get_services.return_value = [
        {"provider": "pdbe", "accessPoint": "/api/health"}
    ]
    mock_get_base_service_url.return_value = "http://mocked"
    mock_get_final_service_url.return_value = "http://mocked/api/health"

    class MockResponse:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        def json(self):
            return [
                {
                    "status": "fail",
                    "service_id": "pdbe",
                    "beacons_api_version": "2.7.0",
                    "output": "Service is unhealthy, not able to reach the backend!",
                }
            ]

    mock_send_async_requests.return_value = [MockResponse()]

    response = client.get("/health/")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.headers["content-type"].startswith("application/health+json")
    assert response.json() == [
        {
            "status": "fail",
            "service_id": "pdbe",
            "beacons_api_version": "2.7.0",
            "output": "Service is unhealthy, not able to reach the backend!",
        }
    ]
