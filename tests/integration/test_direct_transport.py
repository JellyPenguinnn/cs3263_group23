import json

import httpx
import pytest

from scheduling.cli import main
from scheduling.pipelines.direct import request_direct
from scheduling.providers import ModelConfig, RequestBudget, SoCLaaSProvider
from scheduling.providers import ModelResponse


@pytest.mark.parametrize("task_type", ["generation", "repair"])
def test_public_prompt_through_transport_to_parser(task_type):
    old = [{"activity_id": "A", "start_slot": 0}] if task_type == "repair" else None
    def handler(request):
        data = json.loads(request.content)
        public = json.loads(data["messages"][1]["content"])
        assert "gold" not in public and public["description"] == "A must start at slot 1."
        if old is not None:
            assert public["original_schedule"] == old
        return httpx.Response(200, json={"model": "canned", "choices": [{"message": {"content": '{"status":"SAT","schedule":[{"activity_id":"A","start_slot":1}]}'}, "finish_reason": "stop"}]})
    with SoCLaaSProvider(api_key="synthetic-test-key", budget=RequestBudget(1, 100), transport=httpx.MockTransport(handler)) as provider:
        result = request_direct("A must start at slot 1.", ModelConfig("canned", 100), task_type=task_type, required_activity_ids=["A"], original_schedule=old, provider_complete=provider.complete)
    assert result.status == "SAT" and result.parsed.schedule[0]["start_slot"] == 1
    assert len(result.response.attempts) == 1


def test_cli_offline_invalid_exit(tmp_path, capsys):
    response = tmp_path / "response.txt"
    response.write_text('{"status":"SAT","schedule":[]}', encoding="utf-8")
    assert main(["parse-direct", str(response), "--activity-id", "A"]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["declared_status"] == "SAT" and output["status"] == "INVALID_OUTPUT"


def test_offline_cli_requires_no_credentials(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("SOCLAAS_API_KEY", raising=False)
    text = tmp_path / "text.txt"
    response = tmp_path / "response.json"
    text.write_text("A starts at slot zero.")
    response.write_text('{"status":"SAT","schedule":[{"activity_id":"A","start_slot":0}]}')
    assert main(["direct-offline", "--text-file", str(text), "--response-file", str(response), "--activity-id", "A", "--task-type", "generation"]) == 0
    assert json.loads(capsys.readouterr().out)["evidence"] == "offline_canned_unvalidated"


def live_arguments(tmp_path):
    text = tmp_path / "text.txt"
    text.write_text("A starts at slot zero.")
    output = tmp_path / "result.json"
    return ["direct-live", "--text-file", str(text), "--activity-id", "A", "--task-type", "generation",
            "--model", "fake", "--max-tokens", "32", "--allow-live", "--output", str(output)], output


def fake_provider(monkeypatch, callback):
    class Fake:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def complete(self, messages, config):
            return callback(messages, config)
    monkeypatch.setattr(SoCLaaSProvider, "from_environment", lambda **kwargs: Fake())


def test_live_cli_saved_record_is_private_and_never_overwritten(tmp_path, monkeypatch, capsys):
    calls = []
    def callback(messages, config):
        calls.append(config)
        return ModelResponse('{"status":"UNKNOWN","schedule":null}', "fake", 0, (), finish_reason="stop")
    fake_provider(monkeypatch, callback)
    args, output = live_arguments(tmp_path)
    assert main(args) == 0
    record = json.loads(output.read_text())
    assert record["state"] == "completed" and record["result"]["status"] == "UNKNOWN"
    assert output.stat().st_mode & 0o777 == 0o600
    assert len(record["source_sha256"]) == 4
    assert main(args) == 2 and len(calls) == 1
    assert "output_exists_no_request_sent" in capsys.readouterr().out


def test_interrupted_call_leaves_visible_record(tmp_path, monkeypatch):
    def callback(*args):
        raise KeyboardInterrupt
    fake_provider(monkeypatch, callback)
    args, output = live_arguments(tmp_path)
    with pytest.raises(KeyboardInterrupt):
        main(args)
    assert json.loads(output.read_text())["state"] == "pending_or_interrupted"


def test_invalid_repair_never_calls_or_reserves_record(tmp_path, monkeypatch):
    fake_provider(monkeypatch, lambda *_: pytest.fail("Invalid repair must not call provider"))
    args, output = live_arguments(tmp_path)
    args[args.index("generation")] = "repair"
    assert main(args) == 2 and not output.exists()
