"""Versioned description of the actual SoCLaaS request, without message content."""

from .types import ModelConfig


BASE_URL = "https://soclaas-api.comp.nus.edu.sg/v1"


def execution_contract(config: ModelConfig) -> dict:
    return {
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
