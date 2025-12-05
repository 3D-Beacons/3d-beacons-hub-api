from typing import Any, Dict, List, Optional

import msgpack

from worker.cache.redis_cache import RedisCache


def get_job_results(hashed_sequence: str) -> Optional[List[Any]]:
    packed = RedisCache.hget("job-results", hashed_sequence, decode=False)

    if packed is None:
        return None

    data: Dict[str, Any] = msgpack.loads(packed)
    return list(data.values())


def set_job_results(hashed_sequence: str, result):
    RedisCache.hset("job-results", hashed_sequence, msgpack.dumps(result))


def get_celery_task_id(hashed_sequence: str):
    return RedisCache.hget("sequence-task-mapping", hashed_sequence)


def get_jobdispatcher_id(hashed_sequence: str):
    return RedisCache.hget("sequence-jdid-mapping", hashed_sequence)


def set_jobdispatcher_id(hashed_sequence: str, jdispatcher_id: str):
    RedisCache.hset("sequence-jdid-mapping", hashed_sequence, jdispatcher_id)


def set_celery_task_id(hashed_sequence: str, result_task):
    RedisCache.hset("sequence-task-mapping", hashed_sequence, result_task.id)


def clear_job_results(hashed_sequence: str):
    RedisCache.hdel("job-results", hashed_sequence)


def clear_celery_task_id(hashed_sequence: str):
    RedisCache.hdel("sequence-task-mapping", hashed_sequence)


def clear_jobdispatcher_id(hashed_sequence: str):
    RedisCache.hdel("sequence-jdid-mapping", hashed_sequence)
