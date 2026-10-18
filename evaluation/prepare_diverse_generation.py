"""Prepare 1000 varied generation cases offline in a new directory.

This prepares 4000 main scheduling attempts across two models; it never calls
models. The separate 24 wording variants are not part of that allowance.
"""
import argparse
import hashlib
from pathlib import Path

from scheduling.evaluation import diverse_generation as design
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.runner import write_new
from scheduling.evaluation.scoring import digest
from scheduling.schema import to_data


def prepare(directory, *, seed=design.DEFAULT_SEED, reference_seconds=60):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError("Use a new dataset directory; old cases and evidence are immutable")
    cases, proofs = design.build_suite(seed=seed, reference_seconds=reference_seconds)
    bundle = case_bundle(cases)
    manifest = {
        "format_version": "1.0", "dataset_version": design.VERSION,
        "campaign_policy": design.CAMPAIGN_POLICY, "seed": seed,
        "status": "offline_verified_development_pending_human_review",
        "seed_semantics": "Changes durations, activity windows, participant/resource incidence, precedence edges, preference targets and neutral IDs; generator families remain related, not independent held-out samples.",
        "generator_sha256": hashlib.sha256(Path(design.__file__).read_bytes()).hexdigest(),
        "preparation_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "case_bundle_sha256": digest(bundle), "proofs_sha256": digest(proofs),
        "coverage": design.verify_suite(cases, proofs), "structural_audit": structural_audit(cases),
        "models": list(design.MODELS), "expected_response_models": dict(design.EXPECTED_RESPONSE_MODELS),
        "counts": dict(design.COUNTS), "reference_solver_seconds_per_case": reference_seconds,
        "budget_per_model": dict(design.BUDGET_PER_MODEL),
        "optional_wording_selection": design.optional_wording_selection(cases),
        "human_gold_review": "pending", "human_wording_review": "pending", "new_model_calls": 0,
        "limitations": [
            "AI-assisted constructed development inputs; not real calendars, human-reviewed or pristine held-out evidence.",
            "1000 distinct hard fingerprints and 500 matched label pairs remain nested in ten conservative generator families; they are not 1000 independent populations.",
            "Tier names are size/interaction construction targets, not measured model difficulty or an upper-bound guarantee.",
            "Of 500 UNSAT cases, 100 have whole-instance capacity certificates involving all activities and 400 have independently exhaustively checked cores of at most four activities. Neither certificate establishes computational search hardness.",
            "Matched labels share constraint kinds/counts and incidence; numeric restrictions necessarily differ. Empty unary domains are excluded, but other statistical cues may remain.",
            "All added activities are coupled to the existing interaction network; larger cases add constraints and alternatives rather than only renamed text.",
            "Single-day 30-minute grid with 8/12/16/24/32 activities. All eight-activity cases use 09:00-17:00. Capacity stress tiers use up to 48 slots and 30-60-minute activities; other tiers use up to 32 slots and 60-90-minute activities. Midnight-based long shifts are synthetic stress tests, not ordinary office calendars. No multi-day planning or uncertainty semantics.",
            "Preferences are weighted preferred-start windows, not consecutive-meeting or weekly-clustering objectives.",
            "The 24 preselected reordered variants are order-robustness conditions sharing canonical gold, not additional independent problems or semantic paraphrases; excluded from the main 4000 attempts.",
            "Every UNSAT certificate is verified independently of CP-SAT; reference objective optimality additionally relies on the CP-SAT compiler.",
            "Preparation authorizes no inference. Human review and explicit frozen execution authorization remain separate gates.",
        ],
    }
    design.validate_manifest(cases, proofs, manifest)
    review = {"format_version": "1.0", "dataset_version": design.VERSION,
        "case_bundle_sha256": digest(bundle), "human_review_status": "pending",
        "warning": "Evaluator-only gold/labels/certificates: never send this review file to a measured model.",
        "cases": [{"case_id": c.case_id, "group_id": c.group_id, "pair_id": proofs[c.case_id]["pair_id"],
            "mechanism": c.sweep, "stratum": c.level, "expected_label": c.expected_label,
            "problem": to_data(c.problem), "renderings": {r.variant_id: r.text for r in c.authored_renderings},
            "proof": proofs[c.case_id], "review_status": "pending", "reviewer": None, "review_notes": None}
            for c in cases]}
    directory.mkdir(parents=True, exist_ok=False)
    for name, content in (("cases", bundle), ("proofs", proofs), ("manifest", manifest), ("review", review)):
        write_new(directory / f"{name}.json", content)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--seed", type=int, default=design.DEFAULT_SEED)
    parser.add_argument("--reference-seconds", type=float, default=60)
    args = parser.parse_args()
    result = prepare(args.directory, seed=args.seed, reference_seconds=args.reference_seconds)
    print({"status": result["status"], **result["counts"], "new_model_calls": 0})


if __name__ == "__main__":
    main()
