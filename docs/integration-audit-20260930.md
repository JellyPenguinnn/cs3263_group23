# Integrated implementation audit — 30 September 2026

## Outcome and Git state

The three published member branches are already ancestors of GitHub main
`92a975bbcb17721cd312b72d89d1460a080c1468`:

| Published branch | Tip | Integration |
| --- | --- | --- |
| `lihao-llm-baseline` | `8cc43b6` | Included in main |
| `yaoxiang-formal-core` | `630d978` | Included in main |
| `yongqing-evaluation` | `b94f707` | Included in main |

At the verification snapshot, the working branch was `yongqing-evaluation` at
that main commit, with the
latest authored-text package and this integration fix uncommitted. At that point, no branch
reset, commit, push, PR, remote merge or live model call occurred. The local
`main` name still points to an older commit; the working branch already contains
current `origin/main`, so no checkout switch or redundant merge was needed.

## Final stage audit and corrections

A subsequent requested failure/boundary audit reproduced two additional defects:

1. A structurally valid but gold-invalid model schedule could contain an enormous
   integer start slot. CLI explanations overflowed in `timedelta`; dashboard
   calendar rendering could fail similarly. Both readers now label out-of-horizon
   slots without trying to convert them to dates. Python retains exact slot
   values; the browser directs values beyond JavaScript's exact-number range to
   the preserved raw response. Independent rejection and raw records are unchanged.
2. An older case-detail response could overwrite a newer selection or reopen a
   dismissed dialog; an obsolete error could obscure a current case. Request
   order and run/variant/repeat checks now suppress stale responses and errors.
   Closing, Escape and selection changes invalidate outstanding detail requests.

Regression tests reproduced the failures before correction. The focused Python
consumer suite passes **44 tests** and the frontend suite passes **seven tests**.
Final fresh noneditable macOS/Linux ARM64 builds each pass **489 Python tests and
seven frontend tests**, installed assets/dependencies, complete v1/v2/v3/authored
canned integration, 24 authored explanations, figure exports and exact replay of
all four historical summaries. The 486/three-test receipt below remains the prior
integration snapshot; [the final stage receipt](../configs/development/stage-verification-20260930.json)
records the new 97 source/fixture hashes, exact versions and log paths.

An actual in-app browser check opened the deliberately rejected extreme-slot
case, displayed its violations beside the accepted canned solver answer, and
closed the dialog successfully; no console errors were reported. The screenshot
and synthetic browser run are saved under `runs/stage-validation-20260930-01/`.
The temporary verification server was stopped; the existing user dashboard was
not changed. This is failure-display evidence, not model-performance evidence.

The §4–9/11 requirements matrix below remains applicable. Current supported
engineering paths have no known defect found by this audit, while human/final-study
acceptance gates remain open. No prompt, solver semantics, scoring rule, stored
live result or live-call cap was changed. The verification receipt records the local, uncommitted snapshot.

The final local archive is `artifacts/stage-validated-baseline-replay-20260930-01.tar.gz`
(810,221 bytes), SHA-256
`f3b06b8e4b21dad01f891a5c4fb127a1173dbf1633050f19f5858cb9c52c18a0`.
All 460 content checksums passed after unpacking; historical/authored replay and
all 24 authored explanations passed using the qualified installed package. Its
credential scan passed. This immutable archive predates adding its own receipt
to these documents. External sharing and independent human replay remain pending.

## Integration defect found and fixed

The authored-case runner/replay path supported bundle 2.0, but the dashboard
reconstructed every case with the legacy `BenchmarkCase.from_dict`. A saved
authored run raised `Missing or unsupported benchmark case fields`; its HTTP
API returned 422. The explanation CLI uses the dashboard's evidence reader,
so it was affected too.

`dashboard/service.py` now uses the shared `load_cases` boundary and validates
references against the correctly typed case. JSON responses keep the existing
shape and retain authored provenance. Independent rescoring, checksums, caching
and read-only behavior are preserved. No gold or review metadata is added to
model requests. No UI layout, prompt, metric or solver semantics changed.

The dashboard fixture now exercises both legacy and mixed authored bundles.
Regressions cover monitoring, references, HTTP case/detail routes, corruption,
record immutability and deterministic explanations without inference. The new
HTTP test failed before the fix and passed after it. CI now executes the authored
qualification alongside v1 preflight and v2/v3 qualification.

## Audit against planning.md

| Requirement | Implemented and checked | Remaining acceptance work |
| --- | --- | --- |
| §4 Li Hao: provider/direct/CLI/package/demo | Shared bounded provider; strict direct generation/repair; neutral B metadata; installed prompts/TLS/assets; R4 formatter; read-only dashboard and demo | Human consumer/wording review; final-model capability/access checks under a new cap; final docs/demo assembly |
| §4 Yao Xiang / WP1, R1–R3 | Canonical schema and repair invariants; exact sequential CP-SAT objectives; parser-checked extraction revision 3; typed differences; bounded domain reasons; independent tiny certificates | Human mathematical/semantic sign-off; final-model eligibility and proposal receipt/feedback coordination |
| §4 Yong Qing / WP2 | V1 preserved; seeded v2 matrix, v3 challenge cases, family/duplicate audits; authored prose support and twelve explicitly AI-assisted drafts | Human prose/gold and equivalent-rendering review; independently human-written requirement; fresh final allocation and construction policy review |
| WP3 failure analysis | Saved A/provider and B extraction failures retained; semantic counterexamples; evaluator regression checks; four historical summaries replayed | Final-study error analysis and named teammate review; no retrospective correction of model answers |
| WP4 frozen controls | Separate development/frozen modes, preflight, hash/manifest/review checks, bounded reservation/resume/stops and model-drift guard | Eligible model/access, reviewed protocol, exclusion registry completeness, fresh held-out inputs, explicit final cap and real study |
| WP5 / §8 analysis | Independent gold validity; SAT/UNSAT/error denominators; conditional repair gaps; canonical pairing/family uncertainty; separate rendering analyses; tables/figures and replay | Final difficulty/repair/robustness findings; independent human replay and claim-to-final-result review |
| §6 architecture | One package/CLI/provider/schema/runner; equal public views to A/B; fixed compiler; evaluator-only gold; saved-record dashboard | No additional component is needed for the current scope |
| §12/17 delivery | Method drafts, four bounded responsible-AI discussion cases and recorded-evidence demo instructions exist | Complete paper/presentation, actual contribution and AI disclosure records, human understanding/rehearsal and submission receipts |

R1–R4 and current engineering integration are implemented. Gate A/B technical
checks are supported; their human review/sign-off remains pending. The evaluation
freeze and Gates C/D remain open. The rounds of implementation do not establish
independent teammate review or final-study completion.

Optional external data, extra models, feedback correction, alternative objective
sensitivity, precedence preprocessing and search tuning are not missing core
components. Decide their value explicitly before adding scope or spending.

## Executed verification

The focused dashboard/explanation/authored/request-boundary/frozen tests passed
**67 tests**. A fresh noneditable wheel on each of macOS ARM64 and Linux ARM64
then passed **486 Python tests and three frontend tests**, installed asset checks,
JavaScript syntax and dependency checks. Locked dependencies are unchanged.

Each installed build also passed 180 legacy canned attempts (including six
intentional failures), 864 v2, 648 v3 and 24 authored canned attempts; resume,
replay and figure export succeeded. The real dashboard service read all twelve
authored cases, and the installed explanation CLI read all 24 A/B outputs.
Consumer checks verified that saved files remained unchanged.

All four historical live summaries replayed exactly: original baseline, v2
pilot, neutral-boundary v3 pilot and extraction-revision-3 qualification. Their
raw failures and accounting remain unchanged. Historical metadata confounds,
small family counts and reuse of development cases still limit interpretation;
this audit produces no new model-performance finding.

[The verification receipt](../configs/development/integration-verification-20260930.json)
records 97 qualified source/fixture hashes, branch ancestry, exact platform
versions and local logs under `runs/integration-audit-20260930-01/`. Local Linux
uses Node 18; hosted CI specifies Node 20. Hosted CI is unverified: `gh` is not
authenticated and the unauthenticated API returned 404. Git fetch succeeded.
No remote check is claimed to have passed for these unpublished changes.

The commands below were executed in fresh installed environments (use new output
paths from the repository root):

```sh
python scripts/check_installed.py
python -m pytest -q
python -m pip check
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
python evaluation/offline_demo.py runs/NEW-legacy-check
python evaluation/v2_qualification.py runs/NEW-v2-check
python evaluation/v2_qualification.py runs/NEW-v3-check --version 3
python evaluation/v2_qualification.py runs/NEW-authored-check --cases benchmarks/fixtures/realistic-drafts-v1.json
scheduling explain --run-dir runs/NEW-authored-check/run --case-id realistic-draft-07 --approach solver_augmented --format json
```

Canned responses test integration, not language understanding. Live authorization
caps from previous runs are consumed; this audit used zero calls.

## Local reproduction archive

`artifacts/integrated-baseline-replay-20260930-01.tar.gz` contains the integrated
source, qualified wheel, logs and preserved synthetic evidence. Size: 752,158 bytes;
SHA-256: `51481261f2598788be82349b5961e5cd95a72bbd721044c933bd170157236867`.
After unpacking, all 453 content checksums passed, four historical and one authored
canned summary replayed exactly, and all twelve dashboard cases plus 24 CLI
explanations passed. The credential scan passed. The archive is local and ignored;
external sharing and an independent teammate replay remain pending. It preserves
the documentation snapshot before this archive receipt was added. Previous
archives are unchanged.

## Next concrete work

1. Publish the verified combined checkpoint directly to `main`, as explicitly
   authorized by the user on 30 September, then verify the remote commit.
   This authorization supersedes the earlier local-only status; immutable
   receipts and archives retain their pre-publication metadata.
2. Complete the human contract, prose and gold reviews. Li Hao checks wording and
   consumers; Yao Xiang checks semantics; Yong Qing checks evaluation and replay.
   AI-assisted drafts cannot silently count as independently human-written cases.
3. Confirm final-model eligibility/access, construction/selection policy, reviewed
   fresh splits and cap; qualify that model on development data before freezing.
4. Execute and analyze the frozen study, then finish the report, presentation and
   independent teammate reproduction. Preserve the recorded development evidence.
