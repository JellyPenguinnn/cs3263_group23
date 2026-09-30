"""Authored-text plumbing and synthetic drafts; no human approval or model evidence."""

from collections import Counter
from copy import deepcopy
from dataclasses import fields, replace
from itertools import product
import json
from pathlib import Path

import pytest

from scheduling.evaluation.benchmark import render, tiny_fixtures
from scheduling.evaluation.cases import (
    AuthoredBenchmarkCase,
    AuthoredRendering,
    BenchmarkCase,
    case_bundle,
    load_cases,
)
from scheduling.evaluation.frozen import settings_digest
from scheduling.evaluation.manifests import structural_audit
from scheduling.evaluation.runner import _contract, plan_run, replay, run_batch
from scheduling.evaluation.scoring import digest, reference, evaluate
from scheduling.pipelines.direct import build_messages
from scheduling.pipelines.solver_augmented import build_extraction_messages
from scheduling.schema import PipelineResult, Schedule, to_data
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule
from tests.formal_support import assignment_objective, enumerate_answers
from tests.integration.test_evaluation import canned, config
from tests.integration.test_frozen_evaluation import frozen_setup

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "benchmarks/fixtures/realistic-drafts-v1.json"


def authored(case=None):
    base = case or tiny_fixtures()[0]
    return AuthoredBenchmarkCase(
        **{f.name: getattr(base, f.name) for f in fields(BenchmarkCase)},
        authored_renderings=(
            AuthoredRendering(
                "canonical",
                "Synthetic verbatim test prose.\nKeep this line exactly.",
                "llm_assisted",
                "TEST AUTHOR ONLY",
                "Tests plumbing, not text semantics.",
            ),
        ),
        gold_author_reference="TEST GOLD AUTHOR ONLY",
    )


def test_legacy_serialization_and_mixed_bundle_roundtrip(tmp_path):
    legacy = tiny_fixtures()
    bundle = case_bundle(iter(legacy))
    assert bundle == {"format_version": "1.0", "cases": [to_data(c) for c in legacy]}
    assert all("authored_renderings" not in to_data(c) for c in legacy)
    mixed = (legacy[1], authored())
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(case_bundle(mixed)))
    assert case_bundle(mixed)["format_version"] == "2.0"
    assert load_cases(path) == mixed
    assert digest(load_cases(path)[0]) == digest(legacy[1])
    data = case_bundle(mixed)
    data["format_version"] = "1.0"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="version 2.0"):
        load_cases(path)


def test_exact_public_prose_and_no_provenance_gold_leak():
    case = authored()
    view = render(case)
    assert view.text == case.authored_renderings[0].text
    messages = [
        build_messages(
            view.text, task_type=view.task_type, required_activity_ids=view.activity_ids
        ),
        build_extraction_messages(view),
    ]
    for prompt in messages:
        assert view.text in json.loads(prompt[-1].content).values()
        prompt = to_data(prompt)
        assert "TEST AUTHOR" not in json.dumps(prompt)
        assert "TEST GOLD" not in json.dumps(prompt)
        assert case.justification not in json.dumps(prompt)
    changed_gold = replace(case, problem=replace(case.problem, constraints=()))
    assert render(changed_gold).text == view.text
    assert render(case, rendering_seed=99).text == view.text


def test_missing_authored_variant_stops_before_calls(tmp_path):
    case = authored()
    cfg = config(evidence="live_development", variants=("canonical", "paraphrase"))
    with pytest.raises(ValueError, match="Missing authored rendering"):
        run_batch(
            (case,),
            tmp_path / "run",
            cfg,
            provider_complete=lambda *_: pytest.fail("No provider call"),
        )
    assert not (tmp_path / "run").exists()


@pytest.mark.parametrize(
    "change",
    [
        {"text": " "},
        {"creation_method": "human-ish"},
        {"author_reference": ""},
        {"rationale": ""},
        {"review_status": "approved"},
        {"review_reference": "Not actually approved"},
        {"variant_id": "unknown"},
    ],
)
def test_authored_metadata_rejects_missing_or_false_state(change):
    with pytest.raises(ValueError):
        replace(authored().authored_renderings[0], **change)


def test_duplicate_variants_and_missing_canonical_rejected():
    case = authored()
    text = case.authored_renderings[0]
    for variants in ((text, text), (replace(text, variant_id="paraphrase"),)):
        with pytest.raises(ValueError):
            replace(case, authored_renderings=variants)


def freeze_authored(case, *, provenance="llm_assisted"):
    _, cfg = frozen_setup()
    f = deepcopy(cfg.freeze)
    contract = _contract((case,), cfg)
    for k in ("source_sha256", "case_bundle_sha256", "request_prompt_sha256"):
        f[k] = contract[k]
    audit = structural_audit((case,))
    f["benchmark_manifest"]["cases"] = [
        {
            "case_id": case.case_id,
            "group_id": case.group_id,
            "split": case.split,
            "source_family_id": audit["family_for_group"][case.group_id],
            "sha256": digest(case),
            "creation_method": provenance,
            "fixture_review": "approved",
            "language_review": "approved",
            "gold_review_reference": case.gold_review_reference,
            "renderings": {"canonical": digest(render(case))},
        }
    ]
    return replace(cfg, freeze=f)


def test_frozen_authored_reviews_and_provenance_are_bound_to_text():
    # Deliberately retagged known fixture for guard tests, never real held-out data.
    case = replace(authored(), split="test")
    with pytest.raises(ValueError, match="gold needs"):
        plan_run((case,), freeze_authored(case))
    case = replace(case, gold_review_reference="TEST REVIEW ONLY")
    with pytest.raises(ValueError, match="text review incomplete"):
        plan_run((case,), freeze_authored(case))
    text = replace(
        case.authored_renderings[0],
        review_status="approved",
        review_reference="TEST TEXT REVIEW ONLY",
    )
    case = replace(case, authored_renderings=(text,))
    cfg = freeze_authored(case)
    assert plan_run((case,), cfg)["state"] == "ready"
    with pytest.raises(ValueError, match="provenance disagrees"):
        plan_run((case,), freeze_authored(case, provenance="human_written"))
    changed = replace(
        case, authored_renderings=(replace(text, text=text.text + " changed"),)
    )
    with pytest.raises(ValueError, match="mismatch"):
        plan_run((changed,), cfg)


def test_procedural_renderer_cannot_claim_human_authorship():
    cases, cfg = frozen_setup()
    f = deepcopy(cfg.freeze)
    f["benchmark_manifest"]["cases"][0]["creation_method"] = "human_written"
    with pytest.raises(ValueError, match="verbatim authored text"):
        plan_run(cases, replace(cfg, freeze=f))


@pytest.mark.parametrize("index", range(12))
def test_draft_gold_matches_complete_independent_enumeration(index):
    case = load_cases(DRAFTS)[index]
    old = case.original_schedule.starts() if case.context else None
    answers = enumerate_answers(case.problem, old)
    assert bool(answers) == (case.expected_label == "SAT")
    assert min((obj for obj, _ in answers), default=None) == case.expected_objective
    result = solve(case.problem, SolverLimits(10), case.context)
    assert result.status == ("OPTIMAL" if answers else "INFEASIBLE")
    if answers:
        assert result.objectives.as_tuple() == case.expected_objective
    # Every assignment, not only the generated witness, cross-checks independent
    # validator feasibility and objectives against a separate arithmetic oracle.
    for values in product(
        range(case.problem.horizon_slots), repeat=len(case.problem.activities)
    ):
        starts = dict(zip((a.id for a in case.problem.activities), values))
        expected = assignment_objective(case.problem, starts, old)
        schedule = Schedule.from_list(
            [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
        )
        validated = validate_schedule(case.problem, schedule, case.context)
        assert validated.hard_feasible == (expected is not None)
        if expected is not None:
            assert validated.objectives.as_tuple() == expected
    if case.context:
        assert validate_schedule(
            case.original_problem, case.original_schedule
        ).hard_feasible


def test_all_drafts_are_honest_development_and_complete_canned_roundtrip(
    tmp_path, monkeypatch
):
    cases = load_cases(DRAFTS)
    assert Counter(c.problem.task_type for c in cases) == {"generation": 6, "repair": 6}
    assert Counter(c.expected_label for c in cases) == {"SAT": 6, "UNSAT": 6}
    assert Counter(c.level for c in cases) == {"personal": 6, "shared": 6}
    assert Counter(c.event for c in cases if c.context) == {
        "new blocked interval": 2,
        "tightened deadline": 2,
        "changed fixed appointment": 2,
    }
    assert all(c.split == "development" and c.kind == "realistic" for c in cases)
    assert all(
        c.gold_review_reference is None
        and all(
            r.creation_method == "llm_assisted" and r.review_status == "pending"
            for r in c.authored_renderings
        )
        for c in cases
    )
    cfg = config()
    responses = canned(cases, cfg)
    assert run_batch(cases, tmp_path, cfg, canned=responses)["completed"] == 24
    monkeypatch.setattr(
        "scheduling.evaluation.runner.run_direct",
        lambda *_a, **_k: pytest.fail("No new calls"),
    )
    monkeypatch.setattr(
        "scheduling.evaluation.runner.run_solver_augmented",
        lambda *_a, **_k: pytest.fail("No new calls"),
    )
    assert run_batch(cases, tmp_path, cfg, canned=responses)["reserved_requests"] == 24
    rows, progress = replay(tmp_path)
    assert progress["completed"] == 24 and all(r["accepted"] for r in rows)
