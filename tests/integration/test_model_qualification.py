"""F2 selection uses preserved development inputs and never calls a model."""

from collections import Counter
from dataclasses import replace
import importlib.util
from pathlib import Path

import pytest

from scheduling.evaluation.benchmark import generate_development_v2, generate_development_v3
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.runner import read, write_new
from scheduling.evaluation.scoring import digest


ROOT = Path(__file__).resolve().parents[2]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "evaluation" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pool():
    a, pa, _ = generate_development_v2(3264)
    b, pb, _ = generate_development_v3(3265)
    return load_script("prepare_development_expansion").select_cases(a, b, {**pa, **pb})


def test_fixed_packet_balances_strata_and_retains_failures_longest_and_coupled(pool):
    script = load_script("prepare_model_qualification")
    selected, reasons, sizes = script.select_cases(pool)
    assert len(selected) == len({c.case_id for c in selected}) == 24
    assert set(script.FAILURES) <= set(reasons)
    assert Counter((c.problem.task_type, c.expected_label) for c in selected) == {
        (t, label): 6 for t in ("generation", "repair") for label in ("SAT", "UNSAT")
    }
    for task in ("generation", "repair"):
        for label in ("SAT", "UNSAT"):
            matches = lambda c: (c.problem.task_type, c.expected_label) == (task, label)
            subset = [c for c in selected if matches(c)]
            assert max(sizes[c.case_id] for c in subset) == max(sizes[c.case_id] for c in pool if matches(c))
            assert any(c.sweep == "resource_chain" and c.level == "5" for c in subset)
    again, again_reasons, _ = script.select_cases(reversed(pool))
    assert selected == again and reasons == again_reasons
    assert all(c in pool for c in selected)


def test_packet_preflight_two_models_same_inputs_settings_and_no_overwrite(pool, tmp_path):
    script = load_script("prepare_model_qualification")
    source = tmp_path / "source.json"
    write_new(source, case_bundle(pool))
    manifest = ROOT / "benchmarks/manifests/expanded-development-100-20260930.json"
    before = source.read_bytes()
    output = tmp_path / "packet"
    selection = script.prepare(source, manifest, output, models=script.MODELS)
    assert selection["case_bundle_sha256"] == digest(case_bundle(load_cases(output / "cases.json")))
    configs = [read(output / (m.replace(":", "-") + ".json")) for m in script.MODELS]
    assert configs[0]["model"].pop("model") != configs[1]["model"].pop("model")
    assert configs[0] == configs[1]
    assert configs[0]["qualification_policy"] == "strict_model_backend_v1"
    assert selection["proposed_requests_including_metadata"] == 102
    assert selection["proposed_metadata_requests"] == 2
    assert selection["proposed_total_output_reservation"] == 3276800
    for model in script.MODELS:
        preflight = read(output / (model.replace(":", "-") + ".preflight.json"))
        assert preflight["state"] == "ready" and preflight["within_cap"]
        assert preflight["planned_requests"] == 48
        assert preflight["reference_labels"] == {"SAT": 12, "UNSAT": 12}
    with pytest.raises(FileExistsError):
        script.prepare(source, manifest, output)
    assert source.read_bytes() == before


def test_selected_candidate_default_has_explicit_per_model_and_session_caps(pool, tmp_path):
    script = load_script("prepare_model_qualification")
    source = tmp_path / "source.json"
    write_new(source, case_bundle(pool))
    output = tmp_path / "candidate"
    selection = script.prepare(
        source, ROOT / "benchmarks/manifests/expanded-development-100-20260930.json", output
    )
    assert selection["selected_models"] == ["qwen3.8:27b"]
    assert selection["case_completions_per_model"] == selection["planned_case_completions"] == 48
    assert selection["proposed_capability_completions"] == 2
    assert selection["proposed_completion_calls_total"] == 50
    assert selection["proposed_metadata_requests"] == 1
    assert selection["proposed_requests_including_metadata"] == 51
    assert selection["proposed_total_output_reservation"] == 1638400
    cfg = read(output / "qwen3.8-27b.json")
    assert cfg["evidence"] == "live_development"
    assert cfg["qualification_policy"] == "strict_model_backend_v1"
    assert cfg["max_requests"] == 48
    assert cfg["max_requested_output_tokens"] == 1572864
    assert not (output / "qwen3.6-35b.json").exists()


@pytest.mark.parametrize("change", ["heldout", "duplicate", "missing_failure", "small_stratum", "missing_coupled"])
def test_incomplete_or_non_development_packet_rejected(pool, change):
    script = load_script("prepare_model_qualification")
    cases = list(pool)
    if change == "heldout":
        cases[0] = replace(cases[0], split="test")
    elif change == "duplicate":
        cases.append(cases[0])
    elif change == "missing_failure":
        cases = [c for c in cases if c.case_id != script.FAILURES[0]]
    elif change == "small_stratum":
        cases = [c for c in cases if c.problem.task_type != "repair" or c.expected_label != "SAT"]
    else:
        cases = [c for c in cases if c.sweep != "resource_chain"]
    with pytest.raises(ValueError):
        script.select_cases(cases)


def test_changed_source_rejected_before_outputs(pool, tmp_path):
    script = load_script("prepare_model_qualification")
    source = tmp_path / "source.json"
    write_new(source, case_bundle(reversed(pool)))
    with pytest.raises(ValueError, match="preserved expanded"):
        script.prepare(source, ROOT / "benchmarks/manifests/expanded-development-100-20260930.json", tmp_path / "output")
    assert not (tmp_path / "output").exists()
