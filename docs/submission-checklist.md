# Report and submission acceptance checklist

Current source: [submission-report.md](submission-report.md). Current PDF: [submission-report.pdf](submission-report.pdf). This publication prepares an exploratory report using the completed comparisons. An unchecked item requires real evidence; it is not permission to fabricate a review, submission receipt or human contribution.

## Prepared and verified

- [x] Both generation and minimum-disruption repair, direct and solver-assisted paths, independent validation and end-to-end evaluation are implemented.
- [x] Both full 600-attempt comparisons are complete; all failed attempts remain scored and both archived analyses reproduce offline.
- [x] Current report replaces the older 200-call results with two-model acceptance, SAT/UNSAT, difficulty, paired uncertainty, optimality, extraction, wording and resource analysis.
- [x] Three grouped bar charts derive from the saved summary, with exact denominators and consistent scales.
- [x] Report covers formulation, design, related work, limitations, responsible AI, reproducibility and disclosed AI assistance.
- [x] Two original replay archives are included in the repository and checksum-verified; fuller source/operational/historical evidence has a private verified backup.
- [x] Public report rendered and all ten pages visually inspected: title page 1, eight body pages 2-9, references page 10. Text and compact figure labels are at least 11 pt, with one-inch margins and a single column. The [format receipt](../results/summary/submission-report-format.json) binds this check to exact bytes.

The previous report and format check are historical. Every substantive revision, new figure or private-title edit requires an appropriate fresh render/check; do not reuse a previous page count for a changed document.

## Genuine actions still required before submission

- [ ] Check actual proposal receipt/feedback and current Canvas arrangements; the proposal was mandatory for a project grade (Guidelines P37/P43).
- [ ] Confirm the teaching team's interpretation of the hosted Qwen models against the frontier-model wording (Project p5 / Guidelines P25; SoCLaaS/open weights suggested in Project p6 / P33). No automatic approval or rejection is inferred.
- [ ] Members review the natural-language/gold meaning, reference assumptions and failure examples, and record actual findings in [contributions.md](contributions.md) and the [claim index](claim-evidence.md).
- [ ] Members interpret, revise and take responsibility for the complete report, with accurate actual contributions and human/AI division (Guidelines P56-60/P87-88).
- [ ] Add each member's name, matriculation number and email to the **private** submitted title page (P51); do not put private identifiers in public Git.
- [ ] Produce the actual presentation/deck or requested recording and rehearse **15 minutes plus five-minute Q&A** (P47). All members understand the whole system (P57); a storyboard is not a completed presentation.
- [ ] Have a teammate follow [evidence.md](evidence.md) from a clean compatible environment and record the actual replay/review; existing automated replay does not establish that human action.
- [ ] Recheck the final submitted PDF: at most **10 single-spaced, single-column body pages**, at least **11 pt**, one-inch margins; title/references excluded, all substantive figures/tables included (P49/P92).
- [ ] Verify final filename/upload instructions, submit by the actual Canvas cutoff, and retain the receipt. Presentation week: **9 November 2026**; report due **13 November** (Project p8 / P13-14). **30 October** is the team's complete-draft target.

## Scientific scope and course distinctions

Constructed or downloaded instances are explicitly allowed (Project p5 / P25). The course values meaningful comparison and insight about assumptions, realism, representation and results (P84), not a prescribed accuracy, solver victory, external benchmark or extra feature count. The current report presents known synthetic/AI-assisted development evidence honestly. A fresh holdout, exactly 600 calls, independent-human prose and fixed backend were team study choices, not additional course rules.

An additional model or fresh study is conditional on actual teaching feedback or a separately agreed scientific need. If chosen, define the question, eligibility, exact protocol, new data/review and separate execution allowance first. Never relabel inspected cases as held out. The new report's scope does not resolve model eligibility or supply human review.

## Responsible-AI review

Discuss concrete unequal inconvenience, lexicographic objective trade-offs, privacy/reidentification, ambiguous hard versus soft requirements, explanation boundaries and user control. Fixed task assignments do not establish fair workload allocation. Prompt-boundary tests do not establish live adversarial robustness. Sources: Project p7 / Guidelines P35/P62; ResponsibleAI slides 9-10, 17-20, 23-27, 30-31 and 34-35.

## Rebuild the report

The Markdown source is canonical. From the repository root, regenerate compact figures using the locked experiment environment:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/render_benchmark_results.py \
  --report --output docs/figures/submission
```

Report tooling is separate from the scheduling runtime:

```sh
python3.12 -m venv .venv-docs
.venv-docs/bin/python -m pip install reportlab==4.4.9 pdfplumber==0.11.9
.venv-docs/bin/python scripts/render_report.py
.venv-docs/bin/python scripts/check_report.py
```

Use Poppler `pdftoppm` to render every PDF page for visual inspection. Automated bounds/text checks supplement that inspection. Report plotting and rendering are offline; no provider key is needed. For private title details, edit a separate private Markdown copy and render with `--source` / `--output`; never overwrite the public evidence with identifiers.
