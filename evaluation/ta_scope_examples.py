"""Small office examples for TA scope discussion; offline, never model evidence."""
import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path

from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, PreferredStart,
    ProblemSpec, RepairCase, RepairContext, Schedule, Window,
)
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule


def schedule(starts):
    return Schedule.from_list([{"activity_id": key, "start_slot": value} for key, value in starts.items()])


def examples():
    full = (Window(0, 16),)
    rows = (
        ("M1", 2, ("Alice", "Bob"), ("Room",)),
        ("M2", 2, ("Alice", "Bob"), ("Room",)),
        ("M3", 2, ("Alice", "Bob"), ("Room",)),
        ("A1", 2, ("Alice",), ()), ("A2", 4, ("Alice",), ()),
        ("A3", 2, ("Alice",), ()), ("B1", 4, ("Bob",), ()),
        ("B2", 2, ("Bob",), ()),
    )
    original = schedule({"M1": 2, "M2": 4, "M3": 6, "A1": 0, "A2": 8, "A3": 12, "B1": 8, "B2": 12})
    rules = (FixedStart("appointment", "M1", 2),
             *(Deadline(f"end-{key}", key, 16) for key, *_ in rows),
             PreferredStart("morning-M2", "M2", 0, 6, 1),
             PreferredStart("morning-M3", "M3", 0, 6, 1))
    loose = ProblemSpec("1.0", "office-loose", "generation", 16, 30,
                        "2026-10-26T09:00:00+08:00", "+08:00",
                        (Entity("Alice", full), Entity("Bob", full)),
                        (Entity("Room", full),),
                        tuple(Activity(key, duration, people, rooms, full)
                              for key, duration, people, rooms in rows), rules)
    def restrict(end, ident):
        return replace(loose, instance_id=ident, activities=tuple(
            replace(a, availability=(Window(4, end),)) if a.id in ("M2", "M3") else a
            for a in loose.activities))
    tight = restrict(8, "office-tight")
    impossible = restrict(6, "office-impossible")
    repair = replace(loose, instance_id="office-repair", task_type="repair",
                     constraints=loose.constraints + (BlockedInterval("change", "participant", "Alice", 12, 14),))
    return loose, tight, impossible, repair, original


def verify():
    loose, tight, impossible, repair, original = examples()
    assert validate_schedule(loose, original).hard_feasible
    assert validate_schedule(tight, original).hard_feasible
    RepairCase(loose, original, "Alice unavailable 15:00-16:00", repair)
    context = RepairContext(original)
    # Independent capacity certificate: two one-hour meetings have one room-hour.
    confined = [a for a in impossible.activities if a.id in ("M2", "M3")]
    assert all(a.resource_ids == ("Room",) and a.availability == (Window(4, 6),) for a in confined)
    assert all(a.duration_slots <= 2 for a in confined)
    assert sum(a.duration_slots for a in confined) > 2
    records = []
    for spec, expected in ((loose, "OPTIMAL"), (tight, "OPTIMAL"),
                           (impossible, "INFEASIBLE"), (repair, "OPTIMAL")):
        ctx = context if spec.task_type == "repair" else None
        result = solve(spec, SolverLimits(), ctx)
        if result.status != expected:
            raise AssertionError((spec.instance_id, result.status))
        checked = validate_schedule(spec, result.schedule, ctx) if result.schedule else None
        if checked and not checked.hard_feasible:
            raise AssertionError("Solver output fails independent validation")
        records.append({"id": spec.instance_id, "specification": spec.to_dict(),
                        "status": result.status,
                        "schedule": result.schedule.starts() if result.schedule else None,
                        "objective": asdict(result.objectives) if result.objectives else None,
                        "gold_valid": checked.hard_feasible if checked else None})
    fixed_others = original.starts()
    legal = []
    for start in range(16):
        candidate = schedule({**fixed_others, "A3": start})
        if validate_schedule(repair, candidate, context).hard_feasible:
            legal.append(start)
    # A3's old start is blocked, so >=1 move is required. With all others held,
    # slot 14 is the only feasible new start: (moved=1, shift=2) is optimal.
    assert legal == [14]
    assert records[-1]["schedule"] == {**fixed_others, "A3": 14}
    assert records[-1]["objective"] == {"preference_penalty": 1, "moved_count": 1, "total_shift_slots": 2}
    return {
        "format_version": "1.0", "evidence_class": "offline illustrative qualification; no LLM evaluation",
        "new_model_calls": 0, "slot_minutes": 30,
        "scope": "One Monday 09:00-17:00, two participants, one room, eight activities lasting 1-2 hours. Not a five-day/hourly implementation.",
        "original_schedule": fixed_others, "examples": records,
        "independent_checks": {"original_and_tight_witnesses_valid": True,
            "unsat_room_workload_slots": 4, "unsat_room_capacity_slots": 2,
            "only_A3_repair_start_with_others_fixed": legal,
            "repair_forced_moved_lower_bound": 1},
        "repair_summary": {"changed_activities": ["A3"],
            "unchanged_activities": sorted(k for k in fixed_others if k != "A3"),
            "moved_count": 1, "total_shift_slots": 2, "total_shift_minutes": 60,
            "changed_activity_occupancy_cells": 4,
            "note": "Two start-shift slots differ from four changed occupancy cells (two vacated plus two occupied). Bob's B2 remains at 15:00 while Alice's A3 moves to 16:00."},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New JSON output path")
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print("Verified loose/tight SAT, capacity-certified UNSAT and minimal repair; no model calls.")


if __name__ == "__main__":
    main()
