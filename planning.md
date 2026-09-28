# Four-week project plan

## 1. Authority, status, and completion target

This is the working implementation and evaluation plan for Group 23's **AI Assistant for Dynamic Constraint-Aware Scheduling: Direct LLM Reasoning vs Constraint-Solver-Augmented Reasoning**. It elaborates the supplied proposal; proposed design decisions below are not experimental findings.

- Setup and contract agreement: **28 September–4 October 2026**.
- Four implementation weeks: **5–30 October 2026**.
- Completion target: **Friday 30 October 2026**, in the user-specified Week 11 window of 26–30 October.
- Course presentation: week of **9 November 2026**, normally 15 minutes plus 5 minutes of questions; a recording may be requested.
- Course final report: **13 November 2026**.
- The Week 11 target includes implementation, evaluated results, a complete report draft, and presentation/demo material. The remaining course window is for review and required submission adjustments, not planned core development.
- Current repository status: documentation/configuration bootstrap only. All implementation and research gates below remain open until supported by evidence.

The course project carries 25% of the course grade. The mandatory proposal is ungraded. The final report is at most 10 single-spaced, single-column pages, excluding title/references, with 1-inch margins and at least 11-point font. Figures, tables, and substantive discussion count toward the limit. Contributions, responsible AI, source attribution, and disclosure of AI assistance are required. Check Canvas for subsequent instructor changes before submission.

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
- A second verified model, or a second initial-schedule policy sensitivity check.
- A small visualization/demo interface.
- Participant assignment, multi-capacity resources, new/cancelled tasks, longer horizons, and repeated disruption sequences.

Live calendars, account integrations, RAG, autonomous calendar edits, mobile applications, model training, and production deployment are outside the four-week core. Do not add them as implicit dependencies.

Generation-only is the proposal's fallback. Taking it requires an explicit team decision and a documented scope reduction; it does not satisfy the original generation-and-repair completion claim.

## 4. Team ownership and balanced effort

Working assumption: **8–10 hours per member per week**, approximately 32–40 hours each for implementation, with lightweight setup beforehand. Confirm availability at kickoff and rebalance at each weekly review. These are planning estimates, not records of work performed.

| Member | Branch | Primary deliverables | Approximate total effort |
| --- | --- | --- | --- |
| Tea Li Hao | `lihao-formal-core` | Shared schema implementation; CSP/COP formulation; CP-SAT compiler; generation/repair solver; reference labels; tiny-case exhaustive cross-checks | 24h technical + 6h review/analysis + 6h writing/demo |
| Tham Yao Xiang, leader | `yaoxiang-llm-pipelines` | SoCLaaS adapter; direct scheduling; NL-to-specification extraction; prompts; provider/pipeline tests; integration support | 20h technical + 4h coordination + 6h review/analysis + 6h writing/demo |
| Woo Yong Qing | `yongqing-evaluation` | Synthetic generator/rendering; independent validator; runner; metrics; result tables/figures | 24h technical + 6h review/analysis + 6h writing/demo |

The independent validator moves from Li Hao's proposed sole implementation responsibility to Yong Qing, with Li Hao reviewing the mathematical rules. This balances the implementation load and reduces shared solver/validator bugs. All members approve the rules and own the overall result.

Review rotation: Li Hao reviews LLM extraction semantics; Yao Xiang reviews runner/provider boundaries and benchmark wording; Yong Qing reviews solver behavior against independently enumerated cases. Any member may flag a correctness problem outside their ownership.

Report ownership: Li Hao drafts formulation and solver methodology; Yao Xiang drafts motivation, related work, pipeline method, and AI-assistance disclosure; Yong Qing drafts benchmark and results. All jointly write discussion, limitations, responsible AI, and conclusion, and rehearse questions about the entire system.

### File ownership once implementation starts

| Area | Lead | Review/coordination |
| --- | --- | --- |
| `src/scheduling/schema.py`, `solver.py`, `objectives.py` | Li Hao | Other two approve contract changes |
| `src/scheduling/providers/`, `pipelines/`, `prompts/` | Yao Xiang | Li Hao checks extracted semantics |
| `src/scheduling/validation.py`, `benchmarks/`, `evaluation/` | Yong Qing | Li Hao cross-checks validity rules |
| Corresponding component tests | Component owner | Rotating reviewer |
| `pyproject.toml`, lockfile, CI, shared CLI, README | Yao Xiang integrates | Owners request changes; avoid competing edits |
| `planning.md`, `AGENTS.md` | Team agrees; one editor at a time | Record material decisions below |

No implementation directories are promised to exist at bootstrap. Keep a small Python package; avoid unnecessary service/framework layers.

## 5. Parallel start and dependency management

**Day 1–2: 28–29 September.** Agree the version-1 contract below and at least six tiny fixtures: simple SAT, overlap, shared resource, precedence/deadline interaction, proven UNSAT, and repair. Li Hao owns the schema PR; all review it. Each person can start immediately:

- Li Hao: formal definitions and tiny enumerated solver cases.
- Yao Xiang: provider capability checks, canned response parsing, and prompts against the draft JSON contract.
- Yong Qing: hand-written gold fixtures, independent schedule checks, and renderer/runner design using canned pipeline outputs.

Mocks/canned outputs unblock interface work but never count as live-model research evidence. Merge the shared contract first, then merge small component increments every 1–2 days. Do not wait until the end of a week to integrate three large branches.

If a contract change is needed, record its motivation, affected consumers, migration, and schema version; coordinate before editing shared files. Never copy divergent schemas into separate components.

## 6. Version-1 shared contract

This section is a proposed implementation contract to freeze by 29 September. Field names can change during that review, but all consumers must change together.

### Gold problem and natural-language view

`ProblemSpec`: `schema_version`, `instance_id`, `task_type` (`generation` or `repair`), `horizon_slots`, `slot_minutes` (30), participant IDs, resource IDs, activities, and constraints. Activity records contain unique stable IDs, positive integer `duration_slots`, participant/resource IDs, and one or more availability windows. Constraints/preferences have stable IDs and typed operands; unknown types and dangling IDs are errors.

- Slot zero is the explicitly stated horizon start. No implicit current date or timezone.
- Intervals are half-open `[start,end)`. Adjacent activities are permitted.
- An activity must fit completely within an allowed window, not span the gap between two windows.
- Mandatory activity IDs must occur exactly once in a schedule. Missing, duplicate, and invented activities are invalid.
- Release times, deadlines, fixed starts, precedence, and blocked intervals have explicit semantics. No inferred travel/rest constraints unless stated.
- Resources and participants cannot be double-booked. Multiple required participants must all be available for the full interval.
- A preferred start window uses explicit inclusive lower/exclusive upper start bounds and an integer penalty weight. Generation minimizes the sum of violated-preference weights.
- Repair additionally carries a gold-valid original schedule, an event description, and a fully updated problem. Both systems receive identical original schedules and updated information.

`NaturalLanguageView` contains the user-visible text, variant ID, base-instance ID, and, for repair, the common original schedule. Evaluated pipelines receive this view and the public output/schema instructions. They do not receive gold constraints, oracle solutions, hidden labels, or expected objective values.

### Output and outcomes

`Schedule`: a list of activity IDs and integer start slots. End times are computed from fixed durations. Claimed textual times must be normalized without guessing or rounding invalid inputs.

`PipelineResult`: `instance_id`, `variant_id`, `approach`, `status`, optional schedule, optional extracted specification, diagnostics, timings, and usage. Pipeline status is one of `SAT`, `UNSAT`, `UNKNOWN`, `INVALID_OUTPUT`, or `ERROR`. A SAT claim requires a complete schedule; an UNSAT claim from a direct LLM is a prediction, not a proof.

Preserve the underlying solver status separately: `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `UNKNOWN`, or `MODEL_INVALID`. Also store objective value, best bound where available, time limit, elapsed time, and whether each lexicographic stage was proven optimal. Never report a feasible incumbent as a proven optimum, or a timeout as UNSAT.

`ValidationResult`: structural validity, hard-feasible flag, violations with constraint IDs, objective components recomputed from gold, and repair distance. The validator consumes a schedule and gold specification; it must not call CP-SAT or reuse the solver's constraint-building implementation.

### Proposed Python interfaces

```python
solve(spec, limits) -> SolveResult
validate_schedule(gold_spec, schedule) -> ValidationResult
run_direct(nl_view, model_config) -> PipelineResult
run_solver_augmented(nl_view, model_config, solver_limits) -> PipelineResult
evaluate(instance, pipeline_result, gold_reference) -> EvaluationRecord
```

Use explicit typed models and deterministic serialization. Validate generated JSON before compilation. Do not execute model-generated code. Schema-valid JSON is not proof of semantic correctness.

## 7. Formalization and repair objective

For each activity i, choose an integer start s_i and define end e_i = s_i + duration_i. Require allowed-window containment, e_i <= deadline_i, and s_i >= release_i where specified. A precedence i→j imposes e_i <= s_j. Shared participants/resources impose e_i <= s_j OR e_j <= s_i. Fixed appointments impose equality on start.

Generation: satisfy all hard constraints and minimize the stated preference penalty.

Repair: satisfy the updated hard constraints and lexicographically minimize:

1. `moved_count = sum(start_i != old_start_i)` over retained activities;
2. `total_shift_slots = sum(abs(start_i - old_start_i))`;
3. preference penalty.

Use sequential optimization or a proven equivalent bounded encoding. For sequential optimization, only freeze a prior objective value as optimal after that stage has been proven optimal. Otherwise retain the feasible incumbent and explicitly mark optimality as unproven. Hard constraints are never converted into soft penalties.

Document the initial-schedule policy (initially a deterministic feasible schedule from the gold solver) and give both approaches exactly that schedule. Report that this choice may favor some repair patterns. New/cancelled activities are excluded from v1; if later added, define retained-task distance and mandatory-presence semantics first.

Changing weights or objective priority changes the question being studied and requires a new experiment configuration. Keep raw moved count and total shift even when reporting the lexicographic optimum.

## 8. Benchmark and evaluation design

### Construction and splits

- Development: approximately 20–30 manually checked cases. Cover boundaries, each constraint type, interactions, and known failure modes.
- Provisional main target: 120 generation + 120 repair base instances. Adjust after the pilot based on measured cost/runtime, and freeze the final count before inspecting test results.
- Add 12 human-written realistic scenarios, balanced across personal/shared settings and generation/repair. These assess plausibility; do not claim population representativeness.
- Select 24 base instances for two additional equivalent language variants each: paraphrase and constraint reordering. This yields a provisional total of 300 input renderings (240 + 12 + 48).
- Both core approaches use each rendering: 600 model calls per complete single-model, single-attempt pass. Repeats, pilot calls, feedback, and extra models are additional. This arithmetic is a planning estimate, not a budget authorization.
- Group all variants and related generation/repair scenarios from a common base in the same split. Keep prompt examples and tuning cases out of the held-out test set.

Generate feasible instances with a known witness. Establish UNSAT with the gold solver, including interacting contradictions rather than only obvious single-rule failures. Discard or relabel unresolved reference cases; do not silently assign a binary truth label to UNKNOWN. Record selection/exclusion counts and reasons.

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

Confidence intervals and paired comparisons should group by base instance; paraphrases are not independent samples. Report the sample sizes and uncertainty. Do not pool results from changed model/backend configurations without identifying the change.

### Fair comparison and error attribution

Use the same verified model ID, prompt information, reasoning settings where supported, and predeclared per-call output budget for A and B. Record prompt lengths and token usage because output tasks differ. One model attempt per approach is the core condition; transport retries are bounded, recorded, and distinct from semantic corrections. Neither path gets hidden gold feedback.

Gold-to-Solver isolates the reference/modeling layer. Compare B's extracted specification to gold and validate B's final schedule against gold. A correct output despite an extraction mistake remains an end-to-end success but an extraction failure. If the gold solver or independent validator fails cross-checks, fix the infrastructure before interpreting model results.

Preserve malformed outputs and failures with appropriate redaction. Never hand-repair a test response or keep only successful retries. An optional feedback experiment must state whether feedback uses gold constraints or only the model's extracted specification; those are different information settings.

## 9. NUS SoCLaaS and execution budget

- Base URL: `https://soclaas-api.comp.nus.edu.sg/v1`.
- Environment names: `SOCLAAS_BASE_URL`, `SOCLAAS_API_KEY`, `SOCLAAS_MODEL`.
- `default` is the supplied bootstrap model alias. Query `/models`, inspect available model IDs, and choose a verified ID before pilot/freeze. If only an alias is available, record it, the returned model identity, run time, and the resulting reproducibility limitation.
- The supplied setup describes an OpenAI-compatible client. Verify completion endpoint, model access, output parsing, supported structured-output/reasoning parameters, quota, and rate limits; do not assume feature parity with another provider.
- Adapter must have explicit connect/read timeouts, bounded retries for transient errors, sanitized errors, and per-attempt accounting. Start with sequential requests; increase concurrency only within verified provider limits.
- Credentials stay in a local ignored `.env` or process environment. Each member supplies an authorized credential. Do not distribute the project owner's key through Git or team documents. Rotate any key shared through chat/screenshots.
- Validate authentication with a model listing and one small non-sensitive completion before scheduling experiments. These are connectivity checks, not research results.
- Before bulk execution, run a small pilot and estimate request/token cost and runtime. Set a maximum requests/tokens or currency cap, concurrency cap, and stop conditions. Obtain the project owner's explicit budget authorization; course reimbursement is not an execution budget.
- The supplied course guidance allows a group claim up to $100 under its receipt rules. SoCLaaS accounting may differ; confirm institutional quota/cost rather than assuming it is free or reimbursable.

Store model ID, returned backend identity if available, prompt/config hashes, benchmark version/hash, code commit, dependency versions, solver parameters/seed/workers, host/CPU context, timestamps, and usage coverage in each run manifest. Keep raw responses local/private by default; publish reviewed synthetic fixtures, manifests without secrets, and aggregate results needed for reproducibility.

### Bootstrap connectivity evidence — 28 September 2026

An authenticated model listing and one non-sensitive chat completion returned HTTP 200. The `default` alias returned model ID `qwen3.6:35b`; the response was exactly the requested short acknowledgement, with 17 prompt and 2 completion tokens reported. This is connectivity evidence only. Structured-output support, rate limits, quota/cost, model suitability for the course requirement, and scheduling performance remain unverified. The local credential is ignored by Git and restricted to its owner; no secret is stored in this document.

## 10. Four-week delivery schedule

| Week | Li Hao | Yao Xiang | Yong Qing | Shared gate |
| --- | --- | --- | --- | --- |
| **1: Oct 5–11** | Schema, formal rules, basic SAT/UNSAT solver, exhaustive tiny cases | SoCLaaS smoke check, adapter and canned parsing tests, first A/B prompts | Gold fixtures, independent validator, renderer, runner using canned outputs | Contract frozen during setup (target Sep 29); one generation and one repair example through both live paths by Oct 11, or an explicit provider blocker |
| **2: Oct 12–18** | Complete supported constraints, preferences, lexicographic repair, solver diagnostics | Robust structured parsing, both pipelines, extraction diagnostics, bounded error handling | Generator/splits, reference labelling, metrics, pilot automation | Core feature complete; development suite passes; pilot completed; benchmark/prompts/model/budget frozen |
| **3: Oct 19–25** | Reference audit, optimality/bounds checks, solver failure analysis | Execute assigned model runs, audit extraction failures, record provider drift | Execute remaining runs, aggregate records, paired analysis and figures | Planned runs complete or explicitly accounted for; provenance and denominators audited |
| **4: Oct 26–30** | Formulation/method draft, independent rerun of selected cases | Related work/pipeline draft, integration/demo, coordination | Benchmark/results draft, reproducibility rerun and figures | Complete report draft within limit; presentation and demo; all members can explain findings; core frozen Oct 30 |

Two brief team checkpoints each week: progress/blockers and integration/review. Leadership is coordination, not sole responsibility for integration. Rebalance workload based on remaining tasks, not only the original titles. Use a shared decision log for scope/API changes; record actual contributions as work occurs.

## 11. Verification and acceptance gates

### Gate A — contract and trustworthy reference

- Shared schemas reject unsupported constraints, invalid endpoints, duplicates, and missing references.
- Tiny hand-checked and exhaustively enumerated cases agree with CP-SAT on feasibility and objective values.
- Independent validator catches deliberate mutations: overlaps, missed deadlines, dropped/extra tasks, resource conflicts, and wrong repair accounting.
- No-op repair preserves a valid original schedule with zero movement when objectives permit; disruption cases have checked optimal repair distances.

### Gate B — integrated core

- Both generation and repair work through A and B with recorded live-provider evidence.
- Provider errors, invalid JSON, valid-but-wrong extraction, model UNSAT predictions, and solver UNKNOWN remain distinguishable.
- Dependency versions are locked, relevant tests pass, and installation/demo commands are verified from a fresh environment.
- Model, prompts, seeds, fixtures, metrics, and execution caps are frozen before the main test set is run.

### Gate C — defensible results

- Every planned attempt has a record, or an explicit exclusion/failure reason.
- Gold labels/objective proof status and all reported denominators are checked.
- Analysis includes difficulty, repair, language robustness, extraction failures, uncertainty, and limits of realism.
- A teammate independently reproduces representative results from saved manifests without accessing secrets.

### Gate D — four-week completion

- Complete report draft and presentation/demo with no fabricated or unverified claims.
- Responsible AI analysis includes concrete cases/measurements and objective trade-offs.
- Actual member contributions and AI assistance disclosed; every member understands the whole pipeline.
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
| SoCLaaS access/model is unsuitable for course frontier-model requirement | Record model identity, discuss suitability with the instructor; do not label an unverified model frontier or silently switch providers |
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

## 15. Decision log and next actions

| Date | Decision | Status / follow-up |
| --- | --- | --- |
| 2026-09-28 | Complete core by Week 11, Oct 26–30; target Oct 30 | User clarified timeline; setup Sep 28–Oct 4 and four implementation weeks Oct 5–30; course deadlines remain unchanged |
| 2026-09-28 | Use NUS SoCLaaS and local secret configuration | User selected provider; model/budget suitability to be verified |
| 2026-09-28 | Three owned workstreams with an independently implemented validator | Working allocation; confirm availability at kickoff |
| 2026-09-28 | Single-day fixed-duration v1 and lexicographic repair | Proposed contract; freeze with team by Sep 29 |

Next actions: each member reads these documents; confirm available hours; freeze schema/fixtures and objective priorities; choose a verified model and pilot budget; implement Gate A and the provider adapter in parallel. Record subsequent material decisions here without overwriting prior experiment configurations.

## 16. Source grounding

- Group 23 proposal, supplied 28 September 2026: problem, two approaches, repair, metrics, team, and original milestones. This plan accelerates completion and redistributes validator implementation explicitly.
- CS3263 Project.pdf and CS3263-Project-Guidelines 2627.docx: course comparison requirement, deliverables, evaluation, responsible AI, team contributions, and AI-assistance disclosure.
- ResponsibleAI.pptx: privacy, fairness/trade-offs, transparency, adversarial behavior, unintended effects, and human control.
- [SCHEDBench](https://arxiv.org/abs/2608.00991): scheduling under equivalent language forms.
- [NATURAL PLAN](https://arxiv.org/abs/2406.04520): natural-language planning and complexity.
- [Hao et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.176/): formal-tool-assisted planning and verification.
- [CP-SAT](https://developers.google.com/optimization/cp/cp_solver): integer modeling and distinct solver statuses.
- [SoCLaaS](https://dochub.comp.nus.edu.sg/cf/guides/soclaas/start) and the user-supplied setup screen: connection configuration. Institutional documentation access and actual provider capability are separate checks.
