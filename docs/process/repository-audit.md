# Detailed repository audit — 18 October 2026

This review follows published commit `a43747c549fe61623aadfb55307dec5f3beb022c`. It examines implementation and operational paths, in addition to the earlier report/navigation review. The fixes and verification below are included in the authorized audit/cleanup publication; they do not alter the completed experiments. The publication commit identifies this revision.

## Coverage

The [path inventory](../../results/summary/repository-path-audit-20261018.json) records the pre-cleanup audit of the base revision's 517 tracked paths, their inspected hashes, structural checks and review categories. New audit/support files are listed separately. The later [documentation cleanup receipt](../../results/summary/documentation-cleanup-20261018.json) maps retired and relocated paths; the earlier inventory is a point-in-time record, not a current-path manifest. Every production Python module and operational entry-point script was read across the formal-method, experiment-operation and documentation/tooling reviews. Relevant callers and regression tests were checked. Test execution covers contracts that cannot be established by reading alone.

| Area | Concrete review |
| --- | --- |
| Schema and formal method | Integer slots, half-open intervals, resource/participant non-overlap, availability containment, deadlines, fixed starts, precedence, repair identity and lexicographic objectives |
| Solver and independent validator | CP-SAT compilation, independent arithmetic checking, proof bounds, extraction diagnostics, saved-result explanation and CLI dispatch |
| Both LLM pipelines | Public request boundary, strict output parsing, canonical extraction, model identity, provider accounting, TLS, no silent retries and failure classification |
| Evaluation and datasets | Controlled/balanced/diverse construction, feasibility certificates, pairing, conditional objective denominators, source/configuration manifests, replay and analysis |
| Long-running operations | Qualification, preparation, supervision, resume, parallel execution, repeated concurrency reduction, immutable completed records and request budgets |
| Dashboard and packaging | Read-only endpoints, frontend state, installed prompts/static/TLS assets, noneditable wheel, supported CLI and offline demonstration |
| Documentation and delivery | Active relative paths, historical snapshots, report/figure tooling, scientific versus document dependencies, CI checks, private-report exclusion and evidence preservation |

All tracked Python files parse; JSON and TOML files parse; all text files decode. No tracked symlinks or case/Unicode-normalized path collisions were found. All 58 PNG files decode, and all 59 PDF files have readable pages. Binary readability is not a claim that every historical page was visually reviewed. No missing nonhistorical Markdown path targets were found. The 111 unresolved links are original-location references inside preserved historical snapshots; the [history guide](../history/README.md) explains how to use those records without rewriting their bytes.

## Defects corrected

1. **Repeated concurrency reduction:** the first continuation preserved summaries under `prior-phase/`, but a second reduction collided with that existing directory. Later phases now get distinct directories while retaining the original first-transition layout. A regression exercises 16 → 8 → 4, preservation of both prior phases, retained 429 failures, accounting and no duplicate mocked requests. The completed published campaigns each used only one reduction, so their results do not require correction.
2. **Saved-explanation numeric boundary:** converting an arbitrarily large JSON integer through `math.isfinite` could raise `OverflowError`. Integer finiteness now avoids float conversion; the existing exact-range proof check still refuses unsupported proof claims. Positive and negative oversized values and bounds are covered.
3. **Dashboard label:** the UI always said “Sequential” even for parallel recordings. It now says “Recorded attempts · read-only”; regression checks cover different pending-request counts without inferring concurrency from that count.
4. **Verification/reproduction gaps:** CI now checks all four evidence manifests and builds/checks the report in a separate pinned document environment. Figure instructions use fresh output directories, and the timetable renderer accepts `--output`. The scientific dependency lock is unchanged. A stale pipeline-package docstring was corrected.

These changes do not change scheduling semantics, cases, prompts, metrics, recorded results or historical source snapshots. Future live campaigns must prepare new source-bound packets; archived runs continue to use their preserved source and manifests.

## Verification

**The complete suite passed: 1,031 tests in one uninterrupted run (1,527.09 seconds), using a fixed source snapshot and a freshly installed noneditable wheel.** All 227 runtime, test, prompt, configuration and benchmark files checked against that snapshot match the current checkout. The companion receipt records the tested wheel hash, per-module test counts and verification results.

- Focused regressions: 80 explanation/proof/CLI checks, 53 continuation/campaign checks and ten frontend checks passed.
- A newly built, noneditable wheel passes installed-asset verification and dependency checks. Its offline demonstration completed and replayed 180 attempts: 174 accepted and six intentionally invalid, with no live requests.
- All eight evidence archives and all 9,186 checksum-covered members passed fresh verification. The reconstructed 4,000-attempt comparison summary is byte-identical to the saved summary. All 283 checked existing input, result, report-asset, historical and lock/configuration paths retain their original bytes.
- A clean document environment builds and checks the report: one cover, ten body pages and one references page. All 12 rendered pages are pixel-identical to the published PDF at the comparison resolution. Regenerated chart/timetable data match the saved sources, and the images were visually checked; image bytes can differ with rendering dependencies, so preserved published assets were not replaced.
- CI YAML parses. Its commands were checked locally; an Ubuntu or remote GitHub Actions pass is not inferred from macOS checks.

Two earlier in-progress full-suite attempts were interrupted and are not counted as successful validation. One used the sandbox, and source edits overlapped the other. The final run uses a fixed source snapshot and the installed package, avoiding source-bound fixture invalidation.

## Boundaries and remaining work

This engineering audit covers implementation and automated verification. It does not include manual semantic review of every natural-language case. Automated validity, correct extraction and faithful natural-language interpretation remain distinct. The synthetic construction limitations, infrastructure exclusions, timing caveats and course/TA scope differences already stated in the report remain in force.

At this 18 October audit, the [submission checklist](submission-checklist.md) tracked case review, contributions, scope, presentation and submission; the [publication log](publication-verification.md) records their final state. No new model calls were made. Private reports, student identifiers, credentials and local run directories remain excluded from Git.
