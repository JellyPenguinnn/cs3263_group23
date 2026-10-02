# Li Hao integration follow-up — 30 September 2026

Local work on `lihao-llm-baseline`, fast-forwarded to GitHub main
`f12e5216e4777ef345240d06922be0917200d539` before editing. This brings in
Yao Xiang's R1–R3 and Yong Qing's v2 benchmark/frozen controls without rebuilding
completed components. No changes were dropped. After the assignment audit, the
user authorized committing and pushing this checkpoint to `lihao-llm-baseline`.
The Git handoff records the resulting commit and remote verification; this does
not authorize a main merge or publication of the local raw archive.

## Assignment audit: Sections 4–5

**The current development implementation is complete and validated for this
checkpoint; Li Hao’s full responsibilities through final course delivery are
not complete.** The publication audit rechecked Sections 4–5, R4, provider
requirements, the weekly milestones and course-delivery assignments. All 83
qualified runtime/test/prompt/build files still match the installed verification
snapshot, and the source-manifest and local-archive checksums match their receipt.
Only handoff documentation and publication metadata changed after qualification.

| Responsibility | Current evidence | Remaining work or gate |
| --- | --- | --- |
| Direct generation/repair, strict parser, prompts and provider | Existing implementation retained; 18 added tests exercise protocol failures and real-adapter/runner boundaries, without network calls | Human scientific-assumption review; final eligible-model qualification when selected and separately capped |
| WP3: direct/provider failure analysis | Original analysis retained; both saved datasets replay identically. Later v2 pilot has seven invalid A schedules, one false UNSAT and one prose-wrapped JSON failure | No evidence supports claiming a general accuracy improvement; any prompt experiment needs a new configuration/run and live cap |
| R4: proof-aware explanations and CLI | Integrated R3 consumer checked; three saved examples render on both platforms: accepted repair, false UNSAT and schema-invalid extraction | Yao Xiang reviews proof semantics; Yong Qing reviews gold labels; human sign-off is outstanding |
| WP4: provider/runner and frozen-mode integration review | Approved malformed-envelope stop/resume fix; actual adapter with synthetic HTTP transport checks auth, rate, TLS, timeout, malformed/deep JSON, and model-answer failure in both development/frozen modes | Final model/access/cap and reviewed study freeze are still required |
| WP5: package, CI and portable reproduction | Fresh noneditable macOS/Linux ARM64 installs, assets, complete tests, reference checks, v2 integration, exact historical replay and local archive verification | Hosted CI status and independent teammate replay remain unverified; normal review is required before main integration |
| WP2 review rotation: benchmark wording | Technical audit of 144 v2 cases × three renderings; evaluator metadata removal does not change either pipeline's prompt, original repair schedules remain intact, variant facts agree | Human language/semantic review and 12 independently authored realistic scenarios remain pending; templates are limited variation |
| Report/demo/responsible AI | Existing method, motivation/related-work and four responsible-AI drafts retained; demo commands verified and later pilot linked separately | Human source checking, final study/results discussion, actual contribution disclosure, timed rehearsal and course submission receipts |

Public-dataset adaptation, search tuning, feedback/repair loops, fairness-objective
changes and additional UI are optional, not missing required baseline modules.
No such optimization was added. The dashboard remains read-only.

## Changes and scientific impact

A malformed HTTP-200 response envelope already produced
`invalid_provider_response`, but the runner omitted that category from its stop
policy. It could spend the rest of a batch's authorized calls on a broken
provider. With the user's explicit coordination approval for Yong Qing-owned
runner code, that category now stops further calls and a matching resume.

The adapter also converts excessively nested response JSON into the same
recorded failure instead of allowing a `RecursionError` to escape accounting.
Malformed model listings now raise a safe `invalid_model_listing` category.
Usage remains unknown when absent; no retries, hidden corrections or alternate
provider were added. HTTP/TLS failure details remain sanitized.

A valid provider envelope containing an invalid model answer still produces an
ordinary recorded `INVALID_OUTPUT` and allows the batch to continue. The tests
check both sides of this boundary in development and frozen modes, durable
reservations, stopped resumes, missing usage and preserved denominators.

No prompt, schema, solver, objective, metric, dependency or historical record
was changed. Future inference must use a new source contract/run ID. Both old
summaries reproduce exactly under the new code; this does not retroactively
change their outcomes or constitute new model evidence.

Installed verification exposed a separate test defect: the dashboard refresh
test used 29 September as its fixed newest timestamp. On 30 September its own
fixture records were newer. The test now derives the new event from the latest
fixture timestamp plus one second. Dashboard sorting and production behavior
are unchanged; the original failed qualification logs are retained.

## Executed verification

[Machine-readable receipt](../configs/development/lihao-integration-verification-20260930.json)
and ignored `runs/lihao-integration-20260930-01/` contain source hashes, commands
and logs. Both installs used `pip install --require-hashes -r requirements.lock`,
a wheel built with `pip wheel --no-deps --no-build-isolation`, and noneditable
wheel installation. No editable or `PYTHONPATH=src` fallback qualified these builds.

| Check | macOS ARM64 | Linux ARM64 |
| --- | --- | --- |
| Python / OpenSSL | 3.12.2 / 3.6.3 | 3.12.14 / 3.0.22 |
| Node | 20.15.0 | 18.20.4 |
| `python -m pytest -q` | 416 passed | 416 passed |
| `python scripts/check_installed.py` | Three prompts and four runtime assets match source | Same |
| `python -m pip check` | Passed | Passed |
| `node --check src/scheduling/dashboard/static/app.js` | Passed | Passed |
| `node --test tests/frontend/dashboard.test.cjs` | 3 passed | 3 passed |
| Legacy generate + `evaluate-plan` | 30 checked: 28 SAT, 2 UNSAT | Same |
| `python evaluation/v2_qualification.py NEW_PATH` | 144 cases, 864 accepted canned attempts; matching resume makes no extra attempts | Same |
| `evaluate-replay --figures` on each saved run | Exact 60-record and 24-record summaries; figures exported | Same |
| Three documented `scheduling explain` examples | Passed | Passed |

The 76 targeted provider/runner/frozen tests passed before broad qualification;
the corrected dashboard's six tests passed separately. Full suite results above
include both changes. The local Linux environment is Debian Bookworm in Colima,
using the image digest recorded in the receipt. Its initial host bind mount did
not expose the temporary directory, so the sanitized snapshot was copied into
the container. No credential directory was mounted or copied.

CI now verifies installed assets and the full v2 offline integration in addition
to its existing tests/frontend/reference checks. It uses Node 20 on both hosted
platforms; the local Linux Node 18 check is explicitly distinguished. GitHub CLI
was unauthenticated and the connector returned 404, so no hosted check success
is asserted. This ARM64 container execution is not an x86/Windows qualification
or independent human replay.

**Zero live model requests were made.** All 864-attempt checks use explicitly
canned answers and test integration rather than model accuracy. The historical
24-call pilot remains a six-family development sample, with A accepted 3/12 and
B 12/12; it is not a held-out or general superiority result.

## Wording review and next handoff

The renderer covers duration, all assigned participants/resources, full-window
containment, capacity-one non-overlap, time origin, half-open intervals, release,
deadline, fixed start, precedence, blocking and weighted start preferences.
Repair receives the complete updated problem and common original schedule with
the unchanged lexicographic objective. Technical audit results and all 432 public
text hashes are in the local receipt. Removing evaluator labels, witnesses,
objectives, justification and grouping/difficulty metadata left both prompt paths
unchanged. This is a bounded noninterference check, not proof of language fidelity.

The current paraphrase only adds an introductory sentence and changes precedence
wording; reordering shuffles the same fact lines. These variants cannot establish
coverage of realistic natural language. Li Hao should review Yong Qing's next
human-written scenario packet against independently derived gold specifications;
the team must record authorship, simplifications and actual review decisions.
Do not label generated template examples independently human-written.

The next concrete handoff is Yao Xiang/Yong Qing review of the provider stop
boundary, wording packet and R4 proof/gold distinctions, followed by independent
replay of the sanitized archive. Review the published member-branch checkpoint
before integration into main. Final model selection/eligibility, fresh split allocation,
protocol freeze and a new cap must precede final-model qualification and held-out
runs. The proposal receipt and final course submissions remain unconfirmed.

The local archive is `artifacts/lihao-integration-replay-20260930-01.tar.gz`, with
308 files and a separate checksum file. The tracked receipt gives its SHA-256.
It contains the qualified source/wheel, both original synthetic run datasets,
checksums, qualification logs and `REPLAY.md`; final handoff-only documentation
postdates the source snapshot. The archive was unpacked, all content checksums
verified and both summaries replayed. It has not been shared externally, and
agent-executed replay is not teammate sign-off. Existing archives remain intact.

This work and its technical audit were AI-assisted. It does not record human
hours, understanding, review, rehearsal, model eligibility or course approval.
