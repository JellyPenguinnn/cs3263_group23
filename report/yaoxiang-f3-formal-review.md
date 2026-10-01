# Yao Xiang F3 formal review — 1 October 2026

`yaoxiang-formal-core` was fast-forwarded from `eecbe45` to GitHub main `ebab01e`,
including Li Hao's published diagnostic and Yong Qing's candidate/rehearsal work.
Existing work and raw records were preserved. The user subsequently authorized
committing and pushing this checkpoint to `yaoxiang-formal-core`. Main integration
and new live calls are not authorized by that instruction.

## Scope and implementation

F1's eight saved-failure regressions and proposed bounded amendment were already
implemented; revision 3 remains unchanged. The prompt experiment still waits for
model qualification and a fresh cap. The next unblocked assigned work was F3's
formal gold cross-check and F6's mathematical evidence. Optional solver speed work,
feedback, new constraints and provider integrations were not added.

[The review helper](../tests/candidate_review.py) independently evaluates unary
requirements, saved witnesses and objective values using the existing test-only
arithmetic evaluator. It does not call CP-SAT or reuse production legal-domain,
compiler or objective helpers. Loading typed cases retains the existing validation
boundary; the subsequent arithmetic review is a separate check. The accompanying
regressions compare these expectations with the real solver.

Three sufficient contradiction certificates cover this candidate policy:

- No start survives an activity's unary requirements over the entire finite horizon.
- Two fixed intervals overlap while requiring a common capacity-one entity.
- An anchored predecessor plus both durations forces the successor's end past its deadline.

The latter two include the responsible rule IDs and numerical bounds/intervals.
These are sufficient proofs for these formal cases, not minimum conflicts or proof
that natural-language extraction is faithful. Removing the disruptive rule in each
preserved UNSAT fixture restores an independently checked original witness.

Bounded optimality checks enumerate the Cartesian product of independently derived
unary domains, then check every binary interaction and objective. Dropping binary
constraints for domain construction cannot discard a feasible assignment. Cases
above 60,000 assignments receive `not_checked_assignment_cap`, never an invented
optimum. This is review/test tooling, not another production solver or model path.

The [12-case fixture](../tests/examples/f3-formal-review.json) preserves six existing
pilot families: within each event/label stratum, minimum recorded domain product,
then case ID, retaining both task siblings. Manifest case hashes are asserted.
Selection uses no model outcomes. Original and updated structures are already in
the development registry; no new holdout or synthetic family was created.

## Observed results

The full saved pilot contains 48 cases / 24 source families. The complete packet
must match its declared IDs and case hashes before receiving a review receipt.

| Independent arithmetic check | Result |
| --- | --- |
| SAT witness feasibility and objective value | 24/24 cases |
| Original repair schedule feasibility | 24/24 repair cases |
| UNSAT certificate | 24/24 cases: eight per mechanism, four source families each |
| Exhaustive objective optimum | 6 SAT cases / 3 source families |
| Remaining SAT optima | 18 not independently enumerated; recorded solver proofs retained |

No disagreement with saved gold was found. Generation/repair siblings are dependent;
48 cases are not 48 independent source problems. Every human review remains pending.

For the preserved coupled repair `family-fb3ef866b748616a6d9a3c55-repair`, A3 lasts
one slot and moves 9→10 after its new fixed appointment. A4 lasts three slots and
uses the same Rpair resource; its old start 10 now overlaps A3, so it must move too.
The saved repair moves A4 to 11, giving `(M,T,P)=(2,2,12)`. Both must move, so M≥2;
two integer moves require T≥2. Exhaustive checking of 50,400 unary-domain
assignments also establishes preference penalty 12 at that optimal `(M,T)`.
This provides an inspectable constructed-pilot example of propagated repair.

## Verification and reproduction

- Final full installed macOS suite: **614 passed** in 55.35 seconds.
- New formal tests: **18 passed** on macOS and Linux ARM64. They cover all three
  mechanisms, removing the event, suboptimal-but-feasible witnesses, the enumeration
  cap, altered/partial evidence and exact saved fixture identity.
- All fields in the independent 48-case receipt match between macOS and Linux.
- Installed assets and dependency consistency passed. Production package, active
  prompts, scoring, generator, dependencies and historical records are unchanged.
- All **76 saved pilot JSON files** remain byte-identical. No new model calls.
- Hosted CI and actual independent human/team replay are not claimed.

Fresh-clone offline regression:

```sh
.venv/bin/python -m pytest -q tests/integration/test_candidate_formal_review.py
```

Full review requires the preserved raw pilot, and a new output path:

```sh
.venv/bin/python -m tests.candidate_review \
  --cases runs/yongqing-f3-pilot-20261001-01/cases.json \
  --manifest benchmarks/manifests/yongqing-f3-policy-pilot-20261001.json \
  --output artifacts/NEW-f3-arithmetic-review.json
```

Create the output parent directory first. Existing receipts are never overwritten.
The tracked [verification receipt](../configs/development/yaoxiang-f3-formal-review-20261001.json)
contains all case certificates, source/input hashes and the remaining limits.

## Remaining dependencies and next task

F3's automated mathematical cross-check is delivered; its actual member gold/text
review, policy/size decision and fresh final draw are not. Yao Xiang should personally
review these three proof mechanisms and the coupled repair, then record actual
findings with Li Hao's wording review and Yong Qing's policy decision. That review
must not be inferred from this AI-assisted implementation.

F2 remains Li Hao-led. The agreed direction is SoCLaaS development followed by an
official provider API for submission; exact final provider/model, access, eligibility
and cap remain undecided. Yao Xiang coordinates course eligibility and reviews the
model/formal assumptions. Keep the stopped development comparison and strict
frozen guards intact. Once model qualification is available, the next F1 experiment
is the one proposed amendment versus revision 3 under otherwise equal settings and
a new cap. F4/F5 final execution/analysis and F6 final report/rehearsal depend on those
actual decisions and reviews. No optional optimization is needed to fill that gap.
