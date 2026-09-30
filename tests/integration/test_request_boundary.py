"""Full provider-message audit; evaluator IDs must not supply label hints."""

from dataclasses import replace
import json

import pytest

from scheduling.evaluation.benchmark import (
    generate_development, generate_development_v2, generate_development_v3,
    render, tiny_fixtures,
)
from scheduling.pipelines.direct import build_messages
from scheduling.pipelines.solver_augmented import build_extraction_messages


@pytest.mark.parametrize("version", [1, 2, 3])
def test_development_messages_only_contain_common_public_facts(version):
    if version == 1:
        cases = tiny_fixtures() + generate_development(3263)
    else:
        generator = generate_development_v2 if version == 2 else generate_development_v3
        cases, _, selection = generator(3262 + version)
        assert selection["quota_complete"]
    for case in cases:
        for variant in ("canonical", "paraphrase", "reordered"):
            view = render(case, variant, 3263)
            a = build_messages(
                view.text, task_type=view.task_type,
                required_activity_ids=view.activity_ids,
                original_schedule=view.original_schedule.to_list() if view.original_schedule else None,
            )
            b = build_extraction_messages(view)
            public_a, public_b = json.loads(a[1].content), json.loads(b[1].content)
            assert public_b.pop("instance_id") == "request"
            assert public_b.pop("task_type") == view.task_type
            assert public_b == public_a
            for label in ("private-SAT", "private-UNSAT"):
                changed = replace(view, instance_id=label, variant_id="private-selection-stratum")
                assert build_extraction_messages(changed) == b
            assert set(public_a) == {"description", "activity_ids"} | (
                {"original_schedule"} if view.task_type == "repair" else set()
            )
