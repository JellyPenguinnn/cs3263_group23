# Integrated development baseline — 29 September 2026

The three member contributions are merged at `eea2e09` on `main`. The subsequent integration changes were requested by the user; after validation, the user explicitly authorized committing and pushing them to main. This baseline runs both actual model pipelines, validates their answers independently, and preserves reproducible evidence. It does not guarantee correct model answers or complete the final course experiment.

## Architecture and integration changes

The system follows planning.md Sections 6–9 and 14:

1. Evaluator-only benchmark cases preserve original/updated repair problems, the common starting schedule, reference witnesses and labels.
2. The renderer creates a common public description for both approaches. Neither receives hidden labels, gold solutions or evaluator metadata.
3. A uses one direct model call and strict schedule parsing. B uses one extraction call, the canonical schema and the fixed CP-SAT compiler. Generation minimizes preference penalty; repair sequentially minimizes moved count, total shift and preference penalty.
4. The independent validator checks outputs against gold using direct arithmetic. Solver proof status and extraction fidelity remain separate from schedule validity.
5. The runner writes a durable reservation before each call, preserves raw responses and results, independently scores them, and records hashes. Replay recomputes validation, metrics and figures without model or solver calls.

Integration fixes:

- Added `evaluate-plan`: checks every reference and reports the exact request count, requested output-token allowance and prompt sizes without credentials.
- Added per-attempt progress on stderr and meaningful nonzero exit codes for exhausted/stopped batches.
- Authentication, rate-limit, HTTP, TLS and timeout/transport failures stop execution and remain durable across resume. TLS failures have a sanitized distinct category and are never automatically retried.
- Rejected malformed configuration/case objects at their boundaries instead of leaking incidental TypeError/KeyError tracebacks.
- Made OR-Tools a required runtime dependency and retained the old solver extra as a compatibility alias. Existing version pins were preserved.
- Recorded TLS/runtime dependency versions and packaged certificate hashes alongside Python source and prompt hashes. Installed preflight does not require Git; unavailable revision identity remains null while source hashes are retained.
- Extended installed-package CI to generate and independently check all 30 development references.
- Fixed Linux TLS: the server supplies its leaf without the intermediates. Two certificates downloaded from the official issuer complete the path to existing certifi roots; partial-chain trust stays disabled. No new root or leaf trust anchor was introduced. macOS retains native verification. See [issuer provenance](../configs/development/tls-issuer-provenance.json).

No prompts, scientific objectives, gold checks or parsing rules were relaxed to improve the observed results. No response was repaired by hand, retried or replaced by canned output.

## Executed verification

| Check | Observed result |
| --- | --- |
| Current checkout full suite | 278 passed |
| Fresh noneditable macOS ARM64 package | 278 passed; pip check passed |
| Isolated noneditable Linux ARM64 package | 278 passed; pip check passed |
| Full generated development references | Same case-bundle hash and 28 SAT / 2 UNSAT labels across platforms; witnesses independently validated |
| TLS rejection tests | Untrusted certificate and wrong hostname rejected; supplemental issuer chain alone not trusted |
| Credential-free HTTPS | HTTP 200 on macOS and Linux with verification enabled |
| Live run | 60/60 HTTP 200; returned model qwen3.6:35b throughout; finish_reason stop throughout; zero retries/provider errors |
| Completed resume | All 60 records reused; a callback that would fail on any new provider request was never invoked |
| Cross-platform replay | Original frozen-run, final macOS and final Linux summaries exactly equal |
| Exports | CSV, JSON and PNG/PDF figures generated; macOS figures visually inspected |

Routine verification used `python -m pytest -q`, `python -m pip check`, installed `scheduling benchmark-generate`, `scheduling evaluate-plan` and `scheduling evaluate-replay --figures`. All Python commands used the appropriate explicit virtual-environment executable. Tests remain network-blocked; certificate tests use local socket pairs and temporary OpenSSL certificates. Live inference was explicitly selected and separately authorized.

The Linux container base was `python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f`. It received only a credential-free source snapshot and later the saved synthetic run. No credential was copied to Linux. Hosted CI could not be inspected through the unauthenticated local GitHub CLI; these are executed local checks, not a claimed remote CI result.

## Actual live development results

Run: `main-baseline-20260929-01`. Config: [main-baseline.json](../configs/development/main-baseline.json). Thirty development cases cover six fixtures plus activity-count, slack, interaction-density and resource-contention sweeps, with 2–12 activities and both generation/repair. Each case received one canonical description and one call per approach.

Authorized ceiling: 60 calls × 8,192 output tokens = 491,520 requested output tokens, sequential, no retries, 10 seconds of CP-SAT per B case. Gold references had a separate 30-second solver budget. The entire 60-call allowance is consumed. Reported usage: **76,876 input + 41,100 output = 117,976 tokens**. Currency cost is unavailable.

Accepted answers include gold-valid schedules and correct UNSAT answers; every failed answer stays in its denominator.

| Task | Direct A | Solver-augmented B |
| --- | ---: | ---: |
| Generation | 12/17 (70.6%) | 13/17 (76.5%) |
| Repair | 6/13 (46.2%) | 12/13 (92.3%) |
| All development cases, descriptive | 18/30 (60.0%) | 25/30 (83.3%) |

A produced ten invalid schedules (availability/deadline violations) and two false UNSAT claims. B produced five schema-invalid extractions: each added an unsupported resource `capacity` field, despite the schema's fixed capacity-one semantics. These are model instruction-following failures; the parser correctly refused them. All 25 schema-valid B extractions matched the normalized gold specification and their answers were accepted. This does not establish general extraction reliability.

The small development matrix is imbalanced (28 SAT, 2 UNSAT) and has tiny sweep cells. Results are descriptive, not a held-out superiority claim. The complete summaries retain task/class denominators, paired outcomes, conditional objective gaps and usage coverage. No paraphrase/repeat inference was authorized, so no live robustness result is claimed.

## Evidence, replay and handoff

- [Aggregate receipt](../configs/development/main-baseline-verification.json)
- [Full aggregate development summary](../results/summary/main-development-20260929.json)
- Private raw run: `runs/main-baseline-20260929-01/`
- Frozen live input/config/source: `runs/main-baseline-20260929-01-input/` and `runs/main-baseline-20260929-01-source/`
- Final tested source, macOS/Linux logs and file checksums: `runs/main-baseline-verification-20260929/`
- CSV/JSON/PNG/PDF export: `artifacts/main-baseline-20260929-01/`

The live run used the pre-Linux-fix installed source, frozen before its first request. Subsequent Linux certificate packaging/provenance changes did not affect prompts, constraints or scoring; replay equality with the final package was checked on both platforms. The source guard intentionally prevents resuming an old run under changed source. The exact frozen installation successfully resumed without additional requests. Preserve the original archives when sharing a sanitized reproduction package.

Use the runnable workflow in [README.md](../README.md#run-the-integrated-development-baseline). Another live run needs a fresh cap and new run ID. Maintain the certificate supplement if the server changes issuer or before YE2 expires in September 2028; service-side full-chain configuration remains the preferable upstream repair.

Remaining research gates: human mathematical/language review, independently written realistic cases, balanced held-out data, final-model eligibility/access/qualification, protocol freeze and main experimental runs. Agent verification is not independent teammate review. The implementation is an operational research baseline; course-level Gates C/D and final report completion are not claimed. AI-assisted integration, code changes and test execution are disclosed here.
