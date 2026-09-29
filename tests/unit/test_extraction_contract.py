"""Parser-enforced examples and safe diagnostics; failures are never corrected."""

from dataclasses import fields, replace
import json
import re

import pytest

from scheduling.extraction_diagnostics import compare_specifications
from scheduling.pipelines.solver_augmented import (
    build_extraction_messages,
    run_solver_augmented,
)
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.schema import (
    Activity,
    Deadline,
    Entity,
    NaturalLanguageView,
    Precedence,
    PreferredStart,
    ProblemSpec,
    SchemaError,
    Window,
    to_data,
    CONSTRAINT_TYPES,
)
from scheduling.solver import SolverLimits
from tests.formal_support import tiny


def public_view():
    return NaturalLanguageView(
        "tiny",
        "canonical",
        "generation",
        "Only A and B, exactly as described",
        ("A", "B"),
        None,
    )


@pytest.mark.parametrize("namespace", ["participants", "resources"])
def test_extra_capacity_has_exact_path_and_no_value_echo(namespace):
    data = tiny().to_dict()
    data[namespace][0]["capacity"] = "never echo this private value"
    raw = json.dumps(data)
    result = run_solver_augmented(
        public_view(),
        ModelConfig("offline", 1024),
        SolverLimits(),
        provider_complete=lambda *_: ModelResponse(raw, "offline", 0, ()),
    )
    assert result.status == "INVALID_OUTPUT" and result.solve_result is None
    assert result.model_response.content == raw
    detail = result.schema_diagnostics[0]
    assert detail.path == f"$.{namespace}[0].capacity"
    assert detail.code == "object_fields" and detail.unsupported_fields == ("capacity",)
    assert detail.format_version == "1.0"
    assert "never echo" not in str(detail) and "never echo" not in result.diagnostics[0]
    assert "capacity" in result.diagnostics[0]


@pytest.mark.parametrize(
    "mutation,path,code",
    [
        (
            lambda d: d["activities"][0].pop("duration_slots"),
            "$.activities[0].duration_slots",
            "object_fields",
        ),
        (
            lambda d: d["activities"][0].update(duration_slots=True),
            "$.activities[0].duration_slots",
            "invalid_integer",
        ),
        (
            lambda d: d["activities"][0].update(participant_ids=["missing"]),
            "$.activities[0].participant_ids[0]",
            "dangling_reference",
        ),
        (
            lambda d: d["participants"][0].update(
                availability=[{"start": 2, "end": 1}]
            ),
            "$.participants[0].availability[0].end",
            "invalid_window",
        ),
        (
            lambda d: d["constraints"].append({"type": "travel"}),
            "$.constraints[0].type",
            "unsupported_constraint",
        ),
    ],
)
def test_schema_error_locations(mutation, path, code):
    data = tiny().to_dict()
    mutation(data)
    with pytest.raises(SchemaError) as caught:
        ProblemSpec.from_dict(data)
    assert caught.value.detail.path == path and caught.value.detail.code == code


@pytest.mark.parametrize(
    "raw,code",
    [
        ('{"x":1,"x":2}', "duplicate_key"),
        ('{"x":NaN}', "nonfinite_number"),
        ("bad JSON", "invalid_json"),
    ],
)
def test_json_ambiguity_codes(raw, code):
    with pytest.raises(SchemaError) as caught:
        ProblemSpec.from_json(raw)
    assert caught.value.detail.code == code


def test_prompt_example_and_exact_constraint_fields_match_parser():
    prompt = build_extraction_messages(public_view())[0].content
    example = prompt.split("BEGIN_SCHEMA_EXAMPLE\n")[1].split("\nEND_SCHEMA_EXAMPLE")[0]
    spec = ProblemSpec.from_json(example)
    assert spec.instance_id == "FORMAT_EXAMPLE" and len(spec.activities) == 1
    shapes = [
        json.loads(line) for line in prompt.splitlines() if line.startswith('{"type":')
    ]
    assert {s["type"] for s in shapes} == set(CONSTRAINT_TYPES)
    for shape in shapes:
        cls = CONSTRAINT_TYPES[shape["type"]]
        assert set(shape) == {"type"} | {f.name for f in fields(cls)}
        cls(**{k: v for k, v in shape.items() if k != "type"})
    assert "NO capacity field" in prompt
    result = run_solver_augmented(
        public_view(),
        ModelConfig("offline", 1024),
        SolverLimits(),
        provider_complete=lambda *_: ModelResponse(example, "offline", 0, ()),
    )
    assert result.status == "INVALID_OUTPUT"  # Copied example is never a valid answer.


def test_field_differences_and_unique_typed_alterations():
    gold = tiny(constraints=(Deadline("d", "A", 4), Precedence("p", "A", "B")))
    changed = replace(
        gold,
        activities=(replace(gold.activities[0], duration_slots=2), gold.activities[1]),
        constraints=(Deadline("new", "A", 3), Precedence("reverse", "B", "A")),
    )
    result = compare_specifications(gold, changed)
    assert result.omitted_constraints == result.invented_constraints == 2
    assert result.differences[0].path == '$.activities[id="A"].duration_slots'
    assert (result.differences[0].expected, result.differences[0].actual) == (1, 2)
    assert all(
        d.kind == "altered" and d.count == 1 for d in result.constraint_differences
    )
    assert result.format_version == "2.0"


def test_ambiguous_correspondence_remains_unmatched_and_counts_multiplicity():
    gold = tiny(
        constraints=(
            PreferredStart("p1", "A", 0, 1, 1),
            PreferredStart("p2", "A", 1, 2, 2),
        )
    )
    changed = replace(
        gold,
        constraints=(
            PreferredStart("p3", "A", 2, 3, 3),
            PreferredStart("p4", "A", 2, 3, 3),
        ),
    )
    result = compare_specifications(gold, changed)
    assert result.omitted_constraints == result.invented_constraints == 2
    assert all(d.kind != "altered" for d in result.constraint_differences)
    assert [d.count for d in result.constraint_differences if d.kind == "invented"] == [
        2
    ]


def test_window_normalization_does_not_merge_adjacent_windows():
    gold = tiny()
    split = replace(
        gold,
        activities=(
            replace(gold.activities[0], availability=(Window(0, 2), Window(2, 4))),
            gold.activities[1],
        ),
    )
    assert not compare_specifications(gold, split).structurally_equivalent
    reordered = replace(
        split,
        activities=(
            replace(
                split.activities[0],
                availability=tuple(reversed(split.activities[0].availability)),
            ),
            split.activities[1],
        ),
    )
    assert compare_specifications(split, reordered).structurally_equivalent


def test_missing_entity_is_reported_by_id():
    gold = replace(
        tiny(), participants=tiny().participants + (Entity("Q", (Window(0, 4),)),)
    )
    detail = compare_specifications(gold, tiny()).differences[0]
    assert detail.path == '$.participants[id="Q"]' and detail.kind == "omitted"
