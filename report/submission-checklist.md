# Report and submission acceptance checklist

Working checklist, 1 October 2026. This records what remains to be evidenced; an
unchecked item is not a claim that a member failed to do it. Fill review dates and
receipts only from actual actions. The editable source is [study-draft.md](study-draft.md),
with [claim evidence](claim-evidence.md), [contributions](contributions.md), and
[presentation preparation](../presentation/rehearsal.md).

## Authority and current boundary

The supplied *CS3263 Project Guidelines AY2026/27* is authoritative together with
confirmed Canvas updates. Paragraph references below identify the extracted
original, not new rules created by this checklist. The proposal's second page
sets the generation/repair and controlled/realistic/wording direction. Exact case
counts, independent-human prose policy, backend-fingerprint policy and frozen-run
machinery are team choices; approved changes must be documented honestly.

Current evidence consists of an implemented development system, preserved live
SoCLaaS development comparisons and offline final-study preparation. The report
source includes methods, worked examples, 200-call results and responsible-AI
analysis. Neither it nor this checklist establishes a final eligible-model study,
actual human review or a completed deck/rehearsal. The development PDF has a
separate verified format check below; the eventual submission still needs its own audit.

## Verified development-draft rendering

The 1 October development PDF has **nine pages: title page 1, seven body pages
2–8, and references page 9**. All nine pages were rendered and visually inspected.
Text extraction verified every visible source paragraph/table cell/diagram label
(121 chunks); the PDF has at least 11-point text throughout and every text bounding
box lies inside 72-point (one-inch) margins. Body text uses 11-point Times with
12.5-point leading, one column and modest paragraph spacing. The architecture
figure derives its labels/edges from the Markdown Mermaid source. External
reference links remain clickable. No model result or human review is created by
this layout check.

`study-draft.md` remains canonical. The renderer supports its current Markdown
subset and rejects unsupported code fences or a changed diagram node set. Rebuild
after edits and review all pages again; do not reuse this page count for a changed
report. `output/pdf/study-draft-format.json` records this build's source/PDF hashes,
page geometry and text-completeness counts. It is a derived local audit artifact.

Optional document tooling, separate from the scheduling runtime, uses
`reportlab==4.4.9`. From the repository root, in a dedicated environment:

```sh
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install reportlab==4.4.9
.venv-docs/bin/python scripts/render_report.py
mkdir -p tmp/pdfs
pdftoppm -r 100 -png output/pdf/study-draft.pdf tmp/pdfs/study-draft-page
```

The verified build used the bundled Python with that ReportLab version; no
production dependency was added. Poppler supplies `pdftoppm`. Optional extraction
checks used `pdfplumber==0.11.9` and `pypdf==6.10.0`. A local Poppler Fontconfig
configuration was needed for this host's bundled renderer; that environment fix
is not a change to the report or its runtime requirements.

## Before the frozen study

- [ ] Record the selected final model/provider/access and evidence of frontier-model
  eligibility or actual teaching-team acceptance. Guidelines P25 requires the
  comparison; P33's SoCLaaS option does not automatically waive it.
- [ ] Complete the exact model/configuration qualification within a newly authorized
  cap and resolve the retained execution-policy stop. Selecting `qwen3.8:27b` for
  development is not this final decision.
- [ ] Decide prompt, construction policy, achieved family/label/event allocation,
  study size and optional repeats before final outcomes. Retain all development
  exclusions and candidate rejections.
- [ ] Draw and independently review fresh final gold/text pairs, including realistic
  provenance and semantically equivalent wording. Automated checks do not record
  human authorship or interpretation.
- [ ] Freeze compatible blocks, analysis definitions, resource limits and actual
  approval references; rehearse the reviewed packet without model calls.
- [ ] Execute only the approved study; retain errors and uncertain requests. No
  replacement, tuning or relabelling after results while claiming untouched holdout.

## Report evidence and human review

- [ ] Final canonical outcomes retain task/label denominators, paired families,
  uncertainty and every failure. Keep development, realistic and wording conditions
  identifiable; no double-counting canonical observations.
- [ ] Review repair objectives and conditional gaps; prove reference optima or state
  bounds/unresolved status. Include the coupled-repair worked example.
- [ ] Explain at least one meaningful extraction failure and the distinction between
  structural mismatch, equivalent encoding and gold validity.
- [ ] Supply paired wording results and limitations, or explicitly revise the proposal
  scope rather than silently omit the promised condition.
- [ ] Interpret difficulty, generator assumptions and tool availability/translation
  limitations. Guidelines P84 rewards analysis and insight, not a target score or
  compulsory extra ablation/model/public dataset.
- [ ] Review the four responsible-AI discussions in the source. Connect each harm,
  mitigation and residual limit to actual evidence or clearly labelled design
  scenarios (P35); do not invent an evaluated user interaction.
- [ ] Each member personally reviews mathematics/meaning, interprets results and
  revises the report. Record actual work and AI assistance; all can explain the
  whole project (P56–60, P87–88). Approval tokens or branch names are insufficient.
- [ ] A teammate replays the reviewed archive without credentials and checks the
  claim-to-table/figure mapping. Record environment, command, result and reviewer.
- [ ] Verify original references, paraphrases and attribution (P58–59); finish the
  literature synthesis, including the proposal's scheduling/wording motivation.

## Format, presentation and delivery

- [ ] Inspect the rendered final document: at most ten body pages, single-spaced,
  single-column, one-inch margins, at least 11-point font. All substantive discussion,
  tables and figures count; title and references are excluded (P49/P92). An appendix
  may hold permitted supporting outputs, not displaced essential discussion.
- [ ] Use readable equations/figures, a coherent argument and language for classmates
  with general AI knowledge (P53). Remove unresolved editorial notes only when
  resolved; never disguise them as completed results.
- [ ] Place every member's name, matriculation number and email on the private
  submission title page (P51); do not add private identifiers to public Git.
- [ ] Produce the actual presentation/recording, assign speakers and rehearse
  15 minutes plus five minutes of Q&A (P47). Every member explains beyond their own
  component; label development and recorded/canned demonstrations accurately.
- [ ] Verify the mandatory September 28 proposal submission/receipt privately (P37/P45)
  and read actual feedback; missing repository evidence does not imply non-submission.
- [ ] Finish a complete draft by the internal October 30 target; use November 2–6
  for cross-review/rehearsal. Confirm Canvas presentation arrangements for the week
  of November 9 and the precise final-report cutoff on November 13.
- [ ] Upload the audited report early enough to verify receipt, targeting November 12;
  verify required presentation delivery. Retain actual receipts privately.

## Review record template

For each completed review, record: date; reviewer; artifact version/commit and claim
IDs; check performed; evidence or reproduction command; finding/correction; and
any remaining limitation. Do not fill this template with inferred actions.
