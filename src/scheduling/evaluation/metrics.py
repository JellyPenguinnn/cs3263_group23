"""Denominator-explicit summaries and paired, group-preserving uncertainty."""

from collections import Counter, defaultdict
import csv
import math
from pathlib import Path
import random


def rate(successes, total):
    return {
        "numerator": successes,
        "denominator": total,
        "rate": successes / total if total else None,
    }


def wilson(successes, total):
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [max(0, center - radius), min(1, center + radius)]


def paired(rows, *, seed=3263, resamples=10000):
    pairs = defaultdict(dict)
    for row in rows:
        key = (row["case_id"], row["variant_id"], row["repeat"])
        if row["approach"] in pairs[key]:
            raise ValueError("Duplicate paired attempt")
        pairs[key][row["approach"]] = row
    counts = Counter()
    groups = defaultdict(list)
    incomplete = unresolved = 0
    for pair in pairs.values():
        if set(pair) != {"direct", "solver_augmented"}:
            incomplete += 1
            continue
        a, b = pair["direct"], pair["solver_augmented"]
        if a["group_id"] != b["group_id"] or a["gold_label"] != b["gold_label"]:
            raise ValueError("Pair metadata mismatch")
        if a["accepted"] is None or b["accepted"] is None:
            unresolved += 1
            continue
        if (
            a["returned_model"]
            and b["returned_model"]
            and a["returned_model"] != b["returned_model"]
        ):
            raise ValueError("Do not pair different returned model identities")
        av, bv = bool(a["accepted"]), bool(b["accepted"])
        counts[
            "both" if av and bv else "only_A" if av else "only_B" if bv else "neither"
        ] += 1
        groups[a["group_id"]].append(int(bv) - int(av))
    deltas = [v for values in groups.values() for v in values]
    interval = None
    if len(groups) >= 10:
        rng = random.Random(seed)
        keys = sorted(groups)
        samples = []
        for _ in range(resamples):
            sampled = [v for key in rng.choices(keys, k=len(keys)) for v in groups[key]]
            samples.append(100 * sum(sampled) / len(sampled))
        samples.sort()
        interval = [
            samples[int(0.025 * (resamples - 1))],
            samples[int(0.975 * (resamples - 1))],
        ]
    return {
        "counts": {k: counts[k] for k in ("both", "only_A", "only_B", "neither")},
        "pair_count": len(deltas),
        "group_count": len(groups),
        "incomplete_pairs": incomplete,
        "unresolved_pairs": unresolved,
        "B_minus_A_percentage_points": (
            100 * sum(deltas) / len(deltas) if deltas else None
        ),
        "cluster_bootstrap_95": interval,
        "seed": seed,
        "resamples": resamples,
        "interval_note": (
            "descriptive_only_fewer_than_10_groups"
            if len(groups) < 10
            else "paired_group_resampling"
        ),
    }


def summarize(rows):
    rows = list(rows)
    summaries = []
    buckets = defaultdict(list)
    for r in rows:
        # Backend/config groups remain separate; config hashes differ between approaches.
        buckets[
            (
                r["kind"],
                r["task_type"],
                r["variant_id"],
                r["repeat"],
                r["approach"],
                r["model_config_sha256"],
            )
        ].append(r)
    for key, items in sorted(buckets.items(), key=lambda kv: str(kv[0])):
        labelled = [r for r in items if r["gold_label"] != "UNRESOLVED"]
        sat = [r for r in labelled if r["gold_label"] == "SAT"]
        unsat = [r for r in labelled if r["gold_label"] == "UNSAT"]
        groups = len({r["group_id"] for r in items})
        accepted = sum(r["accepted"] is True for r in labelled)
        tokens = {}
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            values = [u.get(field) for r in items for u in r["usage"]]
            tokens[field] = {
                "reported_sum": (
                    sum(v for v in values if v is not None)
                    if any(v is not None for v in values)
                    else None
                ),
                "reported_attempts": sum(v is not None for v in values),
                "all_provider_attempts": len(values),
            }
        violations = Counter(
            v["category"]
            for r in items
            if r["validation"]
            for v in r["validation"]["violations"]
        )
        summaries.append(
            {
                "subset": dict(
                    zip(
                        (
                            "kind",
                            "task_type",
                            "variant_id",
                            "repeat",
                            "approach",
                            "config_sha256",
                        ),
                        key,
                    )
                ),
                "primary_controlled": key[0] == "controlled"
                and key[2] == "canonical"
                and key[3] == 0,
                "returned_models": sorted(
                    {
                        r["returned_model"]
                        for r in items
                        if r["returned_model"] is not None
                    }
                ),
                "attempt_count": len(items),
                "group_count": groups,
                "accepted_answer": rate(accepted, len(labelled)),
                "sat_validity": rate(sum(r["gold_valid"] for r in sat), len(sat)),
                "unsat_accuracy": rate(
                    sum(r["pipeline_status"] == "UNSAT" for r in unsat), len(unsat)
                ),
                "unresolved_reference_count": len(items) - len(labelled),
                "status_counts": dict(Counter(r["pipeline_status"] for r in items)),
                "confusion": dict(
                    Counter(
                        r["gold_label"] + "->" + r["pipeline_status"] for r in items
                    )
                ),
                "category_counts": dict(Counter(r["category"] for r in items)),
                "violation_counts": dict(violations),
                "accepted_wilson_95": (
                    wilson(accepted, len(labelled))
                    if len({r["group_id"] for r in labelled}) == len(labelled)
                    and len(labelled) >= 10
                    else None
                ),
                "objective_gaps": [
                    {
                        "count": len(values),
                        "mean": sum(values) / len(values) if values else None,
                    }
                    for i in range(3 if key[1] == "repair" else 1)
                    for values in [
                        [
                            r["objective_gaps"][i]
                            for r in items
                            if r["objective_gaps"][i] is not None
                        ]
                    ]
                ],
                "tokens": tokens,
                "requests": sum(r["request_count"] for r in items),
                "uncertain_reservations": sum(
                    r.get("uncertain_reservations", 0) for r in items
                ),
                "extraction_mismatches": sum(
                    bool(r["extraction_comparison"])
                    and not r["extraction_comparison"]["structurally_equivalent"]
                    for r in items
                ),
                "latency_seconds": [
                    {
                        "component": component,
                        "count": len(values),
                        "mean": sum(values) / len(values) if values else None,
                    }
                    for component in (
                        "total_seconds",
                        "extraction_seconds",
                        "solver_seconds",
                    )
                    for values in [
                        [
                            dict(r["timings"])[component]
                            for r in items
                            if component in dict(r["timings"])
                        ]
                    ]
                ],
                "cost": None,
            }
        )
    paired_groups = defaultdict(list)
    for row in rows:
        paired_groups[
            (row["kind"], row["task_type"], row["variant_id"], row["repeat"])
        ].append(row)
    comparisons = []
    for key, items in sorted(paired_groups.items()):
        # Never silently pool reruns with different per-approach configurations.
        for approach in ("direct", "solver_augmented"):
            if (
                len(
                    {
                        r["model_config_sha256"]
                        for r in items
                        if r["approach"] == approach
                        and r["category"] != "interrupted_or_uncertain"
                    }
                )
                > 1
            ):
                raise ValueError(
                    "Multiple configs in paired subset; summarize runs separately"
                )
        if (
            len({r["returned_model"] for r in items if r["returned_model"] is not None})
            > 1
        ):
            raise ValueError(
                "Returned backend changed; analyze model groups separately"
            )
        comparisons.append({"subset": key, **paired(items)})
    return {
        "evidence": "recomputed_from_saved_attempts",
        "subsets": summaries,
        "paired": comparisons,
        "robustness": robustness(rows),
        "difficulty": difficulty_rates(rows),
    }


def export_tables(rows, directory: Path):
    directory.mkdir(parents=True, exist_ok=False)
    fields = [
        "case_id",
        "group_id",
        "task_type",
        "sweep",
        "level",
        "variant_id",
        "repeat",
        "approach",
        "gold_label",
        "pipeline_status",
        "gold_valid",
        "accepted",
        "category",
        "objective_values",
        "objective_gaps",
    ]
    with (directory / "attempts.csv").open("x", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def robustness(rows):
    lookup = {}
    transitions = []
    for row in rows:
        key = (row["case_id"], row["approach"], row["repeat"], row["variant_id"])
        if key in lookup:
            raise ValueError("Duplicate robustness unit")
        lookup[key] = row
    for key, variant in lookup.items():
        if key[-1] == "canonical":
            continue
        canonical = lookup.get((*key[:3], "canonical"))
        if canonical is None:
            continue
        if (
            canonical["returned_model"]
            and variant["returned_model"]
            and canonical["returned_model"] != variant["returned_model"]
        ):
            raise ValueError("Backend mismatch across renderings")
        transitions.append(
            {
                "case_id": key[0],
                "group_id": variant["group_id"],
                "approach": key[1],
                "repeat": key[2],
                "variant_id": key[3],
                "canonical_accepted": canonical["accepted"],
                "variant_accepted": variant["accepted"],
                "canonical_objectives": canonical["objective_values"],
                "variant_objectives": variant["objective_values"],
            }
        )
    return transitions


def difficulty_rates(rows):
    groups = defaultdict(list)
    for r in rows:
        if (
            r["kind"] == "controlled"
            and r["variant_id"] == "canonical"
            and r["repeat"] == 0
        ):
            groups[(r["task_type"], r["sweep"], r["level"], r["approach"])].append(r)
    return [
        {
            "task_type": key[0],
            "sweep": key[1],
            "level": key[2],
            "approach": key[3],
            "accepted_answer": rate(
                sum(r["accepted"] is True for r in rs),
                sum(r["accepted"] is not None for r in rs),
            ),
            "sat_validity": rate(
                sum(r["gold_valid"] for r in rs if r["gold_label"] == "SAT"),
                sum(r["gold_label"] == "SAT" for r in rs),
            ),
            "realized_mean_unary_slack": sum(
                r["difficulty"]["mean_unary_slack"] for r in rs
            )
            / len(rs),
            "realized_mean_interaction_density": sum(
                r["difficulty"]["interaction_density"] for r in rs
            )
            / len(rs),
            "realized_mean_resource_contention": sum(
                r["difficulty"]["resource_contention"] for r in rs
            )
            / len(rs),
        }
        for key, rs in sorted(groups.items(), key=lambda kv: str(kv[0]))
    ]
