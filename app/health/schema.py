from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# Health Endpoint Models
class HealthStatusEnum(str, Enum):
    """Health status enumeration based on the OpenAPI spec"""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class HealthStatus(BaseModel):
    """Individual service health status model for /health endpoint"""

    status: HealthStatusEnum = Field(..., description="The status of the service")
    service_id: str = Field(
        ...,
        description="The identifier of the service, corresponds to the provider ID "
        "in the registry",
    )
    beacons_api_version: str = Field(
        ..., description="The version of the 3DBeacons API"
    )
    output: Optional[str] = Field(
        None, description="Raw error output, in case of 'fail' or 'warn' states"
    )


class HealthResponse(BaseModel):
    """Response model for /health endpoint - returns array of status objects"""

    __root__: List[HealthStatus] = Field(
        ..., description="List of service health statuses"
    )
