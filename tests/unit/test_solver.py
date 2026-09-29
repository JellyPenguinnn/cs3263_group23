from dataclasses import replace
import random

import pytest
from ortools.sat.python import cp_model

from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, Precedence, PreferredStart,
    ReleaseTime, RepairContext, Schedule, SchemaError, Window,
)
from scheduling.solver import SolverLimits, solve
import scheduling.solver as implementation
from tests.formal_support import enumerate_answers, tiny


def old_context():
    return RepairContext(Schedule.from_list([{"activity_id": "A", "start_slot": 0}, {"activity_id": "B", "start_slot": 2}]))


def assert_matches_enumeration(spec, context=None):
    old = context.original_schedule.starts() if context else None
    answers = enumerate_answers(spec, old)
    result = solve(spec, SolverLimits(), context)
    if not answers:
        assert result.status == "INFEASIBLE" and result.schedule is None
    else:
        assert result.status == "OPTIMAL" and result.optimality_proven
        expected = min(objective for objective, _ in answers)
        assert result.objectives.as_tuple() == expected
        assert (expected, result.schedule.starts()) in answers
        assert all(stage.proven_optimal and stage.value == stage.best_bound for stage in result.stages)
    return result


@pytest.mark.parametrize("constraints", [
    (), (Precedence("p", "A", "B"),),
    (FixedStart("a", "A", 0), FixedStart("b", "B", 0)),
    (ReleaseTime("r", "A", 3), Deadline("d", "A", 1)),
    (Precedence("p", "A", "B"), Deadline("d", "B", 1)),
    (BlockedInterval("b", "resource", "R", 0, 3),),
    (PreferredStart("a", "A", 0, 1, 1), PreferredStart("b", "B", 0, 1, 3)),
])
def test_tiny_feasibility_and_preferences(constraints):
    assert_matches_enumeration(tiny(constraints=constraints))


def test_resource_alone_prevents_overlap():
    spec = tiny(constraints=(FixedStart("a", "A", 0), FixedStart("b", "B", 0)))
    spec = replace(spec, activities=tuple(replace(a, participant_ids=()) for a in spec.activities))
    assert assert_matches_enumeration(spec).status == "INFEASIBLE"


def test_all_participants_and_gap_containment():
    spec = tiny()
    people = (Entity("P", (Window(0, 1), Window(2, 4))), Entity("Q", (Window(2, 4),)))
    activity = Activity("A", 2, ("P", "Q"), (), (Window(0, 4),))
    spec = replace(spec, participants=people, activities=(activity,))
    assert assert_matches_enumeration(spec).schedule.starts() == {"A": 2}
    spec = replace(spec, participants=(Entity("P", (Window(0, 1), Window(1, 2))), people[1]))
    assert assert_matches_enumeration(spec).status == "INFEASIBLE"


def test_empty_availability_is_unsat_not_schema_failure():
    assert assert_matches_enumeration(replace(tiny(), resources=(Entity("R", ()),))).status == "INFEASIBLE"


def test_noop_repair_preserves_old_even_if_preferences_would_improve():
    spec = tiny(task_type="repair", constraints=(PreferredStart("p", "A", 1, 2, 10),))
    result = assert_matches_enumeration(spec, old_context())
    assert result.objectives.as_tuple() == (0, 0, 10)
    assert result.schedule == old_context().original_schedule


def test_blocked_interval_repair_lower_bound():
    spec = tiny(task_type="repair", constraints=(BlockedInterval("b", "participant", "P", 0, 1), Precedence("p", "A", "B")))
    result = assert_matches_enumeration(spec, old_context())
    assert result.objectives.as_tuple() == (1, 1, 0)
    assert result.schedule.starts() == {"A": 1, "B": 2}


@pytest.mark.parametrize("seed", range(60))
def test_seeded_exhaustive_generation_and_repair(seed):
    rng = random.Random(seed)
    constraints = [PreferredStart("pa", "A", rng.randrange(4), 4, rng.randrange(6)),
                   PreferredStart("pb", "B", rng.randrange(4), 4, rng.randrange(6))]
    if rng.choice((True, False)):
        constraints.append(ReleaseTime("r", rng.choice(("A", "B")), rng.randrange(5)))
    if rng.choice((True, False)):
        constraints.append(Deadline("d", rng.choice(("A", "B")), rng.randrange(5)))
    if rng.choice((True, False)):
        constraints.append(FixedStart("f", rng.choice(("A", "B")), rng.randrange(4)))
    if rng.choice((True, False)):
        constraints.append(Precedence("p", "A", "B"))
    if rng.choice((True, False)):
        constraints.append(BlockedInterval("b", rng.choice(("participant", "resource")), "P" if seed % 2 else "R", 0, 1))
        # Keep target namespace consistent, independently of random constraint mixes.
        constraints[-1] = replace(constraints[-1], target_id="P" if constraints[-1].target_kind == "participant" else "R")
    spec = tiny(constraints=constraints)
    assert_matches_enumeration(spec)
    assert_matches_enumeration(replace(spec, task_type="repair"), old_context())


def test_missing_or_wrong_context_rejected():
    with pytest.raises(SchemaError):
        solve(tiny(task_type="repair"), SolverLimits())
    with pytest.raises(SchemaError):
        solve(tiny(), SolverLimits(), old_context())


def test_zero_budget_means_unknown_without_proof():
    result = solve(tiny(), SolverLimits(time_limit_seconds=0))
    assert result.status == "UNKNOWN" and result.schedule is None and not result.optimality_proven


def test_later_unknown_retains_feasible_incumbent(monkeypatch):
    real = cp_model.CpSolver
    solvers = []
    class Limited:
        def __init__(self):
            self.inner = real()
            self.parameters = self.inner.parameters
            solvers.append(self)
        def solve(self, model):
            return self.inner.solve(model) if len(solvers) == 1 else cp_model.UNKNOWN
        def status_name(self, code):
            return self.inner.status_name(code)
        def value(self, expr):
            return self.inner.value(expr)
        @property
        def best_objective_bound(self):
            return self.inner.best_objective_bound if len(solvers) == 1 else 0.0
    monkeypatch.setattr(cp_model, "CpSolver", Limited)
    result = solve(tiny(task_type="repair"), SolverLimits(), old_context())
    assert result.status == "FEASIBLE" and result.last_solver_status == "UNKNOWN"
    assert result.schedule is not None and not result.optimality_proven
    assert result.stages[0].proven_optimal and not result.stages[1].proven_optimal
    assert solvers[1].parameters.max_time_in_seconds < solvers[0].parameters.max_time_in_seconds
    assert all(s.parameters.absolute_gap_limit == 0 and s.parameters.relative_gap_limit == 0 for s in solvers)


def test_unproven_first_stage_is_never_fixed(monkeypatch):
    real = cp_model.CpSolver
    class Feasible(real):
        def solve(self, model, *args):
            assert super().solve(model, *args) == cp_model.OPTIMAL
            return cp_model.FEASIBLE
    monkeypatch.setattr(cp_model, "CpSolver", Feasible)
    result = solve(tiny(task_type="repair"), SolverLimits(), old_context())
    assert result.status == "FEASIBLE" and len(result.stages) == 1 and not result.optimality_proven


def test_model_invalid_distinct_from_infeasible(monkeypatch):
    model = cp_model.CpModel()
    model.new_int_var(2, 1, "invalid")
    monkeypatch.setattr(implementation, "_compile", lambda *_: (model, {}, [("preference_penalty", 0)]))
    assert solve(tiny(), SolverLimits()).status == "MODEL_INVALID"
