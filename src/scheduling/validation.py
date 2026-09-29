"""Independent schedule checking. Imports schema only, never solver/objectives."""

from collections import Counter
from itertools import combinations

from scheduling.schema import (
    BlockedInterval,
    Deadline,
    FixedStart,
    ObjectiveValues,
    Precedence,
    PreferredStart,
    ProblemSpec,
    ReleaseTime,
    RepairContext,
    Schedule,
    SchemaError,
    ValidationResult,
    Violation,
)


def validate_schedule(
    gold_spec: ProblemSpec,
    schedule: object,
    repair_context: RepairContext | None = None,
) -> ValidationResult:
    if not isinstance(gold_spec, ProblemSpec):
        raise TypeError("Validation requires a canonical gold specification")
    ids = tuple(a.id for a in gold_spec.activities)
    if gold_spec.task_type == "repair":
        if not isinstance(repair_context, RepairContext):
            raise SchemaError("Repair validation requires original schedule")
        repair_context.original_schedule.require_ids(ids)
    elif repair_context is not None:
        raise SchemaError("Generation must not receive repair context")
    violations = []

    def fail(category, activities=(), constraint_id=None):
        violations.append(Violation(constraint_id, category, tuple(activities)))

    rows = schedule.to_list() if isinstance(schedule, Schedule) else schedule
    if not isinstance(rows, list):
        return ValidationResult(
            False, False, (Violation(None, "malformed_schedule", ()),), None
        )
    starts = {}
    seen = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"activity_id", "start_slot"}
            or not isinstance(row["activity_id"], str)
            or not row["activity_id"].strip()
            or type(row["start_slot"]) is not int
            or row["start_slot"] < 0
        ):
            fail("malformed_entry")
            continue
        seen.append(row["activity_id"])
        starts[row["activity_id"]] = row["start_slot"]
    for key, count in Counter(seen).items():
        if count > 1:
            for _ in range(count - 1):
                fail("duplicate_activity", (key,))
    for key in sorted(set(ids) - set(seen)):
        fail("missing_activity", (key,))
    for key in sorted(set(seen) - set(ids)):
        fail("extra_activity", (key,))
    if violations:
        return ValidationResult(False, False, tuple(violations), None)
    ends = {a.id: starts[a.id] + a.duration_slots for a in gold_spec.activities}
    people = {p.id: p for p in gold_spec.participants}
    resources = {r.id: r for r in gold_spec.resources}
    for activity in gold_spec.activities:
        start, end = starts[activity.id], ends[activity.id]
        if end > gold_spec.horizon_slots:
            fail("horizon", (activity.id,))
        groups = [("activity_availability", activity.availability)]
        groups += [
            ("participant_availability", people[p].availability)
            for p in activity.participant_ids
        ]
        groups += [
            ("resource_availability", resources[r].availability)
            for r in activity.resource_ids
        ]
        for category, windows in groups:
            if not any(w.start <= start and end <= w.end for w in windows):
                fail(category, (activity.id,))
    for left, right in combinations(gold_spec.activities, 2):
        if starts[left.id] < ends[right.id] and starts[right.id] < ends[left.id]:
            if set(left.participant_ids).intersection(right.participant_ids):
                fail("participant_overlap", (left.id, right.id))
            if set(left.resource_ids).intersection(right.resource_ids):
                fail("resource_overlap", (left.id, right.id))
    penalty = 0
    for rule in gold_spec.constraints:
        if type(rule) is ReleaseTime and starts[rule.activity_id] < rule.slot:
            fail("release", (rule.activity_id,), rule.id)
        elif type(rule) is Deadline and ends[rule.activity_id] > rule.slot:
            fail("deadline", (rule.activity_id,), rule.id)
        elif type(rule) is FixedStart and starts[rule.activity_id] != rule.slot:
            fail("fixed_start", (rule.activity_id,), rule.id)
        elif isinstance(rule, Precedence) and ends[rule.before] > starts[rule.after]:
            fail("precedence", (rule.before, rule.after), rule.id)
        elif isinstance(rule, BlockedInterval):
            for activity in gold_spec.activities:
                used = (
                    activity.participant_ids
                    if rule.target_kind == "participant"
                    else activity.resource_ids
                )
                if (
                    rule.target_id in used
                    and starts[activity.id] < rule.end
                    and rule.start < ends[activity.id]
                ):
                    fail("blocked", (activity.id,), rule.id)
        elif (
            isinstance(rule, PreferredStart)
            and not rule.start <= starts[rule.activity_id] < rule.end
        ):
            penalty += rule.weight
    objectives = ObjectiveValues(penalty)
    if repair_context:
        old = repair_context.original_schedule.starts()
        objectives = ObjectiveValues(
            penalty,
            sum(starts[k] != old[k] for k in ids),
            sum(abs(starts[k] - old[k]) for k in ids),
        )
    return ValidationResult(True, not violations, tuple(violations), objectives)


def participant_disruption(
    spec: ProblemSpec, schedule: Schedule, context: RepairContext
) -> dict:
    checked = validate_schedule(spec, schedule, context)
    if not checked.hard_feasible:
        raise ValueError("Participant burden requires a valid repair")
    starts, old = schedule.starts(), context.original_schedule.starts()
    return {
        p.id: {
            "moved_count": sum(
                starts[a.id] != old[a.id]
                for a in spec.activities
                if p.id in a.participant_ids
            ),
            "total_shift_slots": sum(
                abs(starts[a.id] - old[a.id])
                for a in spec.activities
                if p.id in a.participant_ids
            ),
        }
        for p in spec.participants
    }
