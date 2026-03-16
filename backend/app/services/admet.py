def screen_admet(molecule: dict) -> dict:
    mw = float(molecule.get("molecular_weight", 0))
    logp = float(molecule.get("xlogp", 0))
    hbd = int(molecule.get("hbd", 0))
    hba = int(molecule.get("hba", 0))
    tpsa = float(molecule.get("tpsa", 0))
    rotatable = int(molecule.get("rotatable_bonds", 0))

    flags = []
    passed = True

    if mw > 500:
        flags.append(f"High MW: {mw} Da (>500)")
        passed = False
    if logp > 5:
        flags.append(f"High LogP: {logp} (>5, poor solubility)")
        passed = False
    if logp < -2:
        flags.append(f"Low LogP: {logp} (<-2, poor permeability)")
        passed = False
    if hbd > 5:
        flags.append(f"High HBD: {hbd} (>5)")
        passed = False
    if hba > 10:
        flags.append(f"High HBA: {hba} (>10)")
        passed = False
    if tpsa > 140:
        flags.append(f"High TPSA: {tpsa} (>140, poor absorption)")
        passed = False
    if rotatable > 10:
        flags.append(f"High rotatable bonds: {rotatable} (>10, poor oral bioavailability)")

    toxicity_risk = "low"
    if logp > 4.5 or mw > 450:
        toxicity_risk = "moderate"
    if logp > 5.5 or mw > 600:
        toxicity_risk = "high"
        passed = False
        flags.append("High toxicity risk based on physicochemical properties")

    bioavailability = "good"
    if tpsa > 120 or mw > 450:
        bioavailability = "moderate"
    if tpsa > 140 or mw > 500:
        bioavailability = "poor"

    return {
        "admet_pass": passed,
        "toxicity_risk": toxicity_risk,
        "bioavailability": bioavailability,
        "flags": flags,
        "lipinski_violations": len([f for f in flags if any(x in f for x in ["MW", "LogP", "HBD", "HBA"])]),
        "drug_likeness_score": round(max(0, 1 - (len(flags) * 0.15)), 2)
    }

def batch_screen_admet(molecules: list) -> list:
    results = []
    for mol in molecules:
        admet = screen_admet(mol)
        mol_with_admet = {**mol, **admet}
        results.append(mol_with_admet)
    passing = [m for m in results if m.get("admet_pass")]
    failing = [m for m in results if not m.get("admet_pass")]
    return passing + failing
