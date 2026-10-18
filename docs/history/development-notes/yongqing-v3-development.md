# Yong Qing: development challenge benchmark — 30 September 2026

Work starts from GitHub main `1de9e7e` (PR #8) on `yongqing-evaluation`.
The clean checkout was fast-forwarded, preserving all prior member commits.
The user authorized the separate v3 development benchmark and subsequently
authorized committing and pushing this verified checkpoint to
`yongqing-evaluation`. Main integration and new live inference remain separate. This is AI-assisted technical
work, not independent human review or a final-study freeze.

## Assignment audit against planning.md Sections 4–5

| Responsibility | Implemented / validated at this checkpoint | Remaining deliverable or dependency |
| --- | --- | --- |
| Synthetic generator, rendering and grouping (WP2) | V1/v2 retained; v3 challenge matrix, opaque IDs, provenance, exhaustive reference checks and all-rendering integration | Twelve independently human-written scenarios, actual gold/wording reviews and fresh final allocation; v3 does not replace those requirements |
| Independent validator and R1–R4 review support | Existing independent validity/objective checks and formal regressions pass in both 434-test installed suites; v3 exhaustively cross-checks validator results | Named human mathematical, semantic and consumer sign-off |
| Runner and frozen-mode controls (WP4) | Existing caps, reservations, stop/resume, development/test separation and frozen guards pass integration/regression checks | Approved final model, reviewed protocol, complete development exclusion registry and execution cap; no actual study is frozen |
| Scoring and failure analysis (WP3) | Historical denominators/scores preserved; both live summaries replay exactly; label-bearing B metadata flaw diagnosed and disclosed | Generic B request-ID masking needs coordinated pipeline edit; v3 live pilot has no approved cap |
| Metrics, tables, figures and reproducibility (WP5) | Existing paired/conditional analysis, v3 figure export, 648 v3 and 864 v2 canned attempts per platform; 924-file archive verified and replayed | Frozen main-study results/robustness, authorized archive sharing and actual independent teammate replay |
| Benchmark/results writing and joint course work | Current method, construction, limitations and evidence handoff documented; prior result drafts retained | Final benchmark/results discussion, actual contribution/AI disclosures, report/presentation review and rehearsal |

**Conclusion:** the current authorized development checkpoint is implemented and
technically validated. The full set of Yong Qing's planning responsibilities is
not yet complete. Optional external-data adaptation, solver optimizations,
extra models and parallel inference are not missing mandatory deliverables.
Publication of this checkpoint does not resolve the pending gates above.

## Assignment and implementation

WP2 extends the existing generator, renderer, manifest and CLI. V1 remains the
default and v1/v2 inputs, archived replies and scores are preserved. V3 uses the
same scheduling schema, objectives, solver, independent validator and two paths.
No dependency, provider setting, prompt template, dashboard or metric changed.

One repetition contains **108 procedural development cases in nine source
families**: three mechanisms × three sizes (3/4/5 activities) × three disruption
types × two labels × generation/repair. There are 27 cases in each task/label
stratum. Related task, event and label variants deliberately share families;
the 108 rows are not 108 independent problems.

- **Resource displacement:** all activities share a capacity-one resource.
  Each can keep its old slot or move to the next slot; the last can wrap to the
  first. A disruption forces the whole cycle to move. In the UNSAT counterpart,
  the last activity cannot wrap, causing a capacity contradiction even though
  every individual domain remains nonempty.
- **Precedence propagation:** an adjacent chain and two starts per activity
  propagate a disruption along the entire chain. Fixing the last activity to
  its old window makes the updated chain infeasible. Removing any one chain
  edge restores feasibility in these constructed UNSAT cases.
- **Unary boundary:** independent activities provide a simple control. One
  activity can move in the SAT version; in the UNSAT version its disruption
  eliminates its sole available start. This is explicitly an easy contradiction,
  not an interacting-reasoning example.

Every activity has two mutually incompatible preferred starts with different
weights. Feasible generation references therefore have nonzero unavoidable
preference costs (5–19 for seed 3265). The old schedule is the unique preference
optimum of the original problem and is supplied identically to both approaches.
For the 27 SAT repairs, nine move one activity and six each move three, four and
five. Resource cycles shift a total of `2*(n-1)*duration` slots; precedence chains
shift `n*duration` slots; unary controls shift one duration.

Deadline cases reflect the construction in time, so a tighter end bound triggers
the same type of propagation. Duration and offset are seeded; all three events
appear at every mechanism/size/label. Each selected case has an exact reference
and an independently checked witness when feasible. An unresolved reference
excludes its whole generation/repair pair and leaves an explicit incomplete
quota; no model outcome drives selection and no silent retry occurs.

`tests/unit/test_benchmark_v3.py` independently enumerates every start fitting
each activity window, then checks the full Cartesian product (at most 32
assignments). Independent arithmetic, the validator and the reference agree on
feasibility and objectives. Tests also check unique original optima, propagation,
constraint-removal witnesses, grouping, determinism, rendering boundaries,
zero-budget exclusions and the installed CLI without Git.

## Request metadata finding and historical evidence

The request audit found that the existing solver-augmented builder sends
`NaturalLanguageView.instance_id` to B. Direct A does not receive that ID.
Two of the original 30 case IDs (`simple-sat`, `proven-unsat`) and all 12 selected
v2 pilot case IDs explicitly encode SAT/UNSAT. This is a label-leakage risk and
an unequal-information condition, not proof that the model used the hint.

Preserve the original acceptance counts and raw attempts. Their ability to
support a fair A/B comparison is limited by this confound; do not treat the v2
pilot's perfect B acceptance as evidence of unaided formalization reliability.
A corrected future run needs a new source contract/run identity. Replaying old
records does not remove the information that was available during inference.

V3 now assigns opaque deterministic case IDs and keeps labels/mechanisms only
in evaluator metadata. A narrow shared B-boundary fix has been requested to
protect arbitrary future input bundles too; its authorization remains separate.

## Scope and next dependencies

This small challenge set supplements v2's four sweeps; it does not replace the
planned controlled study, establish scaling difficulty or supply independently
human-written realistic prose. Binary domains and construction motifs remain
narrow. The sample has only nine source families; uncertainty must respect that
grouping. Different seeds/IDs do not prove structural or semantic independence.

The next required data contribution is the twelve independently human-written
fictional scenarios and separate gold/wording reviews. Actual human authorship
and sign-off cannot be supplied by this coding-agent session. Final model,
protocol, fresh split allocation and execution budget remain later freeze gates.
Optional external-data adaptation, solver tuning, parallel inference and extra
research arms are deferred.

## Executed qualification

The final opaque-ID source was installed as a noneditable wheel into fresh
Python 3.12 environments on macOS ARM64 and Debian Linux ARM64:

- `python -m pytest -q`: **434 passed on each platform**.
- `python -m pip check` and `python scripts/check_installed.py`: passed on each.
- `scheduling benchmark-generate --version 3 --seed 3265`: 108 cases, complete
  quota, all references resolved; the CLI also works when Git is not installed.
- `python evaluation/v2_qualification.py NEW --version 3`: **648/648 accepted
  canned attempts** on each platform, all three renderings, completed resume
  without additional reservations and successful replay/figure export.
- The same script's unchanged default v2 route: **864/864 canned attempts** on
  each platform. These checks test wiring, not model performance.
- Offline replay of the saved 60-call original and 24-call v2 pilot reproduced
  both tracked summaries exactly on each platform.
- All 83 qualified runtime/test/prompt/evaluation/build files matched their
  source hashes when the final receipt was recorded. No frontend code changed.

The first fresh Linux run exposed an unhandled missing `git` executable during
optional revision collection. The CLI now records `unavailable` when Git is
absent, with a regression; it still preserves generator source hashes. Initial
failure logs and subsequent successful qualifications remain separate.

The [machine-readable receipt](../configs/development/yongqing-v3-verification-20260930.json)
contains versions, source hashes, construction counts and evidence boundaries.
Local logs and the final pilot draft are in `runs/yongqing-v3-20260930-01/`.
The earlier pre-audit draft is superseded by `opaque-inputs/`; neither has model
responses. The opaque pilot draft preselects twelve cases in six families, with
balanced tasks/labels and all mechanisms/events. A separate request cap is still
pending. **Zero new live model calls** were made in this checkpoint.

The combined development fingerprint registry covers the thirty legacy cases,
144 seed-3264 v2 cases and 108 seed-3265 v3 cases (282 distinct hard fingerprints
including original problems). Its exact coverage is recorded; extend it for
other inspected seeds/fixtures before any final allocation. It is not a claim
that all possible equivalent or future cases have been excluded.

WP2's new construction and WP5's current installed reproduction checks are
complete for this development checkpoint. WP3's metadata diagnosis is recorded;
the broader B request-boundary fix awaits coordination. Realistic authorship,
human review, final freeze and later course deliverables remain separate.


## Local reproduction archive

`artifacts/yongqing-v3-replay-20260930-01.tar.gz` contains the qualified wheel,
source, 648 synthetic canned records, manifest, summaries and platform logs.
It is 1,147,514 bytes, SHA-256
`33071f73dfafa02ae6fa374847b8469591ce15775c62bb69e8fd42fcd1c1a9a7`.
All 924 checksummed files matched after unpacking, and credential-free replay
reproduced the saved summary exactly. This is agent-executed archive validation,
not an independent human teammate replay. No external archive sharing occurred.
