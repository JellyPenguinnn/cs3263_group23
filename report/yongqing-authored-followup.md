# Yong Qing authored-case and evaluation review — 30 September 2026

The clean `yongqing-evaluation` branch fast-forwarded from `b94f707` to GitHub
main `92a975b`, including Yao Xiang’s `630d978` availability checkpoint. Existing
work was preserved. The user approved compatible authored-text support and asked
Codex to draft the fictional scenarios. This follow-up is local and uncommitted;
no new publication, live inference, external sharing or human sign-off is claimed.

## Implemented work packages

WP2 had a concrete missing path: `render()` always rebuilt a procedural description
from gold, so a supposedly realistic case could not actually deliver its authored
prose. The approved opt-in `AuthoredBenchmarkCase` and `AuthoredRendering` extension
uses case-bundle **2.0** for supplied prose. Legacy cases remain bundle **1.0** with
identical field serialization and hashes; mixed bundles retain legacy case hashes.
Canonical `ProblemSpec` remains schema 1.0. No solver, provider, prompt, metric or
dashboard behavior changed.

The renderer passes the selected text verbatim, alongside the same public activity
IDs and original repair schedule used by both pipelines. Authorship, rationale,
review references, gold and expected answers remain evaluator-only. A missing
requested variant fails preflight; no generated paraphrase or gold-based fallback
is substituted. The new field types reject duplicate/missing canonical variants,
unknown provenance, blank text/author/rationale and inconsistent review states.

WP4’s frozen controls now require matching authored provenance, a recorded gold
review reference and approved supplied text for every requested variant. A
procedural case cannot claim `human_written`, `llm_assisted` or
`external_adaptation` without explicit authored text. Existing source/input/prompt
hash checks bind the reviewed content. Recorded references are attestations to
check; code cannot establish that a human really reviewed a case or that the
course accepts a dataset. The final study remains unfrozen.

A regression also exposed `check_case_set()` consuming an iterator before returning
its contents. It now materializes once, preventing a supplied iterator from becoming
an empty saved bundle. Existing tuple/list inputs and historical hashes are unchanged.

## Twelve requested fictional drafts

The [review packet](realistic-drafts-review.md), [case bundle](../benchmarks/fixtures/realistic-drafts-v1.json)
and [manifest](../benchmarks/manifests/realistic-drafts-v1.json) contain twelve
**AI-assisted development drafts**, with canonical prose only:

- Six generation and six repair cases; six SAT and six UNSAT.
- Six personal and six shared settings; two repairs per disruption type.
- Examples include a recording booth, a laboratory instrument, study coordination,
  separate rehearsal windows, consultation appointments and a loading-equipment conflict.
- Feasible repair optima include (3,4,0), (2,3,0) and (3,9,0); a generation case
  has unavoidable preference cost 3. Simple contradictions are intentional controls.

Independent complete enumeration checks **6,592 assignments** across these twelve
updated/generation specifications. Every assignment also cross-checks the separate
production validator; CP-SAT agrees on feasibility and exact optima. Original
repair schedules pass independent validation against their original specifications.
These finite checks validate the mathematical encodings, not the prose-to-gold
interpretation. The same assistant drafted prose and gold; human review remains
pending and the independently human-written count is **zero**. The user’s drafting
request does not make AI text human-authored. All inspected drafts stay in development;
they cannot be retagged as fresh held-out data.

A known-development [fingerprint registry](../benchmarks/manifests/development-hard-fingerprints-20260930.json)
now covers the 30 v1, 144 v2, 108 v3 and twelve draft cases: 294 cases and
300 distinct hard fingerprints including original repair specifications. No
cross-split family was found. This covers named inputs, not every possible
historical/private case; add any other inspected cases before final freeze.
Fingerprints are conservative structural checks, not proof of semantic novelty.
The verification receipt records each source bundle hash and the draft-family mapping.

## Scoring and recorded-evidence review

Four new evaluator regression checks use the observed v3 window changes:
false-SAT schedules remain gold-invalid, an altered but correct UNSAT remains
accepted with a mismatch, and the redundant participant-window change remains an
accepted (5,16,19) repair with zero conditional gaps and a structural mismatch.
Raw responses are retained and no gold correction enters inference. This is
AI-assisted technical reviewer work, not independent human teammate approval.

All four historical summaries replay exactly with the new installed package:

| Saved development run | Calls | A accepted | B accepted | Nonaccepted attempts retained |
| --- | ---: | ---: | ---: | ---: |
| `main-baseline-20260929-01` | 60 | 18/30 | 25/30 | 17 |
| `yongqing-v2-pilot-20260929-01` | 24 | 3/12 | 12/12 | 9 |
| `lihao-boundary-pilot-20260930-01` | 24 | 5/12 | 10/12 | 9 |
| `yaoxiang-availability-pilot-20260930-01` | 24 | 4/12 | 12/12 | 8 |

Do not pool these datasets/prompt versions. The first two retain the disclosed
B-only label-ID confound, and the later same-packet qualification reused development
cases that informed prompt revision 3. No new model calls or accuracy claims arise
from this replay. Parsed extraction, structural fidelity, semantic diagnostics,
solver proof and independent acceptance remain separate records.

## Executed verification and reproducibility

The affected authored/frozen/evaluation/validator checks passed **96 tests**;
the final authored/scoring subset passed **30 tests**. Fresh noneditable wheel
installations on macOS ARM64 and Linux ARM64 each passed:

- **478 Python tests and three frontend tests**, JavaScript syntax, `pip check`
  and installed prompt/certificate/dashboard comparisons.
- 180 legacy canned attempts (six deliberate failures), 864 v2, 648 v3 and
  24 authored-case canned attempts, completed resume, replay and figure export.
- Exact replay of the four historical live summaries, with zero inference.

The [verification receipt](../configs/development/yongqing-authored-verification-20260930.json)
records 96 qualified source/fixture hashes, exact versions, assignment counts and
log locations. macOS used Python 3.12.2 / Node 20.15.0; local Linux used Python
3.12.14 / Node 18.20.4. Hosted CI uses Node 20 and was not checked. No dependency
was changed. New source changes require a new future run identity; old archives
remain readable and were not rewritten.

Reproduce the new canned qualification with no credential:

```sh
.venv/bin/python evaluation/v2_qualification.py runs/NEW-authored-qualification \
  --cases benchmarks/fixtures/realistic-drafts-v1.json
.venv/bin/scheduling evaluate-replay \
  --run-dir runs/NEW-authored-qualification/run \
  --export-dir artifacts/NEW-authored-qualification --figures
```

This uses gold-derived canned outputs to verify wiring. It does not measure model
understanding of authored prose. The same script retains its existing `--version 2`
and `--version 3` paths. No live cap was requested or consumed in this follow-up.

## Local replay archive

`artifacts/yongqing-authored-replay-20260930-01.tar.gz` contains the source,
qualified wheel, verification logs, four historical synthetic runs and the new
24-attempt canned run. It is local and ignored by Git. Size: 756,102 bytes;
SHA-256: `8ddc19306c6e543975931fccbc409fa0435b101a08496e567c54d12bc36585ec`.
All 451 content checksums passed after unpacking; the portable `replay.py`
reproduced the four historical summaries and authored canned summary exactly
using the qualified installed wheel without credentials. The credential scan
passed. External sharing and an actual independent teammate replay are pending.
The immutable archive predates this archive receipt being added to the handoff;
its source contains the same qualified runtime and earlier documentation snapshot.

## Assignment audit and next concrete task

| Yong Qing responsibility | Current checkpoint | Remaining gate / owner |
| --- | --- | --- |
| Generator/rendering/provenance; WP2 | V1–v3 retained; exact authored text and twelve AI-assisted drafts with finite certificates | Yong Qing coordinates real human prose/gold review; Li Hao wording, Yao Xiang semantics. Required independent human authorship remains unsatisfied unless the team explicitly revises that plan |
| Independent validator and formal review support | Exhaustive draft/validator cross-checks, v3 scoring counterexamples and installed suites | Named human mathematical and consumer sign-off |
| Runner/frozen controls; WP4 | Authored-review enforcement, iterator fix, compatible serialization, known-development registry | Final eligible model/access, complete reviewed exclusion registry, fresh splits, protocol and execution cap |
| Metrics/error analysis; WP3/WP5 | All four historical summaries preserved; failures and fidelity distinctions verified | Final-study difficulty/repair/robustness results; no live prose qualification yet |
| Tables/figures/reproduction | Installed exports and recorded replays pass on both platforms | Authorized archive sharing and actual independent teammate replay |
| Benchmark/results writing and course delivery | Review packet, provenance, technical review and this handoff | Final results discussion, responsible-AI/contribution disclosure, report, presentation and rehearsal |

Next, review the twelve draft texts against their gold specifications and record
actual reviewers and corrections. They can serve as development/review material;
produce independently human-written scenarios for the current final plan, or
explicitly agree and document a changed provenance policy. Keep optional external
data, extra models, solver tuning and new live runs separate. Human/final-study
gates prevent a full-project completion claim, but do not invalidate this tested
engineering checkpoint.
