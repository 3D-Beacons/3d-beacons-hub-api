from typing import List

import msgpack
from celery.result import AsyncResult
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app import logger
from app.cache.redis_cache import RedisCache
from app.constants import (
    JOB_FAILED_ERROR_MESSAGE,
    JOB_SUBMISSION_ERROR_MESSAGE,
    SEARCH_IN_PROGRESS_MESSAGE,
)
from app.exception import (
    JobNotFoundException,
    JobResultsNotFoundException,
    RequestSubmissionException,
)
from app.sequence.helper import (
    generate_hash,
    handle_no_job_error,
    submit_sequence_search_job,
)
from app.sequence.schema import (
    JobSubmissionErrorMessage,
    NoJobFoundMessage,
    SearchAccession,
    SearchInProgressMessage,
    SearchSuccessMessage,
    Sequence,
)
from worker.worker import retrieve_result

sequence_route = APIRouter()


@sequence_route.post(
    "/search",
    status_code=HTTP_202_ACCEPTED,
    response_model=str,
    responses={
        HTTP_200_OK: {"model": SearchSuccessMessage},
        HTTP_202_ACCEPTED: {"model": SearchSuccessMessage},
        HTTP_400_BAD_REQUEST: {"model": JobSubmissionErrorMessage},
    },
    tags=["Sequence"],
)
async def search(sequence: Sequence):
    hashed_sequence = generate_hash(sequence.sequence)

    try:
        job_id = await RedisCache.hget("sequence", hashed_sequence)
    except JobNotFoundException:
        job_id = None

    if job_id:
        return JSONResponse(
            content={"job_id": hashed_sequence}, status_code=HTTP_200_OK
        )

    try:
        job_id = await submit_sequence_search_job(sequence.sequence)
    except RequestSubmissionException:
        return JSONResponse(
            content={"message": JOB_SUBMISSION_ERROR_MESSAGE},
            status_code=HTTP_400_BAD_REQUEST,
        )

    logger.debug(f"Sequence {sequence.sequence} submitted to search engine")
    packed_response = msgpack.dumps(jsonable_encoder(job_id))

    await RedisCache.hset("sequence", hashed_sequence, packed_response)

    # submit the task to celery
    result_task = retrieve_result.delay(job_id, hashed_sequence)

    await RedisCache.hset("job-queue", hashed_sequence, result_task.id)

    return JSONResponse(
        status_code=HTTP_202_ACCEPTED,
        content={"job_id": hashed_sequence},
    )


@sequence_route.get(
    "/result",
    status_code=HTTP_200_OK,
    response_model=List[SearchAccession],
    responses={
        HTTP_200_OK: {"model": List[SearchAccession]},
        HTTP_202_ACCEPTED: {"model": SearchInProgressMessage},
        HTTP_400_BAD_REQUEST: {"model": NoJobFoundMessage},
    },
    tags=["Sequence"],
)
async def result(
    job_id: str,
):
    celery_job_id = None
    try:
        celery_job_id = await RedisCache.hget("job-queue", job_id)
        if not celery_job_id:
            return await handle_no_job_error(job_id)

    except JobNotFoundException:
        return await handle_no_job_error(job_id)

    try:
        celery_job = AsyncResult(celery_job_id)

        if celery_job.status in ["STARTED", "PENDING"]:
            return JSONResponse(
                status_code=HTTP_202_ACCEPTED,
                content={"message": SEARCH_IN_PROGRESS_MESSAGE},
            )
        elif celery_job.status == "SUCCESS":

            if not celery_job.result:
                return JSONResponse(
                    status_code=HTTP_404_NOT_FOUND,
                    content={},
                )

            return [x for x in celery_job.result.values()]

        elif celery_job.status == "FAILURE":
            await RedisCache.hdel("job-queue", job_id)
            await RedisCache.hdel("sequence", job_id)

            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"message": JOB_FAILED_ERROR_MESSAGE},
            )

    except JobResultsNotFoundException:
        return await handle_no_job_error(job_id)
