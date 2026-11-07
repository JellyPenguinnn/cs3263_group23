# Presentation rehearsal guide

This guide matches the prepared **20-slide deck and 1,814-word script**: slides 1–15 form the main talk, and slides 16–20 support Q&A. The speaking checkpoints total **14 minutes 35 seconds**, leaving 25 seconds for handovers or pauses before the 15-minute limit. Q&A has a separate five-minute allowance. Timing is an estimate until rehearsed aloud.

Use the [report](../docs/submission-report.md), [claim index](../docs/claim-evidence.md) and [demonstration guide](README.md). The proposed speaker allocation is Yao Xiang for slides 1–5, Yong Qing for 6–10 and Li Hao for 11–15. Adjust handovers to the group's speaking pace while preserving the slide sequence.

## Main talk

| Slide | Elapsed time | Main message |
| --- | --- | --- |
| 1 | 0:00–0:30 | Scheduling with language models |
| 2 | 0:30–1:40 | Scheduling as a constraint problem |
| 3 | 1:40–2:50 | Two methods, one independent evaluation |
| 4 | 2:50–4:10 | One room, eight activities |
| 5 | 4:10–5:10 | The experiment |
| 6 | 5:10–6:05 | Solver assistance raises acceptance |
| 7 | 6:05–7:05 | Overall scores hide construction failures |
| 8 | 7:05–8:15 | Failure patterns explain the performance gap |
| 9 | 8:15–9:30 | An exact solver can solve the wrong specification |
| 10 | 9:30–10:30 | GLM5.3 Flash quality and delivery |
| 11 | 10:30–11:35 | Preference quality after feasibility |
| 12 | 11:35–12:40 | What the evidence supports |
| 13 | 12:40–13:20 | What this comparison establishes |
| 14 | 13:20–14:10 | Team contributions |
| 15 | 14:10–14:35 | Discussion |

## Q&A reference slides

| Slide | Purpose |
| --- | --- |
| 16 | Exact model identities, shared-service settings and request/solve limits |
| 17 | Mean, median, p95 and coverage of token usage |
| 18 | Observed pipeline durations and timing-comparison limitations |
| 19 | Lexicographic repair as a separate extension |
| 20 | Research foundations, full references in speaker notes and evidence sources |

Use these only when relevant to a question. A saved-record demonstration is optional; the main talk already contains a measured worked example. Do not make a new model request during the talk or present canned answers as observed model results.

## Quantities and interpretation

- **Models:** Qwen3.6 35B A3B (Qwen3.6), request/response `qwen3.6:35b`; GLM5.3 Flash, request `x-test-1`, response `glm-5.3-flash`.
- **Design:** 1,000 generation cases, 500 feasible and 500 infeasible; two methods and two models give 4,000 attempts. Ten related construction families and five sizes (8, 12, 16, 24, 32 activities) do not establish independent real-world sampling. The 24 optional reordered conditions were not executed.
- **Acceptance, direct versus solver-assisted:** Qwen3.6 308/1,000 (30.8%) versus 953/1,000 (95.3%); GLM5.3 Flash 891/1,000 (89.1%) versus 988/1,000 (98.8%). Gains are **64.5 and 9.7 percentage points**, respectively. All failures remain in these denominators.
- **Valid schedules:** Qwen3.6 1/500 versus 467/500; GLM5.3 Flash 404/500 versus 492/500. Correct infeasibility answers: Qwen3.6 307/500 versus 486/500; GLM5.3 Flash 487/500 versus 496/500. Overall acceptance hides the direct Qwen3.6 construction weakness.
- **Conditional optimality:** Qwen3.6 direct 1/1 and assisted 467/467; GLM5.3 Flash direct 403/404 and assisted 492/492. These denominators include only valid schedules on feasible cases. Reference optima range from 0 to 37, with median 12; only two are zero. The reference optimizer shares compiler code.
- **Failures:** 51 infrastructure failures for Qwen3.6 and 68 for GLM5.3 Flash. They are distinct from invalid schedules, false infeasibility and formatting errors. GLM5.3 Flash's paired returned-response subset has 891/935 direct versus 927/935 assisted acceptance; the 3.85-point gap is diagnostic, not corrected accuracy.
- **Resources:** unknown token usage is excluded, not counted as zero. Duration statistics include failures. Changing OS, concurrency and backend conditions prevent a controlled intrinsic-speed ranking.
- **Scope:** generation is the main study. Repair and wording checks belong to earlier studies with their original denominators. Single-day, 30-minute slots and preferred-start penalties are the implemented semantics; weekly scheduling and richer preferences are outside scope.

## Q&A preparation

Use the following questions to check each member’s understanding.

| Question | Answer boundary |
| --- | --- |
| Why CP-SAT; is a new solver the contribution? | Integer domains and coupled constraints fit CP-SAT. The contribution is the formulation, inspectable pipelines and evaluated trade-offs; CP-SAT itself is established. |
| Could the solver and reference share a bug? | Yes. Arithmetic validation, independent feasibility certificates and tiny exhaustive checks reduce risk. The shared compiler limits independence of optimality checks. |
| Does 98.8% mean deployment reliability? | No. It is finite synthetic development evidence, with related families and known service/extraction failures. Real-calendar generalization is untested. |
| Why not treat 1,000 cases as independent? | Ten related construction families share mechanisms. The family bootstrap is descriptive design sensitivity, not a real-world population confidence claim. |
| Does a structural mismatch prove an extraction error? | No. Structural equality and semantic equivalence differ. Use the concrete invented-deadline and dropped-constraint traces to demonstrate actual errors. |
| Is solver-assisted optimization perfect? | Every valid solver-assisted schedule matches its proven reference optimum here. This is conditional on validity, bounded constructed instances and a shared reference compiler, not a general guarantee about language interpretation. |
| When might direct reasoning be useful? | GLM5.3 Flash constructs 404 valid schedules directly and can propose schedules when no compatible solver/schema is available. Answers still need validation; no universal speed advantage follows from these runs. |
| Why sequential repair objectives? | Fixing each proven optimum preserves priority; a weighted sum may trade it away. UNKNOWN is not UNSAT, and FEASIBLE is not OPTIMAL. Repair is a separately evaluated extension. |
| How is responsible AI addressed? | Explain privacy, unequal inconvenience, objective choices, ambiguity and user control. Formal validity does not establish fairness or live adversarial robustness. |
| Are the models and scope course-approved? | The TA accepts Qwen/GLM, as reported in the team’s consultation follow-up. The single-day calendar and preferred-start-only objective remain separate scope clarifications. |

## Rehearsal record

Record actual speakers, deck version, elapsed time, questions answered, weak explanations and corrections. Check chart readability, denominators and saved example commands. The group has confirmed its contribution allocation and whole-project understanding. Practise explaining the findings and limitations without reading the script. Follow [remaining submission tasks](../docs/submission-checklist.md#remaining-submission-tasks).
