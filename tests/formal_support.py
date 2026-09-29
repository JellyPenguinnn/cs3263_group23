"""Tiny, independently enumerated mathematical expectations for formal-core tests."""

from itertools import product

from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, Precedence,
    PreferredStart, ProblemSpec, ReleaseTime, Window,
)


def tiny(*, task_type="generation", constraints=()):
    windows = (Window(0, 4),)
    return ProblemSpec("1.0", "tiny", task_type, 4, 30, "2026-10-05T09:00:00+08:00", "+08:00",
                       (Entity("P", windows),), (Entity("R", windows),),
                       (Activity("A", 1, ("P",), ("R",), windows),
                        Activity("B", 1, ("P",), ("R",), windows)), tuple(constraints))


def enumerate_answers(spec, old=None):
    """Enumerate the full Cartesian product, without compiler/domain/objective helpers."""
    answers = []
    for times in product(range(spec.horizon_slots), repeat=len(spec.activities)):
        starts = dict(zip((a.id for a in spec.activities), times))
        ends = {a.id: starts[a.id] + a.duration_slots for a in spec.activities}
        valid = all(ends[a.id] <= spec.horizon_slots for a in spec.activities)
        for activity in spec.activities:
            sets = [activity.availability]
            sets += [p.availability for p in spec.participants if p.id in activity.participant_ids]
            sets += [r.availability for r in spec.resources if r.id in activity.resource_ids]
            for allowed in sets:
                valid &= any(w.start <= starts[activity.id] and ends[activity.id] <= w.end for w in allowed)
        for index, left in enumerate(spec.activities):
            for right in spec.activities[index + 1:]:
                shared = set(left.participant_ids) & set(right.participant_ids) or set(left.resource_ids) & set(right.resource_ids)
                if shared:
                    valid &= ends[left.id] <= starts[right.id] or ends[right.id] <= starts[left.id]
        penalty = 0
        for c in spec.constraints:
            if type(c) is ReleaseTime:
                valid &= starts[c.activity_id] >= c.slot
            elif type(c) is Deadline:
                valid &= ends[c.activity_id] <= c.slot
            elif type(c) is FixedStart:
                valid &= starts[c.activity_id] == c.slot
            elif isinstance(c, Precedence):
                valid &= ends[c.before] <= starts[c.after]
            elif isinstance(c, BlockedInterval):
                for activity in spec.activities:
                    used = activity.participant_ids if c.target_kind == "participant" else activity.resource_ids
                    if c.target_id in used:
                        valid &= ends[activity.id] <= c.start or starts[activity.id] >= c.end
            elif isinstance(c, PreferredStart):
                if starts[c.activity_id] < c.start or starts[c.activity_id] >= c.end:
                    penalty += c.weight
        if valid:
            objective = (penalty,) if old is None else (
                sum(starts[key] != old[key] for key in starts),
                sum(abs(starts[key] - old[key]) for key in starts), penalty)
            answers.append((objective, starts))
    return answers
