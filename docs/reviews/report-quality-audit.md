# Report scientific-quality and course-requirement review

> Historical review of the 18 October report. Section and table numbers below refer to that version; the 9 November final revision is recorded in the [publication log](../process/publication-verification.md).

Reviewed 18 October 2026 against the supplied Project brief, CS3263 Project Guidelines AY2026/27, Responsible AI slides, original proposal, consultation notes and written TA feedback. The [report source](../submission-report.md), every table row, formula, caption and reference were reviewed against implementation and saved evidence. The [verification receipt](../../results/summary/report-scientific-review-20261018.json) binds the reviewed source and PDF; later edits require renewed checks. This review does not replace member contributions, independent interpretation or teaching-team approval.

The walkthrough below records the source version bound by the original review receipt. Subsequent model-selection and contribution confirmations, together with remaining evidence-review tasks, are tracked in the [submission checklist](../process/submission-checklist.md). The current [format receipt](../../results/summary/submission-report-format.json) identifies the latest report source and PDF.

## Report walkthrough

Line ranges refer to this reviewed Markdown version; PDF page numbers include the cover.

| Source lines / unit | Review and disposition |
| --- | --- |
| 1–15: cover | Course, semester, title and members agree with supplied materials. Public copy omits identifiers; local private copy contains them. Members must confirm their details. |
| 17–19: abstract | Question, two approaches, 1,000-case design, four headline scores and qualified conclusion match evidence. No claim of real-world reliability or new solver algorithm. |
| 21–27: motivation, domain, contribution | Scheduling assistant fits the course theme; fixed assignments and single-day scope are explicit. Generation is central and repair is an extension. Contribution is the inspectable comparison, not invention of CP-SAT. |
| 29–33: related work | Motivation and distinctions are supported by the cited primary sources. External benchmark scores are not presented as predictions for this study. |
| 35–45: mathematical formulation | Integer starts, durations, finite domains, half-open intervals, precedence, shared capacity and weighted preferences agree with schema/solver/validator semantics. Hard feasibility and soft cost are distinct. |
| 47: solver rationale | Product-of-domains search space motivates formal reasoning without claiming all constructed cases are computationally difficult. |
| 49–55: repair | Lexicographic moved-count/shift/preference objective and optimality-bound stages agree with implementation; budget exhaustion is not infeasibility. Main study remains generation only. |
| 57–71: architecture | Diagram preserves the public-input/gold boundary and separates direct generation, extraction, fixed compilation, validation and reference scoring. |
| 73–77: implementation and controls | JSON contracts, one call per method, no silent repair or feedback, and arithmetic validator independence are described. Shared reference compiler and whole-pipeline comparison are disclosed. |
| 79–96: worked example and Table 1 | All four saved outputs support the explanation. The timetable refutes Qwen's UNSAT prediction; GLM double-books the room and violates availability. Both B extractions match gold and achieve penalty 6; the lower bound is explained. Selected example is not a frequency estimate. |
| 98–104: dataset design | 1,000 cases, ten families, five sizes, 500 matched pairs and 500 topology signatures agree with evidence. Small-case view, schema limits and unexecuted optional variants are explicit. |
| 106: gold construction | Witness/certificate counts and reference statuses agree. Synthetic development provenance, missing human meaning review and evaluator-only information are distinguished. |
| 108–112: protocol and metrics | Model IDs, settings, 4,000 calls, failure-inclusive denominators, one sample per condition and ten-family dependence agree. Hidden server settings and execution confounding are disclosed. |
| 114–127: primary results, Figure 1 and Table 2 | All scores and SAT/UNSAT/conditional-optimum counts match saved analysis. Clarified that bootstrap ranges are central 95% ranges; design-sensitivity qualification remains. |
| 129–137: mechanisms | Constructive scheduling differs from infeasibility prediction; format rejection is not automatically a mathematical error. Both extraction counterexamples and structural-match counts match traces. |
| 139–141: Figure 2 and sensitivity | Infrastructure categories remain separate. Response-intersection denominators and the 3.85-point GLM gap match evidence; secondary analysis is not called corrected accuracy. |
| 143–145: scale and optimization | Size-stratum counts, infrastructure contribution and conditional optima agree. Case size is not an isolated causal intervention; a 1/1 optimum result is not general optimization evidence. |
| 147–160: Table 3 | Every mean/median/p95 and reported-usage count matches the resource derivative. Missing usage is unknown rather than zero; p95 definition is stated. |
| 162–175: Table 4 and timing | Pipeline/solver measurements and invocation counts agree; timings include failures. No intrinsic speed ranking is inferred from mixed service/concurrency/OS conditions. |
| 177–181: practical interpretation | Added explicit solver/schema-availability discussion. Supported representation and unsupported travel/weekly/fairness preferences are distinguished. No unperformed alternative comparison is claimed. |
| 183–185: validity | Related synthetic families, label-shortcut limits, single samples, untested new wording conditions, shared compiler and missing human review remain explicit. Model eligibility is unresolved, not inferred. |
| 187–189: responsible AI | Privacy, objective fairness, human control and adversarial-input risks are domain-specific. Clarified that solver conclusions concern the extracted specification; they do not certify extraction fidelity. |
| 191–197: reproduction and conclusion | Added a versioned code/evidence reference so the PDF provides a direct route to reproduction. Conclusion follows measured evidence. Per-member contributions remain an explicit unresolved requirement. |
| 199–207: references | Primary-source titles/authors/venues and links checked. New repository reference pins an existing published code/evidence version; each experiment retains its original source identity. |

## Course criteria and TA feedback

| Requirement / criterion | Coverage and remaining action |
| --- | --- |
| Guidelines P25/P62/P81: course-related formal problem and direct-versus-tool comparison | Sections 1, 3–6 cover CSP/COP, both pipelines, evaluation and limitations. |
| P62/P70–84: motivation, technical depth, achievement, methodology, analysis and insights | Report links formal structure to observed outcomes, separates failure mechanisms, examines conditional quality/resources and discusses constructed-data assumptions. Novelty and difficulty are bounded rather than exaggerated. |
| P25/P84: practical conditions, tool limits and realistic assumptions | Section 8 discusses solver/schema availability, unsupported requirements, template dependence, uncertainty and validation. Artificial construction is explicit. |
| P34–35/P74: responsible AI | Section 8 applies privacy, fairness, transparency, oversight and misuse concerns to scheduling, with concrete objective trade-offs. |
| P49/P53/P90–93: technical audience, concise academic report, format | End-to-end scientific structure and a worked example are present. Both PDFs pass ten body pages, single column, at least 11-point text and one-inch margins. All discussions/figures/tables remain in the body; references and title are separate. |
| P58–59/P82: sources and prior work | Related work and numbered references support borrowed concepts; evidence reference enables inspection. Claims are not copied from external benchmark outcomes. |
| P51: private names, student IDs and emails | Prepared in the ignored private copy; actual member confirmation and correct final upload remain. |
| P56–60/P87–88: division of labour, understanding and honest AI use | **Not complete.** Interim disclosure is honest but does not replace factual per-member contributions. Each member must supply their own work, decisions, interpretation and AI assistance, and understand the entire project. The guidelines explicitly warn of deductions for missing/poor contribution statements. |
| TA: feasibility, generation core, repair minor, feedback/UI bonus | Current report keeps generation central, describes completed repair as an extension and does not claim feedback correction. Larger study is a completed bounded team choice, not a TA requirement. |
| TA: varied cases, small first, failure analysis, strong-model ceilings | Earlier small benchmark motivates the separate diverse study. Main results analyse mechanisms, size, failures, extraction and resources rather than only aggregate success. Historical fictional/wording evidence remains separate. |
| TA: suggested weekly/hourly office scenario and soft preferences | **Clarification remains.** Implemented single-day/30-minute scope and preferred-start penalties differ from weekly/hourly, consecutive-meeting and day-clustering suggestions. Report discloses these differences. |
| P25/P27/P33: hosted models and frontier-model wording | **Resolved by subsequent feedback.** The team reports TA acceptance of Qwen and GLM; see the submission checklist. |
| P47/P51/P57: presentation, understanding and delivery | **Human tasks remain.** Complete actual review/contributions, confirm Canvas instructions, prepare/rehearse the presentation or requested recording, verify the final private PDF and retain submission receipts. |

## Changes and verification

Only report wording/references and review records changed: clarified central 95% bootstrap coverage, practical solver availability and extracted-specification guarantees, and added the versioned evidence citation. No statistical values, figures, experiment inputs, traces, scientific runtime or scoring were changed. No inference was requested.

An independent read-only numerical review checked claims against the saved resource/comparison JSON, archived analyses and relevant traces. Format checks passed for both PDFs; all pages were reviewed visually, with identical private/public body and reference pages. The verification receipt records archive preservation and the reviewed source/PDF hashes. The submission checklist tracks the remaining member review and delivery tasks.
