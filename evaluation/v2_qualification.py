"""Offline v2/v3 qualification using the existing generator, runner and evaluator.

Usage: python evaluation/v2_qualification.py runs/NEW_QUALIFICATION [--version 2|3]
Canned gold-derived model responses verify integration, NOT model performance.
"""

import json
from pathlib import Path
import argparse
from scheduling.evaluation.benchmark import (
    generate_development_v2,
    generate_development_v3,
)
from scheduling.evaluation.cases import case_bundle
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
from scheduling.solver import SolverLimits


def main(directory, version="2"):
    directory.mkdir(parents=True, exist_ok=False)
    generate, make_manifest, seed = (
        (generate_development_v2, benchmark_manifest_v2, 3264)
        if version == "2"
        else (generate_development_v3, benchmark_manifest_v3, 3265)
    )
    cases, records, selection = generate(seed)
    expected = len(cases) * 3 * 2
    if not selection["quota_complete"]:
        write_new(directory / "incomplete-selection.json", selection)
        raise ValueError("Qualification matrix quota incomplete; exclusions retained")
    write_new(directory / "cases.json", case_bundle(cases))
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
    cfg = RunConfig(
        ModelConfig(f"offline-canned-v{version}", 8192),
        SolverLimits(10),
        SolverLimits(30),
        expected,
        expected * 8192,
        variants=("canonical", "paraphrase", "reordered"),
    )
    responses = {}
    for key, identity, case, _ in requests(cases, cfg):
        responses[key] = (
            case.problem.to_json()
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
    parser.add_argument("--version", choices=("2", "3"), default="2")
    args = parser.parse_args()
    main(args.directory, args.version)
