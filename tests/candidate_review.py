"""Independent arithmetic review of F3 development gold; never human sign-off.

This test/review helper neither calls CP-SAT nor uses production legal-domain or
objective helpers. It reuses the established test-only arithmetic enumerator.
"""

import argparse
from collections import Counter
from dataclasses import replace
from itertools import product
import json
from math import prod
from pathlib import Path

from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.scoring import digest
from scheduling.schema import BlockedInterval, Deadline, FixedStart, Precedence
from tests.formal_support import assignment_objective


def unary_domains(spec):
    """Project to each activity, dropping binary rules but retaining unary facts."""
    domains = {}
    for activity in spec.activities:
        constraints = tuple(
            c
            for c in spec.constraints
            if not isinstance(c, Precedence)
            and (isinstance(c, BlockedInterval) or c.activity_id == activity.id)
        )
        projection = replace(
            spec,
            task_type="generation",
            activities=(activity,),
            constraints=constraints,
        )
        domains[activity.id] = tuple(
            start
            for start in range(spec.horizon_slots)
            if assignment_objective(projection, {activity.id: start}) is not None
        )
    return domains


def contradiction(spec, domains):
    """Check the three declared construction mechanisms using integer arithmetic."""
    for key, domain in domains.items():
        if not domain:
            return {
                "mechanism": "unary_availability",
                "activities": [key],
                "reason": "No start satisfies all unary requirements",
            }
    activities = {a.id: a for a in spec.activities}
    fixed = [c for c in spec.constraints if type(c) is FixedStart]
    for left in fixed:
        for right in fixed:
            if left.activity_id == right.activity_id:
                continue
            a, b = activities[left.activity_id], activities[right.activity_id]
            shared = bool(
                set(a.participant_ids) & set(b.participant_ids)
                or set(a.resource_ids) & set(b.resource_ids)
            )
            if (
                shared
                and left.slot < right.slot + b.duration_slots
                and right.slot < left.slot + a.duration_slots
            ):
                return {
                    "mechanism": "shared_resource_collision",
                    "activities": [a.id, b.id],
                    "rules": [left.id, right.id],
                    "intervals": [
                        [left.slot, left.slot + a.duration_slots],
                        [right.slot, right.slot + b.duration_slots],
                    ],
                }
    for edge in (c for c in spec.constraints if isinstance(c, Precedence)):
        for anchor in (c for c in fixed if c.activity_id == edge.before):
            lower = (
                anchor.slot
                + activities[edge.before].duration_slots
                + activities[edge.after].duration_slots
            )
            for deadline in (
                c
                for c in spec.constraints
                if type(c) is Deadline and c.activity_id == edge.after
            ):
                if lower > deadline.slot:
                    return {
                        "mechanism": "precedence_deadline",
                        "activities": [edge.before, edge.after],
                        "rules": [anchor.id, edge.id, deadline.id],
                        "earliest_successor_end": lower,
                        "deadline": deadline.slot,
                    }
    return None


def review_case(case, max_assignments=60_000):
    if type(max_assignments) is not int or not 0 <= max_assignments <= 200_000:
        raise ValueError("Enumeration cap must be an integer in 0..200000")
    spec = case.problem
    old = case.original_schedule.starts() if case.context else None
    if old is not None and assignment_objective(case.original_problem, old) is None:
        raise ValueError("Original schedule fails independent arithmetic")
    domains = unary_domains(spec)
    combinations = prod(map(len, domains.values()))
    proof = contradiction(spec, domains)
    result = {
        "case_id": case.case_id,
        "case_sha256": digest(case),
        "label": case.expected_label,
        "unary_domain_product": combinations,
        "original_witness_checked": old is not None,
        "contradiction": proof,
        "optimality_check": "not_applicable",
    }
    if case.expected_label == "UNSAT":
        if proof is None:
            raise ValueError("UNSAT has no independent construction certificate")
        return result
    if case.expected_label != "SAT" or case.witness is None or proof is not None:
        raise ValueError("SAT requires a witness and no contradiction")
    objective = assignment_objective(spec, case.witness.starts(), old)
    if objective is None or objective != case.expected_objective:
        raise ValueError("Witness or claimed objective fails independent arithmetic")
    result["witness_objective"] = objective
    if combinations > max_assignments:
        result["optimality_check"] = "not_checked_assignment_cap"
        return result
    best, feasible = None, 0
    for times in product(*domains.values()):
        value = assignment_objective(spec, dict(zip(domains, times)), old)
        if value is not None:
            feasible += 1
            best = value if best is None else min(best, value)
    if best != objective:
        raise ValueError("Claimed optimum differs from exhaustive arithmetic")
    result.update(
        optimality_check="exhaustive", feasible_assignments=feasible, optimum=best
    )
    return result


def review_packet(cases, manifest, max_assignments=60_000):
    records = {r["case_id"]: r for r in manifest["cases"]}
    if (
        len(records) != len(manifest["cases"])
        or len(cases) != manifest["case_count"]
        or len({c.case_id for c in cases}) != len(cases)
        or {c.case_id for c in cases} != set(records)
    ):
        raise ValueError("Review requires the exact complete packet")
    reviewed = []
    for case in cases:
        row = records[case.case_id]
        if case.split != "development" or row["sha256"] != digest(case):
            raise ValueError("Review accepts only unchanged declared development cases")
        result = review_case(case, max_assignments)
        if (
            result["contradiction"]
            and result["contradiction"]["mechanism"] != row["mechanism"]
        ):
            raise ValueError(
                "Declared contradiction mechanism is not independently supported"
            )
        reviewed.append(result)
    return {
        "evidence": "automated independent arithmetic, not human review or model performance",
        "manifest_sha256": digest(manifest),
        "case_count": len(cases),
        "max_assignments_per_case": max_assignments,
        "labels": dict(Counter(r["label"] for r in reviewed)),
        "optimality_checks": dict(Counter(r["optimality_check"] for r in reviewed)),
        "human_review": "pending",
        "cases": reviewed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-assignments", type=int, default=60_000)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; retain the prior receipt")
    result = review_packet(
        load_cases(args.cases),
        json.loads(args.manifest.read_text()),
        args.max_assignments,
    )
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
