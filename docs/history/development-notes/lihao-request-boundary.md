# Li Hao request-boundary qualification — 30 September 2026

This work continues the integrated baseline on `lihao-llm-baseline`. The clean
checkout was fast-forwarded from `ddc130f` to GitHub main `1de9e7e`, then to Yong
Qing's published v3 checkpoint `b94f707` with explicit user approval. No existing
work was dropped. The user also approved the narrow Yao Xiang-owned request
boundary and canned-consumer changes. During the publication audit, GitHub main
advanced to `be59228` through PR #9, integrating that same v3 checkpoint. Its Git
tree is identical to `b94f707`; the member branch fast-forwarded without changing
the qualified code or local work. The user has now authorized committing and
pushing this checkpoint to `lihao-llm-baseline`. This does not authorize a main
merge, archive sharing, further model calls or human sign-off.

## Required package and implementation

Section 5 WP3's fair-input audit found that B sent evaluator `instance_id` and
`variant_id` values to the model, while A omitted them. Two original baseline
case IDs and all twelve v2 pilot IDs contained SAT/UNSAT labels. Opaque v3 IDs
addressed that dataset only; arbitrary future evaluator IDs could still leak.

The B builder now sends the constant request-local ID `request` and omits the
variant ID. The existing schema stays at 1.0. The model must echo this public ID;
an evaluator ID or any other value is rejected before solving. After parsing
and checking public task/activity coverage, the pipeline maps only the ID back
to its local bookkeeping identity. Raw response bytes remain available and no
constraint, objective, activity or schedule is corrected. Evaluation records
still retain their original case/variant IDs. Prompt templates are unchanged;
actual request hashes and source hashes distinguish the new request contract,
`neutral-request-id-no-variant-v1`. New inference requires a new run directory.

The CLI, dashboard fixtures and v1/v2/v3 canned producers now use this same wire
contract. Archived responses are not rewritten; replay consumes recorded results
and continues to read the old archives. CI now runs v3 qualification in addition
to the existing v2/reference/frontend checks.

A regression audit constructs complete A/B messages for all 282 current
seeded development cases and all three renderings (846 views). Apart from B's
neutral ID and explicit task type (A selects its task-specific system prompt),
the user-message scheduling facts match exactly. Counterfactual SAT/UNSAT case
IDs and variant metadata leave the messages unchanged. This is a technical
information-boundary check, not human review of language fidelity.

## Executed offline evidence

The [receipt](../configs/development/lihao-boundary-verification-20260930.json)
records source hashes and installed environments. The source manifest and full
logs are retained in ignored `runs/lihao-boundary-20260930-01/`.

| Check | Fresh macOS ARM64 wheel | Fresh Linux ARM64 wheel |
| --- | --- | --- |
| Python / OpenSSL | 3.12.2 / 3.6.3 | 3.12.14 / 3.0.22 |
| Full Python suite | 444 passed | 444 passed |
| JavaScript syntax / frontend | Passed / 3 passed, Node 20.15.0 | Passed / 3 passed, Node 18.20.4 |
| Installed prompts/assets / dependency consistency | Passed | Passed |
| Legacy canned demo and matching resume | 180 attempts; 174 accepted, 6 deliberate failures retained | Same |
| V2 canned integration / matching resume / replay | 864 accepted attempts | Same |
| V3 canned integration / matching resume / replay / figures | 648 accepted attempts | Same |
| Historical 60-record and 24-record summary replay | Both exactly unchanged | Both exactly unchanged |

Before broad qualification, 64 targeted pipeline/evaluator/dashboard/extraction
checks and three full-dataset request-boundary checks passed. Both environments
installed the unchanged hash-locked dependencies and a fresh noneditable wheel.
Linux used the pinned Python Bookworm image recorded in the receipt, in local
Colima; it is not an independent teammate or hosted x86 runner. Hosted CI uses
Node 20; this local Linux frontend check used Node 18. No hosted-CI result is
claimed. Canned integration is not model-performance evidence.

## Bounded live pilot and failure handoff

The user explicitly approved the unchanged preselected v3 packet under a new
run identity, `lihao-boundary-pilot-20260930-01`: twelve canonical development
cases from six families, six SAT/six UNSAT, six generation/six repair, covering
all three construction mechanisms and events. Both approaches used
`qwen3.6:35b`, sequential requests, no retries, at most 8,192 output tokens each
(24 calls / 196,608 requested output tokens), and ten seconds per B solve.
Inputs were additional and recorded. The installed preflight proved all twelve
references and checked the cap before inference; all cases were selected before
any outputs. Source hashes link the noneditable build to base `b94f707` plus
these local changes; wheel installation has no Git metadata, so the runner's
`code_commit` is null rather than an invented commit.

All 24 requests completed once with HTTP 200 and returned `qwen3.6:35b`.
Reported usage: 30,376 input + 13,756 output = 44,132 total tokens, coverage
24/24; currency cost unavailable. The cap is consumed. All twelve B responses
echoed `request`; raw content keeps that ID while recorded specifications use
the local case identity. A completed matching resume with a callback that
rejects any new request returned completed with **zero provider calls**.

| Outcome | Direct A | Solver-assisted B |
| --- | ---: | ---: |
| Generation accepted | 3/6 | 6/6 |
| Repair accepted | 2/6 | 4/6 |
| Gold-SAT valid schedules | 3/6 | 6/6 |
| Gold-UNSAT correct predictions | 2/6 | 4/6 |
| All accepted | 5/12 | 10/12 |

A's seven failures comprise two false UNSAT predictions and five gold-invalid
schedules. On `dev-v3-8c76290cef6036f833b5a4ba-{generation,repair}`, A wrongly
predicted UNSAT despite the independently checked resource-chain witness.
For `dev-v3-6fd74cf4780390d3c5cb45d4-repair`, A left the old schedule unchanged
and violated the new deadline. The other four invalid outputs belong to gold-
UNSAT cases and violate activity availability and/or the deadline. Existing
semantic regressions and independent v3 enumeration cover these failure classes;
no parser relaxation, hidden retry or retrospective schedule correction was made.

B had nine structurally equivalent extractions out of twelve. Two altered-
availability repairs yielded gold-invalid schedules: in
`dev-v3-d9a5c7aa60e26500e2852c5f-repair`, A1 availability expanded from
`[39,42), [42,45)` to `[39,48)`; in
`dev-v3-246eabff6bb1ff745a7bfbfc-repair`, A4 gained the unsupported window
`[6,7)` in addition to `[5,6)`. The third structural mismatch still produced a
correct UNSAT answer and remains an extraction diagnostic. These are concrete
Yao Xiang review inputs; accepted status alone is not extraction fidelity.

The [unchanged-denominator aggregate](../results/summary/lihao-boundary-pilot-20260930.json)
comes from independent saved-record replay; local analysis exports include
per-attempt CSV, structured differences and diagnostic PNG/PDF. This is a
six-family selected development pilot, not held-out evidence, a difficulty
trend, or a controlled estimate of improvement over the v1/v2 pilots. No prompt
or selection changes were made after seeing these outputs.

## Scientific consequences

The earlier Li Hao wording audit removed evaluator labels/witnesses/grouping
from case data but did not vary the case ID itself. Its successful 432-view check
therefore did not establish complete metadata isolation. The new complete-message
regression closes that specific gap. Historical reports/receipts and scores are
preserved. Their B-only ID hints limit fair A/B interpretation, and replay cannot
undo that exposure or establish whether it affected model behavior.

## Assignment audit and remaining dependencies

The publication audit rechecked Sections 4–5, the weekly milestones, provider
requirements, R4 and the course-delivery assignments. All 86 qualified source,
test, prompt and build files still match their installed verification hashes.
The pilot summary and local archive hashes also match. Only publication/handoff
metadata changed after qualification. Current unblocked development deliverables
are implemented and validated; the remaining obligations below are not marked
complete. No extra live calls or repeated unchanged qualification runs were made.

| Li Hao responsibility in Sections 4–5 | Current evidence | Remaining acceptance dependency |
| --- | --- | --- |
| Direct generation/repair, prompts/parser and provider | Existing components retained; current installed suites include malformed responses, TLS, accounting and strict parsing | Human assumptions review; final selected-model qualification under its own cap |
| WP3 direct/provider failure analysis and fair inputs | Existing failure tables retained; generic B metadata boundary fixed and regression-tested | Interpret each new pilot separately; no unsupported accuracy-improvement claim |
| R4 explanations and shared consumers | Existing proof-aware formatter, saved-record CLI and current suite pass | Human proof/semantic/gold-label sign-off |
| WP2 wording review rotation | 846 full request views checked across v1/v2/v3; common public facts and metadata independence verified | Twelve independently human-written realistic scenarios and human wording review |
| WP4 provider/frozen-run integration | Existing preflight, reservation, stop/resume and frozen controls pass unchanged | Final model eligibility/access, fresh split allocation, protocol and budget decisions |
| WP5 packaging, CI, demo and reproducibility | Both fresh installed platforms, all three canned datasets and historical replay verified; v3 added to CI | Hosted CI on publication, authorized archive sharing and independent teammate replay |
| Report, related work, responsible AI, contribution disclosure and demo | Existing drafts retained; this handoff adds request-contract and scientific-limit evidence | Human source checking, final study/results, actual contribution records, timed rehearsal and submissions |

Optional external datasets, prompt tuning, solver optimizations, feedback loops
and additional UI are not missing baseline modules and were not added. The
required development implementation is usable; the full frozen study and course
delivery are not complete. All work here is AI-assisted and does not constitute
human review, hours, course approval or submission evidence.

## Reproduction and next concrete task

The local archive is `artifacts/lihao-boundary-replay-20260930-01.tar.gz`
(767,900 bytes; SHA-256
`3e22f05c1ac3641731327b74eb98c6414b5ee01454a98b438c05eee7ece574f9`).
It contains 360 files: current source and wheel, all three saved synthetic live
runs, new pilot inputs/preselection, qualification logs, analysis outputs and
portable replay instructions. All 359 listed content checksums passed after
unpacking; installed assets matched and all three serialized summaries reproduced
exactly. The archive has been scanned locally for the configured credential,
contains no credential file, and has not been shared externally. Its snapshot
predates this archive-receipt paragraph and the final receipt update; the 86
qualified code/test/prompt/build files were rechecked unchanged. No claim of
independent human replay is made.

Next, Yao Xiang should review the two saved availability-expansion failures and
the strict neutral-ID consumer contract. Li Hao's next owned review is the
team's twelve independently authored realistic scenarios and equivalent
renderings, once that packet exists; synthetic prose generated by an agent
cannot fulfil its human-authorship gate. The current direct/provider error
analysis is complete for this pilot. Any further prompt experiment needs a
separate version/run and cap. Final-model qualification depends on the model,
eligibility/access and budget decision. Publish this checkpoint only when the
user authorizes it, then review it through the member-branch workflow. The
subsequent publication request authorizes this member-branch checkpoint; the
Git handoff records its commit and remote verification.
