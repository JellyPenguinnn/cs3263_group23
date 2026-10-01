"""Synthetic frozen fixtures qualify bookkeeping, never human approval or model accuracy."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

import pytest

from evaluation.rehearse_study import rehearse, synthetic_config
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.frozen import settings_digest
from scheduling.evaluation.runner import run_batch, read
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.study import (
    analyze_blocks,
    export_study,
    resource_statistics,
)
from scheduling.providers.types import Attempt, ModelResponse, Usage
from scheduling.providers.types import ProviderExecution
from scheduling.providers.execution import execution_contract
from scheduling.solver import SolverLimits
from tests.integration.test_evaluation import canned


@pytest.fixture(scope="module")
def rehearsal(tmp_path_factory):
    path = tmp_path_factory.mktemp("study") / "rehearsal"
    result = rehearse(path)
    return path, result


def blocks(path):
    return {role: path / role for role in ("controlled", "realistic", "language")}


def test_hand_checked_denominators_failures_pairing_and_no_inference(
    rehearsal, monkeypatch
):
    path, result = rehearsal
    monkeypatch.setattr(
        "scheduling.solver.solve", lambda *a, **k: pytest.fail("Replay must not solve")
    )
    monkeypatch.setattr(
        "scheduling.evaluation.runner.run_direct",
        lambda *a, **k: pytest.fail("Replay must not call"),
    )
    before = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for role in blocks(path).values()
        for p in role.rglob("*.json")
    }
    again = analyze_blocks(blocks(path))
    assert again == result
    assert result["counts"] == dict(
        primary_attempts=6,
        realistic_attempts=2,
        additional_language_attempts=8,
        unique_attempts=16,
    )
    assert sum(r["accepted"] for r in result["rows"]) == 15
    assert len(result["diagnostics"]["language_transitions"]) == 8
    assert all(r["repeat"] == r["raw_repeat"] == 0 for r in result["rows"])
    assert all(r["usage"] == [] for r in result["rows"])
    assert sum(r["without_provider_records"] for r in result["resources"]) == 16
    assert all(
        d["distributions"]["total_tokens"]["mean"] is None for d in result["resources"]
    )
    assert before == {
        p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before
    }


def test_archive_checksums_allowlist_and_replay(rehearsal, tmp_path):
    path, _ = rehearsal
    with tarfile.open(path / "analysis/reproduction.tar.gz") as archive:
        names = archive.getnames()
        assert not any(
            ".env" in n
            or "__pycache__" in n
            or n.startswith("/")
            or ".." in Path(n).parts
            for n in names
        )
        checks = json.load(archive.extractfile("CHECKSUMS.json"))
        assert set(names) == set(checks) | {"CHECKSUMS.json"}
        assert "tables/resources.csv" in checks
        for name, expected in checks.items():
            assert (
                hashlib.sha256(archive.extractfile(name).read()).hexdigest() == expected
            )
        archive.extractall(tmp_path, filter="data")
    result = analyze_blocks(
        {r: tmp_path / p for r, p in read(tmp_path / "blocks.json").items()}
    )
    original = read(tmp_path / "analysis.json")
    for field in (
        "counts",
        "primary_controlled",
        "realistic",
        "language",
        "resources",
        "diagnostics",
    ):
        assert digest(result[field]) == digest(original[field])


def test_duplicate_directory_rejected(rehearsal):
    path, _ = rehearsal
    with pytest.raises(ValueError, match="Duplicate run directory"):
        analyze_blocks(
            {"controlled": path / "controlled", "realistic": path / "controlled"}
        )


def test_missing_attempt_cannot_be_claimed_complete(rehearsal, tmp_path):
    path, _ = rehearsal
    shutil.copytree(path / "controlled", tmp_path / "controlled")
    next((tmp_path / "controlled/attempts").glob("*.json")).unlink()
    with pytest.raises(ValueError, match="Incomplete/uncertain"):
        analyze_blocks({"controlled": tmp_path / "controlled"})


def make_block(
    path,
    cases,
    role,
    variants,
    *,
    solver=None,
    live_fingerprint=None,
    missing_metadata=False,
):
    cfg = synthetic_config(cases, role, variants)
    if solver is not None:
        cfg = replace(cfg, solver=solver)
        cfg = replace(
            cfg, freeze={**cfg.freeze, "settings_sha256": settings_digest(cfg)}
        )
    if live_fingerprint is not None or missing_metadata:
        cfg = replace(cfg, evidence="live_frozen")
        cfg = replace(
            cfg, freeze={**cfg.freeze, "settings_sha256": settings_digest(cfg)}
        )
        outputs = iter(canned(cases, cfg).values())

        def callback(*_):
            attempts = (
                ()
                if missing_metadata
                else (
                    Attempt(
                        1,
                        0.1,
                        200,
                        Usage(2, 3, 5),
                        returned_model=cfg.model.model,
                        execution=ProviderExecution(
                            execution_contract(cfg.model), live_fingerprint
                        ),
                    ),
                )
            )
            return ModelResponse(next(outputs), cfg.model.model, 0.1, attempts)

        run_batch(cases, path, cfg, provider_complete=callback)
    else:
        run_batch(cases, path, cfg, canned=canned(cases, cfg))
    return path


@pytest.mark.parametrize("change", ["absent", "gold"])
def test_language_requires_exact_canonical_partner(rehearsal, tmp_path, change):
    path, _ = rehearsal
    from scheduling.evaluation.cases import load_cases

    cases = load_cases(path / "controlled/cases.json")
    case = (
        replace(tiny_fixtures()[2], split="test")
        if change == "absent"
        else replace(cases[0], justification="different gold provenance")
    )
    lang = make_block(
        tmp_path / "language", (case,), "language", ("paraphrase", "reordered")
    )
    with pytest.raises(ValueError, match="missing or changed canonical"):
        analyze_blocks({"controlled": path / "controlled", "language": lang})


def test_valid_individual_blocks_with_different_solver_settings_cannot_join(
    rehearsal, tmp_path
):
    path, _ = rehearsal
    case = replace(tiny_fixtures()[1], split="test", kind="realistic")
    real = make_block(
        tmp_path / "realistic",
        (case,),
        "realistic",
        ("canonical",),
        solver=SolverLimits(2),
    )
    with pytest.raises(ValueError, match="Incompatible"):
        analyze_blocks({"controlled": path / "controlled", "realistic": real})


def test_related_sources_cannot_cross_primary_and_realistic_blocks(rehearsal, tmp_path):
    path, _ = rehearsal
    original = tiny_fixtures()[0]
    case = replace(
        original,
        case_id="renamed",
        group_id="renamed-family",
        split="test",
        kind="realistic",
        problem=replace(original.problem, instance_id="renamed"),
    )
    real = make_block(tmp_path / "realistic", (case,), "realistic", ("canonical",))
    with pytest.raises(ValueError, match="related source family"):
        analyze_blocks({"controlled": path / "controlled", "realistic": real})


def test_live_fingerprints_must_agree_between_individually_stable_blocks(tmp_path):
    controlled = (replace(tiny_fixtures()[0], split="test"),)
    realistic = (replace(tiny_fixtures()[1], split="test", kind="realistic"),)
    a = make_block(
        tmp_path / "controlled",
        controlled,
        "controlled",
        ("canonical",),
        live_fingerprint="backend-one",
    )
    b = make_block(
        tmp_path / "realistic",
        realistic,
        "realistic",
        ("canonical",),
        live_fingerprint="backend-two",
    )
    with pytest.raises(ValueError, match="Backend fingerprint changed across blocks"):
        analyze_blocks({"controlled": a, "realistic": b})


def test_missing_live_execution_metadata_rejected(tmp_path):
    cases = (replace(tiny_fixtures()[0], split="test"),)
    a = make_block(
        tmp_path / "controlled",
        cases,
        "controlled",
        ("canonical",),
        missing_metadata=True,
    )
    with pytest.raises(ValueError, match="Missing live provider attempt metadata"):
        analyze_blocks({"controlled": a})


def test_resource_distributions_keep_missing_usage_and_tails():
    rows = [
        dict(
            study_block="controlled",
            approach="direct",
            timings=[("total_seconds", v)],
            usage=[dict(total_tokens=t)],
        )
        for v, t in ((1, 10), (2, None), (3, 30), (4, 40))
    ]
    result = resource_statistics(rows)[0]["distributions"]
    assert result["total_seconds"] == dict(
        observations=4,
        reported=4,
        missing=0,
        mean=2.5,
        median=2.5,
        p95_nearest_rank=4,
        max=4,
    )
    assert result["total_tokens"]["missing"] == 1
    assert result["total_tokens"]["median"] == 30
    assert result["solver_seconds"]["reported"] == 0


def archive_project(tmp_path):
    root = Path(__file__).resolve().parents[2]
    project = tmp_path / "project"
    (project / "evaluation").mkdir(parents=True)
    shutil.copytree(root / "prompts", project / "prompts")
    for name in ("pyproject.toml", "requirements.lock", "evaluation/analyze_study.py"):
        shutil.copy2(root / name, project / name)
    return project


@pytest.mark.parametrize(
    "prompt",
    ["direct/generation.txt", "direct/repair.txt", "extraction/specification.txt"],
)
def test_archive_rejects_checkout_prompt_drift_before_writing(
    rehearsal, tmp_path, prompt
):
    path, _ = rehearsal
    project = archive_project(tmp_path)
    (project / "prompts" / prompt).write_text(
        "Different instructions from the recorded run"
    )
    output = tmp_path / "export"
    with pytest.raises(ValueError, match="prompt"):
        export_study(blocks(path), output, project_root=project)
    assert not output.exists()


@pytest.mark.parametrize(
    "linked",
    ["prompts/direct/generation.txt", "evaluation/analyze_study.py", "prompts/direct"],
)
def test_archive_rejects_linked_project_inputs(rehearsal, tmp_path, linked):
    path, _ = rehearsal
    project = archive_project(tmp_path)
    original = project / linked
    outside = tmp_path / "outside"
    original.rename(outside)
    original.symlink_to(outside, target_is_directory=outside.is_dir())
    output = tmp_path / "export"
    with pytest.raises(ValueError, match="link"):
        export_study(blocks(path), output, project_root=project)
    assert not output.exists()


def test_archive_excludes_unrelated_prompt_sidecars(rehearsal, tmp_path):
    path, _ = rehearsal
    project = archive_project(tmp_path)
    (project / "prompts/private-notes.txt").write_text("synthetic-private-sentinel")
    output = tmp_path / "export"
    export_study(blocks(path), output, project_root=project)
    with tarfile.open(output / "reproduction.tar.gz") as archive:
        assert "source/prompts/private-notes.txt" not in archive.getnames()


@pytest.mark.parametrize("change", ["version", "missing"])
def test_archive_lock_must_reproduce_recorded_runtime(rehearsal, tmp_path, change):
    path, _ = rehearsal
    project = archive_project(tmp_path)
    lock = project / "requirements.lock"
    text = lock.read_text()
    assert "httpx==0.28.1" in text
    lock.write_text(
        text.replace(
            "httpx==0.28.1",
            "httpx==0.1.0" if change == "version" else "removed-httpx==0.28.1",
        )
    )
    output = tmp_path / "export"
    with pytest.raises(ValueError, match="lock"):
        export_study(blocks(path), output, project_root=project)
    assert not output.exists()
