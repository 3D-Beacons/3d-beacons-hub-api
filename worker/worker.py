import os
import time

import redis
from celery import Celery, current_task
from celery.app import trace

from worker.helper import (
    JobStatusNotFoundException,
    filter_json_results,
    get_job_dispatcher_job_status,
    get_job_dispatcher_json_results,
    prepare_hit_dictionary,
    prepare_hit_dictionary_with_summary_results,
)

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://broker:5672")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")
celery = Celery("worker", backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
redis_cache = redis.Redis.from_url(CELERY_RESULT_BACKEND, decode_responses=True)
MAX_WAIT_TIME = int(os.environ.get("MAX_WAIT_TIME", 600))
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 60))

trace.LOG_SUCCESS = """\
Task %(name)s[%(id)s] succeeded in %(runtime)ss\
"""


@celery.task(time_limit=MAX_WAIT_TIME, soft_time_limit=MAX_WAIT_TIME - SLEEP_TIME)
def retrieve_result(job_id: str, hashed_sequence: str):
    waited_time = 0

    while True:
        existing_job = redis_cache.hget("job-queue", hashed_sequence)

        if existing_job and current_task.request.id != existing_job:
            return None

        if waited_time > MAX_WAIT_TIME:
            redis_cache.hdel("sequence", hashed_sequence)
            break
        try:
            job_status = get_job_dispatcher_job_status(job_id)
        except JobStatusNotFoundException:
            redis_cache.hdel("sequence", hashed_sequence)
            break
        except Exception:
            redis_cache.hdel("sequence", hashed_sequence)
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
                redis_cache.hdel("sequence", hashed_sequence)
                return None

            return final_hit_dictionary

        elif job_status == "NOT_FOUND":
            redis_cache.hdel("sequence", hashed_sequence)
            break

    return None
