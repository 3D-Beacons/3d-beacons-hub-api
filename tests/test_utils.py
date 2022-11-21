from app.uniprot.uniprot import filter_on_checksum
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
