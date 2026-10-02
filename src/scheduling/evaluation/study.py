"""Checked frozen-block analysis and local reproduction archives; no inference."""

from collections import Counter, defaultdict
import csv
import hashlib
import math
import statistics
import io
import json
import os
import re
from pathlib import Path
import tarfile

from scheduling.evaluation.benchmark import render, tiny_fixtures
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.frozen import ANALYSIS_SETTINGS, check_frozen, check_frozen_reference
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.metrics import summarize, analysis_details, export_tables
from scheduling.evaluation.runner import (
    OBSERVE_BACKEND_POLICY, STRICT_QUALIFICATION_POLICY, RunConfig, _contract,
    _stop_reason, baseline_fingerprints, read, replay, write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.pipelines.direct import build_messages
from scheduling.pipelines.solver_augmented import build_extraction_messages
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
    protocol = (
        {k: cfg["freeze"][k] for k in ("development_registry", "analysis_settings")}
        if cfg.get("freeze") else {
            "development_registry": None,
            "analysis_settings": ANALYSIS_SETTINGS,
            "qualification_policy": cfg.get("qualification_policy"),
            "qualification_baseline": cfg.get("qualification_baseline"),
        }
    )
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
        **({"provider_failure_policy": cfg["provider_failure_policy"]}
           if cfg.get("provider_failure_policy") is not None else {}),
        **protocol,
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


def backend_statistics(rows):
    """Describe observed routing and paired outcomes without attributing causality.

    Pipeline outcomes are associated with their final recorded provider attempt;
    coverage counts every provider attempt. Missing metadata and failed requests
    remain explicit categories rather than being assigned to a known backend.
    """
    coverage = Counter(pipeline_attempts=len(rows), provider_attempts=0,
                       reported_fingerprints=0, missing_fingerprints=0,
                       successful_provider_responses=0,
                       successful_responses_with_fingerprint=0)
    outcomes, pairs = defaultdict(list), defaultdict(dict)

    def observation(attempt):
        fingerprint = (attempt.get("execution") or {}).get("system_fingerprint")
        if not attempt:
            return "no_provider_attempt", None
        if attempt.get("http_status") != 200 or attempt.get("error"):
            return "provider_failure", fingerprint
        return ("reported" if fingerprint is not None else "missing"), fingerprint

    for row in rows:
        attempts = row.get("provider_attempts", [])
        for attempt in attempts:
            state, fingerprint = observation(attempt)
            coverage["provider_attempts"] += 1
            coverage["reported_fingerprints" if fingerprint is not None
                     else "missing_fingerprints"] += 1
            if state in ("reported", "missing"):
                coverage["successful_provider_responses"] += 1
                coverage["successful_responses_with_fingerprint"] += state == "reported"
        state, fingerprint = observation(attempts[-1] if attempts else {})
        outcomes[(row["study_block"], row["approach"], state, fingerprint)].append(row)
        key = (row["study_block"], row["case_id"], row["variant_id"], row["repeat"])
        pairs[key][row["approach"]] = (state, fingerprint, row["accepted"])

    by_backend = []
    for (block, approach, state, fingerprint), items in sorted(outcomes.items(), key=str):
        by_backend.append({
            "study_block": block, "approach": approach,
            "backend_observation": state, "system_fingerprint": fingerprint,
            "pipeline_attempts": len(items),
            "accepted": sum(r["accepted"] is True for r in items),
            "failed": sum(r["accepted"] is False for r in items),
            "unscored": sum(r["accepted"] is None for r in items),
            "categories": dict(sorted(Counter(r["category"] for r in items).items())),
        })
    combinations = defaultdict(Counter)
    missing_pairs = 0
    for (block, *_), pair in pairs.items():
        if set(pair) != {"direct", "solver_augmented"}:
            missing_pairs += 1
            continue
        a_state, a_fingerprint, accepted_a = pair["direct"]
        b_state, b_fingerprint, accepted_b = pair["solver_augmented"]
        counts = combinations[(block, a_state, a_fingerprint, b_state, b_fingerprint)]
        counts["pairs"] += 1
        outcome = ("unscored" if accepted_a is None or accepted_b is None else
                   "both_accepted" if accepted_a and accepted_b else
                   "direct_only_accepted" if accepted_a else
                   "solver_only_accepted" if accepted_b else "neither_accepted")
        counts[outcome] += 1
    pair_combinations = []
    for (block, a_state, a_fp, b_state, b_fp), counts in sorted(combinations.items(), key=str):
        pair_combinations.append({
            "study_block": block,
            "direct_backend_observation": a_state, "direct_system_fingerprint": a_fp,
            "solver_backend_observation": b_state, "solver_system_fingerprint": b_fp,
            **{key: counts[key] for key in ("pairs", "both_accepted", "direct_only_accepted",
                                           "solver_only_accepted", "neither_accepted", "unscored")},
        })
    return {
        "scope": "Scheduling attempts only; capability observations remain in the qualification baseline.",
        "interpretation": (
            "Descriptive shared-service routing evidence. Backend assignment is not randomized; "
            "case difficulty, method and request time may differ between groups. Fingerprints are "
            "reported metadata, not proof of pinned weights. No backend-causal or fixed-backend "
            "superiority claim is supported. All failures remain in the study denominators."
        ),
        "coverage": dict(coverage), "outcomes": by_backend,
        "pair_fingerprint_combinations": pair_combinations,
        "missing_method_pairs": missing_pairs,
    }


def analyze_blocks(blocks, *, development=False):
    """Require one canonical block and optional realistic/language blocks.

    Only the core one-repeat design is supported. Optional repeat mapping needs
    its separately agreed protocol and cannot be silently concatenated here.
    Current packaged prompt text must reproduce every saved request hash; use the
    archived runtime/prompts for historical analyses rather than guessing identity.
    Development blocks require explicit opt-in and retain their evidence class.
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
        allowed = ("offline_canned", "live_development") if development else (
            "offline_frozen", "live_frozen"
        )
        if cfg.evidence not in allowed:
            raise ValueError(
                "Study analysis requires matching frozen/development mode; development needs explicit opt-in"
            )
        if (cfg.evidence == "live_development" and cfg.qualification_policy not in
                (STRICT_QUALIFICATION_POLICY, OBSERVE_BACKEND_POLICY)):
            raise ValueError("Development study requires an explicit model/backend policy")
        observe_backend = development and cfg.qualification_policy == OBSERVE_BACKEND_POLICY
        observations.update(baseline_fingerprints(cfg))
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
            if cfg.evidence in ("live_frozen", "live_development"):
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
                # Match the runner: provider failures remain failed observations,
                # while returned answers must satisfy the frozen model contract.
                reason = _stop_reason(response, cfg.model.model, observations,
                                      allow_backend_variation=observe_backend)
                if reason == "returned_model_mismatch":
                    raise ValueError("Returned model differs from required study model")
                if reason == "backend_fingerprint_changed":
                    raise ValueError("Backend fingerprint changed across blocks")
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
    shared_service = common.get("qualification_policy") == OBSERVE_BACKEND_POLICY
    if len(observations) > 1 and not shared_service:
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
        "backend_note": (
            "Shared-service development evidence: exact model identity was required, backend "
            "variation was explicitly permitted and recorded. This is not a fixed-backend study."
            if shared_service else
            "Reported metadata only; unavailable fingerprints do not establish pinned weights."
        ),
        **({"evidence_scope": "shared_service_development",
            "backend_diagnostics": backend_statistics(all_rows)} if shared_service else {}),
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


def _archive_read(root, relative):
    """Read only regular files below the declared root; reject linked parents too."""
    root, relative = Path(root), Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Archive path must stay inside its declared root")
    if any(
        (root / Path(*relative.parts[:i])).is_symlink()
        for i in range(1, len(relative.parts) + 1)
    ):
        raise ValueError("Archive inputs cannot follow file or directory links")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Archive input must be a regular file inside its root")
    return path.read_bytes()


def _archive_sources(project_root, settings):
    """Snapshot and check the bytes to archive before creating any output files."""
    project_root = Path(project_root)
    package = Path(__file__).resolve().parents[1]
    entries, source_map = {}, {}
    for path in sorted(package.rglob("*")):
        if path.is_file() and path.suffix in (".py", ".crt", ".js", ".css", ".html"):
            relative = path.relative_to(package)
            data = _archive_read(package, relative)
            entries["source/src/scheduling/" + str(relative)] = data
            if path.suffix in (".py", ".crt"):
                # Match read_text's universal-newline semantics in run contracts.
                source_map[str(relative)] = digest(
                    io.TextIOWrapper(io.BytesIO(data), encoding="utf-8").read()
                )
    if source_map != settings["source"]:
        raise ValueError("Archive needs the exact recorded package source")
    # Both builders resolve the active installed/editable templates. These are
    # also the builders whose complete request hashes analyze_blocks verifies.
    prompts = {}
    for case in (tiny_fixtures()[0], tiny_fixtures()[-1]):
        view = render(case)
        prompts[f"prompts/direct/{view.task_type}.txt"] = build_messages(
            view.text,
            task_type=view.task_type,
            required_activity_ids=view.activity_ids,
            original_schedule=(
                view.original_schedule.to_list() if view.original_schedule else None
            ),
        )[0].content
        prompts["prompts/extraction/specification.txt"] = build_extraction_messages(
            view
        )[0].content
    for name, expected in prompts.items():
        data = _archive_read(project_root, name)
        text = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8").read()
        if text != expected:
            raise ValueError(f"Archive prompt differs from verified runtime: {name}")
        entries["source/" + name] = data
    for name in ("pyproject.toml", "requirements.lock", "evaluation/analyze_study.py"):
        entries["source/" + name] = _archive_read(project_root, name)
    # The pinned project lock must install the versions recorded by the run.
    # Unknown historical build settings are not reconstructed or silently updated.
    pins = defaultdict(set)
    for name, version in re.findall(
        r"^([A-Za-z0-9_.-]+)==([^\s\\;]+)",
        entries["source/requirements.lock"].decode("utf-8"),
        re.MULTILINE,
    ):
        pins[name.lower().replace("_", "-").replace(".", "-")].add(version)
    for name, version in settings["runtime"].items():
        if name not in ("python", "platform") and pins.get(name) != {version}:
            raise ValueError(f"Archive lock differs from recorded runtime: {name}")
    return entries


def export_study(blocks, directory, *, project_root, figures=False, development=False):
    """Export immutable analysis and an explicit allowlist archive, never .env."""
    result = analyze_blocks(blocks, development=development)
    entries = _archive_sources(project_root, result["settings"])
    run_roots = {
        role: f"runs/{role}/{Path(path).resolve().name}" for role, path in blocks.items()
    }
    for role, path in blocks.items():
        for name, expected in result["block_checksums"][role].items():
            data = _archive_read(path, name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("Run changed during export")
            entries[f"{run_roots[role]}/{name}"] = data
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
    if "backend_diagnostics" in result:
        for name in ("outcomes", "pair_fingerprint_combinations"):
            values = result["backend_diagnostics"][name]
            if not values:
                continue
            with (directory / "tables" / f"backend_{name}.csv").open(
                "x", newline="", encoding="utf-8"
            ) as out:
                writer = csv.DictWriter(out, list(values[0]))
                writer.writeheader()
                for value in values:
                    writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, dict)
                                     else v for k, v in value.items()})
    if figures:
        from scheduling.evaluation.figures import export_figures

        export_figures(
            result["rows"], directory / "tables", evidence=result["evidence"]
        )
    entries["analysis.json"] = (directory / "analysis.json").read_bytes()
    for p in sorted((directory / "tables").iterdir()):
        entries["tables/" + p.name] = p.read_bytes()
    entries["blocks.json"] = json.dumps(
        run_roots, sort_keys=True
    ).encode()
    mode_flag = " --development" if development else ""
    entries["REPRODUCE.txt"] = (
        "Offline replay of saved evidence; no key or model calls. From archive root, create a Python 3.12 venv, "
        "install source/requirements.lock with --require-hashes, then install ./source with --no-deps --no-build-isolation. "
        f"Run: .venv/bin/python source/evaluation/analyze_study.py blocks.json NEW-analysis --no-archive{mode_flag}\n"
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
