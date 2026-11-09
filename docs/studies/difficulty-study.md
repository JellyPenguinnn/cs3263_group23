# Easy-to-extreme scheduling study

The **200-scheduling-attempt campaigns for Qwen3.6 and GLM5.3 Flash are complete**. Their [comparison audit](difficulty-comparison-audit.md), replay archives, graphs and updated report are available. The earlier 600-attempt Qwen studies and original report are preserved separately. The [24-attempt smoke](../history/development-notes/difficulty-smoke-verification.md) remains an integration checkpoint, not part of the full comparison. Tier names describe construction targets; the measured results are not monotone with size.

The written TA follow-up makes **controlled generation the reporting core**, with repair a completed bounded extension. [The alignment](../ta-feedback-alignment.md) records that study’s 30-case generation core, twelve-case small view and separate office illustration. The primary report now leads with the separately completed [diverse generation study](diverse-generation.md). The executed 200-attempt protocol below is preserved unchanged; it is not an instruction to run more experiments.

## Design and counts

| Tier | Activities per case | Controlled conditions | Fictional conditions | Additional wording conditions | Calls with both methods |
| --- | ---: | ---: | ---: | ---: | ---: |
| Easy | 4 | 12 | 4 | 4 | 40 |
| Moderate | 8 | 12 | 4 | 4 | 40 |
| Hard | 12 | 12 | 4 | 4 | 40 |
| Very hard | 20 | 12 | 4 | 4 | 40 |
| Extreme | 32 | 12 | 4 | 4 | 40 |
| Total | — | 60 | 20 | 20 | 200 |

There are **80 unique cases from 40 construction families**. Generation and repair share the updated hard problem within a family; repair also receives its valid original schedule. The wording block adds two renderings of each of ten selected controlled cases. Thus 100 conditions are not 100 independent problems. The completed Qwen3.6/GLM pair contains **400 scheduling attempts**. Structural normalization leaves 39 distinct groups from the 40 generated families (29 controlled plus ten fictional). Each model additionally performs two capability checks and one metadata request.

The controlled block has three mechanisms at every tier, each with SAT/UNSAT and generation/repair cases:

- **Resource bottleneck:** multiple jobs compete for capacity-one equipment and participants. Impossible cases require more resource time before a shared deadline than exists, while every activity still fits individually.
- **Precedence/deadline interaction:** job chains, cross-job dependencies and resource competition interact. A critical-path duration certificate proves the impossible cases.
- **Coupled repair:** a displaced booking propagates around a cycle of alternative starts. SAT repair moves all activities; the UNSAT version has fewer eligible unit slots than activities. Increasing cycle size probes dependency tracking, not an asserted exponential lower bound.

Job schedules include durations of one to three slots, competing preferences and calendar breaks at higher tiers. IDs are shuffled relative to construction order. Preferences do not reveal the job-schedule witness. The single-day/30-minute-slot schema and fixed assignments are unchanged. Size and interaction structure change together, so this design does not isolate a causal effect of activity count.

Fictional cases describe equipment sharing, event preparation or studio bookings using complete clock-time instructions. They are deterministic AI-assisted templates, not real calendar data or independently human-authored scenarios. They were outside the team's 24-case manual review, which covered the main study. The clock-time paraphrase also tests time-to-slot interpretation; the reordered variant preserves the original slot-based wording while shuffling facts. Analyse those two transformations separately.

Canonical blocks are balanced by tier/task/SAT label. Wording selection has five generation and five repair bases, five SAT and five UNSAT bases. Joint counts are generation-SAT 3, generation-UNSAT 2, repair-SAT 2, repair-UNSAT 3; each has two variants. Selection rotates mechanisms across tiers and uses no model outcomes.

## Verification and provenance

The versioned inputs are [controlled.json](../../benchmarks/fixtures/difficulty-v1/controlled.json), [realistic.json](../../benchmarks/fixtures/difficulty-v1/realistic.json) and [manifest.json](../../benchmarks/fixtures/difficulty-v1/manifest.json). The manifest binds case hashes, seed `32661013`, generator source, construction rejections, structural audit, difficulty descriptors and proof metadata. Gold/proof/review information remains evaluator-only.

Every original repair schedule and SAT witness passes the independent arithmetic validator. UNSAT certificates are checked without invoking CP-SAT. Every activity has a nonempty individual start domain, including UNSAT instances. Reference solving must prove each SAT objective and each UNSAT label before preparation succeeds; unresolved references stop preparation. The reference compiler is shared with method B, so independent certificates and small exhaustive checks reduce, but do not eliminate, shared-assumption risks. They do not certify natural-language meaning.

To reproduce the deterministic construction in a new directory:

```sh
PYTHONPATH=src .venv/bin/python evaluation/prepare_difficulty_suite.py runs/NEW-difficulty-data
```

This command is offline. It refuses existing destinations and never replaces historical results. After code changes, regenerate into a new directory and compare hashes; do not edit an executed dataset or its receipts in place.

Prepare a concrete human-review packet before execution:

```sh
PYTHONPATH=src .venv/bin/python evaluation/prepare_case_review.py \
  benchmarks/fixtures/difficulty-v1 runs/NEW-difficulty-review \
  --source-mode difficulty-v1
```

The command rechecks all 80 construction certificates and reference solves, then produces `review-index.csv`, `review-packet.json` and one reviewer file per case. Each file places the original/updated gold specification, schedule, witness, proof and all three public renderings together. No member review of these cases was recorded; the 24-case manual review covered the main study only. Review clock conversion, hard/soft rules, repair priorities, ambiguity and possible hints separately. Focus on all twenty fictional requests and examples spanning tiers, mechanisms, task types and labels. These evaluator-only files must not become model inputs. Automated checks establish mathematical consistency, not human review or naturalness.

## Optional preparation for future runs

The original preparation examples below cover Qwen3.6 and Qwen3.8. The executed difficulty pair instead used Qwen3.6 and GLM (`x-test-1`, expected return `glm-5.3-flash`); see its preserved settings in the comparison summary. No full Qwen3.8 difficulty run is claimed. These optional examples build fresh current-source preflights with no credentials or network calls and do not authorize another run. Use the locked Python 3.12 environment from the README:

```sh
# Refresh the installed package before using an independent OS service.
.venv/bin/python -m pip install --no-deps --no-build-isolation .

PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  benchmarks/fixtures/difficulty-v1/controlled.json runs/NEW-difficulty-qwen36-input \
  --realistic benchmarks/fixtures/difficulty-v1/realistic.json \
  --design difficulty-200 --model qwen3.6:35b \
  --qualification-policy strict_model_observe_backend_v1

PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  benchmarks/fixtures/difficulty-v1/controlled.json runs/NEW-difficulty-qwen38-input \
  --realistic benchmarks/fixtures/difficulty-v1/realistic.json \
  --design difficulty-200 --model qwen3.8:27b \
  --qualification-policy strict_model_observe_backend_v1
```

Prepared packets bind source, prompts, environment and case bytes. Regenerate on the actual execution machine after final source changes or installation; a packet is not portable across arbitrary source/runtime changes. The dataset and preparation commands are portable. Use separate output directories for models and runs.

| Setting | Per model |
| --- | --- |
| Scheduling calls | 120 controlled + 40 fictional + 40 wording = 200 |
| All HTTP requests | 203: 200 scheduling + 2 capability + 1 metadata |
| Requested output ceiling | 32,768 tokens per completion |
| Total output reservation | 6,619,136 tokens; actual consumption is recorded; input tokens are additional |
| Connect / read-write-pool limits | 30 / 1,800 seconds |
| Retry policy | One attempt; no retries |
| B solver / gold reference | 30 / 60 seconds, one worker, seed 0 |
| Prompts | Existing revision-3 direct/extraction prompts, equivalent public facts |
| Shared service | Require the exact returned Qwen model ID; record backend fingerprint variation |
| Transient failures | Retain timeout/transport/HTTP 408/500/502/503/504 as failures, cool down 30 seconds, continue to the next distinct request |
| Fatal stops | Authentication/quota/TLS, malformed envelopes, wrong/missing model identity, integrity or exhausted budget |

The two models together reserve at most 406 HTTP requests and 13,238,272 output tokens. Reservations are ceilings, not actual token consumption or monetary caps. No new model calls are authorized by preparing or reading these files. Existing allowances from completed campaigns are not reused.

To run a new campaign, use the existing one-shot supervisor and private local credential file. For example, substituting the actual private file and authorization reference:

```sh
PYTHONPATH=src .venv/bin/python evaluation/launch_macos_campaign.py \
  runs/NEW-difficulty-qwen36-input runs/NEW-difficulty-qwen36-live \
  --env-file /ABSOLUTE/PRIVATE/PATH/.env \
  --authorization-reference 'ACTUAL NEW RUN AUTHORIZATION' --allow-live
```

Use the corresponding Qwen3.8 packet and a different output root for that model. The portable supervisor is `evaluation/supervise_development_campaign.py`. Source must stay fixed while running; keep the machine awake. The dashboard retains separate counters of **120 / 40 / 40**. Full analysis, tables, difficulty figures and replay archive are exported only after all blocks finish. Use saved status/exit JSON for checks; avoid unfiltered OS environment/status dumps.

## Analysis and submission priorities

Preserve the original study as a separate result set; do not pool its rates with this harder and smaller sample. For the extension, compare approaches within each model first, under matched cases and prompts. Cross-model differences remain descriptive because hosted weights, load and hidden defaults are not controlled.

Report failure-inclusive acceptance, SAT validity, UNSAT correctness, valid-schedule reference-objective matching, extraction diagnostics, model/solver/total time and token-usage coverage. Report tier, mechanism, task and label denominators. Tiny cells are descriptive: a controlled tier contains only three SAT instances per task/method. Wider tiers and larger case counts do not imply statistical certainty or monotonically increasing difficulty.

Inspect failures using the original request, extracted specification or direct answer, validation details and objective comparison. Distinguish formalization errors, solving/optimization limitations and operational failures. Select representative examples without excluding other outcomes. Explain both continued success and failure at extreme tiers. Investigate any construction artefacts or shortcuts as limitations, not hidden reasons to discard results.

The supervisor automatically exports the following companions after a complete run. They are derived from verified attempts and included in the new reproduction archive; they never overwrite the old studies.

| Output under `analysis/tables/` | Use |
| --- | --- |
| `study_strata.csv` | Separate block, tier and fine-cell views; accepted/attempted, SAT and UNSAT counts, objective comparison coverage, extraction mismatch and failure counts |
| `tier_resources.csv` | Per block/tier/method full-pipeline, model and solver time plus token distributions; mean, median, p95, maximum and reported/missing coverage |
| `paired_attempts.csv` | Case/rendering/repeat A/B outcomes, objective status and recorded full-pipeline time difference; missing partners remain explicit |
| `casebook.json` | Every attempt's observed diagnostic, plus full evidence for all issues and deterministic successful examples, with checksummed trace pointers |
| `interpretation.md` | Readable block outcomes and casebook index with questions for actual member analysis |
| `tier-comparison.png` / `.pdf` | Grouped A/B bars by block and tier for failure-inclusive acceptance and mean full-pipeline time |

Block, tier and cell rows are different views of the same observations; never sum them together. A fine controlled cell contains only one observation. Objective matching is conditional on valid SAT schedules and comparable reference stages, while acceptance retains every failed attempt. Missing time/tokens stay unavailable. Tier resource averages mix the explicitly declared task/label composition and are descriptive.

The casebook includes every rejected/unscored outcome, structural extraction mismatch and valid suboptimal or incompletely proved objective. It also includes the first clean success per block/tier/method in sorted identity order. Selection is deterministic and does not favour one method; example frequencies are not evaluation rates. Structural differences alone do not establish semantic error or its cause. Human interpretation must connect the actual request fact, output/extraction and validation evidence before making a causal explanation. New performance claims require complete measured runs and verified evidence; keep pending human interpretation explicit. The current comparison has completed those automated checks.

For schema-valid extractions, analysis independently checks the recorded candidate and available gold-reference witness against both specifications on the same time grid. A schedule accepted by one specification and rejected by the other demonstrates a concrete hard-feasibility difference. Matching those witnesses does **not** establish global equivalence or equivalent preferences. Changed time frames/activity sets are reported without pretending their coordinates are comparable. These checks use the independent arithmetic validator, make no model calls and do not rerun the solver or feed gold corrections into either method.

The final report summarizes this study in Table 3.
