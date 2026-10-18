# Report and submission acceptance checklist

Current source: [submission-report.md](submission-report.md). Current PDF: [submission-report.pdf](submission-report.pdf). This publication prepares an exploratory report using the completed comparisons. An unchecked item requires real evidence; it is not permission to fabricate a review, submission receipt or human contribution.

## Prepared and verified

- [x] [Line-by-line scientific and course-requirement review](reviews/report-quality-audit.md) completed against supplied source documents, TA feedback and saved evidence. The audit distinguishes verified content from unresolved human/course obligations.

- [x] Both generation and minimum-disruption repair, direct and solver-assisted paths, independent validation and end-to-end evaluation are implemented.
- [x] The diverse 2,000-attempt/model, balanced 96-attempt/model and difficulty 200-attempt/model Qwen3.6/GLM campaigns, and historical 600-attempt/model Qwen pair, are complete. Failures remain scored; all archived analyses have reproduced offline.
- [x] Current report leads with 1,000 diverse generation cases and 2,000 attempts/model and distinguishes strict-format, reasoning and provider failures. The earlier difficulty-generation views, repair/fictional/wording extensions and historical reports remain preserved separately.
- [x] Current diverse charts and the worked timetable derive from verified archives and saved observations; previous generation/block/tier/resource figures remain unchanged. Four offline office examples demonstrate the supported scope separately from model results.
- [x] Report covers formulation, design, related work, limitations, responsible AI, reproducibility and disclosed AI assistance.
- [x] Eight replay archives (six original packages and two explicitly labelled portable derivatives) are included in the repository and checksum-verified; fuller source/operational/historical evidence has a private verified backup.
- [x] Public report rebuilt and all pages visually checked after the analysis-focused revision: one title, ten body and one reference page, at least 11-point text and compact figure labels, one-inch margins and single column. The [format receipt](../results/summary/submission-report-format.json) and [publication verification](publication-verification.md) record the exact current source/PDF and checks. The local private copy also passes its own format check and has the same body/reference pages; its title details still require member confirmation.

- [x] User-confirmed responsibility allocation recorded in the report and [division of work](contributions.md): Yao Xiang — formal methods; Yong Qing — evaluation; Li Hao — integration, experiments and quality assurance.

Earlier report snapshots and their format checks are historical. Every substantive revision, new figure or private-title edit requires an appropriate fresh render/check; do not reuse a previous page count for a changed document.

## Genuine actions still required before submission

- [ ] Verify the original Canvas feedback/receipt and current arrangements. The supplied written TA feedback has been addressed in [the alignment](ta-feedback-alignment.md); confirm the single-day/30-minute and preferred-start-only simplifications against the suggested weekly/hourly scenario. The proposal was mandatory for a project grade (Guidelines P37/P43).
- [ ] Confirm the teaching team's interpretation of the hosted Qwen and GLM models against the frontier-model wording (Project p5 / Guidelines P25; SoCLaaS/open weights suggested in Project p6 / P33). No automatic approval or rejection is inferred.
- [ ] Review diverse-study public/gold pairs across the ten families, both labels and activity counts; inspect certificates, reference assumptions and saved failure examples. Record genuine findings, corrections and generalization limits in the team’s review notes, using the [claim index](claim-evidence.md) to identify the supporting evidence. Keep earlier studies separate. Completed execution does not establish human review; use the [review procedure](report-details.md#conducting-the-human-review).
- [ ] Each member supplies a factual account of their own work, decisions, findings and AI-supported parts, and interprets/reviews the complete report (Guidelines P56-60/P87-88). Refine the responsibility allocation into personal-work statements only with confirmed facts. Disclosure alone does not establish substantive human work or understanding; use the [human-review guidance](report-details.md#conducting-the-human-review).
- [ ] Confirm each member's name, matriculation number and email on the prepared **private** title page (P51). The local `docs/private/submission-report.md` and PDF contain the supplied details and are excluded from Git. Refresh this copy after substantive report edits; never put private identifiers in public Git.
- [ ] Produce the actual presentation/deck or requested recording and rehearse **15 minutes plus five-minute Q&A** (P47). All members understand the whole system (P57); a storyboard is not a completed presentation.
- [ ] Recheck the final submitted PDF: at most **10 single-spaced, single-column body pages**, at least **11 pt**, one-inch margins; title/references excluded, all substantive figures/tables included (P49/P92).
- [ ] Verify final filename/upload instructions, submit by the actual Canvas cutoff, and retain the receipt. Presentation week: **9 November 2026**; report due **13 November** (Project p8 / P13-14). **30 October** is the team's complete-draft target.

## Suggested completion order

Confirm scope/model interpretation and gather factual member accounts while reviewing the report and preparing the presentation. Review representative public/gold cases across the ten families, activity counts and both feasibility labels; inspect the saved failure examples, conditional optima and infrastructure/timing caveats. Record actual findings using the [claim index](claim-evidence.md) and [review guidance](report-details.md#conducting-the-human-review). Then incorporate corrections and confirmed contributions, refresh the private report, check every page, rehearse the presentation and submit under the actual Canvas instructions. Optional teammate replay can proceed in parallel.

## Scientific scope and course distinctions

Constructed or downloaded instances are explicitly allowed (Project p5 / P25). The course values meaningful comparison and insight about assumptions, realism, representation and results (P84), not a prescribed accuracy, solver victory, external benchmark or extra feature count. The current report presents known synthetic/AI-assisted development evidence honestly. Sample counts, a proposed fresh holdout, independent-human prose and a fixed backend were experiment-design choices or earlier proposals, not additional course rules. The executed primary study has 4,000 attempts on known development cases with observed backend variation; none of those unperformed alternatives is claimed.

An additional model or fresh study is conditional on actual teaching feedback or a separately agreed scientific need. If chosen, define the question, eligibility, exact protocol, new data/review and separate execution allowance first. Never relabel inspected cases as held out. The new report's scope does not resolve model eligibility or supply human review.

The appendix may contain relevant model printouts, screenshots or planning graphs (P49); these are permitted examples, not a requirement to invent a probabilistic graphical model for a CSP/COP project. The report already contains the actual system architecture and measured-result charts. Keep essential formulation, results and discussion in the counted body.

## Recommended team verification

These support a reliable handoff; the course does not prescribe these particular records or procedures. The required remaining work is listed above; these additional checks are recommendations.

- [ ] A teammate follows [evidence.md](evidence.md) from a clean compatible environment and records the actual replay/review. Existing automated replay does not establish that human action.
- [ ] If the team wants protection against loss of this computer, copy the verified private historical bundle to approved private off-device storage and verify it there. The current same-device backup is not off-device protection.

## Responsible-AI review

Discuss concrete unequal inconvenience, lexicographic objective trade-offs, privacy/reidentification, ambiguous hard versus soft requirements, explanation boundaries and user control. Fixed task assignments do not establish fair workload allocation. Prompt-boundary tests do not establish live adversarial robustness. Sources: Project p7 / Guidelines P35/P62; ResponsibleAI slides 9-10, 17-20, 23-27, 30-31 and 34-35.

## Rebuild the report

The Markdown source is canonical. Create a separate document environment from the repository root; the scientific installation alone does not include all PDF libraries:

```sh
python3.12 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements-docs.txt
```

The current report figures were rendered with Matplotlib 3.10.0, while the scientific lock retains 3.10.8. The separate environment preserves that distinction. Follow the [fresh-output reproduction commands](report-details.md#reproducing-the-report-visuals) to reconstruct resources, figures and PDF without overwriting published artifacts. The normal PDF build reuses the preserved Mermaid vector asset; Mermaid CLI and Chrome are needed only for an intentional architecture change.

After reviewing a deliberate report edit, regenerate the public report and its format receipt with `.venv-docs/bin/python scripts/render_report.py` and `.venv-docs/bin/python scripts/check_report.py`. Those defaults replace the current public derivative, so review the diff and rendered pages before publication. Keep prior evidence and dated snapshots unchanged.

The Markdown uses TeX syntax in `math` fences. Matplotlib MathText parses the equations; ReportLab embeds them as selectable vector text, so no system TeX installation is required. The checker verifies mathematical operators as well as ordinary report text. Tables show each method in its own row and preserve counts, rates, units and missing-usage coverage.

Use Poppler `pdftoppm` to render every PDF page for visual inspection. Automated bounds/text checks supplement that inspection. Report plotting and rendering are offline; no provider key is needed. For private title details, edit a separate private Markdown copy and render with `--source` / `--output`; never overwrite the public evidence with identifiers.
