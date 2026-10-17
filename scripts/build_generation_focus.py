#!/usr/bin/env python3
"""Derive generation-first views without replacing executed study results."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

from build_difficulty_comparison import ARMS, TIERS, aggregate, resources, unit
from verify_evidence import ROOT, verify_archive


def summarize(rows, diagnostics):
    return {
        "cases": len({r["case_id"] for r in rows}),
        "normalized_groups": len({r["group_id"] for r in rows}),
        "approaches": {
            arm: {**aggregate([r for r in rows if r["approach"] == arm], diagnostics),
                  "resources": resources([r for r in rows if r["approach"] == arm])}
            for arm in ARMS
        },
        "observation_ids": [list(unit(r)) for r in sorted(rows, key=unit)],
    }


def build(manifest):
    result = {
        "format_version": "1.0", "new_model_calls": 0,
        "scope": "Post-run descriptive presentation of unchanged development observations",
        "selection": {
            "generation_core": "All controlled generation cases, all five tiers",
            "generation_small": "Controlled generation at easy/moderate tiers (4/8 activities)",
            "generation_stress": "Controlled generation at hard/very_hard/extreme tiers (12/20/32 activities)",
            "repair_extension": "All controlled repair cases",
            "fictional_generation": "All fictional generation cases",
            "fictional_repair": "All fictional repair cases",
            "wording_generation": "All additional generation wordings",
            "wording_repair": "All additional repair wordings",
        },
        "notes": [
            "The reporting hierarchy follows TA feedback after execution; it is not a preregistration or new experiment.",
            "All 200 original observations per model remain in the full comparison; scoped views overlap and must not be added together.",
            "Small-case selection uses construction size only, not outcomes; all larger cases and failures remain reported.",
            "Repair is a completed extension; no scoring, solver objective, public input or budget changed.",
        ],
        "models": {},
    }
    for entry in manifest["archives"]:
        verify_archive(ROOT / entry["path"], entry)
        with tarfile.open(ROOT / entry["path"]) as archive:
            raw = archive.extractfile("analysis.json").read()
        analysis = json.loads(raw)
        rows = analysis["rows"]
        if len(rows) != 200 or len({unit(r) for r in rows}) != 200:
            raise ValueError("Expected the complete 200-observation study")
        diagnostics = {tuple(d["unit"]): d for d in analysis["interpretation"]["attempt_diagnostics"]}
        controlled = [r for r in rows if r["study_block"] == "controlled"]
        generation = [r for r in controlled if r["task_type"] == "generation"]
        scopes = {
            "generation_core": generation,
            "generation_small": [r for r in generation if r["level"] in ("easy", "moderate")],
            "generation_stress": [r for r in generation if r["level"] not in ("easy", "moderate")],
            "repair_extension": [r for r in controlled if r["task_type"] == "repair"],
        }
        for prefix, block in (("fictional", "realistic"), ("wording", "language")):
            for task in ("generation", "repair"):
                scopes[f"{prefix}_{task}"] = [r for r in rows if r["study_block"] == block and r["task_type"] == task]
        expected = {"generation_core": 60, "generation_small": 24,
                    "generation_stress": 36, "repair_extension": 60,
                    "fictional_generation": 20, "fictional_repair": 20,
                    "wording_generation": 20, "wording_repair": 20}
        if {k: len(v) for k, v in scopes.items()} != expected:
            raise ValueError("Unexpected scope sizes")
        result["models"][entry["id"]] = {
            "model": entry["required_returned_model"], "archive": entry["path"],
            "archive_sha256": entry["sha256"], "analysis_sha256": hashlib.sha256(raw).hexdigest(),
            "scopes": {k: summarize(v, diagnostics) for k, v in scopes.items()},
            "generation_tiers": {
                tier: summarize([r for r in generation if r["level"] == tier], diagnostics)
                for tier in TIERS
            },
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/summary/generation-focus-20261015.json")
    args = parser.parse_args()
    result = build(json.loads((ROOT / "results/difficulty-evidence-manifest.json").read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Verified and derived generation/extension views; 400 original observations retained; zero model calls.")


if __name__ == "__main__":
    main()
