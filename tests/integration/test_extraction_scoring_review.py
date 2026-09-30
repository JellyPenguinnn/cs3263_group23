"""Reviewer regressions: extraction fidelity never replaces independent gold scoring."""

from dataclasses import replace

import pytest
from scheduling.evaluation.benchmark import generate_development_v3, render
from scheduling.evaluation.scoring import evaluate, reference
from scheduling.pipelines.solver_augmented import (
    PUBLIC_REQUEST_ID,
    run_solver_augmented,
)
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import Window
from scheduling.solver import SolverLimits
from tests.unit.test_availability_extraction_review import CHANGES, change_windows


@pytest.fixture(scope="module")
def cases():
    return {c.case_id: c for c in generate_development_v3(3265)[0]}


@pytest.mark.parametrize("case_id,changes,false_sat", CHANGES)
def test_observed_window_errors_keep_gold_and_fidelity_separate(
    cases, case_id, changes, false_sat
):
    case = cases[case_id]
    raw = replace(
        change_windows(case.problem, changes), instance_id=PUBLIC_REQUEST_ID
    ).to_json()
    result = run_solver_augmented(
        render(case),
        ModelConfig("offline", 8192),
        SolverLimits(10),
        provider_complete=lambda *_: ModelResponse(raw, "canned", 0, ()),
    )
    row = evaluate(case, result, reference(case, SolverLimits(10)))
    assert row["gold_label"] == "UNSAT"
    assert row["category"] == ("gold_invalid_schedule" if false_sat else "accepted")
    assert row["accepted"] is (not false_sat)
    assert not row["extraction_comparison"]["structurally_equivalent"]
    assert row["objective_gaps"] == [None, None, None]
    assert result.model_response.content == raw


def test_redundant_participant_window_is_success_but_still_structural_mismatch(cases):
    case = cases["dev-v3-8c76290cef6036f833b5a4ba-repair"]
    altered = replace(
        case.problem,
        instance_id=PUBLIC_REQUEST_ID,
        participants=tuple(
            replace(p, availability=(Window(2, 48),)) if p.id == "P0" else p
            for p in case.problem.participants
        ),
    )
    raw = altered.to_json()
    result = run_solver_augmented(
        render(case),
        ModelConfig("offline", 8192),
        SolverLimits(10),
        provider_complete=lambda *_: ModelResponse(raw, "canned", 0, ()),
    )
    row = evaluate(case, result, reference(case, SolverLimits(10)))
    assert row["accepted"] and row["gold_valid"]
    assert row["objective_values"] == (5, 16, 19)
    assert row["objective_gaps"] == [0, 0, 0]
    assert row["extraction_comparison"]["mismatches"] == ["participants"]
    assert not row["extraction_comparison"]["structurally_equivalent"]
