"""Prepare a versioned development campaign without model calls.

The legacy and difficulty designs retain their three separate blocks. The
balanced design has 48 generation cases; the diverse design has 1,000 distinct
generation cases. Both have one controlled block. None are held-out data.
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
    DEVELOPMENT_QUALIFICATION_POLICIES, OBSERVE_BACKEND_POLICY, STRICT_QUALIFICATION_POLICY, RunConfig, plan_run, write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.difficulty_suite import (
    CAMPAIGN_POLICY, CALLS, check_design, select_language as select_difficulty_language,
)
from scheduling.evaluation import balanced_generation, diverse_generation
from scheduling.evaluation.runner import read
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
            qualification_policy=STRICT_QUALIFICATION_POLICY, design="legacy-600"):
    if not isinstance(model, str) or not model or model == "default" or any(c.isspace() for c in model):
        raise ValueError("Select an explicit provider model ID, not the default alias")
    if qualification_policy not in DEVELOPMENT_QUALIFICATION_POLICIES:
        raise ValueError("Select a supported development qualification policy")
    if design == "diverse-generation-2000":
        return prepare_diverse(controlled_path, directory, model=model,
                               qualification_policy=qualification_policy)
    if design == "balanced-generation-96":
        return prepare_balanced(controlled_path, directory, model=model,
                                qualification_policy=qualification_policy)
    controlled, realistic = load_cases(controlled_path), load_cases(realistic_path)
    if design not in ("legacy-600", "difficulty-200"):
        raise ValueError("Unsupported campaign design")
    compact = design == "difficulty-200"
    controlled_count, realistic_count = (60, 20) if compact else (240, 12)
    if (
        len(controlled) != controlled_count or len(realistic) != realistic_count
        or any(c.split != "development" or c.kind != "controlled" for c in controlled)
        or any(c.split != "development" or c.kind != "realistic"
               or not isinstance(c, AuthoredBenchmarkCase) for c in realistic)
    ):
        raise ValueError("Campaign case counts/types do not match its declared design")
    if compact:
        check_design(controlled, realistic)
    expected = {(task, label): controlled_count // 4 for task in ("generation", "repair") for label in ("SAT", "UNSAT")}
    if Counter((c.problem.task_type, c.expected_label) for c in controlled) != expected:
        raise ValueError("Controlled task/label strata must be balanced")
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
    blocks = {"controlled": controlled, "realistic": realistic,
              "language": select_difficulty_language(controlled) if compact else select_language(controlled)}
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
        "format_version": "1.0", "policy_version": CAMPAIGN_POLICY if compact else "development-campaign-2",
        "status": "prepared_offline_not_live_authorization", "evidence": "development_only",
        "model": model, "inputs": inputs, "family_mapping": families,
        "preparation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "configs": configs, "blocks": details,
        "qualification_policy": qualification_policy,
        "language_selection": ("Two controlled bases per tier with balanced task/SAT margins; both clock-time paraphrase and reordered facts; no model outcomes"
                               if compact else "Six per task/label, distinct source families; least-used sweep then event within stratum, stable case-ID tie-break; no model outcomes"),
        "authored_creation_methods": dict(Counter(
            r.creation_method for c in realistic for r in c.authored_renderings if r.variant_id == "canonical"
        )),
        "planned_scheduling_completions": sum(d["planned_requests"] for d in details.values()), "capability_completions": 2,
        "metadata_requests": 1, "total_requests": sum(d["planned_requests"] for d in details.values()) + 3,
        "requested_output_tokens": (sum(d["planned_requests"] for d in details.values()) + 2) * 32768,
        "limitations": [
            "All inspected/generated cases remain development data, not a final held-out study.",
            "Realistic drafts retain their AI-assisted provenance and actual pending reviews.",
            "Requested output reservation excludes additional input tokens and does not enforce a currency cap.",
        ],
    }
    if compact and {role: d["planned_requests"] for role, d in details.items()} != CALLS:
        raise ValueError("Difficulty campaign must contain exactly 200 scheduling attempts")
    write_new(directory / "campaign.json", manifest)
    return manifest


def prepare_balanced(cases_path, directory, *, model, qualification_policy):
    """Qualify a new generation-only dataset; never reinterpret an old study."""
    if model not in balanced_generation.MODELS:
        raise ValueError("Balanced campaign supports explicit Qwen3.6 and GLM identities")
    cases_path = Path(cases_path)
    cases = load_cases(cases_path)
    source = read(cases_path.parent / "manifest.json")
    proofs = read(cases_path.parent / "proofs.json")
    balanced_generation.validate_manifest(cases, proofs, source)
    families = structural_audit(cases)["family_for_group"]
    normalized = tuple(replace(c, group_id=families[c.group_id]) for c in cases)
    balanced_generation.verify_suite(normalized, proofs)
    count = balanced_generation.CALLS["controlled"]
    cfg = RunConfig(
        ModelConfig(model, 32768, connect_timeout=30, read_timeout=1800),
        SolverLimits(30), SolverLimits(60), count, count * 32768,
        evidence="live_development", variants=("canonical",),
        qualification_policy=qualification_policy,
        provider_failure_policy=CONTINUE_TRANSIENT_POLICY,
    )
    preflight = plan_run(normalized, cfg)
    if preflight["state"] != "ready" or not preflight["within_cap"] or preflight["planned_requests"] != count:
        raise ValueError("Balanced campaign reference preflight failed")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in (("dataset-cases.json", case_bundle(cases)),
                        ("dataset-proofs.json", proofs), ("dataset-manifest.json", source),
                        ("controlled-cases.json", case_bundle(normalized)),
                        ("controlled-config.json", cfg), ("controlled-preflight.json", preflight)):
        write_new(directory / name, value)
    manifest = {
        "format_version": "1.0", "policy_version": balanced_generation.CAMPAIGN_POLICY,
        "status": "prepared_offline_not_live_authorization", "evidence": "development_only",
        "model": model, "qualification_policy": qualification_policy,
        "dataset_manifest_sha256": digest(source), "family_mapping": families,
        "preparation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "configs": {"controlled": to_data(cfg)},
        "blocks": {"controlled": {
            "case_count": len(normalized), "case_bundle_sha256": digest(case_bundle(normalized)),
            "case_ids": [c.case_id for c in normalized],
            "source_families": len({c.group_id for c in normalized}),
            "task_label_counts": dict(Counter(f"generation/{c.expected_label}" for c in normalized)),
            "planned_requests": count, "variants": ["canonical"],
        }},
        "planned_scheduling_completions": count, "capability_completions": 2,
        "metadata_requests": 1, "total_requests": count + 3,
        "requested_output_tokens": (count + 2) * 32768,
        "limitations": ["AI-assisted constructed development data; human wording review pending.",
                        "Related variants are grouped; this is not 48 independent source families.",
                        "Output reservation excludes input tokens and is not a currency cap.",
                        "No new model results or live authorization are supplied by preparation."],
    }
    write_new(directory / "campaign.json", manifest)
    return manifest


def prepare_diverse(cases_path, directory, *, model, qualification_policy):
    """Prepare 2,000 canonical attempts without adding optional wording requests."""
    if model not in diverse_generation.MODELS:
        raise ValueError("Diverse campaign supports explicit Qwen3.6 and GLM identities")
    if qualification_policy != OBSERVE_BACKEND_POLICY:
        raise ValueError("Diverse campaign requires the declared model-strict backend-observation policy")
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(directory)
    cases_path = Path(cases_path)
    cases = load_cases(cases_path)
    source = read(cases_path.parent / "manifest.json")
    proofs = read(cases_path.parent / "proofs.json")
    # Manifest validation independently recomputes certificates and structure.
    diverse_generation.validate_manifest(cases, proofs, source)
    families = source["structural_audit"]["family_for_group"]
    normalized = tuple(replace(c, group_id=families[c.group_id]) for c in cases)
    count = diverse_generation.CALLS["controlled"]
    cfg = RunConfig(
        ModelConfig(model, 32768, connect_timeout=30, read_timeout=1800),
        SolverLimits(30), SolverLimits(60), count, count * 32768,
        evidence="live_development", variants=("canonical",),
        qualification_policy=qualification_policy,
        provider_failure_policy=CONTINUE_TRANSIENT_POLICY,
    )
    preflight = plan_run(normalized, cfg)
    if (preflight["state"] != "ready" or not preflight["within_cap"]
            or preflight["planned_requests"] != count):
        raise ValueError("Diverse campaign reference preflight failed")
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in (("dataset-cases.json", case_bundle(cases)),
                        ("dataset-proofs.json", proofs), ("dataset-manifest.json", source),
                        ("controlled-cases.json", case_bundle(normalized)),
                        ("controlled-config.json", cfg), ("controlled-preflight.json", preflight)):
        write_new(directory / name, value)
    manifest = {
        "format_version": "1.0", "policy_version": diverse_generation.CAMPAIGN_POLICY,
        "status": "prepared_offline_not_live_authorization", "evidence": "development_only",
        "model": model, "qualification_policy": qualification_policy,
        "dataset_manifest_sha256": digest(source), "family_mapping": families,
        "preparation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "execution_source_sha256": hashlib.sha256(
            Path(__file__).with_name("run_development_campaign.py").read_bytes()).hexdigest(),
        "configs": {"controlled": to_data(cfg)},
        "blocks": {"controlled": {
            "case_count": len(normalized), "case_bundle_sha256": digest(case_bundle(normalized)),
            "case_ids": [c.case_id for c in normalized],
            "source_families": len({c.group_id for c in normalized}),
            "task_label_counts": dict(Counter(f"generation/{c.expected_label}" for c in normalized)),
            "planned_requests": count, "variants": ["canonical"],
        }},
        "planned_scheduling_completions": count, "capability_completions": 2,
        "metadata_requests": 1, "total_requests": count + 3,
        "requested_output_tokens": (count + 2) * 32768,
        "limitations": [
            "AI-assisted constructed development data; human wording review pending.",
            "Distinct hard structures are not independent real-world samples; preserve family grouping.",
            "Difficulty tiers are construction targets, not measured model difficulty.",
            "Optional wording variants are excluded from this canonical-only campaign.",
            "Output reservation excludes input tokens and is not a currency cap.",
            "Preparation does not authorize live inference or supply model results.",
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
    parser.add_argument("--design", choices=("legacy-600", "difficulty-200", "balanced-generation-96", "diverse-generation-2000"), default="legacy-600")
    parser.add_argument("--qualification-policy", choices=DEVELOPMENT_QUALIFICATION_POLICIES,
                        default=STRICT_QUALIFICATION_POLICY,
                        help="Backend observation requires separate explicit development authorization")
    args = parser.parse_args()
    result = prepare(args.controlled, args.realistic, args.directory, model=args.model,
                     qualification_policy=args.qualification_policy, design=args.design)
    print({k: result[k] for k in ("status", "planned_scheduling_completions", "total_requests", "requested_output_tokens")})


if __name__ == "__main__":
    main()
