import hashlib

from starlette.status import HTTP_200_OK

from app.exception import RequestSubmissionException
from app.utils import request_post


def generate_hash(sequence: str):
    """Generate an MD5 hash from a sequence.

    Args:
        sequence (str): A protein sequence string
    """
    return hashlib.md5(sequence.encode()).hexdigest()


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
    try:
        response = await request_post(url, data)
        if response and response.status_code == HTTP_200_OK:
            return response.content.decode()
    except Exception:
        pass
    raise RequestSubmissionException("Request submission failed!")
