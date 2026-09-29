"""Formal-core objective arithmetic, not independent gold validation."""

from scheduling.schema import ObjectiveValues, PreferredStart, ProblemSpec, RepairContext, Schedule, SchemaError


def check_repair_context(spec: ProblemSpec, context: RepairContext | None) -> None:
    if spec.task_type == "repair":
        if not isinstance(context, RepairContext):
            raise SchemaError("Repair solve requires RepairContext")
        context.original_schedule.require_ids(tuple(a.id for a in spec.activities))
        if any(start >= spec.horizon_slots for start in context.original_schedule.starts().values()):
            raise SchemaError("Original start outside common horizon")
    elif context is not None:
        raise SchemaError("Generation must not receive RepairContext")


def measure_objectives(spec: ProblemSpec, schedule: Schedule,
                       repair_context: RepairContext | None = None) -> ObjectiveValues:
    """Measure returned solver objectives; evaluator must recompute independently."""
    check_repair_context(spec, repair_context)
    schedule.require_ids(tuple(a.id for a in spec.activities))
    starts = schedule.starts()
    penalty = sum(c.weight for c in spec.constraints if isinstance(c, PreferredStart)
                  and not c.start <= starts[c.activity_id] < c.end)
    if repair_context is None:
        return ObjectiveValues(penalty)
    old = repair_context.original_schedule.starts()
    return ObjectiveValues(penalty, sum(starts[key] != old[key] for key in starts),
                           sum(abs(starts[key] - old[key]) for key in starts))
