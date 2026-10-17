"""Trace-backed descriptive analysis; never infer a model's hidden reasoning.

These exports supplement the existing scoring contract. They do not change
acceptance, rerun solvers, remove failures or certify human interpretation.
"""

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

from scheduling.evaluation.scoring import digest
from scheduling.schema import ProblemSpec, to_data
from scheduling.validation import validate_schedule


def unit(row):
    return tuple(row[k] for k in ("study_block", "case_id", "variant_id", "repeat", "approach"))


def objective_status(row):
    """A later lexicographic gap is comparable only after earlier objectives tie."""
    if row["gold_label"] != "SAT" or not row["gold_valid"]:
        return "not_comparable"
    gaps = row["objective_gaps"]
    count = 3 if row["task_type"] == "repair" else 1
    if any(g is not None and g > 0 for g in gaps):
        return "proven_suboptimal"
    if len(gaps) == count and all(g == 0 for g in gaps):
        return "reference_match"
    return "partially_proven"


def semantic_witness_check(case, result, gold_reference):
    """Test concrete schedules against both specs; no search or equivalence claim.

    A distinguishing witness proves the two predicates differ on that schedule.
    Matching these few witnesses does not prove global semantic equivalence.
    """
    if result.get("extracted_spec") is None:
        return {"status": "no_extracted_specification"}
    extracted = ProblemSpec.from_dict(result["extracted_spec"])
    frame = ("task_type", "horizon_slots", "slot_minutes", "horizon_start", "timezone")
    changed = [key for key in frame if getattr(case.problem, key) != getattr(extracted, key)]
    if changed or {a.id for a in extracted.activities} != {a.id for a in case.problem.activities}:
        return {"status": "incompatible_frame_or_activity_set", "changed_frame_fields": changed}
    checks = []
    for name, schedule in (("candidate", result.get("schedule")),
                           ("gold_reference_witness", gold_reference["result"].get("schedule"))):
        if schedule is None:
            continue
        gold = validate_schedule(case.problem, schedule, case.context)
        candidate = validate_schedule(extracted, schedule, case.context)
        checks.append({"witness": name, "schedule": schedule,
                       "gold_validation": to_data(gold), "extracted_validation": to_data(candidate),
                       "distinguishes_hard_feasibility": gold.hard_feasible != candidate.hard_feasible})
    return {"status": "witnesses_checked", "checks": checks,
            "hard_feasibility_difference_demonstrated": any(c["distinguishes_hard_feasibility"] for c in checks),
            "limitation": "Finite hard-feasibility witnesses only; matching checks do not establish global equivalence, preference equivalence or the cause of model behaviour."}


def observed_reasons(row):
    """Record observed symptoms separately from unverified causal explanations."""
    meanings = {
        "provider_error": "The provider attempt failed; this is not evidence of a reasoning failure.",
        "invalid_output": "The answer failed the required output/schema contract.",
        "solver_model_error": "The compiler/solver rejected the extracted model.",
        "solver_limit": "The solver returned no definite SAT/UNSAT result within its limits.",
        "model_unknown": "The direct model declined to decide SAT/UNSAT.",
        "gold_invalid_schedule": "The returned schedule violates the evaluator's gold requirements.",
        "false_unsat": "UNSAT was returned for a gold problem with a validated feasible witness.",
        "unresolved_reference": "The reference is unresolved; this attempt cannot support a correctness claim.",
        "accepted": "The answer met the primary gold acceptance criterion.",
    }
    reasons = [meanings[row["category"]]]
    violations = sorted({v["category"] for v in (row.get("validation") or {}).get("violations", [])})
    if violations:
        reasons.append("Gold validation found: " + ", ".join(violations) + ".")
    comparison = row.get("extraction_comparison")
    if comparison and not comparison["structurally_equivalent"]:
        reasons.append("The extracted specification differs structurally from gold. This alone does not prove semantic error or causation.")
    semantic = row.get("semantic_witness_check", {})
    if semantic.get("hard_feasibility_difference_demonstrated"):
        reasons.append("Independent validation found a concrete schedule accepted by one specification and rejected by the other, demonstrating a hard-feasibility difference on that witness.")
    if semantic.get("status") == "incompatible_frame_or_activity_set":
        reasons.append("The extracted frame or activity set differs; schedule witnesses cannot be compared as the same task coordinates.")
    quality = objective_status(row)
    if quality == "proven_suboptimal":
        reasons.append("The valid schedule is worse at a proven comparable objective stage; primary acceptance is unchanged.")
    elif quality == "partially_proven":
        reasons.append("A valid schedule exists, but complete reference-objective matching is not established.")
    return reasons


def stratified_outcomes(rows):
    """Include block/tier aggregates and the exact fine cells; no small-cell CIs."""
    output = []
    levels = {
        "block": ("study_block", "approach"),
        "tier": ("study_block", "level", "approach"),
        "cell": ("study_block", "level", "sweep", "task_type", "gold_label", "variant_id", "approach"),
    }
    dimensions = levels["cell"]
    for scope, keys in levels.items():
        buckets = defaultdict(list)
        for row in rows:
            buckets[tuple(row[k] for k in keys)].append(row)
        for key, items in sorted(buckets.items(), key=str):
            sat = [r for r in items if r["gold_label"] == "SAT"]
            unsat = [r for r in items if r["gold_label"] == "UNSAT"]
            accepted = sum(r["accepted"] is True for r in items)
            known = sum(r["accepted"] is not None for r in items)
            statuses = Counter(objective_status(r) for r in items)
            comparisons = [r["extraction_comparison"] for r in items if r.get("extraction_comparison")]
            output.append({
                "scope": scope, **{d: "all" for d in dimensions}, **dict(zip(keys, key)),
                "attempts": len(items), "families": len({r["group_id"] for r in items}),
                "accepted": accepted, "rejected": sum(r["accepted"] is False for r in items),
                "unscored": len(items) - known,
                "acceptance_rate": accepted / len(items) if known == len(items) else None,
                "gold_sat_attempts": len(sat), "gold_sat_valid": sum(r["gold_valid"] for r in sat),
                "gold_unsat_attempts": len(unsat),
                "correct_unsat": sum(r["pipeline_status"] == "UNSAT" for r in unsat),
                "reference_matches": statuses["reference_match"],
                "proven_suboptimal": statuses["proven_suboptimal"],
                "objective_partially_proven": statuses["partially_proven"],
                "objective_comparable": statuses["reference_match"] + statuses["proven_suboptimal"],
                "schema_valid_extractions": len(comparisons),
                "structural_mismatches": sum(not c["structurally_equivalent"] for c in comparisons),
                "witness_demonstrated_mismatches": sum(r.get("semantic_witness_check", {}).get("hard_feasibility_difference_demonstrated", False) for r in items),
                "failure_categories": dict(sorted(Counter(r["category"] for r in items if r["accepted"] is False).items())),
            })
    return output


def paired_observations(rows):
    buckets = defaultdict(dict)
    for row in rows:
        key = unit(row)[:-1]
        if row["approach"] in buckets[key]:
            raise ValueError("Duplicate method observation in interpretation")
        buckets[key][row["approach"]] = row
    output = []
    for key, pair in sorted(buckets.items()):
        a, b = pair.get("direct"), pair.get("solver_augmented")
        item = dict(zip(("study_block", "case_id", "variant_id", "repeat"), key))
        item["complete_pair"] = a is not None and b is not None
        item["outcome"] = (
            "missing_method" if not item["complete_pair"] else
            "unscored" if a["accepted"] is None or b["accepted"] is None else
            "both_accepted" if a["accepted"] and b["accepted"] else
            "direct_only" if a["accepted"] else "solver_only" if b["accepted"] else "neither_accepted"
        )
        for name, r in (("direct", a), ("solver_augmented", b)):
            item[name + "_objective"] = objective_status(r) if r else None
            item[name + "_category"] = r["category"] if r else None
        ta = dict(a["timings"]).get("total_seconds") if a else None
        tb = dict(b["timings"]).get("total_seconds") if b else None
        item["total_seconds_B_minus_A"] = tb - ta if ta is not None and tb is not None else None
        output.append(item)
    return output


def interpret(rows, evidence):
    """All issues plus deterministic success examples, with no performance tuning."""
    rows = sorted(rows, key=unit)
    seen, examples, diagnostics = set(), [], []
    for row in rows:
        comparison = row.get("extraction_comparison")
        quality = objective_status(row)
        issue = row["accepted"] is not True or quality in ("proven_suboptimal", "partially_proven") or (
            comparison and not comparison["structurally_equivalent"])
        success_key = tuple(row[k] for k in ("study_block", "level", "approach"))
        selection = "all_observed_issues" if issue else "deterministic_success_example"
        reasons = observed_reasons(row)
        diagnostics.append({"unit": list(unit(row)), "category": row["category"],
                            "objective_status": quality, "observations": reasons,
                            "trace": evidence[unit(row)]["trace"]})
        if not issue and success_key in seen:
            continue
        if not issue:
            seen.add(success_key)
        examples.append({
            "example_id": digest(unit(row)), "selection": selection,
            "identity": {k: row[k] for k in ("study_block", "case_id", "variant_id", "repeat", "approach", "task_type", "level", "sweep", "gold_label")},
            "accepted": row["accepted"], "objective_status": quality, "observations": reasons,
            "validation": row.get("validation"), "extraction_comparison": comparison,
            "objective_values": row["objective_values"], "objective_gaps": row["objective_gaps"],
            "semantic_witness_check": row.get("semantic_witness_check"),
            "human_interpretation": "pending", **evidence[unit(row)],
        })
    return {
        "format_version": "1.0", "scope": "descriptive_observations_not_causal_or_human_review",
        "notes": [
            "All attempts remain in denominators, including provider failures. No inference or solver reruns are performed by analysis.",
            "Block and tier rows pool task/label cells explicitly; fine cells may contain one observation and have no population confidence claim.",
            "Related renderings and generation/repair instances share families; rows across summary scopes must not be added together.",
            "Casebook includes every rejection, unscored answer, structural mismatch and valid nonmatching/unproved objective, plus the first clean success per block/tier/method in sorted identity order.",
            "Examples are selected for interpretation, not for estimating rates. Structural mismatches are not automatic causal explanations.",
            "Gold data in the casebook is evaluator-only and must never be passed back to either method during measured inference.",
        ],
        "strata": stratified_outcomes(rows), "paired_attempts": paired_observations(rows),
        "attempt_diagnostics": diagnostics, "casebook": examples,
    }


def export_interpretation(result, directory: Path):
    """Readable companion plus complete machine-readable evidence and tables."""
    analysis = result["interpretation"]
    tables = {"study_strata": analysis["strata"], "paired_attempts": analysis["paired_attempts"]}
    tables["tier_resources"] = [
        {**{k: v for k, v in item.items() if k != "distributions"}, "measurement": name, **stats}
        for item in result["tier_resources"] for name, stats in item["distributions"].items()
    ]
    for name, values in tables.items():
        if not values:
            continue
        with (directory / (name + ".csv")).open("x", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows({k: json.dumps(v, sort_keys=True) if isinstance(v, (list, dict)) else v
                              for k, v in item.items()} for item in values)
    with (directory / "casebook.json").open("x", encoding="utf-8") as out:
        json.dump(analysis, out, sort_keys=True, ensure_ascii=False, allow_nan=False)
    lines = ["# Study interpretation companion", "", f"Evidence class: `{result['evidence']}`. Model: `{result['settings']['model']['model']}`.", "",
             "Generated from verified recorded attempts. Human interpretation remains pending.", ""]
    lines.extend("- " + note for note in analysis["notes"])
    lines += ["", "## Failure-inclusive block outcomes", "",
              "| Block | Method | Accepted / attempted | Rate | Valid SAT / SAT | Correct UNSAT / UNSAT | Objective matches / comparable |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in analysis["strata"]:
        if row["scope"] != "block":
            continue
        percentage = f"{100 * row['acceptance_rate']:.1f}%" if row["acceptance_rate"] is not None else "unscored present"
        lines.append(f"| {row['study_block']} | {row['approach']} | {row['accepted']}/{row['attempts']} | {percentage} | {row['gold_sat_valid']}/{row['gold_sat_attempts']} | {row['correct_unsat']}/{row['gold_unsat_attempts']} | {row['reference_matches']}/{row['objective_comparable']} |")
    lines += ["", "Objective matching is conditional on gold-valid SAT schedules with comparable reference stages; 0/0 means unavailable, not zero performance.", "",
              "## Evidence review", "", "Full request, original schedule, gold specification, model output, extracted specification and checksummed trace pointers are in `casebook.json`. Paths identify reproduction-archive members.", ""]
    for item in analysis["casebook"]:
        identity = item["identity"]
        lines += [f"### Example `{item['example_id'][:12]}`", "",
                  f"`{identity['case_id']}` / {identity['variant_id']} / {identity['approach']} / {identity['level']}. Selection: {item['selection']}.", ""]
        lines.extend("- " + reason for reason in item["observations"])
        lines += [f"- Attempt record: `{item['trace']['attempt_member']}`", "",
                  "Review: Which exact request fact explains the observation? Does the evidence establish a cause or only a difference? What does the paired method do, and what scope limitation follows?", ""]
    (directory / "interpretation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
