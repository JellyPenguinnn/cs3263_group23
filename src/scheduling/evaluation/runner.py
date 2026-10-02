"""Serial development runs with durable reservations and immutable replay inputs."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
import json
import hashlib
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import case_bundle, check_case_set, load_cases
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY, FailureState
from scheduling.evaluation.liveness import RunLock
from scheduling.evaluation.scoring import digest, evaluate, reference, check_reference
from scheduling.pipelines.direct import build_messages, run_direct
from scheduling.pipelines.solver_augmented import (
    build_extraction_messages,
    run_solver_augmented,
)
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.providers.execution import execution_contract
from scheduling.schema import load_json, to_data
from scheduling.solver import SolverLimits
from scheduling.evaluation.frozen import (
    FROZEN_MODES,
    check_frozen,
    check_frozen_reference,
)

STRICT_QUALIFICATION_POLICY = "strict_model_backend_v1"
OBSERVE_BACKEND_POLICY = "strict_model_observe_backend_v1"
DEVELOPMENT_QUALIFICATION_POLICIES = (STRICT_QUALIFICATION_POLICY, OBSERVE_BACKEND_POLICY)


def baseline_fingerprints(config):
    """Restore actual capability observations without inventing a single backend."""
    baseline = config.qualification_baseline
    if baseline is None:
        return set()
    if config.qualification_policy == OBSERVE_BACKEND_POLICY:
        return set(baseline["system_fingerprints"])
    return {baseline["system_fingerprint"]}


@dataclass(frozen=True)
class RunConfig:
    model: ModelConfig
    solver: SolverLimits
    reference_solver: SolverLimits
    max_requests: int
    max_requested_output_tokens: int
    evidence: str = "offline_canned"
    variants: tuple[str, ...] = ("canonical",)
    repeats: int = 1
    rendering_seed: int = 3263
    freeze: dict | None = None
    qualification_policy: str | None = None
    qualification_baseline: dict | None = None
    provider_failure_policy: str | None = None

    def __post_init__(self):
        if not isinstance(self.model, ModelConfig) or not all(
            isinstance(value, SolverLimits)
            for value in (self.solver, self.reference_solver)
        ):
            raise ValueError(
                "Run configuration requires typed model and solver settings"
            )
        if self.evidence not in ("offline_canned", "live_development", *FROZEN_MODES):
            raise ValueError("Unsupported run evidence mode")
        if self.evidence in FROZEN_MODES:
            if not isinstance(self.freeze, dict):
                raise ValueError("Frozen mode needs an explicit protocol")
        elif self.freeze is not None:
            raise ValueError("Development mode cannot carry frozen protocol")
        if self.qualification_policy is not None and (
            self.qualification_policy not in DEVELOPMENT_QUALIFICATION_POLICIES
            or self.evidence != "live_development"
        ):
            raise ValueError(
                "Qualification policy requires live development and a supported version"
            )
        if self.qualification_baseline is not None:
            baseline = self.qualification_baseline
            observing = self.qualification_policy == OBSERVE_BACKEND_POLICY
            field = "system_fingerprints" if observing else "system_fingerprint"
            if (
                self.qualification_policy not in DEVELOPMENT_QUALIFICATION_POLICIES
                or not isinstance(baseline, dict)
                or set(baseline) != {field, "capability_sha256"}
            ):
                raise ValueError("Invalid qualification baseline")
            fingerprints = baseline[field] if observing else [baseline[field]]
            hashes = baseline["capability_sha256"]
            if (
                not isinstance(fingerprints, list) or not 1 <= len(fingerprints) <= 2
                or any(f is not None and (not isinstance(f, str) or not 0 < len(f) <= 200
                                         or any(c.isspace() for c in f)) for f in fingerprints)
                or len(set(fingerprints)) != len(fingerprints)
                or not isinstance(hashes, list)
                or len(hashes) != 2
                or any(not isinstance(h, str) or re.fullmatch(r"[0-9a-f]{64}", h) is None for h in hashes)
            ):
                raise ValueError("Invalid qualification baseline observation or hashes")
        if self.model.max_attempts != 1:
            raise ValueError(
                "Serial runner permits one request per attempt, no hidden retries"
            )
        if self.provider_failure_policy not in (None, CONTINUE_TRANSIENT_POLICY):
            raise ValueError("Unsupported provider failure policy")
        if any(
            type(x) is not int or x < 0
            for x in (
                self.max_requests,
                self.max_requested_output_tokens,
                self.rendering_seed,
            )
        ):
            raise ValueError("Caps and seed must be nonnegative integers")
        if type(self.repeats) is not int or self.repeats < 1:
            raise ValueError("Repeat count must be positive")
        if (
            not isinstance(self.variants, tuple)
            or not self.variants
            or any(not isinstance(v, str) for v in self.variants)
            or len(set(self.variants)) != len(self.variants)
            or set(self.variants) - {"canonical", "paraphrase", "reordered"}
        ):
            raise ValueError("Invalid or duplicate variants")


def write_new(path, data):
    with os.fdopen(
        os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
        "w",
        encoding="utf-8",
    ) as out:
        json.dump(to_data(data), out, sort_keys=True, allow_nan=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def replace_pending(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, delete=False, encoding="utf-8"
        ) as out:
            temporary = Path(out.name)
            json.dump(to_data(data), out, sort_keys=True, allow_nan=False)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def read(path):
    return load_json(path.read_text(encoding="utf-8"))


def requests(cases, config):
    for case in cases:
        for variant in config.variants:
            view = render(case, variant, config.rendering_seed)
            for repeat in range(config.repeats):
                for approach in ("direct", "solver_augmented"):
                    identity = {
                        "case_id": case.case_id,
                        "variant_id": variant,
                        "task_type": case.problem.task_type,
                        "approach": approach,
                        "repeat": repeat,
                        "model_config": to_data(config.model),
                    }
                    yield digest(identity), identity, case, view


def _contract(cases, config):
    config_data = to_data(config)
    # Preserve the legacy wire shape when optional policies were not selected.
    for field in ("qualification_policy", "qualification_baseline", "provider_failure_policy"):
        if config_data[field] is None:
            config_data.pop(field)
    package = Path(__file__).resolve().parents[1]
    source = {
        str(p.relative_to(package)): digest(p.read_text(encoding="utf-8"))
        for p in sorted(package.rglob("*"))
        if p.is_file() and p.suffix in (".py", ".crt")
    }
    prompts = {}
    for key, identity, case, view in requests(cases, config):
        messages = (
            build_extraction_messages(view)
            if identity["approach"] == "solver_augmented"
            else build_messages(
                view.text,
                task_type=view.task_type,
                required_activity_ids=view.activity_ids,
                original_schedule=(
                    view.original_schedule.to_list() if view.original_schedule else None
                ),
            )
        )
        prompts[key] = digest(messages)
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=package, text=True, capture_output=True
        )
        revision = commit.stdout.strip() if commit.returncode == 0 else None
    except FileNotFoundError:
        # Installed runtime images need not contain Git; source hashes remain mandatory.
        revision = None
    return {
        "code_commit": revision,
        "format_version": "2.0" if config.evidence in FROZEN_MODES else "1.0",
        "case_bundle_sha256": digest(case_bundle(cases)),
        "config": config_data,
        "provider_execution": (execution_contract(config.model)
                               if config.evidence in ("live_development", "live_frozen") else None),
        "source_sha256": source,
        "request_prompt_sha256": prompts,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "httpx": version("httpx"),
            "ortools": version("ortools"),
            "truststore": version("truststore"),
            "httpcore": version("httpcore"),
            "certifi": version("certifi"),
            "protobuf": version("protobuf"),
            "numpy": version("numpy"),
        },
    }


def plan_run(cases, config):
    """Check gold references and size the exact public requests without a provider."""
    cases = check_case_set(tuple(cases))
    contract = _contract(cases, config)
    check_frozen(cases, config, contract)
    labels = Counter()
    for case in cases:
        ref = reference(case, config.reference_solver)
        if config.evidence in FROZEN_MODES:
            check_frozen_reference(case, ref)
        labels[check_reference(case, ref)[0]] += 1
    sizes = []
    for _, identity, _, view in requests(cases, config):
        messages = (
            build_extraction_messages(view)
            if identity["approach"] == "solver_augmented"
            else build_messages(
                view.text,
                task_type=view.task_type,
                required_activity_ids=view.activity_ids,
                original_schedule=(
                    view.original_schedule.to_list() if view.original_schedule else None
                ),
            )
        )
        sizes.append(sum(len(m.content) for m in messages))
    requested = len(sizes) * config.model.max_tokens
    return {
        "state": "ready" if labels["UNRESOLVED"] == 0 else "unresolved_references",
        "evidence": "preflight_no_model_calls",
        "case_count": len(cases),
        "task_counts": dict(Counter(c.problem.task_type for c in cases)),
        "reference_labels": dict(labels),
        "planned_requests": len(sizes),
        "requested_output_tokens": requested,
        "within_cap": len(sizes) <= config.max_requests
        and requested <= config.max_requested_output_tokens,
        "prompt_characters": {
            "min": min(sizes),
            "max": max(sizes),
            "total": sum(sizes),
        },
        "input_token_estimate": None,
        "contract": contract,
    }


def _stop_reason(response, expected_model=None, fingerprints=None, *, allow_backend_variation=False):
    response = to_data(response) if response else {}
    for attempt in response.get("attempts", []):
        status = attempt.get("http_status")
        if status in (401, 403, 429):
            return f"http_{status}"
    error = response.get("error")
    if error in (
        "tls_verification_error",
        "transport_error",
        "timeout",
        "request_budget_exhausted",
        "invalid_provider_response",
    ):
        return error
    if isinstance(error, str) and error.startswith("http_"):
        return error
    if expected_model is not None and response.get("returned_model") != expected_model:
        return "returned_model_mismatch"
    if expected_model is not None and fingerprints is not None:
        # Unknown is an identity observation too; a newly appearing/disappearing
        # fingerprint must not silently change a frozen block's backend evidence.
        attempts = response.get("attempts", [])
        fingerprints.update((a.get("execution") or {}).get("system_fingerprint") for a in attempts)
        if not attempts:
            fingerprints.add(None)
        if len(fingerprints) > 1 and not allow_backend_variation:
            return "backend_fingerprint_changed"
    return None


def run_batch(
    cases,
    directory: Path,
    config: RunConfig,
    *,
    canned=None,
    provider_complete=None,
    progress=None,
    failure_state=None,
):
    cases = check_case_set(tuple(cases))
    contract = _contract(cases, config)
    check_frozen(cases, config, contract)
    if failure_state is None:
        failure_state = FailureState(config.provider_failure_policy)
    elif failure_state.policy != config.provider_failure_policy:
        raise ValueError("Shared provider failure policy changed between blocks")
    expected_model = (
        config.model.model
        if config.evidence == "live_frozen"
        or config.qualification_policy in DEVELOPMENT_QUALIFICATION_POLICIES
        else None
    )
    if config.evidence in ("offline_canned", "offline_frozen") and (
        canned is None or provider_complete is not None
    ):
        raise ValueError("Offline runs require saved canned responses only")
    if config.evidence in ("live_development", "live_frozen") and (
        provider_complete is None or canned is not None
    ):
        raise ValueError("Live runs require an explicitly configured provider")
    if canned is not None:
        contract["canned_sha256"] = digest(canned)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = RunLock(directory / ".lock")
    try:
        manifest = directory / "manifest.json"
        if manifest.exists():
            if read(manifest)["contract"] != to_data(contract):
                raise ValueError(
                    "Run configuration/source/input changed; use a new run ID"
                )
            if digest(read(directory / "cases.json")) != contract["case_bundle_sha256"]:
                raise ValueError("Saved case bundle changed")
        else:
            if any(p.name != ".lock" for p in directory.iterdir()):
                raise ValueError("New run directory must be empty")
            write_new(directory / "cases.json", case_bundle(cases))
            write_new(
                manifest,
                {
                    "contract": contract,
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                },
            )
        refs = directory / "references"
        refs.mkdir(exist_ok=True)
        records = directory / "attempts"
        records.mkdir(exist_ok=True)
        gold = {}
        # Verify all references before making model requests.
        for case in cases:
            path = refs / (digest(case.case_id) + ".json")
            if not path.exists():
                ref = reference(case, config.reference_solver)
                write_new(path, {"reference": ref, "sha256": digest(ref)})
            saved = read(path)
            if digest(saved["reference"]) != saved["sha256"]:
                raise ValueError("Reference record changed")
            check_reference(case, saved["reference"])
            if config.evidence in FROZEN_MODES:
                check_frozen_reference(case, saved["reference"])
            gold[case.case_id] = saved["reference"]
        fingerprints = baseline_fingerprints(config)
        existing = list(records.glob("*.json"))
        reserved = len(existing)
        if (
            reserved > config.max_requests
            or reserved * config.model.max_tokens > config.max_requested_output_tokens
        ):
            raise ValueError("Saved reservations exceed run cap")
        for path in existing:
            saved = read(path)
            if path.stem not in contract["request_prompt_sha256"]:
                raise ValueError("Unexpected saved attempt")
            if saved["state"] != "completed":
                raise ValueError(
                    "Interrupted/uncertain attempt reserved; manual reconciliation required, no automatic retry"
                )
            if saved["sha256"] != digest(saved["payload"]):
                raise ValueError("Completed record changed")
        # Replay recovery state in planned order, never hash/filename order.
        # Completed timeouts stay completed; pending reservations still block above.
        for key, _, _, _ in requests(cases, config):
            path = records / (key + ".json")
            if not path.exists():
                continue
            saved = read(path)
            response = saved["payload"]["pipeline_result"].get("model_response") or {}
            reason = failure_state.observe(_stop_reason(
                response,
                expected_model,
                fingerprints,
                allow_backend_variation=config.qualification_policy == OBSERVE_BACKEND_POLICY,
            ))
            if reason:
                return {
                    "state": "stopped_provider",
                    "stop_reason": reason,
                    "completed": reserved,
                    "reserved_requests": reserved,
                }
        completed = 0
        for key, identity, case, view in requests(cases, config):
            path = records / (key + ".json")
            if path.exists():
                completed += 1
                continue
            if (
                reserved >= config.max_requests
                or (reserved + 1) * config.model.max_tokens
                > config.max_requested_output_tokens
            ):
                return {
                    "state": "budget_exhausted",
                    "completed": completed,
                    "reserved_requests": reserved,
                }
            if canned is not None and key not in canned:
                raise ValueError("Missing canned response; no attempt consumed")
            failure_state.before_request()
            pending = {
                "state": "pending_or_interrupted",
                "identity": identity,
                "requested_output_tokens": config.model.max_tokens,
                "started_utc": datetime.now(timezone.utc).isoformat(),
            }
            write_new(path, pending)
            reserved += 1
            callback = provider_complete
            if canned is not None:
                content = canned[key]
                callback = lambda *_: ModelResponse(
                    content, "offline-canned", 0.0, (), finish_reason="stop"
                )
            if identity["approach"] == "direct":
                result = run_direct(view, config.model, provider_complete=callback)
            else:
                result = run_solver_augmented(
                    view, config.model, config.solver, provider_complete=callback
                )
            replace_pending(path, {**pending, "pipeline_result": to_data(result)})
            scored = evaluate(
                case, result, gold[case.case_id], repeat=identity["repeat"]
            )
            payload = {
                "identity": identity,
                "public_view": to_data(view),
                "pipeline_result": to_data(result),
                "evaluation": to_data(scored),
            }
            replace_pending(
                path,
                {
                    **pending,
                    "state": "completed",
                    "payload": payload,
                    "sha256": digest(payload),
                },
            )
            completed += 1
            if progress is not None:
                progress(
                    {
                        "event": "attempt_completed",
                        **identity,
                        "completed": completed,
                        "planned": len(contract["request_prompt_sha256"]),
                        "pipeline_status": result.status,
                        "category": scored["category"],
                        "gold_valid": scored["gold_valid"],
                    }
                )
            reason = failure_state.observe(_stop_reason(
                result.model_response,
                expected_model,
                fingerprints,
                allow_backend_variation=config.qualification_policy == OBSERVE_BACKEND_POLICY,
            ))
            if reason:
                return {
                    "state": "stopped_provider",
                    "stop_reason": reason,
                    "completed": completed,
                    "reserved_requests": reserved,
                }
        return {
            "state": "completed",
            "completed": completed,
            "reserved_requests": reserved,
            "reserved_output_tokens": reserved * config.model.max_tokens,
        }
    finally:
        lock.release()


def replay(directory: Path):
    """No model requests or solver calls; recompute from immutable saved inputs."""
    manifest = read(directory / "manifest.json")
    cases = load_cases(directory / "cases.json")
    if digest(case_bundle(cases)) != manifest["contract"]["case_bundle_sha256"]:
        raise ValueError("Case bundle checksum mismatch")
    by_id = {c.case_id: c for c in cases}
    rows = []
    pending = []
    for path in sorted((directory / "attempts").glob("*.json")):
        record = read(path)
        if path.stem not in manifest["contract"]["request_prompt_sha256"]:
            raise ValueError("Unexpected saved attempt")
        if record["state"] != "completed":
            pending.append(path.stem)
            identity = record["identity"]
            case = by_id[identity["case_id"]]
            if digest(identity) != path.stem:
                raise ValueError("Pending identity mismatch")
            ref = read(directory / "references" / (digest(case.case_id) + ".json"))
            if digest(ref["reference"]) != ref["sha256"]:
                raise ValueError("Reference checksum mismatch")
            config_value = (
                identity["model_config"]
                if identity["approach"] == "direct"
                else {
                    "model": identity["model_config"],
                    "solver": manifest["contract"]["config"]["solver"],
                }
            )
            failed = {
                "instance_id": case.case_id,
                "variant_id": identity["variant_id"],
                "approach": identity["approach"],
                "status": "ERROR",
                "schedule": None,
                "config_sha256": hashlib.sha256(
                    json.dumps(config_value, sort_keys=True).encode()
                ).hexdigest(),
            }
            row = evaluate(case, failed, ref["reference"], repeat=identity["repeat"])
            row["category"] = "interrupted_or_uncertain"
            row["uncertain_reservations"] = 1
            rows.append(row)
            continue
        payload = record["payload"]
        if digest(payload) != record["sha256"]:
            raise ValueError("Attempt checksum mismatch")
        identity = payload["identity"]
        if digest(identity) != path.stem:
            raise ValueError("Attempt identity mismatch")
        case = by_id[identity["case_id"]]
        ref = read(directory / "references" / (digest(case.case_id) + ".json"))
        if digest(ref["reference"]) != ref["sha256"]:
            raise ValueError("Reference checksum mismatch")
        result = payload["pipeline_result"]
        if (
            result["approach"] != identity["approach"]
            or result["variant_id"] != identity["variant_id"]
        ):
            raise ValueError("Pipeline/attempt identity mismatch")
        rows.append(evaluate(case, result, ref["reference"], repeat=identity["repeat"]))
    return rows, {
        "pending_attempt_ids": pending,
        "completed": len(rows) - len(pending),
        "reserved": len(rows),
        "planned": len(manifest["contract"]["request_prompt_sha256"]),
        "not_started": len(manifest["contract"]["request_prompt_sha256"]) - len(rows),
        "evidence": manifest["contract"]["config"]["evidence"],
    }
