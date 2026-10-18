"""Execute one explicitly authorized, versioned SoCLaaS development campaign."""

import argparse
from collections import Counter
from dataclasses import replace
import json
import hashlib
from pathlib import Path

from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.qualification import execute_blocks
from scheduling.evaluation.runner import (
    DEVELOPMENT_QUALIFICATION_POLICIES, OBSERVE_BACKEND_POLICY, STRICT_QUALIFICATION_POLICY, plan_run, read,
)
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.difficulty_suite import CAMPAIGN_POLICY, CALLS, check_design, select_language
from scheduling.evaluation import balanced_generation, diverse_generation
from scheduling.providers import ModelConfig
from scheduling.schema import to_data
from scheduling.solver import SolverLimits

ROLES = ("controlled", "realistic", "language")
EXPECTED_CALLS = {"controlled": 480, "realistic": 24, "language": 96}


def load_packet(packet):
    packet = Path(packet)
    manifest = read(packet / "campaign.json")
    if manifest.get("policy_version") == diverse_generation.CAMPAIGN_POLICY:
        return _load_diverse_packet(packet, manifest)
    model = manifest.get("model")
    compact = manifest.get("policy_version") == CAMPAIGN_POLICY
    balanced = manifest.get("policy_version") == balanced_generation.CAMPAIGN_POLICY
    expected_calls = balanced_generation.CALLS if balanced else CALLS if compact else EXPECTED_CALLS
    roles = tuple(expected_calls)
    if (manifest.get("policy_version") not in ("development-campaign-2", CAMPAIGN_POLICY, balanced_generation.CAMPAIGN_POLICY)
            or manifest.get("evidence") != "development_only"
            or not isinstance(model, str) or not model or model == "default"
            or any(c.isspace() for c in model)):
        raise ValueError("Unsupported development campaign packet")
    if set(manifest.get("blocks", {})) != set(roles) or set(manifest.get("configs", {})) != set(roles):
        raise ValueError("Campaign block roles changed")
    expected_model = ModelConfig(model, 32768, connect_timeout=30, read_timeout=1800)
    policy = manifest.get("qualification_policy", STRICT_QUALIFICATION_POLICY)
    if policy not in DEVELOPMENT_QUALIFICATION_POLICIES:
        raise ValueError("Unsupported development qualification policy")
    blocks = {}
    for role in roles:
        cases = load_cases(packet / f"{role}-cases.json")
        cfg = load_config(packet / f"{role}-config.json")
        variants = ("paraphrase", "reordered") if role == "language" else ("canonical",)
        if (
            digest(case_bundle(cases)) != manifest["blocks"][role]["case_bundle_sha256"]
            or to_data(cfg) != manifest["configs"][role]
            or cfg.evidence != "live_development"
            or cfg.qualification_policy != policy
            or cfg.provider_failure_policy != CONTINUE_TRANSIENT_POLICY
            or cfg.qualification_baseline is not None
            or cfg.model != expected_model
            or cfg.solver != SolverLimits(30) or cfg.reference_solver != SolverLimits(60)
            or cfg.rendering_seed != 3263
            or cfg.max_requests != expected_calls[role]
            or cfg.max_requested_output_tokens != expected_calls[role] * 32768
            or cfg.variants != variants or cfg.repeats != 1
            or any(c.split != "development" or c.kind != ("realistic" if role == "realistic" else "controlled") for c in cases)
        ):
            raise ValueError("Campaign input/configuration changed")
        current = plan_run(cases, cfg)
        prepared = read(packet / f"{role}-preflight.json")
        if (current["contract"] != prepared.get("contract") or current["state"] != "ready"
                or not current["within_cap"] or current["planned_requests"] != expected_calls[role]):
            raise ValueError("Campaign preflight changed; prepare a new packet")
        blocks[role] = (cases, cfg, current)
    if balanced:
        source = read(packet / "dataset-manifest.json")
        original = load_cases(packet / "dataset-cases.json")
        proofs = read(packet / "dataset-proofs.json")
        balanced_generation.validate_manifest(original, proofs, source)
        families = structural_audit(original)["family_for_group"]
        normalized = tuple(replace(c, group_id=families[c.group_id]) for c in original)
        expected_details = {
            "case_count": len(normalized), "case_bundle_sha256": digest(case_bundle(normalized)),
            "case_ids": [c.case_id for c in normalized],
            "source_families": len({c.group_id for c in normalized}),
            "task_label_counts": dict(Counter(f"generation/{c.expected_label}" for c in normalized)),
            "planned_requests": 96, "variants": ["canonical"],
        }
        if (model not in balanced_generation.MODELS
                or digest(source) != manifest.get("dataset_manifest_sha256")
                or manifest.get("family_mapping") != families
                or manifest["blocks"]["controlled"] != expected_details
                or blocks["controlled"][0] != normalized
                or manifest.get("planned_scheduling_completions") != 96
                or manifest.get("total_requests") != 99
                or manifest.get("capability_completions") != 2
                or manifest.get("metadata_requests") != 1
                or manifest.get("requested_output_tokens") != 98 * 32768):
            raise ValueError("Balanced campaign dataset/proofs/budget changed")
        balanced_generation.verify_suite(normalized, proofs)
        return blocks, manifest
    controlled = {c.case_id: c for c in blocks["controlled"][0]}
    if any(c.case_id not in controlled or digest(c) != digest(controlled[c.case_id]) for c in blocks["language"][0]):
        raise ValueError("Language block must retain exact controlled partners")
    if compact:
        check_design(blocks["controlled"][0], blocks["realistic"][0])
        if blocks["language"][0] != select_language(blocks["controlled"][0]):
            raise ValueError("Difficulty language selection changed")
        if (manifest.get("planned_scheduling_completions") != 200
                or manifest.get("total_requests") != 203
                or manifest.get("capability_completions") != 2
                or manifest.get("metadata_requests") != 1
                or manifest.get("requested_output_tokens") != 202 * 32768):
            raise ValueError("Difficulty campaign budget metadata changed")
    families = structural_audit(blocks["controlled"][0] + blocks["realistic"][0])["family_for_group"]
    if any(group != family for group, family in families.items()):
        raise ValueError("Campaign source families must be normalized together")
    if {c.group_id for c in blocks["controlled"][0]} & {c.group_id for c in blocks["realistic"][0]}:
        raise ValueError("Controlled and realistic blocks share source families")
    return blocks, manifest


def _load_diverse_packet(packet, manifest):
    """Revalidate the large design before creating a provider or reserving calls."""
    model = manifest.get("model")
    count = diverse_generation.CALLS["controlled"]
    if (manifest.get("format_version") != "1.0"
            or manifest.get("status") != "prepared_offline_not_live_authorization"
            or manifest.get("evidence") != "development_only"
            or model not in diverse_generation.MODELS
            or manifest.get("qualification_policy") != OBSERVE_BACKEND_POLICY
            or set(manifest.get("blocks", {})) != {"controlled"}
            or set(manifest.get("configs", {})) != {"controlled"}
            or manifest.get("planned_scheduling_completions") != count
            or manifest.get("total_requests") != count + 3
            or manifest.get("capability_completions") != 2
            or manifest.get("metadata_requests") != 1
            or manifest.get("requested_output_tokens") != (count + 2) * 32768):
        raise ValueError("Diverse campaign identity, policy, roles or budget changed")
    for field, path in (
        ("preparation_source_sha256", Path(__file__).with_name("prepare_development_campaign.py")),
        ("execution_source_sha256", Path(__file__)),
    ):
        if manifest.get(field) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("Diverse campaign orchestration source changed; prepare a new packet")
    source = read(packet / "dataset-manifest.json")
    original = load_cases(packet / "dataset-cases.json")
    proofs = read(packet / "dataset-proofs.json")
    diverse_generation.validate_manifest(original, proofs, source)
    families = source["structural_audit"]["family_for_group"]
    normalized = tuple(replace(c, group_id=families[c.group_id]) for c in original)
    expected_details = {
        "case_count": len(normalized), "case_bundle_sha256": digest(case_bundle(normalized)),
        "case_ids": [c.case_id for c in normalized],
        "source_families": len({c.group_id for c in normalized}),
        "task_label_counts": dict(Counter(f"generation/{c.expected_label}" for c in normalized)),
        "planned_requests": count, "variants": ["canonical"],
    }
    cases = load_cases(packet / "controlled-cases.json")
    cfg = load_config(packet / "controlled-config.json")
    if (digest(source) != manifest.get("dataset_manifest_sha256")
            or manifest.get("family_mapping") != families
            or manifest["blocks"]["controlled"] != expected_details
            or cases != normalized
            or to_data(cfg) != manifest["configs"]["controlled"]
            or cfg.evidence != "live_development"
            or cfg.qualification_policy != OBSERVE_BACKEND_POLICY
            or cfg.provider_failure_policy != CONTINUE_TRANSIENT_POLICY
            or cfg.qualification_baseline is not None
            or cfg.model != ModelConfig(model, 32768, connect_timeout=30, read_timeout=1800)
            or cfg.solver != SolverLimits(30) or cfg.reference_solver != SolverLimits(60)
            or cfg.rendering_seed != 3263
            or cfg.max_requests != count or cfg.max_requested_output_tokens != count * 32768
            or cfg.variants != ("canonical",) or cfg.repeats != 1
            or any(c.split != "development" or c.kind != "controlled"
                   or c.problem.task_type != "generation" for c in cases)):
        raise ValueError("Diverse campaign dataset/proofs/configuration changed")
    current = plan_run(cases, cfg)
    prepared = read(packet / "controlled-preflight.json")
    if (current["contract"] != prepared.get("contract") or current["state"] != "ready"
            or not current["within_cap"] or current["planned_requests"] != count):
        raise ValueError("Diverse campaign preflight changed; prepare a new packet")
    return {"controlled": (cases, cfg, current)}, manifest


def run_campaign(packet, directory, *, allow_live=False, authorization_reference=None, provider_factory=None):
    if not allow_live or not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError("Explicit live selection and a new authorization reference are required")
    blocks, manifest = load_packet(packet)
    return execute_blocks(
        blocks, directory, allow_live=allow_live, authorization_reference=authorization_reference,
        provider_factory=provider_factory, packet_metadata={"campaign_sha256": digest(manifest)},
        script_path=__file__, stop_state="stopped_campaign",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--authorization-reference", required=True)
    args = parser.parse_args(argv)
    result = run_campaign(args.packet, args.directory, allow_live=args.allow_live,
                          authorization_reference=args.authorization_reference)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
