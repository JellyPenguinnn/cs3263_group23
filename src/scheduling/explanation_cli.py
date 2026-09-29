"""Read existing evidence only; no solve, inference or run mutation."""

import json
from pathlib import Path

from scheduling.explanations import explain_case, explain_solver, render_text
from scheduling.schema import ProblemSpec, RepairContext, Schedule, load_json


def add_command(commands):
    parser = commands.add_parser(
        "explain",
        help="Explain saved solver or evaluation evidence without model calls",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--run-dir", type=Path)
    source.add_argument(
        "--spec", type=Path, help="Specification supplied to the saved solver result"
    )
    parser.add_argument(
        "--result", type=Path, help="Saved solve JSON (requires --spec)"
    )
    parser.add_argument("--original-schedule", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--approach", choices=("direct", "solver_augmented"))
    parser.add_argument("--variant", default="canonical")
    parser.add_argument("--repeat", type=int, default=0)
    parser.add_argument("--format", choices=("text", "json"), default="text")


def run_command(args):
    if args.run_dir:
        if (
            not args.case_id
            or not args.approach
            or args.result
            or args.original_schedule
            or args.repeat < 0
        ):
            raise ValueError(
                "A saved run needs case ID, approach and nonnegative repeat"
            )
        from scheduling.dashboard.service import Dashboard

        app = Dashboard(args.run_dir.parent, run_dir=args.run_dir)
        key = app.bootstrap()["selected"]
        saved = app.get_run(key)
        index = next(
            (i for i, c in enumerate(saved["cases"]) if c["case_id"] == args.case_id),
            None,
        )
        if index is None:
            raise ValueError("Case not found")
        detail = app.case_detail(key, index, args.variant, args.repeat)
        payload = detail["responses"][args.approach]
        row = next((r for r in detail["rows"] if r["approach"] == args.approach), None)
        if row is None:
            raise ValueError("Variant/repeat not found")
        explanation = explain_case(
            detail["case"], payload["pipeline_result"] if payload else None, row
        )
        explanation["evidence"] = saved["progress"]["evidence"]
        explanation["variant_id"], explanation["repeat"] = args.variant, args.repeat
    else:
        if not args.result or args.case_id or args.approach:
            raise ValueError("Standalone explanation requires --spec and --result")
        spec = ProblemSpec.from_json(args.spec.read_text(encoding="utf-8"))
        raw = load_json(args.result.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Saved solver result must be an object")
        result = raw.get("result", raw)
        required = {
            "status",
            "last_solver_status",
            "schedule",
            "stages",
            "optimality_proven",
        }
        if not isinstance(result, dict) or not required <= result.keys():
            raise ValueError("Not a saved SolveResult")
        context = (
            RepairContext(
                Schedule.from_list(
                    load_json(args.original_schedule.read_text(encoding="utf-8"))
                )
            )
            if args.original_schedule
            else None
        )
        if (spec.task_type == "repair") != (context is not None):
            raise ValueError("Repair requires its original schedule")
        explanation = {
            "format_version": "1.0",
            "case_id": spec.instance_id,
            "evidence": "saved_solver_result_not_gold_evaluation",
            "solver": explain_solver(spec, result, context),
        }
    print(
        (
            json.dumps(explanation, sort_keys=True, allow_nan=False)
            if args.format == "json"
            else f"Evidence: {explanation['evidence']}\n" + render_text(explanation)
        ),
        end="\n" if args.format == "json" else "",
    )
    return 0
