"""Prepare the separately versioned 48-case / 96-attempt generation confirmation.

This command performs construction, arithmetic proof checks and CP-SAT reference
solving only. It never calls a model or authorizes a campaign. Use a NEW directory.
"""

import argparse
import hashlib
from pathlib import Path

from scheduling.evaluation import balanced_generation
from scheduling.evaluation.balanced_generation import (
    BUDGET_PER_MODEL, CAMPAIGN_POLICY, COUNTS, DEFAULT_SEED, EXPECTED_RESPONSE_MODELS,
    MODELS, VERSION, build_suite, profile, validate_manifest, verify_suite,
)
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.runner import write_new
from scheduling.evaluation.scoring import digest
from scheduling.schema import to_data


def prepare(directory, *, seed=DEFAULT_SEED, reference_seconds=60):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError("Use a new dataset directory; existing cases and evidence are immutable")
    cases, proofs = build_suite(seed=seed, reference_seconds=reference_seconds)
    coverage = verify_suite(cases, proofs)
    bundle = case_bundle(cases)
    manifest = {
        "format_version": "1.0", "dataset_version": VERSION, "campaign_policy": CAMPAIGN_POLICY,
        "seed": seed, "status": "offline_verified_development_pending_human_review",
        "seed_semantics": "Permutes neutral activity identifiers; numeric layouts are fixed. Another seed is not an independent held-out construction.",
        "generator_sha256": hashlib.sha256(Path(balanced_generation.__file__).read_bytes()).hexdigest(),
        "preparation_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "case_bundle_sha256": digest(bundle), "proofs_sha256": digest(proofs),
        "coverage": coverage, "structural_audit": structural_audit(cases),
        "models": list(MODELS), "expected_response_models": dict(EXPECTED_RESPONSE_MODELS),
        "counts": dict(COUNTS),
        "reference_solver_seconds_per_case": reference_seconds,
        "budget_per_model": dict(BUDGET_PER_MODEL),
        "human_gold_review": "pending", "human_wording_review": "pending", "new_model_calls": 0,
        "limitations": [
            "Constructed AI-assisted development cases; not human-reviewed, held-out, or real-calendar data.",
            "All 16 related variants per mechanism form one conservative group: only three construction families, not 48 independent samples.",
            "SAT/UNSAT labels balance within every deadline/fixed-start profile and matched type/count pair; this removes the identified presence shortcut, not every possible dataset bias.",
            "Loose/tight are numeric layout targets, not measured model difficulty or real-world coverage.",
            "The capped contract is one 2026-10-26 09:00-17:00 day, 30-minute slots, eight mandatory activities, two participants and one room.",
            "Preferences penalize starting outside the morning window; no weekly clustering or consecutive-meeting objective is implemented.",
            "Independent arithmetic certificates establish feasibility; optimality additionally relies on the CP-SAT reference compiler.",
            "Only canonical prose is in the default 96-attempt campaign; reordered prose is available for inspection, not additional independent data.",
            "Preparation authorizes neither live inference nor publication; previous runs and results remain separate and unchanged.",
        ],
    }
    validate_manifest(cases, proofs, manifest)
    review = {
        "format_version": "1.0", "dataset_version": VERSION, "case_bundle_sha256": digest(bundle),
        "warning": "Evaluator-only gold and labels: never include this file in measured model prompts.",
        "human_review_status": "pending", "cases": [{
            "case_id": c.case_id, "group_id": c.group_id, "mechanism": c.sweep, "layout": c.level,
            "constraint_profile": profile(c.problem), "expected_label": c.expected_label,
            "problem": to_data(c.problem), "renderings": {r.variant_id: r.text for r in c.authored_renderings},
            "proof": proofs[c.case_id], "review_status": "pending", "reviewer": None,
            "review_notes": None,
        } for c in cases],
    }
    directory.mkdir(parents=True, exist_ok=False)
    write_new(directory / "cases.json", bundle)
    write_new(directory / "proofs.json", proofs)
    write_new(directory / "manifest.json", manifest)
    write_new(directory / "review.json", review)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--reference-seconds", type=float, default=60)
    args = parser.parse_args()
    result = prepare(args.directory, seed=args.seed, reference_seconds=args.reference_seconds)
    print({"status": result["status"], **result["counts"], "new_model_calls": 0})


if __name__ == "__main__":
    main()
