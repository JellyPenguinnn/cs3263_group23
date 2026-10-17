"""The 200-attempt extension: certificates, exact budgets, failure retention and replay."""

from collections import Counter
from dataclasses import replace
import hashlib
import json

import httpx
import pytest

from scheduling.evaluation.benchmark import difficulty, render
from scheduling.evaluation.cases import load_cases, case_bundle
from scheduling.evaluation.difficulty_suite import (
    CALLS, TIERS, SIZES, CAMPAIGN_POLICY, check_design, select_language, verify_certificate,
)
from scheduling.evaluation.runner import OBSERVE_BACKEND_POLICY, read, replay
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.study import export_study
from scheduling.providers import SoCLaaSProvider
from scheduling.schema import Deadline, FixedStart
from scheduling.validation import validate_schedule
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script

prepare = load_script("prepare_development_campaign")
execute = load_script("run_development_campaign")
DATA = ROOT / "benchmarks/fixtures/difficulty-v1"


def test_saved_suite_balance_proofs_and_nontrivial_unsat():
    controlled, realistic = load_cases(DATA / "controlled.json"), load_cases(DATA / "realistic.json")
    manifest = read(DATA / "manifest.json")
    check_design(controlled, realistic)
    assert manifest["case_bundle_sha256"] == {"controlled": digest(case_bundle(controlled)),
                                             "realistic": digest(case_bundle(realistic))}
    assert len(controlled + realistic) == 80
    assert len({c.group_id for c in controlled + realistic}) == 40
    language = select_language(controlled)
    assert len(language) == len({c.group_id for c in language}) == 10
    assert language == select_language(tuple(reversed(controlled)))
    for case in controlled + realistic:
        assert len(case.problem.activities) == SIZES[TIERS.index(case.level)]
        assert all(difficulty(case.problem)["unary_start_counts"])
        proof = manifest["proofs"][case.case_id]
        assert proof["problem_sha256"] == digest(case.problem)
        assert verify_certificate(case.problem, proof["certificate"], case.witness)
        if case.expected_label == "SAT":
            validation = validate_schedule(case.problem, case.witness, case.context)
            assert validation.hard_feasible
            assert validation.objectives.as_tuple() == case.expected_objective
            assert proof["reference_optimality_proven"]
            if case.problem.task_type == "repair":
                assert case.expected_objective[0] > 0
                if case.sweep == "coupled_repair":
                    n = len(case.problem.activities)
                    assert case.expected_objective[:2] == (n, 2 * (n - 1))
        else:
            # Remove the stated conflict. A proof checker must reject this altered
            # problem, rather than trusting the unchanged label/certificate.
            kind = proof["certificate"]["kind"]
            drop = FixedStart if kind == "unit_slot_capacity" else Deadline
            weakened = replace(case.problem, constraints=tuple(c for c in case.problem.constraints if not isinstance(c, drop)))
            assert not verify_certificate(weakened, proof["certificate"])
        for variant in ("canonical", "paraphrase", "reordered"):
            text = render(case, variant).text
            assert case.case_id not in text and case.group_id not in text
            assert "certificate" not in text and "expected_label" not in text
            assert "human" not in text and "review" not in text
            assert all(a.id in text for a in case.problem.activities)


def test_cycle_certificates_agree_with_exhaustive_enumeration():
    from itertools import product
    from scheduling.schema import Schedule

    cases = load_cases(DATA / "controlled.json")
    for case in cases:
        if case.level != "easy" or case.sweep != "coupled_repair":
            continue
        domains = [{s for w in a.availability for s in range(w.start, w.end)} for a in case.problem.activities]
        values = []
        for starts in product(*domains):
            schedule = Schedule.from_list([{"activity_id": a.id, "start_slot": s}
                                           for a, s in zip(case.problem.activities, starts)])
            validation = validate_schedule(case.problem, schedule, case.context)
            if validation.hard_feasible:
                values.append(validation.objectives.as_tuple())
        assert bool(values) == (case.expected_label == "SAT")
        if values:
            assert min(values) == case.expected_objective


@pytest.fixture(scope="module", params=("qwen3.6:35b", "qwen3.8:27b"))
def packet(tmp_path_factory, request):
    path = tmp_path_factory.mktemp("difficulty-packet") / "input"
    prepare.prepare(DATA / "controlled.json", DATA / "realistic.json", path,
                    model=request.param, qualification_policy=OBSERVE_BACKEND_POLICY,
                    design="difficulty-200")
    return path


def test_packet_exact_200_and_immutable_inputs(packet):
    blocks, manifest = execute.load_packet(packet)
    assert manifest["policy_version"] == CAMPAIGN_POLICY
    assert manifest["planned_scheduling_completions"] == 200
    assert manifest["total_requests"] == 203
    assert manifest["requested_output_tokens"] == 6619136
    assert {r: p[2]["planned_requests"] for r, p in blocks.items()} == CALLS
    assert Counter(c.level for c in blocks["controlled"][0]) == {t: 12 for t in TIERS}
    with pytest.raises(FileExistsError):
        prepare.prepare(DATA / "controlled.json", DATA / "realistic.json", packet,
                        model=manifest["model"], design="difficulty-200")


def test_full_200_mocked_http_campaign_analysis_and_figures(packet, tmp_path, monkeypatch):
    model = read(packet / "campaign.json")["model"]
    responses = iter(content for role in execute.ROLES for content in canned(
        load_cases(packet / f"{role}-cases.json"),
        execute.load_config(packet / f"{role}-config.json")).values())
    calls = []
    cooldowns = []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", cooldowns.append)

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": model}]})
        i = len(calls) - 2
        content = '{"ok":true}' if i < 2 else next(responses)
        if i == 121:  # Last controlled attempt: later blocks must still run.
            raise httpx.ReadTimeout("offline fixture", request=request)
        if i == 122:  # First realistic attempt.
            return httpx.Response(503)
        body = json.loads(request.content)
        assert body["model"] == model and body["max_tokens"] == 32768
        return httpx.Response(200, json={"model": model, "system_fingerprint": f"backend-{i % 2}",
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}})

    def factory(*, budget):
        return SoCLaaSProvider(api_key="test-only", budget=budget, transport=httpx.MockTransport(handler))

    directory = tmp_path / "campaign"
    result = execute.run_campaign(packet, directory, allow_live=True,
        authorization_reference="OFFLINE TEST mock transport only", provider_factory=factory)
    assert result["state"] == "completed"
    assert len(calls) == result["requests_reserved"] == 203
    assert result["requested_output_tokens_reserved"] == 6619136
    assert len(cooldowns) == 2
    all_rows = []
    for role, count in CALLS.items():
        rows, progress = replay(directory / role)
        assert len(rows) == progress["completed"] == count
        all_rows.extend(rows)
    assert sum(r["accepted"] is True for r in all_rows) == 198
    analysis = export_study({r: directory / r for r in execute.ROLES}, tmp_path / "analysis",
                            project_root=ROOT, development=True, figures=True)
    assert len(analysis["rows"]) == 200
    assert sum(r["accepted"] is True for r in analysis["rows"]) == 198
    assert (tmp_path / "analysis/tables/difficulty.png").is_file()
    assert (tmp_path / "analysis/tables/tier-comparison.png").is_file()
    for name in ("study_strata.csv", "tier_resources.csv", "paired_attempts.csv", "interpretation.md", "casebook.json"):
        assert (tmp_path / "analysis/tables" / name).is_file()
    support = analysis["interpretation"]
    assert len(support["attempt_diagnostics"]) == 200
    assert len(support["paired_attempts"]) == 100
    assert sum(e["accepted"] is False for e in support["casebook"]) == 2
    assert all(r["unscored"] == 0 for r in support["strata"])
    assert sum(r["attempts"] for r in support["strata"] if r["scope"] == "block") == 200
    for example in support["casebook"]:
        trace = example["trace"]
        identity = example["identity"]
        file = directory / identity["study_block"] / "attempts" / trace["attempt_member"].split("/")[-1]
        assert hashlib.sha256(file.read_bytes()).hexdigest() == trace["attempt_sha256"]
        assert example["human_interpretation"] == "pending"
        assert example["public_request"]["text"]


def test_unknown_design_and_incompatible_counts_rejected(tmp_path):
    with pytest.raises(ValueError, match="design"):
        prepare.prepare(DATA / "controlled.json", DATA / "realistic.json", tmp_path / "x", design="unknown")
    with pytest.raises(ValueError, match="case counts"):
        prepare.prepare(DATA / "controlled.json", DATA / "realistic.json", tmp_path / "x")
