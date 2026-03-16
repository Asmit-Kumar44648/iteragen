from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.agent import (
    generate_hypothesis,
    analyze_docking_results,
    generate_final_report,
    think_next_step
)
from app.services.docking import run_batch_docking
from app.services.admet import batch_screen_admet
from app.services.molecules import get_cancer_drug_library, search_molecules
from app.core.database import supabase

router = APIRouter(prefix="/agent", tags=["agent"])

class RunAgentRequest(BaseModel):
    experiment_id: str
    target_protein: str
    disease: str
    pdb_id: str

@router.post("/run")
async def run_agent(data: RunAgentRequest):
    try:
        supabase.table("experiments").update(
            {"status": "running"}
        ).eq("id", data.experiment_id).execute()
    except:
        pass

    hypothesis = await generate_hypothesis(
        experiment_id=data.experiment_id,
        target_protein=data.target_protein,
        disease=data.disease,
        pdb_id=data.pdb_id
    )

    molecules = await get_cancer_drug_library()
    if not molecules:
        molecules = await search_molecules(data.disease, limit=20)

    molecules = batch_screen_admet(molecules)
    passing = [m for m in molecules if m.get("admet_pass")][:15]

    if not passing:
        raise HTTPException(status_code=400, detail="No molecules passed ADMET screening")

    all_results = await run_batch_docking(data.pdb_id, passing)

    analysis = await analyze_docking_results(
        experiment_id=data.experiment_id,
        target_protein=data.target_protein,
        disease=data.disease,
        results=all_results,
        iteration=1
    )

    await think_next_step(
        experiment_id=data.experiment_id,
        current_best=all_results[0] if all_results else {},
        iteration=1,
        total_iterations=3
    )

    second_pass = await search_molecules(
        analysis.get("molecules_to_explore_next", [data.disease])[0],
        limit=10
    )
    if second_pass:
        second_pass = batch_screen_admet(second_pass)
        second_passing = [m for m in second_pass if m.get("admet_pass")][:8]
        if second_passing:
            second_results = await run_batch_docking(data.pdb_id, second_passing)
            all_results.extend(second_results)
            all_results.sort(key=lambda x: x.get("binding_affinity", 0))
            for i, r in enumerate(all_results):
                r["rank"] = i + 1

    await analyze_docking_results(
        experiment_id=data.experiment_id,
        target_protein=data.target_protein,
        disease=data.disease,
        results=all_results,
        iteration=2
    )

    await think_next_step(
        experiment_id=data.experiment_id,
        current_best=all_results[0] if all_results else {},
        iteration=2,
        total_iterations=3
    )

    final_report = await generate_final_report(
        experiment_id=data.experiment_id,
        target_protein=data.target_protein,
        disease=data.disease,
        all_results=all_results,
        hypothesis=hypothesis,
        analyses=[analysis]
    )

    for i, result in enumerate(all_results[:10]):
        try:
            supabase.table("results").insert({
                "experiment_id": data.experiment_id,
                "iteration": i + 1,
                "molecule_name": result.get("molecule_name"),
                "smiles": result.get("smiles", ""),
                "binding_affinity": result.get("binding_affinity"),
                "admet_pass": result.get("lipinski_pass", True),
                "molecular_weight": result.get("molecular_weight"),
                "confidence": result.get("confidence"),
                "mechanism": final_report.get("proposed_mechanism"),
                "rank": result.get("rank", i + 1)
            }).execute()
        except:
            pass

    top = all_results[0] if all_results else {}
    try:
        supabase.table("experiments").update({
            "status": "completed",
            "current_iteration": len(all_results),
            "top_candidate": top.get("molecule_name"),
            "top_score": top.get("binding_affinity")
        }).eq("id", data.experiment_id).execute()
    except:
        pass

    return {
        "experiment_id": data.experiment_id,
        "status": "completed",
        "hypothesis": hypothesis,
        "total_screened": len(all_results),
        "top_candidate": top,
        "final_report": final_report
    }

@router.get("/logs/{experiment_id}")
async def get_logs(experiment_id: str):
    try:
        response = supabase.table("agent_logs").select("*").eq(
            "experiment_id", experiment_id
        ).order("created_at").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/hypothesis")
async def get_hypothesis(data: RunAgentRequest):
    return await generate_hypothesis(
        experiment_id=data.experiment_id,
        target_protein=data.target_protein,
        disease=data.disease,
        pdb_id=data.pdb_id
    )
