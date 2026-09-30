# Yao Xiang reference and reasoning review — 30 September 2026

Member branch `yaoxiang-formal-core` was fast-forwarded from `c65f4d1` to latest
GitHub main `84cc95c` (PR #7, incorporating Li Hao's `ddc130f`). The checkout was
clean and no work was dropped. The user subsequently authorized committing and
pushing this review to `yaoxiang-formal-core`. This authorizes member-branch
publication only; main integration, human sign-off and live calls remain separate.
The JSON certificate retains its original pre-publication coordination snapshot.

## Current assignment status

R1 repair invariants, R2 extraction diagnostics, R3 domain reasoning and the
compatible R4 consumer are already integrated. The next available Section 5
work was the formal review of Yong Qing's redesigned benchmark and the saved
extraction mismatch. This review implements independent regression certificates
and supplies their mathematical argument. It does not rebuild the compiler or
change its guarantees. Optional search tuning, propagation, conflict minimization
and general semantic-equivalence automation remain deferred.

| Responsibility | Completed here / existing evidence | Remaining gate |
| --- | --- | --- |
| WP1 / R1–R3: schema, compiler, repair and reasoning | Existing implementation retained; all v2 unary domains and exclusion reasons cross-checked independently | Yong Qing's human mathematical review and team contract sign-off |
| WP2: review v2 gold and constraint effects | Full 144-case certificates; all 84 original-family precedence edges have counterexamples on removal; limitations below | Yong Qing reviews whether construction diversity is sufficient before final allocation; realistic prose and human wording review remain open |
| WP3 / R2: extraction analysis | Saved pilot's 16 added bounds proved redundant for that pair; structural mismatch and scores retained | Human semantic review; new model qualification requires a new cap |
| R4: formal proof/gold boundaries | Existing UNKNOWN, partial-proof, extracted-versus-gold and objective tests included in the full suite | Li Hao/Yong Qing review actual consumer labels; automated checks are not human approval |
| WP4 / WP5: freeze, reproduction and coordination | Integrated frozen controls retained; current tests pass against qualified installed macOS/Linux runtimes | Final model/access/eligibility, protocol and budget decisions; independent teammate replay |
| Formulation, methods and delivery | This mathematical handoff supplements existing method drafts | Complete final-study discussion, actual contribution/AI disclosures, rehearsal and submission receipts |

## Independent reference certificates

The selected v2 development matrix uses seed 3264 and contains 144 cases from
72 related generation/repair families. The new
[`test_v2_formal_review.py`](../tests/unit/test_v2_formal_review.py) uses the
independent arithmetic oracle in [`formal_support.py`](../tests/formal_support.py).
The oracle imports schema types only; it does not call the compiler, domain
analysis, objective implementation or production validator. Its assignment
checker was extracted from the existing exhaustive enumerator so bounded review
can reuse the same independent arithmetic without enumerating 48^12 assignments.
The complete solver/oracle regression suite checks that refactor.

The generator still calls the reference solver to construct the matrix. The
certificates below independently check the selected labels and objective tuples;
simply agreeing with the generator's status would not be enough.

- **72 UNSAT cases:** project onto A0/A1 by removing other activities and their
  incident rules. This relaxes the problem. Both single-activity projections are
  feasible, but every one of 48² pair assignments is infeasible under independent
  arithmetic: 165,888 pair assignments across the matrix. Removing the pair's
  shared resource restores feasibility. An infeasible relaxation proves the full
  case infeasible; the proof does not depend on the CP-SAT infeasibility flag.
- **36 SAT generation cases:** independently verify each supplied witness and its
  zero preference cost. Nonnegative weights give a lower bound of zero, so the
  witness proves optimality without trusting the solver's objective bound.
- **36 SAT repair cases:** independently verify the original schedule, then show
  it is infeasible under the updated problem. Therefore M >= 1. Integer starts
  imply T >= M >= 1. Enumerate every single-activity one-slot move, including
  both directions and all activities. A feasible candidate attains M=T=1; the
  minimum preference cost among that complete set establishes the third stage.
  The recorded witness and expected tuple match this independent optimum.
- **84 precedence edges over 72 original families:** swap the edge's two tasks
  inside their original combined time span. The resulting assignment violates
  the original problem and becomes feasible when that edge alone is removed.
  This witnesses a real feasible-set restriction, not merely a listed edge.
  The claim concerns the feasible original families; an already-UNSAT update
  cannot establish edge relevance by comparing its empty feasible set.

For R3, the suite independently checks all **1,152 activity domains** and
**55,296 activity/start candidates**. Every one of the **46,734 excluded starts**
has a sufficient actual cited horizon, availability or unary rule. Accepted and
excluded starts cover the horizon without overlap. Nonempty unary domains still
do not prove full feasibility. These are finite checks on the selected matrix,
not a general proof or a human review of every supported future input.

## Saved extraction mismatch: a bounded semantic proof

Saved run `yongqing-v2-pilot-20260929-01`, case
`dev-v2-3264-interaction_density-2-deadline-sat-0-generation`, has 16 extra
release/deadline constraints in B's extracted specification. Its record checksum
was verified before review. All other structural fields and original constraint
multiplicities match; no original rule is omitted and preference costs are
unchanged.

For each activity, enumerate starts satisfying only its duration, horizon and
its own/required-entity availability. This is a superset of starts permitted by
the full problem. Let L be the minimum such start and U the maximum such end.
Every added release r satisfies r <= L; every added deadline d satisfies d >= U.
Thus each added bound is implied even by that relaxed unary problem. Adding all
16 bounds cannot remove a feasible assignment or change any objective value.

The [machine-readable certificate](yaoxiang-reference-review-20260930.json)
records the actual bounds and hashes of both specifications and the saved record.
This establishes equivalence for this pair only. The original structural
mismatch remains useful provenance and was not changed to an exact match;
no scoring, raw reply, prompt, run or model-performance claim was revised.
This diagnostic never supplies gold information back to inference.

## Implications for the next benchmark review

The matrix has structural variation and supported labels, but all 72 UNSAT
cases use the same A0/A1 resource-conflict pattern. Sweeping unrelated activity
count or precedence does not establish that these contradictions require deeper
reasoning. All 36 SAT generation references attain zero preference cost, and all
36 SAT repairs have M=T=1. The current matrix therefore does not measure varying
optimal repair burden or coupled cascades, even though the core supports them.

Retain the current matrix and pilot as development evidence. Before freezing a
final matrix, Yong Qing should decide with Yao Xiang whether to include distinct
contradiction mechanisms, competing-preference optima and coupled multi-activity
repairs. The existing tiny R1 regression A0/B1/C2 → A1/B2/C0 proves that changing
one participant's availability can force all three activities to move, with
(M,T,P)=(3,4,0). It provides a review example, not an untouched held-out instance.
Any changed generator/selection policy needs a new benchmark version and run;
this review makes no such scientific change on another owner's behalf.

These findings support three report explanations: unary domains reduce the
assignment space but miss resource contradictions; lexicographic repair requires
explicit lower bounds and can propagate beyond the changed activity; structural
extraction mismatch is not necessarily semantic error, while a solver proof alone
cannot establish faithful interpretation of a request.

## Executed verification and next task

- Initial new reference checks plus existing formal/solver tests: **97 passed**.
- Expanded domain review plus R3 tests: **16 passed**.
- Complete suite with current tests and noneditable installed package:
  **422 passed on macOS ARM64**, **422 passed on Linux ARM64**.
- `pip check` passed on both; installed assets match current source on both.
- The previously qualified runtime wheel/dependencies were reused because no
  production code, prompt, dependency or metric changed. All current runtime
  Python files match the installed macOS package. Tests ran from a fresh
  credential-free source snapshot, not an editable-runtime fallback.
- The proof audit script produced the full matrix certificate and the 16-bound
  saved-response diagnostic. **Zero live model calls**; no held-out evaluation.

Commands: `python -m pytest -q tests/unit/test_v2_formal_review.py
 tests/unit/test_formal_qualification.py tests/unit/test_solver.py`,
`python -m pytest -q tests/unit/test_v2_formal_review.py
 tests/unit/test_domain_analysis.py`, `python -m pytest -q`, `python -m pip check`
and `python scripts/check_installed.py`. The initial audit script invocation
needed the repository root on its test-helper import path; its successful command
was `PYTHONPATH=. .venv/bin/python runs/yaoxiang-reference-review-20260930-01/audit.py`.
That review script is separate from the installed-package qualification.
Source hashes, logs and the executable audit script are preserved under that
ignored run directory. Hosted CI was not checked and independent human replay
is still pending.

The next concrete task is Yao Xiang/Yong Qing review of these certificates and
construction limitations, followed by a decision about the next benchmark
version before final split allocation. Li Hao reviews the resulting public
wording. Human reviewer names, dates and conclusions must be supplied by the
actual reviewers; this AI-assisted analysis does not sign on their behalf.
The proposal receipt, new teaching-team feedback and final-model eligibility
remain unconfirmed in this checkout. Existing authorized credential availability
is unchanged, but previous live-call caps are consumed. Course coordination can
proceed independently of the new benchmark work.
