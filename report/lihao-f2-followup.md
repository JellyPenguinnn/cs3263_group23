# Li Hao F2/F6 handoff — 30 September 2026

Working branch: `lihao-llm-baseline`, fast-forwarded from `8cc43b6` to GitHub main
`8f3ff1b` with existing history preserved. The user subsequently authorized
committing and pushing this checkpoint to Li Hao's member branch. This does not
authorize a main merge or resume the stopped live qualification. The verification
receipt retains its original pre-publication status as an audit-time snapshot.

## Delivered engineering

- F2 preparation: `evaluation/prepare_model_qualification.py` selects 24 cases
  from the exact preserved expanded 100-case bundle, six per task/label stratum.
  It retains the three predeclared extraction failures, the longest combined A/B
  requests per stratum and five-activity coupled resource chains, then prioritizes
  family/sweep/event diversity. It never reads new model outcomes. The selected
  packet has 19 source families and is known development data.
- Two equal-budget configurations and real reference preflights use unchanged
  prompts, 32,768 output tokens, 30/900-second connection/read timeouts, one
  transport attempt and 30/60-second solver/reference limits. There are 48 case
  calls per model. Preparation creates no inference and refuses altered source
  bundles, missing quotas and existing output directories.
- Compatible per-attempt execution metadata records the versioned request contract,
  endpoint, output ceiling, timeouts, omitted server-default controls and final
  content field. Reported fingerprint and reasoning-token count remain optional;
  weight revision is unknown. Separate reasoning text is neither used as final
  output nor retained. Mixed reasoning inside final content remains an invalid
  model answer rather than being regex-repaired.
- New live contracts and frozen settings include execution settings. Frozen
  backend fingerprint changes (including appearance/disappearance) stop execution
  after saving the observation and remain stopped on resume. Historical replay
  remains supported; changed source/settings require a new run identity.
- F6: [one report source](study-draft.md), [claim index](claim-evidence.md),
  [honest contribution log](contributions.md) and [timed presentation guide](../presentation/rehearsal.md).
  Methods, two-path diagram, coupled repair, four responsible-AI cases and a
  checked four-source bibliography are drafted. Development tables are verified
  against saved summaries; final-study sections remain explicitly unfilled.

## Live qualification and blocker

The user explicitly approved one model-list request plus at most 100 completions:
four capability checks and 96 paired case calls; no retries, 32,768 output tokens
each, total output reservation cap 3,276,800, with input tokens additional.
The metadata/consumer change was also explicitly approved. No final inference,
model eligibility or publication permission follows from either decision.

The single model listing found both requested IDs. All four capability checks
returned their exact requested final JSON and model ID, accepting the requested
output ceiling. They reported **349 tokens**. The provider's effective omitted
controls, weight revision and reasoning-budget semantics remain unverified.
These checks preceded the metadata extension; their original records are retained.

The paired run `lihao-f2-model-qualification-20260930-01` stopped after **two case
calls** on the first reference-model generation case. Both returned HTTP 200,
finish `stop` and `qwen3.6:35b`, but their `system_fingerprint` differed:

| Approach | Reported fingerprint | Reported tokens |
| --- | --- | ---: |
| Direct | `vllm-0.23.0-7cd694fa` | 848 |
| Solver-augmented | `vllm-0.26.0-2ccdf8cb` | 2,810 |

This is an observed serving-identity discrepancy, not proof of different model
weights. The unmodified responses, scores and execution metadata are saved.
The qualification guard stopped before another call. No model selection or
two-model accuracy comparison is supported. One metadata request and **six total
completions** used **4,007 reported tokens** and reserved **196,608 output tokens**.
The unused 94-completion allowance does not waive the stop condition: continuation
requires the pending explicit backend-policy decision, with any exception recorded
as variable-backend development evidence. Frozen backend checks stay strict.

The first attempted batch launch did not execute because automatic approval review
timed out. Its single retry launched the two recorded calls. No hidden retry or
duplicate model call occurred.

## Verification

| Executed check | Result |
| --- | --- |
| Focused provider, packet, runner and frozen tests | 117 passed |
| Complete installed macOS Python suite | 552 passed |
| Fresh locked Linux ARM64 installed Python suite | 552 passed |
| macOS frontend tests and JavaScript syntax | 7 passed; syntax valid |
| Installed prompt/certificate/dashboard assets and pip consistency | Passed on macOS and Linux |
| Selected 24-case canned integration | 48 attempts, all accepted, completed resume and replay on both platforms |
| Five historical live summaries | 332 attempts replay exactly; original files unchanged |
| F6 table, resource counts, test references and local links | Checked against actual artifacts |
| Recorded-failure explanation command | Executed without inference |

Linux used `python:3.12-slim-bookworm` image
`sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e`.
This is local ARM64 evidence; hosted GitHub CI and native Windows are not claimed.
The original runtime snapshot and prompts were unchanged during the actual calls.
Tests use synthetic HTTP responses except the explicitly authorized six calls.

Reproduction commands (fresh output directories required):

```sh
.venv/bin/python evaluation/prepare_development_expansion.py runs/NEW-expanded-input
.venv/bin/python evaluation/prepare_model_qualification.py runs/NEW-f2-input \
  --cases runs/NEW-expanded-input/cases.json
.venv/bin/python evaluation/v2_qualification.py runs/NEW-f2-offline \
  --cases runs/NEW-f2-input/cases.json
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_installed.py
```

The tracked [selection](../benchmarks/manifests/lihao-f2-qualification-20260930.json)
and [verification receipt](../configs/development/lihao-f2-verification-20260930.json)
identify the exact packet, sources and local evidence paths. The execution scripts
and logs remain in the ignored local qualification directory; they are not an
alternative runner or blanket permission to repeat calls. Archived inputs/results
are untouched. No new dependency, solver formulation, scoring rule or prompt was
introduced.

## Remaining responsibilities and next task

F2 is **partially complete**: preparation, metadata and offline qualification are
implemented; the live comparison/model decision is blocked on provider consistency
or an explicit development-only policy exception. Yao Xiang coordinates actual
course eligibility and owns F1's remaining extraction review/prompt decision.
Yong Qing owns F3 fresh construction, F4 frozen rehearsal/study and F5 cross-block
analysis. Those are not completed by this packet or by automated tests.

F6's report preparation is delivered, not the final report. Each member must
contribute interpretation and real cross-review, then supply final evidence,
typeset/audit the ten-page body, rehearse and retain actual submission receipts.
The immediate Li Hao task is to resolve the recorded F2 backend policy, complete
the authorized paired qualification only under that decision, and record a model
recommendation based on balanced task performance, reliability and cost. Optional
extra models, feedback, solver optimization and UI expansion remain deferred.
