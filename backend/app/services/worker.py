import asyncio
from app.services.queue import (
    dequeue_job,
    update_job_status,
    save_result,
    get_queue_length
)
from app.services.agent import (
    generate_hypothesis,
    analyze_docking_results,
    generate_final_report,
    think_next_step
)
from app.services.docking import run_batch_docking
from app.services.admet import batch_screen_admet
from app.services.molecules import get_cancer_drug_library, search_molecules
from app.services.rag import fetch_and_index_for_experiment
from app.core.database import supabase

async def process_job(job: dict):
    experiment_id = job.get("experiment_id")
    target_protein = job.get("target_protein")
    disease = job.get("disease")
    pdb_id = job.get("pdb_id")

    try:
        update_job_status(experiment_id, "indexing_literature")
        supabase.table("experiments").update(
            {"status": "running"}
        ).eq("id", experiment_id).execute()

        await fetch_and_index_for_experiment(target_protein, disease)

        update_job_status(experiment_id, "generating_hypothesis")
        hypothesis = await generate_hypothesis(
            experiment_id=experiment_id,
            target_protein=target_protein,
            disease=disease,
            pdb_id=pdb_id
        )

        update_job_status(experiment_id, "fetching_molecules")
        molecules = await get_cancer_drug_library()
        if not molecules:
            molecules = await search_molecules(disease, limit=20)

        molecules = batch_screen_admet(molecules)
        passing = [m for m in molecules if m.get("admet_pass")][:15]

        if not passing:
            raise Exception("No molecules passed ADMET screening")

        update_job_status(experiment_id, "docking_round_1",
            {"progress": "0%", "total_molecules": len(passing)})

        all_results = await run_batch_docking(pdb_id, passing)

        update_job_status(experiment_id, "analyzing_round_1")
        analysis = await analyze_docking_results(
            experiment_id=experiment_id,
            target_protein=target_protein,
            disease=disease,
            results=all_results,
            iteration=1
        )

        await think_next_step(
            experiment_id=experiment_id,
            current_best=all_results[0] if all_results else {},
            iteration=1,
            total_iterations=3
        )

        update_job_status(experiment_id, "docking_round_2")
        next_molecules_query = analysis.get(
            "molecules_to_explore_next", [disease]
        )
        query = next_molecules_query[0] if next_molecules_query else disease
        second_pass = await search_molecules(query, limit=10)

        if second_pass:
            second_pass = batch_screen_admet(second_pass)
            second_passing = [m for m in second_pass if m.get("admet_pass")][:8]
            if second_passing:
                second_results = await run_batch_docking(pdb_id, second_passing)
                all_results.extend(second_results)
                all_results.sort(key=lambda x: x.get("binding_affinity", 0))
                for i, r in enumerate(all_results):
                    r["rank"] = i + 1

        update_job_status(experiment_id, "analyzing_round_2")
        await analyze_docking_results(
            experiment_id=experiment_id,
            target_protein=target_protein,
            disease=disease,
            results=all_results,
            iteration=2
        )

        await think_next_step(
            experiment_id=experiment_id,
            current_best=all_results[0] if all_results else {},
            iteration=2,
            total_iterations=3
        )

        update_job_status(experiment_id, "generating_report")
        final_report = await generate_final_report(
            experiment_id=experiment_id,
            target_protein=target_protein,
            disease=disease,
            all_results=all_results,
            hypothesis=hypothesis,
            analyses=[analysis]
        )

        for i, result in enumerate(all_results[:10]):
            try:
                supabase.table("results").insert({
                    "experiment_id": experiment_id,
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
        supabase.table("experiments").update({
            "status": "completed",
            "current_iteration": len(all_results),
            "top_candidate": top.get("molecule_name"),
            "top_score": top.get("binding_affinity")
        }).eq("id", experiment_id).execute()

        final_data = {
            "experiment_id": experiment_id,
            "status": "completed",
            "hypothesis": hypothesis,
            "total_screened": len(all_results),
            "top_candidate": top,
            "final_report": final_report
        }

        save_result(experiment_id, final_data)
        update_job_status(experiment_id, "completed", {
            "top_candidate": top.get("molecule_name"),
            "top_score": top.get("binding_affinity")
        })

        return final_data

    except Exception as e:
        update_job_status(experiment_id, "failed", {"error": str(e)})
        try:
            supabase.table("experiments").update(
                {"status": "failed"}
            ).eq("id", experiment_id).execute()
        except:
            pass
        raise e

async def run_worker():
    print("Worker started. Waiting for jobs...")
    while True:
        try:
            queue_length = get_queue_length()
            if queue_length > 0:
                job = dequeue_job()
                if job:
                    print(f"Processing job: {job.get('experiment_id')}")
                    await process_job(job)
                    print(f"Job completed: {job.get('experiment_id')}")
            else:
                await asyncio.sleep(3)
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(5)
