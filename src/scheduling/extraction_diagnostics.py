"""Evaluator-only structural differences. Never feed gold back into inference."""

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json

from scheduling.schema import ProblemSpec


@dataclass(frozen=True)
class FieldDifference:
    path: str
    kind: str
    expected: object
    actual: object


@dataclass(frozen=True)
class ConstraintDifference:
    kind: str
    expected: dict | None
    actual: dict | None
    count: int


@dataclass(frozen=True)
class SpecComparison:
    structurally_equivalent: bool
    mismatches: tuple[str, ...]
    omitted_constraints: int
    invented_constraints: int
    differences: tuple[FieldDifference, ...] = ()
    constraint_differences: tuple[ConstraintDifference, ...] = ()
    format_version: str = "2.0"


def _rows(spec, name):
    result = {}
    for item in getattr(spec, name):
        row = asdict(item)
        # Whole-window containment forbids merging even adjacent windows.
        row["availability"] = sorted((w.start, w.end) for w in item.availability)
        for key in ("participant_ids", "resource_ids"):
            if key in row:
                row[key] = sorted(row[key])
        result[item.id] = row
    return result


def _constraints(spec):
    return Counter(
        json.dumps(
            {"type": c.kind, **{k: v for k, v in asdict(c).items() if k != "id"}},
            sort_keys=True,
        )
        for c in spec.constraints
    )


def _anchor(encoded):
    record = json.loads(encoded)
    kind = record["type"]
    if kind == "precedence":
        return kind, tuple(sorted((record["before"], record["after"])))
    if kind == "blocked":
        return kind, record["target_kind"], record["target_id"]
    return kind, record["activity_id"]


def _constraint_differences(missing, extra):
    missing, extra = missing.copy(), extra.copy()
    groups = defaultdict(lambda: ([], []))
    for encoded in missing:
        groups[_anchor(encoded)][0].append(encoded)
    for encoded in extra:
        groups[_anchor(encoded)][1].append(encoded)
    changes = []
    for key in sorted(groups):
        left, right = groups[key]
        # Pair only a unique unmatched typed shape on each side. Constraint IDs
        # are arbitrary; several candidates must remain unmatched for review.
        if len(left) == len(right) == 1:
            before, after = left[0], right[0]
            count = min(missing[before], extra[after])
            changes.append(
                ConstraintDifference(
                    "altered", json.loads(before), json.loads(after), count
                )
            )
            missing[before] -= count
            extra[after] -= count
    for kind, counter in (("omitted", missing), ("invented", extra)):
        for encoded, count in sorted(counter.items()):
            if count:
                changes.append(
                    ConstraintDifference(
                        kind,
                        json.loads(encoded) if kind == "omitted" else None,
                        json.loads(encoded) if kind == "invented" else None,
                        count,
                    )
                )
    return tuple(changes)


def compare_specifications(gold: ProblemSpec, extracted: ProblemSpec) -> SpecComparison:
    """Keep v1 summary/count meanings; add v2 typed structural review detail.

    IDs/order of constraints normalize away; multiplicity and weights do not.
    Alteration pairing never changes legacy omitted/invented totals. These are
    structural differences, not proofs of semantic inequivalence or causation.
    """
    mismatches, differences = [], []
    for name in (
        "schema_version",
        "task_type",
        "horizon_slots",
        "slot_minutes",
        "horizon_start",
        "timezone",
    ):
        before, after = getattr(gold, name), getattr(extracted, name)
        if before != after:
            mismatches.append(name)
            differences.append(FieldDifference("$." + name, "altered", before, after))
    for name in ("activities", "participants", "resources"):
        expected, actual = _rows(gold, name), _rows(extracted, name)
        if expected != actual:
            mismatches.append(name)
        for key in sorted(expected.keys() | actual.keys()):
            path = f"$.{name}[id={json.dumps(key)}]"
            if key not in actual:
                differences.append(
                    FieldDifference(path, "omitted", expected[key], None)
                )
            elif key not in expected:
                differences.append(FieldDifference(path, "invented", None, actual[key]))
            else:
                for field in sorted(expected[key]):
                    if expected[key][field] != actual[key][field]:
                        differences.append(
                            FieldDifference(
                                path + "." + field,
                                "altered",
                                expected[key][field],
                                actual[key][field],
                            )
                        )
    expected, actual = _constraints(gold), _constraints(extracted)
    missing, extra = expected - actual, actual - expected
    omitted, invented = sum(missing.values()), sum(extra.values())
    if omitted or invented:
        mismatches.append("constraints")
    return SpecComparison(
        not mismatches,
        tuple(mismatches),
        omitted,
        invented,
        tuple(differences),
        _constraint_differences(missing, extra),
    )
