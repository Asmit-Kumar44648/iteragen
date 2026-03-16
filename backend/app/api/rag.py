from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import (
    search_literature,
    fetch_and_index_for_experiment,
    build_rag_context
)
from app.services.pubmed import fetch_papers_for_target

router = APIRouter(prefix="/rag", tags=["rag"])

class IndexRequest(BaseModel):
    target_protein: str
    disease: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/index")
async def index_literature(data: IndexRequest):
    result = await fetch_and_index_for_experiment(
        target_protein=data.target_protein,
        disease=data.disease
    )
    return result

@router.post("/search")
async def search(data: SearchRequest):
    results = await search_literature(data.query, limit=data.limit)
    if not results:
        raise HTTPException(status_code=404, detail="No literature found")
    return results

@router.get("/context/{query}")
async def get_context(query: str):
    context = await build_rag_context(query, limit=3)
    return {"query": query, "context": context}

@router.get("/papers/{target}/{disease}")
async def get_papers(target: str, disease: str):
    papers = await fetch_papers_for_target(target, disease, limit=10)
    return {"count": len(papers), "papers": papers}
