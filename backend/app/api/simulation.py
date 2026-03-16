from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.docking import run_docking, run_batch_docking
from app.services.admet import screen_admet, batch_screen_admet
from app.services.molecules import search_molecules, get_cancer_drug_library
from app.core.database import supabase

router = APIRouter(prefix="/simulation", tags=["simulation"])

class DockingRequest(BaseModel):
    pdb_id: str
    smiles: str
    molecule_name: str
    experiment_id: str = None

class BatchDockingRequest(BaseModel):
    pdb_id: str
    disease: str
    experiment_id: str
    use_cancer_library: bool = True

@router.post("/dock")
async def single_dock(data: DockingRequest):
    result = await run_docking(
        pdb_id=data.pdb_id,
        smiles=data.smiles,
        molecule_name=data.molecule_name
    )
    if data.experiment_id:
        try:
            supabase.table("results").insert({
                "experiment_id": data.experiment_id,
                "iteration": 1,
                "molecule_name": data.molecule_name,
                "smiles": data.smiles,
                "binding_affinity": result.get("binding_affinity"),
                "admet_pass": True,
                "confidence": result.get("confidence"),
                "rank": 1
            }).execute()
        except:
            pass
    return result

@router.post("/batch")
async def batch_dock(data: BatchDockingRequest):
    try:
        supabase.table("experiments").update(
            {"status": "running"}
        ).eq("id", data.experiment_id).execute()
    except:
        pass

    if data.use_cancer_library:
        molecules = await get_cancer_drug_library()
    else:
        molecules = await search_molecules(data.disease, limit=20)

    molecules = batch_screen_admet(molecules)
    passing_molecules = [m for m in molecules if m.get("admet_pass")][:15]

    if not passing_molecules:
        raise HTTPException(status_code=400, detail="No molecules passed ADMET screening")

    docking_results = await run_batch_docking(data.pdb_id, passing_molecules)

    saved_results = []
    for i, result in enumerate(docking_results[:10]):
        try:
            saved = supabase.table("results").insert({
                "experiment_id": data.experiment_id,
                "iteration": i + 1,
                "molecule_name": result.get("molecule_name"),
                "smiles": result.get("smiles"),
                "binding_affinity": result.get("binding_affinity"),
                "admet_pass": result.get("lipinski_pass", True),
                "molecular_weight": result.get("molecular_weight"),
                "confidence": result.get("confidence"),
                "rank": result.get("rank")
            }).execute()
            saved_results.append(saved.data[0] if saved.data else result)
        except:
            saved_results.append(result)

    top = docking_results[0] if docking_results else {}
    try:
        supabase.table("experiments").update({
            "status": "completed",
            "current_iteration": len(docking_results),
            "top_candidate": top.get("molecule_name"),
            "top_score": top.get("binding_affinity")
        }).eq("id", data.experiment_id).execute()
    except:
        pass

    return {
        "experiment_id": data.experiment_id,
        "total_screened": len(molecules),
        "admet_passed": len(passing_molecules),
        "docked": len(docking_results),
        "top_candidate": top,
        "results": docking_results
    }

@router.post("/admet")
async def admet_screen(molecule: dict):
    return screen_admet(molecule)
