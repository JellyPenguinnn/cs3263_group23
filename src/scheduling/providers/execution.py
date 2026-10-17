"""Versioned description of the actual SoCLaaS request, without message content."""

from .types import ModelConfig


BASE_URL = "https://soclaas-api.comp.nus.edu.sg/v1"


def expected_response_model(requested_model: str) -> str:
    # SoCLaaS exposes this route alias but reports its canonical name in replies.
    # Pin the observed identity; a future remapping must not silently pass.
    return {"x-test-1": "glm-5.3-flash"}.get(requested_model, requested_model)


def execution_contract(config: ModelConfig) -> dict:
    contract = {
        "format_version": "1.0",
        "provider": "soclaas",
        "endpoint": BASE_URL + "/chat/completions",
        "configured_body": {"model": config.model, "max_tokens": config.max_tokens, "stream": False},
        "timeouts": {"connect": config.connect_timeout, "read": config.read_timeout,
                     "write": config.read_timeout, "pool": config.read_timeout},
        "max_attempts": config.max_attempts,
        "retry_delay": config.retry_delay,
        "omitted_controls": ["temperature", "top_p", "seed", "reasoning_effort", "response_format"],
        "effective_omitted_values": "server_defaults_unavailable",
        "final_content_field": "choices[0].message.content",
        "weight_revision": None,
        "output_limit_semantics": "max_tokens_requested; hosted_reasoning_budget_semantics_unverified",
    }
    expected = expected_response_model(config.model)
    if expected != config.model:
        contract["model_identity"] = {
            "requested_alias": config.model,
            "required_returned_model": expected,
            "policy": "explicit_alias_pin_v1",
        }
    return contract
