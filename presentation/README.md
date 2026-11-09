# Presentation and demonstration guide

The final presentation is a **recorded video of at most 10 minutes** built from a **16-slide deck**: [CS3263_Group23_Presentation_Slides.pptx](CS3263_Group23_Presentation_Slides.pptx). Its speaker notes give the presenter, target time, narration and sources for each slide; [CS3263_Group23_Script.docx](CS3263_Group23_Script.docx) contains the narration only. The [rehearsal guide](rehearsal.md) lists the slide sequence, timing and likely questions.

The talk follows the [report](../docs/submission-report.md): problem and formulation, the two methods, the 1,000-case study and worked example, results and failure analysis, infrastructure failures and cost, earlier feedback-scenario studies, limits, responsible AI, and the answer to the research question. No live model request is needed during the presentation.

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

Rehearse with the final PPTX and script, check chart readability on the presentation computer, and time the handovers. Each member should be able to explain both methods, one extraction failure and the study's limitations. The [submission checklist](../docs/process/submission-checklist.md) tracks the remaining evidence review and delivery checks. A prepared script does not establish an actual timed rehearsal.
