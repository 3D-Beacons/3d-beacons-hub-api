from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.constants import (
    JOB_FAILED_ERROR_MESSAGE,
    JOB_SUBMISSION_ERROR_MESSAGE,
    NO_JOB_FOUND_MESSAGE,
    SEARCH_IN_PROGRESS_MESSAGE,
)
from app.uniprot.schema import UniprotSummary


class Sequence(BaseModel):
    sequence: str


class JobSubmissionErrorMessage(BaseModel):
    message: str = JOB_SUBMISSION_ERROR_MESSAGE


class SearchSuccessMessage(BaseModel):
    job_id: str


class SearchInProgressMessage(BaseModel):
    message: str = SEARCH_IN_PROGRESS_MESSAGE


class NoJobFoundMessage(BaseModel):
    message: str = NO_JOB_FOUND_MESSAGE


class JobFailedErrorMessage(BaseModel):
    message: str = JOB_FAILED_ERROR_MESSAGE


class HSPS(BaseModel):
    hsp_score: float
    hsp_bit_score: float
    hsp_align_len: int
    hsp_identity: float
    hsp_positive: float
    hsp_qseq: str
    hsp_hseq: str
    hsp_mseq: str
    hsp_expect: float


class SearchAccession(BaseModel):
    accession: str
    id: str
    description: str
    hit_length: int
    hit_hsps: List[HSPS]
    summary: UniprotSummary = None
    hit_uni_ox: int
    hit_uni_os: str
    hit_com_os: str
    title: str


class SearchResults(BaseModel):
    hits: List[SearchAccession]
    total_hits: int
    current_page: int
    total_pages: int
    max_results_per_page: int


class ChecksumType(str, Enum):
    """Type of checksum enumeration"""

    CRC64 = "CRC64"
    MD5 = "MD5"


class ModelCategory(str, Enum):
    """Model category enumeration"""

    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    TEMPLATE_BASED = "TEMPLATE-BASED"
    AB_INITIO = "AB-INITIO"
    CONFORMATIONAL_ENSEMBLE = "CONFORMATIONAL ENSEMBLE"


class ModelFormat(str, Enum):
    """Model format enumeration"""

    PDB = "PDB"
    MMCIF = "MMCIF"
    BCIF = "BCIF"


class ModelType(str, Enum):
    """Model type enumeration"""

    ATOMIC = "ATOMIC"
    DUMMY = "DUMMY"
    MIX = "MIX"


class ExperimentalMethod(str, Enum):
    """Experimental method enumeration"""

    ELECTRON_CRYSTALLOGRAPHY = "ELECTRON CRYSTALLOGRAPHY"
    ELECTRON_MICROSCOPY = "ELECTRON MICROSCOPY"
    EPR = "EPR"
    FIBER_DIFFRACTION = "FIBER DIFFRACTION"
    FLUORESCENCE_TRANSFER = "FLUORESCENCE TRANSFER"
    INFRARED_SPECTROSCOPY = "INFRARED SPECTROSCOPY"
    NEUTRON_DIFFRACTION = "NEUTRON DIFFRACTION"
    X_RAY_POWDER_DIFFRACTION = "X-RAY POWDER DIFFRACTION"
    SOLID_STATE_NMR = "SOLID-STATE NMR"
    SOLUTION_NMR = "SOLUTION NMR"
    X_RAY_SOLUTION_SCATTERING = "X-RAY SOLUTION SCATTERING"
    THEORETICAL_MODEL = "THEORETICAL MODEL"
    X_RAY_DIFFRACTION = "X-RAY DIFFRACTION"
    HYBRID = "HYBRID"


class ConfidenceType(str, Enum):
    """Confidence type enumeration"""

    PLDDT = "pLDDT"
    QMEANDISCO = "QMEANDisCo"
    IPTM_PTM = "ipTM+pTM"


class OligomericState(str, Enum):
    """Oligomeric state enumeration"""

    MONOMER = "MONOMER"
    HOMODIMER = "HOMODIMER"
    HETERODIMER = "HETERODIMER"
    HOMO_OLIGOMER = "HOMO-OLIGOMER"
    HETERO_OLIGOMER = "HETERO-OLIGOMER"


class EntityType(str, Enum):
    """Entity type enumeration"""

    BRANCHED = "BRANCHED"
    MACROLIDE = "MACROLIDE"
    NON_POLYMER = "NON-POLYMER"
    POLYMER = "POLYMER"
    WATER = "WATER"


class EntityPolyType(str, Enum):
    """Entity poly type enumeration"""

    CYCLIC_PSEUDO_PEPTIDE = "CYCLIC-PSEUDO-PEPTIDE"
    PEPTIDE_NUCLEIC_ACID = "PEPTIDE NUCLEIC ACID"
    POLYDEOXYRIBONUCLEOTIDE = "POLYDEOXYRIBONUCLEOTIDE"
    POLYDEOXYRIBONUCLEOTIDE_POLYRIBONUCLEOTIDE_HYBRID = (
        "POLYDEOXYRIBONUCLEOTIDE/POLYRIBONUCLEOTIDE HYBRID"
    )
    POLYPEPTIDE_D = "POLYPEPTIDE(D)"
    POLYPEPTIDE_L = "POLYPEPTIDE(L)"
    POLYRIBONUCLEOTIDE = "POLYRIBONUCLEOTIDE"
    OTHER = "OTHER"


class IdentifierCategory(str, Enum):
    """Identifier category enumeration"""

    UNIPROT = "UNIPROT"
    RFAM = "RFAM"
    CCD = "CCD"
    SMILES = "SMILES"
    INCHI = "INCHI"
    INCHIKEY = "INCHIKEY"


class SequenceIdType(str, Enum):
    SEQUENCE = "sequence"
    CRC64 = "crc64"
    MD5 = "md5"


class Entity(BaseModel):
    """Molecular entity in the model"""

    entity_type: EntityType = Field(..., description="Type of the molecular entity")
    entity_poly_type: Optional[EntityPolyType] = Field(
        None, description="Type of the molecular entity polymer"
    )
    identifier: Optional[str] = Field(None, description="Identifier of the molecule")
    identifier_category: Optional[IdentifierCategory] = Field(
        None, description="Category of the identifier"
    )
    description: str = Field(..., description="Textual label of the molecule")
    chain_ids: List[str] = Field(
        ..., description="List of chain identifiers of the molecule"
    )


class SummaryItems(BaseModel):
    """Summary items for a structure"""

    model_identifier: str = Field(
        ..., description="Identifier of the model, such as PDB id"
    )
    model_category: ModelCategory = Field(..., description="Category of the model")
    model_url: str = Field(..., description="URL of the model coordinates")
    model_format: ModelFormat = Field(..., description="File format of the coordinates")
    model_type: Optional[ModelType] = Field(
        None,
        description="Defines if coordinates are atomic-level or contain dummy atoms",
    )
    model_page_url: Optional[str] = Field(
        None, description="URL of a web page showing the model"
    )
    provider: str = Field(..., description="Name of the model provider")
    number_of_conformers: Optional[float] = Field(
        None, description="Number of conformers in a conformational ensemble"
    )
    ensemble_sample_url: Optional[str] = Field(
        None, description="URL of a sample of conformations from ensemble"
    )
    ensemble_sample_format: Optional[ModelFormat] = Field(
        None, description="File format of the sample coordinates"
    )
    created: str = Field(
        ...,
        description="Date of release of model generation in the format of YYYY-MM-DD",
        json_schema_extra={"example": "2021-12-21"},
    )
    sequence_identity: float = Field(
        ..., ge=0, le=1, description="Sequence identity of model to UniProt sequence"
    )
    coverage: float = Field(
        ..., ge=0, le=1, description="Fraction of UniProt sequence covered by the model"
    )
    experimental_method: Optional[ExperimentalMethod] = Field(
        None, description="Experimental method used to determine structure"
    )
    resolution: Optional[float] = Field(
        None, gt=0, description="Resolution of the model in Angstrom"
    )
    confidence_type: Optional[ConfidenceType] = Field(
        None, description="Type of confidence measure"
    )
    confidence_version: Optional[str] = Field(
        None, description="Version of confidence measure software"
    )
    confidence_avg_local_score: Optional[float] = Field(
        None, description="Average of confidence measures"
    )
    oligomeric_state: Optional[OligomericState] = Field(
        None, description="Oligomeric state of the model"
    )
    oligomeric_state_confidence: Optional[float] = Field(
        None, description="Confidence in oligomeric state"
    )
    preferred_assembly_id: Optional[str] = Field(
        None, description="Identifier of preferred assembly"
    )
    entities: List[Entity] = Field(
        ..., description="List of molecular entities in the model"
    )


class SequenceOverview(BaseModel):
    """Sequence overview containing summary items"""

    summary: SummaryItems = Field(
        ..., description="Summary information for the structure"
    )


class Entry(BaseModel):
    """Entry information for sequence summary"""

    sequence: str = Field(..., description="The protein sequence")
    checksum: str = Field(..., description="CRC64 or MD5 checksum of the sequence")
    checksum_type: ChecksumType = Field(..., description="Type of the checksum")


class SequenceSummary(BaseModel):
    """Main response model for /sequence/summary endpoint"""

    entry: Entry = Field(
        ..., description="Entry information including sequence and checksum"
    )
    structures: List[SequenceOverview] = Field(
        ..., description="List of available structures"
    )


# Request models for the endpoint
class SequenceSummaryRequest(BaseModel):
    """Request parameters for /sequence/summary endpoint"""


# Response models
class SequenceSummaryResponse(BaseModel):
    """Response wrapper for successful requests"""

    data: SequenceSummary
