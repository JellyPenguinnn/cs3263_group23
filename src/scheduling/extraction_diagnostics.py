"""Evaluator-only structural extraction comparison; never fed back into inference."""

from collections import Counter
from dataclasses import asdict, dataclass
import json

from scheduling.schema import ProblemSpec


@dataclass(frozen=True)
class SpecComparison:
    structurally_equivalent: bool
    mismatches: tuple[str, ...]
    omitted_constraints: int
    invented_constraints: int


def compare_specifications(gold: ProblemSpec, extracted: ProblemSpec) -> SpecComparison:
    """Ignore constraint IDs and ordering, retaining multiplicity (including weights).

    A mismatch is diagnostic, not proof of causation or inequivalent feasible sets.
    Alternate encodings require human semantic review. This is not a validator.
    """
    mismatches = []
    for name in ("schema_version", "task_type", "horizon_slots", "slot_minutes", "horizon_start", "timezone"):
        if getattr(gold, name) != getattr(extracted, name):
            mismatches.append(name)
    for name in ("activities", "participants", "resources"):
        def rows(spec):
            result = {}
            for item in getattr(spec, name):
                row = asdict(item)
                row["availability"] = sorted((w.start, w.end) for w in item.availability)
                for key in ("participant_ids", "resource_ids"):
                    if key in row:
                        row[key] = sorted(row[key])
                result[item.id] = row
            return result
        if rows(gold) != rows(extracted):
            mismatches.append(name)
    def constraints(spec):
        return Counter(json.dumps({"type": c.kind, **{k: v for k, v in asdict(c).items() if k != "id"}}, sort_keys=True)
                       for c in spec.constraints)
    expected, actual = constraints(gold), constraints(extracted)
    omitted = sum((expected - actual).values())
    invented = sum((actual - expected).values())
    if omitted or invented:
        mismatches.append("constraints")
    return SpecComparison(not mismatches, tuple(mismatches), omitted, invented)
