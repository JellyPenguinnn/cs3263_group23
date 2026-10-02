# Report and submission acceptance checklist

Current source: [submission-report.md](submission-report.md). Current PDF: [submission-report.pdf](submission-report.pdf). This publication prepares an exploratory report using the completed comparisons. An unchecked item requires real evidence; it is not permission to fabricate a review, submission receipt or human contribution.

## Prepared and verified

- [x] Both generation and minimum-disruption repair, direct and solver-assisted paths, independent validation and end-to-end evaluation are implemented.
- [x] Both full 600-attempt comparisons are complete; all failed attempts remain scored and both archived analyses reproduce offline.
- [x] Current report replaces the older 200-call results with two-model acceptance, SAT/UNSAT, difficulty, paired uncertainty, optimality, extraction, wording and resource analysis.
- [x] Three grouped bar charts derive from the saved summary, with exact denominators and consistent scales.
- [x] Report covers formulation, design, related work, limitations, responsible AI, reproducibility and disclosed AI assistance.
- [x] Two original replay archives are included in the repository and checksum-verified; fuller source/operational/historical evidence has a private verified backup.
- [x] Public report rendered and all eleven pages visually inspected: title page 1, nine body pages 2-10, references page 11. Text, mathematical subscripts and compact figure labels are at least 11 pt, with one-inch margins and a single column. The [format receipt](../results/summary/submission-report-format.json) binds this check to exact bytes.

The previous report and format check are historical. Every substantive revision, new figure or private-title edit requires an appropriate fresh render/check; do not reuse a previous page count for a changed document.

## Genuine actions still required before submission

- [ ] Check actual proposal receipt/feedback and current Canvas arrangements; the proposal was mandatory for a project grade (Guidelines P37/P43).
- [ ] Confirm the teaching team's interpretation of the hosted Qwen models against the frontier-model wording (Project p5 / Guidelines P25; SoCLaaS/open weights suggested in Project p6 / P33). No automatic approval or rejection is inferred.
- [ ] Members review the natural-language/gold meaning, reference assumptions and failure examples, and record actual findings in [contributions.md](contributions.md) and the [claim index](claim-evidence.md).
- [ ] Each member supplies a factual account of their own work, decisions, findings and AI-supported parts, and interprets/reviews the complete report (Guidelines P56-60/P87-88). Replace the interim contribution paragraph only with confirmed facts. Disclosure alone does not establish substantive human work or understanding; follow [planning S2-S3](../planning.md#5-current-task-queue-and-acceptance-evidence).
- [ ] Add each member's name, matriculation number and email to the **private** submitted title page (P51); do not put private identifiers in public Git.
- [ ] Produce the actual presentation/deck or requested recording and rehearse **15 minutes plus five-minute Q&A** (P47). All members understand the whole system (P57); a storyboard is not a completed presentation.
- [ ] Recheck the final submitted PDF: at most **10 single-spaced, single-column body pages**, at least **11 pt**, one-inch margins; title/references excluded, all substantive figures/tables included (P49/P92).
- [ ] Verify final filename/upload instructions, submit by the actual Canvas cutoff, and retain the receipt. Presentation week: **9 November 2026**; report due **13 November** (Project p8 / P13-14). **30 October** is the team's complete-draft target.

## Scientific scope and course distinctions

Constructed or downloaded instances are explicitly allowed (Project p5 / P25). The course values meaningful comparison and insight about assumptions, realism, representation and results (P84), not a prescribed accuracy, solver victory, external benchmark or extra feature count. The current report presents known synthetic/AI-assisted development evidence honestly. A fresh holdout, exactly 600 calls, independent-human prose and fixed backend were team study choices, not additional course rules.

An additional model or fresh study is conditional on actual teaching feedback or a separately agreed scientific need. If chosen, define the question, eligibility, exact protocol, new data/review and separate execution allowance first. Never relabel inspected cases as held out. The new report's scope does not resolve model eligibility or supply human review.

The appendix may contain relevant model printouts, screenshots or planning graphs (P49); these are permitted examples, not a requirement to invent a probabilistic graphical model for a CSP/COP project. The report already contains the actual system architecture and measured-result charts. Keep essential formulation, results and discussion in the counted body.

## Recommended team verification

These support a reliable handoff; the course does not prescribe these particular records or procedures. The detailed remaining-work queue is [planning Section 5](../planning.md#5-current-task-queue-and-acceptance-evidence).

- [ ] A teammate follows [evidence.md](evidence.md) from a clean compatible environment and records the actual replay/review. Existing automated replay does not establish that human action.
- [ ] If the team wants protection against loss of this computer, copy the verified private historical bundle to approved private off-device storage and verify it there. The current same-device backup is not off-device protection.

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
.venv-docs/bin/python -m pip install reportlab==4.4.9 pdfplumber==0.11.9 matplotlib==3.10.8
.venv-docs/bin/python scripts/render_report.py
.venv-docs/bin/python scripts/check_report.py
```

The Markdown uses TeX syntax in `math` fences. Matplotlib MathText parses the equations; ReportLab embeds them as selectable vector text, so no system TeX installation is required. The checker verifies mathematical operators as well as ordinary report text. Tables show each method in its own row and preserve counts, rates, units and missing-usage coverage.

Use Poppler `pdftoppm` to render every PDF page for visual inspection. Automated bounds/text checks supplement that inspection. Report plotting and rendering are offline; no provider key is needed. For private title details, edit a separate private Markdown copy and render with `--source` / `--output`; never overwrite the public evidence with identifiers.
