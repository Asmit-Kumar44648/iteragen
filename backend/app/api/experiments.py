from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import supabase
import hashlib
from datetime import datetime

router = APIRouter(prefix="/experiments", tags=["experiments"])

class CreateExperimentRequest(BaseModel):
    user_id: str
    title: str
    disease: str
    target_protein: str
    pdb_id: str
    total_iterations: int = 50

@router.post("/create")
async def create_experiment(data: CreateExperimentRequest):
    try:
        hash_input = f"{data.pdb_id}-{data.target_protein}-{datetime.utcnow().isoformat()}"
        experiment_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        response = supabase.table("experiments").insert({
            "user_id": data.user_id,
            "title": data.title,
            "disease": data.disease,
            "target_protein": data.target_protein,
            "pdb_id": data.pdb_id,
            "total_iterations": data.total_iterations,
            "status": "queued",
            "experiment_hash": experiment_hash
        }).execute()
        return {
            "experiment_id": response.data[0]["id"],
            "experiment_hash": experiment_hash,
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list/{user_id}")
async def list_experiments(user_id: str):
    try:
        response = supabase.table("experiments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str):
    try:
        exp = supabase.table("experiments").select("*").eq("id", experiment_id).single().execute()
        results = supabase.table("results").select("*").eq("experiment_id", experiment_id).order("rank").execute()
        logs = supabase.table("agent_logs").select("*").eq("experiment_id", experiment_id).order("created_at").execute()
        return {
            "experiment": exp.data,
            "results": results.data,
            "logs": logs.data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
