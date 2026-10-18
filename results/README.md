# Evaluation evidence

The primary study contains **1,000 generation cases × two methods × two models = 4,000 scheduling attempts**. Qwen3.6 and GLM5.3 Flash each have 2,000 attempts. All failures are retained. Earlier designs remain separate; do not pool their scores.

| Study | Scheduling attempts per model | Manifest | Comparison |
| --- | ---: | --- | --- |
| Diverse generation — primary | 2,000 | [Diverse](diverse-evidence-manifest.json) | [Summary](summary/diverse-comparison-20261018.json) · [Audit](../docs/diverse-comparison-audit.md) |
| Balanced generation — earlier | 96 | [Balanced](balanced-evidence-manifest.json) | [Summary](summary/balanced-comparison-20261017.json) · [Audit](../docs/balanced-comparison-audit.md) |
| Difficulty and wording — earlier | 200 | [Difficulty](difficulty-evidence-manifest.json) | [Summary](summary/difficulty-comparison-20261014.json) · [Audit](../docs/difficulty-comparison-audit.md) |
| Historical Qwen3.6/Qwen3.8 | 600 | [Historical](evidence-manifest.json) | [Audit](../docs/two-model-development-audit.md) |

## Where to look

- `archives/`: immutable replay packages bound by the manifests. Diverse archives are explicitly labelled portable derivatives; original records and provenance remain preserved.
- `summary/`: offline analyses, engineering checks and version-specific verification receipts. Dates/hashes identify each checkpoint; old status statements are historical.
- `figures/`: preserved standalone study exports. The current report/README charts are in [`docs/figures/report-polished-20261018/`](../docs/figures/report-polished-20261018/), with their own data/hash receipt.
- Ignored `runs/` at the repository root: local execution, extraction and reproduction outputs. These are not public evidence unless separately reviewed and packaged.

Start with the [README reproduction commands](../README.md#reproduce-the-evidence) and [evidence guide](../docs/evidence.md). Verify manifest checksums before reading extracted evidence. Write new analyses and plots to fresh local paths and compare with preserved outputs; never overwrite attempts, archives or historical summaries to improve a result. Offline verification/replay needs no provider credentials or model calls.

Statistics and interpretation boundaries are documented in the [report](../docs/submission-report.md), [supplement](../docs/report-details.md) and [claim index](../docs/claim-evidence.md). Acceptance, optimality, extraction fidelity, operational reliability and human review are distinct claims.
