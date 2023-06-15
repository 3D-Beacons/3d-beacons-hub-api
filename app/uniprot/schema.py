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
    segment_start: Optional[int] = Field(
        None,
        description="1-indexed first residue of the UniProt sequence segment",
    )
    segment_end: Optional[int] = Field(
        None,
        description="1-indexed last residue of the UniProt sequence segment",
    )


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
    X_RAY_POWDER_DIFFRACTION = "X-RAY POWDER DIFFRACTION"
    SOLID_STATE_NMR = "SOLID-STATE NMR"
    SOLUTION_NMR = "SOLUTION NMR"
    X_RAY_SOLUTION_SCATTERING = "X-RAY SOLUTION SCATTERING"
    THEORETICAL_MODEL = "THEORETICAL MODEL"
    X_RAY_DIFFRACTION = "X-RAY DIFFRACTION"
    HYBRID = "HYBRID"


class Provider(Enum):
    PDBE = "PDBe"
    SWISS_MODEL = "SWISS-MODEL"
    GENOME3D = "Genome3D"
    FOLDX = "FoldX"
    PED = "PED"
    ALPHAFOLD_DB = "AlphaFold DB"
    SASBDB = "SASBDB"
    ALPHAFILL = "AlphaFill"
    MODELARCHIVE = "ModelArchive"
    HEGELAB = "HEGELAB"


class OligoState(Enum):
    MONOMER = "MONOMER"
    HOMODIMER = "HOMODIMER"
    HETERODIMER = "HETERODIMER"
    HOMO_OLIGOMER = "HOMO-OLIGOMER"
    HETERO_OLIGOMER = "HETERO-OLIGOMER"
    SASBDB = "SASBDB"


class ModelCategory(Enum):
    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    TEMPLATE_BASED = "TEMPLATE-BASED"
    AB_INITIO = "AB-INITIO"
    CONFORMATIONAL_ENSEMBLE = "CONFORMATIONAL ENSEMBLE"
    DEEP_LEARNING = "DEEP-LEARNING"


class ModelType(Enum):
    ATOMIC = "ATOMIC"
    DUMMY = "DUMMY"
    MIX = "MIX"


class ConfidenceType(Enum):
    pLDDT = "pLDDT"
    QMEANDisCo = "QMEANDisCo"
    ipTMPlusPTM = "ipTM+pTM"


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
    confidence: Optional[float] = Field(
        None, description="Confidence score in the range of [0,1]"
    )
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


class EntityType(Enum):
    NON_POLYMER = "NON-POLYMER"
    MACROLIDE = "MACROLIDE"
    POLYMER = "POLYMER"
    BRANCHED = "BRANCHED"
    WATER = "WATER"


class IdentifierCategory(Enum):
    UNIPROT = "UNIPROT"
    RFAM = "RFAM"
    CCD = "CCD"
    SMILES = "SMILES"
    INCHI = "INCHI"
    INCHIKEY = "INCHIKEY"


class EntityPolyType(Enum):
    CYCLIC_PSEUDO_PEPTIDE = "CYCLIC-PSEUDO-PEPTIDE"
    PEPTIDE_NUCLEIC_ACID = "PEPTIDE NUCLEIC ACID"
    POLYDEOXYRIBONUCLEOTIDE = "POLYDEOXYRIBONUCLEOTIDE"
    DNA_RNA_HYBRID = "POLYDEOXYRIBONUCLEOTIDE/POLYRIBONUCLEOTIDE HYBRID"
    POLYPEPTIDE_D = "POLYPEPTIDE(D)"
    POLYPEPTIDE_L = "POLYPEPTIDE(L)"
    POLYRIBONUCLEOTIDE = "POLYRIBONUCLEOTIDE"
    OTHER = "OTHER"


class Entity(BaseModel):
    entity_type: EntityType = Field(..., description="The type of the molecular entity")
    entity_poly_type: Optional[EntityPolyType] = Field(
        None,
        description="The type of the molecular entity; similar to _entity_poly.type"
        " in mmCIF",
    )
    identifier: Optional[str] = Field(None, description="Identifier of the molecule")
    identifier_category: Optional[IdentifierCategory] = Field(
        None, description="Category of the identifier"
    )
    description: str = Field(..., description="A textual label of the molecule")
    chain_ids: List[str] = Field(
        ..., description="A list of chain identifiers of the molecule"
    )


class Structure(BaseModel):
    model_identifier: str = Field(
        ..., description="Identifier of the model, e.g. a PDB id"
    )
    model_category: ModelCategory = Field(
        ..., description="Category of the model, e.g. EXPERIMENTALLY DETERMINED"
    )
    model_url: str = Field(..., description="URL of the model coordinates")
    model_format: ModelFormat = Field(
        ..., description="File format of the coordinates, e.g. PDB"
    )
    model_type: Optional[ModelType] = Field(
        None,
        description="Defines if the coordinates are atomic-level or contains dummy "
        "atoms (e.g. SAXS models), or a mix of both (e.g. hybrid models)",
    )
    model_page_url: Optional[str] = Field(
        None,
        description="URL of a web page of the data provider that show the model, "
        "eg. https://alphafold.ebi.ac.uk/entry/Q5VSL9",
    )
    provider: Provider = Field(..., description="Name of the model provider, eg. PED")
    number_of_conformers: Optional[int] = Field(
        None, description="The number of conformers in a conformational ensemble"
    )
    ensemble_sample_url: Optional[str] = Field(
        None,
        description="URL of a sample of conformations from a conformational ensemble, "
        "eg. https://proteinensemble.org/api/ensemble_sample/PED00001e001",
    )
    ensemble_sample_format: Optional[ModelFormat] = Field(
        None, description="File format of the sample coordinates, e.g. PDB"
    )
    created: str = Field(
        ...,
        regex="^[1-2][9|0][0-9]{2}-[0-1][0-9]-[0-3][0-9]$",
        description="Date of release of model generation in the format of YYYY-MM-DD",
    )
    sequence_identity: float = Field(
        ..., description="Sequence identity of the model to the UniProt sequence"
    )
    uniprot_start: int = Field(
        ...,
        description="The index of the first residue of the model according to UniProt "
        "sequence numbering, e.g. 1",
    )
    uniprot_end: int = Field(
        ...,
        description="The index of the last residue of the model according to UniProt "
        "sequence numbering, e.g. 142",
    )
    coverage: float = Field(
        ..., description="Percentage of the UniProt sequence covered by the model"
    )
    experimental_method: Optional[ExperimentalMethod] = Field(
        None,
        description="Experimental method used to determine the structure, if "
        "applicable",
    )
    resolution: Optional[float] = Field(
        None,
        description="The resolution of the model in Angstrom, if applicable, e.g. 2.1",
    )
    confidence_type: Optional[ConfidenceType] = Field(
        None,
        description="Type of the confidence measure. This is required for  theoretical"
        " models.",
    )
    confidence_version: Optional[str] = Field(
        None,
        description="Version of confidence measure software used to calculate quality."
        "This is required for theoretical models.",
    )
    confidence_avg_local_score: Optional[float] = Field(
        None,
        description="Average of the confidence measures in the range of [0,1]. Please "
        "contact 3D-Beacons developers if other estimates are to be added. "
        "This is required for theoretical models.",
    )
    oligomeric_state: Optional[OligoState] = Field(
        None, description="Oligomeric state of the model, e.g. MONOMER"
    )
    preferred_assembly_id: Optional[str] = Field(
        None, description="Identifier of the preferred assembly in the model"
    )
    entities: Optional[List[Entity]]
    chains: Optional[List[Chain]]


class Result(BaseModel):
    uniprot_entry: UniProtEntry = Field(
        ..., description="Information on the UniProt accession the data corresponds to"
    )
    structures: List[Structure] = Field(
        ...,
        description="Information on the structures available for the UniProt accession",
    )
    residues: Optional[List[int]] = Field(
        None, description="An array of residue indices"
    )
    regions: Optional[List[Region]] = None


class Annotations(BaseModel):
    accession: str = Field(..., description="A UniProt accession", example="P00734")
    id: Optional[str] = Field(
        None, description="A UniProt identifier", example="FGFR2_HUMAN"
    )
    sequence: str = Field(
        ..., description="The sequence of the protein", example="AFFGVAATRKL"
    )
    ligand: Optional[List[LigandItem]] = Field(
        None, description="Contains ligand annotations"
    )
    secondary_structure: Optional[List[SecondaryStructureItem]] = None
    feature: Optional[List[FeatureItem]] = None


class MappingAccessionType(Enum):
    uniprot = "uniprot"
    pfam = "pfam"


class ModelCategory1(Enum):
    EXPERIMENTALLY_DETERMINED = "EXPERIMENTALLY DETERMINED"
    TEMPLATE_BASED = "TEMPLATE-BASED"
    AB_INITIO = "AB-INITIO"
    CONFORMATIONAL_ENSEMBLE = "CONFORMATIONAL ENSEMBLE"
    DEEP_LEARNING = "DEEP-LEARNING"


class ModelType1(Enum):
    single = "single"
    complex = "complex"


class Metadata(BaseModel):
    mappingAccession: str = Field(
        ...,
        description="Accession/identifier of the entity the model is mapped to",
        example="P38398",
    )
    mappingAccessionType: MappingAccessionType = Field(
        ...,
        description="The name of the data provider the model is mapped to",
        example="uniprot",
    )
    start: int = Field(
        ...,
        description="The index of the first residue of the model according to the "
        "mapping",
        example=1,
    )
    end: int = Field(
        ...,
        description="The index of the last residue of the model according to the "
        "mapping",
        example=103,
    )
    modelCategory: ModelCategory1 = Field(
        ..., description="Category of the model", example="TEMPLATE-BASED"
    )
    modelType: ModelType1 = Field(
        ..., description="Monomeric or complex strutures", example="single"
    )


class Detailed(BaseModel):
    summary: SummaryItems
    chains: Chains


class Overview(BaseModel):
    summary: SummaryItems


class UniprotSummary(BaseModel):
    uniprot_entry: Optional[UniprotEntry] = None
    structures: Optional[List[Overview]] = None


class UniprotDetails(BaseModel):
    uniprot_entry: Optional[UniprotEntry] = None
    structures: Optional[List[Detailed]] = None


class PdbSummary(BaseModel):
    uniprot_entry: Optional[PdbEntry] = None
    structures: Optional[List[Overview]] = None


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
