# Yao Xiang availability review — 30 September 2026

The clean `yaoxiang-formal-core` branch fast-forwarded to GitHub main `ca710cf`,
which includes the v3 benchmark and neutral B request boundary. Previous work
was preserved. This follow-up extends WP3/R2 and the mathematical review of
WP1/WP2/R3; it does not rebuild the delivered schema, compiler or runner.
The user subsequently authorized committing and pushing this checkpoint to
`yaoxiang-formal-core`. Main integration and independent human review remain
separate decisions.

## Implemented change and semantic certificates

Extraction prompt revision 3 explicitly preserves every stated activity/entity
availability window, including adjacent windows, and forbids inventing windows
to make a repair feasible. Schema 1.0, the single-call architecture, solver
semantics, objectives, provider, direct prompts and scoring are unchanged.
Raw replies remain immutable; erroneous extractions are never corrected using gold.

The independent regression tests in
[`test_availability_extraction_review.py`](../tests/unit/test_availability_extraction_review.py)
reconstruct the three observed window mutations. An additional saved-response
audit verifies the original records and enumerates their actual parsed problems;
its [certificate](yaoxiang-availability-review-20260930.json) retains the hashes,
changed endpoints, domains, witnesses and single-field restoration results.
These are AI-assisted technical checks, not a teammate's human sign-off.

| Prior repair case suffix | Observed mutation | Independent consequence |
| --- | --- | --- |
| `d9a5c7aa60e26500e2852c5f` | Merge A0 windows; expand A1 to [39,48) | Gold has no solution; extracted problem has exactly one, objective (2,6,9). A1 expansion alone causes false SAT; A0 merging alone does not |
| `246eabff6bb1ff745a7bfbfc` | Add A4 window [6,7) | Gold has no solution; extracted problem has exactly one, objective (5,5,18) |
| `66dd6c3548fb70d23bad6865` | Merge A1 and A2 windows | Unary start sets expand, but both complete problems remain UNSAT because the blocked A0 still cannot fit |

For activity i with duration d, enumerate every integer start s for which at
least one of its stated windows [a,b) satisfies a <= s and s+d <= b. This is a
necessary condition, so the Cartesian product covers every feasible assignment.
Independent arithmetic then checks all remaining rules and the objective tuple;
it imports schema types but does not reuse CP-SAT compilation or the production
validator. Thus zero accepted assignments is a finite infeasibility certificate,
and the minimum tuple over all accepted assignments establishes exact optimality.

The control's empty feasible sets are equal despite the altered unary domains.
Its correct UNSAT answer does not establish faithful extraction. Keep structural
fidelity, bounded semantic proofs and end-to-end acceptance separately recorded.
Restoring a field to gold is solely an offline diagnostic intervention; no restored
answer replaces a saved model result or enters the primary scores.

The v3 review additionally checks all **108 cases / 432 activity domains** and
every recorded rejected-start explanation against independent unary arithmetic.
The existing exhaustive v3 oracle and preference/repair certificates run in the
full suite. This extends the previous v2 review without another schema or oracle.

## Executed qualification and measured results

Fresh noneditable Python 3.12 wheels on macOS ARM64 and Linux ARM64 each passed
**448 Python tests**, **three frontend tests**, JavaScript syntax, `pip check`
and packaged prompt/certificate/dashboard comparisons. The targeted first pass
passed 59 tests. Each platform completed 180 legacy canned attempts (174 accepted,
six deliberate failures), 864 v2 and 648 v3 canned attempts, figure export and
exact replay of the historical 60-call, v2 24-call and boundary 24-call summaries.
Canned checks establish integration, not model performance. Local Linux used
Python 3.12.14 / Node 18.20.4; macOS used Python 3.12.2 / Node 20.15.0. Hosted CI
uses Node 20 and was not checked here. Full versions and qualified hashes are in
the [verification receipt](../configs/development/yaoxiang-availability-verification-20260930.json).

The separately approved run `yaoxiang-availability-pilot-20260930-01` reused the
same twelve preselected v3 cases (six related source families), canonical wording,
one repeat, qwen3.6:35b, 8,192 output tokens per call, no retries, serial execution
and a ten-second B solve limit. All 24 calls completed with HTTP 200 and the
expected model; 32,200 input + 16,293 output = **48,493 reported tokens**. Usage
coverage is 24/24; currency cost is unavailable. The 24-call / 196,608 requested
output-token allowance is consumed. Completed resume made **zero provider calls**.
All twelve raw B replies retained the neutral `request` identifier.

| Development observation | Prior revision 2 run | Revision 3 qualification |
| --- | --- | --- |
| A accepted | 5/12 | 4/12 (generation 2/6, repair 2/6) |
| B accepted | 10/12 | 12/12 (generation 6/6, repair 6/6) |
| B structurally equivalent extraction | 9/12 | 11/12 |

The two prior false-SAT repairs now return correctly checked UNSAT; the earlier
accepted-but-altered UNSAT control now preserves its windows. The remaining B
mismatch is repair `8c76290cef6036f833b5a4ba`: P0 availability changes from [0,48)
to [2,48), while its stated [0,2) block remains. Independent exhaustive review
finds identical objective-labelled feasible sets (one schedule, optimum (5,16,19)).
The narrowing is redundant for this pair; the original structural mismatch stays
recorded. All B mismatches from both runs were reviewed, including accepted cases.
A's eight nonaccepted outputs comprise six invalid schedules, one false UNSAT
and one invalid output; all remain in the denominator for Li Hao's next review.

The [new aggregate](../results/summary/yaoxiang-availability-pilot-20260930.json)
was independently replayed from immutable raw records, with figures in the local
receipt directory. No prior result was replaced. These cases informed revision 3,
so the apparent change is **development qualification, not an accuracy-improvement
claim**. A's prompts and settings did not change but its outcomes varied; a single
paired rerun does not isolate the causal effect of the B prompt or provider state.
No held-out cases were inspected and no further calls were made.

Commands executed include:

```sh
python -m pytest -q tests/unit/test_availability_extraction_review.py tests/unit/test_extraction_contract.py tests/integration/test_solver_augmented.py tests/unit/test_benchmark_v3.py
python -m pip install --require-hashes -r requirements.lock
python -m pip wheel --no-deps --no-build-isolation --wheel-dir <wheel-dir> .
python -m pip install --no-deps <built-wheel>
python scripts/check_installed.py
python -m pytest -q
python -m pip check
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
python evaluation/offline_demo.py <output-dir>
python evaluation/v2_qualification.py <output-dir> --version 3
python evaluation/v2_qualification.py <output-dir>
scheduling evaluate-plan --cases <pilot-input>/pilot-cases.json --config <pilot-input>/pilot-config.json --output <pilot-input>/preflight.json
scheduling evaluate-batch --allow-live --cases <pilot-input>/pilot-cases.json --config <pilot-input>/pilot-config.json --run-dir runs/yaoxiang-availability-pilot-20260930-01
scheduling evaluate-replay --run-dir runs/yaoxiang-availability-pilot-20260930-01 --export-dir <analysis-dir> --figures
```

`<...>` denotes each logged temporary environment/output path, not a new CLI
option. Exact commands/scripts and platform logs are retained in
`runs/yaoxiang-availability-20260930-01`; the live command is a historical record,
not authorization to repeat it. The initial local pilot launcher compared a
file-byte hash with a canonical JSON hash and stopped before any call; it was
corrected to verify byte-identical copied inputs and their canonical hashes.

## Local reproduction evidence

The credential-scanned archive
`artifacts/yaoxiang-availability-replay-20260930-01.tar.gz` preserves source,
wheel, synthetic inputs/gold, all four raw runs, prompt/config hashes, failed
answers, usage, exports and replay instructions. It is **823,458 bytes**, SHA-256
`cb9a46376de19024667ec3e595a2a3174b0c999ba5e3e949557346401fbb915c`.
After unpacking, all **410 content hashes** verified and all four saved summaries
replayed exactly with the qualified installed package. No credentials or live
calls were needed. This is local reproduction, not independent teammate review
or external sharing. The archive retains the pre-archive-receipt documentation
snapshot; subsequent handoff-only edits do not change qualified code or evidence.

## Assignment and remaining gates

| Assigned responsibility | Current evidence | Remaining dependency |
| --- | --- | --- |
| Schema, CSP/COP, CP-SAT, generation and lexicographic repair; WP1/R1 | Integrated code, exhaustive tiny cases, repair invariants and installed suites | Yong Qing's human mathematical review and team contract sign-off |
| Gold/reference and benchmark review; WP2 | Existing independent v2/v3 labels and optima; current v3 domain provenance review | Human fixture/realistic-language review and fresh final split allocation with Yong Qing |
| NL extraction and B; WP3/R2 | Three saved mismatch certificates, revision-3 prompt, no gold correction, separately capped development qualification | Human semantic review; additional experiments require a fresh cap |
| Domain reasons and proof-aware consumers; R3/R4 review | Independent domain checks; existing UNKNOWN/partial-proof/gold-boundary tests retained | Li Hao/Yong Qing review consumer wording; optional tuning is not required |
| Final-model eligibility, coordination and freeze support; WP4/WP5 | Frozen-run safeguards retained; qualified development runtime | Recorded final-model eligibility/access, reviewed protocol and budget, proposal receipt/feedback, independent teammate replay |
| Formulation, methods and course delivery | Existing method drafts plus this failure analysis and mathematical argument | Final-study analysis, actual contribution/AI disclosure, report, rehearsal and submission |

The proposal remains the user's accepted working scope; this does not invent a
Canvas receipt or teaching-team approval. The model used here is the confirmed
development model. Optional propagation, search tuning, conflict minimization,
feedback rounds and extra models remain deferred pending measured need and scope.
The next concrete task is Yong Qing's independent review of these availability
certificates and the v3 gold/wording pairs, followed by team contract/model/protocol
decisions before fresh held-out allocation. All twelve qualification cases were
already observed during development and must remain outside held-out evidence.

## Publication audit

The user authorized member-branch commit/push after checking the full Yao Xiang
assignment. GitHub main remains `ca710cf`; both it and the existing published
Yao Xiang branch are ancestors of this checkpoint. All 87 qualified source files,
the aggregate, semantic certificate and 410 archived content hashes were rechecked
unchanged. The passing installed suites therefore still cover the code being
published; only handoff/publication metadata changed afterward. No tests or model
calls were repeated without a changed implementation. The archived pre-publication
snapshot stays immutable. This publication does not close the human-review,
final-model/freeze, final-study, independent-replay or course-delivery gates above.
