import hashlib

import httpx

from app import logger
from app.cache.redis_cache import RedisCache
from app.utils import REQUEST_TIMEOUT, request_get


def generate_hash(sequence: str):
    """Generate an MD5 hash from a sequence.

    Args:
        sequence (str): A protein sequence string
    """
    return hashlib.md5(sequence.encode()).hexdigest()


async def exists_in_cache(sequence: str):
    """Check if a sequence exists in the cache.

    Args:
        sequence (str): A protein sequence string
    """
    hashed_sequence = generate_hash(sequence)
    response = await RedisCache.hget("sequence", hashed_sequence)

    if not response:
        return None

    return response


async def post(url: str, data):
    async with httpx.AsyncClient() as client:
        try:
            return await client.post(url, timeout=REQUEST_TIMEOUT, data=data)
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            logger.info(f"Timeout for {url}")
            return None


async def job_status(job_id: str):
    """Check the status of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/status/{job_id}"

    return await request_get(url)


async def job_results(job_id: str):
    """Get the results of a job.

    Args:
        job_id (str): A job id
    """
    url = f"https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/result/{job_id}/accs"
    return await request_get(url)


async def submit_job(sequence: str):
    """Submit a sequence to the search engine.

    Args:
        sequence (str): A protein sequence string
    """
    url = "https://www.ebi.ac.uk/Tools/services/rest/ncbiblast/run"
    data = {
        "email": "sreenath@ebi.ac.uk",
        "program": "blastp",
        "stype": "protein",
        "sequence": sequence,
        "database": "uniprotkb",
    }
    return await post(url, data)
