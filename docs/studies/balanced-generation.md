# Balanced generation confirmation

**Status: completed earlier study, 96 attempts per model.** Its [comparison audit](balanced-comparison-audit.md) records the outcomes. The primary report now uses the separately preserved [diverse generation study](diverse-generation.md); preparation commands below describe this balanced protocol only.

This separately versioned dataset addresses the constraint-type/feasibility-label confound found in the completed difficulty study. It is a focused generation confirmation, not a replacement or corrected score for that study. Existing cases, model responses, scores, figures and archives remain unchanged.

## Question and design

Can direct scheduling and extraction followed by CP-SAT handle feasible and infeasible requests when deadlines and fixed appointments no longer identify the feasibility label?

`balanced-generation-v1` contains **48 generation cases**: three interaction mechanisms × two numeric layouts × four constraint profiles × two feasibility labels. The mechanisms are shared-room capacity, participant capacity and precedence interactions. Each SAT/UNSAT pair has identical activity assignments, durations, rule values, constraint types/counts and prose style. Only numeric availability changes the feasibility of the matched cases.

| Explicit constraint profile | SAT | UNSAT | Total |
| --- | ---: | ---: | ---: |
| Neither deadline nor fixed appointment | 6 | 6 | 12 |
| Deadline only | 6 | 6 | 12 |
| Fixed appointment only | 6 | 6 | 12 |
| Both | 6 | 6 | 12 |
| **Total** | **24** | **24** | **48** |

Every case has eight mandatory activities lasting 1–2 hours, two participants and one shared room. The horizon is **Monday 26 October 2026, 09:00–17:00 UTC+08:00**, with 30-minute slots. All participants/resources have capacity one. The current schema remains single-day; this does not implement a five-day calendar. Preferred-start windows represent morning preferences; consecutive-meeting and day-clustering objectives remain outside scope.

The seed permutes neutral activity identifiers; it does not sample new numeric geometries, so another seed is not independent evidence. The loose/tight layouts control available slack; they are not claims about measured model difficulty. UNSAT cases retain a nonempty individual domain for every activity and fail through interactions. Deadline and fixed-start constraints are operative: each of the 12 feasible cases containing each type has a saved counterexample that becomes feasible only when that particular rule is removed.

## Independent checks and evidence boundaries

- SAT labels have constructed schedules checked by the independent arithmetic validator.
- UNSAT labels have checked resource/participant capacity or precedence-span certificates. Certificate verification does not call CP-SAT, compiler helpers or the compiler's domain analysis.
- CP-SAT separately confirms feasibility/infeasibility and proves the reference preference optimum. Its output schedules are independently validated; optimality still relies on the reference compiler.
- The design gate recomputes profile/label balance, matched rule/assignment equality, nonempty unary domains, source/proof bindings and public renderings. A changed fixture requires a new version, not a relaxed gate.
- Canonical and reordered prose both include the exact date, origin and timezone. Only **canonical** prose is included in the capped campaign. Gold labels, proofs, case/group IDs and review metadata never enter measured prompts.

The 48 cases belong to **three conservative construction families**, grouping all related variants of each mechanism. They are not 48 independent samples. Treat profile/mechanism results as descriptive and keep family-level uncertainty limitations explicit. The benchmark removes the identified constraint-presence shortcut; it does not eliminate all template bias or establish broad real-calendar competence. It is AI-assisted development data, not manually reviewed; the 24-case review covered the main study only. Both live campaigns completed on 15 October 2026; their results are reported separately from the earlier studies.

## Dataset and review artifacts

The immutable prepared version is under [`benchmarks/fixtures/balanced-generation-v1/`](../../benchmarks/fixtures/balanced-generation-v1/):

| Artifact | Purpose |
| --- | --- |
| `cases.json` | Versioned formal cases, witnesses and canonical/reordered public requests |
| `proofs.json` | Input-bound feasibility certificates and operative-constraint counterexamples |
| `manifest.json` | Generator and content hashes, balance, groups, scope, proposed model settings and limitations |
| `review.json` | Evaluator-only public-text/gold/proof pairs; human review fields are unfilled |

Do not send `review.json`, proof records or gold specifications to either measured model. Member review should check every public request against its gold facts, review the feasibility arguments and preference interpretation, and record actual findings. A revised dataset belongs in a new directory/version and requires fresh packets.

To reproduce construction offline in a **new** directory using the pinned environment:

```sh
PYTHONPATH=src .venv/bin/python evaluation/prepare_balanced_generation.py \
  runs/NEW-balanced-dataset
```

This invokes local proof/reference checks and makes no provider requests. Existing directories are refused.

## Matched model protocol

| Setting | Both campaigns |
| --- | --- |
| Scheduling attempts | 48 cases × two methods × one canonical rendering = **96** |
| Capability checks / metadata | Two completions / one metadata request |
| Total request allowance | **99 requests per model**, no retries |
| Requested output ceiling | 32,768 per completion; **3,211,264 reserved output tokens per model** |
| Timeouts | 30-second connect; 1,800-second read/write/pool |
| Solver / reference budget | 30 / 60 seconds per case |
| Qualification | Exact returned model; backend variation recorded |
| Transient failures | Record eligible timeout/HTTP failures, cool down and continue to the next distinct attempt |
| Fatal failures | Identity, authentication, quota, TLS, integrity or exhausted-budget failures still stop |

Qwen requests and must return **`qwen3.6:35b`**. GLM requests **`x-test-1`** and must return **`glm-5.3-flash`**. No fallback model is allowed. All other configurations, cases and prompt hashes must match. Backend fingerprints and unavailable server defaults remain recorded limitations.

For both completed models together, the authorized cap was **192 scheduling completions, four capability completions and two metadata requests: 198 requests and 6,422,528 reserved output tokens**. Input tokens are additional; the output reservation is not measured consumption or a currency cap. The runner records actual elapsed model/solver time and token usage, including missing-usage coverage.

Prepare the source/runtime-bound packets offline after installing the current checkout:

```sh
PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  benchmarks/fixtures/balanced-generation-v1/cases.json runs/NEW-balanced-qwen-packet \
  --design balanced-generation-96 --model qwen3.6:35b \
  --qualification-policy strict_model_observe_backend_v1

PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  benchmarks/fixtures/balanced-generation-v1/cases.json runs/NEW-balanced-glm-packet \
  --design balanced-generation-96 --model x-test-1 \
  --qualification-policy strict_model_observe_backend_v1
```

Preparation is not live authorization. Changed source, runtime, cases or prompts invalidate a packet; regenerate it in a new directory. Once live execution is explicitly authorized, use the existing supervisor, substituting the chosen packet and a new run directory:

```sh
PYTHONPATH=src .venv/bin/python evaluation/supervise_development_campaign.py \
  runs/NEW-balanced-qwen-packet runs/NEW-balanced-qwen-run \
  --env-file .env --authorization-reference 'actual approved run reference' --allow-live
```

Use a private credential file and the established durable-process workflow in [usage.md](../usage.md). The supervisor now derives its analysis/export blocks from the validated packet, so the generation-only campaign reaches analysis and archive export without expecting nonexistent repair/fictional/wording blocks. A local process still pauses when the Mac sleeps; terminal persistence does not prevent sleep.

## Verification and reporting

The [verification receipt](../../results/summary/balanced-generation-verification-20261015.json) records **900 passing regression tests**, including 23 new dataset tests and 24 new integration tests. A fresh noneditable wheel installation also validates the dataset and prepares/loads a packet. All existing traces/results and the preceding report version are preserved.

The offline integration checks use `httpx.MockTransport`, real provider parsing and campaign orchestration, gold-derived canned responses, both method pipelines, scoring, replay, analysis, figures, archive extraction/replay and dashboard reads. Injected timeouts/HTTP 502s test continuation; a wrong response identity tests fatal stopping. These outputs are **engineering evidence only**, never new Qwen or GLM performance results.

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_balanced_generation.py tests/integration/test_balanced_campaign.py
```

## Completed comparison

Both models completed all 96 planned scheduling attempts, two capability completions and one metadata request, with no retries. Qwen ran first, followed by GLM. Both exported analyses and immutable reproduction archives. Their execution allowances are consumed; commands above document a workflow, not permission for another run.

| Model | Direct LLM | LLM + CP-SAT |
| --- | ---: | ---: |
| Qwen3.6 | 6/48 (12.5%) | 48/48 (100.0%) |
| GLM5.3 Flash | 47/48 (97.9%) | 48/48 (100.0%) |

Qwen direct's 42 rejections comprise 23 hard-constraint violations, nine false UNSAT answers and ten strict JSON-format failures. Prose/fences around JSON violate the declared output contract; this category alone does not establish incorrect scheduling reasoning. GLM direct's single rejection is a `remote_protocol_error` after 34.18 seconds, not the 1,800-second timeout. It received no usable response and has no returned model identity. Both capability responses and all 95 returned GLM scheduling responses report `glm-5.3-flash`; no model mismatch occurred.

Keep the GLM service failure in its primary 47/48 denominator. The secondary 47/47 acceptance among returned direct answers does not erase the failure, and its one-case gap against B does not demonstrate a reasoning advantage. No failure has been retried, excluded or replaced. The available transport record does not identify an exact network/server cause.

[The comparison audit](balanced-comparison-audit.md), [machine-readable summary](../../results/summary/balanced-comparison-20261017.json) and [evidence manifest](../../results/balanced-evidence-manifest.json) retain SAT/UNSAT and profile strata, conditional objective quality, time/token coverage, identity checks and exact trace paths. Regenerate the new graphs with `scripts/render_balanced_results.py`; analyse this pair separately from the 200- and 600-attempt studies. Preserve the earlier confound disclosure, three-family limitation and unconfirmed human review even when all B answers are accepted.
