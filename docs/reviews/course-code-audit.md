# Course, TA feedback and implementation audit

Audit date: 15 October 2026. Target: the local `publication-worktree` on `final-study-preparation`, based on commit `2fcd43295c121f6f28a8463bc303c3ec84fad5fa` with the existing uncommitted study/report changes. GitHub `main` was read directly and has that same commit; the new local work is not yet published. No live model inference, commit or push was performed by this audit.

**Conclusion:** the implemented comparison fits the course's CSP/COP direction and the proposal, and the generation-first scope responds to the TA's feasibility concern. The engineering pipeline is working. A material dataset-design limitation was found and disclosed below. Submission readiness also still depends on actual member analysis/contributions, scope/model clarification and delivery. Automated code checks cannot establish those facts or guarantee a grade.

**Checkpoint status:** the recommended D5 follow-up was subsequently implemented and both [balanced campaigns](../studies/balanced-comparison-audit.md) completed. The separately authorized [diverse study](../studies/diverse-comparison-audit.md) is now the primary report evidence. The findings, next-step recommendations, source equality and test counts below describe this earlier checkpoint; they are not current unfinished tasks. Original runs and their limitations remain unchanged. See the [latest repository audit](../process/repository-audit.md) and [submission checklist](../process/submission-checklist.md) for current verification and remaining work.

## Sources checked directly

- *Project.pdf*, pages 4–7: course-related simplified problem, constructed/downloaded instances, direct versus translation-to-tool comparison, tool limitations, frontier/open-weight model wording and responsible AI. Page 8 supplies dates.
- *CS3263-Project-Guidelines 2627.docx*: P25/P33/P35/P37/P41/P43/P47/P49/P51/P56–60/P62/P68/P70–99. Paragraph locators count the original Word XML paragraphs, including empty paragraphs. P25 explicitly permits constructed instances; P68 encourages public sources without making an external benchmark mandatory. P84 emphasizes analysis of assumptions, failure modes and realism. P88 explicitly penalizes missing or poorly stated contributions.
- The supplied Group 23 proposal: generation, minimum-disruption repair, direct and LLM-to-OR-Tools methods, gold validation, controlled/fictional/wording evaluation and responsible AI. Its fallback permits generation with both methods and validation; feedback correction and UI are stretch goals. Actual work division may differ under Guidelines P56.
- *ResponsibleAI.pptx*: privacy/reidentification (slides 9–13), fairness trade-offs (16–20), transparency/explanation (23–27), adversarial inputs (30–31), objective misspecification and monitoring (34–35), and human control/misuse (2–6). The report applies relevant ideas to scheduling; implementing every technique in the slides is not required.
- All feedback provided to the team: the consultation notes about feasibility, varied cases, failure analysis and strong-model ceilings; the rubric image whose selected ratings were not evident; and the later written feedback praising course fit/evaluation/responsible AI while asking for generation as core, repair minor, feedback/UI bonus and a small office scenario.

The written feedback clarifies the earlier ambiguous image. The alternatives “Good”, “Okay”, “Likely” and “Unlikely” are not independently treated as selected assessments. Private course documents, student identifiers and Canvas records remain outside public Git. The audit reads supplied materials; it does not claim to have checked current private Canvas announcements.

## Material finding: a feasibility-label shortcut in the generated data

The actual controlled case bundles inside **both** completed archives give this coverage for the 30 generation cases:

| Gold label | Cases | With explicit deadline | With fixed start | With either |
| --- | ---: | ---: | ---: | ---: |
| SAT | 15 | 0 | 0 | 0 |
| UNSAT | 15 | 10 | 5 | 15 |

The [coverage receipt](../../results/summary/generation-constraint-coverage-20261015.json) records every case ID, constraint-type set, bundle hash and original archive hash. The cause is visible in [the generator](../../src/scheduling/evaluation/difficulty_suite.py): `_jobshop` uses a block for SAT updates and deadline contradictions for UNSAT; `_cycle` adds the retained fixed appointment only for UNSAT. The same construction pattern occurs in the 30 controlled repair cases and the 20 fictional cases. Wording variants inherit their underlying cases.

This is a **construction confound**, not explicit evaluator-label leakage, and it does not prove a model used a shortcut. It does not invalidate the recorded validation or the concrete extraction counterexamples. However, presence of those constraint types perfectly separates feasibility labels, and the live benchmark does not test feasible deadline/appointment handling. Correct UNSAT classification and stronger-model ceilings therefore cannot be interpreted as broad scheduling competence. The new office cases exercise feasible deadlines/appointments only through local solver/validator checks.

**Action taken:** disclose the limitation in the report, README, contributor notes and TA alignment, and added it to the project plan (D5). No original dataset, output, score or model prompt changed. The previous generation-focused report/PDF/figures/format receipt are preserved in [report history](../history/20261015-generation-focus/submission-report.md).

**Recommended focused next step:** a small separately versioned generation confirmation with matched loose/tight SAT/UNSAT families and counterbalanced deadline/fixed-start presence. Include SAT cases with these constraints and UNSAT cases without them; independently certify the labels and review public wording/calendar frames. Keep the existing two methods, comparable settings and failure-inclusive scoring. This would strengthen the evidence without adding models, harder tiers, repair breadth or feedback loops. Define a small cap before preparing it; live execution needs explicit authorization. Alternatively, the current exploratory report must retain its narrower, openly limited interpretation. This is a scientific judgment under planning D5/S3, not a course-imposed minimum sample count.

## Requirement-to-implementation checks

| Expectation | Code/evidence inspected | Assessment |
| --- | --- | --- |
| Course-related formal subproblem | [schema](../../src/scheduling/schema.py), [domain analysis](../../src/scheduling/domain_analysis.py), [solver](../../src/scheduling/solver.py), report Section 3 | Implemented CSP/COP: mandatory integer start variables, finite domains, fixed durations, shared-resource constraints and explicit objective |
| Fixed appointments, availability, non-overlap and deadlines | Solver/domain restrictions plus independently implemented [validator](../../src/scheduling/validation.py); formal tests and [office examples](../../evaluation/ta_scope_examples.py) | Implemented and checked offline. Live constraint coverage is limited by the finding above |
| Direct versus translation-to-tool | [direct pipeline](../../src/scheduling/pipelines/direct.py), [extraction pipeline](../../src/scheduling/pipelines/solver_augmented.py), [runner](../../src/scheduling/evaluation/runner.py) | One call per method, equivalent public task facts, neutral extraction ID, no gold feedback or silent answer correction |
| Correct solver/proof distinctions | `solver.py`, [scoring](../../src/scheduling/evaluation/scoring.py), [formal tests](../../tests/unit/test_formal_qualification.py) | `UNKNOWN` is not UNSAT; feasible is not optimal. Reference witnesses checked independently; the shared reference compiler remains disclosed |
| Generation core and feasible scope | Planning D4–D5, report Sections 1/5/6, [generation summary](../../results/summary/generation-focus-20261015.json) | All 30 generation cases lead; 12 small cases are a post-run size-defined subset, not extra or held-out data. No generic feature expansion is necessary |
| Repair as extension | `RepairCase`, original-schedule validation, solver stages and independent objectives | Implemented lexicographic moved count, total absolute start shift, then preferences. Later gaps require earlier objective ties. Unrelated activities cannot always be kept fixed |
| Loose/tight SAT/UNSAT and realistic scenarios | [difficulty suite](../../src/scheduling/evaluation/difficulty_suite.py), frozen cases, independent certificates, office examples | Mathematical cases exist and labels are checked; realistic cases are synthetic templates. The live coverage confound and pending human meaning review remain material limits |
| Wording robustness | Archive case/rendering pairing, [interpretation](../../src/scheduling/evaluation/interpretation.py), current failure catalogue | Matched counterparts and concrete omissions are analysed. Ten clock paraphrases per model omit the date, limiting calendar-frame comparison; relative-slot validity is separate |
| Metrics beyond success | Scoring, [metrics](../../src/scheduling/evaluation/metrics.py), [study analysis](../../src/scheduling/evaluation/study.py), archived analysis | Failure-inclusive acceptance, SAT/UNSAT, conditional objective quality, extraction diagnostics, grouped paired comparisons, model/solver time and usage coverage |
| Strong-model near-ceiling analysis | Original Qwen3.8 results, current GLM traces and report Sections 5–7 | Harder cases, service failures, optimization and extraction are distinguished. No unsupported claim that scale alone or model weights caused the difference |
| Responsible AI | Validator and explanation tests, participant burden/objective examples, report Section 7 | Concrete privacy, unequal inconvenience, hard-constraint control, transparency and adversarial-text limitations. Formal validity is not fairness or deployed robustness |
| Report and presentation | Report source/PDF, format checker, [checklist](../process/submission-checklist.md), presentation guides | Report format verified; actual member contributions, final private copy, deck/rehearsal and upload remain open |

The validator imports schema and standard-library utilities, not CP-SAT or the compiler/domain/objective helper implementations. The two pipelines are joined by the shared runner and evaluator, rather than separate incompatible member implementations. The current runtime/prompt bytes match the frozen scientific source used by both completed difficulty runs.

## Exact TA-scenario boundary

The suggested week of hourly slots is **not** the implemented contract: schema v1 permits one day, 30-minute slots and at most 48 slots. The four new office examples use eight 1–2-hour activities, two participants and one room from 09:00–17:00 on Monday. They make no LLM calls and are not part of the model-performance denominators. Preferred-start penalties support a morning-start preference; consecutive-meeting penalties and day clustering are absent. These are explicit simplifications to confirm with the teaching team if the exact suggested scenario is expected. Do not call every TA suggestion completed.

Repair is a finished extension. Verifier-feedback correction is deferred and absent from the measured methods. The existing dashboard is a bonus read-only evidence viewer. A third model, external dataset, weekly calendar, new UI or probabilistic graphical model is not automatically needed to satisfy the central course formulation/comparison requirement.

## Verification executed in this audit

- **853 Python tests covered:** the full current-source run produced 852 passes and one native macOS trust-store failure (`OSStatus -26276`) under sandbox restrictions. The entire eight-test TLS module then passed outside the sandbox using local socket pairs, including that case. This is not a claim of a single uninterrupted 853-pass run; TLS verification was not weakened.
- **Nine dashboard tests and JavaScript syntax** passed.
- **Fresh end-to-end offline demo:** 180/180 canned attempts completed, idempotent resume and replay agreed, 174 accepted and six deliberately invalid, no pending requests, zero live model calls. This is wiring/failure-handling evidence, not additional model performance.
- **Independent formal probe:** 80 deterministic three-activity specifications, each tested for generation and repair; 160 CP-SAT results matched separate full Cartesian enumeration and independent validation (24 SAT, 136 UNSAT), seed 326315. The exact script/output/source-hash receipt are retained in the private audit workspace. Small-case agreement is not a proof of every larger instance.
- **Four original archives verified:** two difficulty archives each have 364 checked inner files; two historical Qwen archives each have 941. Outer hashes and exact memberships match. The preserved full replay receipts remain valid; no new live run was performed.
- **Current/frozen compatibility:** all 47 runtime-source/prompt files in each difficulty archive match the current checkout byte-for-byte. Installed prompts, dashboard assets and issuer certificate match current source; dependency consistency passes.
- **Model identity and results:** 191 successful GLM scheduling responses report `glm-5.3-flash`, with nine HTTP 502 failures; 194 successful Qwen responses report `qwen3.6:35b`, with six provider failures. Generation counts independently match 11/30 versus 28/30 and 25/30 versus 30/30. Failures remain in denominators.
- **Report:** rebuilt after adding the confound, twelve pages total and ten body pages, at least 11-point text, one-inch margins; all 99 visible source chunks, four formulas and four chart images verified. Visual review and the final preservation check are recorded in the publication-verification log.

This audit runs against current local source on macOS ARM64. It does not claim a fresh Ubuntu CI pass or native Windows support. The existing CI matrix targets macOS/Ubuntu; native Windows remains unqualified. The GitHub SHA check is read-only and does not publish uncommitted work.

## What remains before submission

1. **Scientific interpretation:** address D5 explicitly and review actual public-input/gold pairs, extraction failures, optimality and provider confounding. Record members' own reasoning; an automated audit cannot supply their contribution.
2. **Scope/model clarification:** confirm the exact single-day/soft-preference simplification and the teaching team's frontier-model interpretation for the hosted models. The supplied sources mention SoCLaaS but do not conclusively settle this question.
3. **Contributions and AI disclosure:** replace the interim paragraph with factual per-member work and AI support. This is a substantive graded requirement, not just an administrative signature.
4. **Delivery:** prepare the private title-page details, final reviewed report, actual presentation/recording and timed Q&A rehearsal, then follow current Canvas arrangements and retain upload receipts. Supplied dates are presentation week of 9 November and report due 13 November; 30 October is an internal draft target.
5. **Publication/handoff:** publish the reviewed local changes only when authorized; optional independent teammate reproduction and off-device evidence storage remain sensible team practices, not extra rubric requirements.

No new runtime defect was established in the inspected formal/evaluation code. The main newly identified weakness concerns experimental construction and the strength of conclusions that can be drawn from it. Preserve the successful implementation and focus further effort on that issue and human analysis, rather than broadening the project.
