# Report claim-to-evidence index

## Final report additions (9 November 2026)

| Claim | Source |
| --- | --- |
| Search-space sizes: log10 of the unary-domain product, median 4.6 (8 activities), 25.4 (32), maximum 38.1 | `scripts/search_space_summary.py`, [saved output](../results/summary/search-space-20261109.json) |
| Qwen3.6 direct says "no solution" for 291/500 feasible (58%) and 307/500 infeasible (61%) cases; 307/598 correct | [Summary](../results/summary/diverse-comparison-20261018.json) `overall_by_method.direct`: `correct_unsat`, `categories.false_unsat` |
| Given gold specifications the compiler labels all 1,000 cases correctly; wrong solver-assisted answers are 20 Qwen3.6 / 4 GLM5.3 Flash (false UNSAT + invalid schedules) | Reference agreement in the [audit](studies/diverse-comparison-audit.md); summary `categories` |
| GLM5.3 Flash direct infrastructure failures 0/0/4/21/40 by size; 43 of 65 in fragmented packing, fork-join and precedence chain | Summary `by_size`, `by_mechanism` |
| Repair optimality: valid solver-assisted repairs 14/14 (Qwen3.6) and 15/15 (GLM5.3 Flash), GLM5.3 Flash direct 15/15, Qwen3.6 direct 0/2 | [Difficulty summary](../results/summary/difficulty-comparison-20261014.json) `controlled_task_labels`, task repair, `objective_matches` |
| Fictional requests: Qwen3.6 5→18/20, GLM5.3 Flash 18→20/20 | Difficulty summary `accepted_by_block` |
| 24 cases manually reviewed with no mismatches | Team report; [worksheet status](process/human-review-checklist.md) |

## Current diverse generation study

The revised report leads with the **completed 4,000-attempt comparison**. Earlier sections below remain evidence indexes for their named studies, not the latest primary result.

| Claim | Source and interpretation |
| --- | --- |
| 2,000 unique completed attempts/model; no retry or model mismatch | [Portable manifest](../results/diverse-evidence-manifest.json), immutable attempt records and [audit](studies/diverse-comparison-audit.md); all 4,000 evaluations replay exactly |
| Qwen A/B 308/953; GLM A/B 891/988, each /1,000 | [Derived summary](../results/summary/diverse-comparison-20261018.json), `overall_by_method`; failures retained |
| Feasibility, conditional optimum, extraction and concrete failure cases | Audit scientific sections; summary `failure_catalogue` links original record hashes and evaluator references |
| 51 Qwen and 68 GLM infrastructure failures | Audit provider table; failures are HTTP/transport/read-timeout observations, not model reasoning verdicts |
| Size/interaction behavior | Summary `by_size` and `by_mechanism`; 200 cases/size, 100/mechanism, ten related families |
| Timing differences and usage coverage | Summary `execution_segments`; no matched cross-model concurrency/OS subset; sleep-overlapping timeout records preserved |
| Graphs reproduce exact counts | [Current report figure receipt](figures/report-polished-20261018/figure-data.json) binds summary, renderer and plotted values |
| Worked timetable and descriptive failure examples | [Example trace index](report-details.md#example-trace-index) links readable example labels to exact saved case identifiers; timetable uses both recorded B schedules |
| Mean, median and p95 resource statistics | [Source-bound derivative](../results/summary/report-details-20261018.json), [definitions and phase breakdowns](report-details.md); missing usage is unknown, timing descriptive |
| Report format | [Current format receipt](../results/summary/submission-report-format.json); visual review recorded in publication verification |



The following balanced and difficulty indexes preserve earlier studies and shared-system evidence. They do not supply the latest primary denominators. Human review requirements are tracked in the [submission checklist](process/submission-checklist.md).

## Earlier balanced generation claims

Use the [balanced manifest](../results/balanced-evidence-manifest.json), [summary](../results/summary/balanced-comparison-20261017.json) and [audit with exact trace locators](studies/balanced-comparison-audit.md). The builder validates controls against original records; fresh archive-source analysis reproduces both saved analyses exactly. Figure receipts bind plotted values and exported files to this summary.

| ID / report section | Claim | Evidence and boundary |
| --- | --- | --- |
| B1 / 5 | 48 cases, 24 SAT/24 UNSAT, four balanced profiles, three construction families | [Fixture manifest](../benchmarks/fixtures/balanced-generation-v1/manifest.json), [independent proofs](../benchmarks/fixtures/balanced-generation-v1/proofs.json), [construction checks](../results/summary/balanced-generation-verification-20261015.json); finite constructed cases, actual human review pending |
| B2 / 5 | Matched source/runtime/settings, all 96 paired prompts/public views; no retries | Summary `comparison_checks`; archived manifests and completed records; capability/metadata requests are outside scoring |
| B3 / 6 | Qwen A/B 6/48 vs 48/48; GLM 47/48 vs 48/48, SAT/UNSAT breakdown | Summary `models.*.overall_by_method`; original `analysis.json.rows`; all failures retained |
| B4 / 6 | Qwen 23 invalid schedules, nine false UNSAT, ten format failures; GLM one transport failure | Summary `failure_catalogue` and exact record paths in balanced audit; format and transport rejection are not automatically reasoning failures |
| B5 / 6 | Conditional optimum matching: Qwen A 0/1, GLM A 22/23, B 24/24 each | Summary objective counts, archived reference objectives and two concrete suboptimal cases in audit; only valid gold-SAT schedules with proven references enter these fractions |
| B6 / 6 | Time, tokens, coverage and observed backend variation | Summary `resources`, `backend_coverage`; GLM A tokens 47/48, missing not zero; shared-service timing does not isolate model capability |
| B7 / 6 | Clear acceptance and failure graphs | [Report figure data](figures/balanced-comparison-20261017/figure-data.json), [standalone figure data](../results/figures/balanced-comparison-20261017/figure-data.json), deterministic render script; exact counts and denominators retained |
| B8 / 8 | Two balanced archives, 211 checksummed files each, exact replay and preserved originals | Balanced manifest, [evidence guide](evidence.md), [publication checks](process/publication-verification.md); no new inference, no inferred human review or teaching approval |

## Earlier difficulty comparison and shared system claims

The following IDs preserve the preceding study's traceability. They apply to its separate extension results or shared implementation; they must not replace balanced-study denominators.

Use the [difficulty manifest](../results/difficulty-evidence-manifest.json) to verify/extract each original archive. Archive-relative paths below refer to that extraction. The [comparison summary](../results/summary/difficulty-comparison-20261014.json) is rebuilt by `scripts/build_difficulty_comparison.py`; [the audit](studies/difficulty-comparison-audit.md) supplies concrete trace paths and interpretation. [Evidence instructions](evidence.md) describe exact-source replay.

| ID / report section | Claim | Evidence and boundary |
| --- | --- | --- |
| R1 / 3 | CSP domains, non-overlap and lexicographic repair | `src/scheduling/solver.py`, `schema.py`, `validation.py`; [formal regressions](../tests/unit/test_formal_qualification.py); shared reference compiler disclosed |
| R2 / 3 | Eight-activity office illustration: loose/tight SAT, capacity UNSAT and one-move repair | [Executable examples](../evaluation/ta_scope_examples.py), [checked output](../results/summary/ta-scope-examples-20261015.json), [independent tests](../tests/integration/test_ta_scope_examples.py); offline illustration, zero model calls. Original coupled-repair regression remains separate |
| R3 / 4 | Gold boundary, independent validator and explanation binding | [validator](../src/scheduling/validation.py), [explanation tests](../tests/unit/test_explanations.py); proof applies only to its exact specification |
| R4 / 5 | Identical source/runtime/settings and 200 paired prompt hashes | Summary `comparison_checks`; archive `analysis.json.settings`, block manifests and attempt payloads; full frozen source hash map |
| R5 / 5 | 80 cases, 100 conditions, 40 generated / 39 normalized families | Archive rows and case bundles; `group_id` normalization merges one controlled pair; 29 controlled groups per task |
| R6 / 6 | Full-study extension block counts, failures retained | Summary `models.*.accepted_by_block`; [standalone figure receipt](../results/figures/difficulty-comparison-20261014/figure-data.json) and [report figure receipt](figures/difficulty-comparison-20261014/figure-data.json) |
| R7 / 6 | Controlled SAT validity / correct UNSAT | Summary `models.*.controlled_task_labels`; denominators 15 per task/label/method |
| R8 / 6 | Paired acceptance intervals | Summary `models.*.controlled_paired`; original grouped bootstrap: 30 pairs, 29 normalized groups per task; 10,000 resamples, seed 3263 |
| R9 / 6 | Generation tier counts and nonmonotonic difficulty | [Generation summary](../results/summary/generation-focus-20261015.json) `models.*.generation_tiers`; six attempts per bar, with size and interactions changing together; original twelve-count combined tiers remain in the full summary |
| R10 / 6 | Conditional objective matching and suboptimal direct cases | Summary `overall_by_method`, `failure_catalogue[].objective_status/objective_gaps`; null later lexicographic gaps do not exclude proven earlier gaps |
| R11 / 6 | Qwen availability/block confusion; GLM precedence omissions | Full trace paths, case IDs and concrete violations in audit's failure section; archive payloads preserve public wording, extraction and validation |
| R12 / 6 | Failure categories and bounded extraction checks | Summary `overall_by_method`, failure catalogue; archive `analysis.json.interpretation` and extraction diagnostics; structural differences are not semantic-error counts |
| R13 / 6 | Wording/canonical comparisons and omitted dates | Matched case IDs/renderings in archive rows; public clock paraphrases omit calendar date, limiting frame checks; canonical GLM B counterparts accepted |
| R14 / 6 | Core-generation resources, missing usage and provider errors | Generation summary `models.*.scopes.generation_core.approaches.*.resources`; full-study summary `models.*.resources`; [execution receipt](../results/summary/difficulty-run-validation-20261014.json); timing includes errors, token means cover reported usage only |
| R15 / 7 | Historical concentration of participant burden | [Original discussion](history/development-notes/lihao-development-followup.md#four-responsible-ai-cases-for-team-discussion), preserved private baseline evidence; no fairer-solution proof |
| R16 / 7 | Moved-count priority may increase total shift | `test_movement_priority_beats_smaller_total_shift` in formal qualification; declared priority, not universal desirability |
| R17 / 7 | Fixed compiler and prompt boundary | [Direct tests](../tests/unit/test_direct.py); no empirical live adversarial-robustness claim |
| R18 / 8 | 364 hashes and exact 200-attempt replay per archive | Difficulty manifest, `scripts/verify_evidence.py`, archive checksums, execution/replay receipt and [verification log](process/publication-verification.md) |
| R19 / 5, 8 | Earlier results and stopped run preserved separately | [Evidence guide](evidence.md), original historical archives/manifest, preserved old report, private original run/preservation ledger |
| R20 / throughout | Course fit, sources, actual contribution limits | [Submission checklist](process/submission-checklist.md), original course documents, report references and [contributions](contributions.md); group-confirmed work allocation, disclosed Codex/Claude Code assistance and remaining case-level review |
| R21 / 5-6 | Generation-first post-run view, 30 full / 12 small cases and preserved extensions | [Generation summary](../results/summary/generation-focus-20261015.json), [builder](../scripts/build_generation_focus.py), [report chart receipt](figures/generation-focus-20261015/figure-data.json); exact observation IDs, original archive hashes, no new inference or preregistration claim |
| R22 / 1, 3, 5 | TA scope response and unsupported weekly/preference features | [Alignment](ta-feedback-alignment.md), user-supplied written feedback, `schema.py`; single-day/30-minute simplification remains an explicit course-scope clarification |
| R23 / 7 | Deadline/fixed-start presence separates all 30 generation labels | [Coverage audit](../results/summary/generation-constraint-coverage-20261015.json), archived controlled case bundles and `difficulty_suite.py` label-dependent branches; possible shortcut, no claim of observed model exploitation |
| R24 / 5–7 | Separate 48-case correction now completed and reported as B1–B8 | [Balanced protocol](studies/balanced-generation.md), [`balanced-generation-v1` manifest](../benchmarks/fixtures/balanced-generation-v1/manifest.json), independent certificates, source-bound packets, offline integration checks and the balanced manifest; 24 SAT/24 UNSAT across four matched profiles, three conservative families |

A member checks model/block/task/label/rendering, denominator and archive identity, inspects the actual case where a mechanism is claimed, and records their own findings or corrections. Review the date-omitting paraphrases as an input limitation. Do not modify executed fixtures, failures or scores to improve the narrative. Any future scientific correction needs a separately versioned analysis or study.
