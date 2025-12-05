from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FeatureType(Enum):
    CARBOHYD = "CARBOHYD"
    DOMAIN = "DOMAIN"
    ACT_SITE = "ACT_SITE"
    METAL = "METAL"
    BINDING = "BINDING"
    NON_STD = "NON_STD"
    MOD_RES = "MOD_RES"
    DISULFID = "DISULFID"
    MUTAGEN = "MUTAGEN"
    HELIX = "HELIX"
    STRAND = "STRAND"
    DISORDERED = "DISORDERED"
    INTERFACE = "INTERFACE"
    CHANNEL = "CHANNEL"

    def __str__(self) -> str:
        return self.value


class Region(BaseModel):
    start: int = Field(
        ...,
        description="The first position of the annotation",
        json_schema_extra={"example": 23},
    )
    end: int = Field(
        ...,
        description="The last position of the annotation",
        json_schema_extra={"example": 42},
    )
    annotation_value: str = Field(
        None,
        description="The value of the annotation",
        json_schema_extra={"example": "0.9"},
    )
    unit: str = Field(
        None,
        description="The unit of the annotation value, if applicable",
        json_schema_extra={"example": "mmol"},
    )


class Evidence(Enum):
    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    COMPUTATIONAL_PREDICTED = "COMPUTATIONAL/PREDICTED"
    FROM_LITERATURE = "FROM LITERATURE"


class FeatureItem(BaseModel):
    type: FeatureType = Field(
        ...,
        description="Type of the annotation",
        json_schema_extra={"example": "ACT_SITE"},
    )
    description: str = Field(
        ...,
        description="Description/Label of the annotation",
        json_schema_extra={"example": "Pfam N1221 (PF07923})"},
    )
    source_name: Optional[str] = Field(
        None,
        description="Name of the source of the annotations, i.e. where is "
        "the data from",
    )
    source_url: Optional[str] = Field(
        None,
        description="URL of the source of the annotation, i.e. where to find more data",
    )
    evidence: Optional[Evidence] = Field(
        None, description="Evidence category of the annotation"
    )
    residues: Optional[List[int]] = Field(
        None, description="An array of residue indices"
    )
    regions: Optional[List[Region]] = Field(None)


class Annotation(BaseModel):
    accession: str = Field(
        ..., description="A UniProt accession", json_schema_extra={"example": "P00734"}
    )
    id: Optional[str] = Field(
        None,
        description="A UniProt identifier",
        json_schema_extra={"example": "FGFR2_HUMAN"},
    )
    sequence: str = Field(
        ...,
        description="The sequence of the protein",
        json_schema_extra={"example": "AFFGVAATRKL"},
    )
    annotation: Optional[List[FeatureItem]] = None
