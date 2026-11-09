# Documentation

Start with the [report](submission-report.pdf). The documents below support it; earlier studies and superseded material are kept separately so their results are never pooled with the main study.

## Report

| Document | Purpose |
| --- | --- |
| [Report](submission-report.md) / [PDF](submission-report.pdf) | Question, formulation, design, results, failure analysis, limitations, responsible AI and conclusions |
| [Report supplement](report-details.md) | Resource distributions, the worked example's full inputs and outputs, and reproduction of the report visuals |
| [Claim-to-evidence index](claim-evidence.md) | Where each reported number comes from |
| [Contributions](contributions.md) | Division of work and use of AI tools |

## System and evidence

| Document | Purpose |
| --- | --- |
| [Architecture](architecture.md) | Components, data boundaries, scheduling semantics and status meanings |
| [Usage](usage.md) | Command-line tools, offline demos, dashboard, replay and live-run configuration |
| [Evidence and replay](evidence.md) | Archives, checksums and exact-source reproduction for every study |
| [TA-feedback alignment](ta-feedback-alignment.md) | How the proposal feedback shaped the scope, and what was simplified |

## Studies

The main study is the 1,000-case generation comparison; the others are earlier, separate studies with their own cases and denominators.

| Study | Protocol | Results audit |
| --- | --- | --- |
| Main study: 1,000 cases, Qwen3.6 and GLM5.3 Flash | [Protocol](studies/diverse-generation.md) | [Audit](studies/diverse-comparison-audit.md) |
| Office scenario: 48 cases | [Protocol](studies/balanced-generation.md) | [Audit](studies/balanced-comparison-audit.md) |
| Repair, wording and fictional requests: 80 cases | [Protocol](studies/difficulty-study.md) | [Audit](studies/difficulty-comparison-audit.md) |
| Historical Qwen3.6 and Qwen3.8 comparison | — | [Audit](studies/two-model-development-audit.md) |

## Reviews

- [Human-review packet](reviews/human-review-packet.md): the 24 cases the team checked by hand against their gold specifications.
- [Report quality review](reviews/report-quality-audit.md) and [course and code audit](reviews/course-code-audit.md): earlier internal reviews against the course guidelines.

## Process records

[`process/`](process/) holds the team's internal working records: the [submission checklist](process/submission-checklist.md), [human-review worksheet](process/human-review-checklist.md), [repository audit](process/repository-audit.md) and [publication log](process/publication-verification.md). They document how the work was checked; dated entries describe their own checkpoint.

## Figures and history

- [`figures/`](figures/): report artwork with data receipts, plus preserved exports from earlier studies.
- [`history/`](history/README.md): superseded reports, plans and development notes, kept byte-for-byte as historical evidence. Their statements describe their own date, not the final state.
