# Evidence-based scheduling demonstration

Use the [current report](../docs/submission-report.md), [three evaluation charts](../results/figures/two-model-development-20261002/) and [rehearsal guide](rehearsal.md). Both Qwen3.6 and Qwen3.8 comparisons are complete. These are exploratory development results, with 600 scheduling attempts per model; model eligibility and actual human review remain separate course-delivery items.

## Current archived examples

Run from the repository root after the README installation steps. Verify and extract the committed evidence into a **new** directory; these commands make no model calls:

```sh
python3.12 scripts/verify_evidence.py --extract-to runs/presentation-evidence
.venv/bin/scheduling explain --run-dir runs/presentation-evidence/qwen36/runs/controlled/controlled \
  --case-id family-1b6a21e9eaa5121c07e7b362-generation --approach solver_augmented --format json
.venv/bin/scheduling explain --run-dir runs/presentation-evidence/qwen38/runs/controlled/controlled \
  --case-id family-178d62b21632eb32c9dcb923-repair --approach direct --format json
```

The first example shows Qwen3.6 changing A1's deadline from slot 3 to slot 7 during extraction. The compiled specification permits a schedule, but independent gold validation rejects it. The second shows a gold-valid Qwen3.8 direct repair that moves two activities while the reference needs only one. It illustrates why acceptance and optimal repair are separate measures. Claims R11 and R10 in the [claim index](../docs/claim-evidence.md) bind these examples to saved evidence.

Use the current CLI to inspect saved records. To reproduce the original analysis, follow [the exact-source replay instructions](../docs/evidence.md); do not silently rescore archived results with a changed implementation. Never correct a failed extraction and present it as the original model answer. A saved-record demonstration can supplement the presentation; a deck, recording and timed human rehearsal still need to be completed.

## Historical baseline demonstrations

The following examples document earlier integration checkpoints. Their smaller runs and rates are historical, not the completed two-model comparison above. The original private archives are needed for these old run paths.

Run from the repository root after the README installation steps. This workflow
makes zero model calls. With the preserved synthetic live archive available:

```sh
.venv/bin/scheduling evaluate-replay --run-dir runs/main-baseline-20260929-01 --export-dir artifacts/demo-replay
.venv/bin/scheduling explain --run-dir runs/main-baseline-20260929-01 --case-id dev-3263-interaction_density-1-repair --approach solver_augmented
.venv/bin/scheduling explain --run-dir runs/main-baseline-20260929-01 --case-id dev-3263-resource_contention-0-repair --approach direct
.venv/bin/scheduling explain --run-dir runs/main-baseline-20260929-01 --case-id dev-3263-interaction_density-0-repair --approach solver_augmented
```

1. Explain the common public problem and original schedule, then the two paths:
   one direct call versus one extraction plus fixed CP-SAT. Gold stays evaluator-only.
2. The first repair moves A7 earlier one slot. Read (M,T,P)=(1,1,3), stage bounds,
   gold acceptance and P7's 30-minute inconvenience. Optimality under the chosen
   objective does not establish fairness or capture missing commitments.
3. The direct example is a false UNSAT; use its saved reference/accepted B answer
   in the case explorer to inspect the feasible counterexample.
4. The final example is a schema-invalid extraction. Retain the failure rather
   than presenting a repaired output as the model's answer.
5. Use the read-only dashboard for monitoring/results, and explain that these
   are 30 development cases, not frozen held-out findings or a superiority claim.

The 30 September [integration qualification](../docs/lihao-integration-followup.md)
verified the three explanation commands above on installed macOS/Linux builds.
The later v2 pilot can be replayed separately when its synthetic archive is available:

```sh
.venv/bin/scheduling evaluate-replay --run-dir runs/yongqing-v2-pilot-20260929-01 --export-dir artifacts/demo-v2-replay --figures
```

Keep this 12-case/six-family pilot separate from the original 30-case run: A
accepted 3/12 and B 12/12, with no live paraphrase/reordering checks. Show A's
prose-wrapped JSON as a parser failure even though its discussion recognized
infeasibility. These observed failures motivate analysis, not manual rescoring
or a claim that a 12-case pilot establishes general superiority. The new local
replay archive and checksums are listed in the qualification receipt.

A fresh clone without raw live evidence can use the existing explicit canned demo:

```sh
.venv/bin/python evaluation/offline_demo.py runs/NEW-demo
.venv/bin/scheduling explain --run-dir runs/NEW-demo --case-id repair --approach solver_augmented
```

The canned demo is integration evidence only. Choose a fresh directory. Do not
present its injected answers as model responses. Review the whole pipeline and
rehearse timing as a team; no rehearsal or teammate sign-off is recorded here.

## Historical direct-component examples

These are public synthetic examples and explicitly canned replies, not the shared
benchmark fixtures, recorded model outputs, or independent validation evidence.
Run from the repository root after the README installation steps:

```sh
.venv/bin/scheduling direct-offline --text-file presentation/tiny-generation.txt --response-file presentation/canned-generation.json --task-type generation --activity-id A --activity-id B
.venv/bin/scheduling direct-offline --text-file presentation/tiny-repair.txt --response-file presentation/canned-repair.json --task-type repair --activity-id A --activity-id B --original-schedule presentation/tiny-original.json
```

Explain the example in this order:

1. A and B each last one 30-minute slot, use P, and require A before B.
2. The old schedule A=0, B=2 meets the original requirements.
3. P becomes unavailable in [0,1), so A must move. The candidate A=1, B=2 moves
   one activity by one slot and keeps B unchanged. At least one activity and one
   slot must change; this candidate meets those lower bounds with no preferences.
4. The parser checks structure and ID coverage. Gold feasibility and objective
   validation were pending at this original checkpoint; the integrated demo above
   now uses the completed shared validator.

The live development calls are stored privately under
`runs/lihao-components-20260929-01/`, with source snapshots and checksums. The
live generation answer was A=0, B=1, whereas the canned example uses A=0, B=2;
both respect the tiny original constraints. Do not present the canned answer as
the model's answer. The common old repair schedule remains A=0, B=2 regardless
of a model's generated schedule.

For a future, separately authorized live check, load credentials as documented in
README, create an ignored output directory, and use `scheduling direct-live` with
an explicit model, output-token limit and new output filename. Each invocation
makes at most one completion call. The two-call authorization of 29 September
has been consumed; these demo commands remain entirely offline.
