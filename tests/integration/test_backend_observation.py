"""Explicit development-only backend observation never weakens model identity."""

from dataclasses import replace

import pytest

from scheduling.evaluation.qualification import capability_issue
from scheduling.evaluation.runner import OBSERVE_BACKEND_POLICY, baseline_fingerprints, run_batch
from tests.integration.test_evaluation import canned
from tests.integration.test_strict_qualification import strict_setup, response


def observed_setup():
    cases, cfg = strict_setup()
    return cases, replace(cfg, qualification_policy=OBSERVE_BACKEND_POLICY,
                          qualification_baseline={"system_fingerprints": ["a", "b"],
                                                  "capability_sha256": ["0" * 64, "1" * 64]})


def test_observed_run_retains_backend_changes_and_resumes_without_new_calls(tmp_path):
    cases, cfg = observed_setup()
    outputs = iter(canned(cases, cfg).values())
    calls = []

    def callback(*_):
        fingerprint = ("a", "b", None, "new-backend")[len(calls)]
        calls.append(fingerprint)
        return response(cfg, next(outputs), model=cfg.model.model, fingerprint=fingerprint)

    assert run_batch(cases, tmp_path, cfg, provider_complete=callback)["completed"] == 4
    no_call = lambda *_: pytest.fail("No duplicate request on resume")
    assert run_batch(cases, tmp_path, cfg, provider_complete=no_call)["completed"] == 4
    assert len(calls) == 4
    assert baseline_fingerprints(cfg) == {"a", "b"}
    with pytest.raises(ValueError, match="configuration/source/input changed"):
        run_batch(cases, tmp_path, replace(cfg, qualification_policy=None, qualification_baseline=None),
                  provider_complete=no_call)


@pytest.mark.parametrize("model", [None, "other-model"])
def test_observation_stops_wrong_model_even_with_backend_variation(tmp_path, model):
    cases, cfg = observed_setup()
    outputs = iter(canned(cases, cfg).values())
    calls = []

    def callback(*_):
        calls.append(1)
        return response(cfg, next(outputs), model=model, fingerprint="different")

    result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
    assert result["stop_reason"] == "returned_model_mismatch" and len(calls) == 1


def test_observation_capabilities_accumulate_fingerprints_but_reject_wrong_model():
    _, cfg = observed_setup()
    fingerprints = set()
    for fp in ("a", "b", None):
        assert capability_issue(response(cfg, '{"ok":true}', model=cfg.model.model, fingerprint=fp),
                                cfg, fingerprints) is None
    assert fingerprints == {"a", "b", None}
    assert capability_issue(response(cfg, '{"ok":true}', model="other", fingerprint="c"),
                            cfg, fingerprints) == "returned_model_mismatch"


@pytest.mark.parametrize("mode", ["offline_canned", "offline_frozen", "live_frozen"])
def test_observation_cannot_be_used_as_frozen_or_offline_evidence(mode):
    _, cfg = observed_setup()
    with pytest.raises(ValueError, match="Qualification policy"):
        replace(cfg, evidence=mode, freeze=None if mode == "offline_canned" else {})


@pytest.mark.parametrize("values", [[], ["a", "a"], ["a", "b", "c"], ["bad value"], [["nested"]], "a"])
def test_invalid_observation_baselines_are_rejected(values):
    _, cfg = observed_setup()
    with pytest.raises(ValueError, match="baseline"):
        replace(cfg, qualification_baseline={"system_fingerprints": values,
                                            "capability_sha256": ["0" * 64, "1" * 64]})
