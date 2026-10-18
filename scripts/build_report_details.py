#!/usr/bin/env python3
"""Derive report resource distributions and a worked case from preserved evidence.

Standard library only. Verifies the manifest-bound archives, links every analysis
row to its saved attempt, and never invokes a model, solver, or network service.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median
import tarfile

from verify_evidence import ROOT, verify_archive

CASE_ID = "dg-3fd5174321284caacab1f4a9"
ARMS = ("direct", "solver_augmented")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def distribution(values: list[float | int | None]) -> dict:
    observed = sorted(value for value in values if value is not None)
    if any(not math.isfinite(value) or value < 0 for value in observed):
        raise ValueError("Resource observations must be finite and nonnegative")
    return {
        "mean": mean(observed) if observed else None,
        "median": median(observed) if observed else None,
        "p95": observed[math.ceil(0.95 * len(observed)) - 1] if observed else None,
        "reported": len(observed), "attempts": len(values),
        "missing": len(values) - len(observed),
    }


def resources(rows: list[dict]) -> dict:
    token_values = [sum(usage["total_tokens"] for usage in row["usage"])
                    if row["usage"] and all(usage["total_tokens"] is not None
                                            for usage in row["usage"]) else None
                    for row in rows]
    return {
        "total_tokens": {**distribution(token_values),
                         "reported_sum": sum(value for value in token_values if value is not None)},
        "model_seconds": distribution([row["model_seconds"] for row in rows]),
        "pipeline_seconds": distribution([dict(row["timings"]).get("total_seconds") for row in rows]),
        "solver_seconds": distribution([dict(row["timings"]).get("solver_seconds") for row in rows]),
    }


def clock(problem: dict, slot: int) -> str:
    start = datetime.fromisoformat(problem["horizon_start"])
    return (start + timedelta(minutes=slot * problem["slot_minutes"])).strftime("%H:%M")


def clock_schedule(problem: dict, schedule: list[dict] | None) -> list[dict] | None:
    if schedule is None:
        return None
    durations = {activity["id"]: activity["duration_slots"] for activity in problem["activities"]}
    return [{**item, "start_clock": clock(problem, item["start_slot"]),
             "end_clock": clock(problem, item["start_slot"] + durations[item["activity_id"]])}
            for item in sorted(schedule, key=lambda item: (item["start_slot"], item["activity_id"]))]


def build(manifest_path: Path) -> dict:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    output = {
        "format_version": "1.0", "dataset": "diverse-generation-v1", "new_model_calls": 0,
        "builder_sha256": digest(Path(__file__).read_bytes()),
        "manifest_sha256": digest(manifest_bytes),
        "definitions": {
            "p95": "Nearest-rank empirical percentile: sorted nonmissing observations at one-based rank ceil(0.95*n). No interpolation.",
            "median": "Middle observed value, or arithmetic mean of the two middle values for even n.",
            "total_tokens": "Provider-reported prompt plus completion tokens per scheduling attempt; missing usage remains unknown. Capability calls excluded; observed failures with usage would be included.",
            "model_seconds": "Saved model-response elapsed time on the local monotonic clock, including failed requests. Not server-only inference time.",
            "pipeline_seconds": "Saved local total_seconds for each method execution, including provider, parsing/extraction and applicable solver work. Excludes evaluator/reference solving and campaign downtime; not campaign wall time.",
            "solver_seconds": "Local solve invocation elapsed time for B, conditional on reaching the solver. Includes local preprocessing; not CP-SAT search time alone. A has no solver observations.",
            "timing_comparability": "Aggregate times mix recorded OS/concurrency phases; zero cases have all four model/method observations under matching OS/concurrency. Descriptive operational observations, not a controlled speed ranking.",
            "worked_case": "Selected explanatory case, not a representative sample. Saved provider content is final output, not hidden reasoning. Clock labels are deterministic conversions of original slots.",
        },
        "models": {}, "worked_case": {"case_id": CASE_ID, "outputs": {}},
    }
    shared_case = shared_public = None
    for entry in manifest["archives"]:
        archive_path = ROOT / entry["path"]
        verified = verify_archive(archive_path, entry)
        with tarfile.open(archive_path, "r:gz") as archive:
            def read(name: str) -> tuple[dict, str]:
                stream = archive.extractfile(name)
                if stream is None:
                    raise ValueError(f"Missing evidence member: {name}")
                data = stream.read()
                return json.loads(data), digest(data)

            analysis, analysis_sha = read("analysis-with-execution-provenance.json")
            cases, cases_sha = read("runs/controlled/controlled/cases.json")
            case = next(case for case in cases["cases"] if case["case_id"] == CASE_ID)
            if shared_case is not None and shared_case != case:
                raise ValueError("Worked gold cases differ between models")
            shared_case = case
            rows = analysis["rows"]
            if len(rows) != 2000 or len({row["attempt_id"] for row in rows}) != 2000:
                raise ValueError("Expected 2,000 unique completed attempts per model")
            diagnostics = {tuple(item["unit"]): item for item in analysis["interpretation"]["attempt_diagnostics"]}
            outputs = {}
            for row in rows:
                name = f'runs/controlled/controlled/attempts/{row["attempt_id"]}.json'
                record, record_sha = read(name)
                unit = tuple(row[key] for key in ("study_block", "case_id", "variant_id", "repeat", "approach"))
                if record["state"] != "completed" or diagnostics[unit]["trace"]["attempt_sha256"] != record_sha:
                    raise ValueError("Attempt completion or diagnostic linkage mismatch")
                payload = record["payload"]
                pipeline = payload["pipeline_result"]
                response = pipeline["model_response"]
                if len(response["attempts"]) != 1:
                    raise ValueError("Expected one provider request per scheduling attempt")
                if (row["usage"] != pipeline["usage"] or row["timings"] != pipeline["timings"]
                        or row["model_seconds"] != response["elapsed_seconds"]
                        or row["provider_attempts"] != response["attempts"]):
                    raise ValueError("Saved resource row differs from immutable attempt")
                if row["case_id"] == CASE_ID:
                    public = payload["public_view"]
                    if shared_public is not None and shared_public != public:
                        raise ValueError("Worked public inputs differ")
                    shared_public = public
                    outputs[row["approach"]] = {
                        "archive_member": name, "attempt_sha256": record_sha,
                        "accepted": row["accepted"], "category": row["category"],
                        "validation": row["validation"], "objective_values": row["objective_values"],
                        "extraction_comparison": row["extraction_comparison"],
                        "schedule_with_clock": clock_schedule(case["problem"], pipeline["schedule"]),
                        "pipeline_result": pipeline,
                    }
            model = {"archive": entry["path"], "verification": verified,
                     "analysis_sha256": analysis_sha, "cases_sha256": cases_sha,
                     "resources": {}, "execution_segments": []}
            for arm in ARMS:
                subset = [row for row in rows if row["approach"] == arm]
                if len(subset) != 1000 or len({row["case_id"] for row in subset}) != 1000:
                    raise ValueError("Each method must contain 1,000 unique cases")
                model["resources"][arm] = resources(subset)
            segments = sorted({(row["execution_segment"], row["execution_concurrency"], row["execution_platform"])
                               for row in rows})
            for segment, concurrency, platform in segments:
                for arm in ARMS:
                    subset = [row for row in rows if (row["execution_segment"], row["execution_concurrency"],
                              row["execution_platform"], row["approach"]) == (segment, concurrency, platform, arm)]
                    model["execution_segments"].append({
                        "segment": segment, "concurrency": concurrency, "platform": platform, "approach": arm,
                        "categories": dict(sorted(Counter(row["category"] for row in subset).items())),
                        "resources": resources(subset)})
            output["models"][entry["id"]] = model
            output["worked_case"]["outputs"][entry["id"]] = outputs
    if set(output["models"]) != {"qwen36", "glm53flash"}:
        raise ValueError("Expected the two diverse-study model archives")
    output["worked_case"].update({"gold_case": shared_case, "public_view": shared_public,
                                 "gold_witness_with_clock": clock_schedule(shared_case["problem"], shared_case["witness"])})
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/diverse-evidence-manifest.json")
    parser.add_argument("--output", type=Path, required=True,
                        help="New output file; existing files are never overwritten")
    args = parser.parse_args()
    result = build(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "models": len(result["models"]), "new_model_calls": 0}))


if __name__ == "__main__":
    main()
