# Difficulty pipeline smoke verification

The Qwen3.6 smoke completed all **24 scheduling attempts** across 12 paired input conditions: 16 controlled, four fictional and four additional-wording attempts. Its ten distinct cases cover generation, repair, SAT, UNSAT and all five construction tiers, including 32 activities. Selection was fixed for integration coverage before inference; it is not a representative benchmark sample.

The requested and returned model was `qwen3.6:35b`. One metadata request and two capability completions brought the total to **27 HTTP requests**, with no retries, provider failures, timeouts or unexpected pipeline stops. Two backend fingerprints were recorded under the existing shared-service observation policy; this does not establish a fixed backend.

## Observed outcomes

| Block | Direct LLM accepted | LLM + CP-SAT accepted |
| --- | ---: | ---: |
| Controlled | 3/8 | 8/8 |
| Fictional requests | 1/2 | 2/2 |
| Additional wording | 0/2 | 2/2 |

Accepted means a gold-valid schedule or correct UNSAT, not necessarily an optimal answer. The direct method's eight rejected attempts comprise four gold-invalid schedules, two false UNSAT answers and two invalid JSON outputs. These are measured model failures retained in the denominator; the runner recorded them and continued. Solver-assisted acceptance does not establish globally correct extraction or future reliability.

Execution took **656.04 seconds** before analysis export. The provider reported **118,885 total tokens**: 59,125 input and 59,760 output, with usage present for all 26 completions including capability checks. Configured ceilings remained 32,768 output tokens per completion, 30/1,800-second connect/read timeouts, 30 seconds for the method's solver, 60 seconds for references, and one attempt per request. The output reservation was 851,968 tokens; it is distinct from measured consumption and excludes input tokens.

## Verification performed

- Built and installed the current package noneditably in an isolated Python 3.12 environment, reusing unchanged pinned dependencies. All 44 relevant source/asset files and 30 dependency versions matched; installed-asset and dependency checks passed.
- Ran 28 targeted tests against the installed package, including both complete mocked 200-attempt campaigns, mathematical checks, review packets, failure continuation and interpretation exports. All passed. Nine dashboard frontend tests also passed. This supplements the previously recorded broader suite; it is not a claim of a new full-suite run.
- Replayed all three live blocks with no missing, pending or unscored attempts. Generated paired/stratified/resource tables, figures and a trace-backed casebook.
- Verified all 109 files in the reproduction archive against its checksum manifest, checked archive membership for unsafe paths and credential material, and reproduced the complete analysis identically using its archived source without model calls.
- Checked the installed dashboard's real HTTP routes, static page, overview, case lists and details against running and completed records; final totals were 24/24 across three blocks.
- Visually inspected the generated tier figure. Fixed legend overlap with zero-score labels and axis limits for empty tiers. The corrected PNG/PDF is a separately labelled presentation derivative; original responses, scores, figures and archive remain unchanged. No inference or scoring behavior changed.

The [machine-readable receipt](../results/summary/difficulty-smoke-qwen36-20261013.json) records counts, failure categories, backend observations, tokens and the archive checksum. Full traces, the replay archive, exact run source and corrected figure are preserved in the operator's local `final-smoke-20261013` evidence directory; the raw smoke archive is not included in this repository. Historical Qwen evidence remains separate and unchanged.

The chart-only source correction invalidates older source-bound preparation packets. Fresh packets for both full 200-attempt Qwen campaigns were prepared against the corrected source. Reinstall/reprepare after any further source, runtime or commit changes before execution, as described in the [study guide](difficulty-study.md).

## Readiness boundary

This establishes a working live pipeline within the tested scheduling scope. It does not establish full-study performance, monotone difficulty, larger-scale production reliability, human review or course submission. The complete 200-attempt run for each model, representative failure interpretation and the delivery tasks in `planning.md` remain pending. The smoke allowance is consumed; it is not authorization for those full runs.
