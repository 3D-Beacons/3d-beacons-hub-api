from typing import List

import msgpack
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND

from app import logger
from app.cache.redis_cache import RedisCache
from app.sequence.schema import Sequence
from app.sequence.search import generate_hash, job_results, job_status, submit_job
from app.uniprot.schema import UniprotSummary

sequence_route = APIRouter()


@sequence_route.post(
    "/search",
    status_code=HTTP_200_OK,
    response_model=List[UniprotSummary],
)
async def search(sequence: Sequence):
    hashed_sequence = generate_hash(sequence.sequence)

    await RedisCache.hset(
        "sequence",
        hashed_sequence,
        msgpack.dumps(jsonable_encoder("ncbiblast-R20221101-143030-0221-97138404-p1m")),
    )

    response = await RedisCache.hget("sequence", hashed_sequence)

    if response:
        response = msgpack.loads(response)
        # check if the response is a job id
        if response.startswith("ncbiblast-"):
            # check the status of the job
            status_response = await job_status(response)

            if status_response and status_response.status_code == HTTP_200_OK:
                # sends wait response if job is still running
                if status_response.content.decode() == "RUNNING":
                    return JSONResponse(
                        status_code=HTTP_202_ACCEPTED,
                        content={"message": "Search in progress"},
                    )
                # make the accs response call to get the actual results
                elif status_response.content.decode() == "FINISHED":
                    results = await job_results(response)
                    results = results.content.decode()
                    print(results)
                    packed_response = msgpack.dumps(jsonable_encoder(results))
                    await RedisCache.hset("sequence", hashed_sequence, packed_response)
                    return JSONResponse(content=results, status_code=HTTP_200_OK)

        else:
            # send the job results
            return JSONResponse(content=response, status_code=HTTP_200_OK)

    else:
        # not found in cache, submit the job
        job_response = await submit_job(sequence.sequence)

        if job_response.status_code == HTTP_200_OK:
            job_id = job_response.content.decode()
            logger.debug(f"Sequence {sequence.sequence} submitted to search engine")
            packed_response = msgpack.dumps(jsonable_encoder(job_id))
            await RedisCache.hset("sequence", hashed_sequence, packed_response)
            return JSONResponse(
                status_code=HTTP_202_ACCEPTED,
                content={"message": f"Job {hashed_sequence} submitted"},
            )

        print(job_response.__dict__, " job_response")
        return JSONResponse(content={}, status_code=HTTP_404_NOT_FOUND)
