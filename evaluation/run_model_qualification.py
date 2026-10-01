"""One authorized selected-model qualification through the existing provider/runner.

One model-list request, two tiny JSON capability checks at the actual configured
output ceiling, then 48 scheduling calls. Existing output directories are never
reused; reconcile interrupted reservations without automatically reissuing them.
"""

import argparse
import json
from pathlib import Path

from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.runner import STRICT_QUALIFICATION_POLICY, plan_run, read
from scheduling.evaluation.qualification import execute_blocks
from scheduling.evaluation.scoring import digest
from scheduling.schema import to_data

MODELS = ("qwen3.6:35b", "qwen3.8:27b")

def load_packet(packet, model):
    """Reject edited inputs/settings or stale preparation before provider access."""
    packet = Path(packet)
    selection = read(packet / "selection.json")
    if model not in MODELS or model not in selection.get("selected_models", []):
        raise ValueError("Model is not selected in this qualification packet")
    name = model.replace(":", "-")
    cases = load_cases(packet / "cases.json")
    cfg = load_config(packet / (name + ".json"))
    if (
        len(cases) != 24
        or any(c.split != "development" for c in cases)
        or digest(case_bundle(cases)) != selection.get("case_bundle_sha256")
        or to_data(cfg) != selection.get("configs", {}).get(name)
        or cfg.model.model != model
        or cfg.model.max_tokens != 32768
        or cfg.model.connect_timeout != 30
        or cfg.model.read_timeout != 900
        or cfg.evidence != "live_development"
        or cfg.qualification_policy != STRICT_QUALIFICATION_POLICY
        or cfg.qualification_baseline is not None
        or cfg.max_requests != 48
        or cfg.max_requested_output_tokens != 48 * 32768
    ):
        raise ValueError("Qualification packet/configuration changed or unsupported")
    prepared = read(packet / (name + ".preflight.json"))
    current = plan_run(cases, cfg)
    if (
        current["contract"] != prepared.get("contract")
        or current["state"] != "ready"
        or not current["within_cap"]
        or current["planned_requests"] != 48
    ):
        raise ValueError("Qualification preflight changed; prepare a new packet")
    return cases, cfg, selection, current


def qualify(packet, directory, *, model="qwen3.8:27b", allow_live=False,
            authorization_reference=None, provider_factory=None):
    if not allow_live or not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError("Explicit live selection and a new authorization reference are required")
    cases, cfg, selection, preflight = load_packet(packet, model)
    return execute_blocks(
        {"batch": (cases, cfg, preflight)}, directory,
        authorization_reference=authorization_reference, allow_live=allow_live,
        provider_factory=provider_factory, packet_metadata={"selection_sha256": digest(selection)},
        script_path=__file__,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--model", choices=MODELS, default="qwen3.8:27b")
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--authorization-reference", required=True)
    args = parser.parse_args(argv)
    result = qualify(args.packet, args.directory, model=args.model,
                     allow_live=args.allow_live, authorization_reference=args.authorization_reference)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
