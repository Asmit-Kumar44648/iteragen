import json
from groq import Groq
from app.core.config import GROQ_API_KEY
from app.core.database import supabase
from app.services.rag import build_rag_context

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are Iteragen, an autonomous AI drug discovery agent.
You reason like a computational chemist. You are rigorous, skeptical, and scientific.

Your job:
1. Analyze molecular docking results
2. Form hypotheses grounded in real science
3. Decide which molecules to test next
4. Explain mechanisms clearly
5. Flag uncertainty — never present estimates as conclusions

Rules you never break:
- Never fabricate a citation or mechanism without evidence
- Always state confidence level (high/medium/low)
- Always remind that results need wet lab validation
- If you are uncertain, say so explicitly
- Only cite papers that appear in the provided literature context

Output format: Always respond in valid JSON only. No prose outside JSON."""

async def log_agent_thought(experiment_id: str, log_type: str, content: str):
    try:
        supabase.table("agent_logs").insert({
            "experiment_id": experiment_id,
            "log_type": log_type,
            "content": content
        }).execute()
    except:
        pass

async def generate_hypothesis(
    experiment_id: str,
    target_protein: str,
    disease: str,
    pdb_id: str
) -> dict:
    literature_context = await build_rag_context(
        f"{target_protein} {disease} inhibitor binding mechanism",
        limit=3
    )

    prompt = f"""
Generate an initial drug discovery hypothesis for this target.

Target protein: {target_protein}
Disease: {disease}
PDB ID: {pdb_id}

Supporting literature:
{literature_context}

Respond in this exact JSON format:
{{
  "hypothesis": "one clear sentence hypothesis",
  "mechanism": "proposed binding mechanism",
  "key_features": ["feature1", "feature2", "feature3"],
  "molecule_classes_to_test": ["class1", "class2"],
  "confidence": "low|medium|high",
  "reasoning": "brief scientific reasoning",
  "citations": ["PMID if mentioned in literature above, else empty"],
  "search_terms": ["term1", "term2", "term3"],
  "literature_grounded": true
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
    except:
        result = {
            "hypothesis": f"Testing known inhibitors against {target_protein} binding site",
            "mechanism": "Competitive inhibition at ATP binding site",
            "key_features": ["hydrogen bonding", "hydrophobic contacts", "selectivity"],
            "molecule_classes_to_test": ["kinase inhibitors", "small molecule drugs"],
            "confidence": "medium",
            "reasoning": "Standard approach for kinase targets",
            "citations": [],
            "search_terms": [target_protein, disease, "inhibitor"],
            "literature_grounded": False
        }

    await log_agent_thought(
        experiment_id,
        "hypothesis",
        f"Hypothesis: {result.get('hypothesis')} | Citations: {result.get('citations')} | Grounded: {result.get('literature_grounded')}"
    )
    return result

async def analyze_docking_results(
    experiment_id: str,
    target_protein: str,
    disease: str,
    results: list,
    iteration: int
) -> dict:
    top_results = results[:5]
    results_summary = []
    for r in top_results:
        results_summary.append({
            "molecule": r.get("molecule_name"),
            "binding_affinity": r.get("binding_affinity"),
            "confidence": r.get("confidence"),
            "admet_pass": r.get("admet_pass", False),
            "mw": r.get("molecular_weight")
        })

    top_mol = top_results[0].get("molecule_name", "") if top_results else ""
    literature_context = await build_rag_context(
        f"{top_mol} {target_protein} binding affinity mechanism",
        limit=2
    )

    prompt = f"""
Analyze these docking results for iteration {iteration}.

Target: {target_protein} ({disease})
Results: {json.dumps(results_summary, indent=2)}

Supporting literature:
{literature_context}

Respond in this exact JSON format:
{{
  "analysis": "brief analysis of results",
  "top_candidate": "molecule name",
  "top_candidate_reason": "why this is best",
  "mechanism_hypothesis": "proposed binding mechanism",
  "next_steps": ["step1", "step2"],
  "molecules_to_explore_next": ["name1", "name2"],
  "confidence": "low|medium|high",
  "iteration_verdict": "promising|neutral|disappointing",
  "citations": ["PMID if in literature above"],
  "warning": "any concerns"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )

    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
    except:
        top = top_results[0] if top_results else {}
        result = {
            "analysis": f"Analyzed {len(results)} compounds.",
            "top_candidate": top.get("molecule_name", "unknown"),
            "top_candidate_reason": f"Best binding affinity at {top.get('binding_affinity')} kcal/mol",
            "mechanism_hypothesis": "Competitive inhibition at active site",
            "next_steps": ["validate in cell assay", "explore analogs"],
            "molecules_to_explore_next": ["similar scaffolds"],
            "confidence": "medium",
            "iteration_verdict": "promising",
            "citations": [],
            "warning": "All results require experimental validation"
        }

    await log_agent_thought(
        experiment_id,
        "result",
        f"Iteration {iteration}: {result.get('analysis')} | Top: {result.get('top_candidate')} | Verdict: {result.get('iteration_verdict')}"
    )
    return result

async def generate_final_report(
    experiment_id: str,
    target_protein: str,
    disease: str,
    all_results: list,
    hypothesis: dict,
    analyses: list
) -> dict:
    top_5 = all_results[:5]
    top_summary = [
        {
            "rank": i + 1,
            "molecule": r.get("molecule_name"),
            "score": r.get("binding_affinity"),
            "confidence": r.get("confidence")
        }
        for i, r in enumerate(top_5)
    ]

    literature_context = await build_rag_context(
        f"{target_protein} {disease} drug candidate therapeutic",
        limit=3
    )

    prompt = f"""
Generate a final research report.

Target: {target_protein}
Disease: {disease}
Total screened: {len(all_results)}
Top candidates: {json.dumps(top_summary, indent=2)}
Initial hypothesis: {hypothesis.get('hypothesis')}

Supporting literature:
{literature_context}

Respond in this exact JSON format:
{{
  "executive_summary": "2-3 sentence summary",
  "top_candidate": "best molecule name",
  "top_candidate_score": "binding affinity",
  "proposed_mechanism": "detailed mechanism",
  "key_findings": ["finding1", "finding2", "finding3"],
  "recommended_next_experiments": ["experiment1", "experiment2"],
  "limitations": ["limitation1", "limitation2"],
  "citations": ["PMID if in literature above"],
  "confidence_overall": "low|medium|high",
  "disclaimer": "For research use only. All results require wet lab validation."
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1200
    )

    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
    except:
        top = top_5[0] if top_5 else {}
        result = {
            "executive_summary": f"Screened {len(all_results)} compounds against {target_protein}.",
            "top_candidate": top.get("molecule_name", "unknown"),
            "top_candidate_score": str(top.get("binding_affinity", "N/A")),
            "proposed_mechanism": "Competitive inhibition at primary binding site",
            "key_findings": [f"Top binding: {top.get('binding_affinity')} kcal/mol"],
            "recommended_next_experiments": ["In vitro cell assay", "Western blot"],
            "limitations": ["In silico predictions only", "Requires wet lab validation"],
            "citations": [],
            "confidence_overall": "medium",
            "disclaimer": "For research use only. All results require wet lab validation."
        }

    await log_agent_thought(
        experiment_id,
        "result",
        f"Final report: Top candidate: {result.get('top_candidate')}. {result.get('executive_summary')}"
    )
    return result

async def think_next_step(
    experiment_id: str,
    current_best: dict,
    iteration: int,
    total_iterations: int
) -> str:
    prompt = f"""
Current iteration: {iteration}/{total_iterations}
Current best: {current_best.get('molecule_name')}
Score: {current_best.get('binding_affinity')} kcal/mol

Respond in JSON:
{{
  "next_action": "brief next step",
  "reasoning": "scientific reasoning"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=300
    )

    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
        thought = result.get("next_action", "Continuing screening")
    except:
        thought = "Exploring structural analogs of top candidate"

    await log_agent_thought(experiment_id, "thinking", thought)
    return thought
