import os
import time

from celery import Celery, current_task
from celery.app import trace

from worker.cache.redis_cache import RedisCache
from worker.cache.utils import clear_jobdispatcher_id, get_celery_task_id
from worker.helper import (
    JobStatusNotFoundException,
    filter_json_results,
    get_job_dispatcher_job_status,
    get_job_dispatcher_json_results,
    get_nested_value_from_json,
    get_uniprot_summaries,
    prepare_hit_dictionary,
    prepare_hit_dictionary_with_summary_results,
)

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/1")
celery = Celery("worker", backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
RedisCache.init_redis(REDIS_URL, "utf-8")
MAX_WAIT_TIME = int(os.environ.get("MAX_WAIT_TIME", 600))
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 20))

trace.LOG_SUCCESS = """\
Task %(name)s[%(id)s] succeeded in %(runtime)ss\
"""

celery.conf.update(
    result_serializer="msgpack",
    accept_content=["msgpack", "json"],
    result_expires=0,
)


@celery.task(
    time_limit=MAX_WAIT_TIME,
    soft_time_limit=MAX_WAIT_TIME - SLEEP_TIME,
)
def retrieve_result(job_id: str, hashed_sequence: str):
    waited_time = 0

    while True:
        existing_job = get_celery_task_id(hashed_sequence)

        if existing_job and current_task.request.id != existing_job:
            return

        if waited_time > MAX_WAIT_TIME:
            clear_jobdispatcher_id(hashed_sequence)
            break
        try:
            job_status = get_job_dispatcher_job_status(job_id)
        except JobStatusNotFoundException:
            clear_jobdispatcher_id(hashed_sequence)
            break

        if job_status == "RUNNING":
            time.sleep(SLEEP_TIME)
            waited_time += SLEEP_TIME
            continue

        elif job_status == "FINISHED":
            search_job_results = get_job_dispatcher_json_results(job_id)
            filtered_results = filter_json_results(search_job_results)
            hit_dictionary = prepare_hit_dictionary(filtered_results)
            final_hit_dictionary = prepare_hit_dictionary_with_summary_results(
                hit_dictionary
            )

            if all(not x.get("summary") for x in final_hit_dictionary.values()):
                clear_jobdispatcher_id(hashed_sequence)
                return

            # get uniprot api results
            uniprot_api_results = get_uniprot_summaries(
                list(final_hit_dictionary.keys())
            )

            for key in final_hit_dictionary:
                accession_result = uniprot_api_results.get(key)

                if accession_result:
                    protein_name = get_nested_value_from_json(
                        accession_result, "protein.recommendedName.fullName.value"
                    )

                    if not protein_name:
                        protein_name = get_nested_value_from_json(
                            accession_result, "protein.submittedName[0].fullName.value"
                        )

                    organism_names = {
                        name["type"]: name["value"]
                        for name in get_nested_value_from_json(
                            accession_result, "organism.names"
                        )
                    }

                    final_hit_dictionary[key].update(
                        {
                            "title": protein_name,
                            "hit_com_os": organism_names.get("common")
                            if organism_names.get("common")
                            else organism_names.get("scientific"),
                        }
                    )

            return final_hit_dictionary

        elif job_status == "NOT_FOUND":
            clear_jobdispatcher_id(hashed_sequence)
            break

    return
