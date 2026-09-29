# Li Hao method and report draft

Status: historical component draft for member review, 29 September 2026.
The canonical adapter and independent validation described as pending below are
now integrated. See [current follow-up](lihao-development-followup.md) and
[baseline evidence](main-baseline-validation.md) for current status.

Original checkpoint: These paragraphs describe the
implemented provider/direct components and the intended comparison; they are not
a completed study or a final report. No held-out experiments have run.

## Motivation

A revised schedule can satisfy all requirements while unnecessarily moving many
activities. Our study therefore considers both generating a schedule and repairing
a common starting schedule after a stated disruption. Within the proposed v1
domain, every activity has fixed duration and mandatory participants/resources.
The repair priorities are moved activity count, total absolute slot shift, then
preference penalty. This exposes the distinction between feasibility and stability.
The planned empirical question is when direct language-model scheduling is useful
and when formal solving helps, including failures in translating the request.

## Related-work starting comparison

This table uses the primary abstract pages consulted on 29 September 2026. It is a
bounded starting comparison, not a claim to have reviewed every experiment in
these papers. Detailed numerical claims require checking the full papers before
submission.

| Work | Source-grounded description | Project relationship and boundary |
| --- | --- | --- |
| [Zheng et al., NATURAL PLAN (2024)](https://arxiv.org/abs/2406.04520) | Natural-language trip, meeting and calendar-planning tasks with supplied task information | Motivates supplying sufficient information and separating planning from external information retrieval. Its reported scores do not predict our model or domain. |
| [Hao et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.176/) | Formalizes multi-constraint planning for satisfiability solvers and discusses infeasible requests | Motivates the planned formal-tool comparison. Solver correctness for an extracted model does not establish fidelity to the original request. Our project uses a fixed CP-SAT compiler and keeps hard constraints unchanged. |
| [Sharma and Sharma, SCHEDBench (2026)](https://arxiv.org/abs/2608.00991) | Studies constraint faithfulness in natural-language combinatorial scheduling | Motivates the planned wording-sensitivity analysis. Shared generation/repair settings and the selected language variants must still be audited in our own benchmark. |

Our intended contribution is a scoped comparison of direct scheduling, extracted
specification solving, repair disruption and wording sensitivity. No superiority
or strong novelty claim follows from the current component checks.

## Implemented direct/provider method

The direct component builds a system prompt and a public problem message. For
repair it adds the same original schedule that the eventual solver-augmented path
must receive. It makes one semantic model call and parses strict JSON. It has no
access to gold constraints, oracle solutions, solver tools, or validator feedback.
All required activity labels must come from the public problem representation.

The parser preserves the declared SAT/UNSAT/UNKNOWN status separately from parsing
outcomes. It rejects duplicate JSON keys, Markdown wrappers, malformed entries,
noninteger or negative starts, and missing/duplicate/invented activities. Sorting
entries by ID is the only schedule normalization. A structurally accepted SAT
claim still needs independent gold validation; a direct UNSAT claim is a prediction.

The SoCLaaS adapter uses HTTPX with explicit connect/read/write/pool timeouts,
disabled redirects, and a fixed development endpoint. It records the returned
backend ID, per-attempt elapsed time, status, finish reason and reported token
usage. Missing usage stays unavailable. It exposes static error categories instead
of provider error bodies or exception strings. Transport retry limits are explicit
and budgeted; uncertain read/write failures are not automatically retried. HTTP
transient failures may be retried only within the configured attempts and shared
request/output-token reservation budget. Currency, input tokens and full-run
budgets remain runner responsibilities. HTTPX timeouts bound network inactivity,
not an absolute wall-clock deadline; see its [timeout documentation](https://www.python-httpx.org/advanced/timeouts/).

The one-case live CLI creates a private record before sending, refuses to overwrite
an existing record, retains interruptions, and atomically writes completion. It
records the public inputs, runtime, source/config/prompt hashes and response.
It is not the batch/resume/evaluation runner assigned to Yong Qing.

The current component records are explicitly separate from Yao Xiang's pending
canonical `NaturalLanguageView`, `Schedule` and `PipelineResult`. Final
`run_direct(nl_view, model_config)` assembly and independent gold checks remain
integration tasks. No substitute scheduling schema or validator was added.

## Evidence and limits

The two authorized development calls used explicit `qwen3.6:35b`, one attempt each,
with at most 1,024 requested output tokens per call. The provider reported 844
input and 96 output tokens (940 total). Generation returned A=0, B=1; repair
returned A=1, B=2 from the common old A=0, B=2 schedule. Both parsed as SAT.
The tiny repair's movement and shift are hand-checkable; neither record has yet
been checked by the shared independent validator. These observations do not
estimate accuracy, robustness, objective performance on a benchmark, model
eligibility, or one approach's advantage over the other.

The connectivity check used `default`, which returned `qwen3.6:35b` with HTTP 200.
Its text did not exactly match the requested `OK`; retain that distinction rather
than describing it as exact instruction-following success. No additional call was
made to repair that acknowledgement. Advanced structured-output/reasoning options,
rate limits, institutional pricing and quota remain unverified.

## Responsible AI and contribution disclosure draft

Only synthetic schedules were sent. Credentials remain outside Git and model
messages. The software proposes schedules; it does not edit calendars or contact
participants. Prompt instructions treat embedded instruction-like descriptions as
data, but this is not a guarantee of resistance to misleading input.

Minimum total disruption may distribute inconvenience unevenly. The future
evaluation should report each participant's movement burden and discuss objective
trade-offs, without claiming that fixed assignments solve fair workload allocation.
Negotiability and missing real-world constraints remain limitations.

Li Hao authorized this implementation session and chose the development model and
bounded checks. Codex generated the implementation, tests, documentation drafts and
verification commands. Li Hao's code review, understanding, teammate reviews and
course submission remain human responsibilities; no review or work hours are
claimed completed by this draft. Report statements about solver/evaluation methods
and research findings must be completed and checked with the other owners.
