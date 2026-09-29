"""Deterministic, read-only explanations. Never infer, solve or repair an answer.

Solver facts apply only to the specification it received. Gold checks are a
separate evaluator section, never information supplied to either model path.
"""

from collections.abc import Mapping
from datetime import datetime, timedelta
import math

from scheduling.schema import (
    PipelineResult,
    PreferredStart,
    ProblemSpec,
    RepairContext,
    Schedule,
    SolveResult,
    to_data,
)
from scheduling.validation import participant_disruption, validate_schedule

_OBJECTIVES = {
    "moved_count": "minimum moved count",
    "total_shift_slots": "minimum total shift",
    "preference_penalty": "minimum preference penalty",
}


def schedule_details(
    spec: ProblemSpec, schedule, context: RepairContext | None = None
) -> dict:
    """Describe a candidate using the supplied spec; validate before burden claims."""
    checked = validate_schedule(spec, schedule, context)
    result = {
        "validation": to_data(checked),
        "activities": [],
        "preferences": [],
        "moved_activity_ids": [],
        "participant_burden": None,
    }
    if not checked.structural_valid:
        return result
    candidate = (
        schedule if isinstance(schedule, Schedule) else Schedule.from_list(schedule)
    )
    starts = candidate.starts()
    old = context.original_schedule.starts() if context else {}
    origin = datetime.fromisoformat(spec.horizon_start)

    def instant(slot):
        return (origin + timedelta(minutes=spec.slot_minutes * slot)).isoformat(
            timespec="minutes"
        )

    for activity in sorted(spec.activities, key=lambda a: a.id):
        start = starts[activity.id]
        before = old.get(activity.id)
        result["activities"].append(
            {
                "activity_id": activity.id,
                "start_slot": start,
                "start": instant(start),
                "end": instant(start + activity.duration_slots),
                "old_start": instant(before) if before is not None else None,
                "old_end": (
                    instant(before + activity.duration_slots)
                    if before is not None
                    else None
                ),
                "shift_slots": start - before if before is not None else None,
            }
        )
        if before is not None and before != start:
            result["moved_activity_ids"].append(activity.id)
    for rule in sorted(spec.constraints, key=lambda r: r.id):
        if isinstance(rule, PreferredStart):
            violated = not rule.start <= starts[rule.activity_id] < rule.end
            result["preferences"].append(
                {
                    "constraint_id": rule.id,
                    "activity_id": rule.activity_id,
                    "start_window": [rule.start, rule.end],
                    "weight": rule.weight,
                    "violated": violated,
                    "penalty": rule.weight if violated else 0,
                }
            )
    if context and checked.hard_feasible:
        result["participant_burden"] = {
            key: {
                **value,
                "total_shift_minutes": value["total_shift_slots"] * spec.slot_minutes,
            }
            for key, value in sorted(
                participant_disruption(spec, candidate, context).items()
            )
        }
    return result


_SOLVER_STATUSES = {"OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID"}


def _check_saved_solver(data):
    required = {
        "status",
        "last_solver_status",
        "schedule",
        "stages",
        "optimality_proven",
    }
    if (
        not required <= data.keys()
        or not isinstance(data["status"], str)
        or data["status"] not in _SOLVER_STATUSES
        or not isinstance(data["last_solver_status"], str)
        or data["last_solver_status"] not in _SOLVER_STATUSES
        or type(data["optimality_proven"]) is not bool
        or not isinstance(data["stages"], (list, tuple))
        or not isinstance(data.get("diagnostics", []), (list, tuple))
        or any(not isinstance(item, str) for item in data.get("diagnostics", []))
    ):
        raise ValueError("Saved solver result has invalid or missing fields")
    fields = {"objective", "solver_status", "value", "best_bound", "proven_optimal"}
    for stage in data["stages"]:
        if (
            not isinstance(stage, Mapping)
            or not fields <= stage.keys()
            or not isinstance(stage["objective"], str)
            or stage["objective"] not in _OBJECTIVES
            or not isinstance(stage["solver_status"], str)
            or stage["solver_status"] not in _SOLVER_STATUSES
            or type(stage["proven_optimal"]) is not bool
            or any(
                value is not None
                and (type(value) not in (int, float) or not math.isfinite(value))
                for value in (stage["value"], stage["best_bound"])
            )
        ):
            raise ValueError("Saved solver stage has invalid or missing fields")


def explain_solver(
    spec: ProblemSpec,
    result: SolveResult | Mapping,
    context: RepairContext | None = None,
    *,
    scope: str = "supplied_specification",
) -> dict:
    """Format recorded proof stages; exact claims require a matching proven prefix."""
    if scope not in ("supplied_specification", "extracted_specification"):
        raise ValueError("Explicit solver evidence scope required")
    data = to_data(result) if isinstance(result, SolveResult) else dict(result)
    _check_saved_solver(data)
    status = data["status"]
    details = (
        schedule_details(spec, data["schedule"], context)
        if data.get("schedule") is not None
        else None
    )
    valid = (
        status in ("OPTIMAL", "FEASIBLE")
        and details is not None
        and details["validation"]["hard_feasible"]
    )
    values = details["validation"]["objectives"] if valid else {}
    names = (
        ["moved_count", "total_shift_slots", "preference_penalty"]
        if spec.task_type == "repair"
        else ["preference_penalty"]
    )
    stages, proven = [], []
    for index, stage in enumerate(data["stages"]):
        name = stage["objective"]
        exact = (
            valid
            and len(proven) == index
            and index < len(names)
            and name == names[index]
            and stage["solver_status"] == "OPTIMAL"
            and stage["proven_optimal"] is True
            and stage["value"] == stage["best_bound"] == values[name]
        )
        if exact:
            proven.append(name)
        stages.append({**stage, "usable_exact_proof": bool(exact)})
    complete = (
        len(proven) == len(names) == len(stages)
        and data["optimality_proven"] is True
        and status == "OPTIMAL"
    )
    if status == "INFEASIBLE":
        summary = "Solver reports infeasibility for this specification. No detailed conflict was derived."
    elif status == "UNKNOWN":
        summary = "Solver did not determine feasibility; UNKNOWN is not an infeasibility proof."
    elif status == "MODEL_INVALID":
        summary = (
            "Solver model error; no feasibility or optimality conclusion is available."
        )
    elif not valid:
        summary = "Recorded candidate fails specification validation; no optimality claim is made."
    elif complete:
        summary = (
            "All required objective stages are proven optimal for this specification."
        )
    else:
        summary = "A feasible incumbent is available; full optimality is not proven."
    return {
        "scope": scope,
        "status": status,
        "last_solver_status": data["last_solver_status"],
        "summary": summary,
        "optimality_proven": complete,
        "proven_objectives": proven,
        "unproven_objectives": [name for name in names if name not in proven],
        "stages": stages,
        "schedule": details,
        "diagnostics": list(data.get("diagnostics", ())),
    }


def explain_case(
    case: Mapping, response: PipelineResult | Mapping | None, evaluation: Mapping | None
) -> dict:
    """Consume a checked saved case and recomputed evaluation, without new calls."""
    spec = ProblemSpec.from_dict(case["problem"])
    context = (
        RepairContext(Schedule.from_list(case["original_schedule"]))
        if case.get("original_schedule") is not None
        else None
    )
    data = (
        to_data(response)
        if isinstance(response, PipelineResult)
        else dict(response) if response is not None else None
    )
    result = {
        "format_version": "1.0",
        "case_id": case["case_id"],
        "model": None,
        "solver": None,
        "evaluation": None,
    }
    if data is None:
        result["model"] = {
            "status": "NOT_COMPLETED",
            "summary": "No completed response is available.",
            "diagnostics": [evaluation["category"]] if evaluation else [],
        }
        return result
    if data["instance_id"] != case["case_id"]:
        raise ValueError("Case and result identities differ")
    status, approach = data["status"], data["approach"]
    messages = {
        "SAT": "A schedule was returned; independent validation determines acceptance.",
        "UNSAT": (
            "The direct model predicts infeasibility; this is not a solver proof."
            if approach == "direct"
            else "The extracted problem was reported infeasible."
        ),
        "UNKNOWN": "No conclusive answer was returned; this is not UNSAT.",
        "INVALID_OUTPUT": "Output parsing/schema validation failed; no corrected answer was substituted.",
        "ERROR": "Execution failed; no scheduling conclusion is available.",
    }
    if status not in messages or approach not in ("direct", "solver_augmented"):
        raise ValueError("Unsupported pipeline result")
    result["model"] = {
        "approach": approach,
        "status": status,
        "declared_status": data.get("declared_status"),
        "summary": messages[status],
        "diagnostics": list(data.get("diagnostics", ())),
    }
    if data.get("solve_result") is not None:
        if approach != "solver_augmented" or data.get("extracted_spec") is None:
            raise ValueError("Solver proof requires its extracted specification")
        result["solver"] = explain_solver(
            ProblemSpec.from_dict(data["extracted_spec"]),
            data["solve_result"],
            context,
            scope="extracted_specification",
        )
    if evaluation is not None:
        if (
            any(evaluation[key] != data[key] for key in ("approach", "variant_id"))
            or evaluation["case_id"] != case["case_id"]
        ):
            raise ValueError("Evaluation and result identities differ")
        accepted = evaluation["accepted"]
        summary = (
            "Accepted against gold."
            if accepted is True
            else (
                "Rejected against gold."
                if accepted is False
                else "Gold reference unresolved; not scored as accepted or rejected."
            )
        )
        result["evaluation"] = {
            "scope": "evaluator_only_gold",
            "summary": summary,
            "gold_label": evaluation["gold_label"],
            "accepted": accepted,
            "category": evaluation["category"],
            "objective_gaps": evaluation["objective_gaps"],
            "reference_proven_stages": evaluation["reference_proven_stages"],
            "extraction_comparison": evaluation["extraction_comparison"],
            "schedule": (
                schedule_details(spec, data["schedule"], context)
                if data.get("schedule") is not None
                else None
            ),
        }
    return result


def render_text(explanation: Mapping) -> str:
    """One shared presentation formatter; raw model text is never executed/rendered."""
    lines = [f"Case: {explanation.get('case_id', 'supplied specification')}"]
    model = explanation.get("model")
    if model:
        lines += [f"Model outcome: {model['status']}", model["summary"]]
        lines += [f"Diagnostic: {item}" for item in model.get("diagnostics", ())]
    for section in ("solver", "evaluation"):
        block = explanation.get(section)
        if not block:
            continue
        lines += ["", f"Scope: {block['scope']}", block["summary"]]
        if section == "solver":
            lines.append(
                f"Solver status: {block['status']}; last stage: {block['last_solver_status']}"
            )
            for stage in block["stages"]:
                proof = "proven" if stage["usable_exact_proof"] else "unproven"
                lines.append(
                    f"Stage {stage['objective']}: {stage['solver_status']}; value={stage['value']}; bound={stage['best_bound']}; {proof}"
                )
            for name in block["proven_objectives"]:
                lines.append(f"Established: {_OBJECTIVES[name]}.")
            for name in block["unproven_objectives"]:
                lines.append(f"Not established: {_OBJECTIVES[name]}.")
            lines.extend(f"Diagnostic: {item}" for item in block["diagnostics"])
            if block["scope"] == "extracted_specification":
                lines.append(
                    "This solver proof does not establish faithful extraction or correctness against the original request."
                )
        else:
            lines.append(
                f"Gold label: {block['gold_label']}; category: {block['category']}"
            )
            lines.append(
                f"Conditional objective gaps: {block['objective_gaps']} (null means unavailable)."
            )
            comparison = block["extraction_comparison"]
            if comparison is not None:
                lines.append(
                    f"Extraction structurally equivalent: {comparison['structurally_equivalent']}; semantic review is separate."
                )
        details = block["schedule"]
        if not details:
            continue
        checked = details["validation"]
        lines.append(
            f"Candidate hard-feasible in this scope: {checked['hard_feasible']}"
        )
        for row in details["activities"]:
            before = (
                f"{row['old_start']} – {row['old_end']} -> " if row["old_start"] else ""
            )
            shift = (
                f"; shift={row['shift_slots']:+d} slots"
                if row["shift_slots"] is not None
                else ""
            )
            lines.append(
                f"{row['activity_id']}: {before}{row['start']} – {row['end']}{shift}"
            )
        objectives = checked["objectives"]
        if objectives is not None:
            qualifier = (
                ""
                if checked["hard_feasible"]
                else " (invalid candidate; diagnostic only)"
            )
            if objectives["moved_count"] is not None:
                lines.append(
                    f"(M,T,P) = ({objectives['moved_count']}, {objectives['total_shift_slots']}, {objectives['preference_penalty']}){qualifier}"
                )
                lines.append(
                    "Moved activities: "
                    + (", ".join(details["moved_activity_ids"]) or "none")
                )
            else:
                lines.append(
                    f"Preference penalty: {objectives['preference_penalty']}{qualifier}"
                )
        for rule in details["preferences"]:
            lines.append(
                f"Preference {rule['constraint_id']} ({rule['activity_id']}): start window [{rule['start_window'][0]}, {rule['start_window'][1]}), weight={rule['weight']}, penalty={rule['penalty']}"
            )
        for violation in checked["violations"]:
            lines.append(
                f"Violation {violation['category']}: {', '.join(violation['activity_ids'])}; constraint={violation['constraint_id']}"
            )
        if details["participant_burden"] is not None:
            lines.append(
                "Participant inconvenience (fixed assignments; shared events count for each participant):"
            )
            for key, burden in details["participant_burden"].items():
                lines.append(
                    f"{key}: {burden['moved_count']} moved events, {burden['total_shift_minutes']} minutes total absolute shift"
                )
            lines.append("These counts do not establish fair workload allocation.")
    return "\n".join(lines) + "\n"
