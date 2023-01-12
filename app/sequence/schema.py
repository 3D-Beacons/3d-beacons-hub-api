from typing import List

from pydantic import BaseModel

from app.uniprot.schema import UniprotSummary


class Sequence(BaseModel):
    sequence: str


class ErrorMessage(BaseModel):
    message: str = "Error in submitting the job, please retry!"


class SearchSuccessMessage(BaseModel):
    job_id: str


class SearchInProgressMessage(BaseModel):
    message: str = "Search in progress, please try after sometime!"


class NoJobFoundMessage(BaseModel):
    message: str = "No job found for the given sequence, please submit the job again!"


class HSPS(BaseModel):
    hsp_score: float
    hsp_bit_score: float
    hsp_align_len: int
    hsp_identity: float
    hsp_positive: float
    hsp_qseq: str
    hsp_hseq: str
    hsp_mseq: str


class SearchAccession(BaseModel):
    accession: str
    id: str
    description: str
    hit_length: int
    hit_hsps: List[HSPS]
    summary: UniprotSummary = None


class SearchResults(BaseModel):
    hits: List[SearchAccession]
    total_hits: int
    current_page: int
    total_pages: int
    max_results_per_page: int
