# Yao Xiang: formal core and extraction method draft

Current implementation: [formal-core follow-up](yaoxiang-formal-followup.md). Latest mathematical evidence and benchmark handoff: [30 September reference review](yaoxiang-reference-review.md). The historical snapshot below is preserved.

Date: 29 September 2026. Branch: `yaoxiang-formal-core`. This is implementation
and synthetic development evidence, not a benchmark report or a frozen contract.
The provisional dependency is Li Hao's published commit `b063fb9`; Yao Xiang's
changes remain local until separately authorized for commit/publication.

## Implemented scope and formulation

`schema.py` defines the canonical v1 draft. For each mandatory activity i, choose
an integer start s_i and use its fixed positive duration d_i. The interval is
[s_i, s_i + d_i). Its complete interval must fit within one availability window
for the activity and every required participant/resource. Empty availability
means unavailable. Every participant/resource has capacity one; adjacency is
allowed, overlap is forbidden. The horizon is one fixed-offset day with at most
48 slots of 30 minutes and an explicit date, start time and timezone.

The compiler enforces release s_i >= r_i, deadline s_i + d_i <= deadline_i,
fixed start s_i = fixed_i, precedence s_before + d_before <= s_after, and
non-overlap with blocked intervals for every activity using their target entity.
Preferred-start intervals concern the start only: penalty w is incurred unless
lower <= s_i < upper. Generation minimizes the sum of those integer penalties.

Repair preserves the common original schedule and minimizes, lexicographically:
(1) number of activities whose starts change, (2) sum of absolute start shifts
in slots, and (3) preference penalty. No-op repair therefore preserves an already
feasible original even if moving it would improve preferences. `RepairCase`
retains the original problem/schedule, event description and updated problem;
original feasibility is the independent evaluator's responsibility. No new or
cancelled activity semantics are introduced.

`solver.py` builds one CP-SAT interval per activity, legal integer start domains,
entity no-overlap constraints, precedence inequalities, and exact preference
indicators. A malformed specification is rejected before compilation; valid
contradictions remain instances and can produce INFEASIBLE. Unary empty domains
compile to an explicit false constraint rather than an invalid solver model.

Sequential optimization fixes a stage only after an exact OPTIMAL result. Both
absolute and relative gap limits are explicitly zero. A single total time budget
includes compilation and is shared across stages; remaining time is passed to
each CP-SAT call. Results retain objective value, bound, stage status, stage budget,
elapsed time, seed/workers configuration and proof status. A later UNKNOWN retains
a prior feasible incumbent without claiming full lexicographic optimality.
MODEL_INVALID is separate from INFEASIBLE. Total preference weight above 2^53-1
is an explicit backend limitation (MODEL_INVALID), preserving exact integer
interpretation of the double-valued bound interface.

See [OR-Tools CP-SAT statuses](https://developers.google.com/optimization/cp/cp_solver)
and the [locked v9.14 parameter definitions](https://github.com/google/or-tools/blob/v9.14/ortools/sat/sat_parameters.proto).
The compiler uses the repository's objectives, not the job-shop makespan objective.

## Draft API and serialization handoff

- `ProblemSpec.from_dict/from_json` strictly rejects unknown fields, duplicate JSON
  keys/IDs, missing references, type coercion, unsupported constraints, invalid
  endpoints and inconsistent timezone/horizon data. `to_dict/to_json` round-trip
  tagged constraints. Arrays must be explicit; defaults never infer availability.
- `Schedule.from_list` reads `[{"activity_id":"A","start_slot":0}, ...]`;
  `require_ids` checks complete public activity coverage. This checks structure,
  not gold feasibility. `to_list` sorts entries by ID.
- `NaturalLanguageView(instance_id, variant_id, task_type, text, activity_ids,
  original_schedule=None)` contains public inputs only. `task_type` and the public
  `activity_ids` make task dispatch/coverage explicit; both are draft field-name
  concretizations for team review. Its JSON loader requires all six fields,
  including `original_schedule: null` for generation, and rejects gold fields.
- `solve(spec, SolverLimits(time_limit_seconds=5, random_seed=0, num_workers=1),
  repair_context=None) -> SolveResult` exposes reference/provisional solver work.
  Repair requires `RepairContext(original_schedule)`. These development defaults
  are not frozen reference or evaluated-pipeline experiment budgets.
- `run_solver_augmented(nl_view, model_config, solver_limits,
  provider_complete=complete) -> PipelineResult` makes one extraction call through
  Li Hao's provider then compiles the strict output. Provider attempt caps/retries
  remain explicit in the injected provider/config. No gold specification is an
  inference argument. This path does not request a model SAT/UNSAT declaration,
  so `declared_status` is null; solver outcome is stored separately.
- `to_data(result)` is the JSON boundary for nested canonical records: schedules
  become arrays, constraints retain type tags, and timings are name/value pairs.
  Generic dataclass `asdict` loses constraint tags; consumers must use `to_data`.
- `ValidationResult(structural_valid, hard_feasible, violations, objectives)` and
  `Violation(constraint_id, category, activity_ids)` are types only. ObjectiveValues
  carries preference penalty and optional moved count/total shift. Yong Qing must
  recompute these independently, never using `legal_starts`, `_compile`, or
  `measure_objectives` as validator logic.

Supported tagged JSON constraints and all required fields are enumerated in
[`specification.txt`](../prompts/extraction/specification.txt). Complete executable
examples are in [`tests/examples`](../tests/examples); they are synthetic component
examples, not the six reviewed benchmark fixtures owned by Yong Qing.

`compare_specifications` is evaluator-only structural diagnosis. It ignores
constraint IDs/order but retains multiplicity and preference weights. Structural
mismatch is not proof of different feasible sets: alternate equivalent encodings
need semantic review. It never feeds gold information back into inference.

## Verification and failure analysis

Tests cover schema rejection/round trips, hard constraint interactions, resource
contention, multiple participants, full-window containment, preferences, no-op and
disruption repair, status/proof handling, malformed extraction, provider errors,
and hidden-gold boundaries. Sixty seeded tiny cases are checked for both generation
and repair against independently enumerated assignments/objectives. The enumerator
in `tests/formal_support.py` does not call compiler/domain/objective helpers; it is
a test oracle, not the production independent validator or benchmark reference.

Hand-checked demo: A and B last one slot, share P, and require A before B within
[0,4). Generation may return A0/B1. Original A0/B2 is feasible. Blocking P in [0,1)
forces A to move; A1/B2 attains the lower bound (1 moved, 1 slot shifted, 0 penalty).

Approved live run `yaoxiang-components-20260929-01` used explicit `qwen3.6:35b`,
2 requests, no retries, at most 2,048 output tokens each, and 5 solver seconds per
case (seed 0, one worker). Both returned schema-valid extractions and CP-SAT OPTIMAL,
but both reversed precedence. Generation returned A1/B0; repair returned A3/B2,
with extracted objective (1,3,0). Both violate the public A-before-B requirement.
Repair also replaced the explicit block with [1,4) activity/participant windows;
that encoding is equivalent for this case, so it is not a separate demonstrated
semantic failure. Reported usage: generation 892 input + 366 output = 1,258 tokens;
repair 972 input + 252 output = 1,224 tokens; total 2,482 tokens. The authorized
4,096 requested-output-token reservation and two-call cap are consumed.

Raw responses, configs, exact source snapshot and run harness are retained privately
under `runs/yaoxiang-components-20260929-01/`. Do not rewrite this run or interpret it
as an independent gold-validation result. The subsequent extraction prompt clarifies
before/after fields with their explicit inequality; it has offline coverage only,
and has not been live-retested. A synthetic reversed-precedence regression records
the failure class without correcting or hiding model outputs. No held-out data
or benchmark outcomes were used for this development edit.

## Verification commands and remaining gates

POSIX shell from the repository after installing `requirements.lock` and package:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/scheduling solve --spec tests/examples/formal-generation.json
.venv/bin/scheduling solve --spec tests/examples/formal-repair.json --original-schedule tests/examples/formal-original.json
.venv/bin/scheduling solver-offline --view tests/examples/generation-view.json --response-file tests/examples/formal-generation.json
.venv/bin/scheduling solver-offline --view tests/examples/repair-view.json --response-file tests/examples/formal-repair.json
```

Observed verification: the full suite passed **203 tests** in a fresh credential-free
macOS ARM64 environment with Python 3.12.2, a hash-checked dependency install and
a noneditable wheel install. `pip check` passed. Both generation/repair commands
and canned pipelines returned OPTIMAL through the installed package outside the
source directory; the revised packaged prompt loaded successfully. The repair
objective was (1,1,0). Code/prompt/test hashes matched the working checkout.
An earlier in-checkout full run passed 200 tests; after the calendar-boundary fix
and failure-class regression, 55 focused tests and the fresh full 203-test run
passed. Private verification records are under `runs/yaoxiang-offline-20260929-01/`.
Linux remains unverified; Docker reported its daemon socket unavailable.

These commands do not call the model or load credentials. `--output NEW_FILE`
creates a private file exclusively; an existing path is refused. Exit status alone
is not feasibility: inspect the recorded solver/pipeline status, including UNKNOWN.

Gate A remains open for both teammates' contract review and Yong Qing's independent
validator/mutation checks. Gate B remains open for canonical direct integration,
correct gold-validated live A/B cases and fresh Linux verification. The local Docker
daemon is unavailable. Successful tiny direct checks and failed B extractions are
development evidence, not a passed integration gate. Main branch integration and
any shared schema freeze require normal teammate review.

Concrete handoff: Li Hao reviews canonical view/schedule/result serialization and
adapts `request_direct` into `run_direct`; Yong Qing reviews compiler rules and
implements `validate_schedule` plus the six shared fixtures. His runner can then
call `solve` for references, preserving UNKNOWN/FEASIBLE versus proven labels and
stage optima; it must independently check original/repaired schedules against their
respective gold specifications. No benchmark labels or shared gold fixtures have
been fabricated here. Reference audit on that benchmark and statistical analysis
wait for its delivery and the evaluation freeze.

The user reports no teaching-team feedback yet and confirms continued development
with explicit `qwen3.6:35b`. Proposal submission/receipt status was not confirmed.
Coordination still requires that receipt/status, final model
eligibility or teaching-team acceptance, evaluation access/budget and protocol freeze.
These have not been inferred from provider access. No Canvas submission, teammate
review, or approval is claimed. Course deliverables remain as listed in planning.md.

## Contribution and AI-assistance record

Yao Xiang directed this member scope, confirmed availability around 8–10 hours/week,
authorized the provisional Li Hao dependency and narrow CLI/package integration,
and approved the bounded live check. Codex generated the implementation, tests and
this draft; it executed the checks and analyzed the saved synthetic failures. Human
review, authorship understanding, teammate review and independent evaluation remain
required. This record does not imply Yao Xiang personally wrote each generated line
or that tests establish empirical superiority of either research approach.
