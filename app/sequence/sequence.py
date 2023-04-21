from typing import List

from celery.result import AsyncResult
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app import logger
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
from app.utils import include_in_schema
from worker.cache.utils import (
    clear_celery_task_id,
    clear_jobdispatcher_id,
    get_celery_task_id,
    get_jobdispatcher_id,
    set_celery_task_id,
    set_jobdispatcher_id,
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
    include_in_schema=include_in_schema(),
)
async def search(sequence: Sequence):
    hashed_sequence = generate_hash(sequence.sequence)

    try:
        jdispatcher_id = get_jobdispatcher_id(hashed_sequence)
    except JobNotFoundException:
        jdispatcher_id = None

    if jdispatcher_id:
        return JSONResponse(
            content={"job_id": hashed_sequence}, status_code=HTTP_200_OK
        )

    try:
        jdispatcher_id = await submit_sequence_search_job(sequence.sequence)
    except RequestSubmissionException:
        return JSONResponse(
            content={"message": JOB_SUBMISSION_ERROR_MESSAGE},
            status_code=HTTP_400_BAD_REQUEST,
        )

    logger.debug(f"Sequence {sequence.sequence} submitted to search engine")

    set_jobdispatcher_id(hashed_sequence, jdispatcher_id)

    # submit the task to celery
    result_task = retrieve_result.delay(jdispatcher_id, hashed_sequence)

    set_celery_task_id(hashed_sequence, result_task)

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
    include_in_schema=include_in_schema(),
)
async def result(
    job_id: str,
):
    celery_job_id = None

    try:
        celery_job_id = get_celery_task_id(hashed_sequence=job_id)
        if not celery_job_id:
            return await handle_no_job_error(job_id)

    except JobNotFoundException:
        return await handle_no_job_error(job_id)

    try:
        celery_job = AsyncResult(celery_job_id)

        if celery_job.status == "SUCCESS":
            result = celery_job.get()

            if not result:
                return JSONResponse(
                    status_code=HTTP_404_NOT_FOUND,
                    content={},
                )
            else:
                return [x for x in result.values()]

        elif celery_job.status in ["STARTED", "PENDING"]:
            return JSONResponse(
                status_code=HTTP_202_ACCEPTED,
                content={"message": SEARCH_IN_PROGRESS_MESSAGE},
            )
        elif celery_job.status == "FAILURE":
            clear_celery_task_id(hashed_sequence=job_id)
            clear_jobdispatcher_id(hashed_sequence=job_id)

            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"message": JOB_FAILED_ERROR_MESSAGE},
            )

    except JobResultsNotFoundException:
        return await handle_no_job_error(job_id)
