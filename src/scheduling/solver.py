"""Fixed CP-SAT compiler with a shared sequential lexicographic time budget."""

from dataclasses import dataclass
import math
import time

from ortools.sat.python import cp_model

from scheduling.objectives import check_repair_context, measure_objectives
from scheduling.schema import (
    BlockedInterval, Deadline, FixedStart, OptimizationStage, Precedence, PreferredStart,
    ProblemSpec, ReleaseTime, RepairContext, Schedule, ScheduledActivity, SolveResult,
)


@dataclass(frozen=True)
class SolverLimits:
    time_limit_seconds: float = 5.0
    random_seed: int = 0
    num_workers: int = 1

    def __post_init__(self) -> None:
        if type(self.time_limit_seconds) not in (float, int) or not math.isfinite(self.time_limit_seconds) or self.time_limit_seconds < 0:
            raise ValueError("Time budget must be finite and nonnegative")
        if type(self.random_seed) is not int or not 0 <= self.random_seed < 2**31:
            raise ValueError("Seed must be a nonnegative int32")
        if type(self.num_workers) is not int or not 1 <= self.num_workers < 2**31:
            raise ValueError("Worker count must be a positive int32")


def legal_starts(spec: ProblemSpec, activity_id: str) -> tuple[int, ...]:
    """Compiler-only domains. Never reuse this in the independent validator."""
    activity = next(a for a in spec.activities if a.id == activity_id)
    people = {p.id: p for p in spec.participants}
    resources = {r.id: r for r in spec.resources}
    windows = [activity.availability]
    windows.extend(people[p].availability for p in activity.participant_ids)
    windows.extend(resources[r].availability for r in activity.resource_ids)
    starts = []
    for start in range(spec.horizon_slots - activity.duration_slots + 1):
        end = start + activity.duration_slots
        if not all(any(w.start <= start and end <= w.end for w in group) for group in windows):
            continue
        valid = True
        for constraint in spec.constraints:
            if isinstance(constraint, ReleaseTime) and constraint.activity_id == activity.id:
                if type(constraint) is ReleaseTime and start < constraint.slot:
                    valid = False
                elif type(constraint) is Deadline and end > constraint.slot:
                    valid = False
                elif type(constraint) is FixedStart and start != constraint.slot:
                    valid = False
            if isinstance(constraint, BlockedInterval):
                ids = activity.participant_ids if constraint.target_kind == "participant" else activity.resource_ids
                if constraint.target_id in ids and start < constraint.end and constraint.start < end:
                    valid = False
        if valid:
            starts.append(start)
    return tuple(starts)


def _compile(spec: ProblemSpec, context: RepairContext | None):
    model = cp_model.CpModel()
    domains = {a.id: legal_starts(spec, a.id) for a in spec.activities}
    if any(not values for values in domains.values()):
        # Explicit false constraint lets CP-SAT prove unary infeasibility without
        # creating an invalid empty-domain interval (or overflowing a huge duration).
        model.add(False)
        return model, {}, [("preference_penalty" if context is None else "moved_count", 0)]
    starts = {key: model.new_int_var_from_domain(cp_model.Domain.from_values(values), f"start:{key}")
              for key, values in domains.items()}
    durations = {a.id: a.duration_slots for a in spec.activities}
    intervals = {key: model.new_interval_var(start, durations[key], start + durations[key], f"activity:{key}")
                 for key, start in starts.items()}
    for entities, attribute in ((spec.participants, "participant_ids"), (spec.resources, "resource_ids")):
        for entity in entities:
            model.add_no_overlap([intervals[a.id] for a in spec.activities if entity.id in getattr(a, attribute)])
    preference_terms = []
    for constraint in spec.constraints:
        if isinstance(constraint, Precedence):
            model.add(starts[constraint.before] + durations[constraint.before] <= starts[constraint.after])
        elif isinstance(constraint, PreferredStart):
            violated = model.new_bool_var(f"violated:{constraint.id}")
            model.add_allowed_assignments([starts[constraint.activity_id], violated],
                                         [(s, int(not constraint.start <= s < constraint.end))
                                          for s in domains[constraint.activity_id]])
            preference_terms.append(constraint.weight * violated)
    penalty = sum(preference_terms)
    if context is None:
        return model, starts, [("preference_penalty", penalty)]
    old = context.original_schedule.starts()
    moves, shifts = [], []
    for key, start in starts.items():
        moved = model.new_bool_var(f"moved:{key}")
        model.add(start != old[key]).only_enforce_if(moved)
        model.add(start == old[key]).only_enforce_if(moved.Not())
        shift = model.new_int_var(0, spec.horizon_slots, f"shift:{key}")
        model.add_abs_equality(shift, start - old[key])
        moves.append(moved)
        shifts.append(shift)
    return model, starts, [("moved_count", sum(moves)), ("total_shift_slots", sum(shifts)), ("preference_penalty", penalty)]


def solve(spec: ProblemSpec, limits: SolverLimits,
          repair_context: RepairContext | None = None) -> SolveResult:
    if not isinstance(spec, ProblemSpec) or not isinstance(limits, SolverLimits):
        raise TypeError("solve requires a canonical ProblemSpec and SolverLimits")
    check_repair_context(spec, repair_context)
    start_time = time.monotonic()
    stages = []
    incumbent = values = None
    status = last_status = "UNKNOWN"
    diagnostics = ()
    # Objective/bound records use the backend's double-valued bound interface.
    # Reject unsupported magnitudes explicitly rather than losing exactness.
    if sum(c.weight for c in spec.constraints if isinstance(c, PreferredStart)) > 2**53 - 1:
        return SolveResult("MODEL_INVALID", "MODEL_INVALID", None, None, (),
                           time.monotonic() - start_time, False, ("objective_exceeds_exact_bound_range",))
    try:
        model, starts, objectives = _compile(spec, repair_context)
    except (OverflowError, ValueError):
        return SolveResult("MODEL_INVALID", "MODEL_INVALID", None, None, (),
                           time.monotonic() - start_time, False, ("compiler_numeric_range_error",))
    for name, objective in objectives:
        remaining = max(0.0, limits.time_limit_seconds - (time.monotonic() - start_time))
        if remaining == 0:
            last_status = "UNKNOWN"
            status = "FEASIBLE" if incumbent is not None else "UNKNOWN"
            stages.append(OptimizationStage(name, "UNKNOWN", None, None, 0.0, 0.0, False))
            diagnostics = ("total_time_budget_exhausted",)
            break
        model.minimize(objective)
        if model.validate():
            status = last_status = "MODEL_INVALID"
            diagnostics = ("compiled_model_invalid",)
            break
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = remaining
        solver.parameters.num_search_workers = limits.num_workers
        solver.parameters.random_seed = limits.random_seed
        solver.parameters.absolute_gap_limit = 0
        solver.parameters.relative_gap_limit = 0
        tick = time.monotonic()
        code = solver.solve(model)
        last_status = solver.status_name(code)
        feasible = code in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        proven = code == cp_model.OPTIMAL
        value = int(solver.value(objective)) if feasible else None
        bound = float(solver.best_objective_bound) if code != cp_model.MODEL_INVALID else None
        stages.append(OptimizationStage(name, last_status, value, bound, remaining,
                                        time.monotonic() - tick, proven))
        if feasible:
            candidate = Schedule(tuple(ScheduledActivity(key, int(solver.value(var))) for key, var in starts.items()))
            candidate_values = measure_objectives(spec, candidate, repair_context)
            if values is None or candidate_values.as_tuple() < values.as_tuple():
                incumbent, values = candidate, candidate_values
            status = "OPTIMAL" if proven else "FEASIBLE"
            if not proven:
                break
            model.add(objective == value)
            model.clear_hints()
            for key, old_start in incumbent.starts().items():
                model.add_hint(starts[key], old_start)
        elif code == cp_model.UNKNOWN:
            status = "FEASIBLE" if incumbent is not None else "UNKNOWN"
            break
        else:
            status = last_status
            if incumbent is not None and code == cp_model.INFEASIBLE:
                status = "MODEL_INVALID"
                diagnostics = ("inconsistent_lexicographic_stage",)
            break
    fully_proven = len(stages) == len(objectives) and all(stage.proven_optimal for stage in stages)
    if incumbent is not None and status == "OPTIMAL" and not fully_proven:
        status = "FEASIBLE"
    return SolveResult(status, last_status, incumbent, values, tuple(stages),
                       time.monotonic() - start_time, fully_proven, diagnostics)
