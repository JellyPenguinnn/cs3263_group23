"""D5's controlled-only protocol through real orchestration, with offline HTTP."""

from copy import deepcopy
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from types import SimpleNamespace

import httpx
import pytest

from scheduling.dashboard.service import Dashboard
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.runner import OBSERVE_BACKEND_POLICY, read, replay, requests
from scheduling.evaluation.study import export_study
from scheduling.providers import SoCLaaSProvider
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script
from tests.unit.test_evidence_archive import verifier

prepare = load_script("prepare_development_campaign")
execute = load_script("run_development_campaign")


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    directory = tmp_path_factory.mktemp("balanced-source") / "dataset"
    load_script("prepare_balanced_generation").prepare(directory)
    return directory


@pytest.fixture(scope="module", params=("qwen3.6:35b", "x-test-1"))
def packet(dataset, tmp_path_factory, request):
    directory = tmp_path_factory.mktemp("balanced-packet") / "packet"
    prepare.prepare(dataset / "cases.json", None, directory, model=request.param,
                    qualification_policy=OBSERVE_BACKEND_POLICY, design="balanced-generation-96")
    return directory


def mock_provider(packet, *, transient=False, mismatch=False):
    blocks, manifest = execute.load_packet(packet)
    cases, cfg, _ = blocks["controlled"]
    responses = iter(canned(cases, cfg).values())
    calls = []
    returned = "glm-5.3-flash" if manifest["model"] == "x-test-1" else manifest["model"]

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": manifest["model"]}]})
        index = len(calls) - 2
        content = '{"ok":true}' if index < 2 else next(responses)
        body = json.loads(request.content)
        assert body["model"] == manifest["model"]
        assert body["max_tokens"] == 32768
        if transient and index == 7:
            raise httpx.ReadTimeout("offline injected timeout", request=request)
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


def test_balanced_packet_and_equivalent_model_settings(packet, dataset, tmp_path):
    blocks, manifest = execute.load_packet(packet)
    assert set(blocks) == {"controlled"}
    assert len(blocks["controlled"][0]) == 48
    assert manifest["planned_scheduling_completions"] == 96
    assert manifest["total_requests"] == 99
    assert manifest["requested_output_tokens"] == 3211264
    assert blocks["controlled"][2]["reference_labels"] == {"SAT": 24, "UNSAT": 24}
    other_model = "x-test-1" if manifest["model"] == "qwen3.6:35b" else "qwen3.6:35b"
    other = tmp_path / "other-model"
    prepare.prepare(dataset / "cases.json", None, other, model=other_model,
                    qualification_policy=OBSERVE_BACKEND_POLICY, design="balanced-generation-96")
    left, right = read(packet / "controlled-config.json"), read(other / "controlled-config.json")
    assert left["model"].pop("model") != right["model"].pop("model")
    assert left == right
    assert (packet / "controlled-cases.json").read_bytes() == (other / "controlled-cases.json").read_bytes()
    def paired_prompt_hashes(path):
        cases = load_cases(path / "controlled-cases.json")
        cfg = execute.load_config(path / "controlled-config.json")
        hashes = read(path / "controlled-preflight.json")["contract"]["request_prompt_sha256"]
        return {(case.case_id, identity["approach"], view.variant_id, identity["repeat"]): hashes[key]
                for key, identity, case, view in requests(cases, cfg)}
    # Attempt keys include model configuration; compare hashes by the shared task identity.
    assert paired_prompt_hashes(packet) == paired_prompt_hashes(other)
    with pytest.raises(FileExistsError):
        prepare.prepare(dataset / "cases.json", None, packet, model=manifest["model"],
                        qualification_policy=OBSERVE_BACKEND_POLICY, design="balanced-generation-96")


@pytest.mark.parametrize("transient", (False, True))
def test_full_balanced_mocked_campaign_archive_replay_dashboard(packet, tmp_path, monkeypatch, transient):
    factory, calls = mock_provider(packet, transient=transient)
    cooldowns = []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", cooldowns.append)
    run = tmp_path / "campaign"
    result = execute.run_campaign(packet, run, allow_live=True,
        authorization_reference="OFFLINE MOCK TRANSPORT; zero real provider calls", provider_factory=factory)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == len(calls) == 99
    assert result["requested_output_tokens_reserved"] == 3211264
    assert len(cooldowns) == (2 if transient else 0)
    rows, progress = replay(run / "controlled")
    assert progress["completed"] == len(rows) == 96
    assert sum(row["accepted"] is True for row in rows) == (94 if transient else 96)
    assert sum(row["category"] == "provider_error" for row in rows) == (2 if transient else 0)
    exported = tmp_path / "analysis"
    analysis = export_study({"controlled": run / "controlled"}, exported,
                            project_root=ROOT, figures=True, development=True)
    assert analysis["counts"]["unique_attempts"] == 96
    assert analysis["counts"]["realistic_attempts"] == 0
    assert analysis["counts"]["additional_language_attempts"] == 0
    assert (exported / "tables/diagnostics.png").is_file()
    archive_path = exported / "reproduction.tar.gz"
    with tarfile.open(archive_path) as archive:
        checksums = json.load(archive.extractfile("CHECKSUMS.json"))
    assert verifier.verify_archive(archive_path, {
        "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "checksummed_members": len(checksums),
    })["verified_files"] == len(checksums)
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with tarfile.open(archive_path) as archive:
        archive.extractall(extracted, filter="data")
    command = [sys.executable, str(extracted / "source/evaluation/analyze_study.py"),
               str(extracted / "blocks.json"), str(tmp_path / "replayed"), "--development", "--no-archive"]
    subprocess.run(command, check=True, capture_output=True, text=True,
                   env={**os.environ, "PYTHONPATH": str(extracted / "source/src"), "PYTHONDONTWRITEBYTECODE": "1"})
    assert read(tmp_path / "replayed/analysis.json") == read(exported / "analysis.json")
    app = Dashboard(run, run_dir=run / "controlled")
    key = app.bootstrap()["selected"]
    assert app.overview(key)["progress"]["completed"] == 96
    assert app.case_page(key, task="generation")["total"] == 48
    assert app.case_page(key, task="repair")["total"] == 0
    with pytest.raises(FileExistsError):
        execute.run_campaign(packet, run, allow_live=True,
            authorization_reference="OFFLINE reuse must fail", provider_factory=factory)
    assert len(calls) == 99


def test_balanced_wrong_response_identity_stops_without_fallback(packet, tmp_path):
    factory, calls = mock_provider(packet, mismatch=True)
    result = execute.run_campaign(packet, tmp_path / "mismatch", allow_live=True,
        authorization_reference="OFFLINE mismatch test", provider_factory=factory)
    assert result["state"] != "completed"
    assert "model" in result["stop_reason"]
    assert len(calls) == 4


@pytest.mark.parametrize("change", ("proof", "manifest", "blocks", "block_details", "tokens", "source", "cases"))
def test_balanced_changed_packet_rejected_before_provider(packet, tmp_path, change):
    import shutil
    copy = tmp_path / "packet"
    shutil.copytree(packet, copy)
    file = {"proof": "dataset-proofs.json", "manifest": "dataset-manifest.json",
            "blocks": "campaign.json", "block_details": "campaign.json", "tokens": "campaign.json",
            "source": "controlled-preflight.json", "cases": "dataset-cases.json"}[change]
    data = read(copy / file)
    if change == "proof":
        data.pop(next(iter(data)))
    elif change == "manifest":
        data["case_bundle_sha256"] = "0" * 64
    elif change == "blocks":
        data["blocks"]["language"] = deepcopy(data["blocks"]["controlled"])
    elif change == "block_details":
        data["blocks"]["controlled"]["case_count"] = 999
        data["blocks"]["controlled"]["planned_requests"] = 999
        data["blocks"]["controlled"]["task_label_counts"] = {"generation/SAT": 999}
    elif change == "tokens":
        data["requested_output_tokens"] += 1
    elif change == "source":
        data["contract"]["source_sha256"]["solver.py"] = "0" * 64
    else:
        # Preserve valid JSON while removing an entire matched case.
        data["cases"].pop()
    (copy / file).write_text(json.dumps(data))
    with pytest.raises(ValueError):
        execute.run_campaign(copy, tmp_path / "must-not-exist", allow_live=True,
            authorization_reference="OFFLINE tamper test",
            provider_factory=lambda **_: pytest.fail("Must reject before provider creation"))
    assert not (tmp_path / "must-not-exist").exists()


def test_supervisor_exports_only_validated_balanced_roles(packet, tmp_path, monkeypatch):
    supervisor = load_script("supervise_development_campaign")
    factory, calls = mock_provider(packet)
    original = execute.run_campaign
    monkeypatch.setattr(supervisor, "load_credentials", lambda _: {"SOCLAAS_API_KEY": "test-only"})
    monkeypatch.setattr(supervisor, "run_campaign", lambda *a, **kw: original(*a, **kw, provider_factory=factory))
    args = SimpleNamespace(packet=packet, directory=tmp_path, env_file=tmp_path / "unused",
                           authorization_reference="OFFLINE supervisor transport test")
    assert supervisor.worker(args) == 0
    assert len(calls) == 99
    assert read(tmp_path / "worker-exit.json")["state"] == "analysis_exported"
    assert read(tmp_path / "analysis/analysis.json")["counts"]["unique_attempts"] == 96
