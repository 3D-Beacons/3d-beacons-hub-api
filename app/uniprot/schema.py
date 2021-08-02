from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.constants import UNIPROT_AC_DESC, UNIPROT_ID_DESC


class ModelFormat(Enum):
    PDB = "PDB"
    MMCIF = "MMCIF"
    BCIF = "BCIF"


class UniProtEntry(BaseModel):
    uniprot_md5: Optional[str] = Field(
        None, description="MD5 hash of the UniProt sequence"
    )
    sequence_length: Optional[int] = Field(
        None, description="Length of the UniProt sequence, e.g. 100"
    )
    ac: str = Field(..., description=UNIPROT_AC_DESC)
    id: Optional[str] = Field(None, description=UNIPROT_ID_DESC)


class InComplexWithItem(BaseModel):
    chain_id: str = Field(..., description="Chain identifier of the macromolecule")
    name: str = Field(..., description="Name of the macromolecule")
    id: Optional[str] = Field(None, description=UNIPROT_ID_DESC)
    ac: Optional[str] = Field(None, description=UNIPROT_AC_DESC)


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
    HYBRID = "HYBRID"


class Provider(Enum):
    PDBE = "PDBE"
    SWISSMODEL = "SWISSMODEL"
    GENOME3D = "GENOME3D"
    FOLDX = "FOLDX"
    PED = "PED"
    ALPHAFOLD_DB = "AlphaFold DB"


class ModelCategory(Enum):
    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    TEMPLATE_BASED = "TEMPLATE-BASED"
    TEMPLATE_FREE = "TEMPLATE-FREE"
    CONFORMATIONAL_ENSEMBLE = "CONFORMATIONAL ENSEMBLE"
    DEEP_LEARNING = "Deep learning"


class Template(BaseModel):
    template_id: str = Field(
        ..., description="Identifier of the templates, e.g. PDB id"
    )
    chain_id: str = Field(..., description="Identifier of the chain of the template")
    template_sequence_identity: float = Field(
        ..., description="Sequence identity of the template with the UniProt accession"
    )
    last_updated: str = Field(
        ...,
        regex="^[1-2][9|0][0-9]{2}-[0-1][0-9]-[0-3][0-9]$",
        description="Date of release of the last update in the format of YYYY-MM-DD",
    )
    provider: str = Field(..., description="Provider of the template, e.g. PDBe")
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


class StructureSummary(BaseModel):
    model_identifier: str = Field(
        ..., description="Identifier of the model, e.g. a PDB id"
    )
    model_category: ModelCategory = Field(
        ..., description="Category of the model, e.g. EXPERIMENTALLY DETERMINED"
    )
    provider: Provider = Field(..., description="Name of the model provider")
    created: str = Field(
        ...,
        regex="^[1-2][9|0][0-9]{2}-[0-1][0-9]-[0-3][0-9]$",
        description="Date of release of model generation in the format of YYYY-MM-DD",
    )
    sequence_identity: Optional[float] = Field(
        None, description="Sequence identity of the model to the UniProt sequence"
    )
    uniprot_start: Optional[int] = Field(
        None,
        description="The index of the first residue of the model according to UniProt "
        "sequence numbering, e.g. 1",
    )
    uniprot_end: Optional[int] = Field(
        None,
        description="The index of the last residue of the model according to UniProt "
        "sequence numbering, e.g. 142",
    )
    resolution: Optional[float] = Field(
        None,
        description="The resolution of the model in Angstrom, if applicable, e.g. 2.1",
    )
    coverage: Optional[float] = Field(
        None, description="Percentage of the UniProt sequence covered by the model"
    )
    qmean_version: Optional[str] = Field(
        None, description="Version of QMEAN used to calculate quality"
    )
    qmean_avg_local_score: Optional[float] = Field(
        None, description="Average of the local QMEAN scores"
    )
    model_url: str = Field(..., description="URL of the model coordinates")
    model_format: ModelFormat = Field(
        None, description="File format of the coordinates, e.g. PDB"
    )


class Structure(BaseModel):
    model_identifier: str = Field(
        ..., description="Identifier of the model, e.g. a PDB id"
    )
    model_category: ModelCategory = Field(
        ..., description="Category of the model, e.g. EXPERIMENTALLY DETERMINED"
    )
    provider: Provider = Field(..., description="Name of the model provider")
    created: str = Field(
        ...,
        regex="^[1-2][9|0][0-9]{2}-[0-1][0-9]-[0-3][0-9]$",
        description="Date of release of model generation in the format of YYYY-MM-DD",
    )
    sequence_identity: Optional[float] = Field(
        None, description="Sequence identity of the model to the UniProt sequence"
    )
    uniprot_start: Optional[int] = Field(
        None,
        description="The index of the first residue of the model according to UniProt "
        "sequence numbering, e.g. 1",
    )
    uniprot_end: Optional[int] = Field(
        None,
        description="The index of the last residue of the model according to UniProt "
        "sequence numbering, e.g. 142",
    )
    oligo_state: str = Field(
        ..., description="Oligomeric state of the model, e.g. monomer"
    )
    preferred_assembly_id: Optional[str] = Field(
        None, description="Identifier of the preferred assembly in the model"
    )
    resolution: Optional[float] = Field(
        None,
        description="The resolution of the model in Angstrom, if applicable, e.g. 2.1",
    )
    coverage: Optional[float] = Field(
        None, description="Percentage of the UniProt sequence covered by the model"
    )
    qmean_version: Optional[str] = Field(
        None, description="Version of QMEAN used to calculate quality"
    )
    qmean_avg_local_score: Optional[float] = Field(
        None, description="Average of the local QMEAN scores"
    )
    model_url: str = Field(..., description="URL of the model coordinates")
    in_complex_with: Optional[List[InComplexWithItem]] = Field(
        None,
        description="Information on any macromolecules in complex with the "
        "protein of interest",
    )
    chains: List[Chain]
    model_format: ModelFormat = Field(
        None, description="File format of the coordinates, e.g. PDB"
    )


class Result(BaseModel):
    uniprot_entry: UniProtEntry = Field(
        ..., description="Information on the UniProt accession the data corresponds to"
    )
    structures: List[Structure] = Field(
        ...,
        description="Information on the structures available for the UniProt accession",
    )


class ResultSummary(BaseModel):
    uniprot_entry: UniProtEntry = Field(
        ..., description="Information on the UniProt accession the data corresponds to"
    )
    structures: List[StructureSummary] = Field(
        ...,
        description="Information on the structures available for the UniProt accession",
    )
