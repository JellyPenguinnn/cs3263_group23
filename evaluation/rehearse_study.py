"""Synthetic offline F4/F5 rehearsal. Never final data, human approvals or inference."""

from dataclasses import replace
import argparse
import json
from pathlib import Path

from scheduling.evaluation.benchmark import tiny_fixtures, render
from scheduling.evaluation.frozen import draft_frozen_config
from scheduling.evaluation.manifests import (
    FINGERPRINT_VERSION,
    structural_audit,
    development_registry,
)
from scheduling.evaluation.runner import (
    RunConfig,
    requests,
    run_batch,
    plan_run,
    replay,
    write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.study import export_study
from scheduling.providers import ModelConfig
from scheduling.pipelines.solver_augmented import PUBLIC_REQUEST_ID
from scheduling.solver import SolverLimits

MARKER = "SYNTHETIC OFFLINE REHEARSAL ONLY; no human or scientific approval"


def synthetic_config(cases, role, variants):
    count = len(cases) * len(variants) * 2
    cfg = RunConfig(
        ModelConfig("offline-rehearsal", 2048),
        SolverLimits(),
        SolverLimits(),
        count,
        count * 2048,
        variants=variants,
    )
    audit = structural_audit(cases)
    manifest = {
        "format_version": "2.0",
        "fingerprint_version": FINGERPRINT_VERSION,
        "dataset_version": "synthetic-guard-fixture-not-final",
        "status": "reviewed_frozen",
        "human_fixture_review": "approved",
        "human_language_review": "approved",
        "review_references": {"gold": MARKER, "language": MARKER},
        "cases": [
            {
                "case_id": c.case_id,
                "group_id": c.group_id,
                "source_family_id": audit["family_for_group"][c.group_id],
                "split": c.split,
                "sha256": digest(c),
                "creation_method": "fixed_fixture",
                "fixture_review": "approved",
                "language_review": "approved",
                "renderings": {
                    v: digest(render(c, v, cfg.rendering_seed)) for v in variants
                },
            }
            for c in cases
        ],
    }
    draft = draft_frozen_config(cases, cfg, manifest, development_registry({}))
    try:
        plan_run(cases, draft)
    except ValueError as error:
        if "decision references" not in str(error):
            raise
    else:
        raise AssertionError("Draft unexpectedly runnable")
    freeze = {
        **draft.freeze,
        "protocol_id": "synthetic-" + role,
        **{
            k: MARKER
            for k in (
                "eligibility_reference",
                "approval_reference",
                "authorization_reference",
                "development_registry_reference",
            )
        },
    }
    return replace(draft, freeze=freeze)


def rehearse(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    fixtures = tiny_fixtures()
    controlled = tuple(
        replace(c, split="test") for c in (fixtures[0], fixtures[4], fixtures[5])
    )
    realistic = (replace(fixtures[1], split="test", kind="realistic"),)
    blocks = {}
    for role, cases, variants in [
        ("controlled", controlled, ("canonical",)),
        ("realistic", realistic, ("canonical",)),
        ("language", (controlled[0], controlled[2]), ("paraphrase", "reordered")),
    ]:
        cfg = synthetic_config(cases, role, variants)
        canned = {}
        for key, identity, case, _ in requests(cases, cfg):
            canned[key] = (
                replace(case.problem, instance_id=PUBLIC_REQUEST_ID).to_json()
                if identity["approach"] == "solver_augmented"
                else json.dumps(
                    {
                        "status": case.expected_label,
                        "schedule": case.witness.to_list() if case.witness else None,
                    }
                )
            )
            if (
                role == "controlled"
                and case.case_id == controlled[0].case_id
                and identity["approach"] == "direct"
            ):
                canned[key] = "deliberate malformed response; keep in denominator"
        blocks[role] = directory / role
        done = run_batch(cases, blocks[role], cfg, canned=canned)
        assert done["completed"] == cfg.max_requests
        resumed = run_batch(cases, blocks[role], cfg, canned=canned)
        assert resumed["reserved_requests"] == cfg.max_requests
        assert replay(blocks[role])[1]["not_started"] == 0
    write_new(directory / "blocks.json", {role: role for role in blocks})
    result = export_study(
        blocks, directory / "analysis", project_root=Path(__file__).resolve().parents[1]
    )
    write_new(
        directory / "rehearsal.json",
        {
            "evidence": MARKER,
            "new_model_calls": 0,
            "counts": result["counts"],
            "deliberate_failures": sum(not r["accepted"] for r in result["rows"]),
        },
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    print(rehearse(p.parse_args().directory)["counts"])
