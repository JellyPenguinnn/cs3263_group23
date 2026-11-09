# Resource distributions and worked-case evidence

This supplement provides resource distributions, complete worked examples and reproduction instructions for the report. All values derive from the preserved attempt records.

## Definitions and reproduction

Use `python3 scripts/build_report_details.py --output /tmp/NEW-report-details.json` and compare with [the saved derivation](../results/summary/report-details-20261018.json). The builder verifies both archives and links all 4,000 analysis rows to their original attempt checksums. Mean and median use nonmissing observations; p95 is the nearest-rank observation at rank `ceil(0.95*n)`, without interpolation. Unknown token usage is not zero. Timing includes failed attempts; solver time is conditional on solver invocation.

Pipeline duration measures each method execution, including provider waiting, parsing/extraction and applicable local solver work. It excludes independent evaluation/reference solving and pre-dispatch waiting; it is not campaign wall time. Model-call time includes network/service waiting. Local solver duration includes preprocessing, not CP-SAT search alone. Monotonic clocks may differ from UTC elapsed time during sleep.

Zero cases have all four model/method observations under matched OS and concurrency. Pooled distributions describe these runs, not intrinsic model speed. GLM direct p95 near 300 seconds includes gateway failures. See the [execution audit](studies/diverse-comparison-audit.md#execution-phases-and-timing-comparability) for preserved phase transitions, sleep and infrastructure evidence.

## Total tokens per scheduling attempt

| Model / method | Mean | Median | p95 | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6 A | 3,287.53 | 1,977.00 | 12,751.00 | 951/1000 |
| Qwen3.6 B | 5,220.42 | 4,737.50 | 8,490.00 | 998/1000 |
| GLM5.3 Flash A | 7,504.09 | 5,592.00 | 19,191.00 | 935/1000 |
| GLM5.3 Flash B | 7,054.56 | 6,159.00 | 12,750.00 | 997/1000 |

## Model-call duration (seconds)

| Model / method | Mean | Median | p95 | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6 A | 36.53 | 21.55 | 132.49 | 1000/1000 |
| Qwen3.6 B | 41.24 | 37.37 | 87.40 | 1000/1000 |
| GLM5.3 Flash A | 108.67 | 71.46 | 300.05 | 1000/1000 |
| GLM5.3 Flash B | 67.06 | 55.22 | 141.89 | 1000/1000 |

## Pipeline duration (seconds)

| Model / method | Mean | Median | p95 | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6 A | 36.53 | 21.55 | 132.49 | 1000/1000 |
| Qwen3.6 B | 41.26 | 37.38 | 87.42 | 1000/1000 |
| GLM5.3 Flash A | 108.68 | 71.46 | 300.05 | 1000/1000 |
| GLM5.3 Flash B | 67.07 | 55.24 | 141.91 | 1000/1000 |

## Local solver duration (milliseconds)

| Model / method | Mean | Median | p95 | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.6 A | n/a | n/a | n/a | 0/1000 |
| Qwen3.6 B | 16.19 | 10.25 | 36.52 | 973/1000 |
| GLM5.3 Flash A | n/a | n/a | n/a | 0/1000 |
| GLM5.3 Flash B | 13.97 | 11.39 | 33.01 | 992/1000 |

## Distributions by execution phase

The recorded scientific settings remain unchanged, but phases differ operationally. Do not pool these rows into a controlled speed ranking. OS labels and concurrency come from saved provenance. Small phases have unstable empirical tails; p95 can be their maximum.

### Total tokens per scheduling attempt

| Model / arm | Phase | OS | Concurrency | Mean | Median | p95 | Coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6 A | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 6,272.67 | 2,882.00 | 15,072.00 | 3/8 |
| Qwen3.6 B | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 5,492.00 | 5,838.50 | 8,785.00 | 8/8 |
| Qwen3.6 A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 2,999.07 | 1,981.00 | 11,339.00 | 755/796 |
| Qwen3.6 B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 5,367.85 | 4,938.00 | 8,592.00 | 796/797 |
| Qwen3.6 A | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 4,243.79 | 1,720.50 | 14,398.00 | 146/148 |
| Qwen3.6 B | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 4,273.88 | 3,853.50 | 6,695.00 | 146/147 |
| Qwen3.6 A | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 4,760.28 | 2,250.00 | 16,043.00 | 47/48 |
| Qwen3.6 B | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 5,609.29 | 5,693.00 | 7,738.00 | 48/48 |
| GLM5.3 Flash A | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 7,674.40 | 5,793.50 | 19,296.00 | 890/954 |
| GLM5.3 Flash B | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 7,187.36 | 6,420.50 | 12,872.00 | 952/954 |
| GLM5.3 Flash A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 4,135.78 | 3,168.00 | 10,554.00 | 45/46 |
| GLM5.3 Flash B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 4,245.22 | 4,085.00 | 5,762.00 | 45/46 |

### Model-call duration (seconds)

| Model / arm | Phase | OS | Concurrency | Mean | Median | p95 | Coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6 A | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 43.58 | 13.00 | 131.44 | 8/8 |
| Qwen3.6 B | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 49.51 | 44.98 | 92.97 | 8/8 |
| Qwen3.6 A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 39.52 | 23.93 | 136.35 | 796/796 |
| Qwen3.6 B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 47.03 | 43.43 | 89.22 | 797/797 |
| Qwen3.6 A | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 23.99 | 1.45 | 100.51 | 148/148 |
| Qwen3.6 B | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 15.94 | 14.17 | 28.64 | 147/147 |
| Qwen3.6 A | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 24.34 | 0.50 | 109.89 | 48/48 |
| Qwen3.6 B | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 21.23 | 21.39 | 33.18 | 48/48 |
| GLM5.3 Flash A | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 108.12 | 69.28 | 300.05 | 954/954 |
| GLM5.3 Flash B | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 65.47 | 53.25 | 137.67 | 954/954 |
| GLM5.3 Flash A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 120.16 | 96.90 | 256.00 | 46/46 |
| GLM5.3 Flash B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 99.85 | 98.59 | 149.22 | 46/46 |

### Pipeline duration (seconds)

| Model / arm | Phase | OS | Concurrency | Mean | Median | p95 | Coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6 A | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 43.60 | 13.01 | 131.52 | 8/8 |
| Qwen3.6 B | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 49.57 | 45.01 | 93.03 | 8/8 |
| Qwen3.6 A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 39.52 | 23.93 | 136.35 | 796/796 |
| Qwen3.6 B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 47.04 | 43.44 | 89.25 | 797/797 |
| Qwen3.6 A | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 23.99 | 1.46 | 100.52 | 148/148 |
| Qwen3.6 B | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 15.99 | 14.19 | 28.68 | 147/147 |
| Qwen3.6 A | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 24.35 | 0.50 | 109.89 | 48/48 |
| Qwen3.6 B | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 21.27 | 21.43 | 33.24 | 48/48 |
| GLM5.3 Flash A | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 108.12 | 69.28 | 300.05 | 954/954 |
| GLM5.3 Flash B | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 65.49 | 53.27 | 137.73 | 954/954 |
| GLM5.3 Flash A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 120.16 | 96.90 | 256.00 | 46/46 |
| GLM5.3 Flash B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 99.86 | 98.60 | 149.23 | 46/46 |

### Local solver duration (milliseconds)

| Model / arm | Phase | OS | Concurrency | Mean | Median | p95 | Coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3.6 A | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | n/a | n/a | n/a | 0/8 |
| Qwen3.6 B | parallel16 | macOS-27.0.1-arm64-arm-64bit | 16 | 23.04 | 14.93 | 61.30 | 8/8 |
| Qwen3.6 A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | n/a | n/a | n/a | 0/796 |
| Qwen3.6 B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 11.18 | 9.41 | 23.56 | 774/797 |
| Qwen3.6 A | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | n/a | n/a | n/a | 0/148 |
| Qwen3.6 B | serial_before_parallel | macOS-26.5.2-arm64-arm-64bit | 1 | 38.11 | 15.75 | 71.10 | 145/147 |
| Qwen3.6 A | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | n/a | n/a | n/a | 0/48 |
| Qwen3.6 B | serial_before_parallel | macOS-27.0.1-arm64-arm-64bit | 1 | 30.09 | 18.66 | 67.74 | 46/48 |
| GLM5.3 Flash A | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | n/a | n/a | n/a | 0/954 |
| GLM5.3 Flash B | parallel4 | macOS-27.0.1-arm64-arm-64bit | 4 | 14.07 | 11.44 | 34.52 | 947/954 |
| GLM5.3 Flash A | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | n/a | n/a | n/a | 0/46 |
| GLM5.3 Flash B | parallel8 | macOS-27.0.1-arm64-arm-64bit | 8 | 11.98 | 11.09 | 27.20 | 45/46 |

## Worked example and interpretation

Case `dg-3fd5174321284caacab1f4a9` is selected to explain mechanisms, not estimate their frequency. The [derived record](../results/summary/report-details-20261018.json) contains its complete canonical public view, evaluator-only specification, four original pipeline outputs and clock schedules. Report clock notation is a deterministic conversion of slots; the original benchmark prompt was not rewritten or rerun.

Qwen3.6 direct incorrectly reports UNSAT. GLM5.3 Flash direct schedules A4 and A5 together at 11:00-11:30: a room overlap and an A4 availability violation. Both solver-assisted extractions match gold and return the same optimal schedule. All four calls returned answers without provider errors. The three impossible preferred-start windows incur unavoidable soft penalties 3+1+2=6; these deliberately conflicting preferences do not make the hard problem infeasible. A7 meets its preference, so the valid solver-assisted schedule achieves the lower bound.

The main report retains separate counterexamples of harmful extraction. A selected solver-assisted success does not prove universal benefit or perfect translation. Earlier traces and charts remain unchanged; compact report figures are new presentation derivatives.

## Worked-case input table

Availability constrains the whole activity, not only its start. The report timetable illustrates the same saved schedule. Both solver-assisted runs returned the same start time for each activity.

| Activity | Person | Minutes | Availability | Solver-assisted start (both models) |
| --- | --- | ---: | --- | --- |
| A1 | P1 | 30 | 10:00-13:30 | 12:30 |
| A2 | P2 | 60 | 12:00-15:00 | 13:00 |
| A3 | P1 | 30 | 09:30-13:00 | 09:30 |
| A4 | P1 | 30 | 09:00-11:00 | 10:00 |
| A5 | P2 | 30 | 09:00-11:30 | 10:30 |
| A6 | P1 | 60 | 10:00-14:30 | 11:00 |
| A7 | P1 | 30 | 10:30-14:30 | 12:00 |
| A8 | P2 | 30 | 09:00-10:30 | 09:00 |


## Reproducing the report visuals

The resource builder requires a new output path and refuses to overwrite an existing file. Compare the regenerated JSON with the committed derivative; choose a fresh ignored path on subsequent checks.

The scientific runtime and dependency lock remain separate from document tooling. Follow the [report rebuild instructions](process/submission-checklist.md#rebuild-the-report) to create `.venv-docs` from `requirements-docs.txt`. This pins Matplotlib 3.10.0 used by the current report figure receipt; the scientific runtime retains 3.10.8. A different rendering-library version may change figure bytes without changing results. Mermaid is needed only when changing the architecture asset.

Use a fresh ignored directory for reproduction so preserved figures and receipts are not overwritten:

```sh
mkdir -p runs
mkdir runs/report-review
.venv/bin/python scripts/build_report_details.py --output runs/report-review/details.json
cmp runs/report-review/details.json results/summary/report-details-20261018.json
MPLCONFIGDIR=.cache/matplotlib .venv-docs/bin/python scripts/render_report_comparison.py --output runs/report-review/comparison-figures
MPLCONFIGDIR=.cache/matplotlib .venv-docs/bin/python scripts/render_diverse_results.py --compact --output runs/report-review/supplementary-figures
MPLCONFIGDIR=.cache/matplotlib .venv-docs/bin/python scripts/render_worked_timetable.py --output runs/report-review/timetable
.venv-docs/bin/python scripts/render_report.py --output runs/report-review/submission-report.pdf
.venv-docs/bin/python scripts/check_report.py --pdf runs/report-review/submission-report.pdf --receipt runs/report-review/format.json
```

The report build embeds the reviewed assets. The current timetable is in `docs/figures/report-timetable-20261018/`, with PNG, vector PDF/SVG and a source/renderer/data receipt; its earlier rendering remains preserved. Freshly reproduced comparison figures and timetables above are for verification. Replacing a published asset is a separate reviewed edit. Inspect all rendered pages; source/text bounds checks alone do not establish visual quality. Private title copies use `--source docs/private/submission-report.md` and output/receipt paths inside ignored `docs/private/`.

The architecture source is `docs/figures/report-compact-20261018/architecture.mmd`, also included in the report's Mermaid fence. Keep the two sources identical. An intentional architecture edit uses Mermaid CLI 11.12.0 in a separate Node document-tool environment: `python3 scripts/render_report_mermaid.py --mmdc /path/to/mmdc --puppeteer-config /path/to/chrome-config.json`. That command updates the architecture asset/receipt in place and therefore requires a reviewed diff and fresh report checks. Normal report builds reuse the committed vector asset and need no browser. No document command calls the model provider.

## Conducting the human review

The team completed this review for the 24-case packet (eight cases per member) and found no request/gold mismatches. The procedure below is how it was carried out.

Use this worked example as a first exercise, then check contrasting SAT/UNSAT cases and an extraction failure from the claim index. Each member should read the natural-language input before consulting gold, independently list the durations, windows, shared entities, hard constraints and preferences, and compare that interpretation with the formal specification. On the timetable, check complete-window containment, resource/participant non-overlap, precedence and the penalty calculation. For rejected answers, identify the exact violated rule or missing/invented constraint rather than merely repeating the validator label. Review why the selected example does not establish a frequency, and why infrastructure failures cannot be presented as reasoning errors.

Record actual case IDs, reviewer names, findings, disagreements and resolutions in the team review/contribution records. Every member should be able to explain both methods, the extraction/solving distinction and the principal limitations. See the [submission checklist](process/submission-checklist.md) for the remaining submission tasks.

## Example trace index

The main report uses descriptive example names to keep the scientific explanation readable. These identifiers locate the unchanged original cases; they are not additional experiments.

| Report example | Exact case identifier | Evidence |
| --- | --- | --- |
| Shared-room timetable and four outcomes | `dg-3fd5174321284caacab1f4a9` | Full public/gold inputs and four saved outputs in the [resource/example derivative](../results/summary/report-details-20261018.json) |
| Invented deadlines — Qwen B | `dg-901f5127b3f63880cc499f19` | Saved extraction and evaluation in the [diverse comparison audit](studies/diverse-comparison-audit.md) and immutable Qwen archive |
| Dropped constraints — GLM B | `dg-93645cd68c645d31d613fa2b` | Saved extraction and evaluation in the [diverse comparison audit](studies/diverse-comparison-audit.md) and immutable GLM archive |
| Valid but suboptimal schedule — GLM A | `dg-a7542bcaf35f7024ab973f3c` | Preference penalty 33 versus proven optimum 30; [diverse comparison audit](studies/diverse-comparison-audit.md) and immutable GLM archive |

The extraction errors are detailed below:

In Qwen B case `dg-901f5127b3f63880cc499f19`, extraction invents eight deadlines. A1 must run for two slots inside [4,6), but the invented deadline requires completion by 4. The resulting empty domain makes the extracted specification infeasible even though the original is feasible. In GLM B case `dg-93645cd68c645d31d613fa2b`, extraction drops an A2 deadline and the A29-before-A10 relation. CP-SAT then places A29 at 4 for two slots and A10 at 4, violating the omitted precedence. These failures demonstrate the distinction between correct solving and faithful formalization.

## Detailed formulation and original scope notes

The following defines the repair extension in detail. The primary comparison evaluates generation.

### Generation model and repair extension

For activity i, let s_i be its integer start, d_i its fixed duration and e_i = s_i + d_i its end. The horizon H is at most 48 slots. Its domain D_i contains starts from 0 to H-d_i satisfying all unary restrictions: release, deadline, fixed start, blocked intervals, and full containment in an availability window for every required activity, participant and resource. Each activity must fit inside one listed window; adjacent windows are not silently merged. Half-open activity intervals allow one activity to begin exactly when another ends.

Precedence i before j requires e_i <= s_j. Every shared participant or resource imposes non-overlap on its activity intervals. Empty start domains encode contradictions, rather than malformed input. These variables, domains and hard constraints form a constraint satisfaction problem. Adding preferences produces a constraint optimization problem. A weighted preference contributes its weight when an activity starts outside its preferred start window. Generation minimizes the sum P(s).

The repair extension validates the previous schedule against the original specification, then solves the updated specification using the same activity identities and previous starts. Let *A* index activities and *K* index preferences. Each preference *k* has a weight, a preferred start window and a target activity *a(k)*. The indicator is 1 when its condition holds and 0 otherwise. The four expressions below define moved count, total shift, preference penalty and the repair objective, respectively:

```math
M(\mathbf{s}) = \sum_{i \in A} \mathbf{1}[s_i \neq s_i^{\mathrm{old}}]
```

```math
T(\mathbf{s}) = \sum_{i \in A} |s_i-s_i^{\mathrm{old}}|
```

```math
P(\mathbf{s}) = \sum_{k \in K} w_k\,\mathbf{1}[s_{a(k)} \notin W_k]
```

```math
\underset{\mathbf{s}\in F}{\mathrm{lexmin}}\;\left(M(\mathbf{s}),\,T(\mathbf{s}),\,P(\mathbf{s})\right)
```

Here, *F* is the set of schedules satisfying all updated hard constraints; T sums absolute start shifts, not changed occupied timetable cells; the superscript "old" denotes the previous start; weights and preferred windows are indexed by preference. A start outside its preferred window contributes that preference's weight once, regardless of distance. Lexicographic minimization gives moved count priority over total shift, and total shift priority over preference penalty.

CP-SAT proves the best moved count M, fixes it, proves the best shift T, and finally minimizes P. Stages share a 30-second solve budget with zero absolute and relative optimality gaps. A valid incumbent may survive a timeout, but unproved later priorities remain unproved. `UNKNOWN` is distinct from `INFEASIBLE`, and `FEASIBLE` from `OPTIMAL`. A secondary objective gap is reported only when earlier priorities equal their proven reference values.

**Scope relative to feedback.** The TA recommends achievable generation, both approaches and independent validation as the core, with repair as an extension. Our offline office examples demonstrate eight 1–2-hour activities, two people and one room, including loose/tight feasibility and a one-move repair. The implemented calendar is one day on 30-minute slots, not the suggested five-day/hourly calendar. Morning preferences fit preferred-start windows; consecutive-meeting and day-clustering penalties are absent. These simplifications require explicit scope clarification rather than a claim that every suggestion is implemented.

## Source provenance

The report's [ten references](submission-report.md#references) support the methods and interpretation used in the project. Each is cited at the relevant point in the report. The project repository is linked separately under code and data availability; it supplies our empirical evidence rather than independent research findings.

| Report references | Application in this project |
| --- | --- |
| 1-2: NATURAL PLAN and SCHEDBench | Equivalent public task information, explicit constraint faithfulness and evaluation design. Our primary cases are generated locally; no external benchmark instances or published scores are pooled with them. |
| 3-4: formal-tool planning and planning formalization | The direct-versus-translation comparison and the distinction between parsing, extracted-specification fidelity and final answer validity. Our single-call fixed compiler does not reproduce an iterative verification framework. |
| 5-7: CP-SAT research and OR-Tools documentation | Interval/non-overlap modeling, precedence, solver statuses and release-matched proof/bound semantics. |
| 8: Miller | Paired and clustered evaluation principles. The ten-family bootstrap is an analysis of these constructed cases, not evidence of real-calendar representativeness. |
| 10: Garey and Johnson | NP-completeness of single-resource sequencing with release times and deadlines, used for the problem-difficulty discussion in Section 3. |
| 9: minimal perturbation | The separately evaluated repair extension and its minimum-disruption objective; repair is not pooled with the primary generation study. |

Course guidance, TA correspondence and references considered only for unused alternatives remain in the existing development and review records. They are not included in the final report's scientific bibliography. The [preserved development notes](history/development-notes/development-plan-history.md#research-basis-for-the-recommendations) retain that wider history without implying that every discussed method, model or dataset was used.
