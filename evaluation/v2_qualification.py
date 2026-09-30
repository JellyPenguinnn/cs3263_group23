"""Offline v2/v3 qualification using the existing generator, runner and evaluator.

Usage: python evaluation/v2_qualification.py runs/NEW_QUALIFICATION [--version 2|3 | --cases CASES_JSON]
Canned gold-derived model responses verify integration, NOT model performance.
"""

from dataclasses import replace
import json
from pathlib import Path
import argparse
from scheduling.evaluation.benchmark import (
    generate_development_v2,
    generate_development_v3,
)
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.manifests import (
    benchmark_manifest_v2,
    benchmark_manifest_v3,
    structural_fingerprint,
)
from scheduling.evaluation.runner import (
    RunConfig,
    requests,
    run_batch,
    replay,
    write_new,
)
from scheduling.evaluation.metrics import summarize, analysis_details
from scheduling.providers import ModelConfig
from scheduling.pipelines.solver_augmented import PUBLIC_REQUEST_ID
from scheduling.solver import SolverLimits


def main(directory, version="2", *, cases_path=None):
    directory.mkdir(parents=True, exist_ok=False)
    generate, make_manifest, seed = (
        (generate_development_v2, benchmark_manifest_v2, 3264)
        if version == "2"
        else (generate_development_v3, benchmark_manifest_v3, 3265)
    )
    if cases_path is None:
        cases, records, selection = generate(seed)
        variants = ("canonical", "paraphrase", "reordered")
        if not selection["quota_complete"]:
            write_new(directory / "incomplete-selection.json", selection)
            raise ValueError(
                "Qualification matrix quota incomplete; exclusions retained"
            )
        write_new(
            directory / "benchmark.manifest.json",
            make_manifest(
                cases,
                generation_seed=seed,
                rendering_seed=3263,
                selection=selection,
                records=records,
                code_revision="see_run_contract_and_tested_source_receipt",
            ),
        )
    else:
        cases = load_cases(cases_path)
        variants = ("canonical",)
        if not cases or any(c.split != "development" for c in cases):
            raise ValueError("Canned qualification requires nonempty development cases")
        write_new(
            directory / "qualification-input.json",
            {
                "evidence": "supplied_development_cases_canonical_only",
                "authorship_or_review_claim": "none; use the supplied case provenance",
            },
        )
    expected = len(cases) * len(variants) * 2
    write_new(directory / "cases.json", case_bundle(cases))
    cfg = RunConfig(
        ModelConfig(
            "offline-canned-authored" if cases_path else f"offline-canned-v{version}",
            8192,
        ),
        SolverLimits(10),
        SolverLimits(30),
        expected,
        expected * 8192,
        variants=variants,
    )
    responses = {}
    for key, identity, case, _ in requests(cases, cfg):
        responses[key] = (
            replace(case.problem, instance_id=PUBLIC_REQUEST_ID).to_json()
            if identity["approach"] == "solver_augmented"
            else json.dumps(
                {
                    "status": case.expected_label,
                    "schedule": case.witness.to_list() if case.witness else None,
                }
            )
        )
    result = run_batch(cases, directory / "run", cfg, canned=responses)
    assert result["completed"] == expected
    assert (
        run_batch(cases, directory / "run", cfg, canned=responses)["reserved_requests"]
        == expected
    )
    rows, progress = replay(directory / "run")
    assert len(rows) == expected and all(r["accepted"] for r in rows)
    write_new(
        directory / "summary.json",
        {
            "progress": progress,
            "summary": summarize(rows),
            "analysis": analysis_details(rows),
        },
    )
    write_new(
        directory / "development-fingerprints.json",
        sorted(
            {
                structural_fingerprint(s)
                for c in cases
                for s in (c.problem, c.original_problem)
                if s is not None
            }
        ),
    )
    print(
        json.dumps(
            {
                "evidence": "offline_canned_integration_not_model_performance",
                "cases": len(cases),
                "completed": result["completed"],
                "live_model_calls": 0,
                "quota_complete": True,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--version", choices=("2", "3"), default="2")
    inputs.add_argument(
        "--cases", type=Path, help="Supplied development bundle; canonical only"
    )
    args = parser.parse_args()
    main(args.directory, args.version, cases_path=args.cases)
