# Final-data preparation and review packet — 1 October 2026

The existing `source-family-v1` builder can produce the working target of **120 distinct source families / 240 controlled cases** within the supported scheduling contract. This was verified with a new offline **development** pilot, not a final draw or model experiment. No scheduling-model call, human approval, final-study seed or spending decision was made.

Keep the **600-call working target provisionally**: construction capacity is demonstrated. Confirm the team's review capacity and the selected model's actual cost/runtime before choosing it. The **312-call compact alternative** remains available by an explicit pre-outcome decision. Neither number is a statistical power calculation or course minimum.

## Delivered work

- Ran the unchanged builder with seed `32661001`, ten families per sweep/level cell, at most 20 proposals per family, five seconds per reference solve and a 180-second construction budget.
- Independently checked the resulting packet with the existing test-only arithmetic reviewer.
- Added [`prepare_case_review.py`](../evaluation/prepare_case_review.py), which verifies complete case membership, exact case/text hashes and substantiated reference labels/optima before exporting reviewer-only records and a pending-review CSV. It performs no model calls or approvals and refuses to overwrite an existing packet.
- Preserved every inspected original/updated structure, rejected proposal and reference. The new cumulative registry extends all 1,071 prior exclusions to **1,429 structures / 29 sources**. The previous registry remains unchanged.
- Prepared 240 per-case review files containing gold, original/updated repair facts, reference stages, and all three public renderings. These are evaluator-only review material, never model input.

The tracked [readiness receipt](../benchmarks/manifests/f3-target-development-readiness-20261001.json) records source/input/archive hashes, actual quotas and limitations. Use the [new cumulative registry](../benchmarks/manifests/development-hard-fingerprints-v2-20261001-target-pilot.json) for subsequent preparation, after including any additional inspected development work.

## Measured construction and mathematical evidence

| Check | Observed result |
| --- | --- |
| Controlled cases / source families | 240 / 120 |
| Each generation/repair × SAT/UNSAT stratum | 60 cases |
| Each sweep/level/task/label cell | 5 cases |
| Repair events | 40 blocked, 40 deadline, 40 fixed start |
| Proposed families | 179: 120 selected, 25 label mismatch, 34 binary targets with unary wipeout |
| Inspected original and updated structures | 358; all included in cumulative exclusions |
| Coupled SAT repairs | 32 of 60 require more than one moved activity |
| Positive preference cost | All 120 SAT cases |
| Independent SAT witness/objective arithmetic | 120 of 120 checked |
| Independent UNSAT certificate | 120 of 120 checked |
| Independently enumerated SAT optimum | 24 cases, using at most 60,000 unary-domain assignments per case |
| Other SAT optima | 96 not independently enumerated; recorded exact solver proofs remain |
| Human gold/text review | Pending |

The generator's exact labels were checked before selection. Exclusions used formal/reference outcomes, never scheduling-model performance. Both task siblings share the updated hard problem; 240 cases are **120 source families**, not 240 independent source problems.

The inspected diversity is meaningful but bounded:

- Activity-count levels use 4, 8 and 12 activities.
- Slack levels have mean unary-start-count ranges of 2.50–2.75, 3.625–4.75 and 6.375–8.50.
- Interaction-density levels span approximately 0.214–0.250, 0.250–0.321 and 0.357–0.429. Adjacent levels can touch; labels are construction levels, not precise performance thresholds.
- Resource-contention levels span approximately 0.036, 0.214–0.250 and 1.000. Other difficulty measures also change; these are not isolated causal interventions.
- Blocked UNSAT uses unary wipeout; fixed-start UNSAT uses a shared-resource collision; deadline UNSAT uses an anchored precedence bound. There are 20 source families per UNSAT mechanism, represented in both tasks. Mechanism and event remain associated by construction.
- Competing preferences create unavoidable cost, and coupled repairs are represented. These are constructed examples, not a representative population of real scheduling requests.

Do not change the policy merely to make A or B score better. If human review finds a genuine defect, record the finding, version the policy, retain this pilot and its exclusions, and repeat only the affected offline qualification before a fresh final draw.

## Decision packet for the team

| Decision | Recommendation / evidence | What remains unresolved |
| --- | --- | --- |
| Construction policy | Retain provisional `source-family-v1`; target-size quota/diversity demonstrated | Actual policy review reference and acceptance of documented mechanism/covariate limits |
| Study size | Provisionally keep 120 controlled families: 480 controlled + 24 realistic + 96 wording calls = 600 | Human review capacity and model/resource qualification; compact is 48 families: 192 + 24 + 96 = 312 |
| Development model | User-selected SoCLaaS `qwen3.8:27b` belongs to the next development stage | Exact backend policy/qualification and new call allowance; this pilot makes no capability claim |
| Final model | No final model or eligibility decision is supplied by this packet | Actual provider/model/access/eligibility and separately authorized budget |
| Final draw | Use a new approved seed after policy/model decisions | No seed or final freeze record is manufactured here |
| Additional repeats | Omit from core until separately selected and supported by verified analysis | Optional repeat policy, identity mapping and cap remain distinct |

The target/compact choice must precede final outcomes. If target review capacity is insufficient, choose compact explicitly; do not take an easy subset of this pilot or relabel its cases as final. Fresh candidates still need overlap checks and a complete packet review. A new random seed does not itself establish freshness.

## Human gold and wording review

The local archive contains `human-review/review-index.csv` and one reviewer JSON per case, plus exact pilot inputs, ledger, references and the independent arithmetic receipt. The CSV begins with blank reviewer fields and `pending` statuses. Make a working copy for actual review findings; the tool does not promote its contents into frozen approvals.

For each case assigned to review:

1. Check the source hash, activity list, duration, assignments, full-window semantics and time conversion. Confirm every public fixed appointment and hard/soft distinction against gold.
2. For repair, check the original schedule against the original specification, unchanged frame/durations/assignments, the updated disruption and the shared old schedule. Inspect moved count, absolute shift and preference cost in order.
3. Check the SAT witness and objective, or the sufficient UNSAT contradiction. Distinguish the independent arithmetic evidence, solver proof, bounded enumeration and remaining unchecked optimality. A sufficient conflict is not a minimum conflict.
4. Compare each reviewed rendering with its own specification and repair context. Note missing/added facts, hidden label hints, ambiguous clock expressions and changes to objective priority. Do not treat a successful parse as semantic agreement.
5. Record the actual gold reviewer, a second wording reviewer, exact findings, corrected artifact/hash if any, and a real decision reference. Unresolved concerns remain pending. Review of this development packet does not approve future cases.

For the eventual final packet, review **all selected canonical texts**, the 48 additional renderings for the 24 selected language bases, and all 12 realistic texts. The full target pilot's three-rendering packet is available for workflow practice and representative policy inspection; this receipt does not claim that humans have reviewed its 720 renderings.

## Realistic authorship worksheet

This is a blank authoring plan, **not twelve scenarios or a valid benchmark bundle**. A human author supplies each original prose request and confirms its provenance. AI-assisted wording must retain `llm_assisted` provenance and cannot silently count toward an independently human-written requirement. Do not use the evaluated model to generate final prose.

| Slot | Task | Intended gold label | Human author / actual reference | Independent reviewer / actual reference |
| --- | --- | --- | --- | --- |
| R01 | Generation | SAT | Unassigned | Unassigned |
| R02 | Generation | SAT | Unassigned | Unassigned |
| R03 | Generation | SAT | Unassigned | Unassigned |
| R04 | Generation | UNSAT | Unassigned | Unassigned |
| R05 | Generation | UNSAT | Unassigned | Unassigned |
| R06 | Generation | UNSAT | Unassigned | Unassigned |
| R07 | Repair | SAT | Unassigned | Unassigned |
| R08 | Repair | SAT | Unassigned | Unassigned |
| R09 | Repair | SAT | Unassigned | Unassigned |
| R10 | Repair | UNSAT | Unassigned | Unassigned |
| R11 | Repair | UNSAT | Unassigned | Unassigned |
| R12 | Repair | UNSAT | Unassigned | Unassigned |

For each slot retain: fictional use case and public prose; source-family identity; single-day 30-minute-grid horizon; activities/durations/participants/resources and availability; hard constraints and weighted preferences; task objective; and the gold `ProblemSpec`. Repair additionally needs the original specification, independently feasible old schedule, exact event and complete updated description. Record a genuine sufficient UNSAT argument or validated witness/optimum. Never force an intended label by dropping public requirements.

Once real content exists, use the existing `AuthoredBenchmarkCase` and bundle format `2.0`. Each `AuthoredRendering` records `variant_id`, verbatim `text`, actual `creation_method`, `author_reference`, `rationale`, `review_status` and `review_reference`. The case also records `gold_author_reference` and `gold_review_reference`. Pending text has `review_reference=null`; approval requires an actual nonempty reference. The typed fields are records, not proof of authorship/review. Preserve source-family grouping and register any material inspected as development before the final allocation.

## Reproduction and next command

Fresh-clone tests for the review-packet exporter:

```sh
.venv/bin/python -m pytest -q tests/integration/test_candidate_review_packet.py
```

The completed development pilot used policy fields recorded in the readiness receipt and seed `32661001`. Its raw archive is local at `artifacts/f3-target-development-20261001.tar.gz`, SHA-256:

```text
a0574076d17af541464d189c18740a9d203734a87f3f695317b443ead6d2b13d
```

It contains 803,306 bytes. Every archived pilot/reviewer file was checked byte-for-byte against its original after packaging. Distribute this reviewed synthetic archive explicitly; its local existence does not mean teammates received or replayed it. Preserve it because rerunning generation recreates reference timings, not exact archived bytes.

After obtaining and unpacking the archive into a new local directory, the next action is to open `human-review/review-index.csv` with the assigned reviewers. The following offline commands independently recheck the preserved packet and create a separate review copy (both output paths must be new):

```sh
.venv/bin/python -m tests.candidate_review \
  --cases artifacts/NEW-unpacked/pilot/cases.json \
  --manifest artifacts/NEW-unpacked/pilot/manifest.json \
  --output artifacts/NEW-arithmetic-review.json
.venv/bin/python evaluation/prepare_case_review.py \
  artifacts/NEW-unpacked/pilot artifacts/NEW-human-review
```

The final-draw command remains gated, not performed:

```sh
.venv/bin/python evaluation/prepare_final_candidates.py runs/NEW-final-candidates \
  --registry benchmarks/manifests/development-hard-fingerprints-v2-20261001-target-pilot.json \
  --policy configs/experiments/ACTUAL-reviewed-policy.json \
  --mode final --seed ACTUAL_APPROVED_NEW_SEED \
  --freeze configs/experiments/ACTUAL-policy-decision.json
```

Uppercase names denote missing actual decision files/values, not files delivered or approvals granted. The prior decision must match the policy, generator, current cumulative registry and draw seed, and contain real policy/model decision references. Final output still has pending gold/text review. The completed development pilot, its review, or a passing test must never be substituted for that decision or a final study.
