from fastapi import APIRouter, HTTPException
from app.services.protein import fetch_protein_info, search_proteins_by_disease, download_pdb_structure

router = APIRouter(prefix="/proteins", tags=["proteins"])

@router.get("/info/{pdb_id}")
async def get_protein_info(pdb_id: str):
    return await fetch_protein_info(pdb_id)

@router.get("/search/{disease}")
async def search_proteins(disease: str, limit: int = 5):
    results = await search_proteins_by_disease(disease, limit)
    if not results:
        raise HTTPException(status_code=404, detail="No proteins found for this disease")
    return results

@router.get("/structure/{pdb_id}")
async def get_structure(pdb_id: str):
    pdb_content = await download_pdb_structure(pdb_id)
    return {"pdb_id": pdb_id.upper(), "structure": pdb_content[:500] + "...", "full_length": len(pdb_content)}
