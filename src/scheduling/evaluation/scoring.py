"""Independent gold scoring; model claims, reference proof and validity stay separate."""

import hashlib
import json
from scheduling.evaluation.benchmark import difficulty
from scheduling.extraction_diagnostics import compare_specifications
from scheduling.schema import ProblemSpec, Schedule, SchemaError, load_json, to_data
from scheduling.validation import validate_schedule, participant_disruption


def digest(value):
    return hashlib.sha256(
        json.dumps(
            to_data(value), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def reference(case, limits):
    from scheduling.solver import solve

    result = solve(case.problem, limits, case.context)
    record = {
        "problem_sha256": digest(case.problem),
        "context_sha256": digest(case.context),
        "limits": to_data(limits),
        "result": to_data(result),
    }
    label, _, _ = check_reference(case, record)
    if (
        case.expected_label is not None
        and label != "UNRESOLVED"
        and label != case.expected_label
    ):
        raise ValueError("Reference contradicts fixture expectation")
    if (
        case.expected_objective is not None
        and result.optimality_proven
        and result.objectives.as_tuple() != case.expected_objective
    ):
        raise ValueError("Reference contradicts hand-checked objective")
    return record


def check_reference(case, reference):
    if reference["problem_sha256"] != digest(case.problem) or reference[
        "context_sha256"
    ] != digest(case.context):
        raise ValueError("Reference belongs to another problem/context")
    result = reference["result"]
    status = result["status"]
    schedule = result["schedule"]
    if status == "MODEL_INVALID":
        raise ValueError("Invalid reference compiler result; stop run")
    if status == "INFEASIBLE":
        if schedule is not None:
            raise ValueError("Infeasible reference carries a schedule")
        return "UNSAT", None, ()
    if status in ("OPTIMAL", "FEASIBLE"):
        schedule = Schedule.from_list(schedule)
        validation = validate_schedule(case.problem, schedule, case.context)
        if (
            not validation.hard_feasible
            or to_data(validation.objectives) != result["objectives"]
        ):
            raise ValueError(
                "Reference witness or objective fails independent validation"
            )
        expected_names = (
            ["moved_count", "total_shift_slots", "preference_penalty"]
            if case.context
            else ["preference_penalty"]
        )
        values = validation.objectives.as_tuple()
        proven = []
        for i, stage in enumerate(result["stages"]):
            if i >= len(expected_names) or stage["objective"] != expected_names[i]:
                raise ValueError("Reference stage order invalid")
            exact = (
                stage["solver_status"] == "OPTIMAL"
                and stage["proven_optimal"] is True
                and stage["value"] == stage["best_bound"] == values[i]
            )
            if exact and len(proven) == i:
                proven.append(i)
        if result["optimality_proven"] and len(proven) != len(expected_names):
            raise ValueError("Unsubstantiated reference optimality")
        if status == "OPTIMAL" and not result["optimality_proven"]:
            raise ValueError("Inconsistent reference status")
        return "SAT", values, tuple(proven)
    if status == "UNKNOWN" and schedule is None:
        return "UNRESOLVED", None, ()
    raise ValueError("Unsupported reference outcome")


def evaluate(case, pipeline_result, gold_reference, *, repeat=0):
    result = to_data(pipeline_result)
    if result["instance_id"] != case.case_id or result["approach"] not in (
        "direct",
        "solver_augmented",
    ):
        raise ValueError("Pipeline identity mismatch")
    status = result["status"]
    if status not in ("SAT", "UNSAT", "UNKNOWN", "INVALID_OUTPUT", "ERROR"):
        raise ValueError("Unsupported pipeline outcome")
    label, reference_values, proven = check_reference(case, gold_reference)
    validation = None
    if result.get("schedule") is not None or status == "SAT":
        validation = validate_schedule(
            case.problem, result.get("schedule"), case.context
        )
    if (
        validation is None
        and result["approach"] == "direct"
        and status == "INVALID_OUTPUT"
    ):
        response = result.get("model_response") or {}
        try:
            raw = load_json(response.get("content"))
        except SchemaError:
            raw = None
        if isinstance(raw, dict) and "schedule" in raw:
            validation = validate_schedule(case.problem, raw["schedule"], case.context)
    valid = status == "SAT" and validation is not None and validation.hard_feasible
    if label == "UNSAT" and valid:
        raise ValueError("Valid schedule contradicts UNSAT reference; stop scoring")
    objectives = validation.objectives.as_tuple() if valid else None
    gaps = [None] * (3 if case.context else 1)
    if objectives is not None and reference_values is not None:
        for i in proven:
            if all(objectives[j] == reference_values[j] for j in range(i)):
                gaps[i] = objectives[i] - reference_values[i]
                if gaps[i] < 0:
                    raise ValueError(
                        "Validated output beats proven reference; stop scoring"
                    )
    response = result.get("model_response") or {}
    attempts = response.get("attempts") or []
    comparison = None
    if result.get("extracted_spec") is not None:
        comparison = to_data(
            compare_specifications(
                case.problem, ProblemSpec.from_dict(result["extracted_spec"])
            )
        )
    if status == "ERROR":
        category = (
            "solver_model_error"
            if result.get("solve_result", {})
            and result["solve_result"]["status"] == "MODEL_INVALID"
            else "provider_error"
        )
    elif status == "INVALID_OUTPUT":
        category = "invalid_output"
    elif status == "UNKNOWN":
        category = "solver_limit" if result.get("solve_result") else "model_unknown"
    elif status == "SAT" and not valid:
        category = "gold_invalid_schedule"
    elif status == "UNSAT" and label == "SAT":
        category = "false_unsat"
    elif label == "UNRESOLVED":
        category = "unresolved_reference"
    else:
        category = "accepted"
    return {
        "case_id": case.case_id,
        "group_id": case.group_id,
        "split": case.split,
        "kind": case.kind,
        "sweep": case.sweep,
        "level": case.level,
        "task_type": case.problem.task_type,
        "variant_id": result["variant_id"],
        "repeat": repeat,
        "approach": result["approach"],
        "gold_label": label,
        "pipeline_status": status,
        "declared_status": result.get("declared_status"),
        "solver_status": (
            result["solve_result"]["status"] if result.get("solve_result") else None
        ),
        "accepted": (
            (valid or (label == "UNSAT" and status == "UNSAT"))
            if label != "UNRESOLVED"
            else None
        ),
        "gold_valid": valid,
        "validation": to_data(validation),
        "objective_values": objectives,
        "objective_gaps": gaps,
        "reference_proven_stages": proven,
        "category": category,
        "extraction_comparison": comparison,
        "participant_burden": (
            participant_disruption(
                case.problem, Schedule.from_list(result["schedule"]), case.context
            )
            if valid and case.context
            else None
        ),
        "difficulty": difficulty(case.problem),
        "model_config_sha256": result.get("config_sha256"),
        "returned_model": response.get("returned_model"),
        "request_count": len(attempts),
        "rate_limit_events": sum(a.get("http_status") == 429 for a in attempts),
        "usage": [a["usage"] for a in attempts],
        "timings": result.get("timings", []),
    }
