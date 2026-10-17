# Development and submission plan

## 1. Authority, current status and delivery target

This is the active plan for Group 23's **Direct LLM versus LLM-to-CP-SAT dynamic scheduling study**. The core implementation, balanced and difficulty model comparisons, historical Qwen studies, offline replay and result figures are complete. The current deliverable is a reviewed report and reproducible repository based on that evidence. Do not restart delivered components from historical member plans.

The current report makes **balanced controlled generation the core**: 48 cases, 24 SAT/24 UNSAT, and 96 scheduling attempts each for Qwen3.6 and GLM. Both campaigns completed on 15 October 2026 and preserve every outcome. This focused follow-up corrects the constraint-presence/label association found in the earlier difficulty dataset; it does not replace or rescore those observations. Repair is a completed bounded extension; fictional and wording comparisons remain supplementary. The separate 200-attempt difficulty pair and original 600-attempt Qwen3.6/Qwen3.8 studies, graphs and historical reports remain preserved. Known synthetic/AI-assisted inputs do not become held out. See [the balanced audit](docs/balanced-comparison-audit.md) and [difficulty audit](docs/difficulty-comparison-audit.md).

This checkpoint integrates the consultation improvements, balanced results and report/evidence updates for publication. [Publication verification](docs/publication-verification.md) records the actual validation and Git state. Automated verification does not establish member contributions, human interpretation or course acceptance. Keep the contribution disclosure interim until factual accounts are supplied. The earlier detailed plan is preserved in [development-plan-history.md](docs/development-plan-history.md).

| Authority | Requirement or decision |
| --- | --- |
| Course | Course-related formal problem; direct/model-to-tool comparison; evidence and analysis; responsible AI; actual contributions and AI disclosure; prescribed report/presentation format |
| Proposal | Schedule generation and minimum-disruption repair; controlled difficulty, realistic scenarios and equivalent wording; feasibility, solution quality, extraction and resources |
| Team scientific choices | Single day, 30-minute slots, fixed assignments, lexicographic repair, paired comparison, independent gold checking, immutable evidence |
| Received written TA feedback | Clear research question/course connection/evaluation and strong responsible AI; breadth is the risk. Prioritize controlled generation, both approaches and validator; repair minor, feedback/UI bonus |
| Current report scope | Balanced 48-case controlled generation; earlier 30-case difficulty-generation view and completed extensions retained separately; synthetic/AI-assisted development inputs, no holdout or production claim |
| Completed evaluation datasets | Balanced generation: 48 cases × two methods = 96 attempts/model. Difficulty: 100 case/rendering conditions × two methods = 200 attempts/model. Historical Qwen: 600 attempts/model. No pooling across designs |
| Conditional future study | Fresh instance holdout, independently human-authored scenarios, additional models/repeats or pinned backend only with an explicit rationale and authorization |
| Routine engineering | Choose compatible helpers, paths, packaging and focused checks autonomously; do not change scientific semantics silently |

**Course evidence and model choice:** the completed balanced and difficulty pairs use `qwen3.6:35b` and requested alias `x-test-1` with required response `glm-5.3-flash`. The historical pair remains Qwen3.6/Qwen3.8. A full Qwen3.8 difficulty run has not been performed. Do not infer teaching-team approval from API success: resolve the handout's frontier-model wording using actual feedback. Further models or inference are optional and require separate authorization.

### Consultation interpretation

The written feedback supplied by the team confirms a clear research question, strong CSP/CP-SAT connection, careful gold/validator evaluation and strong responsible AI. Its concern is breadth and timely completion, not a rejection of the topic. Keep controlled generation, the fair comparison and the validator as the core. Repair is a minor extension; verifier-feedback correction and UI are bonus work. Earlier screenshot rating alternatives were not a selected assessment and must not be represented as negative grades.

The TA suggested a Monday-to-Friday 09:00–17:00 hourly scenario with two participants, one room and eight 1–2-hour activities. Our existing contract is one day on a 30-minute grid. The new [offline office examples](docs/ta-feedback-alignment.md) concretely cover eight activities, two people, one room, fixed appointments, availability, deadlines, non-overlap and a morning preference. They demonstrate loose SAT, tight SAT, certified UNSAT and a one-move repair. They do **not** implement a weekly/hourly calendar. Consecutive-meeting penalties and day clustering are not supported preference types. These are explicit simplifications to confirm under S1, not claimed TA approval or silently added course requirements.

The complete model comparison is already executed. Reframe the analysis instead of adding more models, harder tasks, weekly semantics or feedback loops. Preserve all observations, including repair and stronger-model successes. The generation focus and small-case view are post-run reporting decisions, not preregistration. AI assistance remains disclosed; actual member interpretation, contributions and understanding remain necessary.

| Milestone | Date / evidence |
| --- | --- |
| Proposal | Course deadline 28 September 2026; actual private receipt/feedback must be confirmed |
| Repository and report preparation | Current publication; complete scientific draft, preserved evidence and repeatable checks |
| Complete reviewed draft | Internal target 30 October 2026, Week 11 |
| Presentation | Week of 9 November; 15 minutes plus five minutes Q&A, or recording if requested |
| Report | Course deadline 13 November; verify exact Canvas cutoff and upload receipt |

The earlier 18 October freeze was an internal target for the conditional fresh study. It is not a course deadline. Report format: at most **10 single-column, single-spaced body pages**, at least 11-point type, one-inch margins; title/references excluded, all substantive figures/tables included. Keep names, matriculation numbers and emails on the private submitted title page; public Git omits the private identifiers.

## 2. Research questions and supported conclusions

1. **Core:** how do direct LLM and LLM-to-CP-SAT compare on controlled schedule generation, including loose feasibility and joint contradictions?
2. How do interpretation, hard validity, optimality and service failures contribute separately to end-to-end results?
3. **Repair extension:** how well do both methods repair the same starting schedule under the declared priorities?
4. **Robustness extension:** what changes under equivalent wording, conditional on matched canonical partners?

The contribution is the integrated formulation, implementation and transparent comparison, not a new solver algorithm. Strong direct performance is informative: the report must explain it rather than introduce tasks or scoring changes to force a solver win. No grade is guaranteed by accuracy, test count or extra features.

## 3. Maintained scope

Mandatory fixed-duration non-preemptive activities use fixed participants and capacity-one resources on a single-day grid. Hard constraints cover full-window availability, release/deadline, fixed appointments, precedence and non-overlap. Generation minimizes preference penalty; repair minimizes moved activities, total shift, then preferences. Preserve the schema's exact interval and preference semantics.

Both pipelines, independent validator, gold references, bounded extraction diagnostics, explanations, dashboard, durable request accounting, failure continuation, supervised execution, frozen controls and offline replay are implemented. Multi-day scheduling, changing assignments, live calendars, RAG, training, arbitrary provider integration and automatic calendar actions are out of scope. Verifier feedback and additional optimizations remain optional follow-up studies, not missing submission features.

## 4. Collaboration and repository responsibilities

The baseline job split is complete. Members coordinate the next concrete deliverable rather than repeating their original streams. Existing branches are `lihao-llm-baseline`, `yaoxiang-formal-core` and `yongqing-evaluation`; shared integration is `main`. Do not use `codex/` for new project branches. Explicit user authorization may allow a direct main publication; otherwise use reviewed PRs.

| Concern | Coordination |
| --- | --- |
| Provider, packaging, CLI and operational run controls | Li Hao |
| Schema, compiler, repair objectives, extraction and mathematical proof boundaries | Yao Xiang |
| Benchmarks, independent evaluation, statistics and replay | Yong Qing |
| Scientific interpretation, responsible AI, report, presentation and whole-system understanding | All members; actual actions recorded individually |

These contacts do not prove authorship or completed human review. An authorized integrator may fix cross-component issues. Read [AGENTS.md](AGENTS.md), preserve existing changes and avoid simultaneous edits to shared files.

Directory roles: `src/scheduling/` contains the single package; `evaluation/` thin experiment entry points; `tests/` independent fixtures/regressions; `benchmarks/`, `configs/`, `prompts/` versioned inputs; `results/` summaries/figures/approved archives; `docs/` scientific report, methods, usage and handoffs; `presentation/` demo/rehearsal preparation. `runs/` and private credentials remain ignored. Historical archive paths may retain the old `report/` spelling.

## 5. Current task queue and acceptance evidence

### Completed difficulty study and focused follow-through: D1-D5

**D1 — Offline dataset and execution preparation.** Use [difficulty-study.md](docs/difficulty-study.md) and `benchmarks/fixtures/difficulty-v1/`. Five tiers contain 4/8/12/20/32 activities. Sixty controlled cases cover resource bottlenecks, precedence/deadline interactions and coupled repair; twenty separate fictional cases mix the supported requests. Ten controlled bases receive clock-time paraphrase and reordered variants, adding twenty conditions. There are 80 unique cases from 40 construction families, which normalize to 39 distinct hard-structure groups, not 100 independent problems. Generation/repair and SAT/UNSAT are balanced in every canonical tier. Independent SAT/UNSAT construction checks, proven reference optima, structural-family normalization, source/input hashes and exact preflights make the packet reviewable. Human wording/gold interpretation remains pending.

**D2 — Completed Qwen3.6 and GLM execution.** Both 200-attempt runs finished and replay exactly; see the comparison audit. Preserve their consumed allowances and exact returned identities. For any separately authorized future run, prepare fresh `difficulty-campaign-1` packets with the same cases, revision-3 prompts, 32,768 output-token ceiling, 30/1,800-second connect/read limits, no retries, 30-second B solver and 60-second reference solver. Per model: 120 controlled + 40 fictional + 40 wording calls, two capabilities and one metadata request; 203 HTTP requests and 6,619,136 reserved output tokens, with input tokens additional. Both models together mean 400 scheduling attempts. Keep strict returned-model checks and observe shared-service fingerprints. Record transient errors and continue to later distinct attempts. Preparation does not start inference or consume a new live allowance.

**D3 — Completed automated difficulty analysis and report draft; human interpretation pending.** The difficulty audit and report contain block/tier/failure/resource comparisons and concrete extraction counterexamples. For ongoing review: Report model/method by block, tier, task, label and mechanism, with denominators. Keep primary acceptance failure-inclusive; explain constraint violations, false UNSAT, malformed output, extraction changes, suboptimal repairs, solver limits and provider failures separately. Compare complete pipeline time, model/solver components and token coverage. Match wording to its own canonical partners. Show trace-backed failures and successful hard cases. Each controlled tier contains six cases per method/task and three SAT cases; finer cells are descriptive, not precise population estimates. Tier names do not prove monotone difficulty. Preserve near-perfect and nonmonotone outcomes; do not select only A failures or call inspected data held out. Human interpretation is substantive project work.

Acceptance: versioned dataset files, every reference resolved, independent certificates checked, no empty unary domains in UNSAT cases, exact 200-attempt preflights for both models, full mocked execution/replay/export including continued transient failures, and unchanged original evidence hashes. A separate 24-attempt live smoke passed the complete pipeline with model mistakes retained as scored failures. All three blocks finished for Qwen3.6 and GLM; both 200-attempt analyses reproduce exactly from verified archives. Do not pool smoke outcomes into those runs. Section 8 distinguishes the two datasets.

**Consultation follow-through in the implementation.** D1 includes an executable reviewer-only packet (`prepare_case_review.py --source-mode difficulty-v1`) with fresh checks of all 80 gold references and separate pending checks for gold meaning and rendered facts. D3 includes automatic block/tier/fine-cell outcomes, tier resource distributions with usage coverage, paired observations, grouped tier charts and a trace-backed casebook from `export_study`. Every issue remains represented alongside deterministic success examples; structural differences are observations, not automatic causal explanations. These analysis tools support the TA's request for thinking beyond accuracy without changing the solver, scoring rules, prompts, dataset or existing results. Measured execution and trace-backed automated interpretation are complete; actual human review and members' own scientific interpretation remain open. See [the study guide](docs/difficulty-study.md) for commands and output definitions.

### D4. Focused response to the written TA feedback

**Implemented.** `scripts/build_generation_focus.py` verifies the unchanged archives and exports all controlled generation observations, a size-defined small-case view, harder generation, repair, fictional and wording scopes with exact observation IDs. `scripts/render_generation_focus.py` creates separate generation charts without replacing earlier figures. The derived view emphasizes generation and retains every extension/failure in the difficulty comparison audit; the report now leads with the later balanced study. `evaluation/ta_scope_examples.py` builds and independently checks a small office illustration using the existing solver and validator; its output is labelled offline evidence with zero model calls.

| View | Per method/model | Interpretation |
| --- | ---: | --- |
| Earlier difficulty-generation view | 30 cases: 15 SAT, 15 UNSAT | Complete controlled generation set; 29 normalized structures |
| Small-case entry view | 12 of those cases: 4/8 activities | Six SAT/six UNSAT; subset chosen by construction size, not results |
| Larger generation | Remaining 18: 12/20/32 activities | Descriptive stress analysis; all successes/failures retained |
| Repair extension | 30 controlled cases | Minimum disruption with separate conditional objective analysis |
| Fictional / wording extensions | 20 / 20 conditions, each including generation and repair | Separate denominators and matched wording limitations |
| Office illustration | Four offline cases, no model evaluation | Loose/tight SAT, capacity UNSAT, minimal repair; eight activities/two people/one room |

**Acceptance evidence.** [Generation summary](results/summary/generation-focus-20261015.json), [office verification](results/summary/ta-scope-examples-20261015.json), new generation chart receipts, focused regressions and report checks. Gold-SAT/UNSAT denominators, provider failures, conditional optimum matching and human-review limits remain explicit. The office repair moves A3 by two 30-minute start slots and preserves seven activities; four changed occupancy cells is a separate illustrative statistic, not the study's shift metric.

**Size cap and stopping point.** D5 below qualifies the scientific coverage of these completed runs; runtime completion is not a claim of broad benchmark representativeness. This earlier view has 30 generation cases/model within the 200-attempt comparison, two models and at most 32 activities. D5 provides the completed 48-case balanced core. Data/solver/pipeline work and the separate derived views are complete. Stop adding data, models and runtime features; proceed to S1-S7. Keep the executed 30-case repair extension without more repair scenarios or correction rounds. Verifier feedback, additional preference types, weekly scheduling, new UI and live studies are deferred unless actual course clarification or a demonstrated defect makes a separately agreed change necessary. Scope reduction changes presentation and future commitments, not recorded scientific results.

### D5. Resolve the measured constraint-type/label confound

**Audited weakness in the earlier dataset.** In the executed 30-case difficulty-generation core, all 15 SAT cases omit explicit deadlines and fixed starts; all 15 UNSAT cases include one of those types. The same constructor pattern occurs in repair and fictional cases. This is a potential label shortcut, not proof that a model used it. Recorded scores, invalid-schedule examples and extraction counterexamples remain valid, but the live dataset does not establish feasible deadline/appointment handling. [The coverage receipt](results/summary/generation-constraint-coverage-20261015.json) and [code/course audit](docs/course-code-audit.md) record the exact evidence. The report now discloses it.

**Implemented correction.** The user selected this focused follow-up. [`balanced-generation-v1`](docs/balanced-generation.md) has 48 generation cases (24 SAT / 24 UNSAT): three interaction mechanisms × two numeric layouts × four deadline/fixed-start profiles × two labels. Each profile contains six SAT and six UNSAT cases. Matched pairs retain identical assignments, durations, constraints and rendering style; numeric availability changes feasibility. All cases have eight 1–2-hour activities, two participants and one room, on 26 October 2026 09:00–17:00 with 30-minute slots. This preserves the existing schema and does not implement weekly scheduling.

**Correctness and meaning.** The new dataset includes independent SAT witnesses, arithmetic capacity/precedence UNSAT certificates, nonempty unary domains, separately proved CP-SAT references, and counterexamples establishing that deadlines/fixed starts actually restrict feasible schedules. The design gate checks matching constraint types/counts and complete dated public prose. All related variants remain in three conservative construction families: neither 48 independent samples nor a new seed implies independent held-out evidence. Human wording/gold interpretation remains pending. The old fixtures, traces, failures and scores are immutable.

**Capped execution contract.** Canonical generation only: 96 scheduling attempts per model, two capability completions and one metadata request, or 99 total requests and 3,211,264 reserved output tokens per model (input tokens additional). Qwen requests/returns `qwen3.6:35b`; GLM requests `x-test-1` and must return `glm-5.3-flash`. Both use the same cases/prompts/settings, 32,768 output tokens per completion, 30/1,800-second connect/read timeouts, zero retries, 30/60-second method/reference solver budgets, observed backend variation and the existing transient-failure continuation policy. Fatal identity/authentication/TLS/integrity/quota/budget failures still stop. Both campaigns completed the authorized 99 requests without retries. The allowances are consumed; this plan does not authorize further calls.

**Completed empirical confirmation.** Qwen direct accepted **6/48 (12.5%)**, versus **48/48** with CP-SAT. Its 42 failures comprise 23 hard-constraint violations, nine false UNSAT answers and ten strict JSON-format failures. The latter category is output-contract failure, not automatically incorrect scheduling reasoning. GLM direct accepted **47/48 (97.9%)**, versus **48/48** with CP-SAT. Its single failure was a `remote_protocol_error` after 34.18 seconds, not the 1,800-second timeout; it produced no usable response or returned model identity. Both GLM capability checks and all 95 returned scheduling responses matched `glm-5.3-flash`. The secondary 47/47 acceptance among returned direct answers must not replace the failure-inclusive denominator or turn a service failure into a reasoning claim.

**Acceptance and stopping point.** [The protocol](docs/balanced-generation.md), [comparison audit](docs/balanced-comparison-audit.md), [summary](results/summary/balanced-comparison-20261017.json) and [archive manifest](results/balanced-evidence-manifest.json) record construction, complete outcomes and reproducible evidence. The prior [engineering verification](results/summary/balanced-generation-verification-20261015.json) records 900 passing regression tests and a checked noneditable installation; mocked outputs remain engineering evidence only. D5 implementation and bounded execution are complete. Remaining work is genuine prose/gold review and interpretation under S3, then S4 delivery; a completed run does not establish that human review. Preserve old results and the earlier confound, and retain the three-family/generalization limit of the new data. Do not add repair cases, harder tiers, new models, feedback loops or weekly semantics merely to close this task.

### Delivered and preserved

- R1-R4 formal invariants, extraction contract, bounded constraint diagnostics and evidence-bound explanations.
- F1 saved-failure regressions; F2 provider metadata/qualification and complete two-model development execution; F3 candidate construction and mathematical checks; F4 supervised multi-block execution; F5 scoring/replay/archive integrity.
- Two historical campaigns, each 480 controlled + 24 realistic + 96 wording attempts; zero retries; preserved failures and two Qwen3.8 pauses.
- Two difficulty campaigns, each 120 controlled + 40 fictional + 40 wording attempts, with matching source/settings/prompts and exact archived-analysis replay.
- Two balanced generation campaigns, each 96 scheduling attempts plus two capability completions and one metadata request, with all failures preserved and returned model identity checked.
- Current report narrative, grouped bar charts, claim index, compressed replay archives and preserved historical reports/evidence.

These are engineering/evidence completions. They do not claim human sign-off, held-out data, teaching-team approval or submission.

### Remaining delivery work

The items below remain **open or unconfirmed**. Human contribution and understanding are substantive course requirements, not administrative sign-offs. Course obligations are distinguished from team review procedures; the handout does not prescribe a review template, hours log, contribution percentage or minimum number of code commits.

| Item | Basis | Completion evidence |
| --- | --- | --- |
| S1. Course scope and model eligibility | Course requirement / unresolved interpretation | Written feedback received; exact single-day/preference simplification and hosted-model eligibility clarified; Canvas arrangements checked |
| S2. Human contribution and AI disclosure | Course, Guidelines P56-60/P87-88 | Factual accounts from all three members, explicit human/AI division in the final report, whole-system understanding |
| S3. Scientific interpretation and technical review | Course P57/P62/P84; team procedure below | Completed D5 findings and limitations understood; reviewed claims/examples, own interpretations and corrections recorded |
| S4. Final report and private submission copy | Course P49/P51/P58/P92 | Reviewed report, actual contributions, private title identifiers, fresh PDF format/visual check |
| S5. Presentation and Q&A | Course P47/P57 | Actual deck or requested recording; team explains the project within 15 minutes plus five-minute Q&A |
| S6. Independent reproduction handoff | Recommended team verification, not a separate course mandate | A teammate's actual clean-environment replay outcome, or a record that this optional check was not performed |
| S7. Final submission | Course P13-14/P51 | Required files uploaded under actual Canvas instructions and private receipts retained |

### S1. Resolve the actual course requirements

- The written TA feedback is now recorded in [the alignment](docs/ta-feedback-alignment.md). Verify its original Canvas record/receipt and current submission arrangements. Confirm that the existing single-day/30-minute simplification and preferred-start-only soft constraints are acceptable relative to the suggested weekly/hourly scenario. Do not claim this exact simplification has already been approved.
- Resolve the frontier-model wording for the current SoCLaaS Qwen3.6/GLM pair and historical Qwen3.8 evidence. The handout suggests considering hosted open-weight models, but API success does not establish eligibility. Use existing written feedback if it resolves this; otherwise a member obtains clarification. Keep private correspondence out of Git.
- If the current study satisfies the intended scope, proceed with S2-S5. If another comparison is required, record that requirement and agree a limited protocol, exact model and new execution budget before any calls. An agent must not commission it automatically.

### S2. Record genuine member work and AI support

Each of Li Hao, Yao Xiang and Yong Qing supplies a concise account of personal design/implementation/analysis/writing, technical decisions and reasons, concrete reviewed artifacts or claims, corrections/findings, and which parts Codex generated, executed or drafted. Leave unknown or unfinished work explicit. Contacts and branch names do not establish authorship.

Record these accounts in [contributions.md](docs/contributions.md), then replace the interim contribution paragraph in the final report with accurate per-member statements and explicit AI support. Retain the current report version until those facts are available. Do not claim manual implementation of generated code, infer equal effort, invent hours or relabel AI-assisted scenarios as human-authored.

Disclosure alone does not satisfy P60's instruction not to delegate all work to an LLM. Each member must actually contribute and understand the project. If substantive interpretation/review has not happened, perform it rather than merely approving generated text. If acceptable AI involvement remains uncertain after an honest account, seek teaching-team clarification. An agent can organize evidence and explain concepts, but cannot attest to another person's contribution or understanding.

### S3. Review scientific claims and explain the findings

Use [claim-evidence.md](docs/claim-evidence.md) to record reviewed cases/claims, reviewer, finding and correction where needed. This is the team's procedure, not a rubric requiring a particular count of sign-offs.

1. **Formal correctness:** explain generation variables/domains, hard constraints, preferred-start penalty, half-open intervals and the offline office SAT/UNSAT witnesses; then explain the repair extension and its three priorities. Work through the coupled repair with objective `(3,4,0)` and the one-move/four-slot versus two-move/two-slot trade-off. Distinguish solver proof, validation, extraction fidelity and reference assumptions (R1-R3/R16).
2. **Input meaning:** first review the balanced public/gold pairs across every profile, mechanism, layout and label, including operative deadline/fixed-start witnesses and the capacity/precedence certificates. Record actual findings; the pending fields are not completed by automated checks. Also review the original study's twelve fictional prose/gold pairs and representative controlled SAT/UNSAT generation/repair cases. For the extension, review its twenty fictional pairs and examples across all five tiers, three mechanisms and both wording transformations. Record checked IDs and ambiguous wording. These remain AI-assisted/project-generated development inputs; sampled review does not certify every case or create a holdout (R4-R5/R9).
3. **Results and failures:** verify all 48 balanced cases and exact all-attempt denominators, four profile strata, SAT/UNSAT outcomes, conditional objective fractions and resource coverage. Explain the 23 Qwen constraint violations, nine false UNSAT answers, ten strict-format failures and one GLM transport failure; do not infer reasoning failure from prose-wrapped JSON or service errors. Review the earlier 30 generation cases (including the 12-case small view), separate extension/block denominators, SAT/UNSAT counts, family-paired intervals and conditional optimum fractions. The generation hierarchy is post-run reporting, not preregistration. Inspect the current Qwen availability/block confusion, GLM precedence omissions and GLM valid but suboptimal generation. Keep operational failures in denominators and missing usage distinct from zero (R6-R14).
4. **Strong-model interpretation:** in the balanced study, explain the primary 47/48 GLM direct result and secondary 47/47 among returned answers; the transport failure does not demonstrate a solver reasoning advantage. Both B ceilings are finite-case observations within three construction families. Separately explain the difficulty study's nine direct GLM HTTP 502 errors, accepted returned answers, one suboptimal direct generation and two B extraction failures. Keep the historical Qwen3.8 ceiling separate. Hidden serving defaults and operational failures prevent causal weight/speed claims. Review the date-omitting clock paraphrases: ten per model have inapplicable calendar-frame comparison, while relative-slot validity remains interpretable. A future version may clarify date semantics, but this study's inputs and scores remain unchanged.
5. **Responsible AI and method choice:** explain inconvenience distribution, objective priorities, hard-constraint negotiability, privacy and formalization limits. Justify where either approach may be preferable without claiming universal superiority or production reliability (R15-R17).

All members need whole-system understanding even when they review different details. If a correctness issue is found, record its impact, fix the demonstrated defect and run affected offline checks. Preserve original evidence. A new live study requires a scientific need and separate authorization; unconfirmed human work is not a reason to add features or rerun benchmarks.

### S4. Prepare the final report copy

Use [submission-report.md](docs/submission-report.md) as the source. Incorporate S1-S3 findings and actual contributions; remove pending-review/title reminders only when the corresponding work is complete. Check citations and distinguish measured findings from hypotheses.

Create the submitted copy under ignored `docs/private/`, with names, matriculation numbers and email addresses on its title page. Follow [the rebuild instructions](docs/submission-checklist.md#rebuild-the-report), using `--source`/`--output` for the private copy and `scripts/check_report.py --source ... --pdf ... --receipt ...` with a private receipt path. Inspect every page. Each changed copy must independently meet the ten-body-page, single-column/single-spacing, 11-point and one-inch-margin requirements.

The handout permits supplementary model printouts, screenshots or planning graphs in an appendix; it does not mandate those artifacts for this CSP/COP project. The current report includes its architecture diagram and measured-result charts. Add a relevant saved-schedule screenshot only if it helps explain a claim; do not invent a probabilistic model or move required analysis into an appendix to avoid the body limit.

### S5. Build and rehearse the presentation

Use the updated [storyboard and Q&A](presentation/rehearsal.md) and [demo guide](presentation/README.md). Produce the actual deck or requested recording; neither currently exists in this repository. Lead with the small office generation/UNSAT illustration, the balanced generation chart, both methods and a trace-backed failure. Explain the balancing motivation, then use the earlier wording extraction failure as a separately labelled extension example. Cover repair briefly as an extension, then optimization/cost and responsible-AI implications; supplementary charts support Q&A. Agree speakers as a team; coding contacts do not determine speaking roles.

Rehearse 15 minutes plus five-minute Q&A. Every member should explain both methods, generated-data limitations, the GLM failure/ceiling distinction, validator/reference differences and their own work. Record actual timing, unclear explanations and corrections. Demonstrations should work offline; label a canned fallback clearly. Do not rely on a new live call during the presentation.

### S6. Recommended independent handoff

A teammate can clone the published revision, follow [evidence.md](docs/evidence.md), verify the two balanced archives and compare exact-source replay with the saved analyses; verify the separate difficulty or historical pair when using those results. Record the commit, platform, commands and outcome. Automated clean-clone checks and replay are already available; they do not imply a teammate performed this check. This recommendation is separate from course contribution and understanding requirements.

### S7. Deliver the correct files on time

The complete-reviewed-draft target remains **30 October 2026**. Work on S1-S3 and initial presentation preparation in parallel, then finalize S4 after those findings. Finish the presentation before the assigned slot in the week of **9 November**, and submit the report by the verified Canvas cutoff on **13 November**. These course dates come from the supplied handout; check later announcements for changes.

Confirm filename/file requirements, private title identifiers, citations, contribution statements, page limit and any requested deck/recording/code/evidence attachments. Submit the requested deliverables, verify the uploaded versions and retain receipts privately. GitHub publication is tracked in [publication verification](docs/publication-verification.md); it is not a Canvas submission.

### Agent execution from a short prompt

Inspect current Git state and these documents, select the agreed task above, then implement and verify its concrete deliverable. Ask focused questions only for unresolved identity/workspace, conflicting requirements, scientific scope, credentials availability, live budget or publication authority. Routine engineering choices are autonomous. A request to write code does not authorize inference or publication. Human approvals and contributions must come from actual human actions.

For S2/S3, collect factual member accounts or support a real review session. Do not mark student work complete by writing an attribution. For S4/S5, help edit/format supplied material while keeping unconfirmed facts and rehearsal status explicit.

## 6. System architecture and contract

This section describes the implemented version-1 contract. Human team review/sign-off is still pending; schema v1 is distinct from the project checkpoint number. Source types in `schema.py` and the shipped prompts concretize the wire fields. Reconcile this description, callers, tests and prompts together if review changes the contract.

### System architecture and data flow

Keep one installable Python package, one CLI and one shared provider interface. The current implementation has one SoCLaaS adapter; a new provider adapter is conditional on an explicit future study decision. Local computation is CPU-only; only the provider sends model requests. The dashboard reads saved records and adds no alternate execution path. Gold access is an explicit evaluation boundary, not a distinction inferred from file names.

```mermaid
flowchart LR
    C[Evaluator-only<br/>case bundle] --> R[Public renderer]
    R --> V[Same public view<br/>and original schedule]
    V --> A[Direct model call<br/>and schedule parser]
    V --> B[Extraction model call<br/>and schema check]
    B --> S[Fixed CP-SAT<br/>compiler]
    C --> G[Gold reference<br/>solver]
    C --> I[Independent<br/>gold validator]
    A --> I
    S --> I
    G --> E[Evaluator and<br/>objective comparison]
    I --> E
    E --> D[Durable attempt<br/>records]
    D --> P[Replay, metrics<br/>and figures]
    P --> U[Read-only dashboard<br/>and report]
```

| Boundary | Existing implementation | Design rule / next extension |
| --- | --- | --- |
| Formal data | `schema.py`, `objectives.py` | One typed schema and deterministic wire serialization; shared semantics are reviewed/versioned, not copied into each pipeline |
| Provider | `providers/types.py`, `soclaas.py`, `tls.py` | Credentials stay local; explicit timeouts/caps and per-attempt usage/errors; both paths inject the same adapter |
| Direct path | `pipelines/direct.py`, `prompts/direct/` | One call, strict public schedule parsing, no solver or gold repair of A's answer |
| Solver path | `pipelines/solver_augmented.py`, `solver.py`, `prompts/extraction/` | One extraction, validated schema, fixed compiler and bounded lexicographic solving; preserve extracted input and native solver outcomes |
| Independent correctness | `validation.py`, `extraction_diagnostics.py`, `evaluation/scoring.py` | Recompute gold feasibility/objectives independently; compare extraction separately and retain conditional objective denominators |
| Data and experiment control | `evaluation/benchmark.py`, `cases.py`, `manifests.py`, `runner.py` | Render equal public information, protect source-family splits, preflight references, reserve calls durably; preserve compatible frozen-study controls |
| Analysis and presentation | `evaluation/metrics.py`, `figures.py`, `dashboard/` | Consume saved evidence; no model calls from dashboard/replay and no second metric definition in the UI |

Paths in this table are relative to `src/scheduling/` except `prompts/`. The gold validator can check final outputs regardless of whether B's extracted specification is faithful; these are separate measurements. Gold reference solver success is infrastructure evidence, not a third natural-language competitor. For UNSAT, compare the prediction with the independently established gold label; a timeout remains unresolved.

### Run lifecycle and stored evidence

The implemented development path is: load/validate cases and config → check references and estimate requests → establish immutable run contract → reserve each attempt → call A or B → save output → independently score → persist completion → export/replay. Reservation precedes the external request so a crash cannot silently erase possible spending. A saved failure is a completed observation; a pending/uncertain reservation needs explicit reconciliation, not automatic reissue. Fatal authentication, TLS, quota and identity failures stop while retaining completed work; the selected development policy records eligible transient transport/service failures and continues with the next distinct attempt. An exclusive lock prevents overlapping writes; a stale lock alone does not prove an active process.

A run stores `manifest.json`, `cases.json`, `references/` and `attempts/` under an ignored run directory. The manifest identifies cases, prompts, model/solver configuration, source and runtime; reference and attempt records carry their checksums and statuses. Offline replay verifies stored records and recomputes validation/metrics from saved pipeline outputs and references without calling the provider or rerunning CP-SAT. It demonstrates reproducibility of recorded evidence, not identical future live answers. The six completed full-run reproduction archives (balanced, difficulty and historical pairs) are included in results/archives/; fuller operational and historical records are preserved in the private checksummed bundle. See docs/evidence.md for exact coverage and replay.

The implemented frozen mode adds protocol and eligibility/cap decision references to this lifecycle. Section 5 specifies remaining preparation and analysis work; it does not require a database, web service, generic agent framework or new scheduler. Keep the current serial execution until measured runtime/rate-limit evidence justifies bounded parallelism.

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

Authored prose is an opt-in case-bundle **2.0** extension (`AuthoredBenchmarkCase`), separate from canonical `ProblemSpec` schema 1.0. It carries exact variant text plus evaluator-only provenance/review records. Bundle 1.0 remains supported with unchanged legacy hashes. Runner, replay, dashboard and explanation consumers use the same version-aware loader. Missing requested authored variants fail preflight; no template fallback or fabricated review is permitted.

### Output and outcomes

`Schedule`: a list of activity IDs and integer start slots. End times are computed from fixed durations. Claimed textual times must be normalized without guessing or rounding invalid inputs.

`PipelineResult`: `instance_id`, `variant_id`, `approach`, `status`, optional schedule, optional extracted specification, diagnostics, timings, and usage. Pipeline status is one of `SAT`, `UNSAT`, `UNKNOWN`, `INVALID_OUTPUT`, or `ERROR`. A SAT claim requires a complete schedule; an UNSAT claim from a direct LLM is a prediction, not a proof.

Record the model's declared status separately from parsing/execution status and final gold validation; a parseable SAT claim is not an accepted solution. Preserve the underlying solver status separately: `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `UNKNOWN`, or `MODEL_INVALID`. Also store objective value, best bound where available, time limit, elapsed time, and whether each lexicographic stage was proven optimal. Never report a feasible incumbent as a proven optimum, or a timeout as UNSAT.

`ValidationResult`: structural validity, hard-feasible flag, violations with constraint IDs, objective components recomputed from gold, and repair distance. The validator consumes a schedule and gold specification; it must not call CP-SAT or reuse the solver's constraint-building implementation.

### Implemented Python interfaces

```python
solve(spec, limits, repair_context=None) -> SolveResult
validate_schedule(gold_spec, schedule, repair_context=None) -> ValidationResult
run_direct(nl_view, model_config, *, provider_complete=None) -> PipelineResult
run_solver_augmented(nl_view, model_config, solver_limits, *, provider_complete=complete) -> PipelineResult
evaluate(case, pipeline_result, gold_reference, *, repeat=0) -> dict
```

These entry points live in `solver.py`, `validation.py`, `pipelines/` and `evaluation/scoring.py` under `src/scheduling/`. The evaluator currently returns a JSON-serializable mapping; there is no separate `EvaluationRecord` class. Inject the shared provider or canned callable through the pipeline keyword argument.

`RepairContext` contains the common original schedule, including stable activity IDs and start slots. It is required for a repair task and absent for generation; missing repair context is an explicit error. Both the solver and validator use it to compute moved count and total shift. The evaluator first checks the original schedule against `original_problem`, then checks repairs against `updated_problem` with this context. The solver-augmented path builds the same context from the public original schedule; it must not receive the original or updated gold specification.

Li Hao provides the implemented typed `complete(messages, model_config) -> ModelResponse` interface with content, returned model, timing, usage, and sanitized error fields. Both pipelines use this adapter. Review it alongside the shared schema; injected canned responses support offline development without live access.

Use explicit typed models and deterministic serialization. Validate generated JSON before compilation. Do not execute model-generated code. Schema-valid JSON is not proof of semantic correctness.

## 7. Formalization, solver design and reasoning-core improvements

### Course fit and implemented technical contribution

The teaching team's *Project Topic* and *Project Evaluation Guidelines* ask for an explicit course-related mathematical formulation, correct implementation, technical depth, and analysis of why direct reasoning or tool use succeeds or fails. They do not require inventing a new general-purpose solver. The proposal selects a scheduling CSP/COP and minimum-disruption repair. The technical contribution is a **faithful, inspectable and mathematically justified translation-and-solving system**, with evidence explaining where its guarantees begin and end.

Retain the two core paths and fixed v1 domain. R1–R4 are implemented; the specification below defines their behavior and ongoing acceptance criteria. These are team engineering/research choices, not extra grading requirements. Human review remains distinct from technical verification. The optional preprocessing/search refinements below are conditional alternatives, not unfinished core work.

### Explicit CSP/COP formulation

Let `I` be the mandatory activities, `H <= 48` the number of 30-minute slots, `d_i > 0` the fixed duration, and `s_i` the integer start variable. End time is `e_i = s_i + d_i`. Let `D_i` contain every start in `{0,...,H-d_i}` satisfying all unary requirements: full containment in an allowed activity window and in an allowed window for every assigned participant/resource; release, deadline and fixed-start conditions; and avoidance of applicable blocked intervals. Empty `D_i` is a well-formed contradiction, not malformed JSON.

The finite-domain **CSP** is `(variables {s_i}, domains {D_i}, hard constraints C)`. Feasibility asks whether a complete assignment exists. The **COP** adds the preference or repair objective below. A schedule cannot omit an activity to make an infeasible problem appear feasible.

| Requirement | Mathematical meaning | Existing CP-SAT representation |
| --- | --- | --- |
| Unary availability/time bounds | `s_i in D_i`; each full interval `[s_i,e_i)` fits one window in each applicable window list | `legal_starts` and `new_int_var_from_domain` |
| Precedence `i -> j` | `s_i + d_i <= s_j` | Linear inequality |
| Shared participant/resource | For each conflicting pair, `e_i <= s_j OR e_j <= s_i` | One fixed-duration interval per activity and a `NoOverlap` constraint for each entity |
| Release / deadline / fixed start | `s_i >= r_i`, `e_i <= deadline_i`, `s_i = f_i` | Incorporated into legal domains |
| Preferred start `k` | Penalty `w_k` if `s_activity(k)` is outside `[lower_k,upper_k)` | Boolean violation linked to the start by an allowed-assignment table |
| Repair change indicators | `m_i = 1` exactly when `s_i != old_s_i`; `t_i = abs(s_i-old_s_i)` | Reified equalities/inequalities and `add_abs_equality` |

Define `P(s) = sum_k w_k * 1[s_activity(k) outside preferred_window_k]`. Generation minimizes `P(s)` subject to all hard constraints. This is a weighted **violation count**, not distance from a preferred time. Each preference contributes separately, including intentional repeated preferences/weights; normalization must not silently change this objective.

For repair, use the common original schedule `old_s` and minimize the tuple lexicographically:

```text
M(s) = sum_i 1[s_i != old_s_i]          # number of moved activities
T(s) = sum_i abs(s_i - old_s_i)         # total shift in slots; minutes = 30*T
objective(s) = (M(s), T(s), P(s))
```

Thus `(1,10,5)` is better than `(2,2,0)`: avoiding a second moved activity has priority over smaller total shift or better preferences. This priority is a declared user-impact choice. It is not an intrinsic definition of the best schedule. Never turn hard constraints into penalties, use unspecified large weights, or switch to makespan minimization just because a job-shop example does so.

**Exact sequential algorithm, already implemented:** minimize `M`; only after proof of its optimum `M*`, add `M=M*` and minimize `T`; only after proof of `T*`, add `T=T*` and minimize `P`. Generation needs only the preference stage. Give the entire repair solve one wall-time budget and pass the remaining time to each stage. If proof is incomplete, retain a feasible incumbent, stop claiming full lexicographic optimality, and preserve the stage objective, bound and native status. A later timeout must not erase an earlier valid solution. Prior-stage solution hints are already implemented.

For exact stages/references use integer coefficients, `absolute_gap_limit=0` and `relative_gap_limit=0`, as the current solver does. The [pinned v9.14 parameter definitions](https://github.com/google/or-tools/blob/v9.14/ortools/sat/sat_parameters.proto) explain stopping limits; a nonzero gap setting changes what a reported `OPTIMAL` status establishes. Retain the existing numeric-range checks and never round a floating bound into an unsupported exact proof. Compare secondary gaps only when all preceding objective components match their proven optima. Raw component values remain reportable without such a match.

The unpruned assignment space is `product_i |D_i|`; it is an upper bound on combinations, not CP-SAT's observed search count. Explain how precedence and shared entities couple those choices. CP-SAT combines SAT/constraint reasoning and linear techniques, as described by its [developers](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2023.3). Keep interval/global constraints and the pinned default search as the starting point. Implementing another general backtracking, SAT or MILP solver is unnecessary; independent tiny enumeration supplies a comprehensible correctness check.

### Implemented core and acceptance criteria

The integrated `solver.py` compiles finite legal domains, global non-overlap, precedence, preferences and the three repair stages. `objectives.py` computes the tuple, while `validation.py` checks schedules independently. Existing tests exercise tiny exhaustive optima, boundaries and timeout/incumbent handling. These features are delivered and should be preserved.

The [expanded study](docs/expanded-development-100.md) reports **4.69 ms mean solver time over 99 B solves**, compared with **10.12 s mean model-response time over 100 B calls**. The malformed response never reached CP-SAT. These conditional measurements cover 3–12 activities and 48 slots; they are not a large-instance scaling benchmark. A faster CP-SAT run cannot repair an omitted constraint or malformed specification. Prioritize formal correctness and extraction reliability; claim a runtime improvement only after measuring it.

| Component | Owner / integration partner | Implemented capability | Acceptance evidence |
| --- | --- | --- | --- |
| **R1 — repair correctness** | Yao Xiang; Yong Qing independently reviews | Enforce stable repair time frame, activity durations and assignments at the shared boundary; broaden mathematical checks | Reject unsupported changes; accepted v1 events preserve meaning; tiny solver/validator/enumerator agreement |
| **R2 — reliable formalization** | Yao Xiang for schema/prompt/diffs; Li Hao for prompt packaging; Yong Qing for scoring consumers | Executable extraction examples, precise schema errors, and typed semantic-review differences | Extra-field errors remain failures with exact paths; examples parse; altered/omitted requirements are inspectable without gold feedback |
| **R3 — constraint reasoning** | Yao Xiang; Yong Qing checks reasoning independently | Small domain-analysis record with actual rule provenance and supported contradiction explanations | No feasible schedules lost; empty-domain reasons are checkable; compiled-model UNSAT remains distinct from source-request correctness |
| **R4 — evidence-based output** | Li Hao for shared formatting/CLI; Yao Xiang for proof semantics; Yong Qing for evaluation labels | Deterministic before/after, objective and proof-status explanations from saved records | No extra LLM call; timeout/extraction/gold distinctions survive; works on existing recorded outputs |

R1–R4 are integrated through shared records and consumers. Maintain their regressions and coordinate serialization changes, preserving old archives. R3 intentionally covers named unary exclusions and simple proven contradictions; a general minimal-conflict service remains optional.

### R1 — repair invariants and mathematical qualification

The integrated baseline audit found that `RepairCase.__post_init__` checked types and activity-ID coverage but permitted changes to time origin, horizon length, duration and assignments. R1 now rejects those changes and is included in main at `bc165bc`; human review remains pending. The shared boundary and evaluator both protect the time frame. This closes the earlier v1 contract gap without changing the research task. The reviewed development cases keep the intended time frame, durations and assignments; this finding does not invalidate their recorded acceptance counts.

Compare original/updated `horizon_start`, timezone, slot length and horizon length, and compare each retained activity's duration, participant IDs and resource IDs by stable ID. Order alone is irrelevant. Keep activity presence fixed. Accept the supported availability/deadline/fixed-commitment disruptions; reject changing an activity's meaning under the same ID. A future task-duration, assignment, new/cancelled-activity or time-resolution feature requires a new explicit repair contract. Original-schedule feasibility remains independently checked against the original specification.

Do not give B an evaluator-only original specification to enforce this boundary. Its solver receives the extracted updated specification and the public original schedule. Shared-case validation protects supplied benchmark/application pairs; extraction fidelity against the public request is still a separate issue. The common public description must state the time frame and immutable activity facts clearly, and both approaches receive the same information.

Extend the existing tiny enumerator cases to three/four activities with unequal durations, multiple participants, asymmetric resource sharing, gapped domains and competing preferences. Compare the feasible set or proven objective tuple, not the exact schedule when ties exist. Include movement-versus-shift disagreement, preference tie-breaking, no-op repair, contradictory complete requests, and existing timeout/incumbent regressions. Keep the enumerator/validator independent of compiler helpers.

**Worked repair counterexample:** three one-slot activities share resource R over slots `[0,3)`. Original starts are A0/B1/C2; legal starts before disruption are A `{0,1}`, B `{1,2}`, C `{0,1,2}`. A new participant block removes A's start 0. The only repaired schedule is A1/B2/C0, with `(M,T,P)=(3,4,0)` when there are no preferences. B and C must move although their own unary windows did not change. Freezing an apparently unaffected activity can wrongly make a feasible repair appear impossible. This independently enumerable example is covered by the formal qualification regressions; preserve it when changing repair or search behavior.

Document the original-schedule policy: initially a saved feasible schedule from the pinned gold-solver configuration, supplied identically to both approaches. Discuss its influence on repair patterns. [Minimal-perturbation research](https://www.unitime.org/papers/ercimprelimin03.pdf) grounds the idea of minimizing departure from a prior assignment; our fixed activity set and three-component objective are a narrower team choice, not a new general repair theory.

### R2 — make extraction an explicit, inspectable contract

In `schema.py`, `prompts/extraction/specification.txt` and `pipelines/solver_augmented.py`, maintain one canonical accepted format. Maintain the complete minimal valid `ProblemSpec` example and compact exact-field reference checked against the parser. Keep it separate from few-shot benchmark solutions and verify that examples do not accidentally add activities or constraints to a request. State explicitly that unit capacity is implicit and there is **no `capacity` field**. The five saved extra-field failures motivate this change; they do not prove a prompt revision will improve accuracy.

Give schema failures safe structured detail: error code, JSON path, missing/unsupported field names, and a concise message, while retaining the raw response in its existing protected record. An extra `participants[0].capacity` should remain `INVALID_OUTPUT`, with an actionable location; do not drop it silently. Keep duplicate-key, invalid-number, unknown-type and dangling-reference rejection. If a formal JSON Schema artifact is introduced, derive/check it against the canonical parser and distinguish structural checks from semantic constraints. Do not depend on provider-enforced structured decoding unless SoCLaaS support is verified; adding that feature would need a recorded new inference configuration.

Maintain the implemented `compare_specifications` typed details beyond top-level labels and omitted/invented totals. Report changes by entity/activity ID and field, with unmatched typed constraint records and multiplicity. Examples: duration A `2 -> 1`, a missing participant P, reversed precedence, or deadline A `4 -> 5`. Pair an alteration only when correspondence is unambiguous; otherwise retain unmatched records. Rename/order differences that do not change meaning may normalize away. Availability windows must not be merged blindly: under whole-window containment, two adjacent windows `[0,2)` and `[2,4)` do not admit a three-slot activity, while the merged window `[0,4)` does.

Keep structural comparison separate from semantic equivalence. For tiny cases with the same time frame and immutable activity facts, an evaluator-only exhaustive comparison may establish equality of feasible start assignments and objective values over that finite horizon. This is an instance-specific mathematical equivalence, not proof of general natural-language understanding. A counterexample demonstrates a difference; failure to find one within a limited search does not prove equivalence. Larger/alternative encodings remain subject to human semantic review. Gold differences never feed corrections into the core extraction call. This addresses the formalization boundary highlighted by [ACL 2025 research](https://aclanthology.org/2025.acl-long.242/) without assuming syntactically valid JSON captures the user's meaning.

### R3 — explainable domains and sound preprocessing

The implemented `domain_analysis.py` provides legal domains and bounded reason records. Maintain this shared analysis with the compiler; extend it only for a demonstrated diagnostic need. Each rejected start can cite an explicit constraint ID or a stable specification path for activity/entity availability. Group identical reasons for display. Index entities and relevant constraints once per solve if useful; with at most 48 slots, straightforward enumeration remains appropriate. Keep this helper out of the independent validator.

Unary domain wipeout can then explain, for example, that a task needs two slots but no start survives its deadline and participant availability. A directed precedence cycle with positive durations is another checkable contradiction: summing the inequalities would require a start time to be strictly later than itself. Report the actual rule chain. These are **sufficient contradictions**, not necessarily smallest explanations. Do not convert failure to derive a simple explanation into a claim that the problem is feasible.

Optional precedence-domain filtering may use this sound rule for `i -> j`, while both domains are nonempty:

```text
D_i <- {s in D_i : s + d_i <= max(D_j)}
if D_i is empty: stop with a contradiction
D_j <- {t in D_j : t >= min(D_i) + d_i}
if D_j is empty: stop with a contradiction
repeat affected arcs until no domain changes
```

Each removed value lacks support on that precedence relation. Preserve holes in domains and retain all original precedence/NoOverlap constraints in CP-SAT. The prepass need not solve resource conflicts; nonempty domains are not a SAT proof. Verify that preprocessing preserves every feasible tiny schedule and therefore the exact objective optimum. If this optional helper is implemented, independently enumerate tiny chain/domain/duration combinations, including empty support and boundary cases. Such checks support the argument but do not establish correctness on every possible instance; retain the support argument and consumer regressions in implementation review.

CP-SAT already propagates constraints internally. The main reason for an explicit prepass is interpretable reasoning and inspectable domains; keep pruning optional until its extra complexity and runtime are justified. If analysis finds a contradiction, either compile an explicit false condition and obtain the actual backend outcome as today, or introduce a distinctly labelled analytical proof record. Never fabricate a native CP-SAT status for a solve that did not occur.

**Optional general conflict diagnostic, after R1–R4:** if simple reasons are insufficient and a report example warrants it, a small offline deletion-based check may rebuild a feasibility-only model while removing named requirement groups. Begin only after the complete feasibility model is proven INFEASIBLE; an initial UNKNOWN cannot establish a conflicting set. Keep immutable background facts explicit. Removing a requirement must relax it: removing an availability requirement means allowing the full horizon, not deleting an allowed window and accidentally narrowing availability. Remove a group permanently only when the remaining model is proven infeasible; preserve it on UNKNOWN. Bound checks and total time, and label an interrupted result merely a sufficient conflicting set. A deletion-minimal set is not necessarily minimum-cardinality. This analysis is separate from ordinary replay, which does not rerun CP-SAT, and from primary measured inference.

Do not obtain misleading explanations by blindly attaching assumptions to every compiled constraint. Unary requirements are currently baked into domains, and installed OR-Tools 9.14 rejects direct enforcement of `NoOverlap`. Its [assumption-core contract](https://github.com/google/or-tools/blob/v9.14/ortools/sat/cp_model.proto) also does not guarantee a minimum conflict and limits core reduction for optimization/multi-worker runs. An assumption-based diagnostic would require a separately validated encoding that exposes all relevant requirements; it is unnecessary for the small initial explanation scope.

### R4 — explanations tied to actual evidence

Implemented by Li Hao and merged through PR #4 (`61d9fbb`, 29 September): shared `explanations.py` and the read-only `scheduling explain` CLI consume current and saved results. The original formatter made no schema, prompt or solver changes. Formal semantic/evaluation sign-off remains pending; the integrated Yao Xiang extension adds compatible recorded R3 reasons. See [Li Hao follow-up](docs/lihao-development-followup.md) for tests, measured failures and the participant-burden example. The behavior requirements below remain the review criteria.

The shared formatter consumes `ProblemSpec`, `SolveResult`, `OptimizationStage`, repair context and validation records through the CLI and read-only case view. A formatter does not solve, call a model, change the schedule or invent a proof. Keep gold/extraction comparisons evaluator-only and visibly separate from what B itself knows.

For a feasible repair, show before/after clock times, moved activity IDs, `(M,T,P)`, and the proof status/bound of each attempted stage. For a timeout after proving movement only, say that minimum moved count is established but minimum shift is not. Explain preference penalties using the actual windows/weights. For infeasibility, distinguish a proven contradiction in the **extracted specification** from a correct infeasibility judgment about the original request; show a supported reason if available and otherwise state that a detailed conflict was not derived. Parsing failure, solver UNKNOWN and gold-invalid output each retain their own explanation.

Connect this to the responsible-AI objective-choice discussion: for each participant p, compute moved-event count and `30 * sum(abs(s_i-old_s_i))` over that participant's activities. These describe participant inconvenience under fixed assignments, not fair workload allocation. Shared events contribute to each affected participant, so participant totals need not equal the activity-level objective. Use one existing realistic/development case to show how minimizing moved activities can distribute inconvenience unevenly. Changing the primary objective to participant weights, minimax burden or soft hard-constraint relaxation would be a separate agreed experiment, not an implementation fix.

New `SolveResult` records carry a versioned exact specification/repair-context binding. Verify it before attributing optimality, infeasibility or domain reasons to supplied standalone files. A matching hash establishes input correspondence, not authenticity of arbitrary evidence. Legacy unbound standalone results may validate a candidate but must withhold proof correspondence; historical run explanations use their checked case/record context. Never replace raw records to manufacture a binding.

### Conditional solver optimizations and boundaries

The following are optional candidates for a separately authorized follow-up; existing evidence does not make them a current priority. Make one change at a time, use the same difficult development specifications and total budget, and retain it only when the evidence or explanatory value justifies the maintenance cost.

| Candidate | Implementation direction | Correctness/performance boundary |
| --- | --- | --- |
| Initial repair hints | Before the first stage, suggest public original starts still in their legal domains. Keep existing later-stage hints | [v9.14 hints](https://github.com/google/or-tools/blob/v9.14/ortools/sat/docs/model.md#solution-hinting) guide search and do not constrain it. Never hard-fix unaffected tasks or import gold starts. Bounded-run incumbents may change even though exact optima do not |
| Compact preference encoding | Keep the present allowed-assignment tables initially. If model construction becomes significant, compare a correctly reified inside/outside-window encoding | Both directions of each Boolean equivalence must hold. Check every legal start and preference penalty; reducing variables alone is not evidence of faster solving |
| Skip a provably constant stage | Reuse a feasible incumbent when the remaining objective is demonstrably constant, e.g. absent preferences | Record analytical constancy separately from solver `OPTIMAL`; update proof consumers/versioning. Do not skip feasibility search when no incumbent exists. Retain three stages if the bookkeeping costs more than it saves |
| Component solving | Only consider it if profiling finds useful disconnected groups in the full precedence/shared-entity interaction graph, with separable objectives | A disruption's local neighborhood is not necessarily an independent component. Prove decomposition and maintain one total budget and global proof accounting before implementation; unnecessary for current tiny solves |

Instrument only what resolves a performance question: compilation time, per-stage elapsed time/status/bounds and, where available, branches/conflicts and time to first incumbent. Compare medians/tails and proof completion on offline cases, retaining all failures. Keep the primary CPU/worker/seed configuration stable; additional workers, hand-chosen branching or large-neighborhood search are not automatic upgrades. Do not promise deterministic elapsed time or identical tied schedules across machines. A change after the evaluation freeze needs a new configuration and assessment of affected results.

Source-grounding spans and explicit ambiguity abstention may be useful later interface variants: a single response could cite public text for extracted fields, or return unresolved required facts without solving. A quotation's presence is not proof of its interpretation. Such output changes need their own schema/prompt version, compatible parsing and token-budget qualification. Complete contradictions must still be formalized and solved; incomplete information must not be invented. Keep these variants in the bounded responsible-AI/diagnostic work unless the team deliberately adds a separate research arm. Multi-call correction, different objectives, new constraint families and new solvers are separate scope decisions.

### Core completion and ongoing verification

R1–R4 have reviewable implementation and evidence. Qualification requires the worked boundary/repair cases and broader tiny enumeration to pass, with explanations accurately distinguishing syntax, interpretation, feasibility and optimality. Human sign-off remains open. No-op and coupled repair work; UNKNOWN remains distinct from UNSAT; malformed extraction cannot become a silently corrected success. Optional optimizations may be declined with a measured or complexity-based reason.

The report should then explain three technical insights using this implementation: **how domains/global constraints reduce the scheduling search; why minimum-disruption repair can propagate beyond the changed activity; and why solver proof does not guarantee faithful language interpretation.** These connect the project's core to the course's formulation, technical-depth, analysis and responsible-AI criteria without requiring a broader product or a new optimization algorithm.

## 8. Dataset, metrics and final report evidence

### Preserved completed study: 600 attempts per model

| Block, per model | Source and pairing | Attempts |
| --- | --- | ---: |
| Controlled | 240 canonical cases / 120 source families; 120 generation and 120 repair; each task 60 SAT / 60 UNSAT | 480 |
| Realistic | Twelve AI-assisted fictional scenarios, canonical prose, three cases per joint task/label stratum | 24 |
| Additional wording | 24 selected controlled bases from distinct families; paraphrase and reordered versions; matched to their canonical partners | 96 |

The two models used identical input bytes and request-prompt hashes. Four controlled sweeps cover activity count, slack, resource contention and interaction density at three levels. All are known development cases. No public benchmark or real calendar was imported. Historical v1/v2/v3 pilots, the 200-call comparison and inspected candidate structures remain development evidence. See [data preparation](docs/final-data-preparation.md) and the source-family exclusion registry for future draws.

### Preserved difficulty extension: 200 attempts per model

| Block | Conditions and pairing | Scheduling attempts |
| --- | --- | ---: |
| Controlled | Five tiers × three mechanisms × two labels × generation/repair = 60 cases / 30 families | 120 |
| Fictional scenarios | Five tiers × two labels × generation/repair = 20 cases / 10 separate families | 40 |
| Additional wording | Two selected controlled bases per tier × two variants = 20 additional conditions | 40 |
| Total | 100 case/rendering conditions; 80 unique cases; 40 construction families | 200 |

Every tier has 40 scheduling attempts after combining blocks. Canonical strata are balanced; wording has equal task and SAT/UNSAT margins but joint task/label base counts of 3/2/2/3, rotated across tiers. These variants are not independent source families. Do not aggregate the blocks into a difficulty claim without explaining their composition.

The generator uses multi-job shared-resource schedules, competing preferences, cross-job precedence, calendar breaks and repair cycles. UNSAT proofs use resource workload, critical-path length or unit-slot capacity rather than an individually impossible activity. SAT repair contexts are valid before the change, and every SAT case has a proven reference optimum. Tier size is deliberately combined with richer interactions: this is a stress ladder, not a causal estimate of activity count alone. The fixture is AI-assisted synthetic development data with pending human semantic review. The full Qwen3.6/GLM comparison is complete; the earlier smoke remains separate. Normalization merges one controlled family pair, leaving 29 controlled and ten fictional groups. Clock paraphrases omit a date, which limits calendar-frame extraction checks without changing relative-slot validity scores.

### Latest balanced generation confirmation: 96 attempts per model

[`balanced-generation-v1`](docs/balanced-generation.md) has 48 cases, 24 SAT and 24 UNSAT, each scored with both methods. Every deadline/fixed-start profile has six cases of each label. Eight 1–2-hour activities, two participants and one room fit the existing single-day/30-minute contract. Three mechanisms and two numeric layouts vary availability while preserving paired assignments, rule values and constraint counts. All related variants belong to only three conservative construction families.

The dataset includes independent SAT witnesses and arithmetic UNSAT certificates, separately proven CP-SAT reference optima, operative-constraint counterexamples and fully dated public prose. Human review remains pending. The two completed campaigns use canonical prose only; they do not add repair, fictional or wording observations. The [summary](results/summary/balanced-comparison-20261017.json) and [audit](docs/balanced-comparison-audit.md) identify every record, denominator, failure category, profile and resource-coverage count.

### Metrics and reporting contract

- Primary acceptance: gold-valid SAT schedule or correct UNSAT answer over all labelled attempts. Preserve every provider/parser/solver failure in the denominator.
- SAT validity and UNSAT accuracy: separate task/label denominators. Direct UNSAT is a prediction; solver infeasibility proves only the compiled problem.
- Optimization: compare proven reference objectives only on valid SAT schedules; secondary repair gaps require equality on earlier components. Also report how many attempts reached that conditional subset.
- Extraction: parsing, structural equality, bounded semantic evidence and end-to-end gold validity are distinct. Structural mismatch alone does not establish semantic error.
- Resources: request/model/solver time, reported tokens and missing coverage; no invented zero usage or monetary cost. CP-SAT times are conditional on actual solver execution.
- Pair A/B on case, rendering and repeat. Canonical controlled, realistic and wording rates stay separate. Wording reuses base problems: neither the preserved 1,200 attempts nor the completed extension's 400 attempts are independent problem counts.
- Existing controlled paired intervals use family bootstrap, 10,000 resamples, seed 3263, within each task/model. Do not interpret a ceiling or degenerate interval as equivalence/perfection.
- Historical difficulty cells with five SAT cases and current finer tier cells with three SAT cases are descriptive. Domain-product size is a bound on naive combinations, not measured CP-SAT search nodes. Preserve nonmonotonic results and avoid cherry-picked thresholds.

### Verified findings and scope

The balanced core scores Qwen A/B **6/48 versus 48/48** and GLM **47/48 versus 48/48**. Keep strict-format, scheduling and service failures separate, as specified in D5; no recorded attempt was retried or removed. GLM's one rejection is a transport failure, not evidence of poorer direct reasoning. Perfect B acceptance does not by itself establish perfect extraction semantics, general scheduling competence or equivalence. The four profile views are descriptive: three construction families cannot support strong population uncertainty claims. The correction addresses the specific earlier confound without establishing that a model previously exploited it.

The earlier difficulty-generation view scores Qwen A/B **11/30 versus 28/30** and GLM **25/30 versus 30/30**. The twelve-case small view is Qwen 6/12 versus 12/12 and GLM 12/12 for both. Core-generation reference-objective matching is Qwen 1/2 versus 15/15 and GLM 10/11 versus 15/15, conditional on valid gold-SAT schedules. The [generation summary](results/summary/generation-focus-20261015.json) records exact observation IDs and resource coverage.

For the complete preserved blocks, the difficulty comparison has Qwen A/B acceptance 17/60 versus 57/60 controlled, 5/20 versus 18/20 fictional, and 4/20 versus 19/20 wording. GLM has 55/60 versus 60/60, 18/20 versus 20/20, and 18/20 versus 18/20. All nine GLM A rejections are HTTP 502 failures; B's two rejections are demonstrated precedence-omission errors. Conditional reference-objective matching is Qwen A 1/5, B 48/48; GLM A 41/42, B 49/49. Interpret these alongside failure-inclusive validity, not as unconditional optimization success.

The [report](docs/submission-report.md), [difficulty audit](docs/difficulty-comparison-audit.md), [claim index](docs/claim-evidence.md), [summary](results/summary/difficulty-comparison-20261014.json) and [figure data](results/figures/difficulty-comparison-20261014/figure-data.json) identify exact values and limitations. The [historical Qwen audit](docs/two-model-development-audit.md) retains the previous 600-attempt study. Do not pool different studies or update immutable results to reflect later documentation status.

### Deferred evaluation beyond D1-D5

For work beyond the completed balanced and difficulty designs, define the scientific question and model decision first. Freeze construction, prompts, metrics and an explicit budget before outcomes. A claimed held-out study must use fresh structural families excluded from inspected/rejected development structures, reviewed prose/gold semantics and related renderings in one split. The active difficulty suite does not claim that stronger status. Additional repeats require explicit repeat mapping and tests. Another model or a function-calling arm needs a separate rationale and allowance. Preserve original results; never rerun merely to replace failures with success.

## 9. Provider, execution and resource contract

Only the approved NUS SoCLaaS adapter is implemented. Reported IDs across the historical and current studies are `qwen3.6:35b`, `qwen3.8:27b` and `glm-5.3-flash`; their hosted weights and unexposed inference defaults are not independently known. All four complete runs used revision-3 prompts, 32,768 requested output tokens per completion, 30-second connect and 1,800-second read/write/pool limits, no retries, one worker and solver seed 0. B uses 30 seconds; references use 60 seconds. HTTPX read timeout concerns waiting for response chunks, not a guaranteed whole-request wall limit.

Each historical 600-attempt campaign allowance covered 603 HTTP requests: one metadata request, two capability completions and 600 scheduling completions. The 19,726,336 reserved output tokens are not actual consumption, an input-inclusive cap or a currency budget. Reported totals including capabilities are 1,773,823 tokens with 602/602 coverage for Qwen3.6 and 3,994,657 with 593/602 for Qwen3.8.

The current difficulty campaigns each used 203 requests, reserving 6,619,136 output tokens. Reported usage including capabilities is 969,165 tokens with 196/202 coverage for Qwen and 1,497,043 with 193/202 coverage for GLM. Qwen reported two fingerprints and GLM one; every successful response matched the required identity.

The authorized development policy `strict_model_observe_backend_v1` requires the exact model while recording backend variation. The historical Qwen3.6 run returned three fingerprints; Qwen3.8 one. `continue_transient_v1` retains timeout/transport/HTTP 408/500/502/503/504 failures and cools down before the next distinct attempt. It never retries failed attempts. Fatal authentication, permission/quota, TLS, malformed-envelope, model-identity, integrity or budget errors still stop. Frozen mode retains the strict backend rule. Preserve every prior policy under its original run identity.

Run long campaigns through an independent one-shot service with automatic restart disabled. Check heartbeat, worker state, real OS lock ownership and exit receipts. A stale lock file alone does not prove a live run. An uncertain request reservation cannot be reissued without reconciliation. App independence does not prevent Mac sleep, logout or reboot. The completed Qwen3.8 run has two verified safe pauses; elapsed wall and monotonic clocks include different effects and cannot be labelled pure inference time. See [operations](docs/usage.md) and [recovery evidence](docs/benchmark-process-recovery.md).

Keys stay in ignored `.env` or a secret source, never in chat/code/archives. TLS validation remains enabled. No further live model request is authorized by this publication or these examples.

## 10. Verification and readiness gates

| Gate | Current status | Remaining evidence |
| --- | --- | --- |
| Formal/implementation | Both paths, repair/diagnostics and independent validator implemented; mathematical fixtures and regression suite verified | Actual member semantic/code review and any defect-specific follow-up |
| Complete development evaluation | Balanced 96-attempt, difficulty 200-attempt and historical 600-attempt pairs complete; failures retained; archived analyses reproduce offline | Genuine interpretation of limitations and optional independent teammate replay |
| Reproducible repository | Integrated source, tests, figures and all six replay archives prepared; actual publication/verification recorded in docs/publication-verification.md | Recommended teammate handoff (S6); optional off-device copy of the private historical bundle |
| Scientific course fit | Written TA feedback supports the topic and evaluation; generation-first hierarchy implemented | Confirm exact single-day/preference simplifications and hosted-model eligibility; actual Canvas record |
| Report/delivery | Exploratory report integrates balanced and separate historical findings; exact PDF checks are recorded in the format/publication receipts | S2-S5 member work, private-copy audit, actual presentation and S7 receipt |

[Publication verification](docs/publication-verification.md) records the exact commands and results, including platform-specific TLS handling. Run targeted checks first; full suites are appropriate for shared runtime changes. Do not repeat live benchmarks or unchanged full suites for documentation edits. If a semantics-changing fix is needed, record its scientific impact before making updated performance claims.

## 11. Acceptance criteria

The report must trace every numerical claim to a saved artifact, retain all failures and metric denominators, distinguish interpretation from measured evidence, explain why direct and solver-assisted methods differ, and discuss synthetic-data assumptions and realism. Uncertainty and small samples stay visible. A strong direct result is a valid outcome.

The submission must include course-required private title information, actual contributions and AI disclosure, member understanding, a compliant PDF and presentation. Record actual actions and eligibility/submission evidence; do not substitute generated approvals. Team review logs and S6 replay are verification practices, not extra course-mandated forms. An agent cannot sign for a member or award course-model eligibility.

If teaching feedback requires an additional comparison, establish that limited follow-up explicitly, with exact provider/model, inputs, outcomes, cap and source snapshot. Existing report scope stays exploratory. Otherwise focus on completing the report and human delivery rather than reopening architecture.

## 12. Responsible AI

Analyse concrete consequences: participant inconvenience can concentrate despite low total disruption; minimizing moved count may increase total time shift; unsupported/ambiguous requirements require clarification; explanations must distinguish extracted-model proof from source correctness. Preserve user control and never silently relax hard constraints. Fictional data reduces privacy exposure but does not establish real-calendar consent or anonymity. Prompt-boundary tests are not live adversarial-robustness evidence. See report Section 7 and the genuine review/contribution records.

## 13. Risks and responses

| Risk | Response |
| --- | --- |
| Course model interpretation unresolved | Check real feedback; obtain targeted clarification before claiming eligibility |
| Gold/text mismatch or compiler bug found | Preserve original evidence, diagnose independently, record impact; new study only if claims require it |
| Strong-model ceiling | Analyse optimum quality, resources and limits; do not change scores or benchmark to manufacture a win |
| Provider/backend variation | Preserve failure coverage/fingerprints; keep shared-service interpretation and no causal speed claim |
| Private historical records lost | Verified local preservation bundle plus tracked full-run replay archives; a same-machine backup is not protection against device loss |
| Report overclaims human work | Keep assistance explicit; require actual member revisions and review records |

## 14. Git, portability and evidence preservation

Use the Python 3.12 hashed lockfile and noneditable installed checks for handoff. macOS and Linux are documented targets; this publication's current suite was executed on macOS and prior Linux receipts apply to their recorded source. Native Windows is unqualified. The runner uses POSIX file locks. CPU-only computation is local; remote model latency includes hosted service conditions.

Preserve existing work, inspect diffs, stage explicit paths and scan for secrets before publication. No force pushes, history rewrites, silent branch switches or deletion of run history. Publish only with user authorization. After publication verify the actual remote SHA and a clean source/artifact checkout, not just command exit status.

The former `report/` directory is now `docs/`. Active links and scripts use the new path; original paths inside immutable archives/receipts remain unchanged. Keep the approved byte-for-byte reproduction archives in `results/archives/` and verify them against `results/evidence-manifest.json` (historical) `results/difficulty-evidence-manifest.json` (difficulty), or `results/balanced-evidence-manifest.json` (balanced). Private full-run/source/capability/supervisor/pause and historical traces are preserved in the separately checksummed bundle described by [evidence.md](docs/evidence.md). Do not overwrite either original or archived results. Saved traces are recorded final outputs and metadata, not complete raw HTTP captures or hidden reasoning.

## 15. Active decisions

| Decision | State |
| --- | --- |
| Report evidence | All 48 balanced generation cases lead; earlier difficulty generation and repair/fictional/wording retained separately; explicitly development evidence, not held out |
| Scope cap | D5 completed 48 cases / 96 scheduling attempts per model. Preserve both 200-attempt studies and historical pairs. No additional inference or features required absent a demonstrated need |
| Major implementation | Delivered; only defect-driven maintenance needed for this report |
| Extra model/fresh holdout | Conditional future work, not automatically required by course |
| Provider eligibility | Pending exact interpretation/feedback |
| Human review/authorship | Accounts, substantive review and understanding remain unconfirmed; follow S2-S3 without inferring from tests, branches or roles |
| Publication | Integrate the balanced and consultation updates with matching source, PDF, figure/format receipts and immutable evidence. Record actual remote state in publication verification; GitHub publication does not establish submission |
| Further inference | Not authorized by publication; prior full-run allowances consumed |

## 16. Source grounding

The original *Project.pdf*, *CS3263-Project-Guidelines 2627.docx*, *ResponsibleAI.pptx* and Group 23 proposal govern scope and grading. They are private course inputs, not uploaded to public Git. [The source audit](docs/two-model-development-audit.md#course-proposal-and-remaining-delivery) and [submission checklist](docs/submission-checklist.md) give page/paragraph locators.

The report cites NATURAL PLAN, minimal-perturbation work, language models as planning formalizers, CP-SAT-LP and official OR-Tools statuses. These primary sources motivate design; they do not establish our scores or course rules. [The historical research plan](docs/development-plan-history.md#research-basis-for-the-recommendations) preserves the broader literature review and release-matched technical sources without making them mandatory features.

## 17. Report and presentation delivery

The canonical source is [docs/submission-report.md](docs/submission-report.md), rendered by `scripts/render_report.py` to `docs/submission-report.pdf`. The prior Qwen report and combined-scope difficulty report are preserved in `docs/history/20261002-report/` and `docs/history/20261014-report/`. The current narrative covers abstract, motivation/questions, related work, CSP/COP and repair, architecture, provenance/protocol, acceptance/SAT/UNSAT/difficulty/optimization/extraction/wording/resources, implications, responsible AI, reproducibility, contributions and conclusion. [claim-evidence.md](docs/claim-evidence.md) connects these to artifacts.

Regenerate figures offline from the portable summary. Compact report figures and mathematical subscripts use at least 11 pt at final size. The current format receipt records the exact PDF page count and source hashes. Rebuild and inspect every page after substantive changes; confirm body page count, single column/spacing, text size and one-inch margins. Title and references are excluded from the ten-page body maximum. Future revisions may change the count; S4 and the submission checklist give the checking procedure.

Produce the actual presentation using the small office generation example, CSP/COP formulation, comparison diagram and balanced generation results (with the earlier studies separately labelled), then briefly cover the repair/robustness extensions, extraction failure, quality/cost trade-off and responsible-AI limits. Rehearse the whole pipeline and questions on gold independence, generated data, backend failures and solver proof. A storyboard is preparation, not delivery. Record genuine contributions, citations, AI assistance and final submission receipts; no grade or course acceptance is inferred from repository publication.
