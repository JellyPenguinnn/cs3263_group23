# Yao Xiang F1 and formal review — 30 September 2026

Branch: `yaoxiang-formal-core`, fast-forwarded from `630d978` to GitHub main
`d12342c` (including Li Hao's `7c066cd`). Existing history and saved runs are
preserved. The user subsequently authorized committing and pushing this checkpoint
to Yao Xiang’s member branch. This does not authorize a main merge or new model
calls. Review below is Codex-assisted engineering work;
it does not stand in for a member's mathematical review or teaching-team approval.

## Delivered F1 regressions

[Eight regressions](../tests/integration/test_expanded_extraction_failures.py)
retain the [three exact final responses](../tests/examples/expanded-extraction-failures.json)
from `expanded-development-100-20260930-01`. The small synthetic fixture records
source-record, final-content, gold-problem, repair-context and public-view hashes.
It contains no transport headers, credentials or reasoning traces. Gold cases are
regenerated from v2 seed 3264 and v3 seed 3265; tests require their original hashes.
A fresh clone can run these regressions without the full live archive or a key.

| Saved failure | Reproduced outcome and independent check |
| --- | --- |
| `dev-v2-3264-slack-0-fixed_start-unsat-0-repair` | A0's updated fixed start at slot 1 is omitted. The extracted problem admits the unchanged old schedule, with `(M,T,P)=(0,0,0)`. A0 remains at 3; gold rejects it. The old schedule is valid for the original problem. |
| `dev-v2-3264-interaction_density-2-fixed_start-unsat-0-generation` | A1's fixed start at slot 2 is omitted. CP-SAT optimizes the extracted problem, but its schedule violates the missing gold anchor. |
| `dev-v3-1cb82271f05a61f8e4b44569-generation` | A normal `stop` completion contains malformed JSON. Python reports a delimiter error at line 25, column 9; the actual token is `]` closing an object. It remains `INVALID_OUTPUT`, has no extracted specification/solver result, and never calls the solver. |

In each omission case, A0 and A1 both last one slot, require Rpair and must start
at the same slot in gold. The two simultaneous intervals contradict unit capacity.
An independent exhaustive `48^2` two-activity check proves this subproblem has no
assignment; hence the complete problem cannot have one. Removing the omitted
appointment admits a witness. Independent full-schedule arithmetic also confirms
that the actual pipeline witness satisfies the extraction but fails gold.

Adding only the omitted field to a separate diagnostic copy yields a structurally
equivalent gold problem and CP-SAT `INFEASIBLE`. This supports attribution in these
two cases. The restoration is evaluator-only: it never changes the fixture, public
request, pipeline, primary score or archived response. Tests assert one injected
completion, neutral request IDs, preserved raw content and correct failure categories.
These are offline regressions of observed failures, not evidence of improved LLM accuracy.

## Prompt review and remaining qualification

Revision 3 already requires all hard constraints, complete updated repair facts
and retention of contradictions, but its explicit final audit emphasizes
availability lists. Both omitted appointments were present in the public text.
The missing JSON object delimiter is a syntax failure, not an output-limit event.
There is no evidence that deterministic parser correction is an appropriate fix.

One bounded amendment is justified for later review. Proposed text, **not installed
or qualified**, is:

> Before returning JSON, check every stated fixed appointment against a fixed_start
> record with the same activity and start slot. For repair, use the complete updated
> description as authoritative; old schedule starts are context, not appointments.
> Retain all stated fixed appointments even when they conflict through a shared
> participant or resource. Check that every JSON object and array closes correctly;
> return the complete specification without dropping contradictory requirements.

It adds no case IDs, benchmark answers, gold data, output fields or extra call.
Keep the shipped revision-3 prompt unchanged for F2's model comparison. After
model/backend selection, consider this single candidate under otherwise identical
settings, a new run identity and a fresh bounded cap. Do not combine a model and
prompt change and attribute improvement to one factor, or chase perfect accuracy
on the known cases. Optional JSON-mode, feedback and solver optimizations remain deferred.

## F2/F6 formal and evidence review

The integrated F2 execution metadata distinguishes configured request settings
from unavailable defaults/revisions. Frozen execution detects fingerprint drift
and preserves it on resume. The observed serving-version discrepancy does not
prove different weights, but a stable model label also does not establish fixed
backend identity. The six completed qualification calls and remaining policy
stop are unchanged; no model decision or new inference was made here.

The eight equivalent encodings among ten structural mismatches were independently
rechecked from the saved records: immutable activity/time facts, precedence and
weighted preferences match; exhaustive per-activity arithmetic yields the same
legal domains. With identical assignments and binary interactions, this establishes
equal feasible sets and objective functions under v1 for those eight instances.
The two omissions have unequal domains. This leaves the original structural metric
unchanged and does not establish general language understanding or human sign-off.

The report's formal claims were checked against the current compiler, independent
enumerator, validator and full regression suite: whole-window containment, exact
lexicographic stages, retained incumbents, coupled repair `(3,4,0)`, movement versus
shift trade-offs and proof/input correspondence. The [single report source](study-draft.md)
now includes a concrete omission example; [C5](claim-evidence.md) links its executable
evidence. No second report or new solver was introduced. Members still need to
interpret and review these arguments themselves.

## Executed checks

- New failure regressions: **8 passed**.
- Complete installed macOS Python suite: **560 passed** in 37.24 seconds.
- `scripts/check_installed.py` and `pip check`: passed.
- All **81 inherited source/test/prompt hashes** still match Li Hao's tested snapshot;
  production code, active prompts, dependencies and scoring are unchanged.
- Expanded-study semantic review: **8 equivalent encodings, 2 true omissions**.
- Offline replay: **200 attempts**, exact saved summary; **302 JSON files unchanged**.

Local audit script and receipt: `runs/yaoxiang-f1-review-20260930-01/`.
Run it from the repository with
`PYTHONPATH=. .venv/bin/python runs/yaoxiang-f1-review-20260930-01/audit_semantics.py`
only in a new copied audit directory, since its receipt is write-once. It requires
the preserved synthetic raw archive. The tracked failure tests need no archive:

```sh
.venv/bin/python -m pytest -q tests/integration/test_expanded_extraction_failures.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_installed.py
.venv/bin/python -m pip check
```

The inherited Linux qualification is 552 tests on the exact unchanged runtime;
this session's 560-test result is macOS evidence, not a new Linux or hosted-CI run.
No API requests occurred. No held-out cases or historical result files changed.

## Remaining dependencies and next owned task

F1's required regression package and bounded prompt review are delivered. The
prompt experiment and scientific configuration choice remain dependent on F2.
Li Hao coordinates the stopped backend qualification; Yao Xiang coordinates actual
final-model eligibility and reviews the eventual model/prompt choice. Proceed with
the one-candidate prompt experiment only after those development prerequisites
and a new cap are resolved. Course eligibility is required for final freeze,
not for authorized SoCLaaS development.

F3–F5 remain Yong Qing-led: candidate policy and fresh data, frozen rehearsal,
compatible-block analysis and reproduction archive. Yao Xiang's gold/text review
requires those packets; it cannot be marked complete before they exist. Gates A/B
still need human review; final readiness/C/D need actual model/data/protocol,
results, independent teammate replay, final report format audit and submission.
Optional solver speed work, feedback and extra research models are not missing core
implementation. Current solver timings give no reason to undertake them now.
