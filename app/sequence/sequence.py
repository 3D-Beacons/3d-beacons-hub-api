from typing import Dict, List

import msgpack
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
    get_job_id,
    get_job_json_results,
    get_job_results_from_cache,
    get_job_status,
    prepare_dictionary_of_summary_results,
    prepare_hit_dictionary,
    prepare_paginated_accessions,
    set_job_results_in_cache,
    submit_sequence_search_job,
)
from app.sequence.schema import (
    ErrorMessage,
    NoJobFoundMessage,
    SearchAccession,
    SearchInProgressMessage,
    SearchResults,
    SearchSuccessMessage,
    Sequence,
)

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
async def search(sequence: Sequence):
    hashed_sequence = generate_hash(sequence.sequence)

    try:
        job_id = await get_job_id(hashed_sequence)
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
    return JSONResponse(
        status_code=HTTP_202_ACCEPTED,
        content={"job_id": hashed_sequence},
    )


@sequence_route.get(
    "/hits",
    status_code=HTTP_200_OK,
    response_model=List[SearchAccession],
    responses={
        HTTP_200_OK: {"model": List[SearchAccession]},
        HTTP_202_ACCEPTED: {"model": SearchInProgressMessage},
        HTTP_400_BAD_REQUEST: {"model": NoJobFoundMessage},
    },
    include_in_schema=True,
    tags=["Sequence"],
)
async def get_hits(job_id: str):
    try:
        actual_job_id = await get_job_id(job_id)
    except JobNotFoundException:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": "No search request found for this sequence"},
        )

    # check if there are cached results for the job
    try:
        job_result_hit_dictionary = await get_job_results_from_cache(actual_job_id)
        return [x for x in job_result_hit_dictionary.values()]
    except JobResultsNotFoundException:
        job_result_hit_dictionary = None

    try:
        job_status = await get_job_status(actual_job_id)
    except JobStatusNotFoundException:
        return await handle_no_job_found(job_id, actual_job_id)

    # sends wait response if job is still running
    if job_status == "RUNNING":
        return JSONResponse(
            status_code=HTTP_202_ACCEPTED,
            content={"message": "Search in progress, please try after sometime!"},
        )
    elif job_status == "NOT_FOUND":
        return await handle_no_job_found(job_id, actual_job_id)

    json_results_resp = await get_job_json_results(actual_job_id)

    if not json_results_resp:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": "No search request found for this sequence"},
        )

    hit_dictionary = prepare_hit_dictionary(json_results_resp["hits"])

    if not hit_dictionary:
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content={"message": "No hits found for this sequence"},
        )

    await set_job_results_in_cache(actual_job_id, hit_dictionary)

    return [x for x in hit_dictionary.values()]


@sequence_route.get(
    "/result",
    status_code=HTTP_200_OK,
    response_model=SearchResults,
    responses={
        HTTP_200_OK: {"model": SearchResults},
        HTTP_202_ACCEPTED: {"model": SearchInProgressMessage},
        HTTP_400_BAD_REQUEST: {"model": NoJobFoundMessage},
    },
    tags=["Sequence"],
)
async def result(
    job_id: str,
    page_num: int = 0,
):
    try:
        actual_job_id = await get_job_id(job_id)
    except JobNotFoundException:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": "No search request found for this sequence"},
        )

    # check if there are cached results for the job
    try:
        job_result_hit_dictionary = await get_job_results_from_cache(actual_job_id)
    except JobResultsNotFoundException:
        job_result_hit_dictionary = None

    if job_result_hit_dictionary:
        summary_result = await prepare_summary_result(
            job_result_hit_dictionary, page_num
        )

        if not summary_result:
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content={},
            )

        return {
            "hits": summary_result,
            "total_hits": len(job_result_hit_dictionary),
            "current_page": page_num,
            "total_pages": len(job_result_hit_dictionary) // MAX_POST_LIMIT,
            "max_results_per_page": MAX_POST_LIMIT,
        }

    try:
        job_status = await get_job_status(actual_job_id)
    except JobStatusNotFoundException:
        return await handle_no_job_found(job_id, actual_job_id)

    # sends wait response if job is still running
    if job_status == "RUNNING":
        return JSONResponse(
            status_code=HTTP_202_ACCEPTED,
            content={"message": "Search in progress, please try after sometime!"},
        )
    # make the json response call to get the actual results
    elif job_status == "FINISHED":
        return await prepare_finished_job(actual_job_id, page_num)
    elif job_status == "NOT_FOUND":
        return await handle_no_job_found(job_id, actual_job_id)


async def handle_no_job_found(seq_hash: str, job_id: str) -> JSONResponse:
    # clear the cache if the job is not found
    await delete_from_cache("sequence", seq_hash)
    await delete_from_cache("job_results", job_id)

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"message": "No search request found for this sequence"},
    )


async def prepare_finished_job(job_id: str, page_num: int) -> JSONResponse:
    json_results_resp = await get_job_json_results(job_id)

    if not json_results_resp:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": "No search request found for this sequence"},
        )

    filtered_results = filter_json_results(json_results_resp)
    hit_dictionary = prepare_hit_dictionary(filtered_results)
    await set_job_results_in_cache(job_id, hit_dictionary)

    summary_result = await prepare_summary_result(hit_dictionary, page_num)

    if not summary_result:
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content={},
        )

    return {
        "hits": summary_result,
        "total_hits": len(hit_dictionary),
        "current_page": page_num,
        "total_pages": len(hit_dictionary) // MAX_POST_LIMIT,
        "max_results_per_page": MAX_POST_LIMIT,
    }


async def prepare_summary_result(hit_dictionary: Dict, page_num: int) -> List:
    paginated_accessions = prepare_paginated_accessions(hit_dictionary, page_num)
    summary_dict = await prepare_dictionary_of_summary_results(paginated_accessions)
    results = []

    for accession, result in summary_dict.items():
        accession_record = hit_dictionary[accession]
        accession_record.update({"summary": result})
        results.append(accession_record)

    return results
