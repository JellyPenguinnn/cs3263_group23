# Usage and experiment operations

Run commands from the repository root after the [locked installation](../README.md#quick-start). The latest completed study is **diverse generation: 2,000 scheduling attempts per model, 4,000 total**, using Qwen3.6 and GLM. Start with [the evidence guide](evidence.md) to verify or replay its saved results without inference. Earlier studies remain separate.

| Design selector | Scheduling attempts per model | Protocol |
| --- | ---: | --- |
| `diverse-generation-2000` | 2,000 | [Current diverse generation](studies/diverse-generation.md) |
| `balanced-generation-96` | 96 | [Earlier balanced confirmation](studies/balanced-generation.md) |
| `difficulty-200` | 200 | [Earlier difficulty and wording study](studies/difficulty-study.md) |
| `legacy-600` | 600 | [Historical Qwen comparison](studies/two-model-development-audit.md) |

The preparation CLI defaults to `legacy-600`; specify `--design` explicitly for another protocol. Prepared packets bind the exact dataset, source and settings. These examples describe supported workflows, not new live authorization. All completed campaign allowances are consumed; a new live run needs its own agreed model, protocol and budget.

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

Open [the local dashboard](http://127.0.0.1:8876). Select a saved run to inspect progress, results and before/after schedules. The dashboard is read-only and binds to localhost; live runs start through the CLI. For a nested qualification run, add `--run-dir runs/quickstart-authored/run`. Historical campaigns have separate `controlled`, `realistic` and `language` runs with 480/24/96 counters; the difficulty design uses 120/40/40. Balanced and diverse campaigns have only `controlled`, with 96 and 2,000 attempts per model respectively. Select the intended study and block; a completed attempt can be a preserved failure.

```sh
.venv/bin/scheduling explain --run-dir runs/quickstart-authored/run \
  --case-id realistic-draft-07 --approach solver_augmented --format json
```

Explanations distinguish the extracted problem's proof from gold acceptance and report participant inconvenience without claiming fair allocation. For a standalone saved solve, use `--spec problem.json --result result.json` and, for repair, `--original-schedule original.json`. Newly saved results bind proof claims to their exact specification and repair context; mismatches are rejected. Legacy unbound standalone results retain candidate validation but cannot establish proof correspondence to a supplied problem. Historical checked-run replay remains supported.

## SoCLaaS and bounded live runs

SoCLaaS is the implemented provider for all completed comparisons. Confirm the
selected model's course eligibility and the team's final-study decision before any
additional experiment. A different provider needs explicit authorization and a
qualified adapter; neither a commercial API nor a third model is an automatic
course requirement. No additional-provider adapter is currently implemented.

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

### Model identity and campaign history

For a GLM run through SoCLaaS route `x-test-1`, the required returned model ID is `glm-5.3-flash`. This is an explicit identity requirement, not a guarantee that the service always routes correctly. A difficulty campaign retained a response reporting `qwen3.8:27b` and stopped; allowing backend fingerprint variation must not allow a different model. The [routing investigation](history/development-notes/glm-routing-investigation.md) records the evidence and rerun conditions. Preserve the requested alias and actual response ID separately; never rewrite a returned ID, accept any model under a testing alias, or discard and silently retry a mismatch. This mapping does not establish a fixed weight revision or improved benchmark performance.

### Historical 600-attempt workflow

This section preserves the original three-block workflow and its engineering checkpoints. Its budgets and test counts are historical, not the latest study or verification totals. Use the [current diverse protocol](studies/diverse-generation.md) for the 2,000-attempt design and the [repository audit](repository-audit.md) for current implementation checks.

The historical 600-attempt campaigns selected **`qwen3.6:35b`** and **`qwen3.8:27b`** explicitly through `--model`, with unchanged revision-3 prompts, **32,768 requested output tokens per completion**, **30/1,800-second connect/read timeouts** and no retries. This timeout is configured by our client, not a documented SoCLaaS service limit. Both arms receive the same limits. B uses a 30-second solve; references use 60 seconds, one worker and seed 0. Sampling/reasoning options remain server defaults. The earlier published checkpoint passed **684 tests on both macOS and network-disabled Linux ARM64** and an exact-input **600-attempt mocked rehearsal**, as recorded in the [integration audit](history/development-notes/main-integration-audit-20261001.md).

The preserved run `campaign-600-live-qwen38-20261001-01` used 900 seconds and the old stop-on-error policy. It stopped after **56 scheduling attempts: 55 returned responses and one timeout**, before the realistic and language blocks. It reserved 59 HTTP requests including metadata/capabilities, took 3,542 seconds, and reported 283,850 tokens with usage available for 57 of 58 completion attempts. Missing timeout usage is unknown, not zero. These partial records are not a completed comparison; their configuration and evidence remain unchanged.

The timeout-continuation checkpoint verified all **726 Python test cases**: 725 passed in the sandbox, and the remaining native macOS certificate check passed outside it (all eight TLS tests passed on that rerun). A mocked 600-attempt campaign retained five timeouts and one HTTP 503 as failures and completed all blocks with exactly 603 HTTP requests. Historical replay matched all 332 previous observations without changing 508 saved JSON files. These are offline regression checks, not a new live benchmark result.

The subsequent live run completed **40 attempts (39 accepted, one timeout)** before a host-app restart interrupted request 41. Its terminal-owned process had no independent supervisor. The [process-recovery note](history/development-notes/benchmark-process-recovery.md) records the evidence and fix. Long local runs now use an OS-owned one-shot service, durable heartbeat/exit records, and dashboard activity verified through an OS-held lock. Keep the Mac awake with its lid open; a service does not keep inference progressing through sleep, logout or reboot.

The recovery and backend-observation implementation previously passed **785 Python tests** on a fresh noneditable macOS installation and **9 dashboard frontend tests**, with installed-source/assets and dependency checks. The completed two-model audit reverified the unchanged implementation, every planned attempt, both analysis exports and archive replay. Qwen3.6 completed across three observed backend fingerprints; Qwen3.8 reported one. The [audit](studies/two-model-development-audit.md) separates this execution evidence from course submission readiness.

| Block | Development inputs | Scheduling completions |
| --- | --- | ---: |
| Controlled | 240 cases / 120 source families from the target-size pilot, seed `32661001`; canonical wording | 480 |
| Realistic | The 12 AI-assisted fictional cases in [`realistic-drafts-v1.json`](../benchmarks/fixtures/realistic-drafts-v1.json); canonical wording | 24 |
| Language | 24 selected controlled bases, six per task/label and from distinct families; paraphrase and reordered wording | 96 |

Selection precedes model outcomes and balances sweep/event counts within each language stratum. Family normalization and exact source hashes are recorded; language cases retain their controlled partners. The [target-pilot receipt](../benchmarks/manifests/f3-target-development-readiness-20261001.json) identifies the actual controlled bundle and its local archive. Import that preserved bundle before running the preparation example; it is not shipped as raw data in a clone. Human gold/text review remains pending, and the authored drafts retain their AI-assisted provenance. These inspected cases cannot become fresh final evaluation data.

The following sequence documents preparation, authorized execution and completed-run analysis. `runs/IMPORTED-target-pilot/cases.json` denotes the imported receipt-matched input; `NEW-*` paths must be unused. It does not grant another campaign allowance.

```sh
.venv/bin/python evaluation/prepare_development_campaign.py \
  runs/IMPORTED-target-pilot/cases.json runs/NEW-campaign-input \
  --design legacy-600 --model qwen3.6:35b \
  --qualification-policy strict_model_observe_backend_v1

# macOS: launch once, independently of the coding app. Output root must be new.
# Only for an authorized run; credentials remain in the private local file.
.venv/bin/python evaluation/launch_macos_campaign.py \
  runs/NEW-campaign-input runs/NEW-campaign-live \
  --env-file .env \
  --allow-live --authorization-reference 'ACTUAL_AUTHORIZATION_REFERENCE'

# The supervisor automatically exports analysis, figures and the archive into
# runs/NEW-campaign-live/analysis after the three blocks finish.
# Optional separate offline re-export, after completion; no model calls.
.venv/bin/python evaluation/analyze_study.py \
  runs/NEW-campaign-live/run/blocks.json artifacts/NEW-campaign-analysis \
  --development --figures
```

The launcher prints its `gui/<uid>/<label>` service identifier. Inspect it with `launchctl print SERVICE_IDENTIFIER`; `launchctl bootout SERVICE_IDENTIFIER` intentionally stops/removes it. Lifecycle evidence is under `supervisor/status.json` and `supervisor/exit.json`; `worker-exit.json` records campaign/export completion or interruption. The service has no automatic restart and is not installed for future logins. `evaluation/supervise_development_campaign.py` is the portable entry point for an equivalent one-shot Linux service. `evaluation/run_development_campaign.py` remains a foreground entry point for an intentionally attended terminal.

For projects under Documents, macOS may require **Documents Folder access for the Python executable itself** in Privacy & Security → Files & Folders. The independent service does not inherit the coding app's permission. A successful `launchctl bootstrap` only confirms registration: verify a fresh supervisor heartbeat and worker PID before declaring the run started. If Python is denied access before startup, inspect the adjacent `*-service.stderr.log`, grant the required folder permission and confirm that no provider request was reserved before launching again.

For this `legacy-600` design, the helper shares a cap of **603 HTTP requests**: one model-list request, two tiny JSON capability completions at the configured ceiling, then 600 scheduling completions. The **19,726,336-token output reservation** covers all 602 completions; input tokens are additional, so it is not a total-token or currency cap. Each block has its own 480/24/96 cap under the shared budget.

Campaign policy `development-campaign-2` selects `provider_failure_policy: continue_transient_v1`. A scheduling timeout, transport error or HTTP 408/500/502/503/504 is saved as a failed attempt, followed by a 30-second cooldown before the **next distinct request**. This also applies to consecutive failures and block boundaries. Failed attempts are never retried, removed from denominators or labelled UNSAT; reservations and actual elapsed time remain recorded. New transport records include a sanitized subtype such as `read_timeout`. A completed campaign means every planned attempt has a record, not that every attempt succeeded.

Exact model checks span both capability responses and every block. The explicitly authorized `strict_model_observe_backend_v1` policy records backend variation, including missing metadata, without stopping. Capability hashes and all capability fingerprints are embedded in each runtime configuration; analysis reports backend coverage and descriptive outcome/pair breakdowns. These are shared-service development results, not a pinned-backend or causal comparison across backend versions. Authentication/permission/quota errors, TLS failures, malformed provider envelopes, missing/wrong returned models, capability failures and exhausted budgets still stop dispatch. The default `strict_model_backend_v1` policy and frozen evaluation continue to reject fingerprint changes. Old packets retain their original behavior and cannot run under changed source/settings; prepare a new packet and use a new authorized run ID. Completed timeout records are not reissued on block resume. Pending/interrupted reservations still require reconciliation, and the whole-campaign directory remains write-once.

The summary records actual request/output reservations, elapsed campaign time, provider failure counts and reported token sums with coverage. `--development` is an explicit analysis opt-in; the default analyzer still requires frozen blocks. Analysis retains all failures and reports controlled canonical, realistic and wording results separately. Stopped/incomplete campaigns do not yield a completed study export; inspect their preserved records without dropping failures. A completed campaign remains development evidence. Course eligibility, actual contributions and human interpretation/review remain open. Fresh data or a frozen follow-up are conditional scientific choices, not automatic submission requirements.

See [evidence and replay](evidence.md) for the completed runs, and [the historical guide](history/development-notes/development-guide.md) for prior handoffs and checkpoint-specific measurements.
