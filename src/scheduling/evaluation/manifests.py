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


def structural_fingerprint(spec, *, include_objective=False, original_schedule=None):
    """ID/order-invariant colored-graph fingerprint, conservatively grouped.

    Equal hashes are possible graph-refinement collisions, not a proof of
    isomorphism. Treat them as related rather than independent samples. This
    does not claim to detect all mathematically equivalent encodings.
    """
    from dataclasses import asdict
    from collections import defaultdict
    from scheduling.schema import Precedence, PreferredStart

    labels, edges = {}, defaultdict(list)

    def node(key, label):
        labels[key] = digest(label)

    def edge(left, right, role):
        edges[left].append((role, right))
        edges[right].append(("reverse_" + role, left))

    for kind in ("participants", "resources"):
        for row in getattr(spec, kind):
            node(
                (kind, row.id),
                [kind, sorted((w.start, w.end) for w in row.availability)],
            )
    old = original_schedule.starts() if original_schedule else {}
    for row in spec.activities:
        key = ("activities", row.id)
        node(
            key,
            [
                "activity",
                row.duration_slots,
                sorted((w.start, w.end) for w in row.availability),
                old.get(row.id),
            ],
        )
        for kind, ids in (
            ("participants", row.participant_ids),
            ("resources", row.resource_ids),
        ):
            for ident in ids:
                edge(key, (kind, ident), "uses_" + kind)
    # Reachability removes transitive edges from acyclic precedence graphs.
    # Cyclic graphs are retained intact, avoiding unsafe deletion of every arc.
    arcs = {(c.before, c.after) for c in spec.constraints if isinstance(c, Precedence)}

    def reachable(start, end, excluded=None):
        todo, seen = [start], set()
        while todo:
            current = todo.pop()
            if current in seen:
                continue
            seen.add(current)
            for a, b in arcs:
                if a == current and (a, b) != excluded:
                    if b == end:
                        return True
                    todo.append(b)
        return False

    cyclic = any(reachable(b, a) for a, b in arcs)
    kept = arcs if cyclic else {(a, b) for a, b in arcs if not reachable(a, b, (a, b))}
    for a, b in sorted(kept):
        edge(("activities", a), ("activities", b), "precedes")
    for i, rule in enumerate(spec.constraints):
        if isinstance(rule, Precedence) or (
            isinstance(rule, PreferredStart) and not include_objective
        ):
            continue
        row = asdict(rule)
        row.pop("id")
        target = row.pop("activity_id", None)
        kind = row.pop("target_kind", None)
        entity = row.pop("target_id", None)
        key = ("rule", i)
        node(key, [rule.kind, row])
        if target is not None:
            edge(key, ("activities", target), "activity")
        if entity is not None:
            edge(
                key,
                ("participants" if kind == "participant" else "resources", entity),
                "target",
            )
    colors = labels.copy()
    for _ in range(len(labels)):
        colors = {
            key: digest(
                [
                    labels[key],
                    sorted((role, colors[other]) for role, other in edges[key]),
                ]
            )
            for key in labels
        }
    return digest(
        {
            "horizon": [
                spec.horizon_slots,
                spec.slot_minutes,
                spec.horizon_start,
                spec.timezone,
            ],
            "colors": sorted(colors.values()),
        }
    )


def structural_audit(cases):
    """Detect shared hard structures across families, including original problems."""
    from collections import defaultdict

    cases = check_case_set(tuple(cases))
    hard, full, relations = defaultdict(list), defaultdict(list), defaultdict(set)
    for case in cases:
        key = structural_fingerprint(case.problem)
        hard[key].append(case.case_id)
        full[
            structural_fingerprint(
                case.problem,
                include_objective=True,
                original_schedule=case.original_schedule,
            )
        ].append(case.case_id)
        relations[key].add(case.group_id)
        if case.original_problem is not None:
            relations[structural_fingerprint(case.original_problem)].add(case.group_id)
    parent = {case.group_id: case.group_id for case in cases}

    def root(key):
        while parent[key] != key:
            key = parent[key]
        return key

    for groups in relations.values():
        ordered = sorted(groups)
        for key in ordered[1:]:
            a, b = sorted((root(ordered[0]), root(key)))
            parent[b] = a
    families = {key: root(key) for key in sorted(parent)}
    splits = defaultdict(set)
    for case in cases:
        splits[families[case.group_id]].add(case.split)
    return {
        "format_version": "1.0",
        "method": "colored_graph_refinement_conservative_families_not_semantic_equivalence",
        "hard_duplicate_sets": [v for _, v in sorted(hard.items()) if len(v) > 1],
        "objective_duplicate_sets": [v for _, v in sorted(full.items()) if len(v) > 1],
        "family_for_group": families,
        "cross_split_families": sorted(k for k, v in splits.items() if len(v) > 1),
    }


def benchmark_manifest_v2(
    cases, *, generation_seed, rendering_seed, selection, records, code_revision
):
    """Development provenance; review fields cannot be inferred from tests."""
    from collections import Counter
    from pathlib import Path
    import hashlib
    from scheduling.evaluation import benchmark
    from scheduling.evaluation.benchmark import difficulty, render

    cases = check_case_set(tuple(cases))
    if set(records) != {c.case_id for c in cases}:
        raise ValueError("Provenance must cover every case exactly")
    audit = structural_audit(cases)
    if audit["cross_split_families"]:
        raise ValueError("Related hard structures cross splits")
    return {
        "format_version": "2.0",
        "dataset_version": "controlled-v2-development",
        "schema_version": "1.0",
        "generator_version": "2.0",
        "generator_source_sha256": hashlib.sha256(
            Path(benchmark.__file__).read_bytes()
        ).hexdigest(),
        "code_revision": code_revision,
        "status": "development_draft_not_frozen",
        "generation_seed": generation_seed,
        "rendering_seed": rendering_seed,
        "human_fixture_review": "pending",
        "human_language_review": "pending",
        "case_count": len(cases),
        "group_count": len({c.group_id for c in cases}),
        "selection": selection,
        "structural_audit": audit,
        "cases": [
            {
                "case_id": c.case_id,
                "group_id": c.group_id,
                "source_family_id": audit["family_for_group"][c.group_id],
                "split": c.split,
                "sha256": digest(c),
                "kind": c.kind,
                "sweep": c.sweep,
                "level": c.level,
                "task_type": c.problem.task_type,
                "expected_label": c.expected_label,
                "realized_difficulty": difficulty(c.problem),
                "renderings": {
                    v: digest(render(c, v, rendering_seed))
                    for v in ("canonical", "paraphrase", "reordered")
                },
                **records[c.case_id],
            }
            for c in cases
        ],
        "counts": dict(
            Counter(
                f"{c.sweep}/{c.level}/{c.problem.task_type}/{c.expected_label}"
                for c in cases
            )
        ),
        "limitations": [
            "Procedural development data, not independently human-written realistic prose.",
            "Constructed interacting UNSAT uses a common two-activity resource conflict recipe.",
            "Sweeps have coupled covariates; realized measurements are not causal difficulty guarantees.",
            "Fingerprint collisions are conservatively related; arbitrary semantic equivalence requires review.",
        ],
    }



def benchmark_manifest_v3(cases, **kwargs):
    """Keep the version-2 provenance wire format for a distinct v3 dataset."""
    manifest = benchmark_manifest_v2(cases, **kwargs)
    manifest.update(
        dataset_version="challenge-v3-development", generator_version="3.0",
        limitations=[
            "Procedural binary-domain development challenges, not human-written realistic prose or a final test matrix.",
            "Three declared mechanisms; unary contradictions are simple controls, not evidence of difficult interaction reasoning.",
            "Sizes, durations and mechanisms have coupled covariates, not causal difficulty guarantees.",
            "Event/task/label variants share source families; repeated or translated structures are not independent samples.",
            "Fingerprint grouping does not prove or exhaust semantic equivalence; human review remains pending.",
        ],
    )
    return manifest
