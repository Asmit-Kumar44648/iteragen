import json
import asyncio
from upstash_redis import Redis
from app.core.config import UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN
from app.core.database import supabase

redis = Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)

QUEUE_KEY = "iteragen:jobs"
PROCESSING_KEY = "iteragen:processing"
RESULTS_KEY = "iteragen:results"

def enqueue_job(job: dict) -> str:
    job_id = job.get("experiment_id")
    redis.lpush(QUEUE_KEY, json.dumps(job))
    redis.hset(PROCESSING_KEY, job_id, json.dumps({
        "status": "queued",
        "experiment_id": job_id,
        "created_at": str(asyncio.get_event_loop().time()) if asyncio.get_event_loop().is_running() else "0"
    }))
    return job_id

def get_job_status(experiment_id: str) -> dict:
    status = redis.hget(PROCESSING_KEY, experiment_id)
    if status:
        try:
            return json.loads(status)
        except:
            return {"status": "unknown", "experiment_id": experiment_id}
    return {"status": "not_found", "experiment_id": experiment_id}

def update_job_status(experiment_id: str, status: str, data: dict = None):
    payload = {"status": status, "experiment_id": experiment_id}
    if data:
        payload.update(data)
    redis.hset(PROCESSING_KEY, experiment_id, json.dumps(payload))

def get_queue_length() -> int:
    return redis.llen(QUEUE_KEY)

def dequeue_job() -> dict:
    job_data = redis.rpop(QUEUE_KEY)
    if job_data:
        try:
            return json.loads(job_data)
        except:
            return None
    return None

def save_result(experiment_id: str, result: dict):
    redis.hset(RESULTS_KEY, experiment_id, json.dumps(result))
    redis.expire(RESULTS_KEY, 86400)

def get_result(experiment_id: str) -> dict:
    result = redis.hget(RESULTS_KEY, experiment_id)
    if result:
        try:
            return json.loads(result)
        except:
            return None
    return None

def get_queue_stats() -> dict:
    return {
        "queued": redis.llen(QUEUE_KEY),
        "processing": redis.hlen(PROCESSING_KEY),
        "results_cached": redis.hlen(RESULTS_KEY)
    }
