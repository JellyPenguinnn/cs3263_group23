"""Bounded F2 serving-identity diagnostic; no scheduling or model-quality claim.

Uses the existing provider and record writer. Each new directory requires its own
human authorization. Existing directories are never resumed or overwritten.
"""

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

from scheduling.evaluation.runner import write_new
from scheduling.providers import Message, ModelConfig, RequestBudget, SoCLaaSProvider
from scheduling.providers.execution import execution_contract
from scheduling.schema import SchemaError, load_json

MODELS = ("qwen3.6:35b", "qwen3.8:27b")
CONFIGS = tuple(
    ModelConfig(model, 256, connect_timeout=30, read_timeout=120) for model in MODELS
)
MESSAGES = (
    Message("system", "Return only the requested JSON object."),
    Message("user", 'Return exactly {"ok":true} with no other text.'),
)
MAX_CALLS = 6
MAX_OUTPUT = 1536


def response_issue(response, config):
    if response.error:
        return "provider_error:" + response.error
    if response.returned_model != config.model:
        return "returned_model_mismatch"
    if response.finish_reason != "stop":
        return "incomplete_completion"
    if len(response.attempts) != 1:
        return "unexpected_attempt_count"
    execution = response.attempts[0].execution
    if not execution or execution.contract != execution_contract(config):
        return "execution_metadata_mismatch"
    try:
        answer = load_json(response.content)
    except SchemaError:
        return "invalid_diagnostic_answer"
    if (
        not isinstance(answer, dict)
        or set(answer) != {"ok"}
        or answer["ok"] is not True
    ):
        return "invalid_diagnostic_answer"
    return None


def summarize(records):
    models = []
    for name in MODELS:
        selected = [r for r in records if r["requested_model"] == name]
        fingerprints = Counter(
            a["execution"]["system_fingerprint"]
            for r in selected
            for a in r["response"]["attempts"]
            if a["execution"]
        )
        complete = len(selected) == 3 and all(r["issue"] is None for r in selected)
        reported = [
            a["usage"]["total_tokens"]
            for r in selected
            for a in r["response"]["attempts"]
            if a["usage"]["total_tokens"] is not None
        ]
        models.append(
            {
                "model": name,
                "completed_responses": len(selected),
                "fingerprints": [
                    {"value": k, "count": v}
                    for k, v in sorted(fingerprints.items(), key=lambda x: str(x[0]))
                ],
                "observed_variation": len(fingerprints) > 1,
                "identity_observation": (
                    "incomplete"
                    if not complete
                    else (
                        "unavailable"
                        if None in fingerprints
                        else (
                            "varied" if len(fingerprints) > 1 else "same_in_three_calls"
                        )
                    )
                ),
                "reported_tokens": sum(reported) if reported else None,
                "usage_reported_attempts": sum(
                    a["usage"]["total_tokens"] is not None
                    for r in selected
                    for a in r["response"]["attempts"]
                ),
            }
        )
    return {
        "models": models,
        "completed_responses": len(records),
        "requests_reserved": len(records),
        "requested_output_tokens_reserved": 256 * len(records),
        "stop_reason": next((r["issue"] for r in records if r["issue"]), None),
        "limits": [
            "Three observations cannot establish stable hosting or pinned weights.",
            "Tiny JSON checks do not qualify scheduling accuracy, long outputs, reasoning budgets or eligibility.",
            "Fingerprint variation is recorded only in this diagnostic; frozen study checks remain strict.",
            "Input tokens are additional; unavailable usage is not zero.",
        ],
    }


def diagnose(directory, *, complete, authorization_reference):
    if (
        not isinstance(authorization_reference, str)
        or not authorization_reference.strip()
    ):
        raise ValueError("An actual authorization reference is required")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    package = __import__("scheduling.providers", fromlist=["__file__"])
    provider_root = Path(package.__file__).parent
    source = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in provider_root.iterdir()
        if p.suffix in (".py", ".crt")
    }
    source["diagnose_provider.py"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    # Source hashes remain available in copied installations without Git.
    try:
        git = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        commit = git.stdout.strip() if git.returncode == 0 else None
    except FileNotFoundError:
        commit = None
    manifest = {
        "format_version": "1.0",
        "evidence": "provider_identity_diagnostic_not_benchmark",
        "authorization_reference": authorization_reference,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code_commit": commit,
        "source_sha256": source,
        "python": platform.python_version(),
        "httpx": version("httpx"),
        "platform": platform.platform(),
        "messages": [asdict(m) for m in MESSAGES],
        "configs": [asdict(c) for c in CONFIGS],
        "max_requests": MAX_CALLS,
        "max_requested_output_tokens": MAX_OUTPUT,
        "metadata_requests": 0,
        "retries": 0,
        "resume": "forbidden; reconcile interrupted reservations without reissue",
    }
    write_new(directory / "manifest.json", manifest)
    records = []
    started = time.monotonic()
    for repeat in range(3):
        for config in CONFIGS:
            index = len(records)
            reservation = {
                "index": index,
                "repeat": repeat,
                "requested_model": config.model,
                "reserved_output_tokens": 256,
            }
            write_new(directory / f"reservation-{index:02}.json", reservation)
            # Unexpected interruption leaves an explicit reservation and no result.
            # A new invocation cannot reissue it because the directory exists.
            response = complete(MESSAGES, config)
            record = {
                **reservation,
                "response": asdict(response),
                "issue": response_issue(response, config),
            }
            write_new(directory / f"response-{index:02}.json", record)
            records.append(record)
            if record["issue"]:
                break
        if records[-1]["issue"]:
            break
    result = {**summarize(records), "batch_wall_seconds": time.monotonic() - started}
    write_new(directory / "summary.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--authorization-reference", required=True)
    args = parser.parse_args(argv)
    if not args.allow_live:
        parser.error(
            "Explicit --allow-live and a new six-call authorization are required"
        )
    with SoCLaaSProvider.from_environment(
        budget=RequestBudget(MAX_CALLS, MAX_OUTPUT)
    ) as provider:
        result = diagnose(
            args.directory,
            complete=provider.complete,
            authorization_reference=args.authorization_reference,
        )
    print(json.dumps(result, sort_keys=True))
    return 2 if result["stop_reason"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
