# Dynamic Constraint-Aware Scheduling

**CS3263 Foundations of Artificial Intelligence · Group 23 · NUS AY2026/27 Semester 1**

Generate schedules and repair them when requirements change. This research system compares a language model that produces schedules directly with the same model translating requests into a structured problem solved by OR-Tools CP-SAT. An independent validator checks both approaches against the original requirements.

**Status: integrated development version 2.** Generation, minimum-disruption repair, extraction diagnostics, constraint explanations, benchmark execution, replay and the read-only dashboard are implemented. The next stage is a focused extraction improvement, model qualification and fresh final-study preparation, followed by reviewed evaluation, analysis and submission. The final-data builder/selector and any required provider extension remain work items; the study has not yet run. Core delivery target: **30 October 2026**.

[Development and final-study plan](planning.md) · [Contributor and agent instructions](AGENTS.md) · [Checkpoint readiness](report/checkpoint-readiness.md) · [Version 2 verification](report/version-2-validation.md)

## Capabilities

- Mandatory, fixed-duration activities on a single-day, 30-minute grid.
- Availability, release times, deadlines, fixed appointments, precedence and participant/resource non-overlap.
- Preference optimization for generation; lexicographic repair minimizing moved activities, then total shift, then preference penalty.
- Shared repair invariants, strict model-output validation, typed extraction differences and bounded constraint-domain explanations.
- Deterministic before/after explanations with feasibility, objective and proof-status boundaries.
- Capped model calls, durable attempt records, safe resume, independent scoring, offline replay and CSV/JSON/PNG/PDF exports.
- Separate development/frozen modes, versioned exclusion registries and a localhost dashboard for inspecting saved evidence.

The inputs are synthetic. The system does not connect to real calendars or autonomously change commitments. Multi-day scheduling, participant assignment, model training and production deployment are outside the current scope.

## Architecture

| Component | Responsibility |
| --- | --- |
| Direct LLM — A | One public natural-language request → one model response → parsed schedule or feasibility prediction |
| LLM-to-Solver — B | The same public request → one extraction response → canonical specification → fixed CP-SAT compiler |
| Gold reference | Evaluator-only specification → reference feasibility and proven objective values/bounds |
| Independent validator | Arithmetic checks of each answer against gold, independent of solver compilation |
| Runner and analysis | Preflight, request accounting, immutable records, scoring, replay and figures |
| Explanation and dashboard | Read-only interpretation of solver/evaluation evidence, without new model calls |

Both approaches receive equivalent task information and, for repair, the same original schedule. Gold specifications, labels and review metadata remain evaluator-only. B receives a neutral request ID; evaluator IDs are restored locally after parsing. A solver can correctly solve an incorrectly extracted problem, so **extraction fidelity, solver proof and end-to-end validity are measured separately**.

The integrated components share one package, schema, completion interface and runner. The current live adapter supports the approved NUS SoCLaaS endpoint; another provider would require explicit integration and qualification. [Planning Sections 6–7](planning.md#system-architecture-and-data-flow) define the interfaces and formal semantics.

## Development results

The expanded SoCLaaS `qwen3.6:35b` comparison completed **200 model calls on 100 preselected cases**, using unchanged prompts and larger explicit execution limits. The packet combines 64 v2 and 36 v3 cases across 41 source families, with balanced generation/repair and SAT/UNSAT strata.

| Task | Direct A accepted | Solver-assisted B accepted |
| --- | ---: | ---: |
| Generation | 23/50 (46%) | 48/50 (96%) |
| Repair | 12/50 (24%) | 49/50 (98%) |
| Total | **35/100** | **97/100** |

Accepted answers include gold-valid schedules and correct UNSAT answers; all failures remain in denominators. B produced valid schedules on 49/50 feasible cases and detected 48/50 infeasible cases. All 25 valid B repairs attained the gold lexicographic objective. Its three failures were two omitted fixed appointments and one malformed JSON response. A correct solver result does not guarantee faithful extraction.

| Resource, 100 calls per approach | Direct A | Solver-assisted B |
| --- | ---: | ---: |
| Reported prompt tokens | 102,676 | 199,426 |
| Reported completion tokens | 22,020 | 141,129 |
| Total tokens | 124,696 | 340,555 |
| Mean model-response latency | 1.90 s | 10.12 s |
| p95 model-response latency | 2.07 s | 14.95 s |

The batch took **20 minutes 5 seconds** and reported **465,251 tokens**, with usage present for all 200 calls. CP-SAT averaged 4.69 ms across 99 executed B solves. All calls completed without provider errors, retries or output truncation. This supports the architecture on the selected development distribution and points to extraction reliability as the next improvement. Detailed strata, paired uncertainty, semantic certificates, maxima/medians and resource accounting are in the [expanded development report](report/expanded-development-100.md), [aggregate](results/summary/expanded-development-100-20260930.json) and [resource statistics](results/summary/expanded-development-100-resources-20260930.json).

**Evidence boundary:** all 100 cases come from known synthetic development generators; 14 IDs appeared in earlier live pilots. Related cases remain grouped, and only canonical wording was tested. These are development results, not held-out or production-reliability claims. The larger limits also prevent a causal comparison with older pilot scores. Fresh reviewed cases, final-model eligibility and the final study remain open.

Earlier evidence is preserved separately:

| Recorded checkpoint | Cases / calls | A / B accepted | Interpretation |
| --- | --- | --- | --- |
| [Original baseline](report/main-baseline-validation.md) | 30 / 60 | 18/30 · 25/30 | Two B requests contained label-bearing IDs |
| [Structural v2 pilot](report/yongqing-evaluation-followup.md) | 12 / 24 | 3/12 · 12/12 | All selected B request IDs exposed labels |
| [Neutral-boundary v3 pilot](report/lihao-request-boundary.md) | 12 / 24 | 5/12 · 10/12 | Corrected metadata boundary; two availability-extraction failures retained |
| [Extraction revision 3 qualification](report/yaoxiang-availability-followup.md) | 12 / 24 | 4/12 · 12/12 | Cases reused during prompt development; 48,493 reported tokens |

The separate [four-call formal-core check](report/yaoxiang-formal-followup.md) used two selected earlier failure cases. Do not pool differing prompts, inputs or budgets. Historical records and scores remain unchanged.

## Next stage: final study and submission

The [current work queue](planning.md#current-priorities-after-the-first-baseline) builds on this checkpoint:

| Work | Intended outcome |
| --- | --- |
| F1 — extraction fidelity | Regressions for the two omitted fixed appointments and malformed JSON; qualify a prompt amendment only if failure analysis justifies one, after model selection |
| F2 — model and execution contract | Qualify a candidate against the current model, record effective settings and eligibility, and add a specific backend adapter only if required |
| F3 — fresh final cases | Versioned construction/selection, complete development exclusions, independent gold/text review and explicit family/label quotas |
| F4 — freeze and study | Rehearse the frozen workflow, finalize actual review/budget decisions, then execute separate controlled, realistic and wording blocks |
| F5–F6 — evidence and delivery | Validate cross-block analysis, archive replayable evidence, write the report and rehearse the presentation |

The working study target is **600 calls**: 240 controlled canonical cases, 12 realistic cases and 48 additional renderings, each evaluated by A and B. A **312-call compact alternative** is available if family diversity, review capacity or resources do not support that target. Select the design using development evidence before final outcomes; neither count is a course requirement, a power guarantee or spending permission. See [the study design](planning.md#final-experiment-matrix-and-size-decision).

A metadata-only SoCLaaS check on 30 September listed **`qwen3.8:27b`**, `gemma4:26b` and `ornith1.5:35b` alongside the current `qwen3.6:35b`. Qualify Qwen3.8 first as a possible upgrade; its [official model card](https://huggingface.co/Qwen/Qwen3.8-27B) motivates checking it, but no project result establishes it as better. Current configurations still use the existing model. [Planning Section 9](planning.md#9-nus-soclaas-model-choice-and-execution-budget) records availability, the proposed bounded comparison, settings and course-eligibility decision. The course's frontier-model requirement must be resolved before the final freeze; an endpoint listing alone does not settle it.

Internal targets are **18 October for freeze** and **30 October for a complete report draft and reproduction package**. Course delivery is a 15-minute presentation plus five-minute Q&A in the week of 9 November, and a report due 13 November with at most ten single-column, single-spaced body pages, at least 11-point font and 1-inch margins. Verify Canvas cutoffs and feedback. [Planning Section 17](planning.md#17-rubric-evidence-and-course-delivery) maps the qualitative rubric to technical evidence, responsible-AI cases, genuine member contributions and delivery checks.

This checkpoint includes the audited integrity fixes, expanded development results and final-study plan. Historical audit receipts describe their earlier local snapshot based on `63d68d8`; use the current commit and GitHub branch state to verify publication. A clone contains source, tests, manifests and reviewed summaries; raw live records must be supplied separately in a reviewed reproduction archive.

### Li Hao F2/F6 follow-up

[The current handoff](report/lihao-f2-followup.md) records a tested 24-case model
qualification packet and versioned provider execution metadata. New frozen runs
stop on reported backend fingerprint drift; historical replay remains supported.
The authorized live qualification stopped after its first pair because the
reference model returned two serving fingerprints. Six completions including
capability checks reported 4,007 tokens; no two-model quality conclusion follows.
See the [report draft](report/study-draft.md) and [claim index](report/claim-evidence.md)
for F6 preparation and explicitly pending human/final-study work.

Prepare the packet offline from the preserved or regenerated expanded bundle:

```sh
.venv/bin/python evaluation/prepare_model_qualification.py runs/NEW-f2-input \
  --cases runs/NEW-expanded-input/cases.json
```

This emits the exact selected cases, two proposed model configurations and
reference/request preflights. It does not authorize calls. Resolve the recorded
backend-policy stop before resuming qualification; do not repeat existing attempts.

## Data and evaluation scope

| Dataset | Origin and coverage | Current use |
| --- | --- | --- |
| Legacy v1 | Six project-authored fixtures plus 24 procedural cases; 17 generation/13 repair, 28 SAT/2 UNSAT | Baseline reproduction and regression checks |
| Structural v2 | 144 procedural cases per repetition; balanced task/label strata, structural variation and three repair events at each level | Development and offline qualification |
| Challenge v3 | 108 procedural cases in nine source families; coupled repairs, contradictions and preference trade-offs | Development, pilots and the expanded 100-case comparison |
| Authored drafts | Twelve AI-assisted fictional scenarios; six generation/six repair and six SAT/six UNSAT | Development integration; human prose/gold review pending |

No public benchmark instances or real calendars have been imported. SCHEDBench, NATURAL PLAN and related work inform the methodology. The authored drafts are not independently human-written or untouched test data. [Planning Section 8](planning.md#8-benchmark-and-evaluation-design) describes provenance, construction limits, human review and the final study.

## Installation

Requirements: Python **3.12**, Git and a CPU-only macOS or Linux environment. Offline TLS tests require `openssl`; dashboard regression tests require Node.js. The dashboard itself uses no Node server or frontend build. Native Windows has not been qualified.

From your own checkout, using a POSIX shell:

```sh
git clone git@github.com:JellyPenguinnn/cs3263_group23.git
cd cs3263_group23
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation .
.venv/bin/python scripts/check_installed.py
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/scheduling --help
```

SSH requires configured GitHub access; HTTPS with your own authentication is also supported. Never embed credentials in URLs. Reinstall after source changes, or deliberately use an editable installation during development. `check_installed.py` requires a noneditable installation and compares packaged prompts, certificates and dashboard assets with the checkout. Dependency maintenance is in [planning.md](planning.md#portable-runtime-and-supported-environments).

## Run offline

No API key is required. Use new output directories so existing evidence is preserved:

```sh
# Solve a specification with real CP-SAT.
.venv/bin/scheduling solve --spec tests/examples/formal-generation.json

# Legacy integration: 180 canned attempts, including six intentional failures.
.venv/bin/python evaluation/offline_demo.py runs/quickstart-offline

# Full structural v2 integration: 144 cases × 3 renderings × 2 paths.
.venv/bin/python evaluation/v2_qualification.py runs/quickstart-v2

# Challenge v3: 108 cases × 3 renderings × 2 paths.
.venv/bin/python evaluation/v2_qualification.py runs/quickstart-v3 --version 3

# Authored drafts: 12 cases × 2 paths, canonical prose only.
.venv/bin/python evaluation/v2_qualification.py runs/quickstart-authored \
  --cases benchmarks/fixtures/realistic-drafts-v1.json
```

These workflows exercise generation/repair, both pipelines, reference checks, accounting, completed resume and replay. They use **gold-derived canned responses**, so their success is integration evidence rather than model performance.

### Dashboard and explanations

```sh
.venv/bin/scheduling dashboard --runs-dir runs --port 8876
```

Open [the local dashboard](http://127.0.0.1:8876). Select a saved run to inspect progress, results and before/after schedules. The dashboard is read-only and binds to localhost; live runs start through the CLI. For a nested qualification run, add `--run-dir runs/quickstart-authored/run`.

```sh
.venv/bin/scheduling explain --run-dir runs/quickstart-authored/run \
  --case-id realistic-draft-07 --approach solver_augmented --format json
```

Explanations distinguish the extracted problem's proof from gold acceptance and report participant inconvenience without claiming fair allocation. For a standalone saved solve, use `--spec problem.json --result result.json` and, for repair, `--original-schedule original.json`. Newly saved results bind proof claims to their exact specification and repair context; mismatches are rejected. Legacy unbound standalone results retain candidate validation but cannot establish proof correspondence to a supplied problem. Historical checked-run replay remains supported.

## SoCLaaS and bounded live runs

```sh
[ -e .env ] || cp .env.example .env
chmod 600 .env
```

Configure your authorized credential locally. Never put keys in chat, source, issues or logs. The CLI reads process environment variables; it does not automatically load `.env`:

```sh
set +x
set -a
. ./.env
set +a
```

The environment uses `SOCLAAS_BASE_URL`, `SOCLAAS_API_KEY` and `SOCLAAS_MODEL`. Live configuration selects an explicit model; `default` is only a bootstrap alias. Verify current availability/capabilities and agree the request/token budget before each new run or session. **Previous pilot allowances are consumed.** A saved configuration or key grants no new spending permission. TLS certificate and hostname verification remain enabled. Current requests explicitly configure the model and output limit but leave sampling/reasoning controls to server defaults. Qualification must record those defaults or add verified options; do not assume temperature zero, JSON mode or an arbitrary compatible endpoint is supported.

### Expanded development profile

`configs/development/expanded-development-100.json` defines 200 calls, 16,384 output tokens per call, 30/600-second connect/read timeouts, no retries, 30-second B solves and 60-second references. The output reservation ceiling is 3,276,800 tokens, with input tokens additional. This is a generous tested profile for the selected packet, not blanket authorization for future calls. **The completed 200-call allowance is consumed.**

```sh
.venv/bin/python evaluation/prepare_development_expansion.py runs/NEW-expanded-input
.venv/bin/python evaluation/v2_qualification.py runs/NEW-expanded-offline \
  --cases runs/NEW-expanded-input/cases.json
```

Preparation, reference checks and canned qualification are offline. With a new execution authorization:

```sh
.venv/bin/scheduling evaluate-batch --allow-live \
  --cases runs/NEW-expanded-input/cases.json \
  --config configs/development/expanded-development-100.json \
  --run-dir runs/NEW-expanded-live
```

### Legacy baseline reproduction

The legacy configuration is paired with the legacy 30-case bundle. Generate references and inspect the request estimate offline:

```sh
.venv/bin/scheduling benchmark-generate --output runs/NEW-input/cases.json
.venv/bin/scheduling evaluate-plan --cases runs/NEW-input/cases.json \
  --config configs/development/main-baseline.json --output runs/NEW-input/preflight.json
```

It specifies 60 serial calls, at most 8,192 requested output tokens per call, no retries, a 180-second read timeout, ten seconds per B solve and thirty seconds per reference. Input tokens are additional. With a newly authorized cap:

```sh
.venv/bin/scheduling evaluate-batch --allow-live \
  --cases runs/NEW-input/cases.json --config configs/development/main-baseline.json \
  --run-dir runs/NEW-live
```

Do not apply a twelve-case pilot configuration to the full v2/v3 matrix. Create a separate configuration and cap for a different case set. Progress goes to stderr; a completed batch returns 0 even if model answers were rejected. Stopped/exhausted batches return 2. Provider failures stop without hidden retries. Resume requires a matching contract; changed source/configuration needs a new run, and uncertain interrupted requests require reconciliation.

### Replay and final-study controls

```sh
.venv/bin/scheduling evaluate-replay --run-dir runs/NEW-live \
  --export-dir artifacts/NEW-live --figures
```

Replay requires no credentials or new model requests. A fresh clone contains aggregate evidence, not raw live runs: obtain the reviewed synthetic archive/checksum for exact historical replay, or use the canned workflows for independent integration checks.

`freeze-draft` creates an intentionally non-runnable configuration until review, eligibility and authorization references are supplied. See `scheduling freeze-draft --help` and [planning Section 8](planning.md#8-benchmark-and-evaluation-design). The versioned registry identifies scheduling structure independently of calendar presentation, while provenance hashes retain exact inputs. Legacy unversioned registries and frozen protocols cannot authorize new runs. Rebuild registries from source cases rather than relabelling old digests; retain old archives for replay.

The current registry is [`development-hard-fingerprints-v2-20260930.json`](benchmarks/manifests/development-hard-fingerprints-v2-20260930.json), rebuilt from 22 named bundles and 300 known structures. Supply this versioned object to `freeze-draft --development-registry`; protocol format 2.0 embeds it as `development_registry`. New benchmark manifests must declare `slot-graph-v2`. Historical protocols remain replayable, but cannot be resumed or used for new execution under the changed source contract.

To rebuild from preserved inputs, use repeatable `--bundle` and `--archive-bundle` arguments; include every known development source, including prior pilots. For example, this command creates a **limited registry for the named authored bundle only**:

```sh
.venv/bin/python evaluation/development_registry.py \
  --bundle benchmarks/fixtures/realistic-drafts-v1.json \
  --output artifacts/NEW-authored-registry.json
```

Do not substitute that limited example for the project's complete registry. Existing output files are never overwritten; raw archives referenced by the full registry must be obtained separately to rebuild it.

No final study is currently approved or executed. Human review, fresh inputs and complete development exclusions, an eligible qualified model, the final protocol and an explicit cap remain prerequisites. Development generators do not produce the planned fresh final packet automatically. F3 implements that preparation; F4 uses separate configurations for canonical and selected-language conditions, and F5 verifies their compatibility before analysis. These planned additions are not commands available in the current CLI.

## Verification

The [checkpoint readiness audit](report/checkpoint-readiness.md) records **521 passing Python tests and 7 passing frontend tests**, a fresh 200-attempt canned integration run, exact replay of 332 saved live attempts and all 100 expanded dashboard cases. It connects those checks to the original teaching materials and proposal. Canned success verifies integration; final scientific and submission gates remain open. Documentation updates do not constitute a new live benchmark or a new platform qualification.

[Version 2 validation](report/version-2-validation.md) records the exact source hashes, environments, checks and residual limits for the current implementation. It includes regression tests for proof/input correspondence and calendar-invariant development exclusions, installed-package checks, full canned integration, historical replay, explanations and dashboard consumers.

```sh
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
```

Routine tests are offline. Native macOS TLS tests require OS certificate-service access; investigate environment errors without disabling verification. Hosted CI status is separate from local macOS/Linux qualification. Passing tests does not establish human review or final scientific conclusions.

## Repository layout

```text
src/scheduling/
  schema.py, solver.py, objectives.py  # canonical types, CP-SAT and repair
  domain_analysis.py                  # bounded constraint reasons
  validation.py                       # independent gold checks
  explanations.py                     # proof-aware evidence formatting
  providers/, pipelines/              # shared transport and A/B paths
  evaluation/                         # cases, manifests, frozen controls, scoring
  dashboard/                          # read-only server and static assets
prompts/                              # direct and extraction templates
configs/development/                  # bounded settings and verification receipts
configs/experiments/                  # final experiment configurations when approved
benchmarks/                           # fixtures, provenance and exclusion registries
evaluation/                           # offline qualification entry points
scripts/check_installed.py            # installed asset verification
tests/                               # unit, integration and frontend checks
results/summary/                      # reviewed development aggregates
report/, presentation/               # methods, validation, figures and demo guidance
.github/workflows/                    # installed offline CI
```

Credentials, virtual environments, raw runs and large generated artifacts are ignored. Keep small fixtures, manifests, lockfiles and reviewed summaries versioned.

## Contributing and agent workflow

The team is Tea Li Hao, Tham Yao Xiang and Woo Yong Qing. Existing member branches and component contacts are recorded in the plan for coordination; the next-stage queue describes deliverables rather than a new baseline job split.

Read [AGENTS.md](AGENTS.md) and [the current work plan](planning.md#current-priorities-after-the-first-baseline). Preserve existing work, incorporate current `origin/main` and use small reviewed changes. The core components are integrated; prioritize F1–F6 and verify their dependencies. Preserve unpublished local work when comparing with GitHub.

To start with a coding agent, replace `[name]` with your name:

> I am [name]. Read README.md, AGENTS.md and planning.md in full. Inspect the current implementation and Git status, and ensure my working branch incorporates the latest GitHub main while preserving existing work.
>
> Use Sections 4–5 of planning.md to confirm the next incomplete F1–F6 deliverable within my scope. Implement and verify it, then continue through unblocked agreed work while prerequisites and authorization are available. Build on the integrated baseline and avoid rebuilding completed components.
>
> Follow the architecture and formal reasoning guidance in Sections 6–7, the relevant evaluation and provider requirements in Sections 8–9, and the acceptance gates in Section 11. Distinguish required deliverables from optional optimizations.
>
> Ask focused questions only for consequential unresolved decisions or missing setup details; reuse previous confirmations and make routine engineering choices independently. Ask about credential availability without requesting secret values. Continue independent work when another task is blocked.
>
> Carry the work through implementation and relevant verification. Report completed changes, checks and observed results, remaining dependencies, and the next concrete task. Follow AGENTS.md for Git publication, live-call authorization, scientific integrity and handoff.

Members must review and understand the system, record actual contributions and disclose AI assistance. Human sign-off and teaching-team decisions cannot be supplied by an agent.

## Responsible AI, references and license

Use synthetic data and preserve privacy. Never silently relax hard requirements. Explain objective trade-offs and unequal participant inconvenience without claiming fair workload allocation. Responsible-AI analysis, source attribution and honest human/AI contribution records are course deliverables.

[Planning's source-grounding section](planning.md#16-source-grounding) connects the design to SCHEDBench, NATURAL PLAN, formalization research and release-matched OR-Tools documentation. Public data adaptation and extra research arms remain optional, separately scoped work.

A distribution license has not yet been selected. Third-party dependencies and cited materials retain their respective licenses.
