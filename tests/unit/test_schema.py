from dataclasses import replace
import json

import pytest

from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, NaturalLanguageView,
    Precedence, PreferredStart, ProblemSpec, ReleaseTime, RepairCase, Schedule,
    ScheduledActivity, SchemaError, Window,
)
from tests.formal_support import tiny


def test_roundtrip_all_constraints_and_deterministic_serialization():
    spec = tiny(constraints=(ReleaseTime("r", "A", 0), Deadline("d", "B", 4), FixedStart("f", "A", 0),
                            Precedence("p", "A", "B"), BlockedInterval("b", "resource", "R", 3, 4),
                            PreferredStart("s", "B", 1, 2, 3)))
    assert ProblemSpec.from_json(spec.to_json()) == spec
    assert ProblemSpec.from_dict(spec.to_dict()).to_json() == spec.to_json()


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(extra=1),
    lambda d: d.pop("participants"),
    lambda d: d.update(schema_version="2.0"),
    lambda d: d.update(horizon_slots=True),
    lambda d: d.update(slot_minutes=15),
    lambda d: d.update(horizon_start="2026-10-05T09:00:00"),
    lambda d: d.update(timezone="UTC"),
    lambda d: d.update(horizon_start="2026-10-05T23:30:00+08:00"),
    lambda d: d["activities"][0].update(duration_slots=1.5),
    lambda d: d["activities"][0].update(duration_slots=False),
    lambda d: d["activities"][0].pop("availability"),
    lambda d: d["activities"][0].update(participant_ids=["missing"]),
    lambda d: d["activities"][0].update(resource_ids=["R", "R"]),
    lambda d: d["activities"].append(d["activities"][0]),
    lambda d: d["participants"][0].update(capacity=2),
    lambda d: d["participants"][0].update(availability=[{"start": 0, "end": 5}]),
    lambda d: d["constraints"].append({"type": "travel", "id": "x"}),
    lambda d: d["constraints"].append({"type": "release", "id": "x", "activity_id": "missing", "slot": 0}),
    lambda d: d["constraints"].append({"type": "blocked", "id": "x", "target_kind": "resource", "target_id": "missing", "start": 0, "end": 1}),
    lambda d: d["constraints"].append({"type": "precedence", "id": "x", "before": "A", "after": "missing"}),
    lambda d: d["constraints"].append({"type": "preferred_start", "id": "x", "activity_id": "A", "start": 2, "end": 2, "weight": 1}),
])
def test_reject_malformed_schema(mutation):
    data = tiny().to_dict()
    mutation(data)
    with pytest.raises(SchemaError):
        ProblemSpec.from_dict(data)


@pytest.mark.parametrize("content", ['{"x":1,"x":2}', '{"x":NaN}', 'not JSON'])
def test_untrusted_json_rejects_duplicate_keys_and_nonfinite_values(content):
    with pytest.raises(SchemaError):
        ProblemSpec.from_json(content)


def test_contradictions_and_unavailable_entities_are_preserved():
    spec = tiny(constraints=(ReleaseTime("r", "A", 3), Deadline("d", "A", 1)))
    unavailable = replace(spec, participants=(Entity("P", ()),))
    assert ProblemSpec.from_json(unavailable.to_json()) == unavailable
    too_long = replace(spec, activities=(replace(spec.activities[0], duration_slots=5), spec.activities[1]))
    assert ProblemSpec.from_json(too_long.to_json()) == too_long


@pytest.mark.parametrize("row", [{"activity_id": "A", "start_slot": True}, {"activity_id": "A", "start_slot": "09:00"}, {"activity_id": "A", "start_slot": -1}])
def test_schedule_starts_never_coerced(row):
    with pytest.raises(SchemaError):
        Schedule.from_list([row])


def test_schedule_coverage_duplicates_and_roundtrip():
    schedule = Schedule.from_list([{"activity_id": "B", "start_slot": 2}, {"activity_id": "A", "start_slot": 0}])
    assert schedule.to_list()[0] == {"activity_id": "A", "start_slot": 0}
    schedule.require_ids(("A", "B"))
    with pytest.raises(SchemaError):
        schedule.require_ids(("A",))
    with pytest.raises(SchemaError):
        Schedule.from_list(schedule.to_list() + [schedule.to_list()[0]])


def test_public_view_requires_original_for_repair_and_no_gold_fields():
    old = Schedule((ScheduledActivity("A", 0), ScheduledActivity("B", 2)))
    view = NaturalLanguageView("tiny", "canonical", "repair", "Updated public description", ("A", "B"), old)
    assert view.original_schedule == old and not hasattr(view, "gold_spec")
    with pytest.raises(SchemaError):
        replace(view, original_schedule=None)
    with pytest.raises(SchemaError):
        replace(view, task_type="generation")
    case = RepairCase(tiny(), old, "P becomes blocked", tiny(task_type="repair"))
    assert case.original_problem.task_type == "generation" and case.updated_problem.task_type == "repair"


def test_named_fixed_offset_timezone_and_dst_rejection():
    assert replace(tiny(), timezone="Asia/Singapore")
    with pytest.raises(SchemaError):
        replace(tiny(), timezone="America/New_York", horizon_start="2026-03-08T01:00:00-05:00")


@pytest.mark.parametrize("start", ["9999-12-31T23:00:00+08:00", "0001-01-01T00:00:00+08:00"])
def test_calendar_boundary_is_schema_error_not_uncaught_overflow(start):
    with pytest.raises(SchemaError):
        replace(tiny(), horizon_start=start, timezone="UTC")
