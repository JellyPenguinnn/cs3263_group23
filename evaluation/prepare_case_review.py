"""Create a reviewer-only case/text/proof packet; never approve or run a model.

The input directory is an existing prepare_final_candidates.py output. Gold data
in this packet must not be supplied to a scheduling model or used as public prose.
"""

import argparse
import csv
from pathlib import Path

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.runner import read, write_new
from scheduling.evaluation.scoring import check_reference, digest
from scheduling.schema import to_data


def prepare_review(source, output):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = prepare_review(args.source, args.output)
    print({k: result[k] for k in ("case_count", "source_mode", "human_review")})


if __name__ == "__main__":
    main()
