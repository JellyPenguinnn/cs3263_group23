"""Direct prompt/response boundary, without gold data or a duplicate shared schema.

DirectParse and DirectAttempt are component records, NOT the canonical Schedule,
NaturalLanguageView or PipelineResult. run_direct adapts them to the canonical
schema supplied by its owner. Structural SAT here is an unvalidated model claim.
"""

from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sysconfig
from typing import Literal

from scheduling.providers import Message, ModelConfig, ModelResponse


@dataclass(frozen=True)
class DirectParse:
    declared_status: str | None
    status: Literal["SAT", "UNSAT", "UNKNOWN", "INVALID_OUTPUT"]
    schedule: list[dict[str, object]] | None
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class DirectAttempt:
    parsed: DirectParse | None
    response: ModelResponse
    prompt_sha256: str
    config_sha256: str
    status: str


def _ids(required_activity_ids: Sequence[str]) -> tuple[str, ...]:
    if isinstance(required_activity_ids, str):
        raise ValueError("Activity IDs must be a sequence, not a string")
    ids = tuple(required_activity_ids)
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Public activity IDs must be nonempty unique strings")
    return ids


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("nonfinite_json_number")


def parse_direct_output(content: str, required_activity_ids: Sequence[str]) -> DirectParse:
    """Validate only the wire format and public task coverage; never repair output."""
    ids = _ids(required_activity_ids)
    try:
        data = json.loads(content, object_pairs_hook=_object, parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError):
        return DirectParse(None, "INVALID_OUTPUT", None, ("invalid_json",))
    declared = data.get("status") if isinstance(data, dict) else None
    declared = declared if isinstance(declared, str) else None
    if not isinstance(data, dict) or set(data) != {"status", "schedule"}:
        return DirectParse(declared, "INVALID_OUTPUT", None, ("invalid_envelope",))
    if declared not in ("SAT", "UNSAT", "UNKNOWN"):
        return DirectParse(declared, "INVALID_OUTPUT", None, ("invalid_declared_status",))
    schedule = data["schedule"]
    if declared != "SAT":
        if schedule is not None:
            return DirectParse(declared, "INVALID_OUTPUT", None, ("schedule_with_non_sat",))
        return DirectParse(declared, declared, None)
    if not isinstance(schedule, list):
        return DirectParse(declared, "INVALID_OUTPUT", None, ("missing_schedule",))
    seen = []
    for row in schedule:
        if (not isinstance(row, dict) or set(row) != {"activity_id", "start_slot"}
                or not isinstance(row["activity_id"], str)
                or type(row["start_slot"]) is not int or row["start_slot"] < 0):
            return DirectParse(declared, "INVALID_OUTPUT", None, ("invalid_schedule_entry",))
        seen.append(row["activity_id"])
    diagnostics = []
    if len(set(seen)) != len(seen):
        diagnostics.append("duplicate_activities")
    if set(ids) - set(seen):
        diagnostics.append("missing_activities")
    if set(seen) - set(ids):
        diagnostics.append("invented_activities")
    if diagnostics:
        return DirectParse(declared, "INVALID_OUTPUT", None, tuple(diagnostics))
    return DirectParse(declared, "SAT", sorted(schedule, key=lambda row: row["activity_id"]))


def build_messages(text: str, *, task_type: str, required_activity_ids: Sequence[str],
                   original_schedule: list[dict[str, object]] | None = None,
                   prompt_path: Path | None = None) -> tuple[Message, ...]:
    ids = _ids(required_activity_ids)
    if task_type not in ("generation", "repair") or not isinstance(text, str) or not text.strip():
        raise ValueError("A generation/repair task and public description are required")
    if task_type == "repair":
        original = parse_direct_output(json.dumps({"status": "SAT", "schedule": original_schedule}), ids)
        if original.status != "SAT":
            raise ValueError("Repair requires a complete structural original schedule")
    elif original_schedule is not None:
        raise ValueError("Generation must not receive an original schedule")
    if prompt_path is None:
        # Installed wheels and editable checkouts use the same tracked prompt files.
        root = Path(sysconfig.get_path("data")) / "share/cs3263-scheduling/prompts/direct"
        checkout = Path(__file__).resolve().parents[3]
        prompt_path = checkout / "prompts/direct" / f"{task_type}.txt"
        if not (checkout / "pyproject.toml").is_file() or not prompt_path.is_file():
            prompt_path = root / f"{task_type}.txt"
    instructions = prompt_path.read_text(encoding="utf-8")
    public_input = {"description": text, "activity_ids": ids}
    if task_type == "repair":
        public_input["original_schedule"] = original_schedule
    return (Message("system", instructions), Message("user", json.dumps(public_input, sort_keys=True)))


def request_direct(text: str, model_config: ModelConfig, *, task_type: str,
                   required_activity_ids: Sequence[str],
                   provider_complete: Callable[[Sequence[Message], ModelConfig], ModelResponse],
                   original_schedule: list[dict[str, object]] | None = None) -> DirectAttempt:
    messages = build_messages(text, task_type=task_type, required_activity_ids=required_activity_ids,
                              original_schedule=original_schedule)
    prompt_hash = hashlib.sha256(json.dumps([asdict(m) for m in messages], sort_keys=True).encode()).hexdigest()
    config_hash = hashlib.sha256(json.dumps(asdict(model_config), sort_keys=True).encode()).hexdigest()
    response = provider_complete(messages, model_config)
    if response.error:
        status = "INVALID_OUTPUT" if response.error == "incomplete_completion" else "ERROR"
        return DirectAttempt(None, response, prompt_hash, config_hash, status)
    parsed = parse_direct_output(response.content, required_activity_ids)
    return DirectAttempt(parsed, response, prompt_hash, config_hash, parsed.status)


def run_direct(nl_view, model_config: ModelConfig, *, provider_complete=None):
    """Canonical adapter; one existing direct call with public inputs only."""
    import time
    from scheduling.providers import complete
    from scheduling.schema import NaturalLanguageView, PipelineResult, Schedule
    if not isinstance(nl_view, NaturalLanguageView):
        raise TypeError("Direct pipeline requires the canonical public view")
    started = time.monotonic()
    attempt = request_direct(nl_view.text, model_config, task_type=nl_view.task_type,
                             required_activity_ids=nl_view.activity_ids,
                             original_schedule=nl_view.original_schedule.to_list() if nl_view.original_schedule else None,
                             provider_complete=provider_complete if provider_complete is not None else complete)
    parsed = attempt.parsed
    return PipelineResult(nl_view.instance_id, nl_view.variant_id, "direct", attempt.status,
                          schedule=Schedule.from_list(parsed.schedule) if parsed and parsed.schedule is not None else None,
                          declared_status=parsed.declared_status if parsed else None,
                          diagnostics=parsed.diagnostics if parsed else (attempt.response.error,),
                          timings=(("total_seconds", time.monotonic()-started),),
                          usage=tuple(a.usage for a in attempt.response.attempts), model_response=attempt.response,
                          prompt_sha256=attempt.prompt_sha256, config_sha256=attempt.config_sha256)
