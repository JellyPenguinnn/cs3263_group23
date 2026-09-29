"""Provider-owned types, independent of the pending scheduling schema."""

from dataclasses import dataclass, field
import math
from typing import Literal


@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str

    def __post_init__(self) -> None:
        if self.role not in ("system", "user", "assistant") or not isinstance(self.content, str):
            raise ValueError("Invalid message role or content")


@dataclass(frozen=True)
class ModelConfig:
    model: str
    max_tokens: int
    connect_timeout: float = 10.0
    read_timeout: float = 60.0
    max_attempts: int = 1
    retry_delay: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("An explicit model is required")
        if type(self.max_tokens) is not int or self.max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 3:
            raise ValueError("max_attempts must be between 1 and 3")
        for value in (self.connect_timeout, self.read_timeout, self.retry_delay):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("Timeouts and retry delay must be finite and positive")


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class Attempt:
    number: int
    elapsed_seconds: float
    http_status: int | None
    usage: Usage
    error: str | None = None
    outcome_uncertain: bool = False
    returned_model: str | None = None
    finish_reason: str | None = None


@dataclass(frozen=True)
class ModelResponse:
    content: str | None
    returned_model: str | None
    elapsed_seconds: float
    attempts: tuple[Attempt, ...]
    error: str | None = None
    finish_reason: str | None = None


@dataclass
class RequestBudget:
    """Serial session budget; reserves output capacity even for uncertain failures.

    This caps requests and requested completion tokens, not input/total tokens or
    currency. The runner must persist attempts and enforce its overall run budget.
    """

    max_requests: int
    max_completion_tokens: int
    requests_used: int = field(default=0, init=False)
    completion_tokens_reserved: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if any(type(v) is not int or v < 0 for v in (self.max_requests, self.max_completion_tokens)):
            raise ValueError("Budget limits must be nonnegative integers")

    def reserve(self, tokens: int) -> bool:
        if type(tokens) is not int or tokens < 0:
            raise ValueError("Reserved tokens must be a nonnegative integer")
        if (self.requests_used >= self.max_requests
                or self.completion_tokens_reserved + tokens > self.max_completion_tokens):
            return False
        self.requests_used += 1
        self.completion_tokens_reserved += tokens
        return True
