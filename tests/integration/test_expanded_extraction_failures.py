"""Preserved F1 failures: offline replay is not new model-quality evidence."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from scheduling.evaluation.benchmark import generate_development_v2, generate_development_v3, render
from scheduling.evaluation.scoring import digest, evaluate, reference
from scheduling.extraction_diagnostics import compare_specifications
from scheduling.pipelines import solver_augmented
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import FixedStart, ProblemSpec, to_data
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule
from tests.formal_support import assignment_objective, enumerate_answers


FIXTURES = json.loads(
    (Path(__file__).parents[1] / "examples/expanded-extraction-failures.json").read_text()
)["cases"]
LIMITS = SolverLimits(5)
OMISSIONS = ((0, "A0", 1, "event"), (1, "A1", 2, "anchor"))


@pytest.fixture(scope="module")
def cases():
    v2 = generate_development_v2(3264)[0]
    v3 = generate_development_v3(3265)[0]
    return {c.case_id: c for c in (*v2, *v3)}


def replay_response(case, record):
    calls = []

    def complete(messages, config):
        calls.append(messages)
        public = json.loads(messages[1].content)
        assert public["instance_id"] == "request"
        assert public["description"] == render(case).text
        assert case.case_id not in messages[1].content
        if case.context:
            assert public["original_schedule"] == case.original_schedule.to_list()
        return ModelResponse(record["content"], record["returned_model"], 0, (),
                             finish_reason=record["finish_reason"])

    result = solver_augmented.run_solver_augmented(
        render(case), ModelConfig("offline-replay", 16384), LIMITS,
        provider_complete=complete,
    )
    assert len(calls) == 1
    assert result.model_response.content == record["content"]
    return result


@pytest.mark.parametrize("record", FIXTURES, ids=lambda r: r["case_id"])
def test_preserved_response_and_regenerated_input_identity(cases, record):
    case = cases[record["case_id"]]
    assert case.split == "development"
    assert digest(case.problem) == record["problem_sha256"]
    assert digest(case.context) == record["context_sha256"]
    assert digest(render(case)) == record["public_view_sha256"]
    assert hashlib.sha256(record["content"].encode()).hexdigest() == record["response_sha256"]
    assert record["returned_model"] == "qwen3.6:35b"
    assert record["finish_reason"] == "stop"  # Malformed output was not truncation.


@pytest.mark.parametrize("index,activity,slot,constraint_id", OMISSIONS)
def test_saved_fixed_start_omission_solves_but_fails_gold(cases, index, activity, slot, constraint_id):
    record = FIXTURES[index]
    case = cases[record["case_id"]]
    result = replay_response(case, record)
    assert result.status == "SAT" and result.solve_result.status == "OPTIMAL"
    assert result.extracted_spec == replace(
        ProblemSpec.from_json(record["content"]), instance_id=case.case_id
    )
    comparison = compare_specifications(case.problem, result.extracted_spec)
    assert comparison.mismatches == ("constraints",)
    assert comparison.omitted_constraints == 1 and comparison.invented_constraints == 0
    assert to_data(comparison.constraint_differences) == [{
        "kind": "omitted", "expected": {"type": "fixed_start", "activity_id": activity, "slot": slot},
        "actual": None, "count": 1,
    }]
    # Independently check the full returned witness, not a solver success flag.
    old = case.original_schedule.starts() if case.context else None
    starts = result.schedule.starts()
    assert assignment_objective(result.extracted_spec, starts, old) is not None
    assert assignment_objective(case.problem, starts, old) is None
    assert starts[activity] != slot
    row = evaluate(case, result, reference(case, LIMITS))
    assert row["gold_label"] == "UNSAT"
    assert row["category"] == "gold_invalid_schedule" and row["accepted"] is False
    assert row["objective_values"] is None and all(x is None for x in row["objective_gaps"])
    assert row["validation"]["violations"] == [{
        "category": "fixed_start", "constraint_id": constraint_id, "activity_ids": [activity],
    }]
    if case.context:
        assert validate_schedule(case.original_problem, case.original_schedule).hard_feasible
        assert case.original_schedule.starts()[activity] == 3 != slot
        assert result.solve_result.objectives.as_tuple() == (0, 0, 0)


@pytest.mark.parametrize("index,activity,slot,constraint_id", OMISSIONS)
def test_fixed_pair_proves_contradiction_and_restoration_is_diagnostic_only(
    cases, index, activity, slot, constraint_id
):
    record = FIXTURES[index]
    case = cases[record["case_id"]]
    gold = case.problem
    pair = tuple(a for a in gold.activities if a.id in ("A0", "A1"))
    anchors = tuple(c for c in gold.constraints if isinstance(c, FixedStart))
    assert len(pair) == len(anchors) == 2
    assert {c.activity_id for c in anchors} == {"A0", "A1"}
    assert {c.slot for c in anchors} == {slot}
    assert all(a.duration_slots == 1 and "Rpair" in a.resource_ids for a in pair)
    # Any full solution would solve this two-activity subproblem. Exhaust its
    # complete 48^2 grid without compiler/domain helpers: both occupy Rpair at slot.
    core = replace(gold, task_type="generation", activities=pair, constraints=anchors)
    assert not enumerate_answers(core)
    relaxed = replace(core, constraints=tuple(c for c in anchors if c.activity_id != activity))
    assert enumerate_answers(relaxed)
    extracted = replace(ProblemSpec.from_json(record["content"]), instance_id=case.case_id)
    missing = next(c for c in anchors if c.id == constraint_id)
    diagnostic = replace(extracted, constraints=extracted.constraints + (missing,))
    assert compare_specifications(gold, diagnostic).structurally_equivalent
    assert solve(diagnostic, LIMITS, case.context).status == "INFEASIBLE"
    # Gold restoration never modifies the fixture, pipeline or primary score.
    assert hashlib.sha256(record["content"].encode()).hexdigest() == record["response_sha256"]


def test_normal_completion_with_malformed_json_never_reaches_solver(cases, monkeypatch):
    record = FIXTURES[2]
    case = cases[record["case_id"]]
    with pytest.raises(json.JSONDecodeError) as caught:
        json.loads(record["content"])
    assert (caught.value.lineno, caught.value.colno) == (25, 9)
    # This reports a comma error, but the observed token is ']' closing an object.
    assert record["content"].splitlines()[24].strip() == "]"
    gold_reference = reference(case, LIMITS)
    assert gold_reference["result"]["status"] == "OPTIMAL"
    monkeypatch.setattr(solver_augmented, "solve", lambda *_: pytest.fail("Malformed JSON must not be solved"))
    result = replay_response(case, record)
    assert result.status == "INVALID_OUTPUT"
    assert result.extracted_spec is result.schedule is result.solve_result is None
    assert result.schema_diagnostics[0].code == "invalid_json"
    assert result.schema_diagnostics[0].path == "$"
    assert "solver_seconds" not in dict(result.timings)
    row = evaluate(case, result, gold_reference)
    assert row["gold_label"] == "SAT" and row["accepted"] is False
    assert row["category"] == "invalid_output"
    assert row["extraction_comparison"] is row["solver_status"] is None
