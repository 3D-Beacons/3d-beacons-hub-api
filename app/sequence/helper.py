import hashlib

from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app.cache.redis_cache import RedisCache
from app.constants import NO_JOB_FOUND_MESSAGE
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


async def handle_no_job_error(job_id: str):
    await RedisCache.hdel("sequence", job_id)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"message": NO_JOB_FOUND_MESSAGE},
    )
