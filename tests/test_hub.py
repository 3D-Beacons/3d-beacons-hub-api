import asyncio

import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app

client = TestClient(app)


# Using 'with TestClient' to test the startup and shutdown events
@pytest.mark.asyncio
async def test_get_uniprot_api(
    mocker, valid_uniprot, valid_uniprot_structures, services
):
    async with TestClient(app) as client:
        future = asyncio.Future()
        future.set_result(valid_uniprot_structures)
        mocker.patch("app.uniprot.uniprot.get_services", return_value=services)
        mocker.patch("app.uniprot.uniprot.send_async_requests", return_value=future)
        response = await client.get(f"/uniprot/{valid_uniprot}.json")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_uniprot_summary_api(
    mocker, valid_uniprot, valid_uniprot_structures_summary, services
):
    future = asyncio.Future()
    future.set_result(valid_uniprot_structures_summary)
    mocker.patch("app.uniprot.uniprot.get_services", return_value=services)
    mocker.patch("app.uniprot.uniprot.send_async_requests", return_value=future)
    response = await client.get(f"/uniprot/summary/{valid_uniprot}.json")
    assert response.status_code == status.HTTP_200_OK
