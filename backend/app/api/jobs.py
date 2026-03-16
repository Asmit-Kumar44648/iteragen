from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.queue import (
    enqueue_job,
    get_job_status,
    get_queue_stats,
    get_result
)
from app.services.worker import process_job
from app.core.database import supabase
import hashlib
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])

class SubmitJobRequest(BaseModel):
    user_id: str
    title: str
    disease: str
    target_protein: str
    pdb_id: str

@router.post("/submit")
async def submit_job(data: SubmitJobRequest, background_tasks: BackgroundTasks):
    hash_input = f"{data.pdb_id}-{data.target_protein}-{datetime.utcnow().isoformat()}"
    experiment_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    try:
        response = supabase.table("experiments").insert({
            "user_id": data.user_id,
            "title": data.title,
            "disease": data.disease,
            "target_protein": data.target_protein,
            "pdb_id": data.pdb_id,
            "total_iterations": 50,
            "status": "queued",
            "experiment_hash": experiment_hash
        }).execute()

        experiment_id = response.data[0]["id"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    job = {
        "experiment_id": experiment_id,
        "user_id": data.user_id,
        "target_protein": data.target_protein,
        "disease": data.disease,
        "pdb_id": data.pdb_id
    }

    enqueue_job(job)
    background_tasks.add_task(process_job, job)

    return {
        "experiment_id": experiment_id,
        "experiment_hash": experiment_hash,
        "status": "queued",
        "message": "Job submitted. Use /jobs/status/{experiment_id} to track progress."
    }

@router.get("/status/{experiment_id}")
async def get_status(experiment_id: str):
    status = get_job_status(experiment_id)
    try:
        db_status = supabase.table("experiments").select(
            "status, current_iteration, top_candidate, top_score"
        ).eq("id", experiment_id).single().execute()
        if db_status.data:
            status["db_status"] = db_status.data
    except:
        pass
    return status

@router.get("/result/{experiment_id}")
async def get_result_endpoint(experiment_id: str):
    result = get_result(experiment_id)
    if result:
        return result
    try:
        exp = supabase.table("experiments").select("*").eq(
            "id", experiment_id
        ).single().execute()
        results = supabase.table("results").select("*").eq(
            "experiment_id", experiment_id
        ).order("rank").execute()
        logs = supabase.table("agent_logs").select("*").eq(
            "experiment_id", experiment_id
        ).order("created_at").execute()
        return {
            "experiment": exp.data,
            "results": results.data,
            "logs": logs.data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Result not found")

@router.get("/queue/stats")
async def queue_stats():
    return get_queue_stats()
