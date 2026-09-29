"""Evaluation CLI; live execution is explicit and capped, replay is offline."""

import json
from pathlib import Path
from scheduling.schema import load_json, to_data

COMMANDS = ("benchmark-generate", "validate", "evaluate-batch", "evaluate-replay")


def add_commands(commands):
    generate = commands.add_parser(
        "benchmark-generate",
        help="Write six fixtures plus 24 synthetic development cases",
    )
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--seed", type=int, default=3263)
    generate.add_argument("--fixtures-only", action="store_true")
    validate = commands.add_parser(
        "validate", help="Independently validate a schedule against explicit gold"
    )
    validate.add_argument("--spec", type=Path, required=True)
    validate.add_argument("--schedule", type=Path, required=True)
    validate.add_argument("--original-schedule", type=Path)
    batch = commands.add_parser(
        "evaluate-batch",
        help="Run/resume a capped development batch with immutable records",
    )
    batch.add_argument("--cases", type=Path, required=True)
    batch.add_argument("--config", type=Path, required=True)
    batch.add_argument("--run-dir", type=Path, required=True)
    batch.add_argument("--canned", type=Path)
    batch.add_argument("--allow-live", action="store_true")
    replay = commands.add_parser(
        "evaluate-replay",
        help="Recompute gold checks/metrics from saved records without model calls",
    )
    replay.add_argument("--run-dir", type=Path, required=True)
    replay.add_argument("--export-dir", type=Path)
    replay.add_argument("--figures", action="store_true")


def load_config(path):
    from scheduling.evaluation.runner import RunConfig
    from scheduling.providers import ModelConfig
    from scheduling.solver import SolverLimits

    data = load_json(path.read_text(encoding="utf-8"))
    data["model"] = ModelConfig(**data["model"])
    data["solver"] = SolverLimits(**data["solver"])
    data["reference_solver"] = SolverLimits(**data["reference_solver"])
    if "variants" in data:
        data["variants"] = tuple(data["variants"])
    return RunConfig(**data)


def run_command(args):
    from scheduling.evaluation.runner import run_batch, replay, write_new

    if args.command == "benchmark-generate":
        from scheduling.evaluation.benchmark import tiny_fixtures, generate_development
        from scheduling.evaluation.cases import case_bundle

        cases = (
            tiny_fixtures()
            if args.fixtures_only
            else tiny_fixtures() + generate_development(args.seed)
        )
        from scheduling.evaluation.manifests import benchmark_manifest

        manifest_path = args.output.with_suffix(".manifest.json")
        if args.output.exists() or manifest_path.exists():
            raise FileExistsError("Benchmark outputs already exist")
        write_new(args.output, case_bundle(cases))
        write_new(
            manifest_path,
            benchmark_manifest(
                cases,
                generation_seed=None if args.fixtures_only else args.seed,
                rendering_seed=3263,
            ),
        )
        result = {
            "case_count": len(cases),
            "split": "development",
            "human_review": "pending",
        }
    elif args.command == "validate":
        from scheduling.schema import ProblemSpec, RepairContext, Schedule
        from scheduling.validation import validate_schedule

        spec = ProblemSpec.from_json(args.spec.read_text())
        schedule = load_json(args.schedule.read_text())
        context = (
            RepairContext(
                Schedule.from_list(load_json(args.original_schedule.read_text()))
            )
            if args.original_schedule
            else None
        )
        result = to_data(validate_schedule(spec, schedule, context))
        print(json.dumps(result, sort_keys=True))
        return 0 if result["hard_feasible"] else 2
    elif args.command == "evaluate-batch":
        from scheduling.evaluation.cases import load_cases

        config = load_config(args.config)
        cases = load_cases(args.cases)
        if config.evidence == "live_development":
            if not args.allow_live or args.canned:
                raise ValueError(
                    "Live run needs explicit selection and no canned responses"
                )
            from scheduling.providers import RequestBudget, SoCLaaSProvider

            with SoCLaaSProvider.from_environment(
                budget=RequestBudget(
                    config.max_requests, config.max_requested_output_tokens
                )
            ) as provider:
                result = run_batch(
                    cases, args.run_dir, config, provider_complete=provider.complete
                )
        else:
            if args.allow_live or not args.canned:
                raise ValueError("Offline batch requires canned responses")
            result = run_batch(
                cases, args.run_dir, config, canned=load_json(args.canned.read_text())
            )
    else:
        from scheduling.evaluation.metrics import summarize, export_tables

        rows, progress = replay(args.run_dir)
        result = {"progress": progress, "summary": summarize(rows)}
        if args.export_dir:
            export_tables(rows, args.export_dir)
            write_new(args.export_dir / "summary.json", result)
            if args.figures:
                from scheduling.evaluation.figures import export_figures

                export_figures(rows, args.export_dir, evidence=progress["evidence"])
        elif args.figures:
            raise ValueError("Figures require an export directory")
    print(json.dumps(result, sort_keys=True))
    return 0
