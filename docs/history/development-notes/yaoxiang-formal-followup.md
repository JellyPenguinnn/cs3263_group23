# Yao Xiang formal-core follow-up — 29 September 2026

Implemented on `yaoxiang-formal-core`. Qualification initially incorporated main
`dce748e` and Li Hao's published `fa6674f` as a provisional formatter dependency.
The publication audit fetched and fast-forwarded to latest main `61d9fbb`, which
merges Li Hao's PR #4 with identical file contents. Existing work and historical
runs are preserved; the qualified code has not changed.
This is AI-assisted implementation and verification, not independent teammate
review, contract sign-off, main integration or final-study evidence.

## Assignment audit

**The current development deliverables are implemented and validated on macOS;
Yao Xiang's full-course responsibilities are not all complete.** Publication was
authorized after this audit. All 83 qualified code, prompt, test and configuration
files match the installed-build receipt. The pending rows below are real review,
platform, experiment and course-delivery requirements, not completed milestones.

| Responsibility from planning.md §§4–5 | Current evidence | Remaining prerequisite |
| --- | --- | --- |
| Canonical schema, generation/repair formulation and CP-SAT | Existing integrated compiler and exact sequential objectives retained; R1 invariants and richer exhaustive checks added | Yong Qing's independent mathematical/fixture review and team contract sign-off |
| R2 extraction and diagnosis | Parser-tested format example, explicit capacity-one guidance, structured schema failures, typed structural differences; all five archived B errors remain failures | Human semantic review; wider qualification after benchmark redesign and a new cap |
| R3 inspectable constraint reasoning | Bounded per-start unary exclusions, domain wipeout and actual positive-duration precedence-cycle chains | Independent reasoning review; no minimum-conflict or general SAT claim |
| R4 proof-semantics integration/review | Existing Li Hao formatter consumes recorded R3 reasons; old records and UNKNOWN/partial-proof distinctions tested | Li Hao consumer review and Yong Qing gold-label review; technical checks are not human sign-off |
| Reference labels and independent validity review | 30 generated reference checks; independent enumerator/validator/solver agreement on richer tiny cases | Review Yong Qing's redesigned benchmark and equivalent renderings when available |
| Development failure analysis | Five archived capacity failures analyzed; separate four-call pilot and independently replayed results below | Selected-case results do not qualify an unbiased accuracy claim |
| Formulation, solver/repair and extraction writing | Original method draft plus this current implementation/mathematical handoff | Final result discussion, contribution review, report assembly and presentation understanding |
| Coordination and final-model eligibility | Previously confirmed development model remains qwen3.6:35b; availability approximately 8–10 hours/week | Canvas submission receipt, new teaching-team feedback and final-model eligibility remain unconfirmed |
| Final study and reproduction | Installed macOS qualification and unchanged historical replay; fresh pilot records preserved | Yong Qing's frozen runner/protocol and fresh benchmark; model eligibility, team reviews and new run cap; current Linux qualification and independent teammate replay |

Optional optimizations are deliberately deferred: precedence-domain pruning,
first-stage hints, alternate encodings, general conflict minimization and tiny
semantic-equivalence comparison. Existing later-stage hints remain. Historical
solver times do not justify prioritizing search tuning over extraction quality.
No new fairness objective, unsupported disruption or alternate pipeline is added.

## R1: preserve the meaning of repair

`RepairCase` now requires equal origin, timezone, slot size and horizon, plus
unchanged activity IDs, durations and participant/resource assignments by stable
ID. Reordering is harmless. Availability, deadline and fixed-start disruptions
remain supported; additions/cancellations, changed durations or assignments are
rejected. This closes the documented v1 gap; valid archived cases still load.
The evaluator continues to validate the original schedule independently. B does
not receive the private original gold specification to enforce this boundary.

`test_formal_qualification.py` checks every bounded start assignment against an
independent enumerator and validator, then compares CP-SAT's proven objective
with the enumerated optimum. Cases include unequal durations, multiple
participants, asymmetric sharing, gaps, competing preferences, UNSAT and no-op
repair. Exact schedules are compared only when a unique solution is justified.

The coupled three-activity example has the sole repair A1/B2/C0 from A0/B1/C2:
(M,T,P)=(3,4,0). B and C must move despite unchanged unary windows. Another test
shows (1,4,0) beating (2,2,0), as movement count has priority over shift. A third
checks preferences only break a tie after movement and shift. These are finite
mathematical checks, not sampled live-model observations.

The original-schedule policy remains a saved feasible schedule from the pinned
gold-solver setup, shared identically with both approaches. Which feasible old
schedule is selected affects subsequent repair burden; minimum disruption is
conditional on that starting point and does not establish fairness.

## R2: reliable extraction boundaries

Prompt revision 2 explicitly forbids a resource/participant `capacity` field and
includes a complete parser-checked format example with conspicuous example IDs.
All seven tagged constraint forms remain tested. Parsing stays strict: no field
dropping, coercion, retry or gold-assisted correction. The v1 ProblemSpec wire
schema and accepted scientific semantics remain unchanged.

Schema errors retain their existing string message and add `SchemaError.detail`
(code, JSON path, safe message, missing/unsupported field names, format 1.0).
`PipelineResult.schema_diagnostics` is optional and defaults to an empty tuple.
Raw responses remain recorded. Duplicate JSON-key/nonfinite errors have root
paths because the JSON hook cannot recover a nested location. Paths carry no
field values; malformed field names are replaced by a bounded placeholder.

`SpecComparison` retains the meaning of its four legacy fields/counts and adds
format 2.0 typed field and constraint differences. Order and arbitrary constraint
IDs normalize away; multiplicity, durations, assignments, windows and weights do
not. A unique unmatched shape pair may be labelled altered; ambiguous pairs stay
omitted/invented. This does not change legacy omission/invention counts. Adjacent
availability windows are never merged: full-window containment makes that unsafe.
Structural comparison is evaluator-only and is not semantic-equivalence proof.

All five B failures in the original 60-call run contain unsupported
`$.resources[0].capacity`; they remain INVALID_OUTPUT on offline reparse:

- dev-3263-resource_contention-2-generation
- dev-3263-interaction_density-2-generation
- dev-3263-interaction_density-0-repair
- proven-unsat
- shared-resource

The old aggregate remains exactly A 18/30 and B 25/30 accepted. No archived answer
is retrospectively corrected or replaced by the new pilot.

## R3 and the shared explanation consumer

`domain_analysis.py` computes one unary legal-start set per activity, indexing
entities/rules once per solve. Each excluded start cites one sufficient actual
rule ID or specification path. At most H (48) rejected starts are recorded per
activity, grouped by reason. This is a coverage explanation, not a complete list
of every violated rule. The product of domain sizes is an assignment-space upper
bound, not observed search effort.

An empty unary domain cites the reasons covering all starts. Iterative traversal
returns an actual directed precedence cycle; positive durations make its summed
inequalities contradictory. Neither explanation is promised to be smallest.
Nonempty domains do not prove feasibility; shared-resource conflicts may still
require CP-SAT and have no simple analytical explanation.

`SolveResult.domain_analysis` is optional (format 1.0). The compiler uses the same
unary domains, retains global NoOverlap and precedence constraints for ordinary
instances, and sends an explicit false constraint to CP-SAT for supported
contradictions. Native backend status remains authoritative: a zero budget stays
UNKNOWN even if analytical evidence exists. The analysis is within the existing
wall-time budget. The independent validator imports none of this logic.

The shared formatter reads these optional recorded reasons, explicitly limits
them to the supplied/extracted specification and never recomputes them. Old
records without the field retain the existing fallback. Full proof, partial
optimality, UNKNOWN and independent gold acceptance remain distinct. No raw-run
migration or source-request correctness claim follows from a compiler proof.

## Authorized live pilot

Run: `yaoxiang-extraction-v2-20260929-01`; configuration:
[`yaoxiang-extraction-v2-pilot.json`](../configs/development/yaoxiang-extraction-v2-pilot.json).
Two development cases were selected because B previously failed on `capacity`.
Both approaches received the same canonical public cases/original schedule.
Model qwen3.6:35b, four serial calls, no retries, at most 8,192 output tokens each,
10 seconds per B solve, 30 seconds per reference, seed 0, one solver worker.
The new prompt is B-only; A's prompt and parser are unchanged.

| Case | Direct A | Solver-augmented B |
| --- | --- | --- |
| interaction_density-0-repair | Gold-valid; (M,T,P)=(8,8,14), movement gap 7; secondary gaps unavailable because M differs | Gold-valid and structurally matching extraction; proven (1,1,2), all reference gaps zero |
| resource_contention-2-generation | Invalid: A5, A6, A7 violate activity availability | Gold-valid and structurally matching extraction; proven preference penalty 0, reference gap zero |

All four returned the configured model with complete usage: 6,038 input + 4,111
output = **10,149 tokens**. No provider failures or retries. All four authorized
requests and the 32,768 requested-output reservation are consumed. Another live
run requires a fresh cap. B extraction took about 12.75/15.43 seconds and solving
about 8 ms per case; this is not a performance comparison.

Observed: these two new B responses parsed and passed independent checks, unlike
their saved predecessors. This selected, unreplicated pilot cannot isolate the
prompt effect from sampling or establish a general accuracy improvement. A's
failure is retained. No held-out examples were inspected or reclassified.

## Verification and handoff

Fresh Python 3.12 macOS environment, hash-locked dependencies, noneditable wheel,
confirmed site-packages import: **365 Python tests**, **3 frontend tests**, JS
syntax and `pip check` passed. `benchmark-generate` plus `evaluate-plan` checked
30 references. `evaluate-replay` recomputed all 60 historical records and matched
the tracked aggregate exactly. The new four records replayed and all four CLI
explanations rendered. The canned integration demo also passed; it remains
separate from live evidence. Current Linux and hosted CI were not executed.

Qualification commands use the existing CLI: `python -m pytest -q`,
`python -m pip check`, `node --check src/scheduling/dashboard/static/app.js`,
`node --test tests/frontend/dashboard.test.cjs`, `benchmark-generate`,
`evaluate-plan`, `evaluate-replay` and `explain`. The installed-wheel test copied
current tracked/unignored source without .env, built with `pip wheel --no-deps
--no-build-isolation`, and installed locked dependencies with `--require-hashes`.

The [sanitized receipt](../results/summary/yaoxiang-formal-followup-20260929.json)
records tested-file/wheel hashes, platform, actual usage and per-attempt outcomes.
Private raw records are under `runs/yaoxiang-extraction-v2-20260929-01/`;
qualification logs and source hashes are under
`runs/yaoxiang-followup-20260929-01/`. Raw data is ignored and is not supplied by a
fresh clone. No credentials or raw model responses are in the tracked receipt.

Next concrete task: Yong Qing independently reviews the richer enumeration and
R3 reasons; Li Hao reviews compatible consumer wiring. Yao Xiang then reviews
Yong Qing's redesigned benchmark constraints and equivalent renderings, and
records the final-model eligibility decision before the evaluation freeze.
The user authorized committing and pushing this checkpoint to
`yaoxiang-formal-core` after the assignment audit. The Git handoff records the
resulting commit and remote verification; publication does not imply main merge
or teammate approval. Canvas proposal receipt, later presentation/recording
arrangements and final report upload/receipt remain Yao Xiang's coordination
responsibilities, with another member verifying submissions.
