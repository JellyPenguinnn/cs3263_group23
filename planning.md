# Four-week project plan

## 1. Authority, status, and completion target

This is the working implementation and evaluation plan for Group 23's **AI Assistant for Dynamic Constraint-Aware Scheduling: Direct LLM Reasoning vs Constraint-Solver-Augmented Reasoning**. It defines scope, interfaces, responsibilities, milestones, and evaluation criteria. Design decisions remain provisional until the corresponding review gate is complete.

- Setup and contract agreement: **28 September–4 October 2026**.
- Four implementation weeks: **5–30 October 2026**.
- Completion target: **Friday 30 October 2026**, in Week 11 (26–30 October).
- Mandatory proposal deadline: **28 September 2026**; confirm the Canvas submission receipt. Its body is limited to one single-spaced, single-column page with 1-inch margins, excluding title/references.
- Course presentation: week of **9 November 2026**, normally 15 minutes plus 5 minutes of questions; a recording may be requested.
- Course final report: **13 November 2026**.
- The Week 11 target includes implementation, evaluated results, a complete report draft, and presentation/demo material. The remaining course window is for review and required submission adjustments, not planned core development.
- Current repository status: documentation, configuration templates, and empty directory scaffold only; no implementation code. All implementation and research gates below remain open until supported by evidence.

The course project carries 25% of the course grade. The mandatory proposal is ungraded. The final report is at most 10 single-spaced, single-column pages, excluding title/references, with 1-inch margins and at least 11-point font. Figures, tables, and substantive discussion count toward the limit. Contributions, responsible AI, source attribution, and disclosure of AI assistance are required. The submitted proposal and report must clearly list every member's name, matriculation number, and email; place those identifying details on the private submission title page. Write for classmates with general AI knowledge. Check Canvas announcements and proposal feedback for subsequent changes before the experimental freeze and final submission.

## 2. Research questions and contribution

1. How do problem size, slack, constraint interactions, and shared resources affect direct versus solver-assisted scheduling?
2. What fraction of failures arises from language-to-formal translation, compared with schedule construction, optimization, or operational errors?
3. How well does each approach repair a common starting schedule while preserving unaffected activities?
4. How stable is performance under semantically equivalent paraphrases and constraint reorderings?

Hypotheses: solver assistance may improve hard-constraint satisfaction as interactions increase, but extraction mistakes may dominate end-to-end failures; direct models may be adequate on simpler cases; equivalent wording may affect both paths. These hypotheses can be rejected by the results. Do not claim superiority or novelty in advance.

The intended contribution is a reproducible, bounded comparison combining generation, repair, language robustness, and failure attribution. The report should explain conditions under which each approach is useful and the limits of the constructed instances.

## 3. Scope and explicit exclusions

### Core

- Both schedule generation and minimum-disruption repair.
- One-day horizon, integer 30-minute slots, explicit date/timezone context when rendered as clock times.
- Mandatory fixed-duration, non-preemptive activities; fixed participants and required capacity-one resources.
- Hard constraints: full-activity availability, release times, deadlines, fixed appointments, precedence, participant non-overlap, resource non-overlap.
- Soft constraints: weighted penalties for a task starting outside a preferred start window; preferences and weights explicitly described to both approaches.
- Initial repair events: a new blocked interval, a tightened deadline, or a changed fixed appointment. Events supply an authoritative updated problem; no ambiguous conversational state.
- Direct LLM, LLM-to-CP-SAT, a gold reference solver, and an independent validator.
- Controlled synthetic instances, a small human-written realistic set, and selected paired language variants.

### Stretch, only after the core gates pass

- One verifier-feedback correction round, reported separately with its exact information and budget.
- A second research model beyond the required primary comparison, or a second initial-schedule policy sensitivity check.
- A small visualization/demo interface.

Participant assignment, multi-capacity resources, new/cancelled tasks, longer horizons, and repeated disruption sequences are future extensions, outside the four-week delivery.

Live calendars, account integrations, RAG, autonomous calendar edits, mobile applications, model training, and production deployment are outside the four-week delivery. Do not add them as implicit dependencies.

Generation-only is the proposal's fallback. Taking it requires an explicit team decision and a documented scope reduction; it does not satisfy the original generation-and-repair completion claim.

## 4. Team responsibilities and workload

Working assumption: **8–10 hours per member per week**, approximately 32–40 hours each for implementation, with lightweight setup beforehand. Confirm availability at kickoff and rebalance at each weekly review. These are planning estimates, not records of work performed.

| Member | Branch | Primary deliverables | Approximate total effort |
| --- | --- | --- | --- |
| Tea Li Hao | `lihao-llm-baseline` | SoCLaaS adapter; direct-LLM generation/repair baseline; direct prompts and parsing; provider tests; package/CLI/CI setup; demo integration | 22h implementation/tooling + 6h review/analysis + 8h writing/demo |
| Tham Yao Xiang, leader | `yaoxiang-formal-core` | Shared schema; CSP/COP formulation; CP-SAT compiler; generation/repair objectives; reference labels; NL-to-specification extraction and solver-augmented pipeline | 24h technical + 4h coordination + 4h review/analysis + 4h writing |
| Woo Yong Qing | `yongqing-evaluation` | Synthetic generator/rendering; independent validator; runner; metrics; result tables/figures | 24h technical + 6h review/analysis + 6h writing/demo |

The independent validator is implemented by Yong Qing, with Yao Xiang reviewing mathematical rules. Separate implementations and cross-checks reduce shared solver/validator bugs. Changes to validation rules require team review. All members are responsible for the overall result.

Review rotation: Li Hao reviews benchmark wording, provider/runner integration, and user-facing diagnostics; Yao Xiang reviews direct-baseline assumptions and formal validity rules; Yong Qing reviews solver and extracted-constraint behavior against independently enumerated cases. Any member may flag a correctness problem outside their ownership.

Report ownership: Li Hao drafts motivation, related work, the direct baseline/provider method, and AI-assistance disclosure, and assembles the demo; Yao Xiang drafts formulation, solver/repair method, and the extraction pipeline; Yong Qing drafts benchmark and results. All jointly write discussion, limitations, responsible AI, and conclusion, and rehearse questions about the entire system.

### File ownership once implementation starts

| Area | Lead | Review/coordination |
| --- | --- | --- |
| `src/scheduling/schema.py`, `src/scheduling/solver.py`, `src/scheduling/objectives.py` | Yao Xiang | Other two approve contract changes |
| `src/scheduling/providers/`, `src/scheduling/pipelines/direct.py`, `prompts/direct/` | Li Hao | Yao Xiang reviews scientific assumptions |
| `src/scheduling/pipelines/solver_augmented.py`, `prompts/extraction/` | Yao Xiang | Yong Qing reviews extraction/validation boundaries |
| `src/scheduling/validation.py`, `benchmarks/`, `evaluation/` | Yong Qing | Yao Xiang cross-checks validity rules |
| Corresponding component tests | Component owner | Rotating reviewer |
| `pyproject.toml`, lockfile, CI, shared CLI, README | Li Hao integrates | Owners request changes; avoid competing edits |
| `planning.md`, `AGENTS.md` | Team agrees; one editor at a time | Record material decisions below |

The directory scaffold exists, but the module files above are planned interfaces, not implemented components. Empty `.gitkeep` files preserve directories in Git; replace them with substantive files as each component is implemented. Keep a small Python package with explicit interfaces. The initial `main` contains no implementation code; later reviewed component PRs integrate into `main`.

### Directory backbone and artifact placement

| Directory | Intended contents | Owner |
| --- | --- | --- |
| `src/scheduling/`, `src/scheduling/providers/`, `src/scheduling/pipelines/` | Shared schema, solver/objectives, validator, provider adapter, and two pipelines; exact module ownership above | Component owners |
| `prompts/direct/`, `prompts/extraction/` | Versioned prompt templates; no hidden gold answers | Li Hao / Yao Xiang |
| `configs/development/` | SoCLaaS development model/settings, solver limits, small pilot caps; no credentials | Li Hao, reviewed by all |
| `configs/experiments/` | Frozen model, prompt, solver, sampling, and budget references for main runs | Yong Qing, approved by all |
| `benchmarks/fixtures/`, `benchmarks/manifests/` | Small synthetic development cases and versioned split/seed/hash manifests; declare split explicitly and keep gold evaluator-only | Yong Qing |
| `evaluation/` | Experiment orchestration, metrics, offline replay, and figure export using the canonical package interfaces | Yong Qing |
| `tests/unit/`, `tests/integration/` | Offline component tests and shared-contract/end-to-end checks | Component owners; Li Hao integrates |
| `.github/workflows/` | Future offline CI; no live API calls or credentials required | Li Hao |
| `results/summary/` | Reviewed aggregate tables and claim-to-run references | Yong Qing |
| `report/`, `report/figures/`, `presentation/` | Report/presentation sources, selected figures, and demo materials; no private submission identifiers in Git | Section owners; Li Hao assembles |

No executable files, empty Python modules, package manifests, sample results, or pretend CI jobs belong in the initial scaffold. Generated large/raw outputs go to ignored local `runs/`, `artifacts/`, or `results/raw/`; private inputs go to ignored `data/private/`. These runtime directories need not exist until used. Preserve reproducibility through the reviewed archive and checksums described in Section 14, rather than committing raw outputs.

## 5. Parallel start and dependency management

Before implementation, each member completes the onboarding confirmation in `AGENTS.md`: identity, own local clone path, assigned branch/scope, credential configuration method, and first milestone. Agents ask focused questions or offer choices for unresolved decisions and wait before dependent work. Missing provider access permits offline work; it does not change component ownership.

**Day 1–2: 28–29 September.** Agree the version-1 contract below and at least six tiny fixtures: simple SAT, overlap, shared resource, precedence/deadline interaction, proven UNSAT, and repair. Yao Xiang owns the schema PR; Li Hao owns the shared provider-call interface; all review both contracts. Each person can start immediately:

- Li Hao: provider capability checks, canned direct-output parsing, direct prompts, and package setup against the draft contract.
- Yao Xiang: formal definitions, tiny solver cases, and extraction prompts; use a canned provider response until the shared adapter is ready.
- Yong Qing: hand-written gold fixtures, independent schedule checks, and renderer/runner design using canned pipeline outputs.

### First implementation checkpoints by member

| Member | First work increment | Required evidence and handoff | Continue with |
| --- | --- | --- | --- |
| Li Hao | Establish the package/test setup and provider interface; implement canned direct-output parsing and bounded provider error handling | Verified offline setup/test commands; provider response contract for Yao Xiang and Yong Qing; parser cases for valid, malformed, and missing-task outputs. A live smoke check is separate and requires configured access and a confirmed cap | Direct generation/repair, shared CLI and integration, then the assigned runs, demo, and writing |
| Yao Xiang | Implement the canonical schema, tiny generation solver, and explicit repair context/objectives incrementally | Schema examples and rejection cases; hand-checked or exhaustive tiny feasibility/objective checks; contract review request to both members. Publish reference-solver interface/limits for Yong Qing | Full core constraints, extraction and solver-augmented pipeline, then proof audit, failure analysis, and writing |
| Yong Qing | Define the six shared gold fixtures, independent validator, and a runner consuming canned pipeline outputs | Manually justified expected validity/objectives; deliberate invalid-schedule mutations caught; generation/repair record format and fixture review with both members | Generator/renderings and splits, reference labelling using Yao Xiang's solver, metrics/replay, then main runs and analysis after the evaluation freeze |

These are ordered starting points, not extra scope or independent replacements for the shared gates. Component tests belong to each component owner. Treat Section 6 as the working draft until team review freezes it; questions that alter its semantics require agreement, but fixture design, solver mathematics, provider parsing, and other independent work can proceed. Li Hao establishes the single package manifest and test command early; other members do not create competing manifests. Yao Xiang's canonical schema is integrated before consumers finalize their imports. Yong Qing checks expected answers independently rather than deriving them solely from the reference solver.

When a dependency blocks execution, the agent names the owner, missing interface/version, and smallest requested deliverable, then continues other owned tasks using the agreed contract. The member passes that handoff to the teammate; agents are not assumed to have access to each other's chats or permission to message them. After reviewed shared work reaches `main`, fetch and merge it into the member branch, preserve local work, and verify integration. A newly created local branch without its remote counterpart or an unavailable dependency is reported explicitly, never silently replaced with another branch or implementation.

Mocks/canned outputs unblock interface work but never count as live-model research evidence. Merge the shared contract first, then merge small component increments every 1–2 days. Do not wait until the end of a week to integrate three large branches.

If a contract change is needed, record its motivation, affected consumers, migration, and schema version; coordinate before editing shared files. Never copy divergent schemas into separate components.

## 6. Version-1 shared contract

This section is a proposed implementation contract to freeze by 29 September. Field names can change during that review, but all consumers must change together.

### Gold problem and natural-language view

`ProblemSpec`: `schema_version`, `instance_id`, `task_type` (`generation` or `repair`), `horizon_slots`, `slot_minutes` (30), participant records, resource records, activities, and constraints. Each participant/resource has a unique ID and explicit availability windows; capacity is one in v1. Activity records contain unique stable IDs, positive integer `duration_slots`, participant/resource IDs, and an explicit list of zero or more availability windows. Constraints/preferences have stable IDs and typed operands; unknown types and dangling IDs are errors.

- Store `horizon_start` and `timezone` explicitly; slot zero is that start, with `0 <= start < end <= horizon_slots`. No implicit current date/timezone. Initial scenarios use a single fixed-offset day.
- Activity, participant, and resource IDs are visible labels in every language rendering. Extracted constraints use their own IDs; hidden gold constraint IDs are never required for a correct extraction. Match constraints by normalized type, operands, and values.
- Intervals are half-open `[start,end)`. Adjacent activities are permitted.
- An activity must fit completely within one allowed window for the activity and for each required participant/resource, not span gaps. Explicit full-horizon availability means unrestricted; an empty list means unavailable.
- A blocked interval identifies its target kind (`participant` or `resource`), target ID, and half-open endpoints. Its effect applies to every activity using that entity. No unstated availability defaults.
- Mandatory activity IDs must occur exactly once in a schedule. Missing, duplicate, and invented activities are invalid.
- Release times, deadlines, fixed starts, precedence, and blocked intervals have explicit semantics. No inferred travel/rest constraints unless stated.
- Resources and participants cannot be double-booked. Multiple required participants must all be available for the full interval.
- A preferred start window uses explicit inclusive lower/exclusive upper start bounds and an integer penalty weight. Generation minimizes the sum of violated-preference weights.
- A repair benchmark case retains `original_problem`, `original_schedule`, `event`, and `updated_problem` separately. The original schedule must pass validation against the original problem; it may violate the updated problem. Evaluate all repaired schedules against the updated problem. Both systems receive the same original schedule and the complete updated natural-language description; the evaluator keeps both gold specifications private.
- Reject malformed types, endpoints, and references as schema errors. Preserve well-formed contradictions (such as a deadline earlier than the release time, or insufficient available time) as scheduling instances whose feasibility must be solved, not filtered away as invalid data.

`NaturalLanguageView` contains the user-visible text, variant ID, base-instance ID, and, for repair, the common original schedule. Evaluated pipelines receive this view and the public output/schema instructions. They do not receive gold constraints, oracle solutions, hidden labels, or expected objective values.

### Output and outcomes

`Schedule`: a list of activity IDs and integer start slots. End times are computed from fixed durations. Claimed textual times must be normalized without guessing or rounding invalid inputs.

`PipelineResult`: `instance_id`, `variant_id`, `approach`, `status`, optional schedule, optional extracted specification, diagnostics, timings, and usage. Pipeline status is one of `SAT`, `UNSAT`, `UNKNOWN`, `INVALID_OUTPUT`, or `ERROR`. A SAT claim requires a complete schedule; an UNSAT claim from a direct LLM is a prediction, not a proof.

Record the model's declared status separately from parsing/execution status and final gold validation; a parseable SAT claim is not an accepted solution. Preserve the underlying solver status separately: `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `UNKNOWN`, or `MODEL_INVALID`. Also store objective value, best bound where available, time limit, elapsed time, and whether each lexicographic stage was proven optimal. Never report a feasible incumbent as a proven optimum, or a timeout as UNSAT.

`ValidationResult`: structural validity, hard-feasible flag, violations with constraint IDs, objective components recomputed from gold, and repair distance. The validator consumes a schedule and gold specification; it must not call CP-SAT or reuse the solver's constraint-building implementation.

### Proposed Python interfaces

```python
solve(spec, limits, repair_context=None) -> SolveResult
validate_schedule(gold_spec, schedule, repair_context=None) -> ValidationResult
run_direct(nl_view, model_config) -> PipelineResult
run_solver_augmented(nl_view, model_config, solver_limits) -> PipelineResult
evaluate(instance, pipeline_result, gold_reference) -> EvaluationRecord
```

`RepairContext` contains the common original schedule, including stable activity IDs and start slots. It is required for a repair task and absent for generation; missing repair context is an explicit error. Both the solver and validator use it to compute moved count and total shift. The evaluator first checks the original schedule against `original_problem`, then checks repairs against `updated_problem` with this context. The solver-augmented path builds the same context from the public original schedule; it must not receive the original or updated gold specification.

Li Hao also provides a minimal typed `complete(messages, model_config) -> ModelResponse` interface with content, returned model, timing, usage, and sanitized error fields. Both pipelines use this adapter. Freeze it alongside the shared schema so Yao Xiang can work with canned responses without waiting for live access.

Use explicit typed models and deterministic serialization. Validate generated JSON before compilation. Do not execute model-generated code. Schema-valid JSON is not proof of semantic correctness.

## 7. Formalization and repair objective

For each activity i, choose an integer start s_i and define end e_i = s_i + duration_i. Require allowed-window containment, e_i <= deadline_i, and s_i >= release_i where specified. A precedence i→j imposes e_i <= s_j. Shared participants/resources impose e_i <= s_j OR e_j <= s_i. Fixed appointments impose equality on start.

Generation: satisfy all hard constraints and minimize the stated preference penalty.

Repair: satisfy the updated hard constraints and lexicographically minimize:

1. `moved_count = sum(start_i != old_start_i)` over retained activities;
2. `total_shift_slots = sum(abs(start_i - old_start_i))`;
3. preference penalty.

Use sequential optimization or a proven equivalent bounded encoding. For sequential optimization, only freeze a prior objective value as optimal after that stage has been proven optimal. Otherwise retain the feasible incumbent and explicitly mark optimality as unproven. Hard constraints are never converted into soft penalties.

Document the initial-schedule policy (initially a saved feasible schedule produced by the pinned gold solver configuration) and give both approaches exactly that schedule. Report that this choice may favor some repair patterns. New/cancelled activities are excluded from v1; if later added, define retained-task distance and mandatory-presence semantics first.

Compare repair objective tuples lexicographically. Report moved-count excess first; treat total-shift excess as a secondary optimality gap only when moved count equals its proven optimum. Interpret preference gaps only when both earlier objectives match. A schedule moving more activities but shifting fewer slots is not a better lexicographic repair. Raw component values can always be shown.

Changing weights or objective priority changes the question being studied and requires a new experiment configuration. Keep raw moved count and total shift even when reporting the lexicographic optimum.

## 8. Benchmark and evaluation design

### Construction and splits

- Development: approximately 20–30 manually checked cases. Cover boundaries, each constraint type, interactions, and known failure modes.
- Provisional main target: 120 generation + 120 repair base instances. Adjust after the pilot based on measured cost/runtime, and freeze the final count before inspecting test results.
- Add 12 human-written realistic scenarios, balanced across personal/shared settings and generation/repair. These assess plausibility; do not claim population representativeness.
- Select 24 base instances for two additional equivalent language variants each: paraphrase and constraint reordering. This yields a provisional total of 300 input renderings (240 + 12 + 48).
- Both core approaches use each rendering: 600 model calls per complete single-model, single-attempt pass. Repeats, pilot calls, feedback, and extra models are additional. This arithmetic is a planning estimate, not a budget authorization.
- Group all variants and related generation/repair scenarios from a common base in the same split. Keep prompt examples and tuning cases out of the held-out test set.

### Confirmatory experiment matrix

Provisional controlled allocation, to confirm using development-only pilots before test generation:

| Sweep | Generation bases | Repair bases | Levels and allocation per task type | Other factors |
| --- | --- | --- | --- | --- |
| Activity count | 30 | 30 | 4/8/12 activities; 10 cases per level | Fix horizon and target slack/contention/density bands |
| Available slack | 30 | 30 | Low/medium/high; 10 cases per level | Fix 8 activities and target contention/density bands |
| Constraint interaction density | 30 | 30 | Low/medium/high; 10 cases per level | Fix 8 activities and target slack/contention bands |
| Resource contention | 30 | 30 | Low/medium/high; 10 cases per level | Fix 8 activities and target slack/density bands |
| **Total** | **120** | **120** | Each cell of 10: 5 proven SAT, 5 proven UNSAT | Unique bases across sweeps |

Balance the three disruption types within the repair set and record their counts. Target 6 SAT/6 UNSAT for the 12 realistic scenarios. Select the 24 language-variant bases in advance: 12 generation and 12 repair, balanced by SAT/UNSAT and spread across difficulty. Report how this artificial class balance differs from real scheduling demand.

Define unary slack using each activity's number of allowable starts after duration, windows, and deadlines, before interactions. Define interaction density and resource contention separately; record realized counts/bands. These factors are coupled, so report unmatched covariates and selection rates rather than claiming a perfect causal intervention. Freeze exact definitions, seeds, quotas, time limits, and exclusion rules in the benchmark manifest after the pilot.

Primary outcome for SAT cases is valid-schedule rate; UNSAT cases assess false SAT and correct infeasibility claims. Repair also measures lexicographic objective quality. Language variants assess paired changes in these outcomes, not exact schedule identity: multiple different schedules may be equally valid and optimal.

Generate feasible instances with a known witness. Establish UNSAT with the gold solver, including interacting contradictions rather than only obvious single-rule failures. Keep unresolved reference cases in a separately reported set, or exclude them using the frozen rule; do not silently assign a binary truth label to UNKNOWN. Record selection/exclusion counts and reasons.

Use targeted difficulty sweeps: task counts such as 4/8/12, several slack levels, low/high resource contention, and sparse/dense meaningful constraint interactions. Pilot for floor/ceiling effects. Avoid a full Cartesian product; separate controlled sweeps from mixed cases. Define density and slack operationally in the generator documentation and store realized values. More constraints do not automatically imply greater difficulty.

Natural-language renderings must state all information needed to solve the task, including objective priorities. Review paraphrases for meaning preservation. Hand-written scenarios need a second member to check the gold formalization. Record limitations of fixed durations, grid rounding, fixed assignments, and single-day horizons.

### Metrics

- Valid-schedule rate on gold-SAT instances, including all failed attempts in the denominator.
- Hard violations by type and instance, plus missing/duplicate/extra activity counts.
- SAT/UNSAT confusion matrix; UNKNOWN, invalid output, transport errors, and timeouts shown separately. Also report overall coverage and correctness across all labelled cases.
- Preference objective gap on gold-feasible, validated outputs with proven reference optima. For other cases, report bounds or unknown gaps; do not invent an optimum. Show denominators to expose survivorship bias.
- Repair moved count, total shift, and excess disruption relative to a proven optimum; preserve component-wise reporting.
- Formalization errors: omitted, invented, or altered constraints; wrong IDs, durations, endpoints, preference weights, and objectives. Canonical structural comparison is a diagnostic, supplemented by semantic review where equivalent encodings differ.
- Paired changes in validity/objective across renderings, with repeated identical prompts on a small subset if resources permit to estimate model variability.
- End-to-end latency plus extraction/solver components; token usage; request count; retries; rate-limit events; cost where known. Missing prices/usage are marked unavailable, never zero.

Define overall accepted-answer rate as `(gold-valid SAT schedules + correct UNSAT answers) / all gold-labelled attempts`, with errors/unknowns contributing no successes. Report SAT validity and UNSAT accuracy separately so a high score on one class cannot hide failure on the other. A gold-UNSAT instance with an independently validated schedule signals a reference/validator defect: investigate before publishing any affected scores.

Confidence intervals and paired comparisons should group by base instance; paraphrases are not independent samples. Report the sample sizes and uncertainty. Do not pool results from changed model/backend configurations without identifying the change.

### Priorities and analysis outputs

The two approaches, both task types, gold validation, and failure accounting are mandatory. The 300-rendering plan is a provisional target, not a minimum required to claim completion. If the pilot exceeds time/quota, reduce the predeclared matrix proportionally while retaining every primary comparison; freeze the revised counts before test access. Do not select easy cases from main-run outcomes.

| Question | Controlled comparison | Required report evidence |
| --- | --- | --- |
| Difficulty and feasibility | A versus B within SAT/UNSAT strata and each sweep | Validity curves with uncertainty; status/coverage table; explanation of interactions |
| Formalization failure | Gold solver versus extracted-spec solver, with independent gold validation | Error-category table; one omitted/altered constraint case; semantic review notes |
| Repair quality | Common old schedule and disruption, A versus B versus gold optimum | Movement/shift results with valid-solution denominators; an annotated repair example |
| Language robustness | Matched canonical/paraphrased/reordered descriptions | Paired validity transitions and objective changes, grouped by base |

Use the same evidence to discuss privacy, participant inconvenience, and objective trade-offs. Bound responsible-AI case analysis to four synthetic cases, drawn from development/realistic examples where possible: unequal inconvenience, an objective trade-off, ambiguous negotiability, and instruction-like task text. Do not build a separate large adversarial benchmark.

For language-effect claims, repeat all three renderings of a preselected 12-base subset three times per approach if the pilot budget permits: 144 additional calls beyond the 600-call pass. Otherwise report observed one-attempt variation and the inability to separate it fully from model sampling variability. Extra models, feedback, and UI follow only after required analysis is complete.

Explain technical depth through the start-domain search space `product_i |D_i|`, the constraints that couple choices, and the distinction between finding a witness, proving infeasibility, and proving optimality. Do not use constraint count alone as a complexity proof. Discuss when ambiguous/missing information, solver availability, translation cost, or time limits make tool use less helpful. Relate any forecast about improved models to observed failures and label it as a hypothesis.

### Fair comparison and error attribution

Use the same verified model ID, problem information, reasoning settings where supported, and predeclared per-call output budget for A and B. Pilot that budget on the longest supported outputs of both paths so one format is not artificially truncated. Freeze each approach's task-appropriate prompt and record both; do not give either path private hints or unreported tools; CP-SAT is the declared tool for B. Direct inference has no external solver/code execution or hidden agent tools. Record prompt lengths and token usage because output tasks differ. One model attempt per approach is the core condition; transport retries are bounded, recorded, and distinct from semantic corrections. Neither path gets hidden gold feedback.

Gold-to-Solver isolates the reference/modeling layer. Compare B's extracted specification to gold and validate B's final schedule against gold. A correct output despite an extraction mistake remains an end-to-end success but an extraction failure. If the gold solver or independent validator fails cross-checks, fix the infrastructure before interpreting model results.

Assign deterministic operational categories first: provider/transport error, malformed output, unsupported specification, solver model error, solver limit, or gold-invalid schedule. Track extraction mismatches separately; an associated mismatch does not alone prove the cause of a failure. On a preselected diagnostic sample of up to 20 B failures (or all if fewer), review normalized constraints and, where useful, replace one erroneous extraction component with gold in an explicitly labelled diagnostic rerun. Keep these reruns outside primary scores. A second member reviews ambiguous equivalences and disagreements. If sampling failures, state the sampling rule and denominator rather than extrapolating unsupported causal percentages.

Preserve malformed outputs and failures with appropriate redaction. Never hand-repair a test response or keep only successful retries. An optional feedback experiment must state whether feedback uses gold constraints or only the model's extracted specification; those are different information settings.

## 9. NUS SoCLaaS and execution budget

- Base URL: `https://soclaas-api.comp.nus.edu.sg/v1`.
- Environment names: `SOCLAAS_BASE_URL`, `SOCLAAS_API_KEY`, `SOCLAAS_MODEL`.
- **Development and integration: use SoCLaaS only, without frontier-model calls.** Development fixtures, integration checks, and bounded pilots can proceed before final evaluation model eligibility is resolved.
- `default` is the initial model alias. Query `/models`, inspect available model IDs, and choose a verified development ID before scheduling pilots. If only an alias is available, record it, the returned model identity, run time, and the resulting reproducibility limitation.
- SoCLaaS provides an OpenAI-compatible API. Verify completion endpoint, model access, output parsing, supported structured-output/reasoning parameters, quota, and rate limits; do not assume feature parity with another provider.
- Adapter must have explicit connect/read timeouts, bounded retries for transient errors, sanitized errors, and per-attempt accounting. Start with sequential requests; increase concurrency only within verified provider limits.
- Credentials stay in a local ignored `.env` or process environment. Each member supplies an authorized credential. Do not distribute the project owner's key through Git or team documents. Rotate any key shared through chat/screenshots.
- Validate authentication with a model listing and one small non-sensitive completion before scheduling experiments. These are connectivity checks, not research results.
- **Development readiness by 4 October:** Li Hao records the SoCLaaS model/backend identity, supported request options, output parsing, and authorized development cap. Final evaluation eligibility is not a prerequisite for live SoCLaaS development.
- **Final evaluation decision by 18 October, before held-out runs:** Yao Xiang documents how the selected primary model meets the course frontier-model requirement or obtains teaching-team acceptance of a SoCLaaS-only comparison. The course describes SoCLaaS open-weight evaluation as an additional option; an accessible model is not automatically eligible. A frontier model, if required, is introduced only for this later evaluation phase under separately authorized access and budget. If eligibility/access remains unresolved, continue development but hold the main comparison and record the schedule impact; do not claim course compliance.
- Keep `configs/development/` and `configs/experiments/` separate. Select models through configuration and the shared provider interface. Any necessary provider extension is an explicit, reviewed scope decision. Before freezing evaluation, qualify the selected model on development cases, rerun parsing/capability checks, and pilot its cost/runtime. Use the same primary model and equivalent information for both paths. SoCLaaS development outputs cannot substitute for missing final-model attempts or be pooled into its results.
- Before bulk execution, run a small pilot and estimate request/token cost and runtime. Set a maximum requests/tokens or currency cap, concurrency cap, and stop conditions. Obtain the project owner's explicit budget authorization; course reimbursement is not an execution budget.
- The course guidelines allow a group claim up to $100 under their receipt rules. SoCLaaS accounting may differ; confirm institutional quota/cost rather than assuming it is free or reimbursable.

Store model ID, returned backend identity if available, prompt/config hashes, benchmark version/hash, code commit, dependency versions, solver parameters/seed/workers, host/CPU context, timestamps, and usage coverage in each run manifest. Keep raw responses local/private by default; publish reviewed synthetic fixtures, manifests without secrets, and aggregate results needed for reproducibility.

### Bootstrap connectivity evidence — 28 September 2026

An authenticated model listing and one non-sensitive chat completion returned HTTP 200. The `default` alias returned model ID `qwen3.6:35b`; the response was exactly the requested short acknowledgement, with 17 prompt and 2 completion tokens reported. This is connectivity evidence only. Structured-output support, rate limits, quota/cost, model suitability for the course requirement, and scheduling performance remain unverified. Credentials must remain in an ignored local environment file with owner-only permissions.

## 10. Four-week delivery schedule

| Week | Li Hao | Yao Xiang | Yong Qing | Shared gate |
| --- | --- | --- | --- | --- |
| **1: Oct 5–11** | SoCLaaS adapter, direct prompts/parsing, provider tests, package/CLI setup | Schema, basic solver/tiny-case checks, extraction prompts and first B path | Gold fixtures, independent validator, renderer, runner using canned outputs | Contract frozen during setup (target Sep 29); one generation and one repair example through both live SoCLaaS paths by Oct 11, or an explicit provider blocker |
| **2: Oct 12–18** | Direct generation/repair baseline, bounded provider errors, offline tests, CI and integration support | Complete constraints/preferences/repair, extraction diagnostics, solver-augmented integration | Generator/splits, reference labelling, metrics, pilot automation | Core feature complete on SoCLaaS; development suite passes; final evaluation model eligibility/access resolved, qualification pilot complete, and benchmark/prompts/model/budget frozen by Oct 18 |
| **3: Oct 19–25** | Execute assigned model runs, audit direct-output failures, provider drift and run support | Reference/optimality audit, solver and extraction failure analysis | Execute remaining runs, aggregate records, paired analysis and figures | Planned runs complete or explicitly accounted for; provenance and denominators audited |
| **4: Oct 26–30** | Related work/direct-method draft, integration/demo, selected independent reruns | Formulation/solver/extraction draft, technical discussion, coordination | Benchmark/results draft, reproducibility rerun and figures | Complete report draft within limit; presentation and demo; all members can explain findings; core frozen Oct 30 |

Two brief team checkpoints each week: progress/blockers and integration/review. Leadership is coordination, not sole responsibility for integration. Rebalance workload based on remaining tasks, not only the original titles. Use a shared decision log for scope/API changes; record actual contributions as work occurs.

## 11. Verification and acceptance gates

### Gate A — contract and trustworthy reference

- Shared schemas reject unsupported constraints, invalid endpoints, duplicates, and missing references.
- Tiny hand-checked and exhaustively enumerated cases agree with CP-SAT on feasibility and objective values.
- Independent validator catches deliberate mutations: overlaps, missed deadlines, dropped/extra tasks, resource conflicts, and wrong repair accounting.
- No-op repair preserves a valid original schedule with zero movement when objectives permit; disruption cases have checked optimal repair distances.

### Gate B — integrated core

- Both generation and repair work through A and B with recorded live SoCLaaS development evidence. Frontier-model access is not needed to complete this development integration check.
- Provider errors, invalid JSON, valid-but-wrong extraction, model UNSAT predictions, and solver UNKNOWN remain distinguishable.
- Dependency versions are locked, relevant tests pass, and installation/demo commands are verified from a fresh environment.
- A fresh macOS checkout and a fresh Linux checkout pass the offline reproduction checks in Section 14; unsupported platforms are documented.

### Evaluation freeze — by 18 October, after Gate B and before main runs

Target Gate B by 15 October, leaving 16–18 October for separately authorized final-model qualification and protocol review. Prepare access/eligibility decisions in parallel with development; do not defer them to the last day. If Gate B slips, revise the experiment schedule explicitly rather than skipping qualification or using held-out cases for debugging.

- Final primary-model eligibility or teaching-team acceptance, access, and execution budget are documented.
- The selected evaluation model passes capability/parsing checks and a bounded qualification pilot on development cases, even if it differs from the SoCLaaS development model.
- Model, prompts, seeds, test manifests, metrics, and execution caps are frozen. No held-out results inform these choices.
- Development and main evaluation have distinct configurations/run IDs. An unresolved eligibility or access decision blocks main runs, not development.

### Gate C — defensible results

- Every planned attempt has a record, or an explicit exclusion/failure reason.
- Gold labels/objective proof status and all reported denominators are checked.
- Analysis includes difficulty, repair, language robustness, extraction failures, uncertainty, and limits of realism.
- A teammate independently replays saved synthetic outputs and recomputes validation, metrics, and figures without an API key. New live inference uses an authorized credential and is reported as a new run, not an exact text reproduction.

### Gate D — four-week completion

- Complete report draft and presentation/demo with no fabricated or unverified claims.
- Responsible AI analysis includes concrete cases/measurements and objective trade-offs.
- Actual member contributions and AI assistance disclosed; every member understands the whole pipeline.
- Rubric evidence, report page allocation, timed presentation, and November submission responsibilities are checked against Section 17.
- Repository instructions reflect implemented commands and current limitations; no open critical correctness defects.

## 12. Responsible AI and limitations

Use synthetic schedules initially. Real routines can reveal identity and sensitive activities even after names are removed; any later real-data collection needs consent and a defined retention/access policy. Never commit raw private calendars or personal student identifiers.

Measure per-participant inconvenience when reporting repair results. Fixed participant assignments permit analysis of unequal disruption, not a claim of fair workload allocation. A fairness-aware alternative objective is optional and must disclose its trade-off with total disruption.

Explanations must refer to actual interpreted constraints and validation results. Do not present an LLM narrative as a solver proof or a purported minimum conflict set without verification. Keep ambiguous requests separate from clean benchmark cases; do not silently guess negotiability.

Treat instruction-like text embedded in activity descriptions as untrusted data. Schema validation and a fixed compiler restrict its effect; neither provides a guarantee that extraction is correct. Test this boundary on synthetic adversarial variants, separately from meaning-preserving paraphrases.

The system proposes schedules. It does not send messages or modify calendars. Future external actions require explicit user control. A mathematically optimal schedule can still be undesirable because of missing constraints or poorly selected objectives.

## 13. Risks and pre-agreed responses

| Risk | Response |
| --- | --- |
| Schema integration blocks parallel work | Freeze minimal v1 by day 2; use six shared fixtures; merge small PRs frequently |
| Final evaluation model eligibility/access is unresolved | Resolve by Oct 18 with a qualifying authorized model or documented teaching-team acceptance; keep SoCLaaS development progressing, hold main runs, and record any schedule impact |
| Unreliable formalization | Measure it explicitly; simplify supported language/schema before freeze; retain failures |
| Quota, cost, latency, or rate limits | Pilot first; bounded concurrency and retries; reduce predeclared sample size/repeats before dropping core comparisons |
| Reference optimality cannot be proven | Reduce pilot difficulty or report bounds/unknown gaps; never invent gold optima |
| Shared solver/validator defect | Separate implementations and exhaustive tiny-case cross-checks |
| Excessive scope | Cut UI, feedback, extra models, and long horizons first; generation-only fallback requires an explicit scope decision |
| Unequal workload or absence | Rebalance at weekly checkpoints; keep reviewable intermediate work on branches |
| Provider/model drift after freeze | Record change and separate or rerun affected experiment blocks within budget |

## 14. Git workflow and reproducibility

`main` is the reviewed integration branch. The initial setup commit is shared by the three member branches listed above. Each member uses their own clone; agents must verify their branch and worktree before editing. Never switch branches in another member's active checkout.

After bootstrap, use small PRs from the assigned branch to `main`, with one other member reviewing and relevant checks passing. Include behavior, validation, and scientific impact. Sync from `origin/main` regularly by a normal merge on shared branches; do not rewrite published history or force push. When scope overlaps, agree a single editor. No branch protection is assumed until configured and verified.

Commit source code, tests, small synthetic fixtures, benchmark generation configuration/manifests, dependency lockfiles, report sources, and reviewed aggregate results. Keep secrets, raw/private data, caches, environments, and large run artifacts out of Git. Never use `git add .` without inspecting all candidate files.

Maintain immutable run directories and manifest hashes; fixes require a new run ID. Offline/mock success, provider connectivity, and actual benchmark results are separate evidence classes.

### Portable runtime and supported environments

Li Hao owns packaging and CI. Use a standard `pyproject.toml`, a documented Python minor version (initial target **Python 3.12**), and one committed dependency lockfile. Verify OR-Tools and provider-client compatibility before freezing versions. Use CPU execution locally and remote model inference; a GPU, local model server, paid desktop app, or developer-specific environment must not be required.

Supported targets are macOS and Linux, verified from fresh environments by Gate B. Windows users can use WSL2 with the Linux workflow; native Windows support is optional and must not be claimed without a check. Keep POSIX shell examples labelled. Use repository-relative paths or explicit CLI/config paths and `pathlib`; no hardcoded home directories, absolute personal paths, shell-only business logic, or implicit local timezone. Configuration changes must not require source edits.

Provide an installable CLI covering fixture generation, gold solving, single-case A/B execution, validation, batch execution/resume, offline replay, and metric/figure export. Freeze the command syntax with the implementation and document only commands actually tested. Add one tiny offline example and one explicitly selected live smoke example. Routine tests and CI run offline. Validate outputs semantically across platforms: different tied optimal schedules are acceptable; compare feasibility, objective tuple, and recorded proof status.

### Bounded execution and restart behavior

Yong Qing owns run bookkeeping. Identify attempts by base/variant/task/approach/model-config/repeat ID and immutable config hashes. Write each completed attempt atomically and save manifest/progress incrementally. Resume only matching configurations and reuse completed records without another API call; configuration changes create a new run. Keep interrupted/uncertain requests visible because the provider may already have charged them. Any retry is explicit, bounded, recorded, and counted toward the approved cap.

Begin with one worker and a small pilot. Scale with bounded concurrency and disjoint instance shards under verified rate limits; each attempt has one owner. Stream records and aggregate incrementally so memory does not grow with raw response volume. A database/service is unnecessary at this scale; per-attempt files plus a manifest are sufficient. Include stop conditions for budget exhaustion, persistent authentication/rate-limit failures, or invalid reference results.

### Reproduction package

By Gate C, preserve a versioned package containing synthetic benchmark inputs/gold references, frozen prompts/configs, sanitized attempt records, status/usage accounting, and scripts that regenerate all reported tables/figures. Include checksums and a short manifest-to-figure index. Keep small configurations and aggregate outputs in Git; share larger reviewed synthetic records in a team-accessible archive with a recorded checksum and location. Ignoring `runs/` must not make the reported results unrecoverable. Retain failed attempts and disclose any redaction affecting reproducibility.

Offline replay must reproduce metrics from saved outputs without credentials or live model access. Exact live text and exact tied solver schedules are not guaranteed; retain their original records and separate reruns. Keep a replay-based demo available for presentation failures and label it clearly as recorded evidence.

## 15. Decision log and next actions

| Date | Decision | Status / follow-up |
| --- | --- | --- |
| 2026-09-28 | Complete core by Week 11, Oct 26–30; target Oct 30 | Setup Sep 28–Oct 4; implementation Oct 5–30; presentation and submission follow the course schedule |
| 2026-09-28 | Use SoCLaaS only during development; local secret configuration | Connectivity verified; development model/cap due Oct 4; final evaluation model/access/budget decision due Oct 18 |
| 2026-09-28 | Li Hao: direct baseline and provider; Yao Xiang: formal model and solver pipeline; Yong Qing: evaluation | Responsibilities and interfaces defined in Sections 4–6 |
| 2026-09-28 | Single-day fixed-duration v1 and lexicographic repair | Proposed contract; freeze with team by Sep 29 |
| 2026-09-28 | Primary-model eligibility, portable replay, and rubric evidence are acceptance gates | Final eligibility due at evaluation freeze by Oct 18; portable replay and rubric evidence due at Gates B–D |

Next actions: each member reads these documents; confirm available hours; freeze schema/fixtures and objective priorities; choose a verified SoCLaaS development model and bounded pilot budget; implement Gate A and the provider adapter in parallel. Resolve final evaluation model eligibility/access by Oct 18 before any main held-out run. Record subsequent material decisions here without overwriting prior experiment configurations.

## 16. Source grounding

- Group 23 project proposal: problem definition, two approaches, schedule repair, evaluation metrics, and research scope. The current implementation schedule and responsibilities are defined in this plan.
- CS3263 Project.pdf and CS3263-Project-Guidelines 2627.docx: course comparison requirement, deliverables, evaluation, responsible AI, team contributions, and AI-assistance disclosure.
- ResponsibleAI.pptx: privacy, fairness/trade-offs, transparency, adversarial behavior, unintended effects, and human control.
- [SCHEDBench](https://arxiv.org/abs/2608.00991): scheduling under equivalent language forms.
- [NATURAL PLAN](https://arxiv.org/abs/2406.04520): natural-language planning and complexity.
- [Hao et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.176/): formal-tool-assisted planning and verification.
- [CP-SAT](https://developers.google.com/optimization/cp/cp_solver): integer modeling and distinct solver statuses.
- [SoCLaaS](https://dochub.comp.nus.edu.sg/cf/guides/soclaas/start) and NUS SoCLaaS connection instructions: API configuration. Institutional documentation access and actual provider capability are separate checks.

## 17. Rubric evidence and course delivery

The teaching handout provides qualitative criteria, not numerical weights or a guaranteed top-grade checklist. Use this mapping to gather substantive evidence; implementation claims and research conclusions still require validation.

| Teaching criterion | Project evidence | Lead and review |
| --- | --- | --- |
| Motivation, problem definition, relevance | Concrete personal/shared scheduling use case; explicit variables, domains, constraints, objectives, and assumptions | Li Hao + Yao Xiang; all review |
| Innovativeness and literature | Comparison of related work's task, method, metrics, and limitations; precise account of what this study adds without unsupported novelty claims | Li Hao; Yao Xiang reviews |
| Knowledge, technical depth, achievement | CSP/COP formulation, search-space/interaction analysis, solver and repair method, independent correctness checks | Yao Xiang; Yong Qing reviews |
| Methodology and implementation | Frozen paired design, clean split, fair model access, reference proofs/bounds, tested pipelines, portable reproduction package | All component owners |
| Analysis and insights | Section 8's four evidence outputs, failures, uncertainty, assumptions, tool limitations, and recommendations supported by results | Yong Qing integrates; all interpret |
| Responsible AI | Four bounded case analyses; privacy boundaries, unequal inconvenience, objective choice, transparency, and user control | All; Li Hao edits |
| Effort, initiative, teamwork | Actual contribution log linked to PRs, experiment/review work, and report sections; AI-assistance disclosure | Each member records; leader reconciles |
| Report quality | Technical accuracy, coherent argument, readable figures, clear writing, citations, strict page/format audit | Li Hao assembles; rotating review |
| Presentation and Q&A | Timed coherent explanation, legible results/demo, rehearsed questions, each member able to explain the whole study | All three |

### Report structure and evidence budget

Indicative body allocation totals **10 pages**, including figures and tables. Adjust within the fixed total and preserve space for analysis: motivation/problem (0.75), related work (0.75), formulation/repair (1.5), systems (1), benchmark/protocol (1.5), results/error analysis (2.5), responsible AI/limitations (1), conclusion/contributions/AI disclosure (1). Title and references are separate. Appendices may contain supporting outputs where allowed, but must not carry essential arguments that belong within the body limit.

Required evidence is the Section 8 status/coverage table, difficulty curves, error taxonomy, repair comparison, and paired robustness results, plus two annotated examples: a valid low-disruption repair and a translation failure or infeasible case. Reuse compact figures across related questions; do not fill the report with screenshots. Maintain a claim-to-run/figure mapping and distinguish measured findings from interpretation.

Start the report outline and related-work comparison in Week 1, method sections in Week 2, and result figures in Week 3. Week 4 synthesizes and edits existing material rather than starting the report from scratch.

### Presentation and submission schedule

Target a 15-minute presentation: problem/questions (2 min), formulation and systems (3), benchmark/fair comparison (2), results and failure cases (5), responsible AI/limitations (2), conclusion (1). Split speaking time approximately equally. Rehearse 5 minutes of Q&A on gold correctness, infeasibility versus timeout, extraction error, repair objectives, sampling, fairness, and when tools do not help. Prepare a recorded replay if live access fails.

| Date | Deliverable and verification | Owner |
| --- | --- | --- |
| Sep 28 | Confirm mandatory proposal uploaded through Canvas and retain receipt; possession of a PDF is not proof of submission | Yao Xiang; another member verifies |
| By Oct 4 | Read proposal feedback/announcements and teaching-team clarifications; confirm SoCLaaS development readiness and cap; record required plan changes | Li Hao checks provider; Yao Xiang checks feedback; all review |
| By Oct 18 | Confirm final evaluation model eligibility/access, qualification pilot, execution budget, and frozen protocol before held-out runs | Yao Xiang coordinates; Li Hao checks provider; Yong Qing freezes manifests |
| Oct 30 | Core freeze, audited experiment records, complete report draft, presentation/demo, contribution records | All three |
| Nov 2–6 | Cross-review report, verify claims/citations and format, conduct full timed rehearsal; confirm presentation/video arrangements and exact Canvas times | Li Hao assembles; all review; Yao Xiang checks Canvas |
| Week of Nov 9 | Present or submit the required recording/materials according to Canvas instructions; verify successful delivery | All present; Yao Xiang coordinates |
| By Nov 12 | Final report audit: <=10-page body, font/margins, references, private title-page identifiers, member contributions, AI disclosure; target early upload | Li Hao assembles; Yong Qing checks evidence; Yao Xiang uploads |
| Nov 13 | Confirm final report submission before the published Canvas cutoff and preserve receipt; resolve upload issues before the cutoff | Yao Xiang; another member verifies |

These are planned actions, not completed submissions or claimed instructor approval. Keep exact submission times and any changed requirements from Canvas in the decision log; do not infer them from the dates alone.
