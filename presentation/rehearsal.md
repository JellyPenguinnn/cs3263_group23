# Fifteen-minute presentation — working rehearsal guide

Use the [current report](../docs/submission-report.md), [claim index](../docs/claim-evidence.md) and [archived demonstrations](README.md). This AI-assisted storyboard is not a finished deck or evidence of a human rehearsal. The balanced, difficulty and historical comparisons are complete; numerical slides must identify them as exploratory development results. Choose speakers as a team, and ensure every member understands the complete system.

## Suggested storyboard

| Slide / elapsed time | Main message and visual | Evidence |
| --- | --- | --- |
| 1 / 0–1:30 | Introduce controlled schedule generation as the core question, with repair as an extension. | Report Sections 1–2; TA-feedback alignment |
| 2 / 1:30–3 | Eight activities, two people and one room: show loose/tight feasibility and two meetings competing for the only room-hour. | R1–R2; checked offline office examples, not extra model results |
| 3 / 3–4:30 | Show integer start domains, non-overlap, deadlines and preferred-start penalties. | R1; generation formulation; repair priorities only briefly |
| 4 / 4:30–6 | Show both paths and the gold boundary. Both get the same public facts; one call per method; independent validator. | R3–R5; original schedule supplied only for repair |
| 5 / 6–8:30 | Lead with 48 balanced generation cases/model and explain the constraint-presence confound that motivated them. Retain failures and separate SAT/UNSAT/profile outcomes. | Balanced audit and figures; earlier generation study remains separately labelled |
| 6 / 8:30–10 | Explain a Qwen balanced invalid schedule versus a strict-format failure. Briefly show the earlier GLM reordered-wording omission: a solver can solve the wrong specification. | Balanced audit; R11–R13 and earlier difficulty trace paths |
| 7 / 10–12 | Explain GLM's balanced transport failure and returned-answer ceiling, conditional objective quality and time/token coverage. Use the earlier valid-but-suboptimal GLM example (15 versus 8) and repair only as extensions. | Balanced audit/resources; R10/R14 in the separate difficulty study |
| 8 / 12–14 | Explain objective priorities, privacy, synthetic-data limits, unsupported weekly/soft-preference features and shared-service uncertainty. | R15–R17/R22; limitations and responsible AI |
| 9 / 14–15 | State bounded conclusions, actual member contributions, AI support and the explicit stopping point. | R18–R22; confirmed contribution accounts |

Use at most one short interactive saved-record demonstration within this timing; a static annotated extract is sufficient for the other example. No live model call is needed. If recording a fallback, use the same preserved evidence and label canned integration examples explicitly. No recording or timed rehearsal is claimed here.

## Quantities to state consistently

- The latest Qwen3.6/GLM pair completed **96 scheduling attempts per model**, from 48 canonical generation cases (24 SAT/24 UNSAT). Two capability completions and one metadata request sit outside scoring: **99 requests/model**, no retries.
- Balanced acceptance: Qwen direct **6/48 (12.5%)**, B **48/48**; GLM direct **47/48 (97.9%)**, B **48/48**. Qwen failures: 23 hard-constraint violations, nine false UNSAT and ten strict JSON-format rejections. Format failure alone is not reasoning failure.
- GLM's one balanced rejection was a `remote_protocol_error` at 34.18 seconds, not a timeout or model mismatch. Both capability responses and all 95 returned scheduling responses identify `glm-5.3-flash`. Keep the failed attempt in the primary denominator; 47/47 accepted returned direct answers is secondary.
- Four deadline/fixed-start profiles each have six SAT/six UNSAT cases. All 48 cases belong to only **three construction families**; balancing removes the identified presence/label association but not all template bias. Human prose/gold review remains pending.
- The earlier difficulty pair remains **200 attempts/model**: 120 controlled, 40 fictional, 40 wording. Its generation view is Qwen **11/30 versus 28/30**, GLM **25/30 versus 30/30**. All five GLM direct generation failures are HTTP 502s; one returned schedule is valid but suboptimal. Two GLM B extraction failures occur in wording. Do not pool these outcomes with balanced results.
- Controlled repair in that extension is Qwen **6/30 versus 29/30**, GLM **30/30 for both**. The 600-attempt Qwen3.6/Qwen3.8 pair remains historical evidence.
- The office illustration is offline only. The implemented study is single-day/30-minute, not the suggested weekly/hourly scenario. Human scope/model clarification remains open.

## Q&A preparation

These are evidence boundaries for members to explain in their own words, not a record that anyone has rehearsed them.

| Question | Answer boundary / evidence |
| --- | --- |
| Why CP-SAT? Is inventing a new solver the contribution? | Integer time domains and coupled constraints fit CP-SAT. The contribution is a controlled comparison, repair formulation and failure analysis; CP-SAT and minimum-perturbation repair are established methods. R1–R3. |
| Why solve three objectives sequentially? | A weighted sum may trade away a higher-priority objective. Sequential proof fixes each optimum before proceeding; timeout limits the proof claim. UNKNOWN is not UNSAT, and FEASIBLE is not OPTIMAL. R1–R2. |
| Could the solver and reference share a bug? | Yes. Independent arithmetic validation and exhaustive tiny checks reduce this risk, without proving the compiler or every gold input correct. R1–R3. |
| Does 48/48 mean deployment reliability or that methods are equivalent? | No. It is finite synthetic development evidence at a ceiling, with related source families. Realism, harder instances and unseen-generator generalization are not established. R5–R8. |
| Why are related cases not independent? | Balanced variants share only three construction families; use descriptive profile/mechanism counts rather than treating 48 cases as independent. Earlier difficulty intervals resample source families to preserve pairing, but do not remove generator bias. R8. |
| Does a structural extraction mismatch prove a semantic error? | No. Structural equality, bounded semantic checks and gold-valid output measure different things. The saved precedence omissions demonstrate concrete semantic failures. R11–R12. |
| Is solver-assisted repair always better? | The observed optimum comparison is conditional on gold-valid SAT outputs and proven reference optima. A valid but suboptimal direct repair is evidence for this case, not a universal result. R10. |
| Does backend variation prove the weights changed? | No. It records reported serving differences. Exact model IDs were required; hidden defaults and serving conditions were not controlled. R4, R14. |
| When might direct reasoning be preferable? | Use the study-specific resource table and its usage coverage. Balanced GLM returned direct answers are accepted; its one failure is operational. The earlier difficulty study also contains a valid but suboptimal direct schedule. Hosted conditions and different failure rates prevent a universal latency or reasoning claim. |
| How is responsible AI addressed? | Explain concentrated burden, objective choices, privacy, negotiability and user control. Formal validity does not establish fairness or adversarial robustness. R15–R17. |
| Do the hosted models satisfy the teaching team's frontier-model wording? | The sources also suggest SoCLaaS/open weights. Actual eligibility or feedback still needs confirmation; neither approval nor rejection is inferred. R20; planning S1. |

## Human rehearsal record — pending

Record the actual date, speakers, deck version, elapsed time, questions answered, weak explanations and corrections. Check chart readability, model/block labels and the saved example commands. Members must verify their own contribution accounts and understand every part, including work supported by AI. Do not mark this complete from a generated storyboard; follow [planning Section 5](../planning.md#5-current-task-queue-and-acceptance-evidence) and the [submission checklist](../docs/submission-checklist.md).
