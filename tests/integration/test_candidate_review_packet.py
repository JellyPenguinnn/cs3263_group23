"""A gold/text review packet preserves exact evidence and cannot invent approval."""

from copy import deepcopy
from pathlib import Path

import pytest

from evaluation.prepare_case_review import prepare_review
from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.runner import read, write_new
from scheduling.evaluation.scoring import digest, reference
from scheduling.solver import SolverLimits


@pytest.fixture
def source(tmp_path):
    case = load_cases(Path(__file__).resolve().parents[1] / "examples/f3-formal-review.json")[0]
    path = tmp_path / "source"
    path.mkdir()
    write_new(path / "cases.json", case_bundle((case,)))
    write_new(path / "references.json", {case.case_id: reference(case, SolverLimits())})
    write_new(path / "manifest.json", {
        "mode": "development", "quota_complete": False, "case_count": 1,
        "policy": {"rendering_seed": 3263},
        "cases": [{"case_id": case.case_id, "sha256": digest(case),
                   "renderings": {v: digest(render(case, v, 3263)) for v in
                                  ("canonical", "paraphrase", "reordered")}}],
    })
    return path, case


def test_packet_keeps_exact_gold_text_and_pending_review(source, tmp_path):
    path, case = source
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    output = tmp_path / "review"
    receipt = prepare_review(path, output)
    record = read(output / (digest(case.case_id) + ".json"))
    assert receipt["human_review"] == "pending"
    assert receipt["source_quota_complete"] is False
    assert record["reference"] == read(path / "references.json")[case.case_id]
    assert record["gold_review_status"] == record["text_review_status"] == "pending"
    assert record["public_views"]["canonical"]["text"] == render(case).text
    assert before == {p.name: p.read_bytes() for p in path.iterdir()}
    with pytest.raises(FileExistsError):
        prepare_review(path, output)


@pytest.mark.parametrize("change", ["case_hash", "text_hash", "reference", "partial"])
def test_changed_or_partial_evidence_rejected_before_output(source, tmp_path, change):
    import json

    path, case = source
    manifest = deepcopy(read(path / "manifest.json"))
    if change == "case_hash":
        manifest["cases"][0]["sha256"] = "wrong"
    elif change == "text_hash":
        manifest["cases"][0]["renderings"]["canonical"] = "wrong"
    elif change == "partial":
        manifest["cases"] = []
    else:
        refs = read(path / "references.json")
        refs[case.case_id]["context_sha256"] = "wrong"
        (path / "references.json").write_text(json.dumps(refs))
    (path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        prepare_review(path, tmp_path / "review")
    assert not (tmp_path / "review").exists()
