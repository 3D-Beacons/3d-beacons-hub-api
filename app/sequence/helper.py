import hashlib
from typing import Dict, List

import msgpack
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_200_OK

from app.cache.redis_cache import RedisCache
from app.config import MAX_POST_LIMIT
from app.exception import (
    JobNotFoundException,
    JobResultsNotFoundException,
    JobStatusNotFoundException,
    RequestSubmissionException,
)
from app.uniprot.schema import AccessionListRequest, UniprotSummary
from app.uniprot.uniprot import get_list_of_uniprot_summary_helper
from app.utils import request_get, request_post


def generate_hash(sequence: str):
    """Generate an MD5 hash from a sequence.

    Args:
        sequence (str): A protein sequence string
    """
    return hashlib.md5(sequence.encode()).hexdigest()


async def get_job_status(job_id: str):
    """Check the status of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/status/{job_id}"

    response = await request_get(url)

    if response and response.status_code == HTTP_200_OK:
        return response.content.decode()
    raise JobStatusNotFoundException("Job status not found!")


async def get_job_accs_results(job_id: str):
    """Get the results of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/result/{job_id}/accs"
    response = await request_get(url)
    if response and response.status_code == HTTP_200_OK:
        return response.content.decode()
    raise JobResultsNotFoundException("Job results not found!")


async def get_job_json_results(job_id: str):
    """Get the results of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/result/{job_id}/json"
    response = await request_get(url)

    if response and response.status_code == HTTP_200_OK:
        return response.json()
    raise JobResultsNotFoundException("Job results not found!")


async def submit_sequence_search_job(sequence: str) -> str:
    """Submit a sequence to the search engine.

    Args:
        sequence (str): A protein sequence string
    Returns:
        str: A job id
    """
    url = "https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/run"
    data = {
        "email": "pdbekb_help@ebi.ac.uk",
        "program": "blastp",
        "stype": "protein",
        "sequence": sequence,
        "database": "uniprotkb",
    }
    response = await request_post(url, data)
    if response and response.status_code == HTTP_200_OK:
        return response.content.decode()
    raise RequestSubmissionException("Request submission failed!")


async def get_job_id(seq_hash: str) -> str:
    """Get the job id from the cache.

    Args:
        seq_hash (str): A sequence hash

    Returns:
        str: A job id
    """
    job_id_resp = await RedisCache.hget("sequence", seq_hash)
    if job_id_resp:
        job_id = msgpack.loads(job_id_resp)
        if job_id.startswith("ncbiblast-"):
            return job_id
    raise JobNotFoundException("Job not found in cache!")


def filter_json_results(results: Dict, hsp_identity: int = 90) -> List:
    """Filter the results from the search engine. Only returns MAX_POST_LIMIT results.

    Args:
        results (Dict): Results from the search engine
        hsp_identity (int, optional): Minimum identity percentage. Defaults to 90.

    Returns:
        List: A list of filtered results
    """
    return [
        x for x in results["hits"] if x["hit_hsps"][0]["hsp_identity"] >= hsp_identity
    ]


def prepare_accession_list(accession_list: List) -> AccessionListRequest:
    """Creates an AccessionListRequest object.

    Args:
        accession_list (List): A list of accessions

    Returns:
        AccessionListRequest: An AccessionListRequest object
    """
    return AccessionListRequest(accessions=accession_list)


def prepare_hit_dictionary(hit_list: List) -> Dict:
    """Creates a dictionary of hits.

    Args:
        hit_list (List): List of hits

    Returns:
        Dict: A dictionary of hits
    """
    hit_dictionary = {}

    for hit in hit_list:
        hit_dictionary.update(
            {
                hit["hit_acc"]: {
                    "accession": hit["hit_acc"],
                    "description": hit["hit_desc"],
                    "hit_length": hit["hit_len"],
                    "id": hit["hit_id"],
                    "hit_hsps": [
                        {
                            "hsp_score": x["hsp_score"],
                            "hsp_bit_score": x["hsp_bit_score"],
                            "hsp_align_len": x["hsp_align_len"],
                            "hsp_identity": x["hsp_identity"],
                            "hsp_positive": x["hsp_positive"],
                            "hsp_qseq": x["hsp_qseq"],
                            "hsp_mseq": x["hsp_mseq"],
                            "hsp_hseq": x["hsp_hseq"],
                        }
                        for x in hit["hit_hsps"]
                    ],
                }
            }
        )

    return hit_dictionary


async def set_job_results_in_cache(job_id: str, results: Dict):  # pragma: no cover
    """Set the results of a job in the cache.

    Args:
        job_id (str): A job id
        results (Dict): Results from the search engine
    """
    await RedisCache.hset(
        "job_results", job_id, msgpack.dumps(jsonable_encoder(results))
    )


async def get_job_results_from_cache(job_id: str):  # pragma: no cover
    """Get the results of a job from the cache.

    Args:
        job_id (str): A job id

    Returns:
        Dict: Results from the search engine
    """
    response = await RedisCache.hget("job_results", job_id)
    if response:
        return msgpack.loads(response)
    raise JobResultsNotFoundException("Job results not found in cache!")


def prepare_paginated_accessions(hit_dictionary: Dict, page_num: int) -> List[str]:
    """Prepare a list of accessions for a page.

    Args:
        hit_dictionary (Dict): A dictionary of hits
        page_num (int): A page number

    Returns:
        List[str]: A list of accessions
    """
    accessions = list(hit_dictionary.keys())

    if len(accessions) <= MAX_POST_LIMIT:
        return accessions

    return accessions[
        page_num * MAX_POST_LIMIT : (page_num * MAX_POST_LIMIT) + MAX_POST_LIMIT
    ]


async def prepare_dictionary_of_summary_results(accessions: List[str]) -> Dict:
    """Prepare a dictionary of summary results.

    Args:
        accessions (List[str]): A list of accessions

    Returns:
        Dict: A dictionary of summary results
    """
    result_dict: Dict[str, UniprotSummary] = {k: None for k in accessions}
    accession_obj_list = prepare_accession_list(accessions)
    summary_results: List[UniprotSummary] = await get_list_of_uniprot_summary_helper(
        accession_obj_list
    )

    if not summary_results:
        return {}

    for x in summary_results:
        result_dict[x.uniprot_entry.ac] = x

    return result_dict
