from app.utils import get_final_service_url
from app.version import __version__


def test_get_final_service_url():
    assert (
        get_final_service_url("http://example.com", "api", "v1")
        == f"http://example.com/api/v1?version={__version__}"
    )
