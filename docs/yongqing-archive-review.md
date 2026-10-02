# Yong Qing F5 archive verification — 1 October 2026

`yongqing-evaluation` now incorporates GitHub main `80df71f` by fast-forward from
`daae194`, including Li Hao's provider diagnostic and Yao Xiang's independent formal
review. Existing work and historical archives are preserved. The user subsequently
authorized committing and pushing this checkpoint to `yongqing-evaluation`. Main
integration, new inference and final freeze remain separate. The verification
receipt retains its original pre-publication status.

## Planning audit and completed correction

F3 construction, F4 rehearsal and F5 analysis/archive were already implemented.
Yao Xiang's arithmetic review independently supports the preserved pilot's witnesses
and contradiction mechanisms, with six bounded optimum checks. It does not supply
human wording/gold review or make that development packet final data. With final
model/policy decisions still open, the next unblocked task was F5 archive integrity.

The exporter verified saved request hashes against the installed prompts, but then
copied prompt files from the checkout without comparing them. A changed checkout
could therefore create an archive whose prompts differed from the verified run.
It also followed links in project inputs, included unrelated prompt text files,
and accepted a lockfile whose pins differed from the recorded runtime. Nine
negative regressions reproduced these gaps before the fix.

[The existing exporter](../src/scheduling/evaluation/study.py) now:

- Checks all three checkout prompt templates against the active pipeline builders.
- Requires the lockfile pins to match every dependency version recorded by the run.
- Rejects linked files or linked parent directories in the included inputs.
- Includes only the three declared prompt files, excluding unrelated prompt notes.
- Snapshots verified source/run bytes before writing output, so failed integrity
  preflight creates no export directory and later copying cannot substitute unchecked bytes.

The public function/CLI and archive/analysis formats are unchanged. This is a
correction to Yong Qing's export boundary; no shared pipeline, prompt, model,
solver, metric or scientific protocol was changed. The lock check covers recorded
runtime dependencies, not unknown historical build metadata. Exact file checksums
and a real archive installation/replay remain part of verification.

## Evidence actually observed

| Check | Result |
| --- | --- |
| New negative regressions before fix | Nine failed, demonstrating the gaps |
| Focused frozen-block/export tests after fix | 20 passed |
| Complete installed macOS suite | 623 passed in 54.86 s |
| Complete installed Linux ARM64 suite | 623 passed in 48.19 s |
| Installed assets and dependency checks | Passed on both platforms |
| New synthetic frozen rehearsal | 16 attempts, including one deliberately rejected output |
| Archive installation and offline replay | All 77 archived file checksums verified; every analysis field reproduced exactly in a separate Linux environment |
| Network isolation | Linux container configured with network mode `none` |
| Previous frozen rehearsal/archive | Full serialized analysis unchanged; archive checksum unchanged; its three prompts and lock match their preserved project inputs |

Linux reused the locked dependency environment and rebuilt/installed the current
package offline; the archive was then installed separately from its own source.
This is automated portability/reproduction evidence, not an independent human
teammate review. The rehearsal uses canned outputs and synthetic approval fixtures;
15 accepted outputs out of 16 are not a model-performance score. Zero model calls.

The previous archive had matching inputs, so the potential export gaps do not
invalidate its recorded results. The actual earlier archive and analysis remain
unchanged. Historical analysis readers still work. Since the package source has
changed, new execution needs a new run identity; do not resume an earlier frozen
run with altered source or overwrite its evidence.

The [verification receipt](../configs/development/yongqing-archive-verification-20261001.json)
records source/log hashes, archive checksum and limits. New local archive:
`runs/yongqing-archive-rehearsal-20261001-01/analysis/reproduction.tar.gz`.
A fresh clone can repeat the canned rehearsal without credentials; it cannot
recover unavailable raw live records merely from summaries.

After the documented noneditable installation:

```sh
.venv/bin/python -m pytest -q tests/integration/test_study_blocks.py
.venv/bin/python evaluation/rehearse_study.py runs/NEW-archive-rehearsal
```

Extract a reviewed archive, verify `CHECKSUMS.json`, and follow its `REPRODUCE.txt`.
The archived `analyze_study.py ... --no-archive` path performs saved-evidence replay
without model calls. Keep original runtime/source archives for historical evidence.

## Remaining assigned work and next task

| Work package | State after this checkpoint |
| --- | --- |
| F1 review support | Failure regressions exist; the one prompt experiment waits for model qualification and a new cap |
| F3 | Construction and automated formal checks exist; actual human gold/wording review, policy/size choice, exclusion completeness and fresh draw remain open |
| F4 | Synthetic rehearsal verified; actual model eligibility, reviewed protocol and final execution allowance remain open |
| F5 | Export integrity and portable replay verified; final-study analysis/archive and actual independent teammate replay remain open |
| F6 | Evidence and contribution index updated; final findings, human interpretation, report format, rehearsal and submission remain open |

The next concrete team task is to review the existing candidate-policy packet and
Yao Xiang's mathematical examples, settle the actual final provider/model and
study size, then authorize the fresh draw and review it before final inference.
SoCLaaS remains for development; the intended official-provider submission API is
not yet selected or integrated. The paused SoCLaaS comparison has no new allowance.
Optional repeat mapping, external datasets, feedback, solver optimization and UI
expansion remain deferred. No missing scientific decision is replaced by a mock,
a fabricated review reference or an extra feature.
