"""Build the versioned 200-attempt-per-model study, entirely offline.

Use a NEW dataset directory. Existing cases, results and packets are never replaced.
Run prepare_development_campaign.py --design difficulty-200 to create portable
fresh preflights on the execution machine after installing the pinned runtime.
"""

import argparse
from collections import Counter
import hashlib
from pathlib import Path

from scheduling.evaluation.benchmark import difficulty
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.difficulty_suite import (
    VERSION, TIERS, SIZES, build_suite, check_design, select_language,
)
from scheduling.evaluation import difficulty_suite
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.runner import write_new
from scheduling.evaluation.scoring import digest


def prepare(directory, *, seed=32661013):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError("Use a new dataset directory; previous evidence is immutable")
    controlled, realistic, proofs, rejected = build_suite(seed)
    check_design(controlled, realistic)
    audit = structural_audit(controlled + realistic)
    families = audit["family_for_group"]
    if {families[c.group_id] for c in controlled} & {families[c.group_id] for c in realistic}:
        raise ValueError("Controlled and fictional sets share a hard-structure family")
    if any(0 in difficulty(c.problem)["unary_start_counts"] for c in controlled + realistic):
        raise ValueError("This design requires every activity to fit individually, including UNSAT cases")
    language = select_language(controlled)
    manifest = {
        "format_version": "1.0", "dataset_version": VERSION, "seed": seed,
        "status": "offline_verified_development_pending_human_review",
        "generator_sha256": hashlib.sha256(Path(difficulty_suite.__file__).read_bytes()).hexdigest(),
        "case_bundle_sha256": {"controlled": digest(case_bundle(controlled)), "realistic": digest(case_bundle(realistic))},
        "tiers": dict(zip(TIERS, SIZES)),
        "counts": {"unique_cases": 80, "construction_families": 40,
                   "controlled_cases": 60, "fictional_cases": 20,
                   "wording_bases": 10, "additional_wording_conditions": 20,
                   "case_rendering_conditions": 100, "scheduling_attempts_per_model": 200,
                   "both_models_scheduling_attempts": 400},
        "models": ["qwen3.6:35b", "qwen3.8:27b"],
        "budget_per_model": {"controlled": 120, "realistic": 40, "language": 40,
                             "capability_completions": 2, "metadata_requests": 1,
                             "total_http_requests": 203, "max_output_tokens_per_completion": 32768,
                             "reserved_output_tokens": 202 * 32768, "input_tokens_additional": True},
        "language_case_ids": [c.case_id for c in language],
        "language_task_label_counts": dict(Counter(f"{c.problem.task_type}/{c.expected_label}" for c in language)),
        "structural_audit": audit, "construction_rejections": rejected,
        "proofs": proofs,
        "case_difficulty": {c.case_id: difficulty(c.problem) for c in controlled + realistic},
        "human_gold_review": "pending", "human_wording_review": "pending", "new_model_calls": 0,
        "limitations": [
            "Tier names are construction targets, not verified monotone difficulty for either model or solver.",
            "Both methods receive identical task facts; the controlled and wording blocks share selected cases.",
            "Fictional scenarios use deterministic AI-assisted templates; no real calendars or human-authored claim.",
            "Construction certificates prove SAT/UNSAT only; optimality additionally relies on the existing CP-SAT compiler.",
            "Input-token usage is unknown until returned; output reservations are not actual consumption or a currency cap.",
            "Preparation authorizes neither inference nor publication; previous 600-attempt results remain separate.",
        ],
    }
    directory.mkdir(parents=True, exist_ok=False)
    write_new(directory / "controlled.json", case_bundle(controlled))
    write_new(directory / "realistic.json", case_bundle(realistic))
    write_new(directory / "manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--seed", type=int, default=32661013)
    args = parser.parse_args()
    result = prepare(args.directory, seed=args.seed)
    print({"status": result["status"], **result["counts"], "new_model_calls": 0})


if __name__ == "__main__":
    main()
