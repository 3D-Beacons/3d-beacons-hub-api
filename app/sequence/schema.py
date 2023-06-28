from typing import List

from pydantic import BaseModel

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
