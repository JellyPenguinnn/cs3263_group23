# TA feedback: generation core and bounded extensions

The written feedback supplied by the team on 15 October praises the research question, CSP/CP-SAT connection, evaluation design and responsible AI. Its concern is breadth and timely completion. This document maps the feedback to the implemented scope, evaluation and remaining clarifications.

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

The completed evaluation consists of a primary generation study and separate earlier studies. The balanced study has **96 scheduling attempts per model** over 48 eight-activity cases. The difficulty study has **200 attempts per model**, with repair, fictional scenarios and wording extensions. Further runtime features or new model runs are outside the delivery plan unless a defect or new research question warrants them. The [submission checklist](submission-checklist.md) covers the remaining review and delivery tasks.

## Expanded generation evaluation

The [diverse generation protocol](studies/diverse-generation.md) evaluates 1,000 cases using both methods and the Qwen3.6/GLM pair: 4,000 scheduling attempts in total. It separates an eight-activity view from larger-scale stress tests. This expansion was a team research decision, beyond the TA’s suggested small benchmark. All attempts are complete and replay-validated. Qwen direct/assisted acceptance is 308/1,000 and 953/1,000; GLM is 891/1,000 and 988/1,000. The [comparison audit](diverse-comparison-audit.md) separates the 119 infrastructure failures, mathematical/format failures and incomparable timing phases. Repair, feedback correction, weekly scheduling and UI functionality were not expanded.

## Additional audit finding: label-correlated constraint types

The earlier difficulty-generation data have no SAT case with an explicit deadline or fixed appointment, while every UNSAT case has at least one. The same constructor pattern affects repair and fictional cases. This permits a potential label shortcut and limits live coverage of the TA's mixed hard constraints; it does not prove shortcut use by a model or invalidate the original scoring. The office examples exercise feasible deadlines/appointments offline only. The report discloses this, and [the balanced generation protocol](studies/balanced-generation.md) now implements a separately versioned 48-case generation confirmation: all four deadline/fixed-start profiles have six SAT and six UNSAT cases, with matched rule counts, operative-constraint checks and explicit dates. The empirical follow-up is complete: Qwen direct/B accepted 6/48 and 48/48; GLM accepted 47/48 and 48/48. Qwen failures separate into 23 hard-constraint, nine false UNSAT and ten strict-format rejections. GLM's one rejection was a transport failure; every returned GLM answer reported `glm-5.3-flash`. Its three construction families and numeric availability templates still limit generalization; human wording/gold review remains pending. Original inputs and results remain preserved separately.

## Exact differences from the suggested scenario

| TA suggestion | Current contract and explicit simplification |
| --- | --- |
| Monday–Friday, 09:00–17:00, hourly slots | One day, 30-minute slots. The illustrative example uses Monday 09:00–17:00; it is not a weekly/hourly implementation |
| Two participants, one room, eight 1–2-hour activities | Exactly implemented in the balanced model study and separate office illustration; the earlier difficulty study varies size, participants/resources and durations. The diverse study also varies activity count (8–32) and duration (30–90 minutes); its eight-activity view is not an exact copy of the TA-suggested scenario |
| Fixed appointments, availability, non-overlap, deadlines | Implemented in the canonical schema, solver, independent validator and office examples |
| Morning preference | Implemented as a preferred **start** window before 12:00; this does not require the whole activity to finish before noon |
| Minimize consecutive meetings / cluster on the same day | Not implemented. The current soft constraint is weighted preferred-start-window violation; general adjacency/clustering requires new semantics and validation |
| Repair and unchanged unrelated activities | Both methods receive the same original schedule; minimize moved count, then total absolute start shift, then preference penalty. The objective minimizes disruption but cannot guarantee every indirectly affected activity remains fixed |

The course permits simplified idealized sub-problems. The single-day calendar and preferred-start-only objective are deliberate simplifications; their acceptability remains a scope clarification in the [submission checklist](submission-checklist.md). Model selection is resolved: the team reports that the TA accepts Qwen and GLM for this project.

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

The small and larger views partition generation; they are not extra data. Generation and repair remain paired by construction family. All five direct GLM generation rejections are HTTP 502 errors. Its small-case feasibility ceiling still leaves one valid but suboptimal generation schedule (penalty 15 versus the reference 8). These distinctions separate scheduling quality from service reliability. Fictional/wording extensions and the [full comparison audit](studies/difficulty-comparison-audit.md) retain all 200 observations per model.

The previous combined-scope [report source](history/20261014-report/submission-report.md), [PDF](history/20261014-report/submission-report.pdf), figures and format receipt are preserved. Remaining review and submission tasks are listed in the [checklist](submission-checklist.md).
