"""Finite semantic counterexamples for the three v3 development mismatches.

These deterministic mutations reproduce the observed field changes, not raw live
answers. Gold restoration is diagnostic-only and never used by either pipeline.
"""

from dataclasses import replace
from itertools import product

import pytest

from scheduling.evaluation.benchmark import generate_development_v3, render
from scheduling.extraction_diagnostics import compare_specifications
from scheduling.pipelines.solver_augmented import (
    PUBLIC_REQUEST_ID,
    run_solver_augmented,
)
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import Schedule, Window
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule
from tests.formal_support import assignment_objective


CHANGES = (
    (
        "dev-v3-d9a5c7aa60e26500e2852c5f-repair",
        {"A0": ((42, 48),), "A1": ((39, 48),)},
        True,
    ),
    ("dev-v3-246eabff6bb1ff745a7bfbfc-repair", {"A4": ((5, 6), (6, 7))}, True),
    (
        "dev-v3-66dd6c3548fb70d23bad6865-repair",
        {"A1": ((6, 10),), "A2": ((8, 12),)},
        False,
    ),
)


@pytest.fixture(scope="module")
def cases():
    return {c.case_id: c for c in generate_development_v3(3265)[0]}


def own_window_starts(spec, activity):
    return {
        s
        for s in range(spec.horizon_slots)
        if any(
            w.start <= s and s + activity.duration_slots <= w.end
            for w in activity.availability
        )
    }


def feasible_assignments(spec, old):
    # Availability is a necessary condition. Enumerate its full Cartesian
    # product; independent arithmetic checks every other rule and objective.
    domains = [sorted(own_window_starts(spec, a)) for a in spec.activities]
    answers = []
    for values in product(*domains):
        starts = dict(zip((a.id for a in spec.activities), values))
        objective = assignment_objective(spec, starts, old)
        if objective is not None:
            answers.append((objective, starts))
    return answers


def change_windows(spec, changes):
    return replace(
        spec,
        activities=tuple(
            (
                replace(a, availability=tuple(Window(*w) for w in changes[a.id]))
                if a.id in changes
                else a
            )
            for a in spec.activities
        ),
    )


@pytest.mark.parametrize("case_id,changes,has_false_sat", CHANGES)
def test_availability_changes_have_independent_semantic_certificates(
    cases, case_id, changes, has_false_sat
):
    case = cases[case_id]
    gold, old = case.problem, case.original_schedule.starts()
    altered = change_windows(gold, changes)
    assert not feasible_assignments(gold, old)
    answers = feasible_assignments(altered, old)
    assert bool(answers) == has_false_sat
    differences = compare_specifications(gold, altered)
    assert differences.mismatches == ("activities",)
    assert {d.path for d in differences.differences} == {
        f'$.activities[id="{key}"].availability' for key in changes
    }
    for before, after in zip(gold.activities, altered.activities):
        if before.id in changes:
            assert own_window_starts(gold, before) < own_window_starts(altered, after)
    result = solve(altered, SolverLimits(10), case.context)
    assert result.status == ("OPTIMAL" if has_false_sat else "INFEASIBLE")
    if answers:
        assert result.objectives.as_tuple() == min(obj for obj, _ in answers)
        for _, starts in answers:
            schedule = Schedule.from_list(
                [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
            )
            assert validate_schedule(altered, schedule, case.context).hard_feasible
            assert not validate_schedule(gold, schedule, case.context).hard_feasible
    # Canned extraction must preserve the erroneous windows, not repair using gold.
    raw = replace(altered, instance_id=PUBLIC_REQUEST_ID).to_json()
    pipeline = run_solver_augmented(
        render(case),
        ModelConfig("offline", 8192),
        SolverLimits(10),
        provider_complete=lambda *_: ModelResponse(raw, "canned", 0, ()),
    )
    assert pipeline.extracted_spec == altered
    assert pipeline.model_response.content == raw
    assert pipeline.status == ("SAT" if has_false_sat else "UNSAT")
    assert pipeline.instance_id == case_id


def test_single_field_restoration_attributes_resource_case_failure(cases):
    case_id, changes, _ = CHANGES[0]
    case = cases[case_id]
    # Isolate A0 merging from A1 expansion instead of attributing both by association.
    a0_only = change_windows(case.problem, {"A0": changes["A0"]})
    a1_only = change_windows(case.problem, {"A1": changes["A1"]})
    assert not feasible_assignments(a0_only, case.original_schedule.starts())
    assert feasible_assignments(a1_only, case.original_schedule.starts())
