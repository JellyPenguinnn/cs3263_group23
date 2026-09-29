"""Unary reasons cover excluded starts; global conflicts still require solving."""

from dataclasses import replace
from itertools import product

import pytest

from scheduling.domain_analysis import analyze_domains
from scheduling.schema import (
    Activity,
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    Precedence,
    ReleaseTime,
    Window,
    to_data,
)
from scheduling.solver import SolverLimits, legal_starts, solve
from scheduling.validation import validate_schedule
from tests.formal_support import tiny, enumerate_answers


@pytest.mark.parametrize(
    "rule,code,expected",
    [
        (ReleaseTime("release", "A", 2), "release", (2, 3)),
        (Deadline("deadline", "A", 2), "deadline", (0, 1)),
        (FixedStart("fixed", "A", 2), "fixed_start", (2,)),
        (BlockedInterval("blocked", "participant", "P", 1, 3), "blocked", (0, 3)),
    ],
)
def test_each_unary_constraint_has_actual_provenance(rule, code, expected):
    spec = tiny(constraints=(rule,))
    row = analyze_domains(spec).domains[0]
    assert row.legal_starts == expected == legal_starts(spec, "A")
    assert row.exclusions[0].code == code
    assert row.exclusions[0].constraint_id == rule.id
    assert row.exclusions[0].path == "$.constraints[0]"
    assert set(row.exclusions[0].rejected_starts) == set(range(4)) - set(expected)


def test_gap_and_long_duration_explanations_are_checkable():
    spec = tiny()
    spec = replace(
        spec,
        activities=(replace(spec.activities[0], duration_slots=3),),
        participants=(Entity("P", (Window(0, 2), Window(2, 4))),),
    )
    result = analyze_domains(spec)
    row = result.domains[0]
    assert row.legal_starts == () and result.search_space_upper_bound == 0
    assert {e.path for e in row.exclusions} == {
        "$.participants[0].availability",
        "$.horizon_slots",
    }
    assert result.contradictions[0].code == "empty_unary_domain"
    assert solve(spec, SolverLimits()).status == "INFEASIBLE"
    assert solve(spec, SolverLimits(time_limit_seconds=0)).status == "UNKNOWN"
    # Supported analytical evidence never fabricates a native CP-SAT result.


def test_reasons_are_bounded_disjoint_and_cover_every_rejected_start():
    spec = tiny(constraints=(ReleaseTime("r", "A", 2), Deadline("d", "A", 1)))
    for row in analyze_domains(spec).domains:
        excluded = [
            start for reason in row.exclusions for start in reason.rejected_starts
        ]
        assert len(excluded) == len(set(excluded)) <= spec.horizon_slots
        assert set(excluded).isdisjoint(row.legal_starts)
        assert set(excluded) | set(row.legal_starts) == set(range(spec.horizon_slots))


@pytest.mark.parametrize("edges", [[("A", "B"), ("B", "A")], [("A", "A")]])
def test_precedence_cycle_returns_actual_closed_rule_chain(edges):
    spec = tiny(
        constraints=tuple(
            Precedence(f"edge{i}", a, b) for i, (a, b) in enumerate(edges)
        )
    )
    analysis = analyze_domains(spec)
    reason = analysis.contradictions[0]
    assert reason.code == "positive_duration_precedence_cycle"
    assert reason.activity_ids[0] == reason.activity_ids[-1]
    for before, after, cid in zip(
        reason.activity_ids, reason.activity_ids[1:], reason.constraint_ids
    ):
        rule = next(c for c in spec.constraints if c.id == cid)
        assert (rule.before, rule.after) == (before, after)
    assert all(d.legal_starts for d in analysis.domains)
    assert solve(spec, SolverLimits()).status == "INFEASIBLE"


def test_nonempty_domains_do_not_prove_sat_or_invent_conflict_reason():
    spec = tiny(constraints=(FixedStart("a", "A", 0), FixedStart("b", "B", 0)))
    analysis = analyze_domains(spec)
    assert not analysis.contradictions and analysis.search_space_upper_bound == 1
    solved = solve(spec, SolverLimits())
    assert solved.status == "INFEASIBLE"
    assert not solved.domain_analysis.contradictions


def test_analysis_never_prunes_a_feasible_independently_enumerated_assignment():
    # Gapped windows and varying precedence, duration, and shared entities.
    for duration, release, deadline in product((1, 2), range(4), range(5)):
        spec = tiny(
            constraints=(
                ReleaseTime("r", "A", release),
                Deadline("d", "B", deadline),
                Precedence("p", "A", "B"),
            )
        )
        spec = replace(
            spec,
            activities=(
                replace(spec.activities[0], duration_slots=duration),
                spec.activities[1],
            ),
        )
        analysis = analyze_domains(spec)
        domains = {d.activity_id: set(d.legal_starts) for d in analysis.domains}
        answers = enumerate_answers(spec)
        if answers:
            assert not analysis.contradictions
        for _, starts in answers:
            assert all(start in domains[key] for key, start in starts.items())
        result = solve(spec, SolverLimits())
        assert (result.status == "INFEASIBLE") == (not answers)
        assert (
            to_data(result)["domain_analysis"]["scope"] == "supplied_specification_only"
        )
