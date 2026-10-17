#!/usr/bin/env python3
"""Derive the balanced comparison from immutable, checksum-verified archives.

No inference or rescoring: the archived analysis is joined to the original
completed responses and public requests, then summarized without exclusions.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tarfile

from build_difficulty_comparison import ARMS, MODELS, aggregate, distribution, normalized_settings, resources, unit
from verify_evidence import ROOT, verify_archive

PROFILES = ("neither", "deadline_only", "fixed_start_only", "both")


def profile(case):
    types = {constraint["type"] for constraint in case["problem"]["constraints"]}
    return ("both" if "deadline" in types and "fixed_start" in types else
            "deadline_only" if "deadline" in types else
            "fixed_start_only" if "fixed_start" in types else "neither")


def build(manifest):
    if len(manifest["archives"]) != 2 or {e["id"] for e in manifest["archives"]} != set(MODELS):
        raise ValueError("Expected exactly the Qwen3.6 and GLM balanced archives")
    result = {
        "format_version": "1.0", "new_model_calls": 0,
        "scope": "Shared-service synthetic/AI-assisted development; generation only; not held out",
        "dataset": "balanced-generation-v1", "models": {},
        "limitations": [
            "All scheduling failures remain in the primary 48-attempt method denominator.",
            "48 cases are related constructions from three families, not 48 independent samples.",
            "Only canonical wording was measured; human prose/gold review remains pending.",
            "Balanced deadline/fixed-start presence removes that specific label shortcut, not all benchmark biases.",
            "Objective matching is conditional on valid gold-SAT schedules and proven reference objectives.",
            "Format noncompliance is not automatically a scheduling reasoning failure.",
            "The GLM transport failure has no model response or reported tokens; missing usage is unknown.",
            "Shared-service timings include failures and do not isolate model speed or hardware effects.",
        ],
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "helper_sha256": hashlib.sha256((ROOT / "scripts/build_difficulty_comparison.py").read_bytes()).hexdigest(),
    }
    shared_settings = shared_inputs = None
    for entry in manifest["archives"]:
        key = entry["id"]
        verify_archive(ROOT / entry["path"], entry)
        with tarfile.open(ROOT / entry["path"]) as archive:
            raw = archive.extractfile("analysis.json").read()
            analysis = json.loads(raw)
            rows = analysis["rows"]
            if (len(rows) != 96 or len({unit(r) for r in rows}) != 96
                    or any(r["study_block"] != "controlled" or r["task_type"] != "generation"
                           or r["variant_id"] != "canonical" or r["repeat"] != 0 for r in rows)):
                raise ValueError("Expected 96 unique canonical, single-repeat generation observations")
            diagnostics = {tuple(d["unit"]): d for d in analysis["interpretation"]["attempt_diagnostics"]}
            if set(diagnostics) != {unit(r) for r in rows}:
                raise ValueError("Incomplete diagnostic records")
            base = "runs/controlled/controlled"
            cases_raw = archive.extractfile(base + "/cases.json").read()
            cases = json.loads(cases_raw)["cases"]
            by_case = {c["case_id"]: c for c in cases}
            if len(cases) != 48 or len(by_case) != 48 or len({c["group_id"] for c in cases}) != 3:
                raise ValueError("Expected 48 cases from three construction families")
            profile_labels = {p: dict(Counter(c["expected_label"] for c in cases if profile(c) == p)) for p in PROFILES}
            if any(counts != {"SAT": 6, "UNSAT": 6} for counts in profile_labels.values()):
                raise ValueError("Constraint-presence profiles are not 6 SAT/6 UNSAT each")
            contract = json.load(archive.extractfile(base + "/manifest.json"))["contract"]
            inputs = {"cases": hashlib.sha256(cases_raw).hexdigest(), "requests": {}}
            records = {}
            for member in archive.getnames():
                if not member.startswith(base + "/attempts/"):
                    continue
                record = json.load(archive.extractfile(member))
                if record["state"] != "completed":
                    raise ValueError("Pending response cannot enter completed comparison")
                payload = record["payload"]
                identity = payload["identity"]
                u = ("controlled",) + tuple(identity[k] for k in ("case_id", "variant_id", "repeat", "approach"))
                if u in records:
                    raise ValueError("Duplicate completed response")
                response = payload["pipeline_result"]["model_response"]
                if response["returned_model"] not in (None, MODELS[key]):
                    raise ValueError("Returned model mismatch")
                if response["returned_model"] is None and not response["error"]:
                    raise ValueError("Response without model identity or provider error")
                if len(response["attempts"]) != 1:
                    raise ValueError("Unexpected retry or missing provider request")
                if any(a["returned_model"] not in (None, MODELS[key]) for a in response["attempts"]):
                    raise ValueError("Attempt-level model mismatch")
                records[u] = payload
                inputs["requests"]["|".join(map(str, u))] = {
                    "prompt": payload["pipeline_result"]["prompt_sha256"],
                    "public_view": payload["public_view"],
                }
            if set(records) != set(diagnostics):
                raise ValueError("Analysis and completed response units differ")
            for row in rows:
                if row["gold_label"] != by_case[row["case_id"]]["expected_label"]:
                    raise ValueError("Analysis gold label differs from archived case")
                if row["returned_model"] != records[unit(row)]["pipeline_result"]["model_response"]["returned_model"]:
                    raise ValueError("Analysis response identity differs from archived response")
            settings = normalized_settings(analysis["settings"])
            if shared_settings is None:
                shared_settings, shared_inputs = settings, inputs
            elif settings != shared_settings or inputs != shared_inputs:
                raise ValueError("Non-model settings, cases or paired prompts/public views differ")
        model = {
            "model": MODELS[key], "requested_model": analysis["settings"]["model"]["model"],
            "archive": entry["path"], "archive_sha256": entry["sha256"],
            "analysis_sha256": hashlib.sha256(raw).hexdigest(),
            "case_bundle_sha256": contract["case_bundle_sha256"],
            "overall_by_method": {}, "resources": {}, "profiles": {}, "backend_coverage": {},
            "failure_catalogue": [], "controlled_paired": analysis["primary_controlled"]["paired"],
            "backend_fingerprints": analysis["backend_fingerprints"],
            "unique_cases": 48, "construction_families": 3, "profile_labels": profile_labels,
        }
        for arm in ARMS:
            subset = [r for r in rows if r["approach"] == arm]
            if len(subset) != 48 or {r["case_id"] for r in subset} != set(by_case):
                raise ValueError("Each method must attempt all 48 cases exactly once")
            returned = [r for r in subset if r["returned_model"] is not None]
            model["overall_by_method"][arm] = {
                **aggregate(subset, diagnostics),
                "secondary_returned_answer_acceptance": {
                    "accepted": sum(r["accepted"] for r in returned), "returned_answers": len(returned),
                    "note": "Secondary only; the primary denominator retains provider failures.",
                },
                "structurally_equivalent_extractions": sum(
                    bool((r.get("extraction_comparison") or {}).get("structurally_equivalent")) for r in subset),
                "extractions_compared": sum(r.get("extraction_comparison") is not None for r in subset),
            }
            model["resources"][arm] = {
                **resources(subset),
                "pipeline_seconds": distribution([dict(r["timings"]).get("total_seconds") for r in subset]),
            }
            fingerprints = [p["execution"]["system_fingerprint"] for r in subset for p in r["provider_attempts"]]
            model["backend_coverage"][arm] = {
                "reported": sum(f is not None for f in fingerprints), "requests": len(fingerprints),
                "missing": sum(f is None for f in fingerprints),
                "counts": dict(sorted(Counter(f for f in fingerprints if f is not None).items())),
            }
        for p in PROFILES:
            model["profiles"][p] = {arm: aggregate(
                [r for r in rows if r["approach"] == arm and profile(by_case[r["case_id"]]) == p], diagnostics)
                for arm in ARMS}
        for row in sorted(rows, key=unit):
            diagnostic = diagnostics[unit(row)]
            if not row["accepted"] or diagnostic["objective_status"] == "proven_suboptimal":
                pipeline = records[unit(row)]["pipeline_result"]
                model["failure_catalogue"].append({
                    **diagnostic, "gold_label": row["gold_label"], "declared_status": row["declared_status"],
                    "profile": profile(by_case[row["case_id"]]), "objective_values": row["objective_values"],
                    "objective_gaps": row["objective_gaps"],
                    "violations": (row.get("validation") or {}).get("violations", []),
                    "pipeline_diagnostics": pipeline["diagnostics"],
                    "provider_attempts": row["provider_attempts"],
                    "model_seconds": row["model_seconds"],
                })
        result["models"][key] = model
    result["comparison_checks"] = {
        "source_runtime_and_non_model_settings_match": True,
        "all_96_paired_prompt_hashes_and_public_views_match": True,
        "case_bundles_match": True, "four_profiles_each_6_sat_6_unsat": True,
        "all_returned_identities_match": True, "no_pending_requests_or_retries": True,
        "allowed_differences": ["requested/required model identity", "observed capability and backend metadata"],
        "shared_settings": shared_settings,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/balanced-evidence-manifest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/summary/balanced-comparison-20261017.json")
    args = parser.parse_args()
    result = build(json.loads(args.manifest.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Verified and summarized all 192 balanced scheduling attempts; zero model calls.")


if __name__ == "__main__":
    main()
