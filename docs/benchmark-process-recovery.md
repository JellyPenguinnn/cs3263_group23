# Benchmark process recovery

The second full Qwen3.8 development campaign recorded 40 completed scheduling
attempts (39 accepted, one timeout) and one pending request before its process
disappeared. The timeout was retained and later tasks ran. No normal campaign
summary or worker exception receipt was produced.

## Diagnosis

The host log records both local and durable app-server connections stopping at
**21:02:19 SGT on 1 October 2026**, followed by a new app-server process and app
launch at **21:02:28–29**. The pending request began at **21:01:30**. Earlier process
inspection placed the benchmark under the app's process tree. The dashboard
process disappeared as well. These observations identify the deployment defect:
the long-running experiment depended on the coding application's terminal
lifecycle. The available evidence does not identify whether the app restart was
manual, an update or another cause; it does not show a Python exception or a
SoCLaaS response terminating the campaign.

A separate earlier pause came from lid-close sleep between approximately 18:36
and 20:08. Preventing idle sleep did not prevent that event. An independent local
service survives the coding application's restart but still depends on the
computer remaining awake, logged in and connected.

## Changes

- `evaluation/launch_macos_campaign.py` registers a one-shot service in the
  current macOS GUI login domain. Its plist stays beside the experiment output;
  it is not installed as a login item. `KeepAlive` is false, so neither a failure
  nor successful completion dispatches another campaign automatically.
- `evaluation/supervise_development_campaign.py` uses the existing packet loader,
  provider, shared budget, runner and analyzer. A child performs exactly one
  authorized campaign and offline reporting export. Preflight validates a private
  credential file; only the worker installs its values in the process environment.
  No key is embedded in a plist or command.
- `supervisor/status.json` supplies the supervisor/worker PIDs, heartbeat,
  actual wall-clock elapsed time and state. `supervisor/exit.json` records the
  child's exit code or signal; `worker-exit.json` records the phase and sanitized
  failure category. A supervisor stop is forwarded to its child. No automatic
  provider retry or pending-request reconciliation is introduced.
- The runner holds an OS advisory lock throughout execution. The dashboard
  checks lock ownership, not just file existence, and invalidates its cache when
  ownership disappears. A legacy empty lock shows **activity unknown**. An
  abandoned new lock shows **incomplete** and remains a guard against accidental
  reissue. Saved model/evaluation records are never edited by the liveness probe.

## Evidence and rerun contract

The interrupted run and its source/runtime are preserved, including the unknown
outcome and usage of request 41. A newly authorized full rerun uses a new packet,
source snapshot and output root. The user subsequently selected `qwen3.6:35b`
for this rerun to seek faster end-to-end validation; actual speed remains to be
measured. It retains the same case bundles, revision-3 prompts, 32,768 output
tokens, 30/1,800-second connect/read limits,
30/60-second B/reference solve limits and `continue_transient_v1`. Its cap remains
600 scheduling completions plus two capability completions and one metadata
request. Earlier responses are not spliced into the new comparison.

Regression coverage includes child success/failure, signal termination, heartbeat
updates, stop forwarding, exclusive output creation, sanitized failures and a
real runner subprocess killed during a pending mock request. The latter verifies
that dashboard liveness changes without modifying any attempt record or lock
timestamp. Offline service qualification and the new run's actual launch/exit
receipts are distinct from live model quality evidence.

The final noneditable macOS package passed 785 Python tests and nine dashboard
frontend tests; dependency and installed-source/asset checks passed. Historical
replay matched all 332 observations and left 508 JSON files unchanged. A separate
hash check preserved all 530 files in the interrupted campaign directory.

The first zero-inference service test reached launchd ownership (parent PID 1),
but macOS denied the Python executable Documents-folder access before Python
initialization. No model calls were made. The user enabled the specific
`python3.12` Documents Folder switch; the separate `Python` entry had not applied
to this executable. A fresh one-shot test then ran independently for 20 seconds
and produced a completed supervisor receipt with exit code 0; launchd recorded
exactly one run. Service registration alone is not a launch-success receipt.

## Shared-service development policy

The first fresh `qwen3.6:35b` campaign reached the provider successfully. Its
metadata request confirmed availability, and two HTTP 200 capability completions
returned the requested model and valid JSON. They reported
`vllm-0.28.0-f8aad13e` and `vllm-0.23.0-7cd694fa`, so the existing strict policy
stopped before scheduling. The preserved summary records three HTTP requests,
84 reported tokens and zero scheduling attempts. The independent supervisor
captured the nonzero exit and exact protocol stop reason; this was not a lost
process or timeout.

The user subsequently authorized a fresh full run with an explicit development
observation policy, `strict_model_observe_backend_v1`. It retains exact model
checks and all existing nonrecoverable-error checks, but records changes or
missing values in backend fingerprints rather than stopping for that reason.
Both capability observations are retained; each saved scheduling response keeps
its reported metadata. Analysis must disclose shared-service evidence, backend
coverage, descriptive outcomes and A/B fingerprint combinations. Backend strata
are observational: routing can correlate with tasks or time, so differences do
not establish a causal effect of a backend version. Strict/frozen policies stay
unchanged, and the stopped capability records cannot be pooled into the new run.

## Verified rerun launch

`benchmark-qwen36-20261001-02` uses the new observation policy and a separate
230-file source snapshot, installed runtime, prepared packet and output root.
All three case bundles match the interrupted Qwen3.8 campaign exactly. The full
offline suite passed in 269.71 seconds; source/assets, dependency checks and
historical replay also passed. The explicit-model campaign tests cover both
Qwen3.6 and Qwen3.8 without changing prompts or silently substituting models.

The live service started at 22:45:39 SGT on 1 October 2026. Both capability checks
passed. A subsequent launch check observed 11 completed scheduling attempts and
one pending request, an advancing supervisor heartbeat, supervisor parent PID 1
(`launchd`), and dashboard `active` lock ownership. Successful scheduling
responses included all three reported backends `vllm-0.23.0-7cd694fa`,
`vllm-0.26.0-2ccdf8cb` and `vllm-0.28.0-f8aad13e`; variation did not stop the run.
This is a launch observation, not a completed 600-attempt result. Completion is
established only by the campaign summary, successful offline analysis/archive
and supervisor exit receipts. The dashboard now serves this run on port 8878.
