"""Evaluation CLI; live execution is explicit and capped, replay is offline."""

import json
import sys
from dataclasses import fields
from pathlib import Path
from scheduling.schema import load_json, to_data

COMMANDS = (
    "benchmark-generate",
    "freeze-draft",
    "validate",
    "evaluate-plan",
    "evaluate-batch",
    "evaluate-replay",
)


def add_commands(commands):
    generate = commands.add_parser(
        "benchmark-generate",
        help="Write legacy v1, structural v2 or challenge v3 development cases",
    )
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--seed", type=int, default=3263)
    generate.add_argument("--fixtures-only", action="store_true")
    generate.add_argument("--version", choices=("1", "2", "3"), default="1")
    generate.add_argument("--repetitions", type=int, default=1)
    draft = commands.add_parser(
        "freeze-draft",
        help="Write a non-runnable protocol draft for team review; no calls",
    )
    draft.add_argument("--cases", type=Path, required=True)
    draft.add_argument("--config", type=Path, required=True)
    draft.add_argument("--manifest", type=Path, required=True)
    draft.add_argument("--development-registry", type=Path, required=True)
    draft.add_argument(
        "--mode", choices=("offline_frozen", "live_frozen"), default="offline_frozen"
    )
    draft.add_argument("--output", type=Path, required=True)
    validate = commands.add_parser(
        "validate", help="Independently validate a schedule against explicit gold"
    )
    validate.add_argument("--spec", type=Path, required=True)
    validate.add_argument("--schedule", type=Path, required=True)
    validate.add_argument("--original-schedule", type=Path)
    plan = commands.add_parser(
        "evaluate-plan",
        help="Validate references and size a run without credentials or model calls",
    )
    plan.add_argument("--cases", type=Path, required=True)
    plan.add_argument("--config", type=Path, required=True)
    plan.add_argument("--output", type=Path)
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
    if not isinstance(data, dict) or set(data) - {f.name for f in fields(RunConfig)}:
        raise ValueError("Unsupported run configuration fields")
    for name, cls in (
        ("model", ModelConfig),
        ("solver", SolverLimits),
        ("reference_solver", SolverLimits),
    ):
        if not isinstance(data.get(name), dict):
            raise ValueError("Missing model or solver configuration")
        try:
            data[name] = cls(**data[name])
        except TypeError:
            raise ValueError(
                "Unsupported model or solver configuration fields"
            ) from None
    if "variants" in data:
        if not isinstance(data["variants"], list):
            raise ValueError("Variants must be an explicit array")
        data["variants"] = tuple(data["variants"])
    try:
        return RunConfig(**data)
    except TypeError:
        raise ValueError("Missing or invalid run configuration fields") from None


def run_command(args):
    from scheduling.evaluation.runner import run_batch, replay, write_new

    if args.command == "benchmark-generate":
        from scheduling.evaluation.benchmark import tiny_fixtures, generate_development
        from scheduling.evaluation.cases import case_bundle

        from scheduling.evaluation.manifests import (
            benchmark_manifest,
            benchmark_manifest_v2,
            benchmark_manifest_v3,
        )

        if args.version in ("2", "3"):
            if args.fixtures_only:
                raise ValueError(
                    "V2/V3 are separate procedural datasets; fixtures stay v1"
                )
            from scheduling.evaluation.benchmark import (
                generate_development_v2,
                generate_development_v3,
            )
            import subprocess

            generate = (
                generate_development_v2
                if args.version == "2"
                else generate_development_v3
            )
            make_manifest = (
                benchmark_manifest_v2 if args.version == "2" else benchmark_manifest_v3
            )
            cases, provenance, selection = generate(
                args.seed, repetitions=args.repetitions
            )
            try:
                revision = subprocess.run(
                    ["git", "rev-parse", "HEAD"], capture_output=True, text=True
                )
                code_revision = (
                    revision.stdout.strip()
                    if revision.returncode == 0
                    else "unavailable"
                )
            except FileNotFoundError:
                # Git metadata is optional in a wheel-only installation.
                code_revision = "unavailable"
            manifest = make_manifest(
                cases,
                generation_seed=args.seed,
                rendering_seed=3263,
                selection=selection,
                records=provenance,
                code_revision=code_revision,
            )
        else:
            if args.repetitions != 1:
                raise ValueError("Repetitions require generator v2 or v3")
            cases = (
                tiny_fixtures()
                if args.fixtures_only
                else tiny_fixtures() + generate_development(args.seed)
            )
            manifest = benchmark_manifest(
                cases,
                generation_seed=None if args.fixtures_only else args.seed,
                rendering_seed=3263,
            )
        manifest_path = args.output.with_suffix(".manifest.json")
        if args.output.exists() or manifest_path.exists():
            raise FileExistsError("Benchmark outputs already exist")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_new(args.output, case_bundle(cases))
        write_new(manifest_path, manifest)
        result = {
            "quota_complete": manifest.get("selection", {}).get("quota_complete", True),
            "case_count": len(cases),
            "split": "development",
            "human_review": "pending",
        }
    elif args.command == "freeze-draft":
        from scheduling.evaluation.cases import load_cases
        from scheduling.evaluation.frozen import draft_frozen_config

        draft = draft_frozen_config(
            load_cases(args.cases),
            load_config(args.config),
            load_json(args.manifest.read_text()),
            load_json(args.development_registry.read_text()),
            mode=args.mode,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_new(args.output, draft)
        result = {
            "state": "draft_requires_team_review",
            "model_calls": 0,
            "output": str(args.output),
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
    elif args.command == "evaluate-plan":
        from scheduling.evaluation.cases import load_cases
        from scheduling.evaluation.runner import plan_run

        result = plan_run(load_cases(args.cases), load_config(args.config))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_new(args.output, result)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["state"] == "ready" and result["within_cap"] else 2
    elif args.command == "evaluate-batch":
        from scheduling.evaluation.cases import load_cases

        config = load_config(args.config)
        cases = load_cases(args.cases)

        def progress(event):
            print(json.dumps(event, sort_keys=True), file=sys.stderr, flush=True)

        if config.evidence in ("live_development", "live_frozen"):
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
                    cases,
                    args.run_dir,
                    config,
                    provider_complete=provider.complete,
                    progress=progress,
                )
        else:
            if args.allow_live or not args.canned:
                raise ValueError("Offline batch requires canned responses")
            result = run_batch(
                cases,
                args.run_dir,
                config,
                canned=load_json(args.canned.read_text()),
                progress=progress,
            )
    else:
        from scheduling.evaluation.metrics import (
            summarize,
            export_tables,
            analysis_details,
        )

        rows, progress = replay(args.run_dir)
        result = {"progress": progress, "summary": summarize(rows)}
        if args.export_dir:
            export_tables(rows, args.export_dir)
            write_new(args.export_dir / "summary.json", result)
            write_new(args.export_dir / "analysis.json", analysis_details(rows))
            if args.figures:
                from scheduling.evaluation.figures import export_figures

                export_figures(rows, args.export_dir, evidence=progress["evidence"])
        elif args.figures:
            raise ValueError("Figures require an export directory")
    print(json.dumps(result, sort_keys=True))
    if args.command == "benchmark-generate" and not result["quota_complete"]:
        return 2
    return (
        2 if args.command == "evaluate-batch" and result["state"] != "completed" else 0
    )
