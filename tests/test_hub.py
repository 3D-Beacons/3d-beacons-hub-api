from fastapi.testclient import TestClient
from starlette import status

from app.app import app

client = TestClient(app)


# Using 'with TestClient' to test the startup and shutdown events
def test_get_uniprot_api_no_range(valid_uniprot):
    with TestClient(app) as client:
        response = client.get(f"/uniprot/{valid_uniprot}.json")
        assert response.status_code == status.HTTP_200_OK


def test_get_uniprot_api_with_range(valid_uniprot):
    response = client.get(f"/uniprot/{valid_uniprot}.json?range=10-50")
    assert response.status_code == status.HTTP_200_OK
