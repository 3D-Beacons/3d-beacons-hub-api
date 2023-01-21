from typing import List, Optional

from pydantic import BaseModel, Field


class AccessionListRequest(BaseModel):
    accessions: List[str] = Field(
        ..., description="A list of UniProt accessions", example=["P00734", "P38398"]
    )
    provider: str = Field(
        None, description="Name of the model provider", example="swissmodel"
    )
    exclude_provider: Optional[str] = Field(
        None, description="Provider to exclude.", example="pdbe"
    )
