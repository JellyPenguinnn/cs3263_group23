"""Evaluator-only case metadata around the canonical problem types."""

from dataclasses import dataclass, fields
from pathlib import Path

from scheduling.schema import (
    ProblemSpec,
    RepairCase,
    RepairContext,
    Schedule,
    load_json,
    to_data,
)
from scheduling.validation import validate_schedule


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    group_id: str
    split: str
    kind: str
    sweep: str
    level: str
    problem: ProblemSpec
    original_problem: ProblemSpec | None = None
    original_schedule: Schedule | None = None
    event: str | None = None
    witness: Schedule | None = None
    expected_label: str | None = None
    expected_objective: tuple[int, ...] | None = None
    justification: str = "Pending independent human review"

    def __post_init__(self):
        if not all(
            isinstance(x, str) and x.strip()
            for x in (
                self.case_id,
                self.group_id,
                self.sweep,
                self.level,
                self.justification,
            )
        ):
            raise ValueError("Case metadata must be explicit")
        if self.split not in ("development", "test") or self.kind not in (
            "controlled",
            "realistic",
            "diagnostic",
        ):
            raise ValueError("Unsupported case subset")
        if self.problem.instance_id != self.case_id:
            raise ValueError("Case and problem IDs must agree")
        if self.problem.task_type == "repair":
            RepairCase(
                self.original_problem, self.original_schedule, self.event, self.problem
            )
            if not validate_schedule(
                self.original_problem, self.original_schedule
            ).hard_feasible:
                raise ValueError(
                    "Original schedule fails independent original-problem validation"
                )
            if (
                self.problem.horizon_start,
                self.problem.timezone,
                self.problem.horizon_slots,
            ) != (
                self.original_problem.horizon_start,
                self.original_problem.timezone,
                self.original_problem.horizon_slots,
            ):
                raise ValueError("Repair must keep a common slot origin and horizon")
        elif any(
            x is not None
            for x in (self.original_problem, self.original_schedule, self.event)
        ):
            raise ValueError("Generation case cannot have repair context")
        if self.expected_label not in (None, "SAT", "UNSAT"):
            raise ValueError("Expected label must be SAT, UNSAT or unresolved")
        if (
            self.witness
            and not validate_schedule(
                self.problem, self.witness, self.context
            ).hard_feasible
        ):
            raise ValueError("Witness fails independent validation")
        if self.expected_label == "UNSAT" and self.witness is not None:
            raise ValueError("UNSAT cannot have a witness")
        if self.expected_objective is not None:
            size = 3 if self.context else 1
            if len(self.expected_objective) != size or any(
                type(v) is not int or v < 0 for v in self.expected_objective
            ):
                raise ValueError("Invalid expected objective")

    @property
    def context(self):
        return (
            RepairContext(self.original_schedule)
            if self.original_schedule is not None
            else None
        )

    @classmethod
    def from_dict(cls, data):
        required = {"case_id", "group_id", "split", "kind", "sweep", "level", "problem"}
        if (
            not isinstance(data, dict)
            or not required <= set(data)
            or set(data) - {f.name for f in fields(cls)}
        ):
            raise ValueError("Missing or unsupported benchmark case fields")
        row = dict(data)
        row["problem"] = ProblemSpec.from_dict(row["problem"])
        if row.get("original_problem") is not None:
            row["original_problem"] = ProblemSpec.from_dict(row["original_problem"])
        for key in ("original_schedule", "witness"):
            if row.get(key) is not None:
                row[key] = Schedule.from_list(row[key])
        if row.get("expected_objective") is not None:
            if not isinstance(row["expected_objective"], list):
                raise ValueError("Expected objective must be an array")
            row["expected_objective"] = tuple(row["expected_objective"])
        return cls(**row)


@dataclass(frozen=True)
class AuthoredRendering:
    """Verbatim public prose; authorship and review metadata stay evaluator-only."""

    variant_id: str
    text: str
    creation_method: str
    author_reference: str
    rationale: str
    review_status: str = "pending"
    review_reference: str | None = None

    def __post_init__(self):
        if self.variant_id not in ("canonical", "paraphrase", "reordered"):
            raise ValueError("Unsupported authored rendering variant")
        if self.creation_method not in (
            "human_written",
            "llm_assisted",
            "external_adaptation",
        ):
            raise ValueError("Explicit authored-text provenance required")
        if not all(
            isinstance(v, str) and v.strip()
            for v in (self.text, self.author_reference, self.rationale)
        ):
            raise ValueError("Authored prose, author and rationale must be explicit")
        if self.review_status not in ("pending", "approved"):
            raise ValueError("Unsupported authored-text review status")
        if self.review_status == "approved":
            if (
                not isinstance(self.review_reference, str)
                or not self.review_reference.strip()
            ):
                raise ValueError("Approved text needs a review reference")
        elif self.review_reference is not None:
            raise ValueError("Pending text cannot carry an approval reference")

    @classmethod
    def from_dict(cls, data):
        required = {
            "variant_id",
            "text",
            "creation_method",
            "author_reference",
            "rationale",
        }
        if (
            not isinstance(data, dict)
            or not required <= set(data)
            or set(data) - {f.name for f in fields(cls)}
        ):
            raise ValueError("Missing or unsupported authored rendering fields")
        return cls(**data)


@dataclass(frozen=True)
class AuthoredBenchmarkCase(BenchmarkCase):
    """Opt-in v2 case bundle extension; legacy case serialization stays exact."""

    authored_renderings: tuple[AuthoredRendering, ...] = ()
    gold_author_reference: str = ""
    gold_review_reference: str | None = None

    def __post_init__(self):
        super().__post_init__()
        if (
            not isinstance(self.authored_renderings, tuple)
            or not self.authored_renderings
            or not all(
                isinstance(r, AuthoredRendering) for r in self.authored_renderings
            )
        ):
            raise ValueError("Authored case needs explicit renderings")
        variants = [r.variant_id for r in self.authored_renderings]
        if "canonical" not in variants or len(set(variants)) != len(variants):
            raise ValueError("Authored variants need one canonical and unique IDs")
        if (
            not isinstance(self.gold_author_reference, str)
            or not self.gold_author_reference.strip()
        ):
            raise ValueError("Gold authorship must be explicit")
        if self.gold_review_reference is not None and (
            not isinstance(self.gold_review_reference, str)
            or not self.gold_review_reference.strip()
        ):
            raise ValueError("Gold review reference must be nonempty when supplied")

    @classmethod
    def from_dict(cls, data):
        extra = {
            "authored_renderings",
            "gold_author_reference",
            "gold_review_reference",
        }
        if not isinstance(data, dict) or not isinstance(
            data.get("authored_renderings"), list
        ):
            raise ValueError("Authored renderings must be an array")
        base = BenchmarkCase.from_dict(
            {k: v for k, v in data.items() if k not in extra}
        )
        return cls(
            **{f.name: getattr(base, f.name) for f in fields(BenchmarkCase)},
            authored_renderings=tuple(
                AuthoredRendering.from_dict(r) for r in data["authored_renderings"]
            ),
            gold_author_reference=data.get("gold_author_reference", ""),
            gold_review_reference=data.get("gold_review_reference"),
        )


def check_case_set(cases):
    cases = tuple(cases)
    ids, groups = set(), {}
    for case in cases:
        if case.case_id in ids:
            raise ValueError("Duplicate case ID")
        ids.add(case.case_id)
        if case.group_id in groups and groups[case.group_id] != case.split:
            raise ValueError("Related cases cannot cross splits")
        groups[case.group_id] = case.split
    return tuple(cases)


def load_cases(path: Path):
    data = load_json(path.read_text(encoding="utf-8"))
    if (
        not isinstance(data, dict)
        or set(data) != {"format_version", "cases"}
        or data["format_version"] not in ("1.0", "2.0")
        or not isinstance(data["cases"], list)
    ):
        raise ValueError("Unsupported benchmark bundle")
    cases = []
    for row in data["cases"]:
        authored = isinstance(row, dict) and "authored_renderings" in row
        if authored and data["format_version"] != "2.0":
            raise ValueError("Authored prose requires case bundle version 2.0")
        cls = AuthoredBenchmarkCase if authored else BenchmarkCase
        cases.append(cls.from_dict(row))
    return check_case_set(tuple(cases))


def case_bundle(cases):
    cases = check_case_set(cases)
    version = (
        "2.0" if any(isinstance(c, AuthoredBenchmarkCase) for c in cases) else "1.0"
    )
    return {"format_version": version, "cases": [to_data(case) for case in cases]}
