"""Reproducible synthetic wiring demo, with canned successes and deliberate failures.

Run from repository root: .venv/bin/python evaluation/offline_demo.py runs/NEW_ID
No model is called. Gold-derived canned answers are test inputs, never research results.
"""

import json
from pathlib import Path
import sys

from scheduling.evaluation.benchmark import tiny_fixtures, generate_development
from scheduling.evaluation.runner import (
    RunConfig,
    requests,
    run_batch,
    replay,
    write_new,
)
from scheduling.evaluation.scoring import reference
from scheduling.evaluation.metrics import summarize, export_tables
from scheduling.evaluation.figures import export_figures
from scheduling.providers import ModelConfig
from scheduling.pipelines.solver_augmented import PUBLIC_REQUEST_ID
from scheduling.solver import SolverLimits


def main(directory):
    if directory.exists():
        raise FileExistsError(
            "Use a new demo directory; existing evidence is preserved"
        )
    cases = tiny_fixtures() + generate_development(3263)
    config = RunConfig(
        ModelConfig("offline-canned", 2048),
        SolverLimits(),
        SolverLimits(),
        180,
        368640,
        variants=("canonical", "paraphrase", "reordered"),
    )
    references = {
        case.case_id: reference(case, config.reference_solver) for case in cases
    }
    responses = {}
    for key, identity, case, view in requests(cases, config):
        if identity["approach"] == "direct":
            result = references[case.case_id]["result"]
            content = json.dumps(
                {
                    "status": "SAT" if result["schedule"] is not None else "UNSAT",
                    "schedule": result["schedule"],
                }
            )
            if case.case_id == "overlap":
                content = "deliberate malformed canned output"
        else:
            spec = case.problem.to_dict()
            spec["instance_id"] = PUBLIC_REQUEST_ID
            if case.case_id == "precedence-deadline":
                spec["constraints"] = [
                    {
                        "type": "precedence",
                        "id": "reversed",
                        "before": "B",
                        "after": "A",
                    }
                ]
            content = json.dumps(spec)
        responses[key] = content
    progress = run_batch(cases, directory, config, canned=responses)
    resumed = run_batch(cases, directory, config, canned=responses)
    assert resumed == progress
    rows, accounting = replay(directory)
    summary = summarize(rows)
    exported = directory / "export"
    export_tables(rows, exported)
    write_new(exported / "summary.json", {"progress": accounting, "summary": summary})
    export_figures(rows, exported, evidence="offline canned wiring checks")
    print(
        json.dumps(
            {
                "progress": progress,
                "replay": accounting,
                "case_count": len(cases),
                "accepted": sum(r["accepted"] is True for r in rows),
                "failures": sum(r["accepted"] is False for r in rows),
                "live_requests": 0,
                "export": str(exported),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
