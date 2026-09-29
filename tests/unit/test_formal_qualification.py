"""Richer bounded mathematics, independently enumerated without compiler helpers."""

from dataclasses import replace
from itertools import product
import random

import pytest

from scheduling.schema import (
    Activity,
    BlockedInterval,
    Entity,
    FixedStart,
    Precedence,
    PreferredStart,
    ProblemSpec,
    RepairCase,
    RepairContext,
    Schedule,
    Window,
)
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule
from tests.formal_support import enumerate_answers


def schedule(starts):
    return Schedule.from_list(
        [{"activity_id": key, "start_slot": value} for key, value in starts.items()]
    )


def problem(activities, constraints=(), horizon=5, participants=(), resources=()):
    return ProblemSpec(
        "1.0",
        "qualification",
        "generation",
        horizon,
        30,
        "2026-10-05T09:00:00+08:00",
        "+08:00",
        participants,
        resources,
        tuple(activities),
        tuple(constraints),
    )


def cross_check(spec, old=None):
    context = RepairContext(schedule(old)) if old is not None else None
    answers = enumerate_answers(spec, old)
    feasible = {tuple(starts[a.id] for a in spec.activities) for _, starts in answers}
    # Check every assignment, not only the solver's winning witness.
    for times in product(range(spec.horizon_slots), repeat=len(spec.activities)):
        checked = validate_schedule(
            spec, schedule(dict(zip((a.id for a in spec.activities), times))), context
        )
        assert checked.hard_feasible == (times in feasible)
    result = solve(spec, SolverLimits(), context)
    if not answers:
        assert result.status == "INFEASIBLE" and result.schedule is None
    else:
        best = min(value for value, _ in answers)
        assert result.status == "OPTIMAL" and result.optimality_proven
        assert result.objectives.as_tuple() == best
        assert (best, result.schedule.starts()) in answers
        assert all(s.value == s.best_bound and s.proven_optimal for s in result.stages)
    return result, answers


def test_coupled_repair_requires_moving_unaffected_activities():
    spec = problem(
        [
            Activity("A", 1, ("P",), ("R",), (Window(0, 2),)),
            Activity("B", 1, (), ("R",), (Window(1, 3),)),
            Activity("C", 1, (), ("R",), (Window(0, 3),)),
        ],
        horizon=3,
        participants=(Entity("P", (Window(0, 3),)),),
        resources=(Entity("R", (Window(0, 3),)),),
    )
    old = {"A": 0, "B": 1, "C": 2}
    assert validate_schedule(spec, schedule(old)).hard_feasible
    updated = replace(
        spec,
        task_type="repair",
        constraints=(BlockedInterval("event", "participant", "P", 0, 1),),
    )
    RepairCase(spec, schedule(old), "P unavailable in [0,1)", updated)
    result, answers = cross_check(updated, old)
    assert answers == [((3, 4, 0), {"A": 1, "B": 2, "C": 0})]
    assert result.schedule.starts() == {"A": 1, "B": 2, "C": 0}


def test_movement_priority_beats_smaller_total_shift():
    spec = problem(
        [
            Activity("A", 1, ("P",), ("R",), (Window(0, 2), Window(4, 5))),
            Activity("B", 1, (), ("R",), (Window(1, 3),)),
            Activity("C", 1, (), (), (Window(0, 1),)),
        ],
        participants=(Entity("P", (Window(0, 5),)),),
        resources=(Entity("R", (Window(0, 5),)),),
    )
    old = {"A": 0, "B": 1, "C": 0}
    updated = replace(
        spec,
        task_type="repair",
        constraints=(BlockedInterval("event", "participant", "P", 0, 1),),
    )
    RepairCase(spec, schedule(old), "P block", updated)
    result, answers = cross_check(updated, old)
    assert ((2, 2, 0), {"A": 1, "B": 2, "C": 0}) in answers
    assert result.objectives.as_tuple() == (1, 4, 0)


def test_preference_breaks_tied_movement_and_shift():
    spec = problem(
        [
            Activity("A", 1, ("P",), (), (Window(1, 4),)),
            Activity("B", 1, (), (), (Window(0, 1),)),
            Activity("C", 2, (), (), (Window(0, 2),)),
        ],
        participants=(Entity("P", (Window(0, 5),)),),
    )
    old = {"A": 2, "B": 0, "C": 0}
    updated = replace(
        spec,
        task_type="repair",
        constraints=(
            BlockedInterval("block", "participant", "P", 2, 3),
            PreferredStart("prefer", "A", 3, 4, 7),
        ),
    )
    result, answers = cross_check(updated, old)
    assert ((1, 1, 7), {"A": 1, "B": 0, "C": 0}) in answers
    assert result.objectives.as_tuple() == (1, 1, 0)


@pytest.mark.parametrize("seed", range(12))
def test_four_activity_asymmetric_domains_and_constraints(seed):
    rng = random.Random(seed)
    windows = (Window(0, 6),)
    activities = [
        Activity("A", 2, ("P", "Q"), ("R",), windows),
        Activity("B", 1, ("P",), (), (Window(0, 2), Window(3, 6))),
        Activity("C", 1, ("Q",), ("S",), windows),
        Activity("D", 1, (), ("R", "S"), (Window(0, 3), Window(4, 6))),
    ]
    constraints = [
        PreferredStart("p" + a.id, a.id, rng.randrange(5), 6, rng.randrange(1, 5))
        for a in activities
    ]
    if seed % 3 == 0:
        constraints += [Precedence("ac", "A", "C"), Precedence("cb", "C", "B")]
    if seed % 4 == 0:
        constraints += [FixedStart("a0", "A", 0), FixedStart("d0", "D", 0)]
    spec = problem(
        activities,
        constraints,
        6,
        (Entity("P", windows), Entity("Q", windows)),
        (Entity("R", windows), Entity("S", windows)),
    )
    _, answers = cross_check(spec)
    if answers:
        old = answers[0][1]
        updated = replace(
            spec,
            task_type="repair",
            constraints=spec.constraints + (PreferredStart("new", "B", 5, 6, 8),),
        )
        repaired, _ = cross_check(updated, old)
        assert (
            repaired.objectives.moved_count
            == repaired.objectives.total_shift_slots
            == 0
        )
