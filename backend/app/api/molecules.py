from fastapi import APIRouter, HTTPException
from app.services.molecules import search_molecules, fetch_molecule_by_name, get_cancer_drug_library

router = APIRouter(prefix="/molecules", tags=["molecules"])

@router.get("/search/{query}")
async def search(query: str, limit: int = 10):
    results = await search_molecules(query, limit)
    if not results:
        raise HTTPException(status_code=404, detail="No molecules found")
    return results

@router.get("/name/{name}")
async def get_by_name(name: str):
    return await fetch_molecule_by_name(name)

@router.get("/cancer-library")
async def cancer_drug_library():
    molecules = await get_cancer_drug_library()
    return {
        "count": len(molecules),
        "molecules": molecules
    }
