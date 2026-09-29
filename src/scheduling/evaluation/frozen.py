"""Frozen-mode preflight assertions; recorded approvals are not human certification.

Offline qualification uses synthetic test fixtures and never the live provider.
The production protocol must be supplied by the team, not inferred by this code.
"""

from collections.abc import Mapping
import re
from scheduling.evaluation.manifests import structural_audit, structural_fingerprint
from scheduling.evaluation.scoring import digest, check_reference
from scheduling.schema import to_data

FROZEN_MODES = ("offline_frozen", "live_frozen")
ANALYSIS_SETTINGS = {
    "primary_variant": "canonical",
    "primary_repeat": 0,
    "bootstrap_seed": 3263,
    "bootstrap_resamples": 10000,
    "minimum_groups_for_interval": 10,
    "separate_kind_task_and_gold_strata": True,
}


def settings_digest(config):
    data = to_data(config)
    data.pop("freeze", None)
    return digest(data)


def check_frozen(cases, config, contract):
    if config.evidence not in FROZEN_MODES:
        if config.freeze is not None:
            raise ValueError("Development mode cannot carry frozen protocol")
        if not cases or any(c.split != "development" for c in cases):
            raise ValueError(
                "Only explicit nonempty development cases may run before freeze"
            )
        return
    if not cases or any(c.split != "test" for c in cases):
        raise ValueError("Frozen mode requires explicit nonempty test membership")
    freeze = config.freeze
    required = {
        "format_version",
        "protocol_id",
        "model_id",
        "eligibility_reference",
        "approval_reference",
        "authorization_reference",
        "benchmark_manifest",
        "settings_sha256",
        "case_bundle_sha256",
        "source_sha256",
        "request_prompt_sha256",
        "development_hard_fingerprints",
        "development_registry_reference",
        "analysis_settings",
    }
    if (
        not isinstance(freeze, Mapping)
        or set(freeze) != required
        or freeze["format_version"] != "1.0"
    ):
        raise ValueError("Missing or unsupported frozen protocol fields")
    for name in (
        "protocol_id",
        "model_id",
        "eligibility_reference",
        "approval_reference",
        "authorization_reference",
        "development_registry_reference",
    ):
        if not isinstance(freeze[name], str) or not freeze[name].strip():
            raise ValueError("Frozen protocol requires explicit decision references")
    if freeze["analysis_settings"] != ANALYSIS_SETTINGS:
        raise ValueError("Frozen analysis settings differ from implemented estimands")
    if freeze["model_id"] != config.model.model or freeze[
        "settings_sha256"
    ] != settings_digest(config):
        raise ValueError("Frozen model/settings mismatch")
    for name in ("case_bundle_sha256", "source_sha256", "request_prompt_sha256"):
        if freeze[name] != contract[name]:
            raise ValueError("Frozen input/source/prompt mismatch")
    planned = len(contract["request_prompt_sha256"])
    if (
        planned > config.max_requests
        or planned * config.model.max_tokens > config.max_requested_output_tokens
    ):
        raise ValueError("Frozen planned requests exceed authorized cap")
    registry = freeze["development_hard_fingerprints"]
    if not isinstance(registry, list) or any(
        not isinstance(k, str) or re.fullmatch(r"[0-9a-f]{64}", k) is None
        for k in registry
    ):
        raise ValueError("Invalid frozen development fingerprint registry")
    for case in cases:
        for spec in (case.problem, case.original_problem):
            if spec is not None and structural_fingerprint(spec) in registry:
                raise ValueError(
                    "Previously developed hard structure cannot enter held-out evaluation"
                )
    manifest = freeze["benchmark_manifest"]
    if (
        not isinstance(manifest, Mapping)
        or manifest.get("format_version") != "2.0"
        or manifest.get("status") != "reviewed_frozen"
        or manifest.get("human_fixture_review") != "approved"
        or manifest.get("human_language_review") != "approved"
    ):
        raise ValueError("Frozen mode needs a reviewed version-2 benchmark manifest")
    reviews = manifest.get("review_references")
    if not isinstance(reviews, dict) or any(
        not isinstance(reviews.get(k), str) or not reviews[k].strip()
        for k in ("gold", "language")
    ):
        raise ValueError("Missing benchmark review references")
    rows = manifest.get("cases")
    if not isinstance(rows, list) or any(
        not isinstance(row, dict)
        or not isinstance(row.get("case_id"), str)
        or not row["case_id"]
        for row in rows
    ):
        raise ValueError("Invalid frozen manifest cases")
    lookup = {row.get("case_id"): row for row in rows}
    if len(lookup) != len(rows) or set(lookup) != {c.case_id for c in cases}:
        raise ValueError("Frozen manifest membership mismatch")
    audit = structural_audit(cases)
    if audit["cross_split_families"]:
        raise ValueError("Frozen source families cross splits")
    from scheduling.evaluation.benchmark import render

    for case in cases:
        row = lookup[case.case_id]
        if (
            row.get("sha256") != digest(case)
            or row.get("split") != case.split
            or row.get("group_id") != case.group_id
            or row.get("source_family_id") != audit["family_for_group"][case.group_id]
            or case.group_id != audit["family_for_group"][case.group_id]
        ):
            raise ValueError(
                "Frozen case hash/split/family mismatch; group related cases together"
            )
        if row.get("creation_method") not in (
            "fixed_fixture",
            "procedural",
            "human_written",
            "external_adaptation",
        ):
            raise ValueError("Frozen case provenance missing")
        if (
            row.get("fixture_review") != "approved"
            or row.get("language_review") != "approved"
        ):
            raise ValueError("Frozen case review incomplete")
        renderings = row.get("renderings", {})
        if not isinstance(renderings, Mapping):
            raise ValueError("Invalid frozen rendering records")
        for variant in config.variants:
            if renderings.get(variant) != digest(
                render(case, variant, config.rendering_seed)
            ):
                raise ValueError("Frozen reviewed rendering mismatch")


def check_frozen_reference(case, ref):
    label, _, proven = check_reference(case, ref)
    expected_stages = 3 if case.context else 1
    if label == "UNRESOLVED" or (label == "SAT" and len(proven) != expected_stages):
        raise ValueError(
            "Frozen reference needs a resolved label and exact objective proof"
        )
    if case.expected_label != label:
        raise ValueError("Frozen reference disagrees with reviewed label")


def draft_frozen_config(
    cases, config, manifest, development_fingerprints, *, mode="offline_frozen"
):
    """Produce a reviewable, deliberately non-runnable draft; never assert approval."""
    from dataclasses import replace
    from scheduling.evaluation.runner import _contract

    if mode not in FROZEN_MODES:
        raise ValueError("Unsupported frozen evidence mode")
    cfg = replace(config, evidence=mode, freeze={})
    contract = _contract(cases, cfg)
    freeze = {
        name: contract[name]
        for name in ("case_bundle_sha256", "source_sha256", "request_prompt_sha256")
    }
    freeze.update(
        format_version="1.0",
        protocol_id="",
        model_id=cfg.model.model,
        eligibility_reference="",
        approval_reference="",
        authorization_reference="",
        benchmark_manifest=manifest,
        settings_sha256=settings_digest(cfg),
        development_hard_fingerprints=development_fingerprints,
        development_registry_reference="",
        analysis_settings=ANALYSIS_SETTINGS,
    )
    return replace(cfg, freeze=freeze)
