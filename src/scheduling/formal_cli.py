"""Formal-core command implementations wired into the shared CLI."""

import argparse
import json
import os
from pathlib import Path

from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import NaturalLanguageView, ProblemSpec, RepairContext, Schedule, load_json, to_data

COMMANDS = ("solve", "solver-offline")


def add_commands(commands: argparse._SubParsersAction) -> None:
    gold = commands.add_parser("solve", help="Solve an explicit specification with CP-SAT; no model calls")
    gold.add_argument("--spec", type=Path, required=True)
    gold.add_argument("--original-schedule", type=Path)
    canned = commands.add_parser("solver-offline", help="Run extraction-to-solver using a canned specification response")
    canned.add_argument("--view", type=Path, required=True)
    canned.add_argument("--response-file", type=Path, required=True)
    for command in (gold, canned):
        command.add_argument("--time-limit", type=float, default=5.0)
        command.add_argument("--seed", type=int, default=0)
        command.add_argument("--workers", type=int, default=1)
        command.add_argument("--output", type=Path)


def run_command(args: argparse.Namespace) -> int:
    from scheduling.solver import SolverLimits, solve
    limits = SolverLimits(args.time_limit, args.seed, args.workers)
    if args.command == "solve":
        spec = ProblemSpec.from_json(args.spec.read_text(encoding="utf-8"))
        context = None
        if args.original_schedule:
            context = RepairContext(Schedule.from_list(load_json(args.original_schedule.read_text(encoding="utf-8"))))
        result = solve(spec, limits, context)
        record = {"evidence": "compiled_spec_only_not_independent_gold_validation", "result": to_data(result),
                  "limits": to_data(limits)}
        failed = result.status == "MODEL_INVALID"
    else:
        from scheduling.pipelines.solver_augmented import run_solver_augmented
        view = NaturalLanguageView.from_dict(load_json(args.view.read_text(encoding="utf-8")))
        content = args.response_file.read_text(encoding="utf-8")
        result = run_solver_augmented(view, ModelConfig("offline-canned", 2048), limits,
                                     provider_complete=lambda *_: ModelResponse(content, "offline-canned", 0.0, (), finish_reason="stop"))
        record = {"evidence": "offline_canned_extraction_not_live_model", "result": to_data(result),
                  "limits": to_data(limits)}
        failed = result.status in ("ERROR", "INVALID_OUTPUT")
    content = json.dumps(record, sort_keys=True) + "\n"
    if args.output:
        with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as stream:
            stream.write(content)
    else:
        print(content, end="")
    return 2 if failed else 0
