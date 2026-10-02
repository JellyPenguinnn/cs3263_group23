# Expanded development comparison: 100 cases, 200 calls

This run broadens the development comparison beyond the twelve-case qualification packet. It evaluates the existing direct and solver-assisted pipelines with the same SoCLaaS model and fixed prompts. It is a development study on known synthetic generators, not the final held-out course evaluation.

## Preselected design

- **100 distinct scheduling cases:** 50 generation and 50 repair, with 25 SAT and 25 UNSAT in each task.
- **200 completion calls:** one direct response and one extraction response per case; one canonical rendering; no repeats, retries, feedback or outcome-based replacements.
- **64 v2 cases:** every activity-count, slack, interaction-density and resource-contention sweep; all three levels and all repair-event types represented.
- **36 v3 cases:** resource chains, precedence chains and unary-boundary controls; all three sizes, both labels and paired generation/repair.
- **41 conservative source families:** related task/event/label variants remain grouped for uncertainty. Counts alone do not make all 100 independent.
- Repair-event balance: 16 blocked-interval, 17 deadline and 17 fixed-start cases.
- Deterministic preparation: v2 seed 3264, v3 seed 3265, ordering seed 326630. Event and extra-level selection follow the checked preparation script, before inspecting outputs.

All 100 cases match known development structures; fourteen case IDs occurred in the available historical live packets. The remaining 86 IDs were not in those packets, but are still development data. The generators were already inspected and used for development. There is no claim of unseen inputs, independent human authorship or natural-language robustness.

`evaluation/prepare_development_expansion.py` saves complete source pools, provenance, selected IDs, hashes, overlap and a source-family audit. The 100 gold references were checked before inference: 50 SAT and 50 UNSAT. A separate canned run completed all 200 attempts, including resume and replay, before live execution. That check is integration evidence only.

## Model, limits and accounting

The user chose 200 model calls and requested more generous time/token budgets plus measured resource statistics. This run uses:

| Setting | Value |
| --- | --- |
| Model | SoCLaaS `qwen3.6:35b` |
| Per-call output ceiling | 16,384 tokens for both approaches |
| Completion-call cap | 200 |
| Reserved output ceiling | 3,276,800 tokens; input tokens additional |
| Connect/read timeout | 30 / 600 seconds |
| Transport attempts | One; no automatic retries |
| B solver limit | 30 seconds per solve, shared across repair stages |
| Gold-reference limit | 60 seconds |
| Solver workers/seed | One worker, seed 0 |
| Prompt | Existing direct prompts and extraction revision 3, unchanged |

One separate metadata-only model-listing request verified availability; it is not included in the 200 scheduling completions. Actual reported prompt, completion and total tokens are stored per attempt. Model-response latency, pipeline time, conditional solver time and overall batch wall time are separate statistics. Missing usage remains missing, not zero; no currency cost is inferred without verified pricing.

The larger model/solver limits differ from the earlier 24-call pilot. The new A/B comparison uses equal model settings within this run; comparison to an older score is descriptive and cannot isolate a prompt or budget effect. Hard failures, invalid answers and incomplete outputs remain in denominators. Provider failures stop the batch with durable accounting.

## Results

| Task | Direct A accepted | Solver-assisted B accepted | A valid on SAT | B valid on SAT | A correct UNSAT | B correct UNSAT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Generation | 23/50 (46%) | 48/50 (96%) | 17/25 | 24/25 | 6/25 | 24/25 |
| Repair | 12/50 (24%) | 49/50 (98%) | 8/25 | 25/25 | 4/25 | 24/25 |
| Total | **35/100** | **97/100** | 25/50 | 49/50 | 10/50 | 48/50 |

All 200 completions returned `qwen3.6:35b`, finish reason `stop`, and complete prompt/completion/total usage. There were no provider errors, hidden retries, timeout outcomes or output-limit truncations. The three B failures are answer/extraction failures, not transport failures. All failures remain in denominators.

The generation B-minus-A difference is **50 percentage points**, with a source-family bootstrap 95% interval of **36.54–63.27 pp**. Repair differs by **74 pp**, interval **59.18–88.89 pp**. There are 41 families and 50 paired cases in each task. These quantify variation under the selected development construction; they do not establish general real-world superiority.

V2 separately: A 21/64, B 62/64. V3 separately: A 14/36, B 35/36. Among the 86 case IDs not used in the named earlier live packets, A 31/86 and B 83/86; those cases still come from known development generators. The advantage is not confined to the 14 repeated IDs. Small factor-level cells remain descriptive, especially v3's nine related families.

**Solution quality:** every one of B's 25 valid repairs attained the gold lexicographic objective (moved activities, shift, preference penalty). All 24 valid B generation schedules had zero preference gap. A produced 8 valid repairs; 6 matched the full gold objective. These quality comparisons are conditional on validity, with different denominators.

### Observed time and token use

| Measurement | Direct A: 100 calls | Solver-assisted B: 100 calls |
| --- | ---: | ---: |
| Prompt tokens | 102,676 | 199,426 |
| Completion tokens | 22,020 | 141,129 |
| Total tokens | 124,696 | 340,555 |
| Mean model-response latency | 1.895 s | 10.115 s |
| Median model-response latency | 1.278 s | 9.413 s |
| p95 model-response latency | 2.074 s | 14.954 s |
| Maximum model-response latency | 48.195 s | 20.321 s |
| Mean full pipeline time | 1.896 s | 10.122 s |

Total reported usage: **465,251 tokens**, comprising 302,102 prompt and 163,149 completion tokens. Batch wall time: **1,204.72 seconds** (20 minutes 4.72 seconds), including reference setup, calls, solving and durable records. Model-response times sum to 1,201.09 seconds. The separate metadata listing is excluded from model-response totals. p95 uses the nearest-rank definition; the slow direct outlier is retained.

B's solver ran 99 times: mean **0.004690 s**, p95 **0.010560 s**, maximum **0.043433 s**, total **0.464282 s**. The malformed extraction never reached the solver and is not recorded as zero solver time. Gold-reference preprocessing is separate from B's solver timing. B used approximately 2.73 times A's reported tokens and 5.34 times its mean model latency; the extraction call dominates this overhead.

The largest completion was 6,703 tokens, below 16,384. All observed model calls finished well inside 600 seconds, and all executed B solves finished within 30 seconds. Larger budgets removed immediate capacity pressure in this run, but do not guarantee success on other models or larger problems.

### Failure and semantic analysis

A failures: 57 gold-invalid schedules, 5 false UNSAT claims and 3 invalid responses. B failures:

| Case | Observation |
| --- | --- |
| `dev-v2-3264-slack-0-fixed_start-unsat-0-repair` | Extractor omitted the updated A0 fixed start; the returned schedule violated that gold appointment |
| `dev-v2-3264-interaction_density-2-fixed_start-unsat-0-generation` | Extractor omitted A1's fixed anchor; the returned schedule violated it |
| `dev-v3-1cb82271f05a61f8e4b44569-generation` | Invalid JSON: missing comma delimiter at line 25, column 9; completion finished normally, without truncation |

B produced 99 schema-valid extractions: 89 matched gold structurally and 10 differed. Independent per-activity exhaustive arithmetic, together with equal durations/assignments, precedence, preferences and repair context, certified 8 of those 10 as equivalent within the supported v1 formal semantics. They add redundant bounds or re-express availability/blocked intervals. The two omitted appointments change legal-start domains and correspond to the two gold-invalid schedules. Keep the original structural-mismatch count unchanged; the [semantic diagnostic](../results/summary/expanded-development-100-semantics-20260930.json) is a separate bounded certificate, not human review or a universal semantic-equivalence checker.

### Verification

The completed run replayed exactly through the existing independent scoring/summary functions. Completed resume retained 200 reservations and invoked a provider callback zero times. All 100 dashboard case consumers read both approaches, and the 302 saved record/reference/manifest files remained byte-for-byte unchanged. JSON/CSV and PNG/PDF exports succeeded. No inference beyond the 200 completion calls and one metadata listing was performed.

See the [aggregate](../results/summary/expanded-development-100-20260930.json), [resource statistics](../results/summary/expanded-development-100-resources-20260930.json), and [verification receipt](../configs/development/expanded-development-100-verification.json). The [per-attempt CSV](../results/summary/expanded-development-100-attempts-20260930.csv) records all 200 calls without raw model content.


## Interpretation and next decisions

The result supports continuing the direct-versus-formal-solver architecture for this development distribution. Both generation and repair show a substantial paired advantage, and the repair objective achieves its intended behavior on B's valid schedules. The cost is a longer, larger extraction response. This is stronger engineering and exploratory evidence than the twelve-case packet, without resolving generator bias or final-study eligibility.

1. **Preserve the working solver and comparison.** The observed solver work is milliseconds; extra search machinery is not the current priority. Retain independent gold checking and all three repair objectives.
2. **Target extraction fidelity.** Add development regressions for the two missing fixed-start cases and the malformed JSON. Review how the extraction guidance accounts for each fixed appointment and updated event. Any prompt/structured-output improvement needs verified provider support, a new configuration and a separately authorized pilot; do not repair archived answers, leak gold or add hidden calls.
3. **Separate equivalent encodings from meaningful omissions.** Use bounded independent certificates or human review for diagnostic interpretation. Do not silently change the existing structural metric or call all 10 differences errors, and do not infer general language faithfulness from these eight certificates.
4. **Expand evidence quality before another large run.** Complete human gold/wording review, introduce the agreed realistic-language condition, and prepare truly fresh final cases with development exclusions. This canonical-only run cannot measure paraphrase robustness.
5. **Complete course gates.** Resolve final-model eligibility/access, freeze the final protocol and budget, run the held-out study, and finish the report/presentation. Do not equate development 97% with expected production reliability or a guaranteed grade.


## Reproduction and evidence

Run ID: `expanded-development-100-20260930-01`. Configuration: `configs/development/expanded-development-100.json`. Inputs and metadata are local under `runs/expanded-development-100-inputs-20260930-01/`; raw attempts are in the run directory. The tracked aggregate and resource receipt contain no credentials or raw model content. A fresh clone can regenerate the deterministic case packet, but exact response replay requires the preserved synthetic run archive.

Prepare and check a new packet without inference:

```sh
.venv/bin/python evaluation/prepare_development_expansion.py runs/NEW-expanded-input
.venv/bin/python evaluation/v2_qualification.py runs/NEW-expanded-offline \
  --cases runs/NEW-expanded-input/cases.json
```

Live execution requires its own authorization; the completed allowance is not reusable:

```sh
.venv/bin/scheduling evaluate-batch --allow-live \
  --cases runs/NEW-expanded-input/cases.json \
  --config configs/development/expanded-development-100.json \
  --run-dir runs/NEW-expanded-live
```

Replay creates no model calls:

```sh
.venv/bin/scheduling evaluate-replay \
  --run-dir runs/expanded-development-100-20260930-01 \
  --export-dir artifacts/NEW-expanded-replay --figures
```

Statistics use the existing independent replay/scoring and summary functions. Paired uncertainty resamples source families with seed 3263 and 10,000 resamples. Cells with fewer than 10 families are descriptive. This follows the distinction between paired and clustered observations discussed in [Miller, Adding Error Bars to Evals](https://arxiv.org/html/2411.00640v1); the selected synthetic distribution is not representative of all real scheduling.

No prompts, solver formulation, old runs, historical scores or held-out data were changed to obtain these results. Human scientific/wording review, final-model eligibility, fresh final data, the approved final study, independent teammate replay and course deliverables remain open.
