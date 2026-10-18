# Integrated version 2 validation

The current system is a runnable development implementation of the proposal's direct-LLM versus LLM-to-CP-SAT study, including generation and minimum-disruption repair. All three members' components and the planned R1–R4 engineering capabilities are integrated. Two integrity defects identified during the final review are corrected. The software is ready for final-study preparation; human review, final-model eligibility/qualification and the approved held-out study remain outstanding.

## Changes and compatibility

1. **Bind explanations to their inputs.** A saved optimal result for a more constrained specification could previously be attributed to a different specification when its candidate happened to remain feasible with the same objective. Every new `SolveResult` now records a versioned exact specification/repair-context digest. The shared explanation formatter rejects mismatches, including changed repair contexts and stale infeasibility reasons. Legacy standalone files still support candidate validation but cannot establish proof correspondence. Historical checked-run consumers retain their case/record context and exact score replay. Hash correspondence is not authentication of arbitrary evidence.
2. **Exclude calendar-only development duplicates.** The previous hard-structure fingerprint included literal calendar origin/timezone. Changing these fields could let the same integer-slot scheduling problem evade a development registry. `slot-graph-v2` fingerprints ignore calendar presentation while retaining slot dimensions and the constraint graph. Exact input/provenance hashes still preserve dates and timezones. New frozen execution requires protocol 2.0, a current-version benchmark manifest and a typed registry; legacy protocols/raw digest lists cannot silently enter new runs.
3. **Rebuild exclusions from actual sources.** The new [versioned registry](../benchmarks/manifests/development-hard-fingerprints-v2-20260930.json) records 300 known structures from 22 named bundles, covering full v1/v2/v3 matrices, authored drafts and saved pilots, including original and updated repair problems. Recomputing the old algorithm against those sources recovered all 300 previous registry entries, with none missing. The old registry remains unchanged. `evaluation/development_registry.py` rebuilds from explicit bundles or named archive members and refuses to overwrite an existing output. Named-source coverage does not establish completeness for private/unregistered development work.
4. **Reconcile documentation.** README now introduces current capabilities, architecture, data origins, qualified commands, results and limitations. Planning distinguishes completed engineering contracts from current human/scientific gates; AGENTS explains the evidence/version boundaries and continuing workflow.

No prompt, provider/model setting, mathematical objective, dependency lock, benchmark source case or historical score was changed. Optional search optimizations, external-data adapters, extra models and feedback remain optional scope decisions. Changes to source contracts mean previous runs are replayable but cannot be resumed with the modified build; retain their original environment for continuation. No production frozen study exists to migrate.

## Verified source and environment

[The machine-readable receipt](../configs/development/version-2-verification.json) records the published base `63d68d8f594974e7204e7c096c110d637f9415e5`, exact qualified runtime/test/fixture hashes, dependency and environment details, and verification commands. Checks used fresh **noneditable** installations of the working source with locked, hashed dependencies. The receipt identifies source independently of an eventual publication commit; documentation finalization after qualification does not change tested code.

| Check | macOS ARM64 | Linux ARM64 |
| --- | ---: | ---: |
| Python suite | 521 passed | 521 passed |
| Frontend tests | 7 passed | 7 passed |
| Installed prompts/certificates/dashboard assets | Passed | Passed |
| Dependency consistency and JavaScript syntax | Passed | Passed |
| Legacy canned workflow | 180 attempts; 174 accepted, 6 deliberately invalid | Same |
| Structural v2 canned workflow | 144 cases, 864 attempts | Same |
| Challenge v3 canned workflow | 108 cases, 648 attempts | Same |
| Authored canned workflow | 12 cases, 24 attempts | Same |
| Historical aggregates replayed exactly | 4 runs / 132 attempts | Same |
| Installed CLI explanations | All 24 authored A/B outputs | Same |
| Dashboard case consumers | All 12 authored cases, actual HTTP routes/assets also checked | All 12 authored cases |
| PNG/PDF figure export | Passed | Passed |

Python versions: macOS 3.12.2; Linux 3.12.14. Node versions: macOS 20.15.0; Linux 18.20.4. Linux used the pinned Python 3.12 Bookworm image recorded in the receipt. Hosted CI specifies Node 20 and remains unverified because GitHub CLI authentication was unavailable; local Linux evidence is not a hosted check result. Native Windows was not qualified.

The legacy preflight also checked all 30 references (28 SAT, 2 UNSAT). New regressions cover different specifications with the same candidate/objective, changed repair contexts, legacy and malformed bindings, stale UNSAT reasons, date/timezone/ID invariance, genuine constraint changes, registry provenance, archive input preservation, stale-version rejection, frozen resume and replay. Independent reproductions of the two original failures now reject the mismatched evidence or known developed structure.

End-to-end checks use canned model responses and real CP-SAT, followed by independent gold validation, accounting, completed resume, replay, analysis and consumers. They establish integration, **not model performance**. No live model calls were made during this verification.

## Reproducing the checks

Use the locked install in README, new output directories and a POSIX shell:

```sh
python scripts/check_installed.py
python -m pytest -q
python -m pip check
node --check src/scheduling/dashboard/static/app.js
node --test tests/frontend/dashboard.test.cjs
python evaluation/offline_demo.py runs/NEW-legacy-check
python evaluation/v2_qualification.py runs/NEW-v2-check
python evaluation/v2_qualification.py runs/NEW-v3-check --version 3
python evaluation/v2_qualification.py runs/NEW-authored-check \
  --cases benchmarks/fixtures/realistic-drafts-v1.json
scheduling evaluate-replay --run-dir runs/NEW-authored-check/run \
  --export-dir artifacts/NEW-authored-export --figures
scheduling dashboard --runs-dir runs --run-dir runs/NEW-authored-check/run --port 8876
```

The exact historical replay checks used `main-baseline-20260929-01`, `yongqing-v2-pilot-20260929-01`, `lihao-boundary-pilot-20260930-01` and `yaoxiang-availability-pilot-20260930-01`. Their nested `summary` objects matched tracked aggregates exactly. Raw runs are ignored; a fresh clone needs the reviewed synthetic archive to repeat these particular checks. Current local qualification logs, source hashes and scripts are retained under `runs/version-2-validation-20260930-01/`.

## Research evidence and remaining gates

At the time of this offline qualification, the latest live evidence was extraction revision 3 on twelve previously used cases: A 4/12 accepted, B 12/12, 24 calls and 48,493 reported tokens. This qualification itself made no model calls. The subsequent [expanded 100-case study](expanded-development-100.md) provides the newer development results. Development reuse, six related source families and historical label-bearing B request IDs limit scientific interpretation. Preserve all earlier scores, raw failures and provenance; do not pool differing runs or treat offline qualification as a new accuracy finding.

Remaining work follows planning Sections 5 and 11:

- Record human mathematical, fixture/gold, language and consumer review. Automated/agent review cannot supply that sign-off.
- Decide and create the fresh final dataset, verify complete development exclusions, and resolve the team commitment to independently human-written scenarios. Existing drafts are AI-assisted; that commitment is a team research policy, not an additional explicit course mandate.
- Confirm course-compliant final-model eligibility/access, qualify on development data under a new cap, and review the protocol and final execution budget before held-out inference.
- Run and analyze the paired study, including difficulty, repair and language robustness; obtain independent teammate replay.
- Complete the report, presentation, responsible-AI analysis, actual contribution/AI disclosures and submission checks.

No completed final-study approval, human sign-off, untouched test set, final grade or external archive publication is implied. Historical receipts and archived environments describe their own checkpoints and remain unchanged.
