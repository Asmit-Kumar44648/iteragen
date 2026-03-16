import httpx
from fastapi import HTTPException

PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

async def search_molecules(query: str, limit: int = 20) -> list:
    async with httpx.AsyncClient() as client:
        search_url = f"{PUBCHEM_URL}/compound/name/{query}/cids/JSON?MaxRecords={limit}"
        response = await client.get(search_url, timeout=15)
        if response.status_code != 200:
            return []
        data = response.json()
        cids = data.get("IdentifierList", {}).get("CID", [])
        molecules = []
        for cid in cids[:limit]:
            try:
                mol = await fetch_molecule_by_cid(cid)
                if mol:
                    molecules.append(mol)
            except:
                continue
        return molecules

async def fetch_molecule_by_cid(cid: int) -> dict:
    async with httpx.AsyncClient() as client:
        props = "MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA"
        url = f"{PUBCHEM_URL}/compound/cid/{cid}/property/{props}/JSON"
        response = await client.get(url, timeout=15)
        if response.status_code != 200:
            return None
        data = response.json()
        props_data = data.get("PropertyTable", {}).get("Properties", [{}])[0]
        mw = props_data.get("MolecularWeight", 0)
        hbd = props_data.get("HBondDonorCount", 0)
        hba = props_data.get("HBondAcceptorCount", 0)
        xlogp = props_data.get("XLogP", 0)
        lipinski_pass = (
            float(mw) <= 500 and
            int(hbd) <= 5 and
            int(hba) <= 10 and
            float(xlogp) <= 5
        )
        return {
            "cid": cid,
            "name": props_data.get("IUPACName", f"Compound-{cid}"),
            "smiles": props_data.get("CanonicalSMILES", ""),
            "molecular_formula": props_data.get("MolecularFormula", ""),
            "molecular_weight": float(mw) if mw else 0,
            "xlogp": float(xlogp) if xlogp else 0,
            "hbd": int(hbd) if hbd else 0,
            "hba": int(hba) if hba else 0,
            "tpsa": float(props_data.get("TPSA", 0)) if props_data.get("TPSA") else 0,
            "rotatable_bonds": int(props_data.get("RotatableBondCount", 0)),
            "lipinski_pass": lipinski_pass,
            "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
        }

async def fetch_molecule_by_name(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        url = f"{PUBCHEM_URL}/compound/name/{name}/cids/JSON"
        response = await client.get(url, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Molecule {name} not found")
        data = response.json()
        cids = data.get("IdentifierList", {}).get("CID", [])
        if not cids:
            raise HTTPException(status_code=404, detail=f"Molecule {name} not found")
        return await fetch_molecule_by_cid(cids[0])

async def get_cancer_drug_library() -> list:
    cancer_drugs = [
        "erlotinib", "gefitinib", "afatinib", "osimertinib",
        "imatinib", "dasatinib", "nilotinib", "bosutinib",
        "sorafenib", "sunitinib", "pazopanib", "axitinib",
        "vemurafenib", "dabrafenib", "trametinib", "cobimetinib",
        "palbociclib", "ribociclib", "abemaciclib",
        "olaparib", "niraparib", "rucaparib", "talazoparib",
        "pembrolizumab", "nivolumab", "atezolizumab",
        "lapatinib", "neratinib", "tucatinib",
        "crizotinib", "alectinib", "brigatinib", "lorlatinib"
    ]
    molecules = []
    for drug in cancer_drugs:
        try:
            mol = await fetch_molecule_by_name(drug)
            if mol and mol.get("lipinski_pass"):
                molecules.append(mol)
        except:
            continue
    return molecules
