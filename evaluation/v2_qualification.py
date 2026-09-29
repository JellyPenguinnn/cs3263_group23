"""Offline v2 qualification using the existing generator, runner and evaluator.

Usage: python evaluation/v2_qualification.py runs/NEW_QUALIFICATION
Canned gold-derived model responses verify integration, NOT model performance.
"""

import json
from pathlib import Path
import sys
from scheduling.evaluation.benchmark import generate_development_v2
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.manifests import (
    benchmark_manifest_v2,
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


def main(directory):
    directory.mkdir(parents=True, exist_ok=False)
    cases, records, selection = generate_development_v2(3264)
    if not selection["quota_complete"]:
        write_new(directory / "incomplete-selection.json", selection)
        raise ValueError("Qualification matrix quota incomplete; exclusions retained")
    write_new(directory / "cases.json", case_bundle(cases))
    write_new(
        directory / "benchmark.manifest.json",
        benchmark_manifest_v2(
            cases,
            generation_seed=3264,
            rendering_seed=3263,
            selection=selection,
            records=records,
            code_revision="see_run_contract_and_tested_source_receipt",
        ),
    )
    cfg = RunConfig(
        ModelConfig("offline-canned-v2", 8192),
        SolverLimits(10),
        SolverLimits(30),
        864,
        864 * 8192,
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
    assert result["completed"] == 864
    assert (
        run_batch(cases, directory / "run", cfg, canned=responses)["reserved_requests"]
        == 864
    )
    rows, progress = replay(directory / "run")
    assert len(rows) == 864 and all(r["accepted"] for r in rows)
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
    main(Path(sys.argv[1]))
