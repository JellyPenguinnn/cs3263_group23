"""Canonical v1 draft contract; no solver or independent-validation logic.

JSON boundaries are strict: no unknown fields, duplicate keys, coercion or implicit
availability. Well-formed contradictions remain problems for the solver.
"""

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import TYPE_CHECKING, ClassVar, Literal

if TYPE_CHECKING:
    from scheduling.domain_analysis import DomainAnalysis
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from scheduling.providers.types import ModelResponse, Usage

TaskType = Literal["generation", "repair"]
PipelineStatus = Literal["SAT", "UNSAT", "UNKNOWN", "INVALID_OUTPUT", "ERROR"]
SolverStatus = Literal["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID"]


@dataclass(frozen=True)
class SchemaDiagnostic:
    code: str
    path: str
    message: str
    missing_fields: tuple[str, ...] = ()
    unsupported_fields: tuple[str, ...] = ()
    format_version: str = "1.0"


class SchemaError(ValueError):
    """Malformed structure with safe location detail; never echo field values."""

    def __init__(self, message, *, code="invalid_schema", path="$",
                 missing_fields=(), unsupported_fields=()):
        super().__init__(message)
        self.detail = SchemaDiagnostic(code, path, message, missing_fields, unsupported_fields)


def _located(path, operation):
    try:
        return operation()
    except SchemaError as error:
        detail = error.detail
        raise SchemaError(detail.message, code=detail.code,
                          path=path + detail.path[1:], missing_fields=detail.missing_fields,
                          unsupported_fields=detail.unsupported_fields) from None



def _integer(value: object, name: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise SchemaError(f"{name} must be an integer >= {minimum}", code="invalid_integer",
                          path="$." + name.split()[-1])


def _identifier(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError("IDs must be nonempty strings", code="invalid_id", path="$.id")


def _tuple_of(value: object, cls: type) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, cls) for item in value):
        raise SchemaError(f"Expected a tuple of {cls.__name__}")


def _unique(values: tuple[str, ...]) -> None:
    _tuple_of(values, str)
    for value in values:
        _identifier(value)
    if len(set(values)) != len(values):
        raise SchemaError("Duplicate IDs")


def _safe_field(value):
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", value) else "<invalid_field_name>"


def _record(data: object, keys: set[str], path="$") -> dict:
    if not isinstance(data, dict):
        raise SchemaError("Expected a JSON object", code="expected_object", path=path)
    missing = tuple(sorted(keys - data.keys()))
    unsupported = tuple(sorted({_safe_field(k) for k in data.keys() - keys}))
    if missing or unsupported:
        extra = unsupported[0] if unsupported else missing[0]
        raise SchemaError("Missing or unsupported object fields", code="object_fields",
                          path=path + "." + extra, missing_fields=missing,
                          unsupported_fields=unsupported)
    return data


def _array(data: object, path="$") -> list:
    if not isinstance(data, list):
        raise SchemaError("Expected an explicit JSON array", code="expected_array", path=path)
    return data


def _json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SchemaError("Duplicate JSON key", code="duplicate_key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    raise SchemaError("Nonfinite JSON number", code="nonfinite_number")


def load_json(content: str) -> object:
    try:
        return json.loads(content, object_pairs_hook=_json_object, parse_constant=_nonfinite)
    except SchemaError:
        raise
    except (ValueError, TypeError, RecursionError):
        raise SchemaError("Invalid or ambiguous JSON", code="invalid_json") from None


@dataclass(frozen=True)
class Window:
    start: int
    end: int

    def __post_init__(self) -> None:
        _integer(self.start, "window start")
        _integer(self.end, "window end")
        if self.start >= self.end:
            raise SchemaError("Window must have positive length", code="invalid_window", path="$.end")


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
            raise SchemaError("Unsupported blocked target kind", code="unsupported_target", path="$.target_kind")
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
            raise SchemaError("Unsupported schema_version", path="$.schema_version")
        _identifier(self.instance_id)
        if self.task_type not in ("generation", "repair"):
            raise SchemaError("Unsupported task_type", path="$.task_type")
        _integer(self.horizon_slots, "horizon_slots", 1)
        if self.horizon_slots > 48:
            raise SchemaError("v1 requires a single day of 30-minute slots", path="$.horizon_slots")
        if type(self.slot_minutes) is not int or self.slot_minutes != 30:
            raise SchemaError("v1 requires a single day of 30-minute slots", path="$.slot_minutes")
        try:
            start = datetime.fromisoformat(self.horizon_start)
        except (TypeError, ValueError):
            raise SchemaError("horizon_start must be an offset-aware ISO datetime", path="$.horizon_start") from None
        if start.utcoffset() is None:
            raise SchemaError("horizon_start requires an explicit UTC offset", path="$.horizon_start")
        zone = _located("$.timezone", lambda: _zone(self.timezone))
        try:
            end = start + timedelta(minutes=self.slot_minutes * self.horizon_slots)
            if start.utcoffset() != start.astimezone(zone).utcoffset() or end.utcoffset() != end.astimezone(zone).utcoffset():
                raise SchemaError("Timezone must agree with a fixed-offset horizon", path="$.timezone")
            midnight = (start + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        except OverflowError:
            raise SchemaError("Horizon exceeds supported calendar range", path="$.horizon_start") from None
        if end > midnight:
            raise SchemaError("Horizon extends beyond the stated day", path="$.horizon_start")
        for name, rows, cls in (("participants", self.participants, Entity), ("resources", self.resources, Entity), ("activities", self.activities, Activity)):
            _tuple_of(rows, cls)
            _located("$." + name, lambda: _unique(tuple(row.id for row in rows)))
            for index, row in enumerate(rows):
                for wi, window in enumerate(row.availability):
                    if window.end > self.horizon_slots:
                        raise SchemaError("Availability endpoint outside horizon", code="horizon_endpoint",
                                          path=f"$.{name}[{index}].availability[{wi}].end")
        _tuple_of(self.constraints, object)
        if any(type(c) not in CONSTRAINT_TYPES.values() for c in self.constraints):
            raise SchemaError("Unsupported constraint type")
        _located("$.constraints", lambda: _unique(tuple(c.id for c in self.constraints)))
        participants = {p.id for p in self.participants}
        resources = {r.id for r in self.resources}
        activities = {a.id for a in self.activities}
        for index, activity in enumerate(self.activities):
            for name, ids in (("participant_ids", participants), ("resource_ids", resources)):
                for j, label in enumerate(getattr(activity, name)):
                    if label not in ids:
                        raise SchemaError("Dangling participant/resource reference", code="dangling_reference",
                                          path=f"$.activities[{index}].{name}[{j}]")
        for index, constraint in enumerate(self.constraints):
            if isinstance(constraint, (ReleaseTime, PreferredStart)) and constraint.activity_id not in activities:
                raise SchemaError("Dangling activity reference", code="dangling_reference", path=f"$.constraints[{index}].activity_id")
            if isinstance(constraint, ReleaseTime) and constraint.slot > self.horizon_slots:
                raise SchemaError("Constraint slot outside horizon", code="horizon_endpoint", path=f"$.constraints[{index}].slot")
            if isinstance(constraint, Precedence) and {constraint.before, constraint.after} - activities:
                raise SchemaError("Dangling precedence reference", code="dangling_reference",
                                  path=f"$.constraints[{index}]." + ("before" if constraint.before not in activities else "after"))
            if isinstance(constraint, (BlockedInterval, PreferredStart)) and constraint.end > self.horizon_slots:
                raise SchemaError("Constraint window outside horizon", code="horizon_endpoint", path=f"$.constraints[{index}].end")
            if isinstance(constraint, BlockedInterval):
                targets = participants if constraint.target_kind == "participant" else resources
                if constraint.target_id not in targets:
                    raise SchemaError("Dangling blocked target reference", code="dangling_reference", path=f"$.constraints[{index}].target_id")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["constraints"] = [{"type": c.kind, **asdict(c)} for c in self.constraints]
        return json.loads(json.dumps(data))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: object) -> "ProblemSpec":
        data = dict(_record(data, {field.name for field in fields(cls)}))
        def windows(raw, path):
            result = []
            for index, item in enumerate(_array(raw, path)):
                item_path = f"{path}[{index}]"
                row = _record(item, {"start", "end"}, item_path)
                result.append(_located(item_path, lambda: Window(**row)))
            return tuple(result)
        for key in ("participants", "resources"):
            rows = []
            for index, item in enumerate(_array(data[key], "$." + key)):
                path = f"$.{key}[{index}]"
                row = _record(item, {"id", "availability"}, path)
                allowed = windows(row["availability"], path + ".availability")
                rows.append(_located(path, lambda: Entity(row["id"], allowed)))
            data[key] = tuple(rows)
        activities = []
        for index, item in enumerate(_array(data["activities"], "$.activities")):
            path = f"$.activities[{index}]"
            row = _record(item, {field.name for field in fields(Activity)}, path)
            people = tuple(_array(row["participant_ids"], path + ".participant_ids"))
            resources = tuple(_array(row["resource_ids"], path + ".resource_ids"))
            _located(path + ".participant_ids", lambda: _unique(people))
            _located(path + ".resource_ids", lambda: _unique(resources))
            allowed = windows(row["availability"], path + ".availability")
            activities.append(_located(path, lambda: Activity(row["id"], row["duration_slots"], people, resources, allowed)))
        data["activities"] = tuple(activities)
        constraints = []
        for index, item in enumerate(_array(data["constraints"], "$.constraints")):
            path = f"$.constraints[{index}]"
            if not isinstance(item, dict) or not isinstance(item.get("type"), str) or item["type"] not in CONSTRAINT_TYPES:
                raise SchemaError("Unsupported constraint type", code="unsupported_constraint", path=path + ".type")
            constraint_cls = CONSTRAINT_TYPES[item["type"]]
            row = _record(item, {"type"} | {field.name for field in fields(constraint_cls)}, path)
            for name in ("id", "activity_id", "before", "after", "target_id"):
                if name in row:
                    # Locate ID failures at their actual operand, without echoing the value.
                    try:
                        _identifier(row[name])
                    except SchemaError:
                        raise SchemaError("IDs must be nonempty strings", code="invalid_id", path=path + "." + name) from None
            constraints.append(_located(path, lambda: constraint_cls(**{key: value for key, value in row.items() if key != "type"})))
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
        for name in ("horizon_start", "timezone", "slot_minutes", "horizon_slots"):
            if getattr(self.original_problem, name) != getattr(self.updated_problem, name):
                raise SchemaError(f"Repair must preserve {name}")
        original = {a.id: a for a in self.original_problem.activities}
        for activity in self.updated_problem.activities:
            before = original[activity.id]
            if activity.duration_slots != before.duration_slots:
                raise SchemaError("Repair must preserve activity duration_slots")
            for name in ("participant_ids", "resource_ids"):
                if set(getattr(activity, name)) != set(getattr(before, name)):
                    raise SchemaError(f"Repair must preserve activity {name}")
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
    integer_lower_bound: int | None = None


@dataclass(frozen=True)
class SolverInputBinding:
    """Exact canonical input correspondence, not authentication of solver evidence."""

    specification_sha256: str
    repair_context_sha256: str
    format_version: str = "1.0"


def solver_input_binding(
    spec: ProblemSpec, context: RepairContext | None = None
) -> SolverInputBinding:
    def digest(value: object) -> str:
        payload = json.dumps(to_data(value), sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return SolverInputBinding(digest(spec), digest(context))


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
    domain_analysis: "DomainAnalysis | None" = None
    input_binding: SolverInputBinding | None = None


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
    schema_diagnostics: tuple[SchemaDiagnostic, ...] = ()

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
