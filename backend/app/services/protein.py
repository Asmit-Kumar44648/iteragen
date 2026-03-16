import httpx
from fastapi import HTTPException

RCSB_URL = "https://data.rcsb.org/rest/v1/core/entry"
RCSB_FILE_URL = "https://files.rcsb.org/download"
RCSB_SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"

async def fetch_protein_info(pdb_id: str) -> dict:
    pdb_id = pdb_id.upper().strip()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RCSB_URL}/{pdb_id}", timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found in RCSB")
        data = response.json()
        return {
            "pdb_id": pdb_id,
            "title": data.get("struct", {}).get("title", "Unknown"),
            "resolution": data.get("refine", [{}])[0].get("ls_d_res_high", None),
            "organism": data.get("rcsb_entry_info", {}).get("source_organism_names", ["Unknown"])[0] if data.get("rcsb_entry_info", {}).get("source_organism_names") else "Unknown",
            "method": data.get("exptl", [{}])[0].get("method", "Unknown"),
            "polymer_count": data.get("rcsb_entry_info", {}).get("polymer_entity_count", 0),
            "download_url": f"{RCSB_FILE_URL}/{pdb_id}.pdb"
        }

async def search_proteins_by_disease(disease: str, limit: int = 5) -> list:
    query = {
        "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {"value": disease}
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {"start": 0, "rows": limit},
            "sort": [{"sort_by": "score", "direction": "desc"}]
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(RCSB_SEARCH_URL, json=query, timeout=15)
        if response.status_code != 200:
            return []
        data = response.json()
        results = []
        for hit in data.get("result_set", []):
            pdb_id = hit.get("identifier", "")
            if pdb_id:
                try:
                    info = await fetch_protein_info(pdb_id)
                    results.append(info)
                except:
                    continue
        return results

async def download_pdb_structure(pdb_id: str) -> str:
    pdb_id = pdb_id.upper().strip()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RCSB_FILE_URL}/{pdb_id}.pdb", timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Could not download structure for {pdb_id}")
        return response.text
