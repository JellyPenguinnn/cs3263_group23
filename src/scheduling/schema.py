"""Canonical v1 draft contract; no solver or independent-validation logic.

JSON boundaries are strict: no unknown fields, duplicate keys, coercion or implicit
availability. Well-formed contradictions remain problems for the solver.
"""

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from typing import ClassVar, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from scheduling.providers.types import ModelResponse, Usage

TaskType = Literal["generation", "repair"]
PipelineStatus = Literal["SAT", "UNSAT", "UNKNOWN", "INVALID_OUTPUT", "ERROR"]
SolverStatus = Literal["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID"]


class SchemaError(ValueError):
    """Malformed structure, distinct from a well-formed infeasible problem."""


def _integer(value: object, name: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise SchemaError(f"{name} must be an integer >= {minimum}")


def _identifier(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError("IDs must be nonempty strings")


def _tuple_of(value: object, cls: type) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, cls) for item in value):
        raise SchemaError(f"Expected a tuple of {cls.__name__}")


def _unique(values: tuple[str, ...]) -> None:
    _tuple_of(values, str)
    for value in values:
        _identifier(value)
    if len(set(values)) != len(values):
        raise SchemaError("Duplicate IDs")


def _record(data: object, keys: set[str]) -> dict:
    if not isinstance(data, dict) or set(data) != keys:
        raise SchemaError("Missing or unsupported object fields")
    return data


def _array(data: object) -> list:
    if not isinstance(data, list):
        raise SchemaError("Expected an explicit JSON array")
    return data


def _json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SchemaError("Duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    raise SchemaError("Nonfinite JSON number")


def load_json(content: str) -> object:
    try:
        return json.loads(content, object_pairs_hook=_json_object, parse_constant=_nonfinite)
    except (ValueError, TypeError, RecursionError):
        raise SchemaError("Invalid or ambiguous JSON") from None


@dataclass(frozen=True)
class Window:
    start: int
    end: int

    def __post_init__(self) -> None:
        _integer(self.start, "window start")
        _integer(self.end, "window end")
        if self.start >= self.end:
            raise SchemaError("Window must have positive length")


@dataclass(frozen=True)
class Entity:
    id: str
    availability: tuple[Window, ...]

    def __post_init__(self) -> None:
        _identifier(self.id)
        _tuple_of(self.availability, Window)


@dataclass(frozen=True)
class Activity:
    id: str
    duration_slots: int
    participant_ids: tuple[str, ...]
    resource_ids: tuple[str, ...]
    availability: tuple[Window, ...]

    def __post_init__(self) -> None:
        _identifier(self.id)
        _integer(self.duration_slots, "duration_slots", 1)
        _unique(self.participant_ids)
        _unique(self.resource_ids)
        _tuple_of(self.availability, Window)


@dataclass(frozen=True)
class ReleaseTime:
    id: str
    activity_id: str
    slot: int
    kind: ClassVar[str] = "release"

    def __post_init__(self) -> None:
        _identifier(self.id)
        _identifier(self.activity_id)
        _integer(self.slot, "release slot")


@dataclass(frozen=True)
class Deadline(ReleaseTime):
    kind: ClassVar[str] = "deadline"


@dataclass(frozen=True)
class FixedStart(ReleaseTime):
    kind: ClassVar[str] = "fixed_start"


@dataclass(frozen=True)
class Precedence:
    id: str
    before: str
    after: str
    kind: ClassVar[str] = "precedence"

    def __post_init__(self) -> None:
        for value in (self.id, self.before, self.after):
            _identifier(value)


@dataclass(frozen=True)
class BlockedInterval:
    id: str
    target_kind: Literal["participant", "resource"]
    target_id: str
    start: int
    end: int
    kind: ClassVar[str] = "blocked"

    def __post_init__(self) -> None:
        _identifier(self.id)
        _identifier(self.target_id)
        if self.target_kind not in ("participant", "resource"):
            raise SchemaError("Unsupported blocked target kind")
        Window(self.start, self.end)


@dataclass(frozen=True)
class PreferredStart:
    id: str
    activity_id: str
    start: int
    end: int
    weight: int
    kind: ClassVar[str] = "preferred_start"

    def __post_init__(self) -> None:
        _identifier(self.id)
        _identifier(self.activity_id)
        Window(self.start, self.end)
        _integer(self.weight, "preference weight")


Constraint = ReleaseTime | Deadline | FixedStart | Precedence | BlockedInterval | PreferredStart
CONSTRAINT_TYPES = {cls.kind: cls for cls in (
    ReleaseTime, Deadline, FixedStart, Precedence, BlockedInterval, PreferredStart)}


def _zone(name: str):
    if not isinstance(name, str):
        raise SchemaError("Explicit timezone required")
    if re.fullmatch(r"[+-]\d{2}:\d{2}", name):
        hours, minutes = map(int, name[1:].split(":"))
        if hours > 23 or minutes > 59:
            raise SchemaError("Invalid timezone offset")
        return timezone((1 if name[0] == "+" else -1) * timedelta(hours=hours, minutes=minutes))
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise SchemaError("Unsupported timezone") from None


@dataclass(frozen=True)
class ProblemSpec:
    schema_version: str
    instance_id: str
    task_type: TaskType
    horizon_slots: int
    slot_minutes: int
    horizon_start: str
    timezone: str
    participants: tuple[Entity, ...]
    resources: tuple[Entity, ...]
    activities: tuple[Activity, ...]
    constraints: tuple[Constraint, ...]

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise SchemaError("Unsupported schema_version")
        _identifier(self.instance_id)
        if self.task_type not in ("generation", "repair"):
            raise SchemaError("Unsupported task_type")
        _integer(self.horizon_slots, "horizon_slots", 1)
        if self.horizon_slots > 48 or type(self.slot_minutes) is not int or self.slot_minutes != 30:
            raise SchemaError("v1 requires a single day of 30-minute slots")
        try:
            start = datetime.fromisoformat(self.horizon_start)
        except (TypeError, ValueError):
            raise SchemaError("horizon_start must be an offset-aware ISO datetime") from None
        if start.utcoffset() is None:
            raise SchemaError("horizon_start requires an explicit UTC offset")
        zone = _zone(self.timezone)
        try:
            end = start + timedelta(minutes=self.slot_minutes * self.horizon_slots)
            if start.utcoffset() != start.astimezone(zone).utcoffset() or end.utcoffset() != end.astimezone(zone).utcoffset():
                raise SchemaError("Timezone must agree with a fixed-offset horizon")
            midnight = (start + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        except OverflowError:
            raise SchemaError("Horizon exceeds supported calendar range") from None
        if end > midnight:
            raise SchemaError("Horizon extends beyond the stated day")
        for rows, cls in ((self.participants, Entity), (self.resources, Entity), (self.activities, Activity)):
            _tuple_of(rows, cls)
            _unique(tuple(row.id for row in rows))
            for row in rows:
                if any(w.end > self.horizon_slots for w in row.availability):
                    raise SchemaError("Availability endpoint outside horizon")
        _tuple_of(self.constraints, object)
        if any(type(c) not in CONSTRAINT_TYPES.values() for c in self.constraints):
            raise SchemaError("Unsupported constraint type")
        _unique(tuple(c.id for c in self.constraints))
        participants = {p.id for p in self.participants}
        resources = {r.id for r in self.resources}
        activities = {a.id for a in self.activities}
        for activity in self.activities:
            if set(activity.participant_ids) - participants or set(activity.resource_ids) - resources:
                raise SchemaError("Dangling participant/resource reference")
        for constraint in self.constraints:
            if isinstance(constraint, (ReleaseTime, PreferredStart)) and constraint.activity_id not in activities:
                raise SchemaError("Dangling activity reference")
            if isinstance(constraint, ReleaseTime) and constraint.slot > self.horizon_slots:
                raise SchemaError("Constraint slot outside horizon")
            if isinstance(constraint, Precedence) and {constraint.before, constraint.after} - activities:
                raise SchemaError("Dangling precedence reference")
            if isinstance(constraint, (BlockedInterval, PreferredStart)) and constraint.end > self.horizon_slots:
                raise SchemaError("Constraint window outside horizon")
            if isinstance(constraint, BlockedInterval):
                targets = participants if constraint.target_kind == "participant" else resources
                if constraint.target_id not in targets:
                    raise SchemaError("Dangling blocked target reference")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["constraints"] = [{"type": c.kind, **asdict(c)} for c in self.constraints]
        return json.loads(json.dumps(data))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: object) -> "ProblemSpec":
        data = dict(_record(data, {field.name for field in fields(cls)}))
        def windows(raw):
            return tuple(Window(**_record(w, {"start", "end"})) for w in _array(raw))
        for key in ("participants", "resources"):
            rows = []
            for item in _array(data[key]):
                row = _record(item, {"id", "availability"})
                rows.append(Entity(row["id"], windows(row["availability"])))
            data[key] = tuple(rows)
        activities = []
        for item in _array(data["activities"]):
            row = _record(item, {field.name for field in fields(Activity)})
            activities.append(Activity(row["id"], row["duration_slots"], tuple(_array(row["participant_ids"])),
                                       tuple(_array(row["resource_ids"])), windows(row["availability"])))
        data["activities"] = tuple(activities)
        constraints = []
        for item in _array(data["constraints"]):
            if not isinstance(item, dict) or not isinstance(item.get("type"), str) or item["type"] not in CONSTRAINT_TYPES:
                raise SchemaError("Unsupported constraint type")
            constraint_cls = CONSTRAINT_TYPES[item["type"]]
            row = _record(item, {"type"} | {field.name for field in fields(constraint_cls)})
            constraints.append(constraint_cls(**{key: value for key, value in row.items() if key != "type"}))
        data["constraints"] = tuple(constraints)
        return cls(**data)

    @classmethod
    def from_json(cls, content: str) -> "ProblemSpec":
        return cls.from_dict(load_json(content))


@dataclass(frozen=True)
class ScheduledActivity:
    activity_id: str
    start_slot: int

    def __post_init__(self) -> None:
        _identifier(self.activity_id)
        _integer(self.start_slot, "start_slot")


@dataclass(frozen=True)
class Schedule:
    entries: tuple[ScheduledActivity, ...]

    def __post_init__(self) -> None:
        _tuple_of(self.entries, ScheduledActivity)
        _unique(tuple(entry.activity_id for entry in self.entries))

    def starts(self) -> dict[str, int]:
        return {entry.activity_id: entry.start_slot for entry in self.entries}

    def require_ids(self, ids: tuple[str, ...]) -> None:
        _unique(ids)
        if set(self.starts()) != set(ids):
            raise SchemaError("Missing or invented scheduled activities")

    def to_list(self) -> list[dict]:
        return [asdict(row) for row in sorted(self.entries, key=lambda row: row.activity_id)]

    @classmethod
    def from_list(cls, data: object) -> "Schedule":
        return cls(tuple(ScheduledActivity(**_record(row, {"activity_id", "start_slot"})) for row in _array(data)))


@dataclass(frozen=True)
class RepairContext:
    original_schedule: Schedule

    def __post_init__(self) -> None:
        if not isinstance(self.original_schedule, Schedule):
            raise SchemaError("RepairContext requires a Schedule")


@dataclass(frozen=True)
class RepairCase:
    original_problem: ProblemSpec
    original_schedule: Schedule
    event: str
    updated_problem: ProblemSpec

    def __post_init__(self) -> None:
        if not isinstance(self.original_problem, ProblemSpec) or not isinstance(self.updated_problem, ProblemSpec):
            raise SchemaError("Both original and updated specifications are required")
        if not isinstance(self.original_schedule, Schedule) or not isinstance(self.event, str) or not self.event.strip():
            raise SchemaError("Original schedule and event description are required")
        if self.original_problem.task_type != "generation" or self.updated_problem.task_type != "repair":
            raise SchemaError("RepairCase requires original generation and updated repair specifications")
        old_ids = tuple(a.id for a in self.original_problem.activities)
        new_ids = tuple(a.id for a in self.updated_problem.activities)
        self.original_schedule.require_ids(old_ids)
        self.original_schedule.require_ids(new_ids)
        # Original feasibility remains the evaluator's independent validation duty.


@dataclass(frozen=True)
class NaturalLanguageView:
    instance_id: str
    variant_id: str
    task_type: TaskType
    text: str
    activity_ids: tuple[str, ...]
    original_schedule: Schedule | None = None

    def __post_init__(self) -> None:
        _identifier(self.instance_id)
        _identifier(self.variant_id)
        _unique(self.activity_ids)
        if self.task_type not in ("generation", "repair") or not isinstance(self.text, str) or not self.text.strip():
            raise SchemaError("Task type and complete public text are required")
        if self.task_type == "repair":
            if not isinstance(self.original_schedule, Schedule):
                raise SchemaError("Repair view requires original schedule")
            self.original_schedule.require_ids(self.activity_ids)
        elif self.original_schedule is not None:
            raise SchemaError("Generation view must not carry repair context")

    @classmethod
    def from_dict(cls, data: object) -> "NaturalLanguageView":
        row = dict(_record(data, {field.name for field in fields(cls)}))
        row["activity_ids"] = tuple(_array(row["activity_ids"]))
        if row["original_schedule"] is not None:
            row["original_schedule"] = Schedule.from_list(row["original_schedule"])
        return cls(**row)


@dataclass(frozen=True)
class ObjectiveValues:
    preference_penalty: int
    moved_count: int | None = None
    total_shift_slots: int | None = None

    def as_tuple(self) -> tuple[int, ...]:
        if self.moved_count is None:
            return (self.preference_penalty,)
        return (self.moved_count, self.total_shift_slots, self.preference_penalty)


@dataclass(frozen=True)
class OptimizationStage:
    objective: str
    solver_status: SolverStatus
    value: int | None
    best_bound: float | None
    time_limit_seconds: float
    elapsed_seconds: float
    proven_optimal: bool


@dataclass(frozen=True)
class SolveResult:
    status: SolverStatus
    last_solver_status: SolverStatus
    schedule: Schedule | None
    objectives: ObjectiveValues | None
    stages: tuple[OptimizationStage, ...]
    elapsed_seconds: float
    optimality_proven: bool
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class Violation:
    constraint_id: str | None
    category: str
    activity_ids: tuple[str, ...]


@dataclass(frozen=True)
class ValidationResult:
    structural_valid: bool
    hard_feasible: bool
    violations: tuple[Violation, ...]
    objectives: ObjectiveValues | None


@dataclass(frozen=True)
class PipelineResult:
    instance_id: str
    variant_id: str
    approach: Literal["direct", "solver_augmented"]
    status: PipelineStatus
    schedule: Schedule | None = None
    extracted_spec: ProblemSpec | None = None
    declared_status: str | None = None
    diagnostics: tuple[str, ...] = ()
    timings: tuple[tuple[str, float], ...] = ()
    usage: tuple[Usage, ...] = ()
    model_response: ModelResponse | None = None
    solve_result: SolveResult | None = None
    prompt_sha256: str | None = None
    config_sha256: str | None = None

    def __post_init__(self) -> None:
        if self.status not in ("SAT", "UNSAT", "UNKNOWN", "INVALID_OUTPUT", "ERROR"):
            raise SchemaError("Unsupported pipeline status")
        if self.status == "SAT" and not isinstance(self.schedule, Schedule):
            raise SchemaError("SAT requires a schedule; completeness checked against public IDs")


def to_data(value: object) -> object:
    """Serialize canonical schedules as arrays and retain tagged constraints."""
    if isinstance(value, ProblemSpec):
        return value.to_dict()
    if isinstance(value, Schedule):
        return value.to_list()
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: to_data(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, (tuple, list)):
        return [to_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_data(item) for key, item in value.items()}
    if value is None or type(value) in (str, int, float, bool):
        return value
    raise TypeError("Unsupported canonical serialization value")
