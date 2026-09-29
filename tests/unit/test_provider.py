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
