# Evidence preservation and offline replay

The latest [diverse comparison](diverse-comparison-audit.md) has **2,000 attempts per model**, with every one of the 4,000 saved evaluations reproduced offline. Original numerical and operational archives remain unchanged. Two explicitly labelled **portable derivatives** in this checkout redact only local campaign paths and update dependent metadata checksums; all attempts, cases, references and scientific source remain byte-identical. They contain final outputs and available metadata, not complete HTTP traffic or hidden reasoning.

## Diverse 2,000-attempt evidence

[The manifest](../results/diverse-evidence-manifest.json) binds both portable archives, each with 3,077 checksummed files and 3,054 unchanged scientific members. The internal `PORTABLE-DERIVATIVE.json` lists every local-path transformation, original archive digests and preserved historical hash semantics. `analysis-with-execution-provenance.json`, `timing-by-execution-segment.json` and `timing-comparability.json` retain the OS/concurrency differences. Original same-device operational archives remain private; this is not an off-device backup claim.

```sh
python3.12 scripts/verify_evidence.py --manifest results/diverse-evidence-manifest.json \
  --extract-to runs/NEW-diverse-replay
.venv/bin/python scripts/build_diverse_comparison.py --manifest results/diverse-evidence-manifest.json
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/render_diverse_results.py
```

For exact-source replay use each archive's `REPRODUCE.txt`, frozen `source/`, `blocks.json` and `analysis.json` in a new directory. Follow the installation procedure below, substituting the extracted `qwen36` and `glm53flash` directories. Replay uses no API key or inference. Its scientific scores match the saved records exactly; portable analysis metadata intentionally refers to the redacted manifest hash rather than the original manifest hash.

The previous balanced report/PDF, active documentation and format receipt are preserved in [report history](history/20261018-before-diverse/). Earlier balanced, difficulty and historical studies retain original byte-for-byte archives and separate scores; they are not pooled into the diverse dataset.

## Balanced 96-attempt evidence

Each archive contains **96 scheduling records and 211 checksum-covered files plus `CHECKSUMS.json`**. These are the original completed-run archives, copied byte for byte. [The manifest](../results/balanced-evidence-manifest.json) records exact SHA-256 values and sizes. No failures were removed, corrected or rerun. The summary and chart source is [balanced-comparison-20261017.json](../results/summary/balanced-comparison-20261017.json).

```sh
python3.12 scripts/verify_evidence.py --manifest results/balanced-evidence-manifest.json \
  --extract-to runs/NEW-balanced-replay
.venv/bin/python scripts/build_balanced_comparison.py
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/render_balanced_results.py
```

For exact-source replay, follow the installation/replay procedure below in each newly extracted `qwen36` and `glm53flash` directory, rather than the historical `qwen38` directory. Use its `blocks.json`, archived `source/` and `analysis.json`. The scientific replay makes zero model calls. Fresh replay of both balanced archives reproduced the complete saved analyses exactly after JSON serialization; tuples in in-memory Python values serialize as JSON arrays.

The complete balanced operational evidence is retained in a separate private same-device backup containing **483 regular files**, including capabilities, request accounting, supervisor receipts, packets, source snapshot and the built wheel. Its SHA-256 is `cf0baa9a297716065227ecfd8400aa378b6ae7d3e86e6691deb1eebac729554d`. The Python environment is retained at the original run location rather than duplicated in that backup. Local paths and credential-file locations remain private. This is preservation, not proof of off-device backup or human review.

## Earlier 200-attempt difficulty evidence


The new pair is preserved separately from the historical archives below. Each original archive contains **200 scheduling records and 364 checksum-covered files plus `CHECKSUMS.json`**. Both fresh exact-source replays reproduced every saved analysis field. The [comparison audit](difficulty-comparison-audit.md) explains the protocol and failures; [validation](../results/summary/difficulty-run-validation-20261014.json) records completion and request accounting.

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| [Qwen3.6](../results/archives/difficulty-200-qwen36-20261014.tar.gz) | 3,220,580 | `dfd5c3dfaa8693f8265663dc8692a38984233c649dd478addc2ef87d54539a42` |
| [GLM5.3 Flash](../results/archives/difficulty-200-glm53flash-20261014.tar.gz) | 1,998,959 | `f35edfd47ddb4fd90c6715780cc38b208d392fd5b304d8a6d0174a2b95c8ae1e` |

Verify or extract into a new directory with the separate [difficulty manifest](../results/difficulty-evidence-manifest.json):

```sh
python3.12 scripts/verify_evidence.py --manifest results/difficulty-evidence-manifest.json
python3.12 scripts/verify_evidence.py --manifest results/difficulty-evidence-manifest.json \
  --extract-to runs/NEW-difficulty-replay
```

Inside each extracted `qwen36/` and `glm53flash/` directory, create a Python 3.12 environment, install that archive's `source/requirements.lock` and source, then replay exactly as in the historical example below (`source/evaluation/analyze_study.py blocks.json replayed-analysis --development --no-archive`). Compare the entire saved and new `analysis.json`. These are offline scoring operations; do not invoke the live runner. Do not install a later checkout in place of archived source.

Rebuild the current derived summary with `scripts/build_difficulty_comparison.py` and charts with `scripts/render_difficulty_results.py`. [Standalone](../results/figures/difficulty-comparison-20261014/figure-data.json) and [report](figures/difficulty-comparison-20261014/figure-data.json) receipts bind figure bytes and source data. The [previous report](history/20261002-report/submission-report.md), PDF, embedded figures and format receipt remain in `docs/history/20261002-report/`.

The completed Qwen campaign, completed GLM rerun, stopped 22-attempt GLM campaign, packets and full frozen source remain untouched in the custodian's original local run directory. A separate private comparison-audit directory records their preservation hashes and replay outputs, with a [portable preservation receipt](../results/summary/difficulty-preservation-verification-20261014.json); no operational paths or credentials are published. The stopped campaign is not mixed into the successful rerun. Portable archives preserve the scientific records; original operational receipts remain separate. Same-device copies do not protect against device loss.

## Generation-first reporting and offline illustration

The [generation summary](../results/summary/generation-focus-20261015.json) derives scoped views from the same verified archives: all 30 controlled generation cases per model, its 12-case small subset and the completed extensions. Every view records exact observation IDs. This post-run hierarchy changes neither the experiment nor its scoring; overlapping views must not be summed. Rebuild with `scripts/build_generation_focus.py`; generate new charts using `scripts/render_generation_focus.py` (add `--report --output docs/figures/generation-focus-20261015` for the report layout). Each layout saves a source/renderer/output hash receipt.

The previous combined-scope report, PDF, figures and format receipt are preserved in [history/20261014-report](history/20261014-report/submission-report.md). Earlier result summaries, figures, fixtures, prompts and live-run evidence remain unchanged. The current report format receipt is refreshed for the new PDF.

The [office illustration](../results/summary/ta-scope-examples-20261015.json) is separately generated by `evaluation/ta_scope_examples.py`; it contains three generation examples and one repair, all offline with zero model calls. It is not included in any model-performance denominator. See [the alignment](ta-feedback-alignment.md) for exact scope differences and independent checks.

## Historical 600-attempt Qwen evidence

| Archive | Size | SHA-256 |
| --- | ---: | --- |
| [Qwen3.6](../results/archives/benchmark-qwen36-20261001-02.tar.gz) | 1,838,407 bytes | `1aa196817f7c78f55e59a68e73650df4da6f6748d55e532d2f456411b08ffb5b` |
| [Qwen3.8](../results/archives/benchmark-qwen38-20261001-04.tar.gz) | 1,682,254 bytes | `a1a70ac7566781fc6360048e5c0a10eeb9cd764d7d7fd0cd1186851284d1aa12` |

Each archive has **600 scheduling attempt records** and **941 checksum-covered files plus `CHECKSUMS.json`**. Every original failure remains. The [portable manifest](../results/evidence-manifest.json) binds file paths, sizes and hashes. Verification rejects checksum mismatch, missing/extra/duplicate members, unsafe paths and links. The committed packages passed credential/private-key/private-path inspection before publication; they contain synthetic study data.

From the repository root, verify without extraction:

```sh
python3.12 scripts/verify_evidence.py
```

Extract both into a **new** directory:

```sh
python3.12 scripts/verify_evidence.py --extract-to runs/replay-evidence
```

For exact-source replay, use each archive's own source and pinned requirements. For example, from the repository root:

```sh
cd runs/replay-evidence/qwen36
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r source/requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation ./source
.venv/bin/python source/evaluation/analyze_study.py blocks.json replayed-analysis \
  --development --no-archive
.venv/bin/python - <<'PY'
import json
from pathlib import Path
assert json.loads(Path('analysis.json').read_text()) == json.loads(Path('replayed-analysis/analysis.json').read_text())
print('Exact analysis replay matched')
PY
```

Repeat in `qwen38/`. These commands make **zero model calls**; dependency installation may require package-index access or a local wheel cache. The scientific replay itself is offline. Install the archived source rather than assume an arbitrary future checkout has identical scoring behavior. Never rewrite original records to make replay pass.

The historical report uses the [two-model summary](../results/summary/two-model-development-20261002.json), [supplemental task/label and difficulty tables](../results/summary/two-model-report-tables-20261002.json), and [historical claim index](claim-evidence-20261002.md). Rebuild the supplemental tables with `python3 scripts/build_report_tables.py`; regenerate charts with `scripts/render_benchmark_results.py`. The original aggregate retains its original audit time/status even after repository publication.

## Full historical and operational preservation

The portable archives contain the 48 source files needed for scoring/replay. A separate **private preservation bundle**, `evidence-preservation-20261002/evidence.tar.gz`, also preserves the full 230-file source snapshots, input packets, capability records, supervisor/worker receipts, pause/resume checkpoints, interrupted campaigns, previous pilots and the earlier 200-call comparison. It includes the first failed 56-attempt campaign formerly stored under `/private/tmp`.

| Private bundle property | Verified value |
| --- | --- |
| Archive bytes | 37,539,046 |
| Archive SHA-256 | `261376861781a4a71c57ab0ac2c60d9c967cc88a552b816bc4ac4dea5f700127` |
| Original files | 10,811; 181,613,871 uncompressed source bytes |
| Archive members | 10,812 regular files, including the manifest |
| Manifest SHA-256 | `c8421965eca3d10a73994d5d6a370e1695410016196864a18853f1f39d55e926` |
| Verification | Every member/hash checked; all 10,811 originals rehashed unchanged |

The bundle is stored beside the local publication worktree. Its private `MANIFEST.json` maps exact original paths to archived paths; `verification.json` records verification. The [public preservation receipt](../results/summary/evidence-preservation-20261002.json) omits local source paths. Ask the team custodian for the private archive when operational history is needed. Do not commit the private manifest or local-path-bearing logs. This local copy provides redundancy on the same machine, **not protection against device loss**; the committed two full-run replay packages provide the repository's portable scientific evidence.

The inventory excluded only environments, Python/pytest caches and `.DS_Store`. Credentials, unrelated checkout files and disposable TLS test trees were outside the selected evidence roots. No scientific attempt was excluded. An earlier uncompleted pause request stays recorded as a request; only two completed Qwen3.8 pauses are counted. Wall/monotonic clocks and unknown token usage retain their original meanings.

## Preservation rules

Do not overwrite archives, prune failed attempts, reuse their live allowance or change their original source/configuration metadata. Any corrected interpretation belongs in a new analysis/receipt with an explicit reference to the original. Any redacted shareable derivative needs its own hash and redaction note. Paths inside historical records may use the former `report/` spelling; this is source history, not an instruction to modify archived bytes.

The current repository includes documentation/rendering improvements made after the historical experiments. Both historical experiments used the same archived implementation based on Git `2f0562b` plus the then-uncommitted resilience changes. Publication does not retroactively change that recorded source identity.
