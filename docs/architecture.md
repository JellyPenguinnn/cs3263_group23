# Architecture and implementation

The system compares direct LLM scheduling with LLM specification extraction followed by a fixed OR-Tools CP-SAT compiler. Controlled generation is the core; minimum-disruption repair is an implemented extension. The [report](submission-report.md) explains the scientific question and findings; [usage](usage.md) covers commands and [the study protocol](studies/diverse-generation.md) defines the latest evaluation.

## Components and boundaries

| Component | Implementation | Responsibility |
| --- | --- | --- |
| Canonical data | [`schema.py`](../src/scheduling/schema.py) | Typed problem, activity, constraint, schedule, repair context and result contracts |
| Public request | [`evaluation/cases.py`](../src/scheduling/evaluation/cases.py), [`evaluation/benchmark.py`](../src/scheduling/evaluation/benchmark.py), [`prompts/`](../prompts/) | Natural-language view and public output/schema instructions; evaluator gold stays private to evaluation |
| Direct method A | [`pipelines/direct.py`](../src/scheduling/pipelines/direct.py) | One model call; strict parsing of a proposed schedule or UNSAT prediction |
| Solver-assisted method B | [`pipelines/solver_augmented.py`](../src/scheduling/pipelines/solver_augmented.py) | One extraction call; schema validation; fixed compilation and solving |
| Shared provider | [`providers/soclaas.py`](../src/scheduling/providers/soclaas.py), [`providers/execution.py`](../src/scheduling/providers/execution.py) | TLS, request budget, response identity, usage, timings and sanitized errors |
| Formal reasoning | [`solver.py`](../src/scheduling/solver.py), [`domain_analysis.py`](../src/scheduling/domain_analysis.py), [`proof_bounds.py`](../src/scheduling/proof_bounds.py) | CP-SAT constraints, sound domain preprocessing and bounded proof interpretation |
| Independent validation | [`validation.py`](../src/scheduling/validation.py), [`objectives.py`](../src/scheduling/objectives.py) | Arithmetic checks against gold; objective recomputation without invoking CP-SAT |
| Extraction and explanation | [`extraction_diagnostics.py`](../src/scheduling/extraction_diagnostics.py), [`explanations.py`](../src/scheduling/explanations.py) | Structural/semantic diagnostics and explanations bound to saved input/results |
| Evaluation | [`evaluation/runner.py`](../src/scheduling/evaluation/runner.py), [`scoring.py`](../src/scheduling/evaluation/scoring.py), [`study.py`](../src/scheduling/evaluation/study.py) | Reservations, immutable attempts, failure-inclusive scoring, paired analysis and replay |
| Operations | [`evaluation/`](../evaluation/) | Dataset/campaign preparation, supervision, continuation, analysis and offline demonstrations |
| Dashboard | [`dashboard/`](../src/scheduling/dashboard/) | Read-only views of recorded progress, schedules, outcomes and provenance |

Both methods receive equivalent public task information. They do not receive gold constraints, hidden feasibility labels, reference solutions, evaluation IDs or human-review metadata. Gold specifications support independent validation; the reference optimizer uses the same formal compiler, a limitation disclosed in the report. Model-generated code is never executed.

## Scheduling contract

- Time uses integer slots and half-open intervals `[start, start + duration)`. Current experiments use a single day, 30-minute slots, fixed durations and fixed participant/resource assignments.
- An activity must fit completely inside its permitted windows. All required participants and resources must be available and non-overlapping.
- Supported hard constraints include fixed starts, releases, deadlines and precedence. Soft preferences penalize starts outside preferred windows; they are not consecutive-meeting or weekly-clustering objectives.
- Generation minimizes weighted preference penalties after satisfying hard constraints.
- Repair uses stable activity IDs and the same original schedule for both methods. It minimizes moved activities, total absolute start shift, then preference penalty, lexicographically. The original schedule is checked against the original problem; repaired schedules are checked against the updated problem.
- Lexicographic stages share the configured solver budget. An earlier objective is fixed only when its optimum is proved; later gaps are meaningful only when earlier objectives match the proven reference.

The core interfaces are `solve(spec, limits, repair_context=None)`, `validate_schedule(gold_spec, schedule, repair_context=None)`, `run_direct(...)`, `run_solver_augmented(...)` and `evaluate(...)`. See their implementations above for exact typed signatures. Provider injection supports offline canned responses without API access.

## Status and evidence semantics

A pipeline returns `SAT`, `UNSAT`, `UNKNOWN`, `INVALID_OUTPUT` or `ERROR`; solver-native statuses remain separate. A direct UNSAT answer is a prediction. `FEASIBLE` is not `OPTIMAL`, and a timeout or `UNKNOWN` is not proof of infeasibility. Solver conclusions concern the extracted specification and do not establish that extraction preserved the request.

Schema validity, extraction agreement, gold feasibility, conditional objective quality and operational reliability are separate measurements. Every failed attempt remains in primary denominators. Missing token usage stays unknown. Timings must retain recorded concurrency/service/OS distinctions; the current study has no fully matched cross-model timing subset.

Authored case bundles use version 2.0 while the canonical problem schema remains 1.0. Legacy bundles remain supported with their original identities. Missing authored variants fail preflight instead of falling back to generated text. The same version-aware loader serves execution, replay, dashboard and explanation paths.

## Execution and preservation

Preparation binds inputs, prompts, configuration, source and runtime before inference. Reservations are recorded before requests; completed records and uncertain pending reservations are distinct. Continuation reuses saved attempts rather than reissuing them. Repeated concurrency reductions preserve each previous phase separately. Qualification and exact-model checks remain enforced: the GLM request alias `x-test-1` must return `glm-5.3-flash`.

The completed studies used one call per method, no retries and no verifier-feedback correction. Further live work requires a separately agreed model, protocol and budget; recorded failures must not be silently retried or removed. The development transient-failure policy records eligible timeouts/service failures and moves to the next distinct attempt, while fatal identity, authentication, integrity and budget errors stop execution.

Independent workers, heartbeats and OS locks distinguish active execution from stale files. A local process can still be interrupted by sleep, logout or reboot. See [usage](usage.md) for operational details and [evidence](evidence.md) for immutable archives, exact-source replay and safe fresh-output reproduction. Credentials and private reports remain ignored local files.

## Verification and scope

The [repository audit](process/repository-audit.md) records detailed source review, regression coverage and installed end-to-end checks. The scientific runtime uses `requirements.lock`; report tooling uses the separate `requirements-docs.txt`. Reinstall after source changes before checking the noneditable package. Future campaigns require newly prepared source-bound packets; old results retain their archived implementation and configuration.

Weekly scheduling, participant allocation, dynamic tool selection, feedback correction and live calendar integration are outside the implemented scope. Team members manually reviewed 24 main-study cases against their gold specifications; see the [human-review packet](reviews/human-review-packet.md).
