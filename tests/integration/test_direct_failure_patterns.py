"""Synthetic regressions for three observed development failures, not new evidence."""

from dataclasses import replace
import json

import pytest

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import BenchmarkCase
from scheduling.evaluation.scoring import check_reference, evaluate, reference
from scheduling.pipelines.direct import run_direct
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import BlockedInterval, Deadline, Schedule, Window
from scheduling.solver import SolverLimits
from tests.formal_support import tiny


@pytest.mark.parametrize("pattern", ["availability", "deadline", "false_unsat"])
def test_semantic_failures_stay_raw_and_rejected(pattern, monkeypatch):
    original = tiny()
    old = Schedule.from_list(
        [
            {"activity_id": "A", "start_slot": 0},
            {"activity_id": "B", "start_slot": 2},
        ]
    )
    if pattern == "availability":
        spec = replace(
            original,
            activities=(
                replace(original.activities[0], availability=(Window(2, 4),)),
                original.activities[1],
            ),
        )
        metadata = {}
        answer = {"status": "SAT", "schedule": old.to_list()}
    else:
        rule = (
            Deadline("event", "B", 2)
            if pattern == "deadline"
            else BlockedInterval("event", "participant", "P", 0, 1)
        )
        spec = replace(original, task_type="repair", constraints=(rule,))
        metadata = {
            "original_problem": original,
            "original_schedule": old,
            "event": pattern,
        }
        answer = (
            {"status": "UNSAT", "schedule": None}
            if pattern == "false_unsat"
            else {
                "status": "SAT",
                "schedule": old.to_list(),
            }
        )
    case = BenchmarkCase(
        "tiny",
        "tiny",
        "development",
        "diagnostic",
        "regression",
        pattern,
        spec,
        **metadata,
    )
    gold = reference(case, SolverLimits())
    # Explicit feasible witnesses: A2/B0, A0/B1 and A1/B2, respectively.
    assert check_reference(case, gold)[0] == "SAT"
    raw = json.dumps(answer)
    calls = []

    def canned(messages, config):
        calls.append(messages)
        return ModelResponse(raw, "offline-regression", 0, ())

    monkeypatch.setattr(
        "scheduling.solver.solve", lambda *_: pytest.fail("Direct path cannot solve")
    )
    result = run_direct(
        render(case), ModelConfig("offline-regression", 128), provider_complete=canned
    )
    row = evaluate(case, result, gold)
    assert len(calls) == 1
    assert result.model_response.content == raw
    assert result.status == answer["status"]
    assert (result.schedule.to_list() if result.schedule else None) == answer[
        "schedule"
    ]
    assert row["accepted"] is False
    assert row["category"] == (
        "false_unsat" if pattern == "false_unsat" else "gold_invalid_schedule"
    )
    if pattern != "false_unsat":
        category = "activity_availability" if pattern == "availability" else "deadline"
        assert category in {
            item["category"] for item in row["validation"]["violations"]
        }
    assert result.solve_result is None and result.extracted_spec is None
