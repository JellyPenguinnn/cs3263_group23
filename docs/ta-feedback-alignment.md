# TA feedback: generation core and bounded extensions

The written feedback supplied by the team on 15 October praises the research question, CSP/CP-SAT connection, evaluation design and responsible AI. Its concern is breadth and timely completion. This document records the response without claiming approval of details that the feedback did not settle. The original Canvas record and current submission arrangements still need human confirmation.

## Scope and stopping point

| Feedback | Implemented response | Boundary |
| --- | --- | --- |
| Keep controlled generation and both approaches central | The report leads with the completed diverse generation comparison: 1,000 cases per method/model, with the 200 eight-activity cases identified separately; one direct call versus one extraction plus fixed CP-SAT; independent gold validation | Earlier 48-case balancing and the later ten-family expansion remain separate studies; synthetic development evidence, not a holdout |
| Start small before scaling | The balanced study fixes eight 1–2-hour activities, two people and one room; preserve the earlier 12-case small view and larger difficulty cases separately | Only three construction families; more rows do not imply independent problems |
| Loose and tight feasible/infeasible examples | Balanced cases include independent SAT witnesses and capacity/precedence UNSAT certificates; the small office illustration explains both | The office illustration is offline; balanced model outcomes are separately measured |
| Make repair minor | Keep the completed 30 controlled repair cases per method/model as a separate extension; describe moved count, start shift and preferences | No further repair dataset or feedback rounds planned |
| Explain failures beyond success rate | Retain trace-backed invalid schedules, false UNSAT, parsing/extraction changes, conditional optimality, provider failures, time and tokens | Solver proof concerns the extracted model; structural differences alone are not semantic errors |
| Wording robustness | Keep matched canonical/paraphrase/reordered observations and extraction counterexamples | One sample per wording and date omissions limit interpretation |
| Feedback correction and UI as bonuses | Existing dashboard remains read-only supporting tooling; no verifier-feedback correction in either method | No UI expansion or dynamic tool-use study needed for delivery |

The earlier D5 engineering stopping point was the completed balanced pair, preserved difficulty/historical evidence, checked office examples and consistent report. The focused D5 follow-up has **96 scheduling attempts per model** over 48 cases with eight activities; the separate difficulty pair retains **200 attempts per model**, maximum 32 activities, with repair/fictional/wording extensions. No additional runtime features, larger dataset or third model is required by this scope. Changes needed for a demonstrated defect or actual course clarification require an impact assessment and separately agreed work. Continue with the submission checklist: member interpretation/contributions, scope/model clarification, final private report, presentation and submission.

## Subsequently authorized and completed D6 expansion

The team subsequently requested a separate 1,000-case generation expansion with the same two methods and Qwen3.6/GLM pair. [The diverse generation protocol](studies/diverse-generation.md) narrowly supersedes the earlier data freeze; [the new protocol](studies/diverse-generation.md) preserves the completed report as the fallback, separates a small-case view from scale stress, and bounds the study at 4,000 main scheduling attempts. This is a team choice, not a TA requirement or approval. All 4,000 scheduling observations are now complete and replay-validated. Qwen direct/assisted acceptance is 308/1,000 and 953/1,000; GLM is 891/1,000 and 988/1,000. The [diverse audit](diverse-comparison-audit.md) separates the 119 infrastructure failures, mathematical/format failures and incomparable timing phases. This completed evidence and report integration are the current stopping point; proceed with the remaining human review and delivery checklist. Repair, feedback correction, weekly semantics and UI scope remain unchanged.

## Additional audit finding: label-correlated constraint types

The earlier difficulty-generation data have no SAT case with an explicit deadline or fixed appointment, while every UNSAT case has at least one. The same constructor pattern affects repair and fictional cases. This permits a potential label shortcut and limits live coverage of the TA's mixed hard constraints; it does not prove shortcut use by a model or invalidate the original scoring. The office examples exercise feasible deadlines/appointments offline only. The report discloses this, and [the balanced generation protocol](studies/balanced-generation.md) now implements a separately versioned 48-case generation confirmation: all four deadline/fixed-start profiles have six SAT and six UNSAT cases, with matched rule counts, operative-constraint checks and explicit dates. The empirical follow-up is complete: Qwen direct/B accepted 6/48 and 48/48; GLM accepted 47/48 and 48/48. Qwen failures separate into 23 hard-constraint, nine false UNSAT and ten strict-format rejections. GLM's one rejection was a transport failure; every returned GLM answer reported `glm-5.3-flash`. Its three construction families and numeric availability templates still limit generalization; human wording/gold review remains pending. Preserve original inputs/results and consumed allowances; any additional inference needs new authorization.

## Exact differences from the suggested scenario

| TA suggestion | Current contract and explicit simplification |
| --- | --- |
| Monday–Friday, 09:00–17:00, hourly slots | One day, 30-minute slots. The illustrative example uses Monday 09:00–17:00; it is not a weekly/hourly implementation |
| Two participants, one room, eight 1–2-hour activities | Exactly implemented in the balanced model study and separate office illustration; the earlier difficulty study varies size, participants/resources and durations. D6 also varies activity count (8–32) and duration (30–90 minutes); its eight-activity view is not an exact copy of the TA-suggested scenario |
| Fixed appointments, availability, non-overlap, deadlines | Implemented in the canonical schema, solver, independent validator and office examples |
| Morning preference | Implemented as a preferred **start** window before 12:00; this does not require the whole activity to finish before noon |
| Minimize consecutive meetings / cluster on the same day | Not implemented. The current soft constraint is weighted preferred-start-window violation; general adjacency/clustering requires new semantics and validation |
| Repair and unchanged unrelated activities | Both methods receive the same original schedule; minimize moved count, then total absolute start shift, then preference penalty. The objective minimizes disruption but cannot guarantee every indirectly affected activity remains fixed |

The course permits simplified idealized sub-problems. The narrower contract is an explicit team choice, not evidence that the TA has approved this exact deviation. Confirm its acceptability under the submission checklist before final submission. Do not expand to weekly scheduling by default or claim unsupported preferences are handled. The written feedback does not independently settle the handout's frontier-model interpretation.

## Executable small office illustration

Run with the locked Python environment from the repository root; the destination must not already exist:

```sh
PYTHONPATH=src .venv/bin/python evaluation/ta_scope_examples.py runs/NEW-office-examples.json
```

The [checked output](../results/summary/ta-scope-examples-20261015.json) contains full formal specifications, solver schedules, independently recomputed validity and explicit evidence labels. All four scenarios have eight activities, Alice and Bob, one capacity-one room, 30-minute slots from 09:00 to 17:00, fixed 1–2-hour durations and 17:00 deadlines. Joint meetings M1–M3 use both people and the room; individual activities use their named person. M1 starts at 10:00. M2/M3 prefer starting before noon.

| Example | Changed restriction | Offline result and independent reasoning |
| --- | --- | --- |
| Loose generation | Full workday availability | Feasible; optimum preference penalty 0 |
| Tight generation | M2 and M3 must each fit within 11:00–13:00 | Feasible; they occupy 11:00 and 12:00, so the minimum preference penalty is 1 |
| Infeasible generation | Both meetings must fit within 11:00–12:00 | UNSAT; each fits individually, but total room demand is 2 hours and room capacity is 1 hour |
| Repair extension | Starting from a valid common schedule, block Alice 15:00–16:00 | Move A3 from 15:00 to 16:00; seven activities stay fixed, including Bob's B2 at 15:00. Objective: one move, two start-shift slots, preference penalty 1 |

The original example schedule is M1 10:00, M2 11:00, M3 12:00, A1 09:00, A2/B1 13:00, A3/B2 15:00. A2/B1 last two hours; all others one. It is feasible but need not minimize preferences before the repair. A3's original time violates the new block, so at least one activity must move. With all others fixed, independent enumeration finds 16:00 as its only feasible replacement: one move and two half-hour start slots is optimal. This proves the example's first two repair priorities without relying solely on the solver. The tiny coupled-repair regression remains available to show when several activities must move.

**Metric distinction:** total shift is the sum of absolute start changes. Here it is two slots, or 60 minutes. Occupancy-cell changes count two vacated plus two newly occupied cells, giving four. These are different measurements. The example reports both for explanation; archived study scoring continues to use total start shift. No occupied-cell metric is retroactively inserted into earlier results.

## Balanced generation evidence and interpretation

The [balanced audit](studies/balanced-comparison-audit.md), [summary](../results/summary/balanced-comparison-20261017.json) and [graphs](../results/figures/balanced-comparison-20261017/) describe all 96 scheduling attempts per model. Every failure stays in the denominator. Qwen's strict-format failures are output-contract errors, not automatically reasoning failures; GLM's single communication error is not a model mismatch or a solver reasoning win. Both B ceilings are finite synthetic observations. The balanced design removes a known association; it does not prove models exploited it before or remove other template effects.

## Earlier generation evidence and interpretation

[The derived summary](../results/summary/generation-focus-20261015.json) verifies the original archive hashes and lists every observation ID in each scope. `scripts/build_generation_focus.py` recreates it offline. `scripts/render_generation_focus.py` produces new charts with receipts; old summaries and charts remain unchanged.

| Generation view | Qwen direct / CP-SAT | GLM direct / CP-SAT |
| --- | --- | --- |
| All 30 controlled cases | 11/30 / 28/30 | 25/30 / 30/30 |
| Small subset, 12 cases | 6/12 / 12/12 | 12/12 / 12/12 |
| Remaining larger subset, 18 cases | 5/18 / 16/18 | 13/18 / 18/18 |

The small and larger views partition generation; they are not extra data. Generation and repair remain paired by construction family. All five direct GLM generation rejections are HTTP 502 errors. Its small-case feasibility ceiling still leaves one valid but suboptimal generation schedule (penalty 15 versus the reference 8). The report analyses these distinctions rather than increasing difficulty until a preferred outcome appears. Fictional/wording extensions and the [full comparison audit](studies/difficulty-comparison-audit.md) retain all 200 observations per model.

The previous combined-scope [report source](history/20261014-report/submission-report.md), [PDF](history/20261014-report/submission-report.pdf), figures and format receipt are preserved. Automated checks and this alignment do not substitute for student interpretation, human input/gold review or course approval.
