from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.config import get_base_service_url, get_services
from app.health.schema import HealthResponse, HealthStatus
from app.utils import get_final_service_url, send_async_requests

health_route = APIRouter()


@health_route.get(
    "/",
    summary="Health Check",
    description="Returns the health status of all the beacons.",
    response_model=HealthResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Service is healthy.",
            "content": {
                "application/health+json": {
                    "example": [
                        {
                            "status": "pass",
                            "service_id": "pdbe",
                            "beacons_api_version": "2.7.0",
                            "output": "",
                        }
                    ]
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Service is down or unhealthy.",
            "content": {
                "application/health+json": {
                    "example": [
                        {
                            "status": "fail",
                            "service_id": "pdbe",
                            "beacons_api_version": "2.7.0",
                            "output": "Service is unhealthy, not able to "
                            "reach the backend!",
                        }
                    ]
                }
            },
        },
    },
)
async def health_check():
    """
    Returns the health status of all the beacons.
    """
    services = get_services(service_type="health")
    calls = []
    for service in services:
        base_url = get_base_service_url(service["provider"])
        final_url = get_final_service_url(base_url, service["accessPoint"])

        calls.append(final_url)

    result = await send_async_requests(calls)
    final_result = []

    failed = False
    for beacons_response in result:
        if beacons_response.status_code != status.HTTP_200_OK:
            # If any service returns a non-200 status, we consider the
            # overall health check as failed
            failed = True
        for beacons_status in beacons_response.json():
            final_result.append(HealthStatus(**beacons_status))

    if failed:
        return JSONResponse(
            media_type="application/health+json",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(final_result),
        )
    return JSONResponse(
        media_type="application/health+json",
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(final_result),
    )
