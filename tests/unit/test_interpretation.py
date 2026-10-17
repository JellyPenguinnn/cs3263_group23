"""Auditable analysis must retain failures and separate symptoms from causes."""

from copy import deepcopy
from dataclasses import replace

import pytest

from scheduling.evaluation.interpretation import (
    interpret, objective_status, paired_observations, semantic_witness_check, stratified_outcomes, unit,
)
from scheduling.evaluation.study import resource_statistics


def row(case="a", approach="direct", **changes):
    return {
        "study_block": "controlled", "case_id": case, "group_id": case,
        "variant_id": "canonical", "repeat": 0, "approach": approach,
        "task_type": "repair", "level": "extreme", "sweep": "coupled_repair",
        "gold_label": "SAT", "gold_valid": True, "accepted": True,
        "pipeline_status": "SAT", "category": "accepted", "validation": None,
        "extraction_comparison": None, "objective_values": [2, 4, 0],
        "objective_gaps": [0, 0, 0], "timings": [["total_seconds", 5]],
        "usage": [], "model_seconds": None, **changes,
    }


@pytest.mark.parametrize("changes,expected", [
    ({}, "reference_match"),
    ({"objective_gaps": [1, None, None]}, "proven_suboptimal"),
    ({"objective_gaps": [0, 2, None]}, "proven_suboptimal"),
    ({"objective_gaps": [0, None, None]}, "partially_proven"),
    ({"gold_valid": False}, "not_comparable"),
    ({"gold_label": "UNSAT", "gold_valid": False}, "not_comparable"),
])
def test_lexicographic_quality_never_fills_missing_gaps(changes, expected):
    assert objective_status(row(**changes)) == expected


def test_failure_inclusive_counts_separate_acceptance_and_quality():
    rows = [row(), row("b", objective_gaps=[1, None, None]),
            row("c", category="provider_error", accepted=False, gold_valid=False),
            row("d", gold_label="UNSAT", gold_valid=False, pipeline_status="UNSAT")]
    before = deepcopy(rows)
    block = next(r for r in stratified_outcomes(rows) if r["scope"] == "block")
    assert block["accepted"] == 3 and block["attempts"] == 4
    assert block["acceptance_rate"] == .75
    assert block["gold_sat_valid"] == 2 and block["gold_sat_attempts"] == 3
    assert block["correct_unsat"] == block["gold_unsat_attempts"] == 1
    assert block["reference_matches"] == block["proven_suboptimal"] == 1
    assert block["objective_comparable"] == 2
    assert block["failure_categories"] == {"provider_error": 1}
    assert rows == before
    unresolved = stratified_outcomes([row(accepted=None, gold_label="UNRESOLVED", category="unresolved_reference")])[0]
    assert unresolved["acceptance_rate"] is None and unresolved["unscored"] == 1


def test_casebook_keeps_all_issues_and_deterministic_success_with_trace():
    rows = [row("a"), row("b"), row("c", category="provider_error", accepted=False, gold_valid=False),
            row("d", objective_gaps=[1, None, None]),
            row("e", "solver_augmented", extraction_comparison={"structurally_equivalent": False})]
    evidence = {unit(r): {"trace": {"attempt_member": r["case_id"], "attempt_sha256": "test"}} for r in rows}
    result = interpret(rows, evidence)
    assert result == interpret(list(reversed(rows)), evidence)
    assert len(result["attempt_diagnostics"]) == 5
    assert {e["identity"]["case_id"] for e in result["casebook"]} == {"a", "c", "d", "e"}
    assert all(e["human_interpretation"] == "pending" for e in result["casebook"])
    e = next(e for e in result["casebook"] if e["identity"]["case_id"] == "e")
    assert any("does not prove semantic error or causation" in s for s in e["observations"])
    c = next(e for e in result["casebook"] if e["identity"]["case_id"] == "c")
    assert "not evidence of a reasoning failure" in c["observations"][0]


def test_pairing_keeps_wording_separate_and_missing_time_unknown():
    a = row()
    b = row(approach="solver_augmented", timings=[["total_seconds", 9]])
    variant = row(variant_id="paraphrase", timings=[])
    pairs = paired_observations([a, b, variant])
    assert pairs[0]["outcome"] == "both_accepted"
    assert pairs[0]["total_seconds_B_minus_A"] == 4
    assert pairs[1]["outcome"] == "missing_method"
    assert pairs[1]["total_seconds_B_minus_A"] is None
    with pytest.raises(ValueError, match="Duplicate"):
        paired_observations([a, a])


def test_resources_reuse_timings_and_record_missingness_per_tier():
    rows = [row(), row("b", timings=[]), row("c", level="easy", usage=[{"total_tokens": 20}])]
    stats = resource_statistics(rows, group_by=("study_block", "level", "approach"))
    hard = next(s for s in stats if s["level"] == "extreme")
    assert hard["pipeline_attempts"] == hard["without_provider_records"] == 2
    assert hard["distributions"]["total_seconds"] == {
        "observations": 2, "reported": 1, "missing": 1, "mean": 5,
        "median": 5, "p95_nearest_rank": 5, "max": 5,
    }
    assert hard["distributions"]["model_seconds"]["mean"] is None
    assert hard["distributions"]["total_tokens"]["mean"] is None


def test_witness_checks_demonstrate_added_and_omitted_hard_requirements_without_search():
    from scheduling.evaluation.benchmark import tiny_fixtures
    from scheduling.schema import Deadline, to_data

    case = tiny_fixtures()[0]
    reference = {"result": {"schedule": case.witness.to_list()}}
    restricted = replace(case.problem, constraints=case.problem.constraints + (Deadline("impossible", "A", 0),))
    check = semantic_witness_check(case, {"extracted_spec": to_data(restricted)}, reference)
    assert check["hard_feasibility_difference_demonstrated"]
    assert check["checks"][0]["gold_validation"]["hard_feasible"]
    assert not check["checks"][0]["extracted_validation"]["hard_feasible"]
    weakened = replace(case.problem, activities=tuple(replace(a, participant_ids=()) for a in case.problem.activities))
    overlap = [{"activity_id": a.id, "start_slot": 0} for a in case.problem.activities]
    check = semantic_witness_check(case, {"extracted_spec": to_data(weakened), "schedule": overlap}, reference)
    assert check["hard_feasibility_difference_demonstrated"]
    assert check["checks"][0]["extracted_validation"]["hard_feasible"]
    assert not check["checks"][0]["gold_validation"]["hard_feasible"]
    same = semantic_witness_check(case, {"extracted_spec": to_data(case.problem)}, reference)
    assert not same["hard_feasibility_difference_demonstrated"]
    assert "do not establish global equivalence" in same["limitation"]
    changed_frame = replace(case.problem, horizon_slots=5)
    assert semantic_witness_check(case, {"extracted_spec": to_data(changed_frame)}, reference)["status"] == "incompatible_frame_or_activity_set"
