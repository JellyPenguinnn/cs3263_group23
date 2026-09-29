# Dynamic Constraint-Aware Scheduling

**CS3263 Foundations of Artificial Intelligence · Group 23 · NUS AY2026/27 Semester 1**

A research project comparing direct language-model scheduling with language-model-to-constraint-solver scheduling. We study both generating a new schedule and repairing an existing schedule after requirements change, while minimizing unnecessary disruption.

**Integrated baseline on `main` (29 September 2026):** all three member contributions are merged. The CLI connects direct generation/repair, extraction plus CP-SAT, independent gold validation, bounded live batches, durable records, replay, metrics and figures. Fresh installed macOS ARM64 and Linux ARM64 checks pass **278 tests**. A real **60-call `qwen3.6:35b` development run** completed with HTTP 200 for every request; the validator accepted 18/30 direct answers and 25/30 solver-augmented answers. Failures are retained. This validates the operational baseline, not perfect model accuracy or the frozen course experiment. See [the baseline validation report](report/main-baseline-validation.md).

## Research questions

- When does direct LLM reasoning produce complete, feasible schedules?
- How does LLM-to-solver performance change with constraint interactions, resource contention, and available slack?
- How much error comes from translating language into constraints versus solving those constraints?
- Can either approach repair schedules with minimal changes, and remain reliable under equivalent paraphrases and constraint reorderings?

## Approaches

| Path | Input and output | Role |
| --- | --- | --- |
| Direct LLM | Natural-language problem → structured schedule or feasibility claim | Evaluated approach A |
| LLM-to-Solver | Same problem → structured specification → OR-Tools CP-SAT → schedule/status | Evaluated approach B |
| Gold-to-Solver | Human-checked specification → CP-SAT → reference status/objective | Evaluation reference; not a natural-language competitor |

Both approaches are checked by an independent validator against the gold specification. A solver-valid answer to an incorrectly translated problem does not count as a correct answer to the original problem.

The core covers fixed-duration activities, availability, deadlines, fixed commitments, precedence, participant/resource non-overlap, preferences, and minimum-disruption repair. A small demo UI and verifier-feedback correction are stretch work. Live calendar integrations are outside project scope.

## Getting started

```bash
git clone git@github.com:JellyPenguinnn/cs3263_group23.git
cd cs3263_group23
```

1. Read [planning.md](planning.md) for scope, interfaces, ownership, experiments, and milestones.
2. Read [AGENTS.md](AGENTS.md) before changing files or using a coding agent.
3. Each member uses a separate local clone. Before an agent clones, switches branches, or implements work, have it confirm your identity, local path, assigned scope/branch, credential setup method, and intended milestone using [the onboarding instructions](AGENTS.md#member-onboarding-and-clarification). Already confirmed details do not need to be repeated.
4. Fetch and switch to the confirmed member branch from the table below. For unresolved choices, the agent should explain the options and wait for your answer before dependent work. Supply API keys only through local secret configuration, never through chat.

The runtime uses CPU-only Python 3.12 and remote SoCLaaS inference. The installed package has been verified in fresh macOS ARM64 and Linux ARM64 environments, including all development references and credential-free HTTPS. Linux replay reproduces the saved live metrics without credentials. Hosted CI repeats installation/tests/preflight on Ubuntu and macOS; its remote result is not claimed here. Model access and final-model course eligibility remain separate checks.

### Install and verify (POSIX shell, Python 3.12)

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation .
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/scheduling --help
```

`requirements.lock` pins and hashes the runtime, test/build tools and agreed OR-Tools dependency. The core pins are HTTPX 0.28.1, certifi 2026.7.22, truststore 0.10.4 and OR-Tools 9.14.6206; tests use pytest 8.4.2; optional figure export adds Matplotlib 3.10.8. The scheduling compiler and exhaustive tiny objective checks now use this locked OR-Tools version. The lockfile is generated with pip-tools 7.5.1:

```sh
pip-compile --allow-unsafe --extra dev --extra solver --extra plots --generate-hashes --strip-extras --no-emit-index-url --no-emit-trusted-host --output-file requirements.lock pyproject.toml
```

Run lock regeneration only when intentionally updating dependencies; normal installation uses the existing lock. Tests use synthetic data and injected HTTP transports; an automatic fixture blocks network connections.

### Implemented commands and integration boundary

- `scheduling parse-direct RESPONSE --activity-id A --activity-id B`: check strict JSON and public activity coverage. SAT is an unvalidated claim, not proof of feasibility.
- `scheduling direct-offline`: exercise the generation/repair prompt and parser using a saved canned response. See [the two runnable demos](presentation/README.md).
- `scheduling provider-smoke --allow-live --model default`: explicitly live, one model listing plus at most one completion, `max_tokens=32`, no retries. Requires prior cap authorization and environment credentials.
- `scheduling direct-live --allow-live --model MODEL --max-tokens N --text-file PUBLIC_TEXT --task-type generation --activity-id A --output runs/NEW_FILE.json`: explicitly live, one completion with no retries. Repair additionally requires `--original-schedule FILE`. The output parent must exist, and the output file must not already exist. This is a component check, not batch evaluation or resume.

- `scheduling solve --spec tests/examples/formal-generation.json`: solve an explicit specification offline. Repair also requires `--original-schedule tests/examples/formal-original.json` with the repair spec.
- `scheduling solver-offline --view tests/examples/generation-view.json --response-file tests/examples/formal-generation.json`: one canned extraction through real CP-SAT. Both commands accept `--time-limit`, `--seed`, `--workers`, and an optional new `--output` path.

The merged baseline passes **278 tests** in this checkout and in installed macOS/Linux packages, plus `pip check` and the 30-case reference preflight. TLS tests use the local `openssl` executable and socket pairs, without a live network. CP-SAT is a required runtime dependency; the older `solver` extra remains accepted for compatibility. Use `-e .` instead of `.` only when intentionally developing an editable installation.

The solver API, strict wire format, repair proof handling, limitations and teammate handoff are in [the formal-core notes](report/yaoxiang-method-notes.md). The schema is a shared draft, not a completed team freeze. Install the hashed lock above to include the solver dependency.

Provider and direct component interfaces are in `src/scheduling/providers/` and `src/scheduling/pipelines/direct.py`. `complete(messages, model_config) -> ModelResponse` is available as a convenience function or a provider method. It preserves individual attempts and missing usage. Share an explicit `RequestBudget` across serial calls to enforce request and requested output-token caps. This does not cap input tokens or currency. Default retries are disabled; retry configuration never overrides a budget.

`request_direct(...) -> DirectAttempt` takes public text, public activity IDs and optional original schedule, plus an injected `complete` callable. Its result retains raw completion text, declared/parsing status, attempt accounting, and prompt/config hashes. `DirectAttempt` and `DirectParse` are component records, not duplicate canonical scheduling types. Yao Xiang supplied draft canonical types, and the explicitly authorized `run_direct(nl_view, model_config)` adapter now wraps this component. Yong Qing implemented independent gold validation and batch/metrics/replay; teammate contract review remains required. No placeholder commands for those components are exposed.

A live single-case output is created with mode 600 before requesting, so interruption remains visible; completion replaces it atomically. Reusing an output filename refuses another call. Completed outputs remain private/ignored under `runs/`; the batch runner preserves immutable manifests and resumes completed records without new calls. Treat arbitrary saved model outputs as untrusted data.

The current direct JSON output contract is provisional for team review: exactly `status` and `schedule`; SAT carries a list of `{activity_id, start_slot}` objects, while UNSAT/UNKNOWN carry `null`. Starts must be nonnegative integers. Markdown fences, duplicate JSON keys, extra fields, and missing/duplicate/invented activities are rejected. Normalization only sorts entries by ID. Full schedule semantics require independent validation.


### Run the integrated development baseline

The tracked [development configuration](configs/development/main-baseline.json) selects `qwen3.6:35b`, 60 serial requests, one canonical rendering per case, one attempt per approach, 8,192 maximum output tokens per call, a 180-second read timeout, 10 seconds per B solve and 30 seconds per gold reference. These limits are configuration, not ongoing spending authorization. Obtain a fresh cap before a new live run. Input tokens are additional; currency cost is unavailable.

Run from the repository after installation. Choose unused output/run names:

```sh
# Generate all 30 cases and check their gold references without credentials.
.venv/bin/scheduling benchmark-generate --output runs/NEW-input/cases.json
.venv/bin/scheduling evaluate-plan --cases runs/NEW-input/cases.json \
  --config configs/development/main-baseline.json --output runs/NEW-input/preflight.json

# After the run's cap is authorized, load the ignored local credential.
set +x
set -a
. ./.env
set +a
.venv/bin/scheduling evaluate-batch --allow-live \
  --cases runs/NEW-input/cases.json --config configs/development/main-baseline.json \
  --run-dir runs/NEW-live

# Recompute validation, tables and figures from saved live responses; no model calls.
.venv/bin/scheduling evaluate-replay --run-dir runs/NEW-live \
  --export-dir artifacts/NEW-live --figures
```

Progress events go to stderr; the final machine-readable outcome goes to stdout. A completed run returns exit code 0, including legitimately rejected model answers. Budget exhaustion, provider stops and invalid inputs return 2. Authentication, rate-limit, TLS, timeout and HTTP failures stop the batch; there are no hidden retries or canned substitutes. A completed rerun with identical source/configuration/input reuses its records. A changed source, prompt or setting requires a new run ID. Interrupted reservations require explicit reconciliation.

Architecture: evaluator-only cases → common public rendering → A: direct model → strict schedule parser; B: extraction model → strict schema → fixed CP-SAT compiler. Both results then enter the independent gold validator → immutable attempt records → replay/metrics/figures. Gold references never enter either model prompt. An incorrect extraction can yield a solver-valid schedule; independent gold checking remains mandatory.

The actual run `runs/main-baseline-20260929-01/` and its frozen source/input archive remain private/ignored. [The tracked aggregate receipt](configs/development/main-baseline-verification.json) and [validation report](report/main-baseline-validation.md) record provenance and observed failures. A 28-SAT/2-UNSAT development set is not the balanced held-out matrix. Human-written realistic cases, wording review, final-model eligibility, the evaluation freeze and final experiments remain open.

`evaluation/offline_demo.py` remains available for testing/rehearsal and is explicitly labelled canned. It is not substituted for the live evidence above. Single-spec solving, validation and direct component commands remain available through `scheduling --help`.

### Start with a coding agent

After cloning, open this repository folder in your coding agent and use this prompt, replacing the name:

> I am [Li Hao / Yao Xiang / Yong Qing]. Read the full `README.md`, `AGENTS.md`, and `planning.md` in this repository. Confirm any missing onboarding details with me, then implement and test my assigned part of `planning.md` on my member branch. Start with Section 5 and continue through my applicable milestones; do not stop at another plan. Ask focused questions or offer choices when a decision is unresolved, and continue independent work while waiting. Follow the repository's verification and handoff rules.

Use the exact filename casing above, including `AGENTS.md`, on case-sensitive systems. The agent should derive your responsibilities from the plan; you do not need to rewrite the technical specification in the prompt. Git and repository access are needed to clone; pushing also requires write access. The SSH clone command assumes your GitHub SSH access is configured; otherwise use the repository's HTTPS clone URL with your own GitHub authentication. Never put credentials in a clone URL.

The [decision guide](planning.md#decision-guide-for-members-and-agents) separates course requirements, shared project decisions, provisional experiments, and routine engineering choices; the following implementation defaults give agents a practical starting direction.

The initial onboarding answers establish the local path, branch, work scope, and allowed Git actions. The agent then implements in small verified increments. If a teammate's component is pending, it follows the dependency guidance in Section 5. For a later session, use:

> Continue my assigned work. Read the three project documents, inspect my branch and existing changes, and use the latest handoff and actual verification evidence to resume from the next incomplete task. Ask me only for missing or changed decisions.

The plan contains the technical information needed to start; the original course documents need not be available at another member's local path. New teaching-team feedback must still be reconciled with the plan. Members review the agent's work, coordinate shared decisions, and understand the implementation; agent output alone is not proof that an acceptance gate passed.

### NUS SoCLaaS configuration

**Scheduling-model inference during development uses SoCLaaS only; no frontier-model access is needed to begin implementation or development pilots.** This does not restrict the coding assistant used to develop the software. Final evaluation model selection is a separate milestone by 18 October, before held-out experiments. The course requires a frontier-model comparison unless the teaching team accepts an alternative; SoCLaaS access alone does not establish that acceptance.

The provider requires certificate and hostname verification, disables environment proxies and redirects, and never globally patches SSL. macOS uses native truststore verification. Linux uses certifi roots plus two packaged ordinary issuer certificates because the current server omits its intermediate chain. Partial-chain trust is explicitly disabled: those issuers cannot become new trust anchors. The certificates came from [Let's Encrypt's official chain publication](https://letsencrypt.org/certificates/); [source URLs, fingerprints and validity](configs/development/tls-issuer-provenance.json) are recorded. See [OpenSSL's trust-anchor rules](https://docs.openssl.org/3.0/man1/openssl-verification-options/). Credential-free HTTP 200 checks passed on both operating systems.

The service should still send its complete chain. Recheck the supplement if its issuer changes or before YE2 expires on 2 September 2028; never disable verification. The prior four-call TLS failures and earlier native-macOS receipt remain historical evidence. No `.env` changes are needed for this fix.

Configure access to the NUS SoCLaaS API:

```bash
# Only create .env if it does not already exist.
[ -e .env ] || cp .env.example .env
chmod 600 .env
```

Edit `.env` locally and supply your own authorized key. The file is ignored by Git. Do not paste keys into source files, commits, screenshots, issue descriptions, prompts, or logs.

For a POSIX shell, explicitly load the file before a connectivity check:

```bash
set -a
. ./.env
set +a
curl --fail --silent --show-error \
  -H "Authorization: Bearer ${SOCLAAS_API_KEY}" \
  "${SOCLAAS_BASE_URL}/models"
```

This lists models and does not run a scheduling experiment. Avoid shell tracing (`set -x`), verbose HTTP logs, and publishing raw provider responses. `SOCLAAS_MODEL=default` is a bootstrap alias; choose and record a verified development model ID before scheduling pilots. Keep development and final evaluation configurations and results separate. Available models, quotas, and advanced request features must be checked live. The CLI reads process environment variables; it does not automatically load `.env`. Load it explicitly with the POSIX steps above, without shell tracing.

Connectivity verified on **28 September 2026**: authenticated model listing and one tiny chat completion succeeded; `default` returned `qwen3.6:35b`. This verifies access only, not scheduling performance or suitability for the course's frontier-model comparison. Final evaluation suitability or teaching-team approval must be established before the main experiment is frozen; this does not block SoCLaaS development.

### Development evidence — 29 September 2026

The approved check made one model-list request and one tiny completion using `default`. The backend was `qwen3.6:35b`, HTTP 200, with 16 input/3 output tokens. The reply did **not** exactly match the requested `OK`; access succeeded, exact acknowledgement did not. No retry was made.

Li Hao then authorized two separate synthetic direct-component calls using explicit `qwen3.6:35b`, 1,024 output tokens each and no retries. Both returned complete parseable SAT schedules; reported usage was 844 input + 96 output = 940 tokens. The tiny schedules also agree with the hand calculation in [the demo notes](presentation/README.md), but have not passed the pending independent validator. The cap is consumed; further live requests require a new authorized cap. These checks do not establish benchmark accuracy or final-model course eligibility.

Private records, exact source snapshots and checksums are in `runs/lihao-components-20260929-01/`. The small [development settings record](configs/development/lihao-component-check.json) contains no credentials. [Li Hao's method draft](report/lihao-method-notes.md) records implementation boundaries, related-work starting notes and AI assistance. Gates A–D and the evaluation freeze remain open.

Yao Xiang separately authorized two B development calls with `qwen3.6:35b`, at most 2,048 output tokens each, no retries, and a 5-second solver budget per case. Both extracted valid JSON but reversed A-before-B, returning A1/B0 (generation) and A3/B2 (repair). Both violate the stated precedence despite solver OPTIMAL results. Usage was 1,864 input + 618 output = 2,482 tokens. Raw records and the original source snapshot remain in `runs/yaoxiang-components-20260929-01/`; the cap is consumed. A later prompt clarification is **not live-retested**. The [formal-core notes](report/yaoxiang-method-notes.md) preserve the failure analysis and distinguish structural differences from semantic errors.

## Team and branches

| Member | Primary responsibility | Branch |
| --- | --- | --- |
| Tea Li Hao | Direct LLM baseline, SoCLaaS adapter, setup/integration tooling, demo | `lihao-llm-baseline` |
| Tham Yao Xiang · team leader | Formal model, CP-SAT and repair, LLM-to-solver pipeline, coordination | `yaoxiang-formal-core` |
| Woo Yong Qing | Benchmark, independent validator, experiment runner, metrics | `yongqing-evaluation` |

All three members share experiment analysis, report writing, presentation, and cross-review. Detailed effort allocation and review rotation are in [planning.md](planning.md).

## Evaluation and responsible AI

We will report schedule validity, SAT/UNSAT claims, invalid outputs, formalization errors, objective quality, repair distance, language robustness, latency, and cost/accounting coverage. Feasible, optimal, infeasible, invalid, and unknown outcomes remain distinct.

Development begins with synthetic scenarios. We will examine privacy of routines, unequal inconvenience across participants, faithful explanations, and the consequences of objective choices. Hard requirements cannot be silently relaxed. Individual contributions and AI assistance will be recorded honestly.

## Repository contents

- `README.md` — project overview and entry points.
- `planning.md` — working plan, interface contract, experiment matrix, rubric evidence checklist, portability requirements, and submission schedule.
- `AGENTS.md` — contributor and coding-agent instructions.
- `.env.example` — configuration names without credentials.
- `.gitignore` — local secrets, environments, generated artifacts, and caches.

The repository layout and component ownership are:

```text
.github/workflows/        # offline macOS/Linux CI definition
src/scheduling/
  providers/              # model access and response accounting
  pipelines/              # direct and solver-augmented paths
prompts/
  direct/
  extraction/
configs/
  development/            # SoCLaaS development settings
  experiments/            # frozen evaluation settings
benchmarks/
  fixtures/               # small reviewed synthetic cases
  manifests/              # split, seed, and provenance records
evaluation/               # experiment orchestration and analysis
tests/
  unit/
  integration/
results/summary/          # reviewed aggregate tables
report/figures/           # report sources and selected figures
presentation/             # slides and demo materials
```

On this member branch, the provider/direct components, CLI, packaging/lock, tests, CI definition, direct prompts and tiny demonstration files now contain substantive implementation. The canonical schema draft, solver, repair objectives and extraction pipeline are also implemented. Independent validation, development fixtures/generation/rendering, evaluation bookkeeping, metrics/replay and diagnostic figure export are implemented on this branch. Held-out data, human-written scenarios and frozen research results remain pending review and authorization. Planned module paths and ownership are in [planning.md](planning.md#4-team-responsibilities-and-workload). Ignored runtime folders such as `runs/`, `artifacts/`, and `data/private/` are created locally when needed; they are not part of the tracked scaffold.

## References

- [SCHEDBench](https://arxiv.org/abs/2608.00991), Sharma and Sharma, 2026.
- [NATURAL PLAN](https://arxiv.org/abs/2406.04520), Zheng et al., 2024.
- [Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools](https://aclanthology.org/2025.naacl-long.176/), Hao et al., NAACL 2025.
- [OR-Tools CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver).
- [NUS SoCLaaS documentation](https://dochub.comp.nus.edu.sg/cf/guides/soclaas/start) — institutional access may be required.

Additional research on formalization failures, constrained planning, verification, minimal-perturbation repair, and statistical evaluation is mapped to concrete design decisions in [planning.md, Section 16](planning.md#16-source-grounding). These references guide implementation and analysis; they do not add course requirements.

Project scope follows the Group 23 proposal and CS3263 project guidelines. A distribution license has not yet been selected.
