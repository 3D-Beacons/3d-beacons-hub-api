import asyncio
from typing import Dict, List

import msgpack
from fastapi import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from app import logger
from app.cache.helper import delete_from_cache
from app.cache.redis_cache import RedisCache
from app.config import MAX_POST_LIMIT
from app.exception import (
    JobNotFoundException,
    JobResultsNotFoundException,
    JobStatusNotFoundException,
    RequestSubmissionException,
)
from app.sequence.helper import (
    filter_json_results,
    generate_hash,
    get_job_id_from_cache,
    get_job_json_results,
    get_job_results_from_cache,
    get_job_status,
    prepare_accession_list,
    prepare_hit_dictionary,
    set_job_results_in_cache,
    submit_sequence_search_job,
)
from app.sequence.schema import (
    ErrorMessage,
    NoJobFoundMessage,
    SearchAccession,
    SearchInProgressMessage,
    SearchSuccessMessage,
    Sequence,
)
from app.uniprot.uniprot import get_list_of_uniprot_summary_helper

sequence_route = APIRouter()


@sequence_route.post(
    "/search",
    status_code=HTTP_202_ACCEPTED,
    response_model=str,
    responses={
        HTTP_200_OK: {"model": SearchSuccessMessage},
        HTTP_202_ACCEPTED: {"model": SearchSuccessMessage},
        HTTP_400_BAD_REQUEST: {"model": ErrorMessage},
    },
    tags=["Sequence"],
)
async def search(sequence: Sequence, background_tasks: BackgroundTasks):
    hashed_sequence = generate_hash(sequence.sequence)

    try:
        job_id = await get_job_id_from_cache(hashed_sequence)
    except JobNotFoundException:
        job_id = None

    if job_id:
        return JSONResponse(
            content={"job_id": hashed_sequence}, status_code=HTTP_200_OK
        )

    # not found in cache, submit the job
    try:
        job_id = await submit_sequence_search_job(sequence.sequence)
    except RequestSubmissionException:
        return JSONResponse(
            content={"message": "Error in submitting the job, please retry!"},
            status_code=HTTP_400_BAD_REQUEST,
        )

    logger.debug(f"Sequence {sequence.sequence} submitted to search engine")
    packed_response = msgpack.dumps(jsonable_encoder(job_id))
    await RedisCache.hset("sequence", hashed_sequence, packed_response)
    background_tasks.add_task(check_for_job_result, job_id, hashed_sequence)

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
    try:
        actual_job_id = await get_job_id_from_cache(job_id)
    except JobNotFoundException:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": "No search request found for this sequence"},
        )

    try:
        job_result_from_cache = await get_job_results_from_cache(actual_job_id)
    except JobResultsNotFoundException:
        job_result_from_cache = None

    if not job_result_from_cache:
        return await handle_no_job_found(job_id, actual_job_id)

    if job_result_from_cache == "RUNNING":
        return JSONResponse(
            status_code=HTTP_202_ACCEPTED,
            content={"message": "Search in progress, please try after sometime!"},
        )

    return [x for x in job_result_from_cache.values()]


async def handle_no_job_found(seq_hash: str, job_id: str) -> JSONResponse:
    # clear the cache if the job is not found
    await delete_from_cache("sequence", seq_hash)
    await delete_from_cache("job_results", job_id)

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"message": "No search request found for this sequence"},
    )


async def prepare_hit_dictionary_with_summary_results(hit_dictionary: Dict):
    final_hit_dictionary = {}
    for accessions_batch in divide_chunks(list(hit_dictionary.keys()), MAX_POST_LIMIT):
        accessions_obj_list = prepare_accession_list(accessions_batch)
        summary_response = await get_list_of_uniprot_summary_helper(accessions_obj_list)

        for result in summary_response:
            accession_record = hit_dictionary[result.uniprot_entry.ac]
            accession_record.update({"summary": result})
            final_hit_dictionary.update({result.uniprot_entry.ac: accession_record})

    return final_hit_dictionary


async def check_for_job_result(job_id: str, hashed_sequence: str):
    MAX_WAIT_TIME = 300
    SLEEP_TIME = 60
    waited_time = 0

    while True:
        if waited_time > MAX_WAIT_TIME:
            await delete_from_cache("job_results", job_id)
            await delete_from_cache("sequence", hashed_sequence)
            logger.warning(
                f"Waited for {MAX_WAIT_TIME} seconds for job {job_id} to finish."
            )
            break

        try:
            job_status = await get_job_status(job_id)
        except JobStatusNotFoundException:
            break
        except Exception:
            await delete_from_cache("job_results", job_id)
            await delete_from_cache("sequence", hashed_sequence)
            break

        if job_status == "RUNNING":
            await set_job_results_in_cache(job_id, "RUNNING")
            await asyncio.sleep(SLEEP_TIME)
            waited_time += SLEEP_TIME
            continue
        elif job_status == "FINISHED":
            search_job_results = await get_job_json_results(job_id)
            filtered_results = filter_json_results(search_job_results)
            hit_dictionary = prepare_hit_dictionary(filtered_results)
            final_hit_dictionary = await prepare_hit_dictionary_with_summary_results(
                hit_dictionary
            )
            await set_job_results_in_cache(job_id, final_hit_dictionary)
        elif job_status == "NOT_FOUND":
            break

    return


def divide_chunks(list: List[str], batch_size: int):
    for i in range(0, len(list), batch_size):
        yield list[i : i + batch_size]
