"""Prepare Section 9's fixed development packet without provider access.

Input is the preserved/regenerated expanded 100-case bundle. This only selects
known development cases; it does not construct held-out data or authorize calls.
"""

import argparse
from collections import Counter
import hashlib
from pathlib import Path

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.runner import RunConfig, plan_run, read, write_new
from scheduling.evaluation.scoring import digest
from scheduling.pipelines.direct import build_messages
from scheduling.pipelines.solver_augmented import build_extraction_messages
from scheduling.providers import ModelConfig
from scheduling.schema import to_data
from scheduling.solver import SolverLimits


FAILURES = (
    "dev-v2-3264-slack-0-fixed_start-unsat-0-repair",
    "dev-v2-3264-interaction_density-2-fixed_start-unsat-0-generation",
    "dev-v3-1cb82271f05a61f8e4b44569-generation",
)
MODELS = ("qwen3.6:35b", "qwen3.8:27b")


def request_characters(case):
    view = render(case, "canonical", 3263)
    direct = build_messages(
        view.text, task_type=view.task_type, required_activity_ids=view.activity_ids,
        original_schedule=view.original_schedule.to_list() if view.original_schedule else None,
    )
    extraction = build_extraction_messages(view)
    return sum(len(message.content) for message in (*direct, *extraction))


def select_cases(cases):
    """Six per task/label; failures, longest and coupled cases, then diversity.

    Selection uses only input structure and the three predeclared failure IDs.
    It never reads model outputs or ranks candidates by an observed A/B gap.
    """
    cases = tuple(cases)
    by_id = {c.case_id: c for c in cases}
    if len(by_id) != len(cases) or any(c.split != "development" for c in cases):
        raise ValueError("Unique development cases required")
    if not set(FAILURES) <= set(by_id):
        raise ValueError("Qualification must retain all three declared failures")
    sizes = {c.case_id: request_characters(c) for c in cases}
    chosen, reasons = [], {}

    def take(case, reason):
        if case.case_id not in reasons:
            chosen.append(case)
            reasons[case.case_id] = reason

    for task in ("generation", "repair"):
        for label in ("SAT", "UNSAT"):
            pool = [c for c in cases if (c.problem.task_type, c.expected_label) == (task, label)]
            if len(pool) < 6:
                raise ValueError("Insufficient cases for six per task/label stratum")
            for case in sorted(pool, key=lambda c: c.case_id):
                if case.case_id in FAILURES:
                    take(case, "predeclared_expanded_failure")
            take(min(pool, key=lambda c: (-sizes[c.case_id], c.case_id)), "longest_combined_public_request_in_stratum")
            coupled = [c for c in pool if c.sweep == "resource_chain" and c.level == "5"]
            if not coupled:
                raise ValueError("Missing five-activity coupled resource-chain coverage")
            take(min(coupled, key=lambda c: c.case_id), "five_activity_resource_chain")
            while True:
                local = [c for c in chosen if (c.problem.task_type, c.expected_label) == (task, label)]
                if len(local) == 6:
                    break
                families = {c.group_id for c in chosen}
                sweeps = {c.sweep for c in local}
                events = {c.event for c in local if c.context}
                remaining = [c for c in pool if c.case_id not in reasons]
                case = min(remaining, key=lambda c: (
                    c.group_id in families, c.sweep in sweeps,
                    bool(c.context and c.event in events), -sizes[c.case_id], c.case_id,
                ))
                take(case, "family_sweep_event_diversity_then_request_length")
    return tuple(chosen), reasons, sizes


def prepare(cases_path, manifest_path, directory):
    cases = load_cases(cases_path)
    source = read(manifest_path)
    if len(cases) != 100 or digest(case_bundle(cases)) != source.get("case_bundle_sha256"):
        raise ValueError("Input must match the preserved expanded 100-case manifest")
    selected, reasons, sizes = select_cases(cases)
    directory.mkdir(parents=True, exist_ok=False)
    write_new(directory / "cases.json", case_bundle(selected))
    configs = {}
    for model in MODELS:
        name = model.replace(":", "-")
        cfg = RunConfig(
            ModelConfig(model, 32768, connect_timeout=30, read_timeout=900),
            SolverLimits(30), SolverLimits(60), 48, 48 * 32768,
            evidence="live_development",
        )
        configs[name] = to_data(cfg)
        write_new(directory / (name + ".json"), cfg)
        preflight = plan_run(selected, cfg)
        write_new(directory / (name + ".preflight.json"), preflight)
        if preflight["state"] != "ready" or not preflight["within_cap"]:
            raise ValueError("Qualification preflight failed; no inference authorized")
    manifest = {
        "format_version": "1.0", "policy_version": "f2-development-selection-1",
        "status": "prepared_offline_not_live_authorization",
        "source_bundle_sha256": digest(case_bundle(cases)),
        "case_bundle_sha256": digest(case_bundle(selected)),
        "preparation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "counts": dict(Counter(f"{c.problem.task_type}/{c.expected_label}" for c in selected)),
        "source_families": len({c.group_id for c in selected}),
        "case_ids": [c.case_id for c in selected], "selection_reasons": reasons,
        "combined_public_request_characters": {c.case_id: sizes[c.case_id] for c in selected},
        "case_groups": {c.case_id: c.group_id for c in selected},
        "planned_case_completions": 96, "proposed_capability_completions": 4,
        "proposed_metadata_requests": 1, "proposed_total_output_reservation": 3276800,
        "configs": configs,
        "limitations": [
            "Known development inputs selected partly to retain observed failures; not held-out.",
            "Families remain related; 24 cases are not 24 independent families.",
            "No new model decision, course eligibility, live budget or human review is implied.",
            "Sampling/reasoning controls are omitted server defaults, not deterministic settings.",
            "Capability checks must precede case calls; unsupported settings need a new decision.",
        ],
    }
    write_new(directory / "selection.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("benchmarks/manifests/expanded-development-100-20260930.json"))
    args = parser.parse_args()
    result = prepare(args.cases, args.manifest, args.output)
    print({key: result[key] for key in ("status", "counts", "source_families", "planned_case_completions")})
