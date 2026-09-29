# Dynamic Constraint-Aware Scheduling

**CS3263 Foundations of Artificial Intelligence · Group 23 · NUS AY2026/27 Semester 1**

A research system for generating schedules and repairing them after requirements change. It compares a language model that produces a schedule directly with the same model translating the request into a specification solved by OR-Tools CP-SAT. An independent validator checks both answers against the original requirements.

**Status:** usable end-to-end development baseline. Both pipelines, minimum-disruption repair, evaluation/replay, and a read-only dashboard are implemented. The final benchmark, human review and course evaluation are still in progress. Core delivery target: **30 October 2026**.

[Development plan](planning.md) · [Agent/contributor instructions](AGENTS.md) · [Baseline evidence](report/main-baseline-validation.md)

## Capabilities and scope

- Fixed-duration, mandatory activities on a single-day, 30-minute grid.
- Availability, deadlines, fixed appointments, precedence, and participant/resource non-overlap.
- Preference optimization for new schedules.
- Repair after a blocked interval, tightened deadline or changed fixed appointment, minimizing moved activities, then total time shift, then preference penalty.
- Independent feasibility/objective checks, extraction diagnostics, bounded model calls, durable records, offline replay and result exports.
- Local dashboard for run monitoring, result inspection and before/after schedule comparison.

The system uses synthetic scheduling problems. It does not connect to real calendars or autonomously change commitments. Multi-day scheduling, participant assignment and model training are outside the current scope.

## Architecture

| Component | Input → output | Role |
| --- | --- | --- |
| Direct LLM — A | Public natural-language description → schedule or feasibility claim | Evaluated approach |
| LLM-to-Solver — B | Same public description → structured specification → CP-SAT → schedule/status | Evaluated approach |
| Gold reference | Evaluator-only specification → CP-SAT reference status/objective | Feasibility and optimality reference |
| Independent validator | Model answer + gold specification → validity, violations and objective values | Checks the original request, independently of solver compilation |
| Runner and replay | Frozen run inputs + attempts → verified records, metrics and figures | Accounting and reproducibility |
| Dashboard | Saved run artifacts → read-only inspection | Development and demonstration |

Both approaches receive the same task information and, for repair, the same original schedule. Gold labels, constraints and solutions remain evaluator-only. A solver can solve an incorrectly extracted problem correctly, so solver success alone is not end-to-end correctness. [System design and interfaces](planning.md#system-architecture-and-data-flow) describe the boundaries in detail.

## Baseline results and limitations

The saved 29 September development run used `qwen3.6:35b`, 30 cases and one call per approach per case. Accepted answers include valid schedules and correct UNSAT predictions; failures remain in the denominator.

The inputs are **6 project-authored fixed fixtures + 24 procedurally generated synthetic cases**; no public benchmark instances or real calendars were imported. The live responses came from SoCLaaS. SCHEDBench and NATURAL PLAN currently serve as research references. See [dataset provenance and the next evaluation design](planning.md#dataset-provenance--verified-29-september-2026).

| Task | Direct A | Solver-assisted B |
| --- | ---: | ---: |
| Generation | 12/17 | 13/17 |
| Repair | 6/13 | 12/13 |
| All development cases, descriptive | 18/30 | 25/30 |

All 60 requests completed; reported usage was 117,976 tokens. Currency cost is unavailable. Current-source offline replay reproduces the [tracked summary](results/summary/main-development-20260929.json) exactly. The [validation report](report/main-baseline-validation.md) records the configuration, failures and provenance.

These are **development results**, not evidence of general superiority. The set has 28 SAT and two UNSAT cases, no live language-robustness evaluation, and known generator limitations: redundant precedence edges, repair events tied to difficulty levels, and seeds that vary weights rather than hard scheduling structures. [The benchmark audit](planning.md#development-benchmark-audit--29-september-2026) defines the required improvements.

The runner currently supports development cases only. Final experiments require a reviewed frozen-evaluation mode, fresh benchmark data, human review, and an eligible primary model or teaching-team acceptance of an alternative. Development scheduling inference remains SoCLaaS-only.

## Getting started

### Requirements

- Python **3.12** and Git; CPU-only execution, no local GPU required.
- macOS or Linux. The earlier installed baseline was verified on ARM64 for both; current audit/platform details are below. Native Windows support is not verified.
- An `openssl` executable for offline TLS tests.
- Node.js for dashboard development tests only; Node 20 was used in the audit. The dashboard itself needs no Node server or frontend build.
- An authorized SoCLaaS credential and agreed spending/request cap only for live model calls.

### Install and verify

Run these POSIX shell commands from your own checkout:

```sh
git clone git@github.com:JellyPenguinnn/cs3263_group23.git
cd cs3263_group23
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation .
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/scheduling --help
```

The SSH URL requires configured GitHub SSH access. HTTPS with your own authentication is also supported; never embed a credential in the URL. Dependencies, including OR-Tools and plotting tools, are pinned in `requirements.lock`. Reinstall after source edits, or deliberately use `-e .` for editable development. Dependency maintenance is described in [planning.md](planning.md#portable-runtime-and-supported-environments).

### Try the system offline

No API key is required. From the repository root, choose unused output paths:

```sh
# Solve a tiny specification with real CP-SAT.
.venv/bin/scheduling solve --spec tests/examples/formal-generation.json

# Exercise both pipelines, validation, resume, replay and figure export with canned responses.
.venv/bin/python evaluation/offline_demo.py runs/quickstart-offline
```

The demo contains 180 canned attempts and deliberately includes failures. It makes **zero model calls** and is not a model benchmark. Results and exports are written beneath the chosen directory; rerunning with an existing directory is refused to preserve evidence. Small direct-component examples are in [presentation/README.md](presentation/README.md); its original handoff notes are historical.

### NUS SoCLaaS configuration

```sh
[ -e .env ] || cp .env.example .env
chmod 600 .env
```

Edit `.env` locally to set your authorized `SOCLAAS_API_KEY`. The template supplies `SOCLAAS_BASE_URL` and a bootstrap `SOCLAAS_MODEL` alias. Never paste keys into chat, source, issues or logs. The CLI reads process environment variables and does not automatically load `.env`:

```sh
set +x
set -a
. ./.env
set +a
```

Live commands/configuration select an explicit model; the saved development configuration uses `qwen3.6:35b`. Verify model availability and provider capabilities before a new pilot. An existing configuration or saved key is not a new spending authorization. [Provider and budget rules](planning.md#9-nus-soclaas-and-execution-budget) distinguish development access from final-model eligibility.

Certificate and hostname verification remain enabled. The Linux client includes ordinary issuer certificates to complete the service's previously incomplete chain; macOS uses native trust. If verification fails, investigate the chain/OS trust service rather than disabling TLS. [Issuer provenance](configs/development/tls-issuer-provenance.json) and the baseline report document the implementation.

### Run the integrated development baseline

First generate and validate the 30 development references without credentials:

```sh
.venv/bin/scheduling benchmark-generate --output runs/NEW-input/cases.json
.venv/bin/scheduling evaluate-plan --cases runs/NEW-input/cases.json \
  --config configs/development/main-baseline.json --output runs/NEW-input/preflight.json
```

The [saved configuration](configs/development/main-baseline.json) allows 60 serial calls, 8,192 requested output tokens per call, no retries, a 180-second read timeout, 10 seconds per B solve and 30 seconds per reference. Input tokens are additional. **The original 60-call allowance is consumed.** After obtaining a new cap and loading your local environment, use a new run directory:

```sh
.venv/bin/scheduling evaluate-batch --allow-live \
  --cases runs/NEW-input/cases.json --config configs/development/main-baseline.json \
  --run-dir runs/NEW-live
```

Progress is written to stderr and the final outcome to stdout. A completed batch returns 0 even when model answers are rejected. Stopped/exhausted batches return 2. Provider failures stop the batch without hidden retries. Resume reuses completed records only under the matching run contract; changed source/configuration requires a new run, and uncertain interrupted requests require reconciliation.

Recompute saved results without model calls:

```sh
.venv/bin/scheduling evaluate-replay --run-dir runs/NEW-live \
  --export-dir artifacts/NEW-live --figures
```

A fresh clone contains aggregate evidence, not the private raw live run. To replay `main-baseline-20260929-01`, obtain the reviewed synthetic archive and checksum from the team; use the canned demo when that archive is unavailable. Do not substitute canned results for live evidence.

### Scheduling dashboard

```sh
.venv/bin/scheduling dashboard --runs-dir runs --port 8876
```

Open `http://127.0.0.1:8876` and select a run. The dashboard refreshes saved progress, shows metrics with denominators, and lets you inspect schedules, violations and extraction diagnostics. It is read-only, binds to localhost and needs no credentials. Live batches run separately through the CLI. A run lock indicates possible activity, not proof that the process is still running.

## Verification

The audit of code at `c2eeffc` on 29 September passed **284 Python tests, three frontend tests, JavaScript syntax checking, dependency checks, all 30 development references, and exact replay of all 60 saved records**. Source tests used `PYTHONPATH=src`. Native macOS TLS tests need access to the OS certificate service; a sandbox restriction was isolated and the complete suite passed with that access.

The earlier installed macOS ARM64/Linux ARM64 baseline passed 278 tests. That historical receipt does not certify every subsequent dashboard change on Linux. Hosted CI is configured for Ubuntu/macOS; its remote status was not inspected in the audit.

For dashboard changes, additionally run:

```sh
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
```

Routine tests are offline. Live checks must be selected explicitly under a confirmed cap.

## Repository layout

```text
src/scheduling/
  schema.py, solver.py, objectives.py  # canonical types and CP-SAT formulation
  validation.py                      # independent gold checks
  providers/                         # SoCLaaS, TLS and accounting
  pipelines/                         # direct and solver-assisted paths
  evaluation/                        # generator, scoring, runner, replay, figures
  dashboard/                         # read-only server and static UI
prompts/                             # direct and extraction prompts
configs/development/                 # development settings and receipts
configs/experiments/                 # future frozen experiment configurations
benchmarks/                          # synthetic fixtures and manifests
evaluation/offline_demo.py           # canned integration demonstration
tests/                               # unit, integration and frontend checks
results/summary/                     # reviewed aggregate evidence
report/                              # method notes, validation report and figures
presentation/                        # demo and presentation materials
.github/workflows/                   # installed offline CI
```

Local credentials, environments, raw runs and generated artifacts are ignored. Small fixtures, configurations, lockfiles and reviewed summaries remain trackable.

## Contributing and agent workflow

| Member | Main responsibility | Branch |
| --- | --- | --- |
| Tea Li Hao | Direct baseline, provider, packaging/CLI/CI and demo | `lihao-llm-baseline` |
| Tham Yao Xiang · leader | Schema, solver/repair, extraction and coordination | `yaoxiang-formal-core` |
| Woo Yong Qing | Benchmark, independent validator, runner and analysis | `yongqing-evaluation` |

Read [AGENTS.md](AGENTS.md) and the [current work plan](planning.md#current-priorities-after-the-first-baseline). Use your own clone and assigned branch; merge the latest `origin/main` before extending an older member branch. Preserve existing work and use small reviewed PRs. Shared scientific changes need coordination; routine owned engineering choices do not require team-wide approval.

To start with a coding agent, replace `[name]` with Li Hao, Yao Xiang, or Yong Qing:

> I am [name]. Read README.md, AGENTS.md and planning.md in full. Inspect the current implementation and Git status, and ensure my working branch incorporates the latest GitHub main while preserving existing work.
>
> Identify my remaining responsibilities in Sections 4–5 of planning.md. Implement and verify the next incomplete work package, then continue through my other unblocked assigned improvements while prerequisites and authorization are available. Build on the integrated baseline and avoid rebuilding completed components.
>
> Follow the architecture and formal reasoning guidance in Sections 6–7, the relevant evaluation and provider requirements in Sections 8–9, and the acceptance gates in Section 11. Distinguish required deliverables from optional optimizations.
>
> Ask focused questions only for consequential unresolved decisions or missing setup details; reuse previous confirmations and make routine engineering choices independently. Ask about credential availability without requesting secret values. Continue independent work when another task is blocked.
>
> Carry the work through implementation and relevant verification. Report completed changes, checks and observed results, remaining dependencies, and the next concrete task. Follow AGENTS.md for Git publication, live-call authorization, scientific integrity and handoff.

Members must review and understand the work, record actual contributions and disclose AI assistance. The next priorities are benchmark refinement, contract review, development failure analysis and frozen-evaluation support; see [implementation work packages](planning.md#implementation-work-packages).

## Responsible AI, references and license

Use synthetic data; do not publish private calendars or identifiers. Preserve hard requirements, explain actual violations and objective trade-offs, and assess unequal participant inconvenience. The system does not claim to solve fair workload allocation. Responsible-AI analysis and honest human/AI contribution records are course deliverables.

Research and design sources include [SCHEDBench](https://arxiv.org/abs/2608.00991), [NATURAL PLAN](https://arxiv.org/abs/2406.04520), [Hao et al.](https://aclanthology.org/2025.naacl-long.176/) and [OR-Tools](https://developers.google.com/optimization/cp/cp_solver). The [source-grounding section](planning.md#16-source-grounding) maps these and additional research to specific project decisions. [SoCLaaS documentation](https://dochub.comp.nus.edu.sg/cf/guides/soclaas/start) may require institutional access.

A distribution license has not yet been selected. Third-party dependencies and cited materials retain their respective licenses.
