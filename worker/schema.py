from typing import List, Optional

from pydantic import BaseModel, Field


class AccessionListRequest(BaseModel):
    accessions: List[str] = Field(
        ...,
        description="A list of UniProt accessions",
        json_schema_extra={"example": ["P00734", "P38398"]},
    )
    provider: Optional[str] = Field(
        None,
        description="Name of the model provider",
        json_schema_extra={"example": "swissmodel"},
    )
    exclude_provider: Optional[str] = Field(
        None, description="Provider to exclude.", json_schema_extra={"example": "pdbe"}
    )
