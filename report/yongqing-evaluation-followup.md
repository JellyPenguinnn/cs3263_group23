# Yong Qing evaluation follow-up — 29 September 2026

Implemented locally on `yongqing-evaluation`, fast-forwarded to GitHub main
`bc165bc` before edits. This incorporates Li Hao’s and Yao Xiang’s integrated
work and preserves their historical runs. The user authorized committing and pushing this checkpoint to
`yongqing-evaluation` on 30 September. No main merge or PR is authorized. This is AI-assisted implementation and verification;
it does not constitute independent human review or a final-study freeze.

## Assignment audit against planning.md Sections 4–5

| Required responsibility | Delivered and observed | Remaining dependency |
| --- | --- | --- |
| WP2: generator, provenance and grouping | V2 structural generator; 144 balanced development cases; checked witnesses/UNSAT references; bounded rejection ledger; ID-independent conservative family audit; realized difficulty and rendering hashes | Yao Xiang reviews gold/contradictions; Li Hao reviews equivalent wording; Yong Qing collects 12 independently human-written realistic scenarios and their separate formalizations. Final fresh test allocation follows review |
| WP3: scoring and failure attribution | Independently replayed all 24 pilot answers; stage funnels, violation-instance counts and typed differences; retained every failure | Human semantic review of the redundant-bound example below; broader model qualification needs a new cap |
| WP4: frozen evaluation controls | Compatible RunConfig/CLI extension, versioned protocol checks, preflight leakage/source/input/model/cap guards, exact references, backend-drift stop and immutable resume tests | Actual reviewed freeze receipt, model eligibility/access, complete development registry and authorized study budget. Test fixtures are not a real held-out study |
| WP5: analysis and reproducibility | Installed macOS qualification, unchanged original replay, supplementary analysis and uncertainty-aware figures; checksum-addressed local replay package | Current Linux execution, team-accessible archive location and independent teammate replay; frozen study and final results/robustness analysis |
| R1–R4 review contribution | Existing independent mathematical tests and proof/gold boundary tests run with the integrated main implementation; new scoring consumes R2 diagnostics | Named human mathematical, consumer and wording sign-offs remain open |
| Benchmark/results writing and course contribution | This method/result draft, aggregate receipt, claim-to-artifact map and recorded AI assistance | Final discussion/report/presentation, responsible-AI discussion review and actual contribution/submission records |

Optional public-data adaptation, semantic-equivalence automation, feedback arms,
parallel model calls and solver optimizations are not added. They are not core
completion conditions. The team still records the optional external-data
include/defer decision before freeze. Missing model eligibility or human review
does not block the implemented development work, but does block a final study.

## V2 construction and evidence boundaries

V1 remains the CLI default and its data/summary semantics are unchanged. Explicit
`--version 2 --seed 3264` selects a separate procedural development version.
One repetition is four sweeps × three levels × three event types × two labels
× generation/repair = **144 cases in 72 source families**. Each task has 36 SAT
and 36 UNSAT cases; every repair event appears 24 times across levels/sweeps.
No candidate was excluded for the qualified seed. Other seeds retain a ledger
of duplicates/unresolved references and unfilled quotas; incomplete generation
returns failure instead of silently advertising a complete matrix.

Seeded choices vary durations, time windows, participant/resource assignments,
precedence and preferences. The activity-count sweep uses 4/8/12 activities.
Each new precedence edge has a tested feasible counterexample when removed;
no edge is justified merely by being present in a constraint count. Structural
fingerprints ignore incidental IDs/order and transitive precedence in acyclic
graphs, and retain preference multiplicity/old starts in the full comparison.
Graph refinement is a conservative grouping aid, not general isomorphism or
semantic-equivalence proof. Related original/updated problems share families.

The generator independently checks a constructed original witness, selects its
saved exact gold solution as the common old schedule, and checks updated
references. The old preference optimum is zero with unique preferred starts.
UNSAT cases force A0 and fixed A1 to overlap the capacity-one resource Rpair
while both individual start domains remain nonempty. Small exhaustive checks
and the named conflict justify that construction independently of CP-SAT status.

Limitations matter: UNSAT cases share this two-activity recipe; all SAT repairs
in this matrix require only one moved activity and one slot of shift. The sweeps
have coupled covariates, not a causal difficulty guarantee. Reference success
and canned rendering coverage do not certify natural-language fidelity. No
human-written realism, unseen final data or broad solver scaling is claimed.
The pilot shows a B ceiling on its selected cases; it does not establish that
the whole matrix or more natural prose will be equally easy.

## Frozen-mode contract

`offline_frozen` and `live_frozen` extend the existing serial runner. Development
mode still requires development splits. Frozen mode requires test membership,
a reviewed v2 manifest, matching case/rendering/source/prompt/config hashes,
family grouping, an exclusion registry of previously developed hard structures,
model/eligibility/approval/budget references and caps covering all planned calls.
References must have resolved labels and exact objective proofs. Live backend
identity drift stops subsequent calls and is retained on resume. Existing
reservation, provider-error, interrupted-attempt and replay behavior is reused.

`freeze-draft` records current hashes but leaves decision references blank, so
the result cannot run until the team supplies an actual reviewed protocol.
Software checks recorded references; it cannot certify that a human reviewed
or approved them. The registry saved with this follow-up covers all 30 legacy
and 144 v2 development cases (174 hard-structure fingerprints including repair
originals). Future development must extend it before final allocation.
The final benchmark, eligible model, count, longest-output budget qualification
and protocol are still pending. No development cases were reclassified.

## Executed verification

A fresh Python 3.12 virtual environment installed `requirements.lock` with
`--require-hashes`, built and installed a noneditable wheel, and confirmed the
import came from `site-packages`. On macOS ARM64:

- `python -m pytest -q`: **398 passed**.
- `python -m pip check`, `node --check src/scheduling/dashboard/static/app.js`
  and `node --test tests/frontend/dashboard.test.cjs`: passed, three frontend tests.
- Legacy `benchmark-generate` / `evaluate-plan`: all 30 references checked.
- V2 CLI generation: all 144 requested cases and references checked.
- `python evaluation/v2_qualification.py NEW_DIRECTORY`: **864/864 accepted
  canned attempts**, 144 cases × three renderings × two paths; completed resume
  made zero extra calls. This is integration evidence, not model accuracy.
- Original `main-baseline-20260929-01` replay: summary identical to the tracked
  A 18/30, B 25/30 aggregate; original files were not rewritten.
- V2 replay/figure export executed; PNG layouts inspected. The supplementary
  intervals preserve source families and omit intervals below ten groups.
- All 91 recorded code/prompt/test/config/build files still match the installed
  qualification hashes after the pilot. Current Linux execution is unverified.

The qualification path and logs are preserved under
`runs/yongqing-followup-20260929-01/`. No dependency, prompt, provider,
solver-objective or dashboard implementation changed in this follow-up.

## Approved live development pilot

The [preselection receipt](../benchmarks/manifests/yongqing-v2-pilot-20260929.json)
fixes six families before any outputs: all three events, balanced SAT/UNSAT,
all four sweeps, retaining generation and repair per family. The
[configuration](../configs/development/yongqing-v2-pilot.json) uses qwen3.6:35b,
24 serial calls, no retries, 8,192 output tokens/call (196,608 requested cap),
10 seconds per B solve and 30 seconds per gold reference. Canonical rendering
only, repeat zero. No held-out data or semantic correction calls were used.

Run: `yongqing-v2-pilot-20260929-01`. **All 24 calls completed**, all returned
qwen3.6:35b and finish reason `stop`. Reported usage covers 24/24 attempts:
36,236 input + 21,123 output = **57,359 total tokens**. The largest completion
was 2,652 tokens; currency cost is unavailable. The approved allowance is
consumed. These observed lengths qualify only the selected cases, not the
longest possible final-study outputs.

| Canonical subset | Direct A | Solver-assisted B |
| --- | ---: | ---: |
| Generation accepted answers | 2/6 | 6/6 |
| Generation gold-SAT validity | 1/3 | 3/3 |
| Generation gold-UNSAT accuracy | 1/3 | 3/3 |
| Repair accepted answers | 1/6 | 6/6 |
| Repair gold-SAT validity | 1/3 | 3/3 |
| Repair gold-UNSAT accuracy | 0/3 | 3/3 |

Each task has six related source families and each label stratum has three.
No confidence interval or general superiority claim is supported. This is a
new dataset and revised extraction prompt; its rates are not a controlled
before/after comparison with the original baseline or Yao Xiang’s selected
four-call pilot. There are no live language variants in this run.

A’s nine rejected answers are seven invalid schedules (one resource overlap,
three blocked-interval violations, three deadline violations), one false UNSAT
and one invalid output. The invalid reply correctly discussed the UNSAT
conflict but surrounded JSON with prose; the unchanged strict parser rejects
it. It stays a failure rather than being manually extracted and rescored.

B has 12 schema-valid extractions, 11 exact structural matches and 12 accepted
answers. On `dev-v2-3264-interaction_density-2-deadline-sat-0-generation`, B adds
16 release/deadline rules. A separate offline diagnostic verifies that each
bound follows from the unchanged availability windows; no gold constraint is
omitted. This explains a structural mismatch without demonstrating a semantic
change. Its recorded mismatch remains; human semantic review is pending.
All six valid B schedules achieve zero conditional objective gaps. All three
SAT B repairs move one activity by one slot, with preference penalties 4, 3
and 1 respectively. A has only one valid repair, so conditional quality
averages do not describe its full-attempt performance.

The existing deterministic `scheduling explain` command can inspect any saved
case without inference. For example, the blocked SAT repair moves A0 earlier
by one slot to avoid its newly blocked old interval while preserving every
other start; `(moved, shift, preference)=(1,1,4)` is proven optimal and independently
valid against gold. This is a concrete repair explanation, not a fairness claim.

## Claim-to-artifact map and handoff

| Claim / result | Authoritative artifact |
| --- | --- |
| Pilot selection and cap | `benchmarks/manifests/yongqing-v2-pilot-20260929.json`, `configs/development/yongqing-v2-pilot.json` |
| Tables, usage, differences, source/run hashes | `results/summary/yongqing-evaluation-followup-20260929.json` |
| Immutable raw outputs and reference records | `runs/yongqing-v2-pilot-20260929-01/` |
| Recomputed tables and scientific PNG/PDF figures | `artifacts/yongqing-v2-pilot-20260929-01/` |
| Fresh environment, source receipt and test logs | `runs/yongqing-followup-20260929-01/` |
| Canned reproduction recipe | `evaluation/v2_qualification.py` |

The local reproduction archive is `artifacts/yongqing-replay-20260929-01.tar.gz`
(763,713 bytes), SHA-256
`50a1ef99dde5c53ad845b9b3cd0b3b0cc12a70ba8e35ced38fb9ec932314cfe2`.
It contains the installed wheel, qualified source, selected inputs, matrix
provenance, raw synthetic pilot records, figures and qualification receipts.
All 193 checksummed files passed verification after unpacking into a separate
directory; credential-free replay matched the pilot summary exactly. An actual
teammate has not yet replayed it, and no shared external location is claimed.
Use its `REPLAY.md` and `CHECKSUMS.json` for the handoff.

Recompute the live pilot without a key using the recorded wheel/package:

```sh
scheduling evaluate-replay --run-dir runs/yongqing-v2-pilot-20260929-01 \
  --export-dir artifacts/NEW-pilot-replay --figures
```

**Next concrete task:** Yao Xiang reviews the v2 gold/UNSAT and objective
constructions; Li Hao reviews paired wording and the provider/runner boundary.
Yong Qing obtains the independently authored realistic scenarios and records
those reviews, then allocates fresh families and drafts the final protocol.
Human review, final-model eligibility, a new budget and current Linux
qualification remain gates. Member-branch publication is authorized; sharing the local replay archive to
an external location still requires the member’s instruction. No member is marked fully finished with
course, review or final-study responsibilities.
