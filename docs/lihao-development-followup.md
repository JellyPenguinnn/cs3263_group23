# Li Hao development follow-up — 29 September 2026

Implementation on `lihao-llm-baseline`, based on integrated `origin/main`
`dce748e`. This supplements the historical component notes; it does not replace
original run records or claim human review, main integration, or a new model run.
The user authorized committing and pushing this checkpoint after the assignment
audit below; the Git handoff records the resulting commit and remote verification.

## Assignment audit against planning.md

**The current development checkpoint is implemented and validated on macOS; not
all of Li Hao's responsibilities through final course delivery are complete.**
The qualified code, tests, prompts, packaging and CI configuration were compared
against the fresh-install receipt before publication: all 68 relevant files match.
No unperformed review, model qualification or experiment is marked complete.

| Assigned responsibility | Implemented/verified evidence | Remaining acceptance or prerequisite |
| --- | --- | --- |
| Section 4: direct generation/repair, prompts/parser and provider | Canonical `run_direct`, strict parser, shared bounded SoCLaaS adapter; existing 30 direct live attempts and offline component tests | Human review of scientific assumptions; model answers can still be wrong |
| Sections 5/10, work package 3: direct/provider failure analysis | All saved A failures classified; representative counterexamples and three new semantic regressions; original scores preserved | A prompt revision is not required merely to change scores. Any future revision needs a separate configuration and authorized pilot |
| Sections 5/7 R4: shared explanations and CLI | Deterministic formatter over existing records; 24 targeted explanation checks; all 60 saved outputs render; no extra inference/solving | Yao Xiang reviews proof semantics; Yong Qing reviews gold labels. Consume supported R3 reasons once available |
| Sections 4/5/14: setup, packaging, CLI/CI and runtime qualification | Locked package, fresh noneditable macOS wheel: 311 tests, dependency checks, three frontend tests; 30-reference preflight. Both-platform CI includes frontend checks | Changed version's Linux and hosted-CI result remain unverified; final integrated version requires requalification |
| Section 5 work package 5: reproducibility package | Local archive and per-file/external checksums; extraction and installed-wheel replay match the tracked summary; original bytes unchanged | Review/share archive through an agreed team location; independent teammate replay is still required |
| Sections 4/10/14: demo integration | Read-only dashboard plus documented live-record replay/explanation commands; 180-attempt canned fallback verified with six deliberate failures | Team rehearsal, final-result selection and presentation timing |
| Sections 4/5: benchmark wording, provider/runner and diagnostic review | Existing integration/diagnostics tested; technical review is not recorded as human sign-off | Review Yong Qing's revised cases/variants and frozen runner when available; Yao Xiang owns R1–R3 |
| Sections 9/10 Week 2: final provider/model qualification | Development backend `qwen3.6:35b` and supported used options recorded in original receipt | Final eligibility/model choice, access, verified limits/settings, qualification configuration and fresh live cap; advanced options/quota are not assumed verified |
| Section 10 Week 3: assigned study runs, direct failures and provider drift | Initial development run preserved and analyzed | Frozen benchmark/protocol, runner, model and cap precede new study runs; development scores do not substitute for them |
| Sections 4/10/12/17: motivation, related work, direct methods, responsible AI and disclosure | Method/related-work drafts, current follow-up, four concrete responsible-AI cases and AI-assistance disclosure | Full-paper/citation checks, final findings/discussion, report assembly/format audit, actual contributions, human understanding, rehearsal and course submissions |

Optional work is not a missing required deliverable: extra UI integration of the
formatter, search tuning, feedback loops, fairness objectives and external-data
adaptation require their stated justification/coordination and, where applicable,
separate budgets. The existing dashboard remains read-only. Gates A–D and the
evaluation freeze retain their outstanding human, dependency and platform checks.

## Work package 3: direct/provider failures

Source evidence: `main-baseline-20260929-01`, 30 development cases, canonical
rendering, repeat 0, `qwen3.6:35b`, one call per approach, 8,192 maximum output
tokens, no retries. See [the original validation report](main-baseline-validation.md)
for the exact original run configuration and source provenance. Current replay
recomputes the same 60 results. Counts below are affected **cases**, not numbers
of violated constraints; failures remain in the denominator.

| Direct A outcome | Generation | Repair | Total |
| --- | ---: | ---: | ---: |
| Accepted | 12 | 6 | 18 |
| Activity availability violated | 5 | 3 | 8 |
| Updated deadline violated | 0 | 2 | 2 |
| False UNSAT on gold SAT | 0 | 2 | 2 |
| Malformed/schema-invalid output or provider failure | 0 | 0 | 0 |
| All attempted | 17 | 13 | 30 |

A returned 26 structurally valid SAT answers and four UNSAT predictions; only two
UNSAT predictions were correct. B retained 25 accepted answers and five rejected
extra-field extractions. Its `capacity` field failures belong to Yao Xiang's R2;
no field is discarded to retrospectively accept those answers.

Representative cases:

- `dev-3263-slack-0-generation`: A scheduled A1 at slot 1, but its allowed window
  is [2,3) with duration one. A1 through A7 violate their windows. The original
  witness uses starts 0,2,4,6,8,10,12,14. Compactness is not a hard-validity check.
- `dev-3263-interaction_density-1-repair`: A kept A7 at 14, ending at 15, after
  the deadline was tightened to 14. The saved valid B/reference repair moves A7
  to 13. An unchanged old schedule must still satisfy the updated requirements.
- `dev-3263-resource_contention-0-repair`: A predicted UNSAT after P0 was blocked
  in [0,1). The saved, independently valid repair moves A0 from 0 to 1 and keeps
  A1…A7 at 2,4,…14. A feasible witness refutes the prediction.

These outputs suggest missed explicit requirements; they do not reveal the
model's internal reasoning or establish why it failed. Current prompts already
state availability and repair semantics. No prompt/parser policy change is made
without a testable hypothesis and a separately configured, authorized pilot.
The new tiny offline regressions reproduce each category through `run_direct`
and independent evaluation: one canned call, exact raw answer retained, no solver
assistance or correction in A, and rejection of the invalid answer. They are
engineering regressions, not additional empirical observations.

## R4: deterministic explanations

`explanations.py` and `scheduling explain` consume existing saved records. Run
explanations reuse the dashboard's checksum-checked replay view, including
recomputed gold evaluation. Standalone solver explanations accept the actual
supplied specification, saved result, and original repair schedule. They do not
solve, make model calls, load a credential, mutate records or guess a conflict.

Output shows before/after offset-aware clock times, moved IDs, (M,T,P), actual
preference windows and weights, and each attempted stage's status/value/bound.
Exact claims require a feasible candidate and a contiguous ordered proof prefix
whose objective values match independent recomputation. A movement proof followed
by UNKNOWN establishes movement only. Gold acceptance and extracted-specification
proofs are separate sections; parsing failures, false UNSAT and execution errors
remain distinct. Existing coarse diagnostics are retained until R3 supplies
supported reasons; no new domain-reason schema is invented here.

The JSON formatter output is version 1.0 and does not alter run or solver wire
formats. Adding code changes the source contract for future runs: replay old
records freely, but use a new run ID rather than resuming old inference under
changed source. Optional case-view integration can reuse this formatter later;
the existing read-only dashboard is unchanged.

## Four responsible-AI cases for team discussion

1. **Privacy and retention.** The reviewed development inputs are synthetic labels
   such as P0/A0, not personal calendars. Replay needs no key. A future real routine
   could identify someone through timing even after names are removed; consent,
   retention and sharing would need separate decisions. Synthetic tests do not
   establish privacy for real data.
2. **Unequal inconvenience.** In saved B case
   `dev-3263-interaction_density-1-repair`, the accepted optimum is (1,1,3): P7
   bears one moved event and 30 minutes of absolute shift; P0–P6 bear zero. This
   demonstrates concentrated inconvenience, not unfairness relative to a feasible
   fairer alternative. Fixed assignments and the deadline restrict alternatives.
   Shared events count for each participant. Minimax/participant weights would
   change the agreed objective and require a separate experiment.
3. **Transparency.** The false-UNSAT case above has a concrete valid counterexample.
   The explanation labels the direct answer a prediction, and labels B's proof as
   concerning its extracted specification. A gold-invalid answer never becomes
   accepted merely because a solver finished. No detailed conflict is claimed when
   none was derived.
4. **Human control and missing requirements.** The deadline repair moves A7 earlier
   by 30 minutes. Even a mathematically optimal change could conflict with an
   unrepresented commitment; the output presents the change for review. The CLI
   and read-only dashboard do not send invitations or change calendars. Resistance
   to adversarial descriptions and consent to real schedule edits are not inferred
   from the current synthetic results.

These are concrete development discussion drafts, not completed human review or
final responsible-AI findings from a frozen study.

## Verification and handoff

Current-source macOS verification: 311 Python tests, three frontend regression
checks, JavaScript syntax and dependency consistency pass. Targeted tests cover
partial proof, malformed evidence, gold-invalid/extracted-valid separation,
no-op and shared-event repair, clock boundary, saved-run integrity, and all three
A failure patterns. Tests prevent explanation-time solver/provider calls and
check record bytes remain unchanged. The fresh noneditable macOS wheel also passed all 311 Python tests and the
frontend/dependency checks; its import path was confirmed inside site-packages.
All 30 reference cases passed (28 SAT, two UNSAT). The documented 180-attempt
canned demo completed with 174 accepted and six deliberately injected failures,
zero live requests, and successful explanation output. All three live-record demo
commands ran against preserved evidence.

Local receipts and tested-file hashes: `runs/lihao-followup-20260929-01/`. The
sanitized replay handoff is `artifacts/lihao-replay-20260929-01.tar.gz` with its
separate SHA-256 file. It includes synthetic raw records, original inference
source, current source/wheel and replay instructions. Teammate sharing/replay and
hosted CI remain pending; producing a local archive is not independent review.

CI now runs the existing frontend checks with Node 20 on both macOS and Ubuntu,
in addition to the installed Python suite and 30-case reference preflight.
The local Linux runtime is stopped/unavailable; no new Linux or hosted-CI success
is claimed. Historical cross-platform receipts concern their recorded versions.

No model calls, prompt changes or schema/solver changes were made.
Commit/push of this checkpoint is now explicitly authorized; main integration
and teammate review remain separate.
Codex implemented these edits, tests and drafts at Li Hao's request. Human
contribution hours, understanding, semantic review and approval remain unclaimed.

Remaining dependencies: Yao Xiang reviews proof semantics and delivers R1–R3;
Yong Qing reviews evaluator labels and owns benchmark redesign/frozen-run mode;
Li Hao reviews resulting public wording and qualifies the selected provider/model
once eligibility/configuration and a fresh call cap are available. A teammate
must independently replay the sanitized package. Gates B–D remain open; this
work does not certify scientific readiness or model eligibility.
