# Diverse generation study

**Status: both full studies completed and audited.** Qwen3.6 and GLM5.3 Flash each completed all 2,000 scheduling attempts on the same 1,000 cases. [The comparison audit](../diverse-comparison-audit.md), [summary](../../results/summary/diverse-comparison-20261018.json) and revised report retain every outcome and distinguish infrastructure and execution phases. All existing results remain preserved. Human review is still unconfirmed. The preparation and authorization sections below describe the frozen protocol and its recorded transitions, not permission to launch another run. The TA's priorities remain generation, feasible scope, independent validation and failure analysis; the sample size is a team choice.
## Questions and denominators

Does performance change with scheduling interactions and larger descriptions? When a method fails, is the cause output format, extraction, scheduling, local solver limits or the provider? When both methods succeed, what is the difference in objective quality, time and token usage?

| Unit | Main study |
| --- | ---: |
| Canonical formal cases | 1,000 |
| Feasibility labels | 500 SAT; 500 UNSAT |
| Matched SAT/UNSAT pairs | 500 |
| Conservative generator families | 10 |
| Construction strata | 5; 200 cases each |
| Cases per mechanism/stratum | 20; 10 SAT and 10 UNSAT |
| Approaches per case | Direct LLM and LLM-to-CP-SAT |
| Scheduling attempts per model | 2,000 |
| Models | Qwen3.6 and GLM5.3 Flash |
| Main scheduling attempts across models | **4,000** |
| Optional extra description-order conditions | 24, separate from the main study |
| Optional extra attempts | 48/model; 96 across models, excluded from main budget |

The two methods and both models receive the same canonical descriptions. The optional conditions reuse 24 canonical problems; they test ordering, not independent problem instances or human paraphrase diversity. Their pre-outcome selection is balanced by label within every mechanism. Merely changing an activity name never qualifies as a new formal case.

## Construction coverage

| Mechanism | Intended reasoning challenge |
| --- | --- |
| Room contention | Aggregate demand for a single shared room across the whole activity set |
| Participant contention | Aggregate demand on a participant even when resources differ |
| Fragmented packing | Enough aggregate free time can still fail because each activity needs a contiguous interval |
| Precedence chain | Durations accumulate along an ordered chain |
| Precedence fork/join | Multiple branches must precede a common successor |
| Appointment collision | Fixed starts, half-open interval boundaries and shared participants |
| Release/deadline chain | Individually legal windows can conflict with cumulative ordering |
| Participant crossing | Different participant calendars must intersect for a joint activity |
| Resource/person crossing | An activity must simultaneously satisfy both person and resource restrictions |
| Mixed order/resource | Shared-resource ordering interacts with precedence and endpoint restrictions |

Five construction strata use 8, 12, 16, 24 and 32 activities. All eight-activity cases use 09:00–17:00, two participants and one room; their 30–90-minute activities differ from the TA’s illustrative 1–2-hour duration range. Report the **200 eight-activity cases** as the small-scenario view, and the other 800 as scale stress. Numerical windows, durations, assignments, precedence edges and preferences vary; both members of each label pair retain constraint kinds/counts and incidence. Joint ID and list permutations avoid locating a contradiction at a predictable prefix. The interaction graph must be connected, and every individual activity must retain a nonempty unary domain.

The schema remains one explicitly dated day with 30-minute slots, mandatory activities, fixed participant/resource assignments, capacity-one entities and weighted preferred-start windows. Whole-instance capacity constructions may use up to a full 24-hour horizon and 30-minute activities to fit 32 mandatory activities; these are synthetic shift-scheduling stress tests, **not the TA's eight-activity office scenario**. The immutable manifest and review packet give exact horizons, durations, dates and resource counts per case. Other mechanisms use a short contradictory subproblem embedded in a connected schedule.

“Easy” through “extreme” are construction labels. Activity count, available time, participants and rooms can change together, so the labels are not a controlled estimate of size alone or proof of increasing hardness. Whole-instance capacity contradictions require global demand reasoning but are arithmetically simple; small-core contradictions test whether a model can detect a local conflict in a larger request. Neither establishes hard global search complexity or an absolute upper bound on model ability. Empty individual domains, optional activities, uncertain durations, weekly calendars and allocation decisions are outside this particular design. It does not cover every edge case.

## Ground truth, diversity and review

1. Independently check every feasible witness with the arithmetic validator.
2. For whole-instance infeasibility, compare required occupancy with the union of available capacity for the required entity. For the remaining cases, exhaustively enumerate a small induced subproblem with primitive domain/overlap/precedence checks. A proved infeasible relaxation establishes full-case infeasibility; reaching the enumeration cap yields UNKNOWN and is rejected.
3. Independently run the full CP-SAT reference. Require a resolved label consistent with the construction evidence and preserve exact objective proof status. UNKNOWN never becomes UNSAT, and feasibility does not imply optimum proof.
4. Compute normalized hard fingerprints, per-mechanism structural metrics, connected-component counts, unary-domain statistics and matched-pair signatures. Check against preserved datasets. These checks detect concrete defects and duplicates; they do not establish real-world representativeness or independent sampling.
5. Review complete public renderings, schema and certificates in `review.json`. Never send that evaluator-only file to a measured model. Public prompts exclude labels, proofs and family/tier metadata.

The cases are deterministic, AI-assisted synthetic development inputs. They are not untouched held-out data. Ten generator families remain the conservative grouping even though 1,000 normalized hard fingerprints differ. Numerical variants within a mechanism remain related; topology diversity is reported separately from numeric fingerprints. A family bootstrap describes sensitivity to reweighting these ten designed classes, not a random population of scheduling problems.

Before live execution, recommend human review of at least one matched pair from each of the 50 mechanism/size cells (100 cases), a disclosed random supplement, and all identified ambiguities. This is a proposed review target, not a course-mandated quota. Record reviewers and scope honestly; do not infer review from passing tests or declare all 1,000 manually reviewed. Fixes create a newly prepared version/packet before any calls, with no silent changes to old evidence.

## Verified construction facts

The materialized manifest records **1,000 unique normalized hard fingerprints and 500 topology signatures** (50 per mechanism). Each topology is shared by a SAT/UNSAT pair. Every interaction graph is connected, and all four deadline/fixed-start presence profiles are label-balanced: neither 75/75, deadline-only 195/195, fixed-start-only 75/75 and both 155/155. These are construction facts, not model outcomes.

Independent certificates comprise 500 feasible witnesses, 100 whole-instance capacity contradictions and 400 local contradiction checks. A separate deletion test validates **1,840 feasible schedules** obtained by removing each activity in turn from the 100 capacity-UNSAT cases and removing its incident rules. Thus those cases require the complete mandatory activity set for infeasibility under that deletion definition. This does not imply computationally difficult search. Full CP-SAT references agree with all 1,000 labels, with proven preference optima for the 500 SAT references.

## Offline preparation

Use Python 3.12 and the pinned environment from the repository quick start. All commands below are offline; they neither load credentials nor call a provider. Use fresh destinations.

```sh
# Regenerate and independently verify the dataset in a new local directory.
PYTHONPATH=src .venv/bin/python evaluation/prepare_diverse_generation.py \
  runs/diverse-inputs-v1

# Prepare matched, source-bound model packets.
PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  runs/diverse-inputs-v1/cases.json runs/diverse-qwen-prepared \
  --design diverse-generation-2000 --model qwen3.6:35b \
  --qualification-policy strict_model_observe_backend_v1
PYTHONPATH=src .venv/bin/python evaluation/prepare_development_campaign.py \
  runs/diverse-inputs-v1/cases.json runs/diverse-glm-prepared \
  --design diverse-generation-2000 --model x-test-1 \
  --qualification-policy strict_model_observe_backend_v1
```

The checked fixture is in [`benchmarks/fixtures/diverse-generation-v1/`](../../benchmarks/fixtures/diverse-generation-v1/). Files contain the cases, independent proofs, bound manifest and human-review packet. Preparing campaign packets copies the exact inputs and binds source, runtime, prompt hashes, budgets and model identities. Later source/runtime changes require new packets. Production operation should use an immutable source snapshot and matching noneditable installation; `PYTHONPATH=src` above is the development preparation interface.

The optional wording selection and reordered descriptions are available in the dataset, but the main campaign has only its canonical controlled block. Adding the optional block requires its own explicit execution contract and matched analysis; changing `variants` inside a prepared main packet is rejected.

## Execution envelope

| Setting | Per model |
| --- | --- |
| Requested / required returned identity | Qwen: `qwen3.6:35b` / `qwen3.6:35b`; GLM: `x-test-1` / `glm-5.3-flash` |
| Ordering | Qwen first, then GLM |
| Scheduling completions | 2,000 |
| Capability completions / metadata requests | 2 / 1, excluded from scheduling metrics |
| Maximum HTTP requests | 2,003 |
| Output allowance per completion | 32,768 tokens |
| Reserved output-token allowance | 65,601,536; input tokens additional |
| Connect / read timeout | 30 / 1,800 seconds |
| Method / reference solver limit | 30 / 60 seconds |
| Retry policy | Zero retries; no correction calls |
| Backend policy | Observe fingerprints, require the exact response model |
| Transient failure policy | Record the failed attempt and continue to the next distinct request |
| Fatal conditions | Identity, authentication, TLS, integrity, quota and budget violations stop execution |

Across both models the envelope is **4,006 HTTP requests**, including qualification, and **131,203,072 reserved output tokens**. Reservations are not actual consumption, an input-token limit or a monetary cap. Record actual time/tokens and coverage; missing usage is unknown, not zero. Provider service time on larger cases is uncertain and can span days. Do not infer runtime by multiplying previous small-case averages without qualification.

Preparation is not live authorization. Existing completed allowances are consumed. A later launch must refer to the exact prepared pair and its envelope. A durable supervisor/tmux session cannot keep a sleeping laptop computing; pause at a safe request boundary before sleep, retain pending reservations and never silently reissue uncertain calls. Existing [operations](../usage.md) remain applicable.

## End-to-end qualification and analysis

The [saved verification receipt](../../results/summary/diverse-generation-verification-20261017.json) records the completed qualification: **974 distinct Python checks** passed across the regression and expanded-campaign suites after a targeted environment recheck, plus **9 dashboard JavaScript checks**. The full regression had one macOS native trust-service failure inside the restricted sandbox; all eight TLS checks passed outside it without changing verification policy or making external requests. Both complete mocked campaigns retained 2,000 attempts and exactly 2,003 requests each, including four intentionally injected failures. Both 3,067-file reproduction archives passed checksum verification and independently reproduced their complete analysis JSON exactly. The ten-mechanism figure was visually checked. These are offline engineering results, not Qwen/GLM performance measurements.

The installed, noneditable runtime and immutable source snapshot were also used to prepare and reload both model packets. Cases, 2,000 request-prompt hashes and all non-model settings match across the pair. All 153 protected evidence files checked against the prior repository remain unchanged; normalized hard fingerprints have no detected exact match in the five prior fixture bundles or six preserved result archives. This overlap check does not establish semantic independence. That offline qualification made no live model requests. Live execution and its later concurrency transition are recorded separately below.

Offline qualification must exercise both complete 2,000-attempt paths through a mocked HTTP provider, capability/identity checks, parsers, extraction, CP-SAT, independent scoring, durable records, exports and dashboard. Inject timeout, HTTP 502, malformed output and a hard-invalid schedule; verify exact request counts, no retries, retained failures and continued processing. Test fatal GLM identity mismatch separately. Check packet mutation rejection, archive integrity and deterministic offline replay. Mocked answers are engineering evidence; never add them to live model charts.

Preflight exposed 12 floating display-bound discrepancies, such as `3.999999999999999` for optimum 4 and `13.000000000000002` for optimum 13. The solver now records the **native integer lower bound** for its unscaled, zero-offset objective, preserving the raw double too. Exact integer-bound equality with the independently validated incumbent establishes the proof; a tiny floating consistency check alone cannot do so. Native OPTIMAL/proof checks and zero solver gap limits remain unchanged. Legacy records lacking the new optional field use `value - 1 < lower_bound <= value`. The [pinned response contract](https://github.com/google/or-tools/blob/v9.14/ortools/sat/cp_model.proto#L747-L759) defines the native integer bound; the [parameter contract](https://github.com/google/or-tools/blob/v9.14/ortools/sat/sat_parameters.proto#L284-L303) explains exact integer optimality. All 1,000 references pass the corrected scoring checks. Failed preflights and their source snapshots remain preserved.

Freeze these analyses before live inference:

- All-attempt acceptance, SAT validity and correct UNSAT, with exact numerators/denominators and paired method differences.
- Separate mechanism and size views; the eight-activity core and larger stress cases remain distinguishable. Do not select favourable cells after seeing results.
- Failure taxonomy with trace-backed examples: strict format, missing/wrong extracted constraints, invalid schedules, false UNSAT, local solver timeout/unknown, provider failure and identity rejection.
- Conditional preference optimum/gap only for valid gold-SAT outputs with proven reference objectives; invalid outputs receive no fabricated zero gap.
- Model-call, local solver and end-to-end time; token totals and missing-usage coverage. Summarize distributions rather than only means when tails are material.
- Family-grouped descriptive uncertainty; do not treat 500 paired constructions or 1,000 cases as independent families. Compare models under the same configured conditions while disclosing uncontrolled hosted backends.
- Optional order robustness only on its preselected paired bases, with additional attempts and denominators separately reported.

Keep all previous studies separate. The current report now incorporates the completed and audited pair; previous reports remain historical evidence. Inference and automated analysis finished ahead of the original 22/25/27 October preparation/run/analysis targets. The 30 October target now concerns substantive member review and delivery preparation. No further model, size, feedback-loop, repair or schema expansion is part of this phase. Human interpretation/contribution, model clarification, report review and presentation remain in the submission checklist.

## Authorized parallel continuation

The user authorized an explicit change from serial execution to **at most 16 in-flight scheduling attempts** for the remaining Qwen3.6 campaign and the subsequent GLM campaign. This is a separate execution protocol, not an unchanged timing condition. The operational adapter is `evaluation/parallel_development_campaign.py`; it reuses the frozen scientific pipelines, parsers, solver, validator and scoring functions.

The serial Qwen handoff was verified at **391 completed attempts and zero unresolved reservations**. Its first 295 attempts ran on macOS 26.5.2 and the next 96 on macOS 27.0.1. The remaining 1,609 Qwen attempts use concurrency 16 on macOS 27.0.1; GLM follows with its original 2,000-attempt allowance. Original metadata and capability checks for Qwen are reused. GLM retains its original one metadata request and two capability checks. The remaining maximum is therefore **3,612 HTTP requests**, within the original combined cap of 4,006; no extra inference is authorized by this protocol note.

Cases, request order, prompts, model identities, 32,768 output-token limits, 30/1,800-second connect/read timeouts, solver limits, seeds and no-retry settings remain unchanged. Qwen requests `qwen3.6:35b`; GLM requests `x-test-1` and must return `glm-5.3-flash`. Each request has a durable exclusive reservation before submission. A synchronized provider budget prevents concurrent overspending. Transient errors trigger a global 30-second pause in **new dispatch**, while already-issued requests finish and are saved. A fatal error or an operator stop prevents new dispatch and drains outstanding calls. Pending/uncertain records are never automatically reissued. This protocol does not guarantee that the shared service will accept 16 requests or provide a 16-fold speedup.

The original serial campaigns remain immutable. A separate derivative includes their completed records byte-for-byte and embeds their manifests, checksums and explicit execution/OS segment assignments. Recorded failures remain in the primary denominator. Do not amend historical results or silently recover a failed response with a replacement model call.

For analysis, use `analysis-with-execution-provenance.json` and `timing-by-execution-segment.json`. Report serial and parallel timings separately, further distinguishing OS segments. Mark method pairs spanning an execution or OS boundary. Compare Qwen/GLM parallel timing on the intersection of cases for which **both methods** ran under concurrency 16, retaining failures; primary outcome analysis still uses all 1,000 cases. Request durations overlap, so their sum is not parallel campaign wall time. Shared-service queueing, backend variation and local solver contention limit causal timing claims. The numerical reproduction export preserves unchanged scoring; its aggregate timing tables alone are insufficient for this mixed-execution campaign.

The operational sequence is a one-shot local macOS service with automatic restart disabled. A stop request drains active calls where the OS allows it; machine shutdown or forced termination can still leave uncertain reservations requiring manual reconciliation. Live completion must be established from durable records and final export receipts, not from preparation or launch alone.

### Observed concurrency-16 stop

The first 16 parallel Qwen requests produced 11 successful HTTP responses reporting `qwen3.6:35b`, four HTTP 429 rejections and one HTTP 502 error. Successful HTTP responses are not automatically accepted schedules. Under the unchanged fatal rate/quota-error policy, dispatch stopped and all outstanding calls drained, leaving **407 recorded Qwen attempts, zero unresolved reservations, and GLM not started**. The original 391 records are unchanged; each of the 16 new attempts has exactly one provider call. All five provider failures remain in the denominator. They are infrastructure outcomes, not demonstrated scheduling-reasoning failures.

The saved provider records establish HTTP 429 but do not retain the error body or rate-limit headers. This suggests rate/concurrency throttling after the burst, but does not prove a particular service limit or rule out a quota restriction. Do not claim that 16-way execution is supported or silently resume past the stop. A lower-concurrency continuation or a confirmed service allowance needs an explicit operational decision; neither may repeat saved calls. This checkpoint has a separately saved partial replay and OS/concurrency timing summary, not a completed-study export.

### Authorized eight-request continuation

After the fully drained 16-request stop, the user authorized an **eight-request maximum** for the remaining Qwen3.6 attempts, followed by GLM. The new derivative starts with all **407** saved Qwen attempts (391 serial and 16 at concurrency 16), leaving **1,593** Qwen scheduling calls. GLM retains 2,000 scheduling calls and its original three qualification/metadata requests: **3,596 maximum new HTTP requests** across the sequence. Qwen qualification is reused and none of its recorded calls, including the four 429 and one 502 errors from the parallel batch, is repeated.

The historical 429 stop is reconciled only for the explicitly identified immutable records under this authorization. Newly encountered 429, identity, authorization or other fatal failures still stop new dispatch and drain in-flight calls. Other settings and the existing transient-error policy remain unchanged. Eight-way service acceptance must be observed; it is not established by offline tests.

The derivative preserves old summary/start receipts under `prior-phase/` and binds their original bytes and locations in its transition manifest. Original campaigns remain untouched. Timing exports preserve serial, concurrency-16 and concurrency-8 membership separately, together with OS segments. Cross-model timing comparisons use cases where both methods ran at concurrency 8 in both models; all recorded failures remain in the primary outcome denominator. Do not treat the new execution phase as a complete or uniformly configured study before both models finish and their evidence is audited.

The initial eight-request live check observed eight overlapping workers, 13 newly completed responses all identifying `qwen3.6:35b`, and no new provider errors at that checkpoint (420 recorded attempts, eight in flight). Original records and phase receipts passed byte-integrity checks, and each new completed attempt had one provider call. GLM was still queued. This is launch/continuation evidence, not a completed benchmark or proof that subsequent requests cannot fail. The transition/recovery validation passed 81 targeted tests; a subsequent archive-receipt preservation adjustment passed its focused export test.

### GLM four-request continuation

Qwen completed all 2,000 scheduling attempts and its analysis export. GLM then completed 92 attempts at concurrency 8: 90 returned responses from `glm-5.3-flash` and two HTTP 429 rejections. The runner stopped dispatch and drained every issued request. The user subsequently authorized concurrency **4 for GLM only**, with **1,908** unattempted scheduling requests remaining. Existing GLM metadata/capability checks are reused; the maximum of 2,003 requests for that model remains unchanged. Its two failures stay counted and are not retried. The completed Qwen campaign is not rerun or modified.

The fresh GLM derivative preserves all 92 original records byte-for-byte and records the original 8-request and new 4-request timing segments. The historical 429 reconciliation is limited to those two explicit records; new fatal errors still stop dispatch and drain outstanding calls. All scientific settings remain frozen. The dashboard's completed-Qwen view is a byte-identical display copy, not another experiment.

Qwen's serial/16/8 execution and GLM's 8/4 execution must not be presented as uniformly controlled resource comparisons. Use per-model OS/concurrency strata and per-case phase labels. The final `timing-comparability.json` reports any common cases for which both approaches in both models used equal concurrency and OS; if that set is empty, no matched-concurrency timing claim is supported. All cases and provider failures remain in the primary outcome analysis, with concurrency differences disclosed as a service-execution limitation.

The initial live four-request check confirmed 93 total GLM records, four requests in flight and the first new response identifying `glm-5.3-flash`, with no new provider error at that checkpoint. All 92 prior GLM records and the complete Qwen campaign/export passed integrity checks. The focused offline GLM 8→4 recovery test passed, covering exact identity, no repeated calls, budget restoration and preserved timing segments. The frozen dashboard still has a static “Sequential · no retries” label; actual concurrency is established by the execution manifest, live worker and attempt records, not that legacy display text.
