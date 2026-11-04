import asyncio

import pytest
from async_asgi_testclient import TestClient
from starlette import status

from app.app import app
from app.uniprot.helper import get_uniprot_summary_helper
from app.version import __major__version__

client = TestClient(app)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("template", "expected_template"),
    [("1abc.1/A", "&template=1abc.1%2FA"), (None, "")],
)
async def test_uniprot_summary_forwards_beacon_query_filters(
    mocker, valid_uniprot_structures_summary, template, expected_template
):
    services = [
        {"provider": "provider-one", "accessPoint": "summary/"},
        {"provider": "provider-two", "accessPoint": "summary/"},
    ]
    get_services = mocker.patch("app.uniprot.helper.get_services", return_value=services)
    mocker.patch(
        "app.uniprot.helper.get_base_service_url",
        side_effect=lambda provider: f"https://{provider}.example/",
    )
    send_requests = mocker.patch(
        "app.uniprot.helper.send_async_requests",
        return_value=valid_uniprot_structures_summary,
    )

    await get_uniprot_summary_helper(
        "P38398",
        provider="provider-one",
        template=template,
        res_range="10-20",
    )

    get_services.assert_called_once_with(
        service_type="summary", provider="provider-one", exclude_provider=None
    )
    assert send_requests.call_args.args[0] == [
        f"https://provider-one.example/summary/P38398.json?version={__major__version__}&range=10-20"
        f"{expected_template}",
        f"https://provider-two.example/summary/P38398.json?version={__major__version__}&range=10-20"
        f"{expected_template}",
    ]


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

    mocker.patch(
        "app.ensembl.ensembl.get_list_of_uniprot_summary_helper",
        return_value=uniprot_summary_obj_list,
    )
    mocker.patch(
        "app.ensembl.ensembl.get_uniprot_api_results",
        return_value={},
    )
    mocker.patch(
        "app.ensembl.ensembl.get_uniprot_name",
        return_value="Test protein",
    )

    response = await client.get(
        "/ensembl/summary/ENSG00000288864.json",
    )

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["uniprot_mappings"]
    assert all(
        isinstance(mapping["ensembl_transcript"]["transcript_id"], str)
        for mapping in response_json["uniprot_mappings"]
    )


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
