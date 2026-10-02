# Evidence preservation and offline replay

The two complete comparisons are preserved as **original, byte-for-byte reproduction archives in Git**. They contain recorded final model content, public inputs/prompts, extracted specifications and schedules, solver/reference results, failure/usage metadata, exact replay source and analysis. They are not complete raw HTTP captures or hidden reasoning traces.

## Checked-in complete-run evidence

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

The report additionally uses the [two-model summary](../results/summary/two-model-development-20261002.json), [supplemental task/label and difficulty tables](../results/summary/two-model-report-tables-20261002.json), and [claim index](claim-evidence.md). Rebuild the supplemental tables with `python3 scripts/build_report_tables.py`; regenerate charts with `scripts/render_benchmark_results.py`. The original aggregate retains its original audit time/status even after repository publication.

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

The current repository includes documentation/rendering improvements made after the experiments. Both experiments used the same archived implementation based on Git `2f0562b` plus the then-uncommitted resilience changes. Publication does not retroactively change that recorded source identity.
