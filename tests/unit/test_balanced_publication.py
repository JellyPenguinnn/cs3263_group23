"""Publication checks use preserved live evidence, never provider calls."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def builder(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    return importlib.import_module("build_balanced_comparison")


@pytest.fixture
def manifest():
    return json.loads((ROOT / "results/balanced-evidence-manifest.json").read_text())


def test_balanced_summary_keeps_primary_failures_and_conditional_objectives(builder, manifest):
    summary = builder.build(manifest)
    qwen = summary["models"]["qwen36"]["overall_by_method"]
    glm = summary["models"]["glm53flash"]["overall_by_method"]
    assert (qwen["direct"]["accepted"], qwen["direct"]["attempts"]) == (6, 48)
    assert qwen["direct"]["categories"] == {
        "accepted": 6, "gold_invalid_schedule": 23, "false_unsat": 9, "invalid_output": 10,
    }
    assert (glm["direct"]["accepted"], glm["direct"]["attempts"]) == (47, 48)
    assert glm["direct"]["secondary_returned_answer_acceptance"]["returned_answers"] == 47
    assert (qwen["direct"]["objective_matches"], qwen["direct"]["objective_comparable"]) == (0, 1)
    assert (glm["direct"]["objective_matches"], glm["direct"]["objective_comparable"]) == (22, 23)
    for methods in (qwen, glm):
        assert methods["solver_augmented"]["accepted"] == 48
        assert methods["solver_augmented"]["objective_matches"] == 24
    assert summary["models"]["glm53flash"]["resources"]["direct"]["total_tokens"]["missing"] == 1
    assert summary["comparison_checks"]["all_96_paired_prompt_hashes_and_public_views_match"]


def test_balanced_summary_is_reproducible_and_does_not_modify_archives(builder, manifest):
    before = {e["path"]: hashlib.sha256((ROOT / e["path"]).read_bytes()).hexdigest()
              for e in manifest["archives"]}
    first = builder.build(manifest)
    assert first == builder.build(manifest)
    assert first == json.loads((ROOT / "results/summary/balanced-comparison-20261017.json").read_text())
    assert before == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in before}


def test_balanced_summary_rejects_duplicate_model_in_place_of_pair(builder, manifest):
    invalid = deepcopy(manifest)
    invalid["archives"][1] = deepcopy(invalid["archives"][0])
    with pytest.raises(ValueError, match="exactly the Qwen3.6 and GLM"):
        builder.build(invalid)
