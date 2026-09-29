"""Auditable split registries for fresh source groups; no retagging tuning data."""

import random
from scheduling.evaluation.cases import check_case_set
from scheduling.evaluation.scoring import digest


def allocate_fresh_groups(
    group_ids, *, development_count, seed, used_development_groups=()
):
    """Plan a split before generating/inspecting outcomes; reject reused tuning groups."""
    groups = sorted(group_ids)
    if len(set(groups)) != len(groups) or any(
        not isinstance(g, str) or not g for g in groups
    ):
        raise ValueError("Fresh group IDs must be unique nonempty strings")
    if set(groups) & set(used_development_groups):
        raise ValueError(
            "Previously used development groups cannot enter a fresh held-out allocation"
        )
    if (
        type(development_count) is not int
        or not 0 <= development_count <= len(groups)
        or type(seed) is not int
    ):
        raise ValueError("Invalid split allocation")
    random.Random(seed).shuffle(groups)
    return {
        group: ("development" if i < development_count else "test")
        for i, group in enumerate(groups)
    }


def benchmark_manifest(cases, *, generation_seed, rendering_seed):
    cases = check_case_set(tuple(cases))
    return {
        "format_version": "1.0",
        "status": "development_draft_not_frozen",
        "generation_seed": generation_seed,
        "rendering_seed": rendering_seed,
        "human_fixture_review": "pending",
        "human_language_review": "pending",
        "case_count": len(cases),
        "group_count": len({c.group_id for c in cases}),
        "cases": [
            {
                "case_id": c.case_id,
                "group_id": c.group_id,
                "split": c.split,
                "sha256": digest(c),
                "kind": c.kind,
                "sweep": c.sweep,
                "level": c.level,
            }
            for c in cases
        ],
        "definitions": {
            "unary_slack": "Number of legal individual starts after duration, activity/entity windows, releases, deadlines, fixed starts and blocked intervals; excludes precedence and pairwise capacity.",
            "interaction_density": "Distinct unordered activity pairs coupled by shared participants/resources or precedence, divided by all distinct activity pairs.",
            "resource_contention": "Activity pairs sharing at least one resource divided by all distinct activity pairs; separate from participant contention.",
        },
        "selection": {
            "constructed": len(cases),
            "excluded": 0,
            "policy": "No selection using model performance; unresolved solver references remain explicitly unresolved in run records",
        },
        "limitations": [
            "Generated development sweep levels are coupled, not causal interventions.",
            "Generation cases carry constructed SAT witnesses; this is not the balanced held-out matrix.",
            "No human-written realistic scenarios are claimed.",
        ],
    }
