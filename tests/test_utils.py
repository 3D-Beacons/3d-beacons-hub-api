import json

from app.config import get_base_service_url, get_services
from app.sequence.helper import (
    filter_json_results,
    prepare_accession_list,
    prepare_hit_dictionary,
)
from app.uniprot.schema import AccessionListRequest
from app.uniprot.uniprot import filter_on_checksum, get_first_entry_with_checksum
from app.utils import get_final_service_url
from app.version import __version__


def test_get_final_service_url():
    assert (
        get_final_service_url("http://example.com", "api", "v1")
        == f"http://example.com/api/v1?version={__version__}"
    )


def test_filter_on_checksum():
    in_list = [
        {"uniprot_entry": {"uniprot_checksum": "123"}},
        {"uniprot_entry": {"uniprot_checksum": "1234"}},
        {"uniprot_entry": {}},
    ]

    assert filter_on_checksum(in_list, "123") == [
        {"uniprot_entry": {"uniprot_checksum": "123"}}
    ]


def test_get_first_entry_with_checksum_valid():
    in_list = [
        {"uniprot_entry": {"ac": "P12345"}},
        {"uniprot_entry": {"ac": "P23456", "uniprot_checksum": "123"}},
        {"uniprot_entry": {"ac": "P34567", "uniprot_checksum": "123"}},
    ]

    assert get_first_entry_with_checksum(in_list) == {
        "ac": "P23456",
        "uniprot_checksum": "123",
    }


def test_get_first_entry_with_checksum_none():
    in_list = []

    assert not get_first_entry_with_checksum(in_list)


def test_get_first_entry_with_checksum_valid_no_checksum():
    in_list = [
        {"uniprot_entry": {"ac": "P12345"}},
        {"uniprot_entry": {"ac": "P23456"}},
        {"uniprot_entry": {"ac": "P34567"}},
    ]

    assert get_first_entry_with_checksum(in_list) == {"ac": "P12345"}


def test_get_services(mocker, registry):
    mocker.patch("app.config.read_data_file", return_value=registry)
    assert get_services(service_type="serviceOne") == [
        {
            "serviceType": "serviceOne",
            "provider": "providerOne",
            "accessPoint": "service/",
        },
        {
            "serviceType": "serviceOne",
            "provider": "providerTwo",
            "accessPoint": "service/v/",
        },
    ]


def test_get_services_exclude_provider(mocker, registry):

    mocker.patch("app.config.read_data_file", return_value=registry)
    assert get_services(service_type="serviceOne", exclude_provider="providerTwo") == [
        {
            "serviceType": "serviceOne",
            "provider": "providerOne",
            "accessPoint": "service/",
        },
    ]


def test_get_services_provider(mocker, registry):
    mocker.patch("app.config.read_data_file", return_value=registry)
    assert get_services(service_type="serviceOne", provider="providerOne") == [
        {
            "serviceType": "serviceOne",
            "provider": "providerOne",
            "accessPoint": "service/",
        },
    ]


def test_get_base_service_url(mocker, registry):
    mocker.patch("app.config.get_providers", return_value=registry["providers"])
    assert (
        get_base_service_url("providerOneId") == "https://providerOneDevBaseServiceUrl"
    )


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
