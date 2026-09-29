"""The shared boundary enforces v1 meanings without validating original feasibility."""

from dataclasses import replace

import pytest

from scheduling.schema import (
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    RepairCase,
    Schedule,
    SchemaError,
    Window,
)
from tests.formal_support import tiny


def old_schedule():
    return Schedule.from_list(
        [{"activity_id": "A", "start_slot": 0}, {"activity_id": "B", "start_slot": 2}]
    )


@pytest.mark.parametrize(
    "change", ["origin", "timezone", "horizon", "duration", "participants", "resources"]
)
def test_changed_repair_meaning_rejected_at_shared_boundary(change):
    original = tiny()
    updated = replace(original, task_type="repair")
    if change == "origin":
        updated = replace(updated, horizon_start="2026-10-05T10:00:00+08:00")
    elif change == "timezone":
        updated = replace(updated, timezone="Asia/Singapore")
    elif change == "horizon":
        updated = replace(updated, horizon_slots=5)
    else:
        field, value = {
            "duration": ("duration_slots", 2),
            "participants": ("participant_ids", ()),
            "resources": ("resource_ids", ()),
        }[change]
        updated = replace(
            updated,
            activities=(
                replace(updated.activities[0], **{field: value}),
                updated.activities[1],
            ),
        )
    with pytest.raises(SchemaError, match="Repair must preserve"):
        RepairCase(original, old_schedule(), "unsupported mutation", updated)


def test_activity_and_assignment_order_are_irrelevant():
    spec = tiny()
    spec = replace(
        spec,
        participants=spec.participants + (Entity("Q", (Window(0, 4),)),),
        activities=tuple(
            replace(a, participant_ids=("P", "Q")) for a in spec.activities
        ),
    )
    updated = replace(
        spec,
        task_type="repair",
        activities=tuple(
            replace(a, participant_ids=tuple(reversed(a.participant_ids)))
            for a in reversed(spec.activities)
        ),
    )
    RepairCase(spec, old_schedule(), "reorder only", updated)


@pytest.mark.parametrize(
    "event",
    [
        BlockedInterval("block", "participant", "P", 0, 1),
        Deadline("deadline", "B", 2),
        FixedStart("fixed", "A", 1),
    ],
)
def test_supported_disruptions_remain_accepted(event):
    original = tiny()
    updated = replace(original, task_type="repair", constraints=(event,))
    RepairCase(original, old_schedule(), "supported event", updated)


def test_changed_availability_allowed_and_presence_still_fixed():
    original = tiny()
    updated = replace(
        original,
        task_type="repair",
        activities=(
            replace(original.activities[0], availability=(Window(1, 4),)),
            original.activities[1],
        ),
    )
    RepairCase(original, old_schedule(), "availability change", updated)
    with pytest.raises(SchemaError, match="Missing or invented"):
        RepairCase(
            original,
            old_schedule(),
            "cancel A",
            replace(updated, activities=(updated.activities[1],)),
        )
