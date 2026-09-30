"""Checked frozen-block analysis and local reproduction archives; no inference."""

from collections import defaultdict
import csv
import hashlib
import math
import statistics
import io
import json
import os
from pathlib import Path
import tarfile

from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.frozen import check_frozen, check_frozen_reference
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.metrics import summarize, analysis_details, export_tables
from scheduling.evaluation.runner import RunConfig, _contract, read, replay, write_new
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.solver import SolverLimits

ROLES = {"controlled", "realistic", "language"}


def _config(data):
    return RunConfig(
        **{
            **data,
            "model": ModelConfig(**data["model"]),
            "solver": SolverLimits(**data["solver"]),
            "reference_solver": SolverLimits(**data["reference_solver"]),
            "variants": tuple(data["variants"]),
        }
    )


def _settings(contract):
    cfg = contract["config"]
    # Block membership, cap, protocol ID and variants intentionally differ.
    return {
        "source": contract["source_sha256"],
        "runtime": contract["runtime"],
        "provider_execution": contract.get("provider_execution"),
        **{
            k: cfg[k]
            for k in (
                "model",
                "solver",
                "reference_solver",
                "rendering_seed",
                "evidence",
            )
        },
        **{k: cfg["freeze"][k] for k in ("development_registry", "analysis_settings")},
    }


def resource_statistics(rows):
    """Observed per-pipeline and per-provider distributions; missing is not zero."""
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["study_block"], row["approach"])].append(row)
    output = []
    for (block, approach), items in sorted(buckets.items()):
        measurements = {}
        for field in ("total_seconds", "extraction_seconds", "solver_seconds"):
            measurements[field] = [dict(r["timings"]).get(field) for r in items]
        measurements["model_seconds"] = [r.get("model_seconds") for r in items]
        measurements["provider_attempt_seconds"] = [
            a["elapsed_seconds"] for r in items for a in r.get("provider_attempts", [])
        ]
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            measurements[field] = [u.get(field) for r in items for u in r["usage"]]
        distributions = {}
        for field, values in measurements.items():
            known = sorted(v for v in values if v is not None)
            distributions[field] = {
                "observations": len(values),
                "reported": len(known),
                "missing": len(values) - len(known),
                "mean": statistics.mean(known) if known else None,
                "median": statistics.median(known) if known else None,
                "p95_nearest_rank": (
                    known[math.ceil(0.95 * len(known)) - 1] if known else None
                ),
                "max": max(known) if known else None,
            }
        output.append(
            {
                "study_block": block,
                "approach": approach,
                "pipeline_attempts": len(items),
                "without_provider_records": sum(not r["usage"] for r in items),
                "distributions": distributions,
            }
        )
    return output


def analyze_blocks(blocks):
    """Require one canonical block and optional realistic/language blocks.

    Only the core one-repeat design is supported. Optional repeat mapping needs
    its separately agreed protocol and cannot be silently concatenated here.
    Current packaged prompt text must reproduce every saved request hash; use the
    archived runtime/prompts for historical analyses rather than guessing identity.
    """
    if (
        not isinstance(blocks, dict)
        or "controlled" not in blocks
        or set(blocks) - ROLES
    ):
        raise ValueError(
            "Declare controlled and optional realistic/language block paths"
        )
    paths = {role: Path(path).resolve() for role, path in blocks.items()}
    if len(set(paths.values())) != len(paths):
        raise ValueError("Duplicate run directory")
    all_rows, cases_by_role, common, observations, snapshots, used = (
        [],
        {},
        None,
        set(),
        {},
        set(),
    )
    for role, path in sorted(paths.items()):
        contract = read(path / "manifest.json")["contract"]
        cfg = _config(contract["config"])
        if cfg.evidence not in ("offline_frozen", "live_frozen"):
            raise ValueError(
                "Study analysis requires frozen blocks, not development runs"
            )
        expected_variants = (
            {"paraphrase", "reordered"} if role == "language" else {"canonical"}
        )
        if set(cfg.variants) != expected_variants or cfg.repeats != 1:
            raise ValueError(
                "Unexpected role variants/repeats; optional repeats need explicit mapping"
            )
        cases = load_cases(path / "cases.json")
        if any(
            c.kind != ("realistic" if role == "realistic" else "controlled")
            for c in cases
        ):
            raise ValueError("Block role disagrees with case kind")
        check_frozen(cases, cfg, contract)
        # Whole request hashes cannot match across different cases/renderings.
        # Reconstruct each request with the same installed prompts and compare it.
        if (
            _contract(cases, cfg)["request_prompt_sha256"]
            != contract["request_prompt_sha256"]
        ):
            raise ValueError(
                "Saved prompt hashes differ from the supplied runtime/prompts"
            )
        settings = _settings(contract)
        if common is None:
            common = settings
        elif settings != common:
            raise ValueError(
                "Incompatible source, runtime, model, provider, solver or analysis settings"
            )
        cases_by_role[role] = {c.case_id: c for c in cases}
        for c in cases:
            record = read(path / "references" / (digest(c.case_id) + ".json"))
            if digest(record["reference"]) != record["sha256"]:
                raise ValueError("Reference checksum mismatch")
            check_frozen_reference(c, record["reference"])
        rows, progress = replay(path)
        if (
            progress["pending_attempt_ids"]
            or progress["not_started"]
            or progress["completed"] != progress["planned"]
        ):
            raise ValueError(
                "Incomplete/uncertain block; retain its standalone replay, not a completed study claim"
            )
        for row in rows:
            identity = (
                row["case_id"],
                row["variant_id"],
                row["repeat"],
                row["approach"],
            )
            if identity in used:
                raise ValueError("Duplicate study observation")
            used.add(identity)
            row.update(study_block=role, raw_run=path.name, raw_repeat=row["repeat"])
        row_lookup = {
            (r["case_id"], r["variant_id"], r["repeat"], r["approach"]): r for r in rows
        }
        all_rows.extend(rows)
        for file in sorted((path / "attempts").glob("*.json")):
            payload = read(file)["payload"]
            result = payload["pipeline_result"]
            response = result.get("model_response") or {}
            identity = payload["identity"]
            row = row_lookup[
                tuple(
                    identity[k] for k in ("case_id", "variant_id", "repeat", "approach")
                )
            ]
            row["model_seconds"] = response.get("elapsed_seconds")
            row["provider_attempts"] = response.get("attempts", [])
            returned = response.get("returned_model")
            if (
                cfg.evidence == "live_frozen"
                and returned is not None
                and returned != cfg.model.model
            ):
                raise ValueError("Returned model differs from frozen model")
            if cfg.evidence == "live_frozen":
                if not response.get("attempts"):
                    raise ValueError("Missing live provider attempt metadata")
                for attempt in response.get("attempts", []):
                    execution = attempt.get("execution")
                    if not execution or execution.get("contract") != contract.get(
                        "provider_execution"
                    ):
                        raise ValueError(
                            "Missing or inconsistent live execution metadata"
                        )
                    observations.add(execution.get("system_fingerprint"))
        run_files = [
            path / "manifest.json",
            path / "cases.json",
            *sorted((path / "references").glob("*.json")),
            *sorted((path / "attempts").glob("*.json")),
        ]
        snapshots[role] = {
            str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in run_files
        }
    if len(observations) > 1:
        raise ValueError("Backend fingerprint changed across blocks")
    controlled = cases_by_role["controlled"]
    realistic = cases_by_role.get("realistic", {})
    if set(controlled) & set(realistic):
        raise ValueError("Canonical controlled and realistic cases overlap")
    combined = tuple(controlled.values()) + tuple(realistic.values())
    families = structural_audit(combined)["family_for_group"]
    if any(group != family for group, family in families.items()):
        raise ValueError("Canonical blocks split a related source family")
    if {c.group_id for c in controlled.values()} & {
        c.group_id for c in realistic.values()
    }:
        raise ValueError("Controlled and realistic source families overlap")
    for cid, c in cases_by_role.get("language", {}).items():
        if cid not in controlled or digest(c) != digest(controlled[cid]):
            raise ValueError(
                "Language block has missing or changed canonical case/gold partner"
            )
    canonical = [r for r in all_rows if r["study_block"] == "controlled"]
    realistic_rows = [r for r in all_rows if r["study_block"] == "realistic"]
    language_ids = set(cases_by_role.get("language", {}))
    language_rows = [
        r
        for r in all_rows
        if r["study_block"] == "language"
        or (r["study_block"] == "controlled" and r["case_id"] in language_ids)
    ]
    return {
        "format_version": "1.0",
        "evidence": common["evidence"],
        "settings": common,
        "block_checksums": snapshots,
        "backend_fingerprints": sorted(observations, key=str),
        "backend_note": "Reported metadata only; unavailable fingerprints do not establish pinned weights.",
        "primary_controlled": summarize(canonical),
        "realistic": summarize(realistic_rows),
        "language": summarize(language_rows),
        "diagnostics": analysis_details(all_rows),
        "resources": resource_statistics(all_rows),
        "rows": all_rows,
        "counts": {
            "primary_attempts": len(canonical),
            "realistic_attempts": len(realistic_rows),
            "additional_language_attempts": sum(
                r["study_block"] == "language" for r in all_rows
            ),
            "unique_attempts": len(all_rows),
        },
    }


def export_study(blocks, directory, *, project_root, figures=False):
    """Export immutable analysis and an explicit allowlist archive, never .env."""
    result = analyze_blocks(blocks)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    write_new(directory / "analysis.json", result)
    export_tables(result["rows"], directory / "tables")
    fields = [
        "study_block",
        "raw_run",
        "case_id",
        "variant_id",
        "raw_repeat",
        "approach",
        "request_count",
        "model_seconds",
        "provider_attempts",
        "usage",
        "timings",
    ]
    with (directory / "tables/resources.csv").open(
        "x", newline="", encoding="utf-8"
    ) as out:
        writer = csv.DictWriter(out, fields)
        writer.writeheader()
        for row in result["rows"]:
            writer.writerow(
                {
                    k: (
                        json.dumps(row[k])
                        if k in ("usage", "timings", "provider_attempts")
                        else row[k]
                    )
                    for k in fields
                }
            )
    if figures:
        from scheduling.evaluation.figures import export_figures

        export_figures(
            result["rows"], directory / "tables", evidence=result["evidence"]
        )
    project_root = Path(project_root)
    package = Path(__file__).resolve().parents[1]
    source_map = {
        str(p.relative_to(package)): digest(p.read_text())
        for p in package.rglob("*")
        if p.is_file() and p.suffix in (".py", ".crt")
    }
    if source_map != result["settings"]["source"]:
        raise ValueError("Archive needs the exact recorded package source")
    entries = {}
    for role, path in blocks.items():
        path = Path(path)
        for name, expected in result["block_checksums"][role].items():
            p = path / name
            if p.is_symlink() or not p.resolve().is_relative_to(path.resolve()):
                raise ValueError("Run archive cannot follow links outside its run")
            data = p.read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("Run changed during export")
            entries[f"runs/{role}/{name}"] = data
    for parent, prefix in (
        (package, "source/src/scheduling"),
        (project_root / "prompts", "source/prompts"),
    ):
        for p in sorted(parent.rglob("*")):
            if p.is_file() and p.suffix in (
                ".py",
                ".crt",
                ".txt",
                ".js",
                ".css",
                ".html",
            ):
                entries[prefix + "/" + str(p.relative_to(parent))] = p.read_bytes()
    for name in ("pyproject.toml", "requirements.lock", "evaluation/analyze_study.py"):
        entries["source/" + name] = (project_root / name).read_bytes()
    entries["analysis.json"] = (directory / "analysis.json").read_bytes()
    for p in sorted((directory / "tables").iterdir()):
        entries["tables/" + p.name] = p.read_bytes()
    entries["blocks.json"] = json.dumps(
        {r: "runs/" + r for r in blocks}, sort_keys=True
    ).encode()
    entries["REPRODUCE.txt"] = (
        "Offline replay of saved evidence; no key or model calls. From archive root, create a Python 3.12 venv, "
        "install source/requirements.lock with --require-hashes, then install ./source with --no-deps --no-build-isolation. "
        "Run: .venv/bin/python source/evaluation/analyze_study.py blocks.json NEW-analysis --no-archive\n"
        "Compare counts and scientific summaries with analysis.json. Evidence class is recorded there; canned rehearsal is not model-performance evidence.\n"
    ).encode()
    checksums = {
        name: hashlib.sha256(data).hexdigest() for name, data in sorted(entries.items())
    }
    entries["CHECKSUMS.json"] = json.dumps(checksums, sort_keys=True).encode()
    archive = directory / "reproduction.tar.gz"
    with os.fdopen(
        os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
    ) as out:
        with tarfile.open(fileobj=out, mode="w:gz") as tar:
            for name, data in sorted(entries.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o600
                tar.addfile(info, io.BytesIO(data))
    with tarfile.open(archive) as tar:
        for name, h in checksums.items():
            if hashlib.sha256(tar.extractfile(name).read()).hexdigest() != h:
                raise ValueError("Archive verification failed")
    write_new(
        directory / "archive-sha256.json",
        {
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "files": len(checksums),
        },
    )
    return result
