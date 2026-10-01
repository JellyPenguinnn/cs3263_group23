"""Bounded development campaign orchestration around the shared provider/runner.

This adds capability checks and a shared session budget, not a second scheduling
pipeline. Each output directory is write-once; interrupted calls stay reserved.
"""

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import time

from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.metrics import token_usage_summary
from scheduling.evaluation.runner import STRICT_QUALIFICATION_POLICY, _stop_reason, read, run_batch, write_new
from scheduling.evaluation.scoring import digest
from scheduling.providers import Message, RequestBudget, SoCLaaSProvider
from scheduling.providers.execution import execution_contract
from scheduling.schema import SchemaError, load_json, to_data

MESSAGES = (
    Message("system", "Return only the requested JSON object."),
    Message("user", 'Return exactly {"ok":true} with no other text.'),
)


def capability_issue(response, cfg, fingerprints):
    reason = _stop_reason(response, cfg.model.model, fingerprints)
    if reason:
        return reason
    if response.error:
        return response.error
    if response.finish_reason != "stop" or len(response.attempts) != 1:
        return "invalid_capability_completion"
    execution = response.attempts[0].execution
    if not execution or execution.contract != execution_contract(cfg.model):
        return "execution_metadata_mismatch"
    try:
        answer = load_json(response.content)
    except SchemaError:
        return "invalid_capability_answer"
    if not isinstance(answer, dict) or set(answer) != {"ok"} or answer["ok"] is not True:
        return "invalid_capability_answer"
    return None



def execute_blocks(blocks, directory, *, authorization_reference, allow_live=False,
                   provider_factory=None, packet_metadata=None, script_path=None,
                   stop_state="stopped_qualification"):
    """Execute prepared (cases, config, preflight) blocks under one serial budget."""
    if not allow_live or not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError("Explicit live selection and a new authorization reference are required")
    started = time.monotonic()
    if not blocks or set(blocks) - {"batch", "controlled", "realistic", "language"}:
        raise ValueError("Unsupported development block roles")
    first = next(iter(blocks.values()))[1]
    model = first.model
    for cases, cfg, preflight in blocks.values():
        if (cfg.model != model or cfg.solver != first.solver
                or cfg.reference_solver != first.reference_solver
                or cfg.rendering_seed != first.rendering_seed
                or cfg.evidence != "live_development"
                or cfg.qualification_policy != STRICT_QUALIFICATION_POLICY
                or cfg.qualification_baseline is not None
                or preflight["state"] != "ready" or not preflight["within_cap"]
                or preflight["planned_requests"] != cfg.max_requests):
            raise ValueError("Development blocks must share strict qualified model settings and exact caps")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    scheduling_calls = sum(cfg.max_requests for _, cfg, _ in blocks.values())
    output_tokens = 2 * model.max_tokens + sum(cfg.max_requested_output_tokens for _, cfg, _ in blocks.values())
    budget = RequestBudget(3 + scheduling_calls, output_tokens)
    write_new(directory / "manifest.json", {
        "format_version": "1.0",
        "evidence": "live_development_not_final_eligibility_or_held_out_study",
        "authorization_reference": authorization_reference,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "packet": packet_metadata,
        "blocks": {role: {"case_bundle_sha256": digest(case_bundle(cases)),
                          "config": to_data(cfg), "preflight": preflight}
                   for role, (cases, cfg, preflight) in blocks.items()},
        "block_order": list(blocks),
        "script_sha256": hashlib.sha256(Path(script_path or __file__).read_bytes()).hexdigest(),
        "capability_messages": to_data(MESSAGES),
        "max_requests": budget.max_requests,
        "max_requested_output_tokens": budget.max_completion_tokens,
        "request_allocation": {"metadata": 1, "capability": 2, "scheduling": scheduling_calls},
        "input_tokens": "additional; not capped by output reservation",
        "resume": "Campaign directory cannot be reused; individual completed/stopped blocks retain runner resume guards",
    })
    write_new(directory / "blocks.json", {role: role for role in blocks})
    results = {}

    def finish(reason):
        attempts = [
            attempt
            for path in sorted(directory.glob("capability-[0-9][0-9].json"))
            for attempt in read(path)["response"]["attempts"]
        ]
        for role in blocks:
            for path in sorted((directory / role / "attempts").glob("*.json")):
                response = read(path)["payload"]["pipeline_result"].get("model_response") or {}
                attempts.extend(response.get("attempts", []))
        result = {
            "state": "completed" if reason is None else stop_state,
            "stop_reason": reason,
            "requests_reserved": budget.requests_used,
            "requested_output_tokens_reserved": budget.completion_tokens_reserved,
            "total_wall_seconds": time.monotonic() - started,
            "tokens": token_usage_summary(a["usage"] for a in attempts),
            "usage_scope": "Recorded capability and scheduling provider attempts; metadata request has no token usage record",
            "blocks": results,
        }
        if "batch" in blocks:
            result["batch"] = results.get("batch")
        write_new(directory / "summary.json", result)
        return result

    factory = provider_factory or SoCLaaSProvider.from_environment
    with factory(budget=budget) as provider:
        write_new(directory / "metadata-reservation.json", {"requests": 1, "output_tokens": 0})
        try:
            models = provider.list_models()
        except ValueError:
            write_new(directory / "metadata.json", {"error": "model_listing_failed"})
            return finish("model_listing_failed")
        available = model.model in models
        write_new(directory / "metadata.json", {
            "requested_model": model.model, "available": available,
            "catalogue_sha256": digest(models),
        })
        if not available:
            return finish("requested_model_unavailable")
        fingerprints, capability_hashes = set(), []
        capability_config = next(iter(blocks.values()))[1]
        for index in range(2):
            write_new(directory / f"capability-{index:02}-reservation.json", {
                "requests": 1, "output_tokens": model.max_tokens,
            })
            response = provider.complete(MESSAGES, model)
            issue = capability_issue(response, capability_config, fingerprints)
            record = {"index": index, "response": to_data(response), "issue": issue}
            write_new(directory / f"capability-{index:02}.json", record)
            capability_hashes.append(digest(record))
            if issue:
                return finish(issue)
        baseline = {"system_fingerprint": next(iter(fingerprints)),
                    "capability_sha256": capability_hashes}
        for role, (cases, cfg, _) in blocks.items():
            cfg = replace(cfg, qualification_baseline=baseline)
            config_name = "runtime-config.json" if role == "batch" else f"{role}-runtime-config.json"
            write_new(directory / config_name, cfg)
            result = run_batch(cases, directory / role, cfg, provider_complete=provider.complete)
            results[role] = result
            if result["state"] != "completed":
                return finish(result.get("stop_reason", result["state"]))
        return finish(None)
