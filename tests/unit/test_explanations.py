"""Explanations preserve proof boundaries without invoking a model or solver."""

from dataclasses import replace

import pytest

from scheduling.explanations import (
    explain_case,
    explain_solver,
    render_text,
    schedule_details,
)
from scheduling.schema import (
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    ObjectiveValues,
    OptimizationStage,
    PipelineResult,
    PreferredStart,
    RepairContext,
    Schedule,
    ScheduledActivity,
    SolveResult,
    Window,
    to_data,
    solver_input_binding,
)
from scheduling.solver import SolverLimits, solve
from tests.formal_support import tiny


def schedule(a=1, b=2):
    return Schedule((ScheduledActivity("A", a), ScheduledActivity("B", b)))


def context():
    return RepairContext(schedule(0, 2))


def stage(name, value, *, status="OPTIMAL", bound=None, proven=True):
    return OptimizationStage(
        name, status, value, value if bound is None else bound, 1.0, 0.01, proven
    )


def saved_partial():
    return SolveResult(
        "FEASIBLE",
        "UNKNOWN",
        schedule(),
        ObjectiveValues(0, 1, 1),
        (
            stage("moved_count", 1),
            stage("total_shift_slots", None, status="UNKNOWN", bound=0, proven=False),
        ),
        0.1,
        False,
        ("total_time_budget_exhausted",),
    )


def test_partial_proof_retains_incumbent_but_not_shift_optimality(monkeypatch):
    spec = tiny(
        task_type="repair",
        constraints=(BlockedInterval("block", "participant", "P", 0, 1),),
    )
    monkeypatch.setattr(
        "scheduling.solver.solve", lambda *_: pytest.fail("Formatter cannot solve")
    )
    result = explain_solver(
        spec, replace(saved_partial(), input_binding=solver_input_binding(spec, context())),
        context(), scope="extracted_specification"
    )
    assert result["proven_objectives"] == ["moved_count"]
    assert result["unproven_objectives"] == ["total_shift_slots", "preference_penalty"]
    assert not result["optimality_proven"]
    assert result["schedule"]["moved_activity_ids"] == ["A"]
    assert result["schedule"]["activities"][0]["old_start"] == "2026-10-05T09:00+08:00"
    assert result["schedule"]["activities"][0]["start"] == "2026-10-05T09:30+08:00"
    text = render_text({"solver": result})
    assert "Established: minimum moved count" in text
    assert "Not established: minimum total shift" in text
    assert "does not establish faithful extraction" in text
    assert "bound=0" in text


@pytest.mark.parametrize(
    "mutation", ["bound", "order", "value", "flag", "invalid_schedule"]
)
def test_unsubstantiated_proof_is_never_promoted(mutation):
    spec = tiny(task_type="repair")
    original = solve(spec, SolverLimits(), context())
    data = to_data(original)
    if mutation == "bound":
        data["stages"][0]["best_bound"] = -1
    elif mutation == "order":
        data["stages"].reverse()
    elif mutation == "value":
        data["stages"][0]["value"] = 5
    elif mutation == "flag":
        data["stages"][0]["proven_optimal"] = False
    else:
        data["schedule"] = schedule(0, 0).to_list()
    result = explain_solver(spec, data, context())
    assert not result["optimality_proven"]
    assert not result["proven_objectives"]


def test_shared_event_burden_counts_both_people_and_actual_preferences():
    spec = tiny(task_type="repair", constraints=(PreferredStart("want", "A", 0, 1, 7),))
    spec = replace(
        spec,
        participants=(Entity("P", (Window(0, 4),)), Entity("Q", (Window(0, 4),))),
        activities=(
            replace(spec.activities[0], participant_ids=("P", "Q")),
            spec.activities[1],
        ),
    )
    details = schedule_details(spec, schedule(), context())
    assert details["validation"]["objectives"] == {
        "moved_count": 1,
        "total_shift_slots": 1,
        "preference_penalty": 7,
    }
    assert details["preferences"][0]["penalty"] == 7
    assert details["participant_burden"]["P"]["total_shift_minutes"] == 30
    assert details["participant_burden"]["Q"]["total_shift_minutes"] == 30
    assert sum(b["moved_count"] for b in details["participant_burden"].values()) == 2
    assert (
        schedule_details(spec, schedule(2, 2), context())["participant_burden"] is None
    )


def test_noop_repair_and_offset_date_boundary():
    spec = replace(tiny(task_type="repair"), horizon_start="2026-10-05T22:00:00+08:00")
    original = RepairContext(schedule(0, 3))
    details = schedule_details(spec, original.original_schedule, original)
    assert details["moved_activity_ids"] == []
    assert details["activities"][1]["end"] == "2026-10-06T00:00+08:00"
    assert details["participant_burden"]["P"]["moved_count"] == 0


def case_and_row(spec, result, **updates):
    case = {"case_id": spec.instance_id, "problem": spec.to_dict()}
    row = {
        "case_id": spec.instance_id,
        "approach": result.approach,
        "variant_id": "canonical",
        "accepted": False,
        "gold_label": "SAT",
        "category": "gold_invalid_schedule",
        "objective_gaps": [None],
        "reference_proven_stages": [0],
        "extraction_comparison": None,
    }
    row.update(updates)
    return case, row


def test_extracted_optimum_does_not_override_gold_invalid_output():
    gold = tiny(constraints=(Deadline("deadline", "A", 1),))
    extracted = tiny(constraints=(PreferredStart("want", "A", 2, 3, 7),))
    solved = solve(extracted, SolverLimits())
    result = PipelineResult(
        "tiny",
        "canonical",
        "solver_augmented",
        "SAT",
        solved.schedule,
        extracted,
        solve_result=solved,
    )
    case, row = case_and_row(
        gold, result, extraction_comparison={"structurally_equivalent": False}
    )
    output = explain_case(case, result, row)
    assert output["solver"]["optimality_proven"]
    assert output["solver"]["scope"] == "extracted_specification"
    assert output["evaluation"]["accepted"] is False
    assert not output["evaluation"]["schedule"]["validation"]["hard_feasible"]
    assert "Violation deadline" in render_text(output)


@pytest.mark.parametrize("status", ["UNSAT", "UNKNOWN", "INVALID_OUTPUT", "ERROR"])
def test_model_outcomes_remain_distinct(status):
    result = PipelineResult(
        "tiny", "canonical", "direct", status, diagnostics=("saved_diagnostic",)
    )
    case, row = case_and_row(
        tiny(), result, category="false_unsat" if status == "UNSAT" else status.lower()
    )
    output = explain_case(case, result, row)
    assert output["model"]["status"] == status
    assert output["solver"] is None
    assert "saved_diagnostic" in render_text(output)
    if status == "UNSAT":
        assert "not a solver proof" in render_text(output)


@pytest.mark.parametrize("status", ["INFEASIBLE", "UNKNOWN", "MODEL_INVALID"])
def test_solver_non_sat_never_becomes_source_request_proof(status):
    saved = SolveResult(status, status, None, None, (), 0.0, False)
    output = explain_solver(tiny(), saved, scope="extracted_specification")
    assert not output["optimality_proven"]
    assert output["schedule"] is None
    text = render_text({"solver": output})
    assert "does not establish faithful extraction" in text
    if status == "INFEASIBLE":
        assert "correspondence to this specification" in text
        assert "not attributed to these inputs" in text


def test_structurally_invalid_schedule_stays_inspectable_without_burden():
    details = schedule_details(tiny(), [{"activity_id": "A", "start_slot": 0}])
    assert not details["validation"]["structural_valid"]
    assert details["activities"] == []
    assert details["participant_burden"] is None


@pytest.mark.parametrize(
    "mutation",
    ["missing_status", "stages_null", "stage_missing", "flag_string", "bound_bool"],
)
def test_malformed_saved_evidence_rejected(mutation):
    data = to_data(saved_partial())
    if mutation == "missing_status":
        del data["status"]
    elif mutation == "stages_null":
        data["stages"] = None
    elif mutation == "stage_missing":
        del data["stages"][0]["objective"]
    elif mutation == "flag_string":
        data["optimality_proven"] = "true"
    else:
        data["stages"][0]["best_bound"] = True
    with pytest.raises(ValueError, match="Saved solver"):
        explain_solver(tiny(task_type="repair"), data, context())


@pytest.mark.parametrize("field", ["value", "best_bound"])
@pytest.mark.parametrize("value", [10**400, -(10**400)])
def test_large_saved_integer_remains_inspectable_without_proof(field, value):
    spec = tiny()
    data = to_data(solve(spec, SolverLimits()))
    data["stages"][0][field] = value
    explained = explain_solver(spec, data)
    assert explained["stages"][0][field] == value
    assert not explained["optimality_proven"]
    assert not explained["stages"][0]["usable_exact_proof"]
    assert "unproven" in render_text({"solver": explained})


@pytest.mark.parametrize("budget, status", [(5, "INFEASIBLE"), (0, "UNKNOWN")])
def test_recorded_contradictions_preserve_native_status(budget, status, monkeypatch):
    spec = tiny(constraints=(Deadline("impossible", "A", 0),))
    result = solve(spec, SolverLimits(time_limit_seconds=budget))
    monkeypatch.setattr(
        "scheduling.domain_analysis.analyze_domains",
        lambda *_: pytest.fail("No recomputation"),
    )
    explained = explain_solver(spec, result, scope="extracted_specification")
    assert explained["status"] == status
    assert not explained["optimality_proven"]
    text = render_text({"solver": explained})
    assert "Recorded sufficient contradiction: empty_unary_domain" in text
    assert "not a minimum conflict" in text
    assert "does not establish faithful extraction" in text
    assert "No detailed conflict" not in explained["summary"]
    if status == "UNKNOWN":
        assert "UNKNOWN is not an infeasibility proof" in explained["summary"]
    old = to_data(result)
    old.pop("domain_analysis")
    assert explain_solver(spec, old)["domain_analysis"] is None


def test_malformed_optional_domain_diagnostics_rejected():
    spec = tiny()
    data = to_data(solve(spec, SolverLimits()))
    data["domain_analysis"]["contradictions"] = [{"code": "invented_proof"}]
    with pytest.raises(ValueError, match="domain contradiction"):
        explain_solver(spec, data)


@pytest.mark.parametrize("start", [5, 10**30])
def test_out_of_horizon_candidate_remains_explainable(start):
    details = schedule_details(tiny(), schedule(start, 2))
    assert details["validation"]["structural_valid"]
    assert not details["validation"]["hard_feasible"]
    row = details["activities"][0]
    assert row["start_slot"] == start
    assert row["start"] == f"slot {start} (outside horizon)"
    assert row["end"] == f"slot {start + 1} (outside horizon)"
    assert details["participant_burden"] is None


def test_bound_result_cannot_transfer_optimality_to_weaker_same_id_spec():
    strong = tiny(constraints=(
        PreferredStart("want", "A", 1, 2, 1), FixedStart("fix", "A", 0),
    ))
    weak = replace(strong, constraints=(strong.constraints[0],))
    recorded = solve(strong, SolverLimits())
    assert recorded.objectives.preference_penalty == 1
    assert solve(weak, SolverLimits()).objectives.preference_penalty == 0
    assert schedule_details(weak, recorded.schedule)["validation"]["hard_feasible"]
    with pytest.raises(ValueError, match="input binding"):
        explain_solver(weak, recorded)


def test_bound_result_cannot_transfer_proof_to_different_repair_context():
    spec = tiny(task_type="repair", constraints=(FixedStart("fix", "A", 1),))
    old = RepairContext(schedule(0, 2))
    changed = RepairContext(schedule(2, 2))
    recorded = solve(spec, SolverLimits(), old)
    # The same feasible candidate has the same full objective tuple under both
    # contexts; witness/objective checks alone cannot establish correspondence.
    before = schedule_details(spec, recorded.schedule, old)
    after = schedule_details(spec, recorded.schedule, changed)
    assert before["validation"]["objectives"] == after["validation"]["objectives"]
    with pytest.raises(ValueError, match="input binding"):
        explain_solver(spec, recorded, changed)


def test_stale_unsat_reasons_are_rejected_or_withheld():
    impossible = tiny(constraints=(Deadline("impossible", "A", 0),))
    recorded = to_data(solve(impossible, SolverLimits()))
    assert recorded["status"] == "INFEASIBLE"
    with pytest.raises(ValueError, match="input binding"):
        explain_solver(tiny(), recorded)
    del recorded["input_binding"]
    legacy = explain_solver(tiny(), recorded)
    assert legacy["input_correspondence"] == "unverified_legacy_inputs"
    assert legacy["domain_analysis"] is None
    assert legacy["diagnostics"] == []
    text = render_text({"solver": legacy})
    assert "not attributed to these inputs" in text
    assert "Applies only to this specification" not in text
    assert "Solver reports infeasibility for this specification" not in text


def test_legacy_candidate_validation_does_not_establish_optimality():
    spec = tiny()
    record = to_data(solve(spec, SolverLimits()))
    del record["input_binding"]
    explained = explain_solver(spec, record)
    assert explained["schedule"]["validation"]["hard_feasible"]
    assert not explained["optimality_proven"]
    assert explained["proven_objectives"] == []
    assert not any(s["usable_exact_proof"] for s in explained["stages"])
    assert "passes current specification validation" in explained["summary"]


def test_checked_legacy_case_retains_recorded_proof_but_cannot_bypass_binding():
    spec = tiny()
    solved = solve(spec, SolverLimits())
    result = PipelineResult("tiny", "canonical", "solver_augmented", "SAT",
                            solved.schedule, spec, solve_result=solved)
    case, row = case_and_row(spec, result)
    record = to_data(result)
    del record["solve_result"]["input_binding"]
    explained = explain_case(case, record, row)
    assert explained["solver"]["optimality_proven"]
    assert explained["solver"]["input_correspondence"] == "verified_saved_record_context"
    record["solve_result"]["input_binding"] = to_data(solved.input_binding)
    record["extracted_spec"]["constraints"] = [
        {"type": "fixed_start", "id": "fix", "activity_id": "A", "slot": 0}
    ]
    with pytest.raises(ValueError, match="input binding"):
        explain_case(case, record, row)


@pytest.mark.parametrize("binding", [{}, "unknown", {"format_version": "2.0"}])
def test_malformed_binding_is_not_treated_as_legacy(binding):
    spec = tiny()
    record = to_data(solve(spec, SolverLimits()))
    record["input_binding"] = binding
    with pytest.raises(ValueError, match="input binding"):
        explain_solver(spec, record)
