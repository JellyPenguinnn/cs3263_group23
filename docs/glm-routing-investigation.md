# GLM routing and identity investigation

## Observed failure

The difficulty study requested `x-test-1` with an explicit required response identity of `glm-5.3-flash`. Qwen3.6 completed its separate 200-attempt campaign and exported analysis. GLM stopped after 22 controlled attempts: 20 reported GLM, one returned HTTP 502, and the last reported `qwen3.8:27b`. No realistic or additional-wording block started. These partial outputs are preserved, not merged into a completed GLM comparison.

The mismatched request started at **2026-10-13 10:07:21 UTC**. Its attempt ID is `7b1e7ef960703490d68d6f524d5b63681cc4063e6399090851bd66ba378a0375`. The saved execution contract records `model: x-test-1`, `max_tokens: 32768`, `stream: false`, no retries and 30/1,800-second timeouts. The saved provider response reports `qwen3.8:27b` with fingerprint `vllm-0.26.0-da484106`; preceding GLM responses reported `vllm-0.31.0-tp2-64d866e2`.

## What the client and gate do

The installed provider matches the preserved source byte for byte. It sends the configured model ID directly in the HTTP body, disables environment-proxy routing and redirects, and copies the response JSON's top-level `model` field into the saved record. It has no model fallback. The alias mapping affects only the expected identity checked by the evaluator; it does not modify requests or responses.

The gate therefore correctly rejects this record. A different backend fingerprint alone is allowed by the development protocol; a different model is not. The observed boundary of the fault is the service-reported identity. Client-side evidence cannot distinguish a server routing/fallback error from incorrect server response metadata, nor establish the underlying weights used. Only the service operator can confirm that internal cause.

## Independent checks

On **14 October 2026**, the authenticated model catalogue still described `x-test-1` as “Testing GLM 5.3 Flash”; it exposed no separate `glm-5.3-flash` model ID. Three standalone HTTP requests containing only `Reply with exactly OK.` all returned `glm-5.3-flash`. They bypassed `SoCLaaSProvider`, the benchmark runner and its identity gate, while retaining verified TLS, the approved endpoint and the same request controls. The exact response bytes, hashes, timing and usage were saved in a separate private diagnostic directory. Total reported diagnostic usage was 209 tokens, including 51 input and 158 completion tokens; these calls are not benchmark observations.

This establishes that the alias currently works for those requests. It does **not** establish that the intermittent problem has been permanently fixed. The official documentation link was unavailable from the investigation environment; no undocumented fallback or routing parameter was added.

## Rerun contract

An explicitly authorized fresh campaign may use the recovered route with the original identity check intact. Preserve the original 22-attempt campaign; use a new output directory and do not resume through its fatal mismatch. Retain the same frozen source/runtime, case bundles, prompts, scoring, solver limits, 200 scheduling calls, two capability checks, one metadata request, output ceiling, timeouts and no-retry policy. Keep routing diagnostics outside all study denominators. Qwen3.6 requires no rerun.

If any response again reports a different or missing model, preserve it and stop further dispatch. A successful startup or several matching responses do not qualify the whole run: a complete GLM comparison requires all planned records and the end-of-run identity, replay and archive checks. For a permanent routing fix, provide the service operator with the timestamp, requested/returned IDs and fingerprints above, and request a stable GLM route with no cross-model fallback. Never send credentials in that report.
