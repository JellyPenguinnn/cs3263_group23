# Repository publication verification

Prepared 2 October 2026 for the user-authorized publication to GitHub `main`. This records checks of the publication worktree and preserved evidence, not course acceptance, a human review or a Canvas submission. The actual publication commit is the Git commit containing this document; original experiment source identities are unchanged.

## Implementation and integration

The current-source import was explicitly confirmed under `src/scheduling/` before testing. The experiment implementation, prompts and existing tests were unchanged during documentation finalization; a pre-edit file-hash comparison confirmed this. The previously uncommitted resilience/backend implementation is included in this publication.

| Check | Observed result |
| --- | --- |
| Full offline Python suite, current source | 784 passed; one native macOS certificate test hit sandbox `OSStatus -26276` |
| Entire TLS test module outside the sandbox | 8 passed, including the failed native test; no TLS verification weakened |
| New evidence-verifier regressions | 19 passed: hashes, membership, safe paths, case/Unicode aliases, file/parent conflicts, extraction and refusal to overwrite |
| Total Python coverage | All 804 tests passed across the main run and targeted follow-ups; not a single uninterrupted 804-test run |
| Dashboard JavaScript | Syntax check and all 9 frontend tests passed |
| Dependency consistency | `pip check` passed against the pinned runtime |
| Noneditable package | Current-source wheel built and installed in a temporary environment; `scripts/check_installed.py` verified prompts, issuer certificate and dashboard assets |
| Fresh offline demo | 180/180 canned attempts completed and replayed; 174 accepted, six intentionally invalid; zero model calls |

Representative commands, after the locked runtime is available:

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider
PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider tests/unit/test_provider_tls.py
PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider tests/unit/test_evidence_archive.py
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
.venv/bin/python -m pip check
.venv/bin/python scripts/check_installed.py
.venv/bin/python evaluation/offline_demo.py runs/NEW-offline-demo
```

The TLS follow-up used the same module outside the sandbox, not a new provider call. The temporary wheel environment reused already installed pinned dependencies without downloading them. Current publication checks ran on macOS ARM64. Historical Linux checks remain evidence only for their exact source versions; the repository's CI matrix targets macOS and Ubuntu. Native Windows remains unqualified because runtime locking uses POSIX `fcntl`. A remote CI pass must be observed separately, not inferred from local tests.

## Evidence and report

- Both committed original replay archives passed their outer SHA-256, exact membership and all **941 inner file hashes each**; 600 attempts per model, no omitted failures.
- Both archives were freshly extracted into a new audit directory. Analysis ran against **each archive's own source** with the preserved compatible runtime and **every JSON analysis field matched** the archived result.
- A separate private archive preserved **10,811 original files**. All member hashes and original bytes were rechecked unchanged; see [evidence.md](evidence.md) for coverage and same-device limits.
- The report's supplementary SAT/UNSAT and difficulty tables were regenerated from the verified archives. All twelve acceptance bars match the unchanged portable summary.
- All three standalone charts and their PDF exports were checked; compact report charts retain at least 11-point labels at the embedded size.
- The report rendered to **10 total pages: one title, eight body, one references**. All pages were rendered and visually inspected with no clipping/overlap found. Automated checks verified 107 visible source chunks, three chart images, at least 11-point text and one-inch margins. The [format receipt](../results/summary/submission-report-format.json) records exact source/PDF hashes.
- The current report and bibliography were checked against the course sources and primary literature. Its measured claims were independently cross-checked against the saved analyses; actual member interpretation/approval remains pending.
- Active local links, figure paths, syntax, final diffs and credential/private-key patterns were checked. Historical path strings inside immutable receipts were retained.

No new model inference was performed for this finalization. These results support a working, reproducible research repository and a complete report for member review. They do not establish teaching-team approval of the hosted models, human authorship/review, presentation delivery, independent teammate reproduction or course submission.

## Publication and future changes

Publish without force after verifying the destination and ancestry; verify the resulting `origin/main` SHA against the local commit. The GitHub commit and its files are the publication record. Keep private identifiers, local operational-path manifests, credentials and environments outside Git. The historical evidence bundle remains private; the two complete scientific replay packages are in the repository.

For later source/semantic changes, test the affected contracts and assess whether reported findings change. Do not overwrite the preserved run archives or rewrite their source identity. For later report edits, rerun `scripts/check_report.py` and inspect the rendered pages; a new PDF cannot inherit this one's format receipt.
