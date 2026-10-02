"""Prepare the authorized 600-attempt development design without model calls.

Controlled 240 cases, 12 AI-assisted realistic drafts and 24 controlled bases
with two additional wordings remain separate blocks. None are held-out data.
"""

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
from pathlib import Path

from scheduling.evaluation.cases import AuthoredBenchmarkCase, case_bundle, load_cases
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.runner import (
    DEVELOPMENT_QUALIFICATION_POLICIES, STRICT_QUALIFICATION_POLICY, RunConfig, plan_run, write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.schema import to_data
from scheduling.solver import SolverLimits


def select_language(cases):
    """Six per task/label, distinct families, then balance sweep/event counts."""
    chosen, used = [], set()
    for task in ("generation", "repair"):
        for label in ("SAT", "UNSAT"):
            sweep_counts, event_counts = Counter(), Counter()
            for _ in range(6):
                candidates = [c for c in cases if c.problem.task_type == task
                              and c.expected_label == label and c.group_id not in used]
                if not candidates:
                    raise ValueError("Language policy cannot fill 24 distinct families; review before changing it")
                case = min(candidates, key=lambda c: (
                    sweep_counts[c.sweep], event_counts[c.event], c.case_id,
                ))
                chosen.append(case)
                used.add(case.group_id)
                sweep_counts[case.sweep] += 1
                event_counts[case.event] += 1
    return tuple(chosen)


def prepare(controlled_path, realistic_path, directory, *, model="qwen3.8:27b",
            qualification_policy=STRICT_QUALIFICATION_POLICY):
    if not isinstance(model, str) or not model or model == "default" or any(c.isspace() for c in model):
        raise ValueError("Select an explicit provider model ID, not the default alias")
    if qualification_policy not in DEVELOPMENT_QUALIFICATION_POLICIES:
        raise ValueError("Select a supported development qualification policy")
    controlled, realistic = load_cases(controlled_path), load_cases(realistic_path)
    if (
        len(controlled) != 240 or len(realistic) != 12
        or any(c.split != "development" or c.kind != "controlled" for c in controlled)
        or any(c.split != "development" or c.kind != "realistic"
               or not isinstance(c, AuthoredBenchmarkCase) for c in realistic)
    ):
        raise ValueError("Campaign requires 240 controlled and 12 authored development cases")
    expected = {(task, label): 60 for task in ("generation", "repair") for label in ("SAT", "UNSAT")}
    if Counter((c.problem.task_type, c.expected_label) for c in controlled) != expected:
        raise ValueError("Controlled task/label strata must each contain 60 cases")
    audit = structural_audit(controlled + realistic)
    families = audit["family_for_group"]
    if {families[c.group_id] for c in controlled} & {families[c.group_id] for c in realistic}:
        raise ValueError("Controlled and realistic blocks share a hard-structure family")
    inputs = {
        "controlled": {"reference": str(controlled_path), "sha256": digest(case_bundle(controlled))},
        "realistic": {"reference": str(realistic_path), "sha256": digest(case_bundle(realistic))},
    }
    controlled = tuple(replace(c, group_id=families[c.group_id]) for c in controlled)
    realistic = tuple(replace(c, group_id=families[c.group_id]) for c in realistic)
    blocks = {"controlled": controlled, "realistic": realistic, "language": select_language(controlled)}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    configs, details = {}, {}
    for role, cases in blocks.items():
        variants = ("paraphrase", "reordered") if role == "language" else ("canonical",)
        count = 2 * len(cases) * len(variants)
        cfg = RunConfig(
            ModelConfig(model, 32768, connect_timeout=30, read_timeout=1800),
            SolverLimits(30), SolverLimits(60), count, count * 32768,
            evidence="live_development", variants=variants,
            qualification_policy=qualification_policy,
            provider_failure_policy=CONTINUE_TRANSIENT_POLICY,
        )
        preflight = plan_run(cases, cfg)
        if preflight["state"] != "ready" or not preflight["within_cap"]:
            raise ValueError("Campaign reference preflight failed; no inference authorized")
        write_new(directory / f"{role}-cases.json", case_bundle(cases))
        write_new(directory / f"{role}-config.json", cfg)
        write_new(directory / f"{role}-preflight.json", preflight)
        configs[role] = to_data(cfg)
        details[role] = {
            "case_count": len(cases), "case_bundle_sha256": digest(case_bundle(cases)),
            "case_ids": [c.case_id for c in cases], "source_families": len({c.group_id for c in cases}),
            "task_label_counts": dict(Counter(f"{c.problem.task_type}/{c.expected_label}" for c in cases)),
            "planned_requests": count, "variants": list(variants),
        }
    manifest = {
        "format_version": "1.0", "policy_version": "development-campaign-2",
        "status": "prepared_offline_not_live_authorization", "evidence": "development_only",
        "model": model, "inputs": inputs, "family_mapping": families,
        "preparation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "configs": configs, "blocks": details,
        "qualification_policy": qualification_policy,
        "language_selection": "Six per task/label, distinct source families; least-used sweep then event within stratum, stable case-ID tie-break; no model outcomes",
        "authored_creation_methods": dict(Counter(
            r.creation_method for c in realistic for r in c.authored_renderings if r.variant_id == "canonical"
        )),
        "planned_scheduling_completions": 600, "capability_completions": 2,
        "metadata_requests": 1, "total_requests": 603,
        "requested_output_tokens": 602 * 32768,
        "limitations": [
            "All inspected/generated cases remain development data, not a final held-out study.",
            "Realistic drafts retain their AI-assisted provenance and actual pending reviews.",
            "Requested output reservation excludes additional input tokens and does not enforce a currency cap.",
        ],
    }
    write_new(directory / "campaign.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("controlled", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--realistic", type=Path, default=Path("benchmarks/fixtures/realistic-drafts-v1.json"))
    parser.add_argument("--model", default="qwen3.8:27b", help="Exact authorized SoCLaaS model ID; no fallback")
    parser.add_argument("--qualification-policy", choices=DEVELOPMENT_QUALIFICATION_POLICIES,
                        default=STRICT_QUALIFICATION_POLICY,
                        help="Backend observation requires separate explicit development authorization")
    args = parser.parse_args()
    result = prepare(args.controlled, args.realistic, args.directory, model=args.model,
                     qualification_policy=args.qualification_policy)
    print({k: result[k] for k in ("status", "planned_scheduling_completions", "total_requests", "requested_output_tokens")})


if __name__ == "__main__":
    main()
