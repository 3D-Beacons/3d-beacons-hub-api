import asyncio

import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app

client = TestClient(app)


# Using 'with TestClient' to test the startup and shutdown events
@pytest.mark.asyncio
async def test_get_uniprot_api(mocker, valid_uniprot, uniprot_details, registry):
    async with TestClient(app) as client:
        future = asyncio.Future()
        future.set_result(uniprot_details)
        mocker.patch(
            "app.uniprot.helper.get_services", return_value=registry["services"]
        )
        mocker.patch("app.uniprot.uniprot.get_uniprot_helper", return_value=future)
        mocker.patch(
            "app.uniprot.helper.get_base_service_url", return_value="http://test"
        )
        response = await client.get(f"/uniprot/{valid_uniprot}.json")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_uniprot_summary_api(
    mocker, valid_uniprot, uniprot_summary, registry
):
    future = asyncio.Future()
    future.set_result(uniprot_summary)
    mocker.patch("app.uniprot.helper.get_services", return_value=registry["services"])
    mocker.patch("app.uniprot.uniprot.get_uniprot_summary_helper", return_value=future)
    mocker.patch("app.uniprot.helper.get_base_service_url", return_value="http://test")
    response = await client.get(f"/uniprot/summary/{valid_uniprot}.json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_uniprot_summaries_api(mocker, uniprot_summary_obj_list, registry):
    future = asyncio.Future()
    future.set_result(uniprot_summary_obj_list)
    mocker.patch("app.uniprot.helper.get_services", return_value=registry["services"])
    mocker.patch(
        "app.uniprot.uniprot.get_list_of_uniprot_summary_helper", return_value=future
    )
    mocker.patch("app.uniprot.helper.get_base_service_url", return_value="http://test")
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
    mocker.patch(
        "app.ensembl.ensembl.get_ensembl_mappings", return_value=valid_gifts_response
    )

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


@pytest.mark.asyncio
async def test_annotations_api(
    mocker, valid_annotation_response, registry, valid_uniprot
):
    future = asyncio.Future()
    future.set_result(valid_annotation_response)
    mocker.patch(
        "app.annotations.annotations.get_services", return_value=registry["services"]
    )
    mocker.patch(
        "app.annotations.annotations.get_annotations_api_helper", return_value=future
    )
    mocker.patch(
        "app.annotations.annotations.get_base_service_url", return_value="http://test"
    )
    response = await client.get(f"/annotations/{valid_uniprot}.json?type=DOMAIN")
    assert response.status_code == status.HTTP_200_OK
