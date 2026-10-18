# Fifteen-minute presentation — working rehearsal guide

Use the [current report](../docs/submission-report.md), [claim index](../docs/claim-evidence.md) and [demonstration guide](README.md). This AI-assisted storyboard is preparation, not a finished deck or evidence of a human rehearsal. Lead with the completed 4,000-attempt diverse generation comparison. Earlier balanced, difficulty and historical studies remain separate development evidence. Every member should understand both methods and their limitations.

## Suggested storyboard

| Slide / elapsed time | Main message and visual | Evidence |
| --- | --- | --- |
| 1 / 0–1:30 | Motivate shared schedule generation and state the direct-versus-tool research question. Repair is an extension. | Report Sections 1–2 |
| 2 / 1:30–3 | Explain the worked request and saved timetable: same room, availability, precedence and preferences; direct failure versus valid tool-assisted schedules. | Report Section 4; supplement example trace index |
| 3 / 3–4:30 | Define integer starts, finite domains, non-overlap and preference penalties. Explain why coupled constraints make local choices insufficient. | Report Section 3; compiler and independent validator |
| 4 / 4:30–6 | Show the two pipelines, equivalent public facts, one call per method and evaluator-only gold. Explain why solver correctness does not imply faithful extraction. | Report Section 4 |
| 5 / 6–8:30 | Explain 1,000 cases, ten families, five sizes and balanced SAT/UNSAT labels. Show acceptance and separate valid schedule construction from correct UNSAT prediction. | Report Sections 5–6; current acceptance chart and feasibility table |
| 6 / 8:30–10 | Explain constraint violations, false UNSAT, format rejection and infrastructure separately. Show invented Qwen deadlines and omitted GLM constraints. | Report Section 6; failure chart and original trace references |
| 7 / 10–12 | Discuss conditional optimality, mean/median/p95 tokens and time. Explain why shared-service conditions prevent a controlled latency ranking. | Report Sections 6–7; resource tables and supplement |
| 8 / 12–14 | Discuss synthetic-case limits, related families, unsupported weekly/preferences features, privacy, fairness and user oversight. | Report Section 8; scope clarification in planning S1 |
| 9 / 14–15 | Give bounded conclusions, confirmed personal contributions and AI assistance. Identify generation as core and earlier repair/wording as extensions. | Report Section 9; factual contribution accounts |

Use at most one short saved-record demonstration; static annotated results are sufficient. No live model request is needed. Label canned integration examples explicitly. Keep optional historical examples only if they add an insight without displacing the main analysis.

## Quantities to state consistently

- Main study: **1,000 generation cases**, 500 SAT and 500 UNSAT; **2,000 scheduling attempts/model**, **4,000 total**. One call per method/case; all failed attempts retained. Capability and metadata checks are outside scoring.
- Acceptance: Qwen A **308/1,000 (30.8%)**, B **953/1,000 (95.3%)**; GLM A **891/1,000 (89.1%)**, B **988/1,000 (98.8%)**.
- Valid SAT construction: Qwen A/B **1/500 versus 467/500**; GLM **404/500 versus 492/500**. Correct UNSAT: Qwen **307/500 versus 486/500**; GLM **487/500 versus 496/500**. Aggregate acceptance alone hides Qwen's construction weakness.
- Infrastructure failures: **51 Qwen, 68 GLM**. These remain in primary denominators but are not scheduling mistakes. Returned-response analysis is a secondary diagnostic, not corrected accuracy.
- Conditional preference optimum: Qwen A **1/1**, B **467/467**; GLM A **403/404**, B **492/492**. These fractions include only valid gold-SAT schedules, not all attempts.
- There are ten related construction families and 200 cases per activity-count stratum (8, 12, 16, 24, 32). Distinct fingerprints are not independent samples or proof of extreme computational hardness. The 24 optional reordered conditions were not executed.
- Token statistics exclude missing usage; time statistics retain failures. OS/concurrency and hosted-service conditions varied; no fully matched cross-model timing subset exists.
- Earlier studies remain separate: 48 balanced cases/96 attempts per model; difficulty 200 attempts/model; historical Qwen 600 attempts/model. Do not pool their denominators or transfer wording-robustness conclusions to the current dataset.
- The office demo is offline illustration. Implemented single-day/30-minute semantics differ from the TA's suggested weekly/hourly scenario; scope/model clarification remains open.

## Q&A preparation

These are evidence boundaries to explain in your own words, not a record of completed rehearsal.

| Question | Answer boundary |
| --- | --- |
| Why CP-SAT; is a new solver the contribution? | Integer domains and coupled constraints fit CP-SAT. The contribution is the formulation, inspectable pipelines and evaluated trade-offs; CP-SAT itself is established. |
| Could the solver and reference share a bug? | Yes. Arithmetic validation, independent feasibility certificates and tiny exhaustive checks reduce risk. The shared compiler limits independence of optimality checks. |
| Does 98.8% mean deployment reliability? | No. It is finite synthetic development evidence, with related families and known service/extraction failures. Real-calendar generalization is untested. |
| Why not treat 1,000 cases as independent? | Ten related construction families share mechanisms. The family bootstrap is descriptive design sensitivity, not a real-world population confidence claim. |
| Does a structural mismatch prove an extraction error? | No. Structural equality and semantic equivalence differ. Use the concrete invented-deadline and dropped-constraint traces to demonstrate actual errors. |
| Is B's optimization perfect? | Every valid B schedule matches its proven reference optimum here. This is conditional on validity, bounded constructed instances and a shared reference compiler, not a general guarantee about language interpretation. |
| When might direct reasoning be useful? | GLM constructs 404 valid schedules directly and can propose schedules when no compatible solver/schema is available. Answers still need validation; no universal speed advantage follows from these runs. |
| Why sequential repair objectives? | Fixing each proven optimum preserves priority; a weighted sum may trade it away. UNKNOWN is not UNSAT, and FEASIBLE is not OPTIMAL. Repair is a separately evaluated extension. |
| How is responsible AI addressed? | Explain privacy, unequal inconvenience, objective choices, ambiguity and user control. Formal validity does not establish fairness or live adversarial robustness. |
| Are the models and scope course-approved? | Actual teaching feedback must resolve the hosted-model interpretation and scope differences. Neither approval nor rejection follows from API access. |

## Human rehearsal record — pending

Record actual speakers, deck version, elapsed time, questions answered, weak explanations and corrections. Check chart readability, denominators and saved example commands. Members must verify their own contributions and understand every part, including AI-supported work. Follow [planning Section 5](../planning.md#5-current-task-queue-and-acceptance-evidence) and the [submission checklist](../docs/submission-checklist.md).
