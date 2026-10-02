"""Versioned handling of task-level provider failures, with no request retries."""

from dataclasses import dataclass
import time


CONTINUE_TRANSIENT_POLICY = "continue_transient_v1"
TRANSIENT_FAILURES = frozenset({
    "timeout", "transport_error", "http_408", "http_500", "http_502",
    "http_503", "http_504",
})
COOLDOWN_SECONDS = 30


@dataclass
class FailureState:
    """Carry a pending cooldown across blocks; each failed attempt remains final."""

    policy: str | None
    cooldown_pending: bool = False

    def observe(self, reason):
        recoverable = (
            self.policy == CONTINUE_TRANSIENT_POLICY and reason in TRANSIENT_FAILURES
        )
        self.cooldown_pending = recoverable
        return None if recoverable else reason

    def before_request(self):
        if self.cooldown_pending:
            time.sleep(COOLDOWN_SECONDS)
            self.cooldown_pending = False
