# Presentation and demonstration guide

The prepared presentation has **15 main slides for a 15-minute talk**, followed by **five reference slides for the separate five-minute Q&A**. It explains the formulation, common-input comparison, worked timetable, measured findings, failure mechanisms, limitations and responsible AI. Use the [rehearsal guide](rehearsal.md) for the matching slide sequence and speaking checkpoints.

The final PPTX and DOCX script are retained in the team's local `cs3263_project_final` delivery folder. This directory contains reproducible demonstration inputs and presentation guidance. The [public report](../docs/submission-report.pdf), [report source](../docs/submission-report.md) and [evidence index](../docs/claim-evidence.md) provide the reader-facing scientific record. Private submission identity details remain outside Git.

## Main study and examples

The presentation uses **Qwen3.6 35B A3B** and **GLM5.3 Flash**, each evaluated on the same **1,000 generation cases using two methods**: 4,000 scheduling attempts overall. Keep the earlier balanced, difficulty and historical Qwen studies separate from these primary scores. Generation is the core; repair is a separately evaluated extension.

Start with the [worked example and original traces](../docs/report-details.md#example-trace-index): both solver-assisted runs return a valid shared-room timetable, while the two direct answers exhibit different failures. Then connect the [acceptance chart](../docs/figures/report-polished-20261018/diverse-acceptance.png) to the [failure chart](../docs/figures/report-polished-20261018/diverse-failures.png). No live model request is needed during the presentation.

## Offline demonstration

Run from the repository root after the [installation steps](../README.md#quick-start), choosing a fresh output path:

```sh
# Four small office examples: loose/tight generation, infeasibility and repair.
PYTHONPATH=src .venv/bin/python evaluation/ta_scope_examples.py runs/presentation-office.json

# Both pipelines and replay with explicitly canned responses.
.venv/bin/python evaluation/offline_demo.py runs/presentation-offline
.venv/bin/scheduling explain --run-dir runs/presentation-offline --case-id repair --approach solver_augmented
```

These commands make zero model calls. Label their outputs as offline illustrations or integration checks, not additional model-performance results. The office examples use the supported single-day/30-minute formulation; [scope details](../docs/ta-feedback-alignment.md) explain the difference from the suggested weekly scenario.

For original recorded model answers, follow the [evidence guide](../docs/evidence.md) and inspect the exact case identifiers in the report supplement. Preserve failures, original extracted specifications and study labels. [Earlier presentation examples](../docs/history/development-notes/presentation-examples-20261107.md) retain their historical commands and assumptions; they are not the current talk outline.

## Before presenting

Rehearse with the final PPTX and script, check chart readability on the presentation computer, and time the handovers. Each member should be able to explain both methods, one extraction failure and the study's limitations. The [submission checklist](../docs/submission-checklist.md) tracks the remaining evidence review and delivery checks. A prepared script does not establish an actual timed rehearsal.
