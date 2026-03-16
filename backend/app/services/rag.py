import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.database import supabase
from app.services.pubmed import fetch_papers_for_target
from typing import List, Dict

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> List[float]:
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def embed_batch(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return embeddings.tolist()

async def index_papers(papers: List[Dict]) -> int:
    if not papers:
        return 0

    texts = [
        f"{p.get('title', '')} {p.get('abstract', '')}"
        for p in papers
    ]
    embeddings = embed_batch(texts)
    indexed = 0

    for paper, embedding in zip(papers, embeddings):
        try:
            existing = supabase.table("literature").select("id").eq(
                "pmid", paper["pmid"]
            ).execute()

            if existing.data:
                continue

            supabase.table("literature").insert({
                "pmid": paper["pmid"],
                "title": paper["title"],
                "abstract": paper.get("abstract", ""),
                "authors": paper.get("authors", []),
                "journal": paper.get("journal", ""),
                "year": paper.get("year", 0),
                "keywords": paper.get("keywords", []),
                "embedding": embedding
            }).execute()
            indexed += 1
        except Exception as e:
            continue

    return indexed

async def search_literature(query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
    query_embedding = embed_text(query)

    try:
        response = supabase.rpc("match_literature", {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit
        }).execute()

        if response.data:
            return response.data
    except:
        pass

    try:
        response = supabase.table("literature").select(
            "pmid, title, abstract, authors, journal, year"
        ).limit(limit).execute()
        return response.data or []
    except:
        return []

async def build_rag_context(query: str, limit: int = 3) -> str:
    papers = await search_literature(query, limit=limit)

    if not papers:
        return "No supporting literature found in database."

    context_parts = []
    for paper in papers:
        part = f"[PMID {paper.get('pmid')}] {paper.get('title')} — {paper.get('abstract', '')[:300]}..."
        context_parts.append(part)

    return "\n\n".join(context_parts)

async def fetch_and_index_for_experiment(
    target_protein: str,
    disease: str
) -> Dict:
    papers = await fetch_papers_for_target(target_protein, disease, limit=20)
    indexed = await index_papers(papers)
    return {
        "papers_found": len(papers),
        "papers_indexed": indexed,
        "target": target_protein,
        "disease": disease
    }
