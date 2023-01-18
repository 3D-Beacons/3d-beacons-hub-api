import asyncio

import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app

client = TestClient(app)


# Using 'with TestClient' to test the startup and shutdown events
@pytest.mark.asyncio
async def test_get_uniprot_api(
    mocker, valid_uniprot, valid_uniprot_structures, registry
):
    async with TestClient(app) as client:
        future = asyncio.Future()
        future.set_result(valid_uniprot_structures)
        mocker.patch(
            "app.uniprot.uniprot.get_services", return_value=registry["services"]
        )
        mocker.patch("app.uniprot.uniprot.send_async_requests", return_value=future)
        mocker.patch(
            "app.uniprot.uniprot.get_base_service_url", return_value="http://test"
        )
        response = await client.get(f"/uniprot/{valid_uniprot}.json")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_uniprot_summary_api(
    mocker, valid_uniprot, valid_uniprot_structures_summary, registry
):
    future = asyncio.Future()
    future.set_result(valid_uniprot_structures_summary)
    mocker.patch("app.uniprot.uniprot.get_services", return_value=registry["services"])
    mocker.patch("app.uniprot.uniprot.send_async_requests", return_value=future)
    mocker.patch("app.uniprot.uniprot.get_base_service_url", return_value="http://test")
    response = await client.get(f"/uniprot/summary/{valid_uniprot}.json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_uniprot_summaries_api(
    mocker, valid_uniprot_structures_summary, registry
):
    future = asyncio.Future()
    future.set_result(valid_uniprot_structures_summary)
    mocker.patch("app.uniprot.uniprot.get_services", return_value=registry["services"])
    mocker.patch("app.uniprot.uniprot.send_async_requests", return_value=future)
    mocker.patch("app.uniprot.uniprot.get_base_service_url", return_value="http://test")
    response = await client.post(
        "/uniprot/summary", json={"accessions": ["P12345", "P23456"]}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_ensembl_summaries_api(
    mocker,
    valid_gifts_response,
    uniprot_summary_obj_list,
):
    gifts_future = asyncio.Future()
    gifts_future.set_result(valid_gifts_response)
    mocker.patch("app.ensembl.ensembl.get_ensembl_mappings", return_value=gifts_future)

    uniprot_list_future = asyncio.Future()
    uniprot_list_future.set_result(uniprot_summary_obj_list)
    mocker.patch(
        "app.ensembl.ensembl.get_list_of_uniprot_summary_helper",
        return_value=uniprot_list_future,
    )

    response = await client.get(
        "/ensembl/summary/ENSG00000288864.json",
    )

    assert response.status_code == status.HTTP_200_OK
