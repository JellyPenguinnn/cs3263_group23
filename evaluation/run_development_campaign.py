"""Execute one explicitly authorized 600-attempt SoCLaaS development campaign."""

import argparse
import json
from pathlib import Path

from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.qualification import execute_blocks
from scheduling.evaluation.runner import STRICT_QUALIFICATION_POLICY, plan_run, read
from scheduling.evaluation.scoring import digest
from scheduling.schema import to_data
from scheduling.solver import SolverLimits

ROLES = ("controlled", "realistic", "language")
EXPECTED_CALLS = {"controlled": 480, "realistic": 24, "language": 96}


def load_packet(packet):
    packet = Path(packet)
    manifest = read(packet / "campaign.json")
    if (manifest.get("policy_version") != "development-campaign-1"
            or manifest.get("evidence") != "development_only"
            or manifest.get("model") != "qwen3.8:27b"):
        raise ValueError("Unsupported development campaign packet")
    blocks = {}
    for role in ROLES:
        cases = load_cases(packet / f"{role}-cases.json")
        cfg = load_config(packet / f"{role}-config.json")
        variants = ("paraphrase", "reordered") if role == "language" else ("canonical",)
        if (
            digest(case_bundle(cases)) != manifest["blocks"][role]["case_bundle_sha256"]
            or to_data(cfg) != manifest["configs"][role]
            or cfg.evidence != "live_development"
            or cfg.qualification_policy != STRICT_QUALIFICATION_POLICY
            or cfg.qualification_baseline is not None
            or cfg.model.model != "qwen3.8:27b" or cfg.model.max_tokens != 32768
            or cfg.model.connect_timeout != 30 or cfg.model.read_timeout != 900
            or cfg.solver != SolverLimits(30) or cfg.reference_solver != SolverLimits(60)
            or cfg.rendering_seed != 3263
            or cfg.max_requests != EXPECTED_CALLS[role]
            or cfg.max_requested_output_tokens != EXPECTED_CALLS[role] * 32768
            or cfg.variants != variants or cfg.repeats != 1
            or any(c.split != "development" or c.kind != ("realistic" if role == "realistic" else "controlled") for c in cases)
        ):
            raise ValueError("Campaign input/configuration changed")
        current = plan_run(cases, cfg)
        prepared = read(packet / f"{role}-preflight.json")
        if (current["contract"] != prepared.get("contract") or current["state"] != "ready"
                or not current["within_cap"] or current["planned_requests"] != EXPECTED_CALLS[role]):
            raise ValueError("Campaign preflight changed; prepare a new packet")
        blocks[role] = (cases, cfg, current)
    controlled = {c.case_id: c for c in blocks["controlled"][0]}
    if any(c.case_id not in controlled or digest(c) != digest(controlled[c.case_id]) for c in blocks["language"][0]):
        raise ValueError("Language block must retain exact controlled partners")
    families = structural_audit(blocks["controlled"][0] + blocks["realistic"][0])["family_for_group"]
    if any(group != family for group, family in families.items()):
        raise ValueError("Campaign source families must be normalized together")
    if {c.group_id for c in blocks["controlled"][0]} & {c.group_id for c in blocks["realistic"][0]}:
        raise ValueError("Controlled and realistic blocks share source families")
    return blocks, manifest


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
