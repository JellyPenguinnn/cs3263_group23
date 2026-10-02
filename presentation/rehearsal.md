# Fifteen-minute presentation — working rehearsal guide

Use the [current report](../docs/submission-report.md), [claim index](../docs/claim-evidence.md) and [archived demonstrations](README.md). This AI-assisted storyboard is not a finished deck or evidence of a human rehearsal. Both model comparisons are complete; numerical slides must identify them as exploratory development results. Choose speakers as a team, and ensure every member understands the complete system.

## Suggested storyboard

| Slide / elapsed time | Main message and visual | Evidence |
| --- | --- | --- |
| 1 / 0–1:30 | A changed commitment can force several schedule changes. Introduce generation, minimum-disruption repair and the comparison question. | Report Sections 1–2; a clearly labelled illustrative scenario |
| 2 / 1:30–3 | Integer start variables, legal domains, availability and shared-resource constraints define a CSP/COP. A solver proof concerns its encoded input. | R1; report formulation |
| 3 / 3–4:30 | Walk A0/B1/C2 → A1/B2/C0: all three activities move, summed shift is four slots. Explain the lexicographic (M,T,P) objective. | R2; tested coupled-repair example |
| 4 / 4:30–6 | Show the two-path architecture and evaluation boundary. Same public request and original schedule; independent gold validation. | R3–R5; 240 controlled cases/120 families, 12 fictional scenarios, wording variants of 24 bases |
| 5 / 6–8:30 | Present one grouped chart for each block, then distinguish SAT validity and correct UNSAT. Qwen3.6 benefits strongly from solver assistance; Qwen3.8 approaches the validity ceiling. | R6–R9; current figures and Table 1, exact denominators and paired intervals |
| 6 / 8:30–10 | A deadline changed from 3 to 7 during extraction makes the encoded problem easier. Show the saved Qwen3.6 output and independent rejection. | R11; first current demonstration in README |
| 7 / 10–12 | Near-perfect validity does not prove equivalence or optimal repair. Show the Qwen3.8 direct repair with two moves versus one, plus time/token overhead and operational failures. | R10, R12–R14; second demonstration and Table 2 |
| 8 / 12–14 | Objective priorities can concentrate inconvenience. Explain privacy, requirement ambiguity, synthetic-data limits and shared-backend uncertainty. | R15–R17; report responsible-AI and limitations discussion |
| 9 / 14–15 | State bounded conclusions, actual team contributions and AI support. Explain what was learned and when direct reasoning may be preferable. | R18–R20; confirmed contribution accounts and final report |

Use at most one short interactive saved-record demonstration within this timing; a static annotated extract is sufficient for the other example. No live model call is needed. If recording a fallback, use the same preserved evidence and label canned integration examples explicitly. No recording or timed rehearsal is claimed here.

## Quantities to state consistently

- Each model completed **600 scheduling attempts**: 480 controlled, 24 realistic and 96 additional-wording attempts. Capability checks are outside these scoring denominators.
- Each approach receives 240 controlled cases, 12 realistic scenarios and 48 wording conditions. Wording conditions reuse selected controlled bases, so they are not independent new problems.
- Controlled acceptance is **95/240 versus 229/240** for Qwen3.6 and **239/240 versus 240/240** for Qwen3.8, direct versus solver-assisted. All failures stay in the denominator.
- All **nine Qwen3.8 rejected attempts across the three blocks** are provider failures, not demonstrated reasoning failures. Controlled valid repair optimum matching is **59/60 direct versus 60/60 solver-assisted**.
- More model capability is a plausible explanation for Qwen3.8's stronger observed performance, not an isolated causal result. Shared-service differences and hidden defaults remain uncontrolled; the known synthetic inputs may be too easy to separate these methods.

## Q&A preparation

These are evidence boundaries for members to explain in their own words, not a record that anyone has rehearsed them.

| Question | Answer boundary / evidence |
| --- | --- |
| Why CP-SAT? Is inventing a new solver the contribution? | Integer time domains and coupled constraints fit CP-SAT. The contribution is a controlled comparison, repair formulation and failure analysis; CP-SAT and minimum-perturbation repair are established methods. R1–R3. |
| Why solve three objectives sequentially? | A weighted sum may trade away a higher-priority objective. Sequential proof fixes each optimum before proceeding; timeout limits the proof claim. UNKNOWN is not UNSAT, and FEASIBLE is not OPTIMAL. R1–R2. |
| Could the solver and reference share a bug? | Yes. Independent arithmetic validation and exhaustive tiny checks reduce this risk, without proving the compiler or every gold input correct. R1–R3. |
| Does 240/240 mean deployment reliability or that methods are equivalent? | No. It is finite synthetic development evidence at a ceiling, with related source families. Realism, harder instances and unseen-generator generalization are not established. R5–R8. |
| Why are uncertainty intervals grouped? | Generation/repair cases descend from common sources. Resampling source families preserves that dependence and A/B pairing; it does not remove generator bias. R8. |
| Does a structural extraction mismatch prove a semantic error? | No. Structural equality, bounded semantic checks and gold-valid output measure different things. The saved deadline example demonstrates a concrete semantic failure. R11–R12. |
| Is solver-assisted repair always better? | The observed optimum comparison is conditional on gold-valid SAT outputs and proven reference optima. A valid but suboptimal direct repair is evidence for this case, not a universal result. R10. |
| Does backend variation prove the weights changed? | No. It records reported serving differences. Exact model IDs were required; hidden defaults and serving conditions were not controlled. R4, R14. |
| When might direct reasoning be preferable? | It used less time and fewer tokens in these runs; Qwen3.8's direct validity was near the ceiling. No untested difficulty threshold or guaranteed future trend is claimed. R6, R14. |
| How is responsible AI addressed? | Explain concentrated burden, objective choices, privacy, negotiability and user control. Formal validity does not establish fairness or adversarial robustness. R15–R17. |
| Do the hosted models satisfy the teaching team's frontier-model wording? | The sources also suggest SoCLaaS/open weights. Actual eligibility or feedback still needs confirmation; neither approval nor rejection is inferred. R20; planning S1. |

## Human rehearsal record — pending

Record the actual date, speakers, deck version, elapsed time, questions answered, weak explanations and corrections. Check chart readability, model/block labels and the saved example commands. Members must verify their own contribution accounts and understand every part, including work supported by AI. Do not mark this complete from a generated storyboard; follow [planning Section 5](../planning.md#5-current-task-queue-and-acceptance-evidence) and the [submission checklist](../docs/submission-checklist.md).
