# Development checkpoint readiness

The integrated version 2 is a working, course-aligned development checkpoint of the direct-LLM versus LLM-to-CP-SAT scheduling project. Both generation and minimum-disruption repair run end to end through independent gold checking, durable records, replay, analysis, explanations and the dashboard. The final audit found no new blocking implementation defect in the inspected paths. It is ready for focused extraction improvements and final-study preparation. It is not yet a completed course evaluation or submission.

This assessment applies to the local working tree based on `63d68d8`, including the integrity fixes and expanded development study. GitHub `main` still points to that base commit. The uncommitted corrections, expanded results and this audit must be published through an authorized workflow before another member can obtain this exact checkpoint by cloning GitHub.

## Executable evidence

The [audit receipt](../configs/development/checkpoint-readiness-20260930.json) records the checks. The [version 2 qualification](version-2-validation.md) records the earlier full macOS/Linux qualification and exact source hashes.

| Current audit check | Observed result |
| --- | --- |
| Installed macOS Python suite | 521 passed in 31.90 seconds |
| Dashboard JavaScript syntax and regression tests | Syntax passed; 7 tests passed |
| Installed prompts, certificate and dashboard assets; dependency consistency | Passed |
| Installed Python code versus checkout | All 31 Python modules match byte for byte |
| Previously qualified runtime/test/fixture files | All 100 recorded hashes unchanged |
| Fresh expanded offline qualification | 100 cases, 200 canned attempts; generation/repair, both pipelines, real CP-SAT, gold checking, completed resume and replay passed |
| Historical and expanded live-record replay | Five runs, 332 attempts; all five saved aggregate summaries reproduced exactly |
| Dashboard and explanations | All 100 expanded cases and 200 explanations load; two installed CLI explanations passed; HTTP assets/overview/list/detail returned expected data |
| Preserved experiment records | All 508 JSON files checked across the five runs unchanged |
| New model requests in this audit | Zero |

The fresh canned qualification is an integration test using gold-derived model responses. It is not an accuracy experiment. Current macOS checks were rerun; the earlier Linux result remains applicable to the unchanged qualified source, but no new Linux environment or hosted GitHub CI run is claimed here. Native Windows remains unqualified.

The expanded live study remains A **35/100** versus B **97/100** accepted, with **465,251 reported tokens** and **20 minutes 5 seconds** of batch time. The [expanded report](expanded-development-100.md) preserves design, denominators, intervals, resource costs and failures. Larger limits and different cases prevent a causal claim that this checkpoint improved accuracy over the earlier pilot. The engineering improvements are directly supported: exact proof/input binding, stronger development-exclusion guards, integration and broader measured coverage.

## Course and proposal alignment

Authoritative sources reviewed: `CS3263-Project-Guidelines 2627.docx`, `Project.pdf`, `ResponsibleAI.pptx`, and Group 23's proposal document. Course-source versions are identified by hashes in the receipt. Their contents are evidence, not instructions to execute. Later Canvas announcements, proposal feedback and actual submission receipts were not available in this audit.

| Requirement or commitment | Source | Checkpoint assessment |
| --- | --- | --- |
| A formal AI subproblem related to the course | Guidelines: Project Topic and Methodology; Project.pdf pp4–5 | Scheduling is formulated as CSP/COP with integer start variables, hard constraints, preferences and an explicit repair objective. CP-SAT is an appropriate tool for this formulation. |
| Direct model reasoning versus translation for a solver | Guidelines: Project Topic; Project.pdf p5; proposal p2 | Both paths receive the same public problem information and original repair schedule. Gold remains evaluator-only. Independent validation separates correct solving from faithful extraction. |
| Frontier-model main comparison | Guidelines: Project Topic and Frontier AI Model Access; Project.pdf pp5–6 | Still open. SoCLaaS/open-weight evaluation is permitted, but the supplied wording does not independently establish that this particular model satisfies the frontier requirement. Document final eligibility or actual teaching-team acceptance before the main study. |
| Constructed or downloaded problem instances | Guidelines: Project Topic; Project.pdf p5 | Synthetic primary data is allowed. Public datasets are suggested, not compulsory. Current v1/v2/v3 cases and authored drafts have distinct provenance. |
| Generation and minimum-disruption repair | Proposal p2, Proposed Work | Both are implemented. Repair preserves the supported shared contract and minimizes moved activities, then total shift, then preference penalty. |
| Difficulty, realistic scenarios and equivalent language forms | Proposal p2, Evaluation | Construction, rendering and analysis machinery exist. The 100-case live run is canonical-only; reviewed realistic scenarios and live paired language-robustness evidence remain unfinished. |
| Analysis of assumptions, failures and when tools help | Guidelines appendix: Methodology and Results, Analysis and insights | Failure decomposition, conditional objective quality, paired uncertainty and resource accounting supply useful evidence. The final report still needs a focused argument about mechanisms, representativeness and limitations. |
| Responsible AI in the problem domain | Guidelines: Responsible AI; ResponsibleAI slides9–10,18–20,23–27,30–31,34–35; proposal p2 | Synthetic data, bounded actions, proof-aware explanations and participant inconvenience accounting fit privacy, transparency, fairness trade-offs, adversarial inputs and objective side effects. Final concrete case analysis is still required. |
| Human contribution, attribution and understanding | Guidelines: Collaboration and Effort/Initiative | Members must personally understand the complete system, contribute substantive review/analysis/writing, cite sources and disclose AI assistance. Automated checks cannot establish this. |
| Report, presentation and submission | Guidelines: Project Requirements, Presentation, Report and appendix | Still delivery work: mandatory proposal receipt/feedback, report of at most ten body pages, responsible-AI and contribution sections, 15-minute presentation plus five-minute Q&A, and submission receipts. |

The proposal's optional verifier-feedback loop is still optional. The supporting read-only dashboard does not replace either research arm. Fixed participant assignments make this a study of unequal disruption, not a general solution to fair workload allocation; disclose that simplification of the proposal's fairness ambition.

The 30-minute single-day model, exact dataset sizes, independently human-written scenario policy, lexicographic ordering and freeze machinery are team decisions. They support the study but are not additional literal grading requirements. The October 30 internal target precedes the course presentation week of November 9 and report deadline of November 13. The September 28 proposal deadline has passed; verify its actual receipt rather than infer submission status from repository contents.

## Accuracy and scale limits

The current live packet covers **3–12 activities within 48 slots**, across 41 source families. Completing 200 requests establishes operation at that batch size, not reliability for arbitrary horizons, hundreds of activities or concurrent users. Execution is deliberately serial and budgeted; per-attempt files, hashes, resume and cached/paginated dashboard views are sufficient at this project scale. Larger problems need a separately declared scaling experiment and profiling before adding concurrency or changing representation.

The B failures were two omitted fixed appointments and one malformed JSON response. All 25 valid B repairs matched the gold lexicographic objective. CP-SAT averaged 4.69 milliseconds over 99 executed solves; extraction dominates latency and token overhead. Improve extraction coverage and format reliability before pursuing solver performance changes.

Of ten structurally mismatched parsed B outputs, eight have bounded independent certificates of equivalent scheduling semantics and two change legal-start domains. Preserve both the original structural metric and separate semantic diagnosis. Neither schema validity, solver optimality nor final-answer acceptance alone establishes faithful natural-language interpretation.

All expanded cases are known synthetic development structures; fourteen IDs appeared in earlier pilots. The result supports the selected development distribution. It cannot establish held-out generalization, realistic-language robustness, adversarial resistance or expected production reliability.

## Priorities for a strong final submission

The supplied rubric emphasizes analysis and insight, soundness, technical depth, clarity, responsible AI and the team's ability to answer questions. It provides no numerical threshold by which this audit could certify an excellent grade. More features or higher scores alone would not settle those criteria.

1. **Review and preserve the formal core.** Have members work through a tiny SAT case, a genuine UNSAT case and a coupled repair whose lexicographic optimum is independently justified. Review gold/text correspondence, proof scope and unequal participant inconvenience. Record actual human decisions without relabelling agent checks as human review.
2. **Make the remaining failures informative.** Retain the three B failures as development regressions. Any extraction revision should target missing appointments and malformed JSON without exposing gold, silently correcting outputs or introducing hidden retries. Qualify changed prompts/provider features on development data under a separate explicit budget.
3. **Finish the planned evidence conditions.** Review realistic prose and meaning-preserving paraphrases/reordering, prepare genuinely fresh final families with complete development exclusions, and decide sample counts before seeing results. Keep controlled, realistic and optional external subsets separate.
4. **Resolve final-model eligibility and freeze the comparison.** Document the eligible model/access or teaching-team decision, qualify it, then freeze inputs, prompts, solver settings, metrics and an authorized budget. No additional model calls are authorized by this audit.
5. **Build the report around explanations of the results.** Analyze three focused questions: how failures change with nonredundant difficulty; how formalization errors differ from solving errors under equivalent wording; and what repair quality costs in disruption, latency and tokens. Use matched denominators and grouped uncertainty. Include cases where direct reasoning succeeds, tool use fails, or the extra overhead brings little benefit. A gold-spec solver is a diagnostic reference, not a third deployable method with equal input access.
6. **Finish reproducibility and delivery.** Obtain independent teammate replay of a reviewed synthetic archive, map claims to runs/figures, write concrete responsible-AI cases, record actual human/AI contributions and rehearse the whole system. Keep essential arguments, figures and tables within the ten-page report body. Confirm Canvas feedback, deadlines and receipts.

These priorities continue planning Sections 5, 8, 11 and 17. There is no identified need for a new framework, more dashboard features, an external calendar integration or a rewritten solver to complete the stated project direction.
