"""Create a reviewer-only case/text/proof packet; never approve or run a model.

By default the input is an existing prepare_final_candidates.py output. Select
--source-mode difficulty-v1 for a prepared difficulty suite. Gold data in either
packet must not be supplied to a scheduling model or used as public prose.
"""

import argparse
from collections import Counter
import csv
import hashlib
from pathlib import Path

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.runner import read, write_new
from scheduling.evaluation.scoring import check_reference, digest
from scheduling.schema import to_data


def prepare_review(source, output, *, source_mode="candidate"):
    if source_mode == "difficulty-v1":
        return prepare_difficulty_review(source, output)
    if source_mode != "candidate":
        raise ValueError("Unsupported review source mode")
    source, output = Path(source), Path(output)
    cases = load_cases(source / "cases.json")
    manifest = read(source / "manifest.json")
    references = read(source / "references.json")
    rows = {r["case_id"]: r for r in manifest["cases"]}
    ids = {c.case_id for c in cases}
    if (len(rows) != len(manifest["cases"]) or len(cases) != manifest["case_count"]
            or set(rows) != ids or set(references) != ids):
        raise ValueError("Review requires the exact complete packet and references")
    seed = manifest["policy"]["rendering_seed"]
    records = []
    for case in cases:
        if rows[case.case_id]["sha256"] != digest(case):
            raise ValueError("Case differs from preparation manifest")
        label, values, proven = check_reference(case, references[case.case_id])
        if label != case.expected_label or label == "UNRESOLVED":
            raise ValueError("Review reference must match the declared resolved label")
        if label == "SAT" and (values != case.expected_objective
                or len(proven) != (3 if case.context else 1)):
            raise ValueError("Review reference must substantiate the declared optimum")
        views = {v: to_data(render(case, v, seed))
                 for v in ("canonical", "paraphrase", "reordered")}
        if any(rows[case.case_id]["renderings"].get(v) != digest(view)
               for v, view in views.items()):
            raise ValueError("Public text differs from preparation manifest")
        records.append((case, {
            "evidence": "reviewer_only_gold_and_text_not_model_input",
            "case_sha256": digest(case), "case": to_data(case),
            "reference": references[case.case_id], "public_views": views,
            "preparation": rows[case.case_id],
            "gold_review_status": "pending", "text_review_status": "pending",
        }))
    output.mkdir(parents=True, exist_ok=False)
    index = []
    for case, record in records:
        name = digest(case.case_id) + ".json"
        write_new(output / name, record)
        index.append({
            "case_id": case.case_id, "family_id": case.group_id,
            "task": case.problem.task_type, "expected_label": case.expected_label,
            "reviewer_file": name, "gold_reviewer": "", "text_reviewer": "",
            "gold_status": "pending", "canonical_status": "pending",
            "paraphrase_status": "pending", "reordered_status": "pending",
            "findings_and_decision_reference": "",
        })
    columns = (list(index[0]) if index else ["case_id", "gold_status"])
    with (output / "review-index.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(index)
    receipt = {
        "format_version": "1.0", "evidence": "pending_human_review_only",
        "case_count": len(cases), "source_manifest_sha256": digest(manifest),
        "source_case_bundle_sha256": digest(read(source / "cases.json")),
        "source_references_sha256": digest(references),
        "source_mode": manifest["mode"],
        "source_quota_complete": manifest["quota_complete"],
        "human_review": "pending",
        "instructions": [
            "Review gold constraints, SAT witness or sufficient UNSAT argument, and exact objective proof separately.",
            "For repair, check the original witness and unchanged frame/durations/assignments; verify the updated event and movement objective.",
            "Compare each public text with its own gold facts, clock conversion, fixed appointments, windows and objective; reject hidden hints and omissions.",
            "Record actual distinct reviewers and findings in a working copy of review-index.csv; this file is not an approval mechanism.",
            "Pilot review never converts development cases into held-out data. Final policy/data and real sign-offs remain separate.",
        ],
    }
    write_new(output / "review-packet.json", receipt)
    return receipt


def prepare_difficulty_review(source, output):
    """Recheck a difficulty suite offline and expose evidence for human review.

    This validates mathematical evidence, not the meaning or naturalness of its
    prose. All human gold and rendered-fact checks remain explicitly pending.
    """
    from scheduling.evaluation import difficulty_suite
    from scheduling.evaluation.benchmark import difficulty
    from scheduling.evaluation.cases import case_bundle
    from scheduling.evaluation.difficulty_suite import (
        VERSION, TIERS, SIZES, check_design, select_language, verify_certificate,
    )
    from scheduling.evaluation.manifests import structural_audit
    from scheduling.evaluation.scoring import reference
    from scheduling.solver import SolverLimits

    source, output = Path(source), Path(output)
    if output.exists():
        raise FileExistsError("Use a new reviewer-only output directory")
    source_names = ("controlled.json", "realistic.json", "manifest.json")
    source_hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                     for name in source_names}
    manifest = read(source / "manifest.json")
    controlled = load_cases(source / "controlled.json")
    realistic = load_cases(source / "realistic.json")
    cases = controlled + realistic
    check_design(controlled, realistic)
    ids = {case.case_id for case in cases}
    if len(ids) != len(cases) or set(manifest.get("proofs", {})) != ids:
        raise ValueError("Review requires every unique case and construction proof")
    bundles = {"controlled": digest(case_bundle(controlled)),
               "realistic": digest(case_bundle(realistic))}
    generator_hash = hashlib.sha256(Path(difficulty_suite.__file__).read_bytes()).hexdigest()
    if (manifest.get("dataset_version") != VERSION
            or manifest.get("case_bundle_sha256") != bundles
            or manifest.get("generator_sha256") != generator_hash):
        raise ValueError("Difficulty source identity differs from its manifest")
    language = select_language(controlled)
    language_ids = {case.case_id for case in language}
    counts = {
        "unique_cases": len(cases), "construction_families": len({c.group_id for c in cases}),
        "controlled_cases": len(controlled), "fictional_cases": len(realistic),
        "wording_bases": len(language), "additional_wording_conditions": 2 * len(language),
        "case_rendering_conditions": len(cases) + 2 * len(language),
        "scheduling_attempts_per_model": 2 * (len(cases) + 2 * len(language)),
        "both_models_scheduling_attempts": 4 * (len(cases) + 2 * len(language)),
    }
    audit = structural_audit(cases)
    families = audit["family_for_group"]
    if ({families[c.group_id] for c in controlled} & {families[c.group_id] for c in realistic}
            or counts["construction_families"] != 40
            or manifest.get("counts") != counts
            or manifest.get("tiers") != dict(zip(TIERS, SIZES))
            or manifest.get("language_case_ids") != [c.case_id for c in language]
            or manifest.get("language_task_label_counts") != dict(Counter(
                f"{c.problem.task_type}/{c.expected_label}" for c in language))
            or digest(manifest.get("structural_audit")) != digest(audit)):
        raise ValueError("Difficulty design or family evidence differs from its manifest")
    measured_difficulty = {c.case_id: difficulty(c.problem) for c in cases}
    if (digest(manifest.get("case_difficulty")) != digest(measured_difficulty)
            or any(0 in d["unary_start_counts"] for d in measured_difficulty.values())):
        raise ValueError("Difficulty evidence or nonempty unary-domain requirement failed")

    limits = SolverLimits(60)
    records = []
    required_certificate_fields = {
        "sat_witness": {"kind"},
        "resource_workload": {"kind", "activities", "resource", "deadline"},
        "critical_path": {"kind", "activities", "deadline"},
        "unit_slot_capacity": {"kind", "activities", "resource"},
    }
    for case in cases:
        proof = manifest["proofs"][case.case_id]
        if not isinstance(proof, dict):
            raise ValueError("Construction proof must be an object")
        cert = proof.get("certificate", {})
        if (not isinstance(cert, dict)
                or not isinstance(cert.get("kind"), str)
                or cert.get("kind") not in required_certificate_fields
                or set(cert) != required_certificate_fields[cert["kind"]]
                or (case.expected_label == "SAT") != (cert["kind"] == "sat_witness")
                or proof.get("problem_sha256") != digest(case.problem)
                or digest(proof.get("expected_objective")) != digest(case.expected_objective)):
            raise ValueError("Construction proof is incomplete or belongs to different gold")
        if cert["kind"] != "sat_witness" and (
                not isinstance(cert["activities"], list)
                or any(not isinstance(activity, str) for activity in cert["activities"])
                or ("deadline" in cert and type(cert["deadline"]) is not int)
                or ("resource" in cert and not isinstance(cert["resource"], str))):
            raise ValueError("Construction certificate fields have invalid types")
        if not verify_certificate(case.problem, cert, case.witness):
            raise ValueError("Independent construction certificate failed")
        fresh_reference = reference(case, limits)
        label, values, proven = check_reference(case, fresh_reference)
        if (label != case.expected_label or label == "UNRESOLVED"
                or (label == "SAT" and (values != case.expected_objective
                    or len(proven) != (3 if case.context else 1)))):
            raise ValueError("Fresh reference must substantiate the label and exact optimum")
        if (proof.get("independent_certificate_checked") is not True
                or proof.get("reference_status") != fresh_reference["result"]["status"]
                or proof.get("reference_optimality_proven") != fresh_reference["result"]["optimality_proven"]):
            raise ValueError("Fresh proof verification contradicts the manifest")
        views = {variant: to_data(render(case, variant, 3263))
                 for variant in ("canonical", "paraphrase", "reordered")}
        fact_checks = ("activity_duration_and_assignments", "availability_and_clock_conversion",
                       "all_hard_constraints", "preferences_and_objective", "original_schedule_and_update",
                       "equivalence_to_gold", "naturalness_and_ambiguity", "no_gold_or_evaluation_hints")
        records.append((case, {
            "evidence": "reviewer_only_gold_and_text_not_model_input",
            "case_sha256": digest(case), "case": to_data(case),
            "reference": fresh_reference, "public_views": views,
            "rendering_sha256": {v: digest(view) for v, view in views.items()},
            "construction_proof": proof,
            "offline_verification": {"independent_certificate_checked": True,
                "reference_recomputed": True, "reference_limits": to_data(limits),
                "reference_label": label, "proven_objective_stages": list(proven)},
            "gold_review_status": "pending", "text_review_status": "pending",
            "gold_review_checks": {key: "pending" for key in
                ("intended_constraints", "feasibility_argument", "objective_interpretation", "repair_context")},
            "rendered_fact_checks": {v: {key: "pending" for key in fact_checks} for v in views},
            "wording_block_selected": case.case_id in language_ids,
        }))

    if any(hashlib.sha256((source / name).read_bytes()).hexdigest() != expected
           for name, expected in source_hashes.items()):
        raise ValueError("Difficulty source changed during reviewer preparation")
    output.mkdir(parents=True, exist_ok=False)
    index = []
    for case, record in records:
        name = digest(case.case_id) + ".json"
        write_new(output / name, record)
        index.append({"case_id": case.case_id, "family_id": case.group_id,
            "kind": case.kind, "tier": case.level, "mechanism": case.sweep,
            "task": case.problem.task_type, "expected_label": case.expected_label,
            "wording_block_selected": case.case_id in language_ids, "reviewer_file": name,
            "gold_reviewer": "", "text_reviewer": "", "gold_status": "pending",
            "canonical_status": "pending", "paraphrase_status": "pending", "reordered_status": "pending",
            "findings_and_decision_reference": ""})
    with (output / "review-index.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(index[0]))
        writer.writeheader()
        writer.writerows(index)
    receipt = {
        "format_version": "1.0", "evidence": "pending_human_review_only",
        "source_mode": VERSION, "source_quota_complete": True,
        "case_count": len(cases), "source_manifest_sha256": digest(manifest),
        "source_case_bundle_sha256": bundles,
        "source_file_sha256": source_hashes,
        "counts": counts, "fresh_reference_solves": len(cases), "new_model_calls": 0,
        "human_review": "pending", "source_role": "project_generated_development",
        "instructions": [
            "Reviewer-only gold, witnesses and certificates must never be copied into model-visible prompts.",
            "Mathematical certificate checks and fresh reference solves do not establish prose faithfulness or human review.",
            "Review gold meaning, feasibility argument and objective interpretation separately from every rendered-fact checklist.",
            "For repairs compare original and updated specifications, original schedule, changed requirements and lexicographic priorities.",
            "Canonical text is scheduled for every case; only the ten selected controlled bases use the two additional wording conditions.",
            "Record actual reviewers and findings in a working copy. Unreviewed and ambiguous cases must remain explicit; no approvals are inferred.",
            "Review across all five tiers, three mechanisms, SAT/UNSAT and generation/repair; inspect all twenty fictional scenarios.",
            "These are development cases. Review does not create a held-out dataset or authorize inference.",
        ],
    }
    write_new(output / "review-packet.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-mode", choices=("candidate", "difficulty-v1"), default="candidate")
    args = parser.parse_args()
    result = prepare_review(args.source, args.output, source_mode=args.source_mode)
    print({k: result[k] for k in ("case_count", "source_mode", "human_review")})


if __name__ == "__main__":
    main()
