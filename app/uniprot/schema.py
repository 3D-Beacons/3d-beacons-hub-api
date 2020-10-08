from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class UniProtEntry(BaseModel):
    uniprot_md5: Optional[str] = Field(
        None, description="MD5 hash of the UniProt sequence"
    )
    sequence_length: int = Field(
        ..., description="Length of the UniProt sequence, e.g. 100"
    )
    ac: str = Field(..., description="UniProt accession, e.g. P00520")
    id: str = Field(..., description="UniProt identifier, e.g. ABL1_MOUSE")


class InComplexWithItem(BaseModel):
    chain_id: str = Field(..., description="Chain identifier of the macromolecule")
    name: str = Field(..., description="Name of the macromolecule")
    id: Optional[str] = Field(None, description="UniProt identifier, e.g. ABL1_MOUSE")
    ac: Optional[str] = Field(None, description="UniProt accession, e.g. P00520")


class ExperimentalMethod(Enum):
    ELECTRON_CRYSTALLOGRAPHY = "ELECTRON CRYSTALLOGRAPHY"
    ELECTRON_MICROSCOPY = "ELECTRON MICROSCOPY"
    EPR = "EPR"
    FIBER_DIFFRACTION = "FIBER DIFFRACTION"
    FLUORESCENCE_TRANSFER = "FLUORESCENCE TRANSFER"
    INFRARED_SPECTROSCOPY = "INFRARED SPECTROSCOPY"
    NEUTRON_DIFFRACTION = "NEUTRON DIFFRACTION"
    POWDER_DIFFRACTION = "POWDER DIFFRACTION"
    SOLID_STATE_NMR = "SOLID-STATE NMR"
    SOLUTION_NMR = "SOLUTION NMR"
    SOLUTION_SCATTERING = "SOLUTION SCATTERING"
    THEORETICAL_MODEL = "THEORETICAL MODEL"
    X_RAY_DIFFRACTION = "X-RAY DIFFRACTION"


class Template(BaseModel):
    template_id: str = Field(
        ..., description="Identifier of the templates, e.g. PDB id"
    )
    chain_id: str = Field(..., description="Identifier of the chain of the template")
    template_sequence_identity: float = Field(
        ..., description="Sequence identity of the template with the UniProt accession"
    )
    last_updated: str = Field(..., description="Date stamp in the format of yyyy/mm/dd")
    provider: str = Field(..., description="Provider of the template, e.g. PDB")
    experimental_method: ExperimentalMethod = Field(
        ..., description="Experimental method used to determine the template"
    )
    resolution: float = Field(..., description="Resolution of the template")
    preferred_assembly_id: Optional[str] = Field(
        None, description="Identifier of the preferred assembly of the template"
    )


class Seqres(BaseModel):
    aligned_sequence: str = Field(..., description="Sequence of the model")
    from_: int = Field(
        ..., alias="from", description="Residue number of the first residue"
    )
    to: int = Field(..., description="Residue number of the last residue")


class UniProt(BaseModel):
    aligned_sequence: str = Field(..., description="Sequence of the UniProt accession")
    from_: int = Field(
        ..., alias="from", description="Residue number of the first residue"
    )
    to: int = Field(..., description="Residue number of the last residue")


class Residue(BaseModel):
    qmean: Optional[float] = Field(None, description="QMEAN score")
    model_residue_label: str = Field(..., description="Model residue index")
    uniprot_residue_number: int = Field(..., description="UniProt residue index")


class Segment(BaseModel):
    templates: Optional[List[Template]] = Field(
        None, description="Information on the template(s) used for the model"
    )
    seqres: Seqres = Field(..., description="Information on the sequence of the model")
    uniprot: UniProt
    residues: List[Residue]


class Chain(BaseModel):
    chain_id: str
    segments: Optional[List[Segment]] = None


class Structure(BaseModel):
    model_identifier: Optional[str] = Field(
        None, description="Identifier of the model, e.g. a PDB id"
    )
    provider: str = Field(..., description="Name of the model provider")
    created: str = Field(
        ..., description="Datetime stamp in the format of yyyy/mm/dd hh:mm:ss"
    )
    sequence_identity: Optional[float] = Field(
        None, description="Sequence identity of the model to the UniProt sequence"
    )
    oligo_state: str = Field(
        ..., description="Oligomeric state of the model, e.g. monomer"
    )
    preferred_assembly_id: Optional[str] = Field(
        None, description="Identifier of the preferred assembly in the model"
    )
    coverage: float = Field(
        ..., description="Percentage of the UniProt sequence covered by the model"
    )
    qmean_version: Optional[str] = Field(
        None, description="Version of QMEAN used to calculate quality"
    )
    qmean_avg_local_score: Optional[float] = Field(
        None, description="Average of the local QMEAN scores"
    )
    coordinates_url: str = Field(..., description="URL of the model coordinates")
    in_complex_with: Optional[List[InComplexWithItem]] = Field(
        None,
        description="Information on any macromolecules in complex with the "
        "protein of interest",
    )
    chains: List[Chain]


class Result(BaseModel):
    uniprot_entry: UniProtEntry = Field(
        ..., description="Information on the UniProt accession the data corresponds to"
    )
    structures: List[Structure] = Field(
        ...,
        description="Information on the structures available for the UniProt accession",
    )
