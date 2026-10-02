# Yong Qing: benchmark and evaluation handoff

29 September 2026, `yongqing-evaluation`. Development implementation and evidence;
no held-out benchmark, human review, experiment freeze or course approval is claimed.
Yao Xiang's work was committed and pushed to `yaoxiang-formal-core` as `69157d5`;
this checkout was explicitly approved for sequential reuse with that provisional
dependency. Yong Qing confirmed 8–10 hours/week and authorized the existing credential
subject to a new bounded live cap. New Yong Qing work remains local and uncommitted.

## Independent validation and fixtures

`src/scheduling/validation.py` imports canonical schema types only, plus standard
library utilities. It does not import CP-SAT, compiler domains, or objective helpers.
It checks raw malformed/missing/duplicate/extra activities, horizon, whole-window
containment for every entity, participant/resource overlap, release/deadline/fixed
starts, precedence, blocked intervals and preferred-start penalties. It independently
recomputes moved count and absolute shift and reports constraint IDs where explicit
rules have them. Implicit capacity/window violations have category/activity IDs and
null constraint IDs. Invalid schedules never contribute to feasible objective scores.
Per-participant repair burden counts shared activities for each affected participant.

The six agent-authored fixtures in `benchmarks/fixtures/development-v1.json` cover
simple SAT, an overlap mutation, shared-resource contention, precedence/deadline
interaction, an interacting UNSAT capacity contradiction, and repair. Each carries a
mathematical justification plus witness/expected objective where feasible. They are
pending human/teammate review; agent-authored justifications are not a human approval.
The repair witness A1/B2 attains (one move, one shifted slot, zero preference penalty).
The original A0/B2 is separately validated against its original problem.

The development generator adds 24 cases (12 generation and 12 repair) for activity
count, unary slack, interaction density and resource contention. It uses seed 3263,
explicit 30-minute slots, and a fixed-offset single-day horizon. Generation starts
with a constructed SAT witness; original repair schedules are saved pinned CP-SAT
outputs and independently checked. Disruptions cover new blocked intervals, tightened
deadlines and changed fixed appointments. No output is selected using model success.
This 30-case development bundle is **not** the proposed balanced held-out matrix.

Realized difficulty measures and exact definitions are in the development manifest:
mean unary legal-start count before interactions, distinct coupled-pair fraction,
and resource-sharing pair fraction. Coupled factors and small cells prevent causal
interpretation. `allocate_fresh_groups` supplies a deterministic split registry for
future unseen source groups and rejects reuse of supplied tuning groups. All current
cases are development; generation/repair relatives share group IDs, and case-set
validation rejects cross-split groups. No test cases were generated or inspected.

## Public rendering and gold boundary

`render` supplies all activity/entity availability, durations, assignments, hard
rules, preference weights, time context, and objective priorities to both approaches.
Only public labels are included; gold constraint IDs, reference schedules/objectives,
expected labels and justifications stay in evaluator records. Repair additionally
receives its common original schedule. Canonical, template paraphrase and seeded
constraint-reordering variants are implemented; these are not human-written prose.
Additional wording still needs teammate semantic review before an experimental freeze.

With explicit coordination approval, the missing `run_direct` adapter now wraps
Li Hao's existing `request_direct` into canonical `PipelineResult`. It adds no tools,
solver correction, prompt changes, provider changes, or gold input. Shared CLI wiring
was authorized. Evaluation modules install under `scheduling.evaluation`; the scripts
under `evaluation/` provide reproducible project workflows.

## References, scoring and uncertainty

References retain the canonical problem/context hashes, solver limits, native statuses,
objective values/bounds and completed stages. Reference SAT witnesses and objective
arithmetic must pass independent validation. UNKNOWN stays unresolved. A valid output
against an UNSAT label, or an output beating a proven optimum, stops scoring for
investigation. A model's declared status, parser/pipeline status, native B solver status,
extraction comparison and independent validity are separate fields.

Accepted-answer, SAT-validity and UNSAT-accuracy rates retain failure denominators.
Malformed direct outputs are also inspected safely for structural violation counts,
without repairing their answers. Uncertain interrupted reservations remain failed
attempts in replay; never-started work is separately counted. Missing usage/prices are
null, not zero. Provider failures with missing returned-model metadata stay in their
requested configuration's denominator. Changed backend/configuration groups are not
silently pooled in paired summaries.

Objective gaps require validated schedules and exact proven reference stages. Shift
excess is interpreted only when moved count matches its proven optimum; preference
excess requires both preceding components to match. Raw component values remain visible.
Canonical controlled cases, realistic cases, variants and repeats are separate subsets.
A/B pairs use both/only A/only B/neither counts and B-minus-A percentage points.
The development estimator is a paired source-group bootstrap with 10,000 resamples,
seed 3263 and a 95% interval. Fewer than ten groups get descriptive counts without
that interval. Wilson intervals are restricted to at least ten independent canonical
units. These thresholds/settings are provisional choices for team review, not an
experiment freeze or a significance claim. Language analysis reports matched canonical
and variant acceptance/objectives; tied schedules need not have identical starts.

## Durable runs and replay

`run_batch` is serial and development-only. Configuration requires the same explicit
model and per-call token cap for both paths, one provider attempt (no retries), separate
B/reference solver budgets, rendering seed, variants, repeats and run-level caps.
The manifest records code commit when available, source hashes, exact request-prompt
hashes, dependency/runtime versions, cases and settings. Cases and reference records
are written before inference. A private exclusive run lock prevents concurrent owners.
Before each request, an exclusive private pending record reserves its request/output
budget; completion atomically replaces it with raw output, public view and scoring.
Raw pipeline output is saved before scoring, so a scoring failure cannot erase it.

Completed records are reused on matching resume; changed source/configuration/inputs
require a new run ID. An interrupted reservation is never automatically retried, even
when the provider's charging status is unknown. It requires explicit reconciliation.
A stale lock after process termination also requires confirming no active owner before
removal. Authentication/authorization/rate-limit errors stop the batch and future resume.
Caps count reserved requested output tokens, not input tokens, total tokens or currency.
Offline canned reservations are logical attempts and make zero network requests.

Replay recomputes validation and metrics from saved case/reference/raw result records,
checks their hashes, and does not call the model or solver. Stored scores are not trusted
as inputs. A corrected checker or renderer uses new output/run identities and preserves
prior artifacts. Checksums detect accidental changes; they are not cryptographic signatures
against an attacker who can rewrite both a record and its checksum.

Matplotlib 3.10.8 is an optional `plots` dependency for PNG/PDF diagnostics and separate
sweep panels. Its seven additional locked packages were inspected; pre-existing pins
were preserved. CSV/JSON export remains available without plotting. Figures show evidence
class, denominators and small-cell limitations; canned charts are never scientific results.

## Observed evidence and commands

Final verification passed **251 tests** both in this checkout and in a fresh credential-free macOS ARM64 environment with a noneditable wheel install. Hash-checked dependencies, `pip check`, installed benchmark/validation commands, and the complete 180-attempt offline demo/resume/replay/figure exports passed. The exact source/logs are retained in `runs/yongqing-offline-20260929-02/`; a small receipt is in `configs/development/yongqing-verification.json`.
The component checks include full Cartesian tiny assignments, deliberate invalid mutations,
six fixture proofs/witnesses, all generated development references, cap persistence,
interruption/authentication stops, changed-record refusal, public-input boundaries, CLI
execution, conditional repair gaps, paired counts, and denominator regressions.

The offline demo produced 180 completed records: 30 development cases × 3 renderings ×
2 approaches, with zero live requests. Its canned answers intentionally include malformed
A output and reversed-precedence B extraction on selected fixtures. Replay retained all
six injected failures (three variants of each) and 174 accepted canned answers. This tests
bookkeeping and scoring, **not model performance**. Resume did not duplicate work.
Initial and revised figure exports were visually inspected; the revised exporter separates
sweeps and displays denominators. Runtime artifacts remain ignored/private.

Retrospective independent checks of preserved earlier live records found both Li Hao
schedules valid and both Yao Xiang schedules invalid for precedence. The original records
were not modified. Their differing prompts and call caps prohibit treating four examples
as a controlled A/B result. The user subsequently approved a new four-call paired check with `qwen3.6:35b`,
2,048 requested output tokens each (8,192 total), no retries and five solver seconds
per B case. `runs/yongqing-live-20260929-01/` preserves all four transport-error
records with no HTTP status, returned model or reported usage. The cap is consumed;
no successful scheduling response or zero-token usage is inferred. A credential-free
TLS check using the provider's CA bundle failed with verification code 20, “unable
to get local issuer certificate”. Certificate verification was not bypassed. The subsequent native-trust fix is recorded below; a fresh cap is still required before another live run.
The exact pre-run source snapshot is in `runs/yongqing-live-20260929-01-source/`.
Offline replay independently recomputed all four failure denominators.

TLS follow-up (29 September): the server supplied only its YE2-issued leaf certificate. The provider now uses pinned truststore 0.10.4 with native certificate and hostname verification. A credential-free HEAD through the patched client returned HTTP 200 on macOS; no model request or API key was used. Current checkout verification passed 255 tests and `pip check`, including trusted, untrusted and wrong-hostname TLS cases. See `configs/development/tls-verification-20260929.json`. This is a local client fix; service-side chain configuration and Linux verification remain separate. Old attempts/source snapshots remain immutable, and a new live run requires a fresh cap and run ID.

POSIX shell from the repository after the locked installation:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/scheduling benchmark-generate --output runs/NEW-development.json
.venv/bin/python evaluation/offline_demo.py runs/NEW-offline-demo
.venv/bin/scheduling evaluate-replay --run-dir runs/NEW-offline-demo --export-dir artifacts/NEW-export --figures
```

The validator expects a schedule array, not a direct-response envelope. A directly runnable raw schedule validation example is:

```sh
.venv/bin/scheduling validate --spec tests/examples/formal-generation.json --schedule tests/examples/formal-original.json
```

Batch inputs are a `case_bundle`, a `RunConfig` JSON, and (offline only) an attempt-ID-to-
response-text JSON map. The demo script constructs the latter explicitly from gold test
answers and deliberate failures; evaluated live pipelines never receive that map. Live
CLI syntax additionally requires `--allow-live` and an explicit live-development config.
Neither a live config nor credential availability constitutes spending approval.

## Milestones, review and responsible AI

Section 5 fixtures/validator/canned runner, development generation/rendering/split records,
reference auditing, metrics/replay/figure export and benchmark-method writing are implemented.
Gate A still requires both teammates' schema/fixture review and Yao Xiang's mathematical
review of this independent implementation. Gate B still needs successful independently validated new
paired live evidence after resolving the certificate-chain blocker and a fresh Linux run; the local Docker daemon is unavailable.
MacOS tests do not establish Linux portability. Main remains unchanged.

The next owner actions are: Yao Xiang reviews validation/reference rules and fixture
arguments; Li Hao reviews public wording and the narrow canonical adapter/CLI integration;
all review paired protocol, estimator settings and final model eligibility. Before held-out
generation, freeze the balanced matrix, split registry, prompts, bounds, exclusion rules,
model and budget. The 12 realistic scenarios require human-written text and another member's
formalization review. No automated template is labelled as that human-authored deliverable.
Main-run analysis, report claims and independent teammate replay await those inputs/gates.

Four bounded responsible-AI considerations: (1) participant burden reports every affected
participant, including shared activities; it is not fair assignment. (2) zero-movement
repair can preserve a preference penalty because the declared objective prioritizes
stability. (3) ambiguous negotiability must be resolved in the public problem, never guessed
as permission to relax a rule. (4) instruction-like task text stays untrusted prompt data;
the schema boundary does not guarantee faithful extraction. These are implementation
limitations/case-analysis topics, not measured social outcomes.

Yong Qing directed the scope and approved the dependency and integration boundaries.
Codex authored code, tests, fixtures, renderings and this draft, executed checks and analyzed
saved synthetic records. Human comprehension, teammate review and academic ownership remain
required. No claim is made that the member manually wrote every line or reviewed every case.
