"""Serial SoCLaaS transport with explicit budgets and safe error categories."""

from dataclasses import asdict
import os
import time
from collections.abc import Callable, Sequence

import httpx

from .types import Attempt, Message, ModelConfig, ModelResponse, RequestBudget, Usage

BASE_URL = "https://soclaas-api.comp.nus.edu.sg/v1"
TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


def _usage(data: object) -> Usage:
    raw = data.get("usage") if isinstance(data, dict) else None
    if not isinstance(raw, dict):
        return Usage()
    values = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = raw.get(key)
        values[key] = value if type(value) is int and value >= 0 else None
    return Usage(**values)


class SoCLaaSProvider:
    def __init__(self, *, api_key: str, budget: RequestBudget,
                 base_url: str = BASE_URL, transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        if not api_key.strip() or api_key == "replace_with_your_own_key":
            raise ValueError("Configure an authorized SOCLAAS_API_KEY locally")
        if any(c.isspace() for c in api_key):
            raise ValueError("Invalid credential format")
        if base_url.rstrip("/") != BASE_URL:
            raise ValueError("Development inference must use the approved SoCLaaS endpoint")
        self.budget = budget
        self._sleep = sleep
        self._client = httpx.Client(
            base_url=BASE_URL + "/", headers={"Authorization": "Bearer " + api_key},
            transport=transport, follow_redirects=False, trust_env=False,
        )

    @classmethod
    def from_environment(cls, *, budget: RequestBudget) -> "SoCLaaSProvider":
        return cls(api_key=os.environ.get("SOCLAAS_API_KEY", ""), budget=budget,
                   base_url=os.environ.get("SOCLAAS_BASE_URL", BASE_URL))

    def __enter__(self) -> "SoCLaaSProvider":
        return self

    def __exit__(self, *args: object) -> None:
        self._client.close()

    def list_models(self) -> tuple[str, ...]:
        """One budgeted request, no retries; never exposes provider error text."""
        if not self.budget.reserve(0):
            raise ValueError("request_budget_exhausted")
        try:
            response = self._client.get("models", timeout=httpx.Timeout(30, connect=10))
            if response.status_code != 200:
                raise ValueError(f"model_listing_http_{response.status_code}")
            data = response.json()
            rows = data["data"]
            if not isinstance(rows, list) or not rows:
                raise ValueError("invalid_model_listing")
            ids = [row["id"] for row in rows]
            if any(not isinstance(value, str) or not value for value in ids):
                raise ValueError("invalid_model_listing")
            return tuple(ids)
        except httpx.RequestError:
            raise ValueError("model_listing_transport_error") from None
        except (KeyError, TypeError):
            raise ValueError("invalid_model_listing") from None

    def complete(self, messages: Sequence[Message], model_config: ModelConfig) -> ModelResponse:
        if not messages or any(not isinstance(m, Message) for m in messages):
            raise ValueError("At least one typed message is required")
        config = model_config
        attempts: list[Attempt] = []
        start = time.monotonic()
        content = model = finish = error = None
        timeout = httpx.Timeout(config.read_timeout, connect=config.connect_timeout)
        for number in range(1, config.max_attempts + 1):
            if not self.budget.reserve(config.max_tokens):
                error = "request_budget_exhausted"
                break
            tick = time.monotonic()
            status = None
            usage = Usage()
            retry = uncertain = False
            content = model = finish = error = None
            try:
                response = self._client.post("chat/completions", timeout=timeout, json={
                    "model": config.model, "messages": [asdict(m) for m in messages],
                    "max_tokens": config.max_tokens, "stream": False,
                })
                status = response.status_code
                try:
                    data = response.json()
                except ValueError:
                    data = None
                usage = _usage(data)
                if status != 200:
                    error = f"http_{status}"
                    retry = status in TRANSIENT_STATUS
                    uncertain = status in {408, 500, 502, 503, 504}
                else:
                    if isinstance(data, dict):
                        returned = data.get("model")
                        model = returned if isinstance(returned, str) and returned else None
                    try:
                        choices = data["choices"]
                        if not isinstance(choices, list) or len(choices) != 1:
                            raise ValueError
                        content = choices[0]["message"]["content"]
                        finish = choices[0]["finish_reason"]
                        if not isinstance(content, str) or not isinstance(finish, str):
                            raise ValueError
                    except (KeyError, IndexError, TypeError, ValueError):
                        content = content if isinstance(content, str) else None
                        finish = finish if isinstance(finish, str) else None
                        error = "invalid_provider_response"
                    if error is None and finish != "stop":
                        error = "incomplete_completion"
            except httpx.RequestError as exc:
                error = "timeout" if isinstance(exc, httpx.TimeoutException) else "transport_error"
                uncertain = not isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout))
                # A read/write failure may already have consumed quota. Never retry it silently.
                retry = not uncertain
            attempts.append(Attempt(number, time.monotonic() - tick, status, usage,
                                    error, uncertain, model, finish))
            if not retry or number == config.max_attempts:
                break
            self._sleep(min(config.retry_delay * 2 ** (number - 1), 10.0))
        return ModelResponse(content, model, time.monotonic() - start, tuple(attempts), error, finish)


def complete(messages: Sequence[Message], model_config: ModelConfig, *,
             budget: RequestBudget | None = None) -> ModelResponse:
    """Shared convenience interface; default permits exactly one request.

    Both pipelines can inject an object's complete method for canned responses.
    Batch callers must share an explicit budget and persist returned attempts.
    """
    if budget is None:
        budget = RequestBudget(1, model_config.max_tokens)
    with SoCLaaSProvider.from_environment(budget=budget) as provider:
        return provider.complete(messages, model_config)
