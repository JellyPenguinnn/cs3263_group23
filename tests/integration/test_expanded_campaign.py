"""Diverse generation campaign guards and complete offline provider execution."""

from copy import deepcopy
import hashlib
import json
import shutil
import tarfile

import httpx
import pytest

from scheduling.dashboard.service import Dashboard
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.runner import OBSERVE_BACKEND_POLICY, read, replay, requests
from scheduling.evaluation.study import export_study
from scheduling.providers import SoCLaaSProvider
from scheduling.schema import Schedule
from scheduling.validation import validate_schedule
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script
from tests.unit.test_evidence_archive import verifier

prepare = load_script("prepare_development_campaign")
execute = load_script("run_development_campaign")


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    directory = tmp_path_factory.mktemp("diverse-source") / "dataset"
    load_script("prepare_diverse_generation").prepare(directory)
    return directory


@pytest.fixture(scope="module")
def packets(dataset, tmp_path_factory):
    result = {}
    for model in ("qwen3.6:35b", "x-test-1"):
        directory = tmp_path_factory.mktemp("diverse-packet") / "packet"
        prepare.prepare(dataset / "cases.json", None, directory, model=model,
                        qualification_policy=OBSERVE_BACKEND_POLICY,
                        design="diverse-generation-2000")
        result[model] = directory
    return result


def test_diverse_exact_budget_matched_models_and_prompts(packets):
    blocks_by_model = {}
    hashes = []
    for model, packet in packets.items():
        blocks, manifest = execute.load_packet(packet)
        cases, cfg, preflight = blocks["controlled"]
        blocks_by_model[model] = blocks
        assert set(blocks) == {"controlled"}
        assert len(cases) == 1000
        assert manifest["planned_scheduling_completions"] == 2000
        assert manifest["total_requests"] == 2003
        assert manifest["requested_output_tokens"] == 2002 * 32768
        assert preflight["reference_labels"] == {"SAT": 500, "UNSAT": 500}
        assert cfg.variants == ("canonical",)
        prompts = preflight["contract"]["request_prompt_sha256"]
        hashes.append({(case.case_id, identity["approach"], view.variant_id): prompts[key]
                       for key, identity, case, view in requests(cases, cfg)})
    assert hashes[0] == hashes[1]
    configs = [read(path / "controlled-config.json") for path in packets.values()]
    assert configs[0]["model"].pop("model") != configs[1]["model"].pop("model")
    assert configs[0] == configs[1]
    assert (packets["qwen3.6:35b"] / "controlled-cases.json").read_bytes() == (
        packets["x-test-1"] / "controlled-cases.json").read_bytes()


def test_diverse_prepare_requires_explicit_policy_model_and_new_directory(dataset, packets, tmp_path):
    for model, policy in (("qwen3.8:27b", OBSERVE_BACKEND_POLICY),
                          ("qwen3.6:35b", "strict_v1")):
        with pytest.raises(ValueError):
            prepare.prepare(dataset / "cases.json", None, tmp_path / "rejected", model=model,
                            qualification_policy=policy, design="diverse-generation-2000")
    assert not (tmp_path / "rejected").exists()
    with pytest.raises(FileExistsError):
        prepare.prepare(dataset / "cases.json", None, packets["qwen3.6:35b"],
                        model="qwen3.6:35b", qualification_policy=OBSERVE_BACKEND_POLICY,
                        design="diverse-generation-2000")


@pytest.mark.parametrize("change", (
    "count", "tokens", "model", "policy", "preparation_source", "execution_source",
    "package_source", "proof", "dataset_manifest", "case", "config", "wording_block",
))
def test_diverse_tampering_rejected_before_provider(packets, tmp_path, change):
    packet = tmp_path / "packet"
    shutil.copytree(packets["qwen3.6:35b"], packet)
    filename = {
        "package_source": "controlled-preflight.json", "proof": "dataset-proofs.json",
        "dataset_manifest": "dataset-manifest.json", "case": "dataset-cases.json",
        "config": "controlled-config.json",
    }.get(change, "campaign.json")
    data = read(packet / filename)
    if change == "count":
        data["blocks"]["controlled"]["case_count"] -= 1
    elif change == "tokens":
        data["requested_output_tokens"] += 32768
    elif change == "model":
        data["model"] = "default"
    elif change == "policy":
        data["qualification_policy"] = "strict_model_and_backend_v1"
    elif change in ("preparation_source", "execution_source"):
        data[change + "_sha256"] = "0" * 64
    elif change == "package_source":
        data["contract"]["source_sha256"]["solver.py"] = "0" * 64
    elif change == "proof":
        data.pop(next(iter(data)))
    elif change == "dataset_manifest":
        data["case_bundle_sha256"] = "0" * 64
    elif change == "case":
        data["cases"].pop()
    elif change == "config":
        data["model"]["read_timeout"] = 900
    else:
        data["blocks"]["language"] = deepcopy(data["blocks"]["controlled"])
    (packet / filename).write_text(json.dumps(data))
    with pytest.raises(ValueError):
        execute.run_campaign(packet, tmp_path / "must-not-exist", allow_live=True,
                             authorization_reference="OFFLINE tamper check only",
                             provider_factory=lambda **_: pytest.fail("Provider must not be created"))
    assert not (tmp_path / "must-not-exist").exists()


def mock_provider(packet, *, transient=False, mismatch=False):
    cases = load_cases(packet / "controlled-cases.json")
    cfg = execute.load_config(packet / "controlled-config.json")
    prepared = canned(cases, cfg)
    if transient:
        prepared[next(key for i, (key, identity, _, _) in enumerate(requests(cases, cfg))
                      if i >= 10 and identity["approach"] == "direct")] = "not JSON"
        for i, (key, identity, case, _) in enumerate(requests(cases, cfg)):
            if i >= 12 and identity["approach"] == "direct" and case.expected_label == "SAT":
                bad = [{"activity_id": a.id, "start_slot": 0} for a in case.problem.activities]
                if not validate_schedule(case.problem, Schedule.from_list(bad)).hard_feasible:
                    prepared[key] = json.dumps({"status": "SAT", "schedule": bad})
                    break
        else:
            pytest.fail("The full fixture must supply a gold-invalid schedule mutation")
    responses = iter(prepared.values())
    calls = []
    returned = "glm-5.3-flash" if cfg.model.model == "x-test-1" else cfg.model.model

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": cfg.model.model}]})
        index = len(calls) - 2
        content = '{"ok":true}' if index < 2 else next(responses)
        body = json.loads(request.content)
        assert body["model"] == cfg.model.model
        assert body["max_tokens"] == 32768
        if transient and index == 7:
            raise httpx.ReadTimeout("Offline injected timeout", request=request)
        if transient and index == 9:
            return httpx.Response(502)
        return httpx.Response(200, json={
            "model": "wrong-model" if mismatch and index == 2 else returned,
            "system_fingerprint": f"offline-backend-{index % 2}",
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
        })

    def factory(*, budget):
        return SoCLaaSProvider(api_key="test-only", budget=budget, transport=httpx.MockTransport(handler))

    return factory, calls


@pytest.mark.parametrize("model", ("qwen3.6:35b", "x-test-1"))
def test_full_diverse_mocked_campaign_replay_archive_dashboard(packets, tmp_path, monkeypatch, model):
    packet = packets[model]
    factory, calls = mock_provider(packet, transient=True)
    cooldowns = []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", cooldowns.append)
    run = tmp_path / "campaign"
    result = execute.run_campaign(packet, run, allow_live=True,
        authorization_reference="OFFLINE mock transport; zero real provider calls", provider_factory=factory)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == len(calls) == 2003
    assert result["requested_output_tokens_reserved"] == 2002 * 32768
    assert len(cooldowns) == 2
    rows, progress = replay(run / "controlled")
    assert progress["completed"] == len(rows) == 2000
    assert sum(r["accepted"] is True for r in rows) == 1996
    assert sum(r["category"] == "provider_error" for r in rows) == 2
    assert sum(r["category"] == "invalid_output" for r in rows) == 1
    assert sum(r["category"] == "gold_invalid_schedule" for r in rows) == 1
    exported = tmp_path / "analysis"
    analysis = export_study({"controlled": run / "controlled"}, exported,
                            project_root=ROOT, figures=False, development=True)
    assert analysis["counts"]["unique_attempts"] == 2000
    assert analysis["counts"]["additional_language_attempts"] == 0
    archive_path = exported / "reproduction.tar.gz"
    with tarfile.open(archive_path) as archive:
        checksums = json.load(archive.extractfile("CHECKSUMS.json"))
        assert "source/src/scheduling/evaluation/diverse_generation.py" in checksums
    assert verifier.verify_archive(archive_path, {
        "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "checksummed_members": len(checksums),
    })["verified_files"] == len(checksums)
    app = Dashboard(run, run_dir=run / "controlled")
    key = app.bootstrap()["selected"]
    assert app.overview(key)["progress"]["completed"] == 2000
    assert app.case_page(key, task="generation")["total"] == 1000
    assert app.case_page(key, task="repair")["total"] == 0
    with pytest.raises(FileExistsError):
        execute.run_campaign(packet, run, allow_live=True,
            authorization_reference="OFFLINE reuse must fail", provider_factory=factory)
    assert len(calls) == 2003


def test_diverse_glm_wrong_identity_stops_without_fallback(packets, tmp_path):
    factory, calls = mock_provider(packets["x-test-1"], mismatch=True)
    result = execute.run_campaign(packets["x-test-1"], tmp_path / "mismatch", allow_live=True,
        authorization_reference="OFFLINE identity test", provider_factory=factory)
    assert result["state"] != "completed"
    assert "model" in result["stop_reason"]
    assert len(calls) == 4


def test_diverse_requires_fresh_live_authorization(tmp_path):
    with pytest.raises(ValueError, match="authorization"):
        execute.run_campaign(tmp_path / "missing", tmp_path / "run",
                             provider_factory=lambda **_: pytest.fail("No provider before authorization"))
    assert not (tmp_path / "run").exists()
