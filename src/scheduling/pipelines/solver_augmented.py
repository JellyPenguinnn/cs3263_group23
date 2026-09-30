"""One public-language extraction call followed by a fixed CP-SAT compiler."""

from collections.abc import Callable, Sequence
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import sysconfig
import time

from scheduling.providers import Message, ModelConfig, ModelResponse, complete
from scheduling.schema import NaturalLanguageView, PipelineResult, ProblemSpec, RepairContext, SchemaError
from scheduling.solver import SolverLimits, solve


# Request-local metadata only; evaluator IDs may encode labels or selection strata.
PUBLIC_REQUEST_ID = "request"


def build_extraction_messages(view: NaturalLanguageView, *, prompt_path: Path | None = None) -> tuple[Message, ...]:
    if not isinstance(view, NaturalLanguageView):
        raise TypeError("Extraction requires a canonical public NaturalLanguageView")
    if prompt_path is None:
        checkout = Path(__file__).resolve().parents[3]
        prompt_path = checkout / "prompts/extraction/specification.txt"
        if not (checkout / "pyproject.toml").is_file() or not prompt_path.is_file():
            prompt_path = Path(sysconfig.get_path("data")) / "share/cs3263-scheduling/prompts/extraction/specification.txt"
    payload = {"instance_id": PUBLIC_REQUEST_ID,
               "task_type": view.task_type, "description": view.text, "activity_ids": view.activity_ids}
    if view.original_schedule is not None:
        payload["original_schedule"] = view.original_schedule.to_list()
    return (Message("system", prompt_path.read_text(encoding="utf-8")),
            Message("user", json.dumps(payload, sort_keys=True)))


def run_solver_augmented(nl_view: NaturalLanguageView, model_config: ModelConfig,
                         solver_limits: SolverLimits, *,
                         provider_complete: Callable[[Sequence[Message], ModelConfig], ModelResponse] = complete) -> PipelineResult:
    started = time.monotonic()
    messages = build_extraction_messages(nl_view)
    prompt_hash = hashlib.sha256(json.dumps([asdict(m) for m in messages], sort_keys=True).encode()).hexdigest()
    config_hash = hashlib.sha256(json.dumps({"model": asdict(model_config), "solver": asdict(solver_limits)}, sort_keys=True).encode()).hexdigest()
    response = provider_complete(messages, model_config)
    base = {"instance_id": nl_view.instance_id, "variant_id": nl_view.variant_id,
            "approach": "solver_augmented", "model_response": response,
            "usage": tuple(attempt.usage for attempt in response.attempts),
            "prompt_sha256": prompt_hash, "config_sha256": config_hash}
    if response.error:
        status = "INVALID_OUTPUT" if response.error == "incomplete_completion" else "ERROR"
        return PipelineResult(**base, status=status, diagnostics=(response.error,),
                              timings=(("total_seconds", time.monotonic() - started),))
    try:
        extracted = ProblemSpec.from_json(response.content)
        if extracted.instance_id != PUBLIC_REQUEST_ID or extracted.task_type != nl_view.task_type:
            raise SchemaError("Extracted metadata differs from public request")
        if {a.id for a in extracted.activities} != set(nl_view.activity_ids):
            raise SchemaError("Extracted activity set differs from public labels")
    except SchemaError as error:
        return PipelineResult(**base, status="INVALID_OUTPUT", diagnostics=(f"{error.detail.path}: {error}",), schema_diagnostics=(error.detail,),
                              timings=(("total_seconds", time.monotonic() - started),))
    # Restore bookkeeping only after validating the wire ID. Raw content is retained;
    # no scheduling field is normalized or repaired using evaluator information.
    extracted = replace(extracted, instance_id=nl_view.instance_id)
    extracted_at = time.monotonic()
    context = RepairContext(nl_view.original_schedule) if nl_view.task_type == "repair" else None
    try:
        result = solve(extracted, solver_limits, context)
    except SchemaError as error:
        return PipelineResult(**base, status="INVALID_OUTPUT", extracted_spec=extracted,
                              diagnostics=(f"{error.detail.path}: {error}",), schema_diagnostics=(error.detail,), timings=(("total_seconds", time.monotonic() - started),))
    status = {"OPTIMAL": "SAT", "FEASIBLE": "SAT", "INFEASIBLE": "UNSAT",
              "UNKNOWN": "UNKNOWN", "MODEL_INVALID": "ERROR"}[result.status]
    return PipelineResult(**base, status=status, schedule=result.schedule, extracted_spec=extracted,
                          solve_result=result, diagnostics=result.diagnostics,
                          timings=(("extraction_seconds", extracted_at - started),
                                   ("solver_seconds", result.elapsed_seconds),
                                   ("total_seconds", time.monotonic() - started)))
