#!/usr/bin/env python3
"""Validate and summarize completed diverse-generation evidence without inference.

Reads immutable analyses and original attempts. It checks their linkage and the
cross-model scientific contract, but does not substitute for independent replay.
Paths in the portable output are relative to the supplied evidence root.
"""
import argparse
from collections import Counter
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

from build_difficulty_comparison import (ARMS, MODELS, aggregate, distribution,
                                         normalized_settings, resources, unit)
from verify_evidence import ROOT

PHASES = {"qwen36": "parallel8-20261017-01", "glm53flash": "parallel4-glm-20261017-01"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def provider_failures(rows):
    counts = Counter()
    for row in rows:
        for request in row["provider_attempts"]:
            if request["error"]:
                transport = request["execution"].get("transport_error_kind")
                counts[transport or request["error"]] += 1
    return dict(sorted(counts.items()))


def resource_summary(rows):
    summary = resources(rows)
    summary["pipeline_seconds"] = distribution([dict(r["timings"]).get("total_seconds") for r in rows])
    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
        values = [sum(u[field] for u in r["usage"])
                  if r["usage"] and all(u[field] is not None for u in r["usage"]) else None for r in rows]
        summary[field] = {**distribution(values), "reported_sum": sum(v for v in values if v is not None)}
    return summary


def group_summary(rows, diagnostics):
    returned = [r for r in rows if r["returned_model"] is not None]
    return {**aggregate(rows, diagnostics), "provider_failures": provider_failures(rows),
            "secondary_returned_answer_acceptance": {
                "accepted": sum(r["accepted"] for r in returned), "returned_answers": len(returned),
                "note": "Secondary; all provider failures remain in primary denominators."}}


def build(evidence_root):
    result = {"format_version": "1.0", "dataset": "diverse-generation-v1", "new_model_calls": 0,
              "scope": "Synthetic/AI-assisted shared-service development evidence; generation only; not held out",
              "builder_sha256": digest(Path(__file__)),
              "helper_sha256": digest(ROOT / "scripts/build_difficulty_comparison.py"),
              "models": {}, "input_sha256": {},
              "limitations": [
                  "1,000 canonical cases per model are related constructions from ten families, not 1,000 independent families.",
                  "Each method has 500 SAT and 500 UNSAT cases; all failures remain in the 1,000-attempt primary denominator.",
                  "The 24 optional reordered conditions were not run; neither paraphrase robustness nor human review follows from this study.",
                  "Activity-count scale is measured; tier names do not establish intrinsic computational difficulty.",
                  "Structural differences are not necessarily semantic errors; witness checks establish only the differences they exhibit.",
                  "Objective matching is conditional on valid gold-SAT schedules and proven references.",
                  "OS, concurrency, shared backends, service errors and sleep confound elapsed-time comparisons.",
                  "Token totals include recorded scheduling usage only; missing usage is unknown, not zero.",
              ]}
    shared_inputs = shared_settings = None
    all_rows = {}
    for key, phase in PHASES.items():
        base = evidence_root / phase / key
        analysis_path = base / "analysis/analysis-with-execution-provenance.json"
        analysis = json.loads(analysis_path.read_text())
        rows = analysis["rows"]
        if (len(rows) != 2000 or len({unit(r) for r in rows}) != 2000 or
            any(r["study_block"] != "controlled" or r["task_type"] != "generation" or
                r["variant_id"] != "canonical" or r["repeat"] != 0 for r in rows)):
            raise ValueError("Expected 2,000 unique canonical generation observations")
        diagnostics = {tuple(d["unit"]): d for d in analysis["interpretation"]["attempt_diagnostics"]}
        if set(diagnostics) != {unit(r) for r in rows}:
            raise ValueError("Incomplete diagnostic records")
        run = base / "run/controlled"
        case_path = run / "cases.json"
        cases = json.loads(case_path.read_text())["cases"]
        by_case = {c["case_id"]: c for c in cases}
        if len(cases) != 1000 or len(by_case) != 1000 or len({c["group_id"] for c in cases}) != 10:
            raise ValueError("Expected 1,000 cases from ten construction families")
        if Counter(c["expected_label"] for c in cases) != {"SAT": 500, "UNSAT": 500}:
            raise ValueError("Unexpected SAT/UNSAT balance")
        archive = base / "analysis/parallel-evidence.tar.gz"
        archive_hash = digest(archive)
        if archive_hash != json.loads((base / "analysis/archive-sha256.json").read_text())["sha256"]:
            raise ValueError("Evidence archive checksum mismatch")
        inputs = {"cases_sha256": digest(case_path), "requests": {}}
        records = {}
        attempt_hashes = {}
        for path in sorted((run / "attempts").glob("*.json")):
            record = json.loads(path.read_text())
            if record["state"] != "completed":
                raise ValueError("Pending record cannot enter comparison")
            payload = record["payload"]
            identity = payload["identity"]
            u = ("controlled",) + tuple(identity[k] for k in ("case_id", "variant_id", "repeat", "approach"))
            if u in records:
                raise ValueError("Duplicate attempt identity")
            response = payload["pipeline_result"]["model_response"]
            if response["returned_model"] not in (None, MODELS[key]):
                raise ValueError("Returned model mismatch")
            if response["returned_model"] is None and not response["error"]:
                raise ValueError("Successful response lacks model identity")
            if len(response["attempts"]) != 1:
                raise ValueError("Retry or absent provider request")
            if any(p["returned_model"] not in (None, MODELS[key]) for p in response["attempts"]):
                raise ValueError("Attempt-level model mismatch")
            records[u] = payload
            attempt_hashes[path.name] = digest(path)
            if diagnostics[u]["trace"]["attempt_sha256"] != attempt_hashes[path.name]:
                raise ValueError("Diagnostic is not linked to the original attempt bytes")
            inputs["requests"]["|".join(map(str, u))] = {
                "prompt": payload["pipeline_result"]["prompt_sha256"], "public_view": payload["public_view"]}
        if set(records) != set(diagnostics):
            raise ValueError("Analysis and attempt sets differ")
        for row in rows:
            response = records[unit(row)]["pipeline_result"]["model_response"]
            if (row["gold_label"] != by_case[row["case_id"]]["expected_label"] or
                row["returned_model"] != response["returned_model"] or
                row["provider_attempts"] != response["attempts"]):
                raise ValueError("Analysis differs from original case/response")
        settings = normalized_settings(analysis["settings"])
        if shared_settings is None:
            shared_settings, shared_inputs = settings, inputs
        elif settings != shared_settings or inputs != shared_inputs:
            raise ValueError("Non-model settings, cases, prompts or public views differ")
        model = {"model": MODELS[key], "requested_model": analysis["settings"]["model"]["model"],
                 "unique_cases": 1000, "construction_families": 10, "overall_by_method": {},
                 "resources": {}, "execution_segments": [], "by_size": {}, "by_mechanism": {},
                 "failure_catalogue": [], "extraction": {},
                 "controlled_paired": analysis["primary_controlled"]["paired"],
                 "backend_fingerprints": analysis["backend_fingerprints"],
                 "archive": str(archive.relative_to(evidence_root)), "archive_sha256": archive_hash,
                 "attempt_sha256": attempt_hashes}
        for arm in ARMS:
            subset = [r for r in rows if r["approach"] == arm]
            if len(subset) != 1000 or {r["case_id"] for r in subset} != set(by_case):
                raise ValueError("Each method must attempt all 1,000 cases once")
            model["overall_by_method"][arm] = group_summary(subset, diagnostics)
            model["resources"][arm] = resource_summary(subset)
        extracted = [r for r in rows if r["extraction_comparison"] is not None]
        witnessed = [r for r in rows if (r.get("semantic_witness_check") or {}).get("hard_feasibility_difference_demonstrated")]
        model["extraction"] = {
            "compared": len(extracted),
            "structurally_equivalent": sum(r["extraction_comparison"]["structurally_equivalent"] for r in extracted),
            "hard_feasibility_witness_differences": len(witnessed),
            "witness_difference_categories": dict(Counter(r["category"] for r in witnessed)),
            "constraint_omissions": sum(r["extraction_comparison"]["omitted_constraints"] for r in extracted),
            "constraint_inventions": sum(r["extraction_comparison"]["invented_constraints"] for r in extracted)}
        for field, getter in (("by_size", lambda r: str(r["difficulty"]["activity_count"])),
                              ("by_mechanism", lambda r: r["sweep"])):
            for value in sorted({getter(r) for r in rows}):
                model[field][value] = {arm: group_summary([r for r in rows if getter(r) == value and r["approach"] == arm], diagnostics) for arm in ARMS}
        segments = sorted({(r["execution_segment"], r["execution_concurrency"], r["execution_platform"]) for r in rows})
        for segment, concurrency, platform in segments:
            for arm in ARMS:
                subset = [r for r in rows if (r["execution_segment"], r["execution_concurrency"], r["execution_platform"], r["approach"]) == (segment, concurrency, platform, arm)]
                model["execution_segments"].append({"segment": segment, "concurrency": concurrency,
                    "platform": platform, "approach": arm, "attempts": len(subset),
                    "provider_failures": provider_failures(subset), "resources": resource_summary(subset)})
        for row in sorted(rows, key=unit):
            diagnostic = diagnostics[unit(row)]
            if not row["accepted"] or diagnostic["objective_status"] == "proven_suboptimal":
                pipeline = records[unit(row)]["pipeline_result"]
                model["failure_catalogue"].append({**diagnostic, "attempt_id": row["attempt_id"],
                    "gold_label": row["gold_label"], "pipeline_status": row["pipeline_status"],
                    "size": row["difficulty"]["activity_count"], "mechanism": row["sweep"],
                    "objective_values": row["objective_values"], "objective_gaps": row["objective_gaps"],
                    "violations": (row.get("validation") or {}).get("violations", []),
                    "pipeline_diagnostics": pipeline["diagnostics"], "provider_failures": provider_failures([row]),
                    "extraction_comparison": row["extraction_comparison"],
                    "semantic_witness_check": row["semantic_witness_check"],
                    "execution_segment": row["execution_segment"], "model_seconds": row["model_seconds"]})
        by_method_case = {(r["approach"], r["case_id"]): r for r in rows}
        returned_pairs = [case_id for case_id in by_case if all(
            by_method_case[(arm, case_id)]["returned_model"] is not None for arm in ARMS)]
        pair_cells = Counter((by_method_case[("direct", c)]["accepted"],
                              by_method_case[("solver_augmented", c)]["accepted"]) for c in returned_pairs)
        model["secondary_both_methods_returned"] = {
            "cases": len(returned_pairs),
            "accepted": {arm: sum(by_method_case[(arm, c)]["accepted"] for c in returned_pairs) for arm in ARMS},
            "both_accepted": pair_cells[(True, True)], "direct_only": pair_cells[(True, False)],
            "solver_augmented_only": pair_cells[(False, True)], "neither_accepted": pair_cells[(False, False)],
            "note": "Selected secondary intersection; retains format/constraint failures but excludes cases with any provider failure. It does not replace all-attempt results or remove service-selection bias."}
        result["models"][key] = model
        all_rows[key] = {unit(r): r for r in rows}
        for path in (analysis_path, case_path, run / "manifest.json", base / "analysis/archive-sha256.json"):
            result["input_sha256"][str(path.relative_to(evidence_root))] = digest(path)
    matched = []
    for case_id in sorted(by_case):
        pairs = [all_rows[m][("controlled", case_id, "canonical", 0, arm)] for m in MODELS for arm in ARMS]
        if len({(r["execution_platform"], r["execution_concurrency"]) for r in pairs}) == 1:
            matched.append(case_id)
    timing_path = evidence_root / "parallel4-glm-20261017-01/timing-comparability.json"
    timing = json.loads(timing_path.read_text())
    if len(matched) != timing["matched_case_count"]:
        raise ValueError("Timing comparability receipt disagrees with independently grouped rows")
    result["input_sha256"][str(timing_path.relative_to(evidence_root))] = digest(timing_path)
    result["timing_comparability"] = {"matched_case_count": len(matched), "matched_cases": matched,
        "note": "Both methods in both models must share case, OS and concurrency. Phase summaries are descriptive, not causal speed comparisons."}
    result["comparison_checks"] = {"all_4000_attempts_complete_unique_single_call": True,
        "case_bundles_match": True, "all_2000_paired_prompts_and_public_views_match": True,
        "scientific_source_and_non_model_settings_match": True, "all_returned_identities_match": True,
        "archive_and_attempt_linkage_checksums_verified": True, "shared_settings": shared_settings,
        "allowed_execution_differences": ["model identity", "observed backend/capability metadata", "OS/concurrency phases and sleep history"]}
    return result


def build_portable(manifest_path):
    """Read verified public archives into a temporary, disposable analysis tree."""
    manifest = json.loads(manifest_path.read_text())
    entries = manifest["archives"]
    if len(entries) != 2 or {e["id"] for e in entries} != set(MODELS):
        raise ValueError("Expected Qwen and GLM portable evidence archives")
    with tempfile.TemporaryDirectory(prefix="diverse-comparison-") as temporary:
        root = Path(temporary)
        timing_bytes = None
        for entry in entries:
            archive_path = ROOT / entry["path"]
            if digest(archive_path) != entry["sha256"]:
                raise ValueError("Portable archive checksum mismatch")
            base = root / PHASES[entry["id"]] / entry["id"]
            analysis_dir = base / "analysis"
            analysis_dir.mkdir(parents=True)
            with tarfile.open(archive_path) as archive:
                seen = set()
                for member in archive.getmembers():
                    if member.name in seen:
                        raise ValueError("Duplicate archive member")
                    seen.add(member.name)
                    if not member.isfile():
                        continue
                    name = member.name
                    if name == "analysis-with-execution-provenance.json":
                        target = analysis_dir / name
                    elif name.startswith("runs/controlled/controlled/"):
                        relative = Path(name.removeprefix("runs/controlled/controlled/"))
                        if relative.is_absolute() or ".." in relative.parts:
                            raise ValueError("Unsafe archive path")
                        target = base / "run/controlled" / relative
                    elif name == "timing-comparability.json":
                        raw = archive.extractfile(member).read()
                        if timing_bytes is not None and raw != timing_bytes:
                            raise ValueError("Models disagree about timing comparability")
                        timing_bytes = raw
                        continue
                    else:
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
            (analysis_dir / "parallel-evidence.tar.gz").symlink_to(archive_path.resolve())
            (analysis_dir / "archive-sha256.json").write_text(json.dumps({"sha256": entry["sha256"]}))
        if timing_bytes is None:
            raise ValueError("Portable archives lack execution timing evidence")
        timing_path = root / "parallel4-glm-20261017-01/timing-comparability.json"
        timing_path.parent.mkdir(parents=True, exist_ok=True)
        timing_path.write_bytes(timing_bytes)
        result = build(root)
    for entry in entries:
        result["models"][entry["id"]]["archive"] = entry["path"]
    result["portable_source"] = {"manifest": str(manifest_path.relative_to(ROOT)) if manifest_path.is_relative_to(ROOT) else manifest_path.name,
        "manifest_sha256": digest(manifest_path),
        "note": "Explicit portable derivative; original attempts/cases/references retained. See archive provenance for private-path redactions."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--evidence-root", type=Path)
    sources.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "results/summary/diverse-comparison-20261018.json")
    args = parser.parse_args()
    result = build_portable(args.manifest.resolve()) if args.manifest else build(args.evidence_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Validated and summarized 4,000 scheduling attempts; no model calls.")


if __name__ == "__main__":
    main()
