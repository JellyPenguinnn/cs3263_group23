"""Incremental CLI: offline parsing/direct replay and explicitly selected live smoke."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import tempfile

from scheduling.pipelines.direct import build_messages, parse_direct_output, request_direct
from scheduling.providers import Message, ModelConfig, ModelResponse, RequestBudget, SoCLaaSProvider


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Group 23 direct component checks (not gold validation)")
    commands = parser.add_subparsers(dest="command", required=True)
    parse = commands.add_parser("parse-direct", help="Check a saved response's structure and public activity coverage")
    parse.add_argument("response", type=Path)
    parse.add_argument("--activity-id", action="append", required=True)
    for name, help_text in (("direct-offline", "Exercise prompts and parsing with a canned response"),
                            ("direct-live", "LIVE: one direct component request, no retries; no gold validation")):
        direct = commands.add_parser(name, help=help_text)
        direct.add_argument("--text-file", type=Path, required=True)
        direct.add_argument("--activity-id", action="append", required=True)
        direct.add_argument("--task-type", choices=("generation", "repair"), required=True)
        direct.add_argument("--original-schedule", type=Path)
        if name == "direct-offline":
            direct.add_argument("--response-file", type=Path, required=True)
        else:
            direct.add_argument("--model", required=True)
            direct.add_argument("--max-tokens", type=int, required=True)
            direct.add_argument("--output", type=Path, required=True)
            direct.add_argument("--allow-live", action="store_true", required=True)
    smoke = commands.add_parser("provider-smoke", help="LIVE: one listing and at most one 32-token completion")
    smoke.add_argument("--model", required=True)
    smoke.add_argument("--allow-live", action="store_true", required=True)
    from scheduling.formal_cli import add_commands
    add_commands(commands)
    from scheduling.evaluation.cli import add_commands as add_evaluation_commands
    add_evaluation_commands(commands)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        from scheduling.evaluation.cli import COMMANDS, run_command as run_evaluation
        if args.command in COMMANDS:
            return run_evaluation(args)
        if args.command in ("solve", "solver-offline"):
            from scheduling.formal_cli import run_command
            return run_command(args)
        if args.command == "parse-direct":
            parsed = parse_direct_output(args.response.read_text(encoding="utf-8"), args.activity_id)
            print(json.dumps({"evidence": "offline_structure_only", **asdict(parsed)}, sort_keys=True))
            return 2 if parsed.status == "INVALID_OUTPUT" else 0
        if args.command in ("direct-offline", "direct-live"):
            original = None
            if args.original_schedule:
                original = json.loads(args.original_schedule.read_text(encoding="utf-8"))
            text = args.text_file.read_text(encoding="utf-8")
            if args.command == "direct-offline":
                content = args.response_file.read_text(encoding="utf-8")

                def canned(messages: object, config: object) -> ModelResponse:
                    return ModelResponse(content, "offline-canned", 0.0, (), finish_reason="stop")

                result = request_direct(
                    text, ModelConfig("offline-canned", 256), task_type=args.task_type,
                    required_activity_ids=args.activity_id, provider_complete=canned,
                    original_schedule=original,
                )
                print(json.dumps({"evidence": "offline_canned_unvalidated", **asdict(result)}, sort_keys=True))
            else:
                config = ModelConfig(args.model, args.max_tokens)
                build_messages(text, task_type=args.task_type, required_activity_ids=args.activity_id,
                               original_schedule=original)
                # Reserve a new record before any network activity. An interrupted call
                # remains visible and must not be automatically replayed or overwritten.
                pending = {"evidence": "live_direct_component_unvalidated", "state": "pending_or_interrupted",
                           "task_type": args.task_type, "model_config": asdict(config),
                           "created_utc": datetime.now(timezone.utc).isoformat(),
                           "python": platform.python_version(), "platform": platform.platform(),
                           "httpx_version": version("httpx"),
                           "source_sha256": {
                               name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                               for name in ("cli.py", "pipelines/direct.py", "providers/soclaas.py", "providers/types.py")},
                           "public_input": {"text": text, "activity_ids": args.activity_id,
                                            "original_schedule": original}}
                with SoCLaaSProvider.from_environment(budget=RequestBudget(1, config.max_tokens)) as provider:
                    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(descriptor, "w", encoding="utf-8") as record:
                        json.dump(pending, record, sort_keys=True)
                        record.flush()
                        os.fsync(record.fileno())
                    result = request_direct(
                        text, config, task_type=args.task_type, required_activity_ids=args.activity_id,
                        provider_complete=provider.complete, original_schedule=original,
                    )
                completed = {**pending, "state": "completed", "result": asdict(result)}
                with tempfile.NamedTemporaryFile(mode="w", dir=args.output.parent, delete=False,
                                                 encoding="utf-8") as record:
                    json.dump(completed, record, sort_keys=True)
                    record.flush()
                    os.fsync(record.fileno())
                    temporary_path = Path(record.name)
                os.replace(temporary_path, args.output)
                print(json.dumps({"evidence": pending["evidence"], "status": result.status,
                                  "returned_model": result.response.returned_model,
                                  "error": result.response.error, "output": str(args.output)}, sort_keys=True))
            return 2 if result.status in ("INVALID_OUTPUT", "ERROR") else 0
        budget = RequestBudget(2, 32)
        with SoCLaaSProvider.from_environment(budget=budget) as provider:
            models = provider.list_models()
            response = provider.complete([Message("user", "Reply exactly OK.")], ModelConfig(args.model, 32))
        # Never print raw provider content or the environment in a connectivity check.
        print(json.dumps({
            "evidence": "connectivity_only", "available_models": models,
            "requested_model": args.model, "returned_model": response.returned_model,
            "acknowledged": response.content is not None and response.content.strip() == "OK",
            "error": response.error, "attempts": [asdict(a) for a in response.attempts],
            "requests_used": budget.requests_used,
            "completion_tokens_reserved": budget.completion_tokens_reserved,
        }, sort_keys=True))
        return 2 if response.error else 0
    except FileExistsError:
        print(json.dumps({"error": "output_exists_no_request_sent"}))
        return 2
    except OSError:
        print(json.dumps({"error": "file_access_error"}))
        return 2
    except ValueError:
        print(json.dumps({"error": "invalid_input_or_provider_configuration"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
