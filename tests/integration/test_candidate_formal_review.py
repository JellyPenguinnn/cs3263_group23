"""Exact development fixtures; no model calls, new cases or human approvals."""

from dataclasses import replace
from itertools import product
import json
from pathlib import Path

import pytest

from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.scoring import digest
from scheduling.schema import Schedule
from scheduling.solver import SolverLimits, solve
from tests.candidate_review import review_case, review_packet, unary_domains
from tests.formal_support import assignment_objective

ROOT = Path(__file__).resolve().parents[2]
CASES = load_cases(ROOT / "tests/examples/f3-formal-review.json")
MANIFEST = json.loads(
    (ROOT / "benchmarks/manifests/yongqing-f3-policy-pilot-20261001.json").read_text()
)
ROWS = {r["case_id"]: r for r in MANIFEST["cases"]}


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.case_id)
def test_preserved_candidate_gold_has_independent_mathematical_support(case):
    assert digest(case) == ROWS[case.case_id]["sha256"]
    checked = review_case(case)
    result = solve(case.problem, SolverLimits(5), case.context)
    if case.expected_label == "UNSAT":
        assert checked["contradiction"]["mechanism"] == ROWS[case.case_id]["mechanism"]
        assert result.status == "INFEASIBLE"
        # Removing the disruptive event restores a feasible original witness.
        repair = next(c for c in CASES if c.group_id == case.group_id and c.context)
        relaxed = replace(
            case.problem,
            constraints=tuple(c for c in case.problem.constraints if c.id != "event"),
        )
        assert (
            assignment_objective(relaxed, repair.original_schedule.starts()) is not None
        )
        with pytest.raises(ValueError, match="no independent"):
            review_case(replace(case, problem=relaxed))
    else:
        assert (
            result.optimality_proven
            and result.objectives.as_tuple() == case.expected_objective
        )
        assert (
            assignment_objective(
                case.problem,
                result.schedule.starts(),
                case.original_schedule.starts() if case.context else None,
            )
            == case.expected_objective
        )


def test_exhaustive_coupled_repair_and_budget_boundary():
    case = next(
        c
        for c in CASES
        if c.context and c.expected_label == "SAT" and c.event == "fixed_start"
    )
    result = review_case(case)
    assert result["optimality_check"] == "exhaustive"
    assert result["optimum"] == (2, 2, 12)
    capped = review_case(case, 1)
    assert capped["optimality_check"] == "not_checked_assignment_cap"
    assert "optimum" not in capped


def test_valid_but_suboptimal_witness_is_not_a_proof():
    case = next(
        c
        for c in CASES
        if c.context and len(c.problem.activities) == 4 and c.expected_label == "SAT"
    )
    domains = unary_domains(case.problem)
    for times in product(*domains.values()):
        starts = dict(zip(domains, times))
        value = assignment_objective(
            case.problem, starts, case.original_schedule.starts()
        )
        if value is not None and value > case.expected_objective:
            worse = replace(
                case,
                witness=Schedule.from_list(
                    [
                        {"activity_id": key, "start_slot": slot}
                        for key, slot in starts.items()
                    ]
                ),
                expected_objective=value,
            )
            with pytest.raises(ValueError, match="exhaustive"):
                review_case(worse)
            break
    else:
        pytest.fail("Fixture must admit a worse feasible schedule")


def test_partial_or_altered_packet_cannot_receive_complete_review():
    with pytest.raises(ValueError, match="complete packet"):
        review_packet(CASES, MANIFEST)
    subset = {
        **MANIFEST,
        "case_count": len(CASES),
        "cases": [ROWS[c.case_id] for c in CASES],
    }
    changed = (replace(CASES[0], justification="altered evidence"), *CASES[1:])
    with pytest.raises(ValueError, match="unchanged"):
        review_packet(changed, subset)


@pytest.mark.parametrize("cap", [-1, True, 200001])
def test_review_cap_is_explicit_and_bounded(cap):
    with pytest.raises(ValueError, match="cap"):
        review_case(CASES[0], cap)
