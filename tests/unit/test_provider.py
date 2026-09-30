import json

import httpx
import pytest

from scheduling.providers import Message, ModelConfig, RequestBudget, SoCLaaSProvider


def body(content="OK", **extra):
    return {"model": "test-backend", "choices": [{"message": {"content": content}, "finish_reason": "stop"}], **extra}


def call(handler, *, config=None, budget=None):
    with SoCLaaSProvider(api_key="test-only-secret", budget=budget or RequestBudget(3, 300),
                        transport=httpx.MockTransport(handler), sleep=lambda _: None) as provider:
        return provider.complete([Message("user", "synthetic")], config or ModelConfig("test-model", 100))


def test_request_and_response_contract():
    def handler(request):
        assert str(request.url) == "https://soclaas-api.comp.nus.edu.sg/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-only-secret"
        assert json.loads(request.content) == {"model": "test-model", "messages": [{"role": "user", "content": "synthetic"}], "max_tokens": 100, "stream": False}
        assert request.extensions["timeout"] == {"connect": 10, "read": 60, "write": 60, "pool": 60}
        return httpx.Response(200, json=body(usage={"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9}))
    result = call(handler)
    assert result.error is None and result.content == "OK" and result.returned_model == "test-backend"
    assert result.attempts[0].usage.total_tokens == 9


@pytest.mark.parametrize("raw", [None, {}, {"prompt_tokens": True, "completion_tokens": -1, "total_tokens": "9"}])
def test_missing_or_invalid_usage_is_not_zero(raw):
    result = call(lambda _: httpx.Response(200, json=body(usage=raw)))
    assert result.attempts[0].usage.prompt_tokens is None
    assert result.attempts[0].usage.completion_tokens is None
    assert result.attempts[0].usage.total_tokens is None


def test_zero_usage_is_preserved():
    result = call(lambda _: httpx.Response(200, json=body(usage={"total_tokens": 0})))
    assert result.attempts[0].usage.total_tokens == 0


@pytest.mark.parametrize("status", [400, 401, 403, 404, 302])
def test_permanent_errors_and_redirects_never_retry_or_leak(status):
    seen = []
    def handler(request):
        seen.append(request)
        return httpx.Response(status, text="test-only-secret private-provider-text", headers={"Location": "https://example.com"})
    result = call(handler, config=ModelConfig("test", 100, max_attempts=3))
    assert result.error == f"http_{status}" and len(seen) == 1
    assert "test-only-secret" not in repr(result) and "private-provider-text" not in repr(result)


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
def test_transient_retries_are_bounded_and_keep_attempts(status):
    responses = iter([httpx.Response(status, json={"usage": {"total_tokens": 5}}), httpx.Response(200, json=body())])
    result = call(lambda _: next(responses), config=ModelConfig("test", 100, max_attempts=2))
    assert result.error is None and len(result.attempts) == 2
    assert result.attempts[0].http_status == status and result.attempts[0].usage.total_tokens == 5
    assert result.attempts[1].usage.total_tokens is None


def test_budget_stops_retry_and_preserves_failure():
    budget = RequestBudget(1, 100)
    result = call(lambda _: httpx.Response(429), config=ModelConfig("test", 100, max_attempts=3), budget=budget)
    assert result.error == "request_budget_exhausted" and len(result.attempts) == 1
    assert result.attempts[0].error == "http_429" and budget.requests_used == 1


def test_budget_is_shared_across_calls_and_checks_tokens_before_sending():
    budget = RequestBudget(5, 100)
    first = call(lambda _: httpx.Response(200, json=body()), budget=budget)
    second = call(lambda _: pytest.fail("request exceeds cap"), budget=budget)
    assert first.error is None and second.error == "request_budget_exhausted"
    assert second.attempts == () and budget.requests_used == 1


@pytest.mark.parametrize("kind,uncertain,count", [(httpx.ReadTimeout, True, 1), (httpx.WriteError, True, 1), (httpx.ConnectTimeout, False, 2)])
def test_timeouts_account_for_uncertain_execution(kind, uncertain, count):
    def handler(request):
        raise kind("test-only-secret", request=request)
    result = call(handler, config=ModelConfig("test", 100, max_attempts=2))
    assert len(result.attempts) == count and result.attempts[0].outcome_uncertain is uncertain
    assert "test-only-secret" not in repr(result)


@pytest.mark.parametrize("data", [None, {}, [], {"choices": []}, body(content=None)])
def test_malformed_provider_response_is_not_retried(data):
    result = call(lambda _: httpx.Response(200, json=data), config=ModelConfig("test", 100, max_attempts=3))
    assert result.error == "invalid_provider_response" and len(result.attempts) == 1


def test_truncated_response_and_usage_retained():
    data = body('{"status":')
    data["choices"][0]["finish_reason"] = "length"
    data["usage"] = {"completion_tokens": 100}
    result = call(lambda _: httpx.Response(200, json=data))
    assert result.error == "incomplete_completion" and result.content == '{"status":'
    assert result.attempts[0].usage.completion_tokens == 100


def test_no_invented_returned_model():
    data = body()
    del data["model"]
    assert call(lambda _: httpx.Response(200, json=data)).returned_model is None


@pytest.mark.parametrize("kwargs", [{"max_tokens": True}, {"max_tokens": 0}, {"read_timeout": float("nan")}, {"connect_timeout": 0}, {"max_attempts": 4}, {"model": ""}])
def test_invalid_config(kwargs):
    values = {"model": "test", "max_tokens": 32, **kwargs}
    with pytest.raises(ValueError):
        ModelConfig(**values)


def test_model_listing_and_completion_share_budget():
    def handler(request):
        return httpx.Response(200, json={"data": [{"id": "test"}]} if request.method == "GET" else body())
    budget = RequestBudget(2, 32)
    with SoCLaaSProvider(api_key="test", budget=budget, transport=httpx.MockTransport(handler)) as provider:
        assert provider.list_models() == ("test",)
        assert provider.complete([Message("user", "OK")], ModelConfig("test", 32)).error is None
    assert budget.requests_used == 2 and budget.completion_tokens_reserved == 32


def test_reject_unapproved_endpoint():
    with pytest.raises(ValueError, match="approved SoCLaaS"):
        SoCLaaSProvider(api_key="test", budget=RequestBudget(1, 32), base_url="https://example.com")


@pytest.mark.parametrize("payload", [b"not-json", b"\xff", b"[" * 1200 + b"]" * 1200])
def test_model_listing_rejects_bad_json_with_safe_category_and_spent_budget(payload):
    budget = RequestBudget(2, 32)
    with SoCLaaSProvider(api_key="test", budget=budget,
                        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=payload))) as provider:
        with pytest.raises(ValueError, match="^invalid_model_listing$"):
            provider.list_models()
    assert budget.requests_used == 1


def test_deep_provider_envelope_is_recorded_as_failure_without_retry():
    result = call(lambda _: httpx.Response(200, content=b"[" * 1200 + b"]" * 1200),
                  config=ModelConfig("test", 32, max_attempts=3))
    assert result.error == "invalid_provider_response"
    assert len(result.attempts) == 1 and result.attempts[0].http_status == 200
    assert result.attempts[0].usage.total_tokens is None


@pytest.mark.parametrize("reasoning_field", ["reasoning_content", "reasoning"])
def test_reasoning_side_channel_is_never_used_or_recorded_as_final_content(reasoning_field):
    data = body('{"status":"UNKNOWN","schedule":null}')
    data['choices'][0]['message'][reasoning_field] = 'private-reasoning-sentinel'
    result = call(lambda _: httpx.Response(200, json=data))
    assert result.content == '{"status":"UNKNOWN","schedule":null}'
    assert result.error is None
    assert 'private-reasoning-sentinel' not in repr(result)


@pytest.mark.parametrize("content", [None, [{"type": "text", "text": "OK"}]])
def test_reasoning_only_or_content_parts_are_not_silently_coerced(content):
    data = body(content)
    data['choices'][0]['message']['reasoning_content'] = 'private-reasoning-sentinel'
    result = call(lambda _: httpx.Response(200, json=data))
    assert result.error == 'invalid_provider_response'
    assert result.content is None and len(result.attempts) == 1
    assert 'private-reasoning-sentinel' not in repr(result)


def test_mixed_reasoning_in_final_field_is_retained_not_regex_repaired():
    from scheduling.pipelines.direct import parse_direct_output
    raw = '<think>synthetic explanation</think>{"status":"UNSAT","schedule":null}'
    result = call(lambda _: httpx.Response(200, json=body(raw)))
    assert result.content == raw and result.error is None
    assert parse_direct_output(result.content, ['A']).status == 'INVALID_OUTPUT'


@pytest.mark.parametrize("finish", ['length', 'content_filter', 'tool_calls'])
def test_non_stop_finish_keeps_response_and_accounting_without_retry(finish):
    data = body('{"status":"UNKNOWN","schedule":null}', usage={"total_tokens": 17})
    data['choices'][0]['finish_reason'] = finish
    result = call(lambda _: httpx.Response(200, json=data), config=ModelConfig('test', 100, max_attempts=3))
    assert result.error == 'incomplete_completion' and result.finish_reason == finish
    assert len(result.attempts) == 1 and result.attempts[0].usage.total_tokens == 17
    assert result.content == data['choices'][0]['message']['content']


def test_unverified_inference_options_are_rejected_not_ignored():
    with pytest.raises(TypeError):
        ModelConfig('test', 100, temperature=0)


def test_execution_metadata_matches_wire_settings_and_retains_only_safe_backend_fields():
    from scheduling.providers.execution import execution_contract
    config = ModelConfig('test-model', 32768, connect_timeout=30, read_timeout=900)
    def handler(request):
        payload = json.loads(request.content)
        contract = execution_contract(config)
        assert {k: v for k, v in payload.items() if k != 'messages'} == contract['configured_body']
        assert request.extensions['timeout'] == contract['timeouts']
        data = body(usage={'completion_tokens': 100, 'completion_tokens_details': {'reasoning_tokens': 83}}, system_fingerprint='fp_test_revision')
        data['choices'][0]['message']['reasoning_content'] = 'private-reasoning-sentinel'
        return httpx.Response(200, json=data)
    result = call(handler, config=config, budget=RequestBudget(1, 32768))
    metadata = result.attempts[0].execution
    assert metadata.contract == execution_contract(config)
    assert metadata.contract['effective_omitted_values'] == 'server_defaults_unavailable'
    assert metadata.contract['weight_revision'] is None
    assert metadata.system_fingerprint == 'fp_test_revision'
    assert metadata.reported_reasoning_tokens == 83 and metadata.reasoning_field_present
    assert 'private-reasoning-sentinel' not in repr(result)


@pytest.mark.parametrize('fingerprint', [None, 42, '', 'test-only-secret', 'bad fingerprint'])
def test_unavailable_or_unsafe_fingerprint_not_invented_or_exposed(fingerprint):
    result = call(lambda _: httpx.Response(200, json=body(system_fingerprint=fingerprint)))
    assert result.attempts[0].execution.system_fingerprint is None
    assert result.attempts[0].execution.reported_reasoning_tokens is None


@pytest.mark.parametrize('count', [None, True, -1, '3'])
def test_malformed_reasoning_count_remains_unavailable(count):
    data = body(usage={'completion_tokens_details': {'reasoning_tokens': count}})
    result = call(lambda _: httpx.Response(200, json=data))
    assert result.attempts[0].execution.reported_reasoning_tokens is None
