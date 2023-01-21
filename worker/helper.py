import os
from typing import Dict, List

import requests

from worker.schema import AccessionListRequest

MAX_POST_LIMIT = int(os.environ.get("MAX_POST_LIMIT", 10))
BEACONS_API_URL = os.environ.get("BEACONS_API_URL")


class JobStatusNotFoundException(Exception):
    pass


class JobResultsNotFoundException(Exception):
    pass


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


def divide_chunks(list: List[str], batch_size: int):
    for i in range(0, len(list), batch_size):
        yield list[i : i + batch_size]


def prepare_accession_list(accession_list: List) -> AccessionListRequest:
    """Creates an AccessionListRequest object.

    Args:
        accession_list (List): A list of accessions

    Returns:
        AccessionListRequest: An AccessionListRequest object
    """
    return AccessionListRequest(accessions=accession_list)


def prepare_hit_dictionary_with_summary_results(hit_dictionary: Dict):
    final_hit_dictionary = {}
    with requests.Session() as session:
        for accessions_batch in divide_chunks(
            list(hit_dictionary.keys()), MAX_POST_LIMIT
        ):
            summary_response = session.post(
                f"{BEACONS_API_URL}/uniprot/summary",
                json={"accessions": accessions_batch},
            )

            if (
                summary_response
                and summary_response.status_code == 200
                and summary_response.json()
            ):
                for result in summary_response.json():
                    accession = result["uniprot_entry"]["ac"]
                    accession_record = hit_dictionary[accession]
                    accession_record.update({"summary": result})
                    final_hit_dictionary.update({accession: accession_record})
            else:
                return None

    return final_hit_dictionary


def get_job_dispatcher_job_status(job_id: str):
    """Check the status of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/status/{job_id}"

    response = requests.get(url)

    if response and response.status_code == 200:
        return response.content.decode()
    raise JobStatusNotFoundException("Job status not found!")


def get_job_dispatcher_json_results(job_id: str):
    """Get the results of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/result/{job_id}/json"
    response = requests.get(url)

    if response and response.status_code == 200:
        return response.json()
    raise JobResultsNotFoundException("Job results not found!")
