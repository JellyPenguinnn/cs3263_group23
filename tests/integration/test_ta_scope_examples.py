"""Independent checks for the bounded office illustration, not model evidence."""
from dataclasses import replace
from itertools import product

from evaluation.ta_scope_examples import examples, schedule, verify
from scheduling.schema import RepairContext
from scheduling.validation import validate_schedule


def test_room_contradiction_is_collective_and_release_makes_it_feasible():
    loose, tight, impossible, _, original = examples()
    for spec in (loose, tight):
        assert validate_schedule(spec, original).hard_feasible
    # All four possible starts of the two restricted meetings fail together.
    # Giving either meeting its loose window restores an independently valid witness.
    for first, second in product((4, 5), repeat=2):
        assert not validate_schedule(impossible, schedule({**original.starts(), "M2": first, "M3": second})).hard_feasible
    for released, confined in (("M2", "M3"), ("M3", "M2")):
        relaxed = replace(impossible, activities=tuple(
            a if a.id != released else next(b for b in loose.activities if b.id == released)
            for a in impossible.activities))
        assert validate_schedule(relaxed, schedule({**original.starts(), confined: 4, released: 6})).hard_feasible


def test_repair_minimum_preserves_unrelated_activity_and_counts_shift_correctly():
    _, _, _, repair, original = examples()
    updated = schedule({**original.starts(), "A3": 14})
    checked = validate_schedule(repair, updated, RepairContext(original))
    assert checked.hard_feasible
    assert not validate_schedule(repair, original, RepairContext(original)).hard_feasible
    # Compute moved activities, shifted start slots and changed occupied cells
    # independently; the latter is not the benchmark's shift objective.
    durations = {a.id: a.duration_slots for a in repair.activities}
    before, after = original.starts(), updated.starts()
    moved = [k for k in before if before[k] != after[k]]
    cells = sum(len(set(range(before[k], before[k]+durations[k])) ^
                    set(range(after[k], after[k]+durations[k]))) for k in before)
    assert moved == ["A3"]
    assert sum(abs(before[k]-after[k]) for k in before) == 2
    assert cells == 4
    assert before["B2"] == after["B2"] == 12
    result = verify()
    assert result["new_model_calls"] == 0
    assert result["repair_summary"]["changed_activity_occupancy_cells"] == cells
