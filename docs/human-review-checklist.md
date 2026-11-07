# Human review and contribution worksheet

Use this worksheet for the selected case-level checks before submission. The group has confirmed its actual work allocation and that all members have read and understood the project, report and slides. Case-review decisions and findings still need to be recorded by the reviewers; reading the report alone does not complete those checks. No student IDs, email addresses or API keys are needed here.

## How to use this worksheet

1. All three members start with [E1: the report worked example](reviews/human-review-packet.md#e1). Read the request, explain the room timetable and penalty calculation, and discuss why the direct answers fail.
2. Review your assigned cases below. Open the original request first, write your interpretation, then expand the gold specification and saved outputs. The expandable evidence is a convenience, not a blinded study.
3. For each case, check durations, availability, shared entities, precedence, fixed starts/deadlines and preferences. If feasible, check a witness or saved valid schedule; if infeasible, explain a contradiction. Inspect the four recorded model/method outcomes and explain at least one meaningful acceptance or rejection.
4. Record a concrete check or discrepancy in the finding column. Use **agree**, **issue**, or **uncertain**, followed by a specific reason. “The program says so” is not sufficient evidence. Leave a case unchecked if the review is incomplete.
5. Resolve findings together, then complete the shared final checks. The optional contribution prompts can help add useful specifics. If a request/gold mismatch affects results, assess and document its effect; preserve the original records rather than editing them in place.

This is a manageable retrospective review sample, not a course-mandated quota, a new benchmark, or a claim that every case was manually checked. C01–C20 cover ten mechanisms, both feasibility labels and all five sizes (four cases per size). E1–E4 are selected report examples. A coverage pair is not necessarily a matched construction pair. Case IDs and source hashes are in the companion packet; use the short labels here.

## Selected cases

| Case | What to examine | Activities | Lead reviewer | Reviewed | Finding / concrete check |
| --- | --- | ---: | --- | --- | --- |
| [C01](reviews/human-review-packet.md#c01) | Appointment collision | 8 | Li Hao | ☐ | __________ |
| [C02](reviews/human-review-packet.md#c02) | Appointment collision | 8 | Li Hao | ☐ | __________ |
| [C03](reviews/human-review-packet.md#c03) | Fragmented packing | 12 | Yong Qing | ☐ | __________ |
| [C04](reviews/human-review-packet.md#c04) | Fragmented packing | 12 | Yong Qing | ☐ | __________ |
| [C05](reviews/human-review-packet.md#c05) | Mixed order resource | 16 | Yao Xiang | ☐ | __________ |
| [C06](reviews/human-review-packet.md#c06) | Mixed order resource | 16 | Yao Xiang | ☐ | __________ |
| [C07](reviews/human-review-packet.md#c07) | Participant contention | 24 | Li Hao | ☐ | __________ |
| [C08](reviews/human-review-packet.md#c08) | Participant contention | 24 | Li Hao | ☐ | __________ |
| [C09](reviews/human-review-packet.md#c09) | Participant crossing | 32 | Yong Qing | ☐ | __________ |
| [C10](reviews/human-review-packet.md#c10) | Participant crossing | 32 | Yong Qing | ☐ | __________ |
| [C11](reviews/human-review-packet.md#c11) | Precedence chain | 8 | Yao Xiang | ☐ | __________ |
| [C12](reviews/human-review-packet.md#c12) | Precedence chain | 8 | Yao Xiang | ☐ | __________ |
| [C13](reviews/human-review-packet.md#c13) | Precedence fork join | 12 | Li Hao | ☐ | __________ |
| [C14](reviews/human-review-packet.md#c14) | Precedence fork join | 12 | Li Hao | ☐ | __________ |
| [C15](reviews/human-review-packet.md#c15) | Release deadline chain | 16 | Yong Qing | ☐ | __________ |
| [C16](reviews/human-review-packet.md#c16) | Release deadline chain | 16 | Yong Qing | ☐ | __________ |
| [C17](reviews/human-review-packet.md#c17) | Resource person crossing | 24 | Yao Xiang | ☐ | __________ |
| [C18](reviews/human-review-packet.md#c18) | Resource person crossing | 24 | Yao Xiang | ☐ | __________ |
| [C19](reviews/human-review-packet.md#c19) | Room contention | 32 | Li Hao | ☐ | __________ |
| [C20](reviews/human-review-packet.md#c20) | Room contention | 32 | Li Hao | ☐ | __________ |
| [E1](reviews/human-review-packet.md#e1) | Report worked example | 8 | All three | ☐ | __________ |
| [E2](reviews/human-review-packet.md#e2) | Invented-deadline example | 8 | Yao Xiang | ☐ | __________ |
| [E3](reviews/human-review-packet.md#e3) | Omitted-constraint example | 32 | Yao Xiang | ☐ | __________ |
| [E4](reviews/human-review-packet.md#e4) | Valid but suboptimal example | 24 | Yong Qing | ☐ | __________ |

**Review date(s):** __________
**Unresolved issues and who will follow up:** __________

For longer findings, copy this entry:

> Case: ____ · Reviewer: ____ · Date: ____
> My interpretation before opening gold: ____
> Specific constraint, schedule interval, contradiction or preference calculation checked: ____
> Comparison with gold and the saved outputs: ____
> Verdict (agree / issue / uncertain), reason and evidence: ____
> Required correction or follow-up, if any: ____

## Yao Xiang — formal methods review and contribution

- [ ] Check start-slot domains, half-open intervals, precedence and shared-resource non-overlap against Section 3 and a selected case.
- [ ] Explain the preferred-start penalty and the repair priority: moved activities, then absolute shift, then preference penalty. Explain why a timeout is not an infeasibility proof.
- [ ] Review E2 and E3: identify the invented or omitted constraints and explain why correct CP-SAT solving can still produce an incorrect answer to the original request.
- [x] Read and understood the project and complete report, as confirmed by the group. Practise explaining both methods and their limitations aloud.

**Optional contribution detail — use verified facts if adding an example:**

> My responsibilities covered mathematical formulation, constraint-extraction semantics and CP-SAT compilation. I personally [designed / implemented / reviewed / checked] __________; one concrete decision or finding was __________, supported by __________. Codex or Claude Code assisted with __________, and I personally checked __________.

**Name and review date:** __________

## Yong Qing — evaluation review and contribution

- [ ] Explain 1,000 generation cases, 500 feasible / 500 infeasible, two methods and two models: 4,000 attempts, not 4,000 independent cases.
- [ ] Verify the report’s acceptance and feasibility tables against the saved summary; check that optimality uses only valid feasible outputs.
- [ ] Review E4 and explain why a valid schedule can be suboptimal. Check one extraction error and distinguish mathematical, output-format and infrastructure failures.
- [ ] Explain the ten related generator families, synthetic development data and shared-reference-compiler limitations. Read the whole report.

**Optional contribution detail — use verified facts if adding an example:**

> My responsibilities covered benchmark design, independent validation, evaluation metrics, failure analysis and interpretation. I personally [designed / implemented / reviewed / checked] __________; one concrete decision or finding was __________, supported by __________. Codex or Claude Code assisted with __________, and I personally checked __________.

**Name and review date:** __________

## Li Hao — pipeline and reproducibility review and contribution

- [ ] Trace a request through both pipelines: public request → direct answer, or extraction → fixed compiler → solver; then independent gold validation and saved result.
- [ ] Verify the model names and service IDs in Section 5. Explain one call per case/method, no retries, and retention of failed attempts.
- [ ] Check the token/time definitions and missing-usage counts. Explain why service failures and changing execution conditions prevent a controlled model-speed claim.
- [ ] Check that the report tables/figures link to preserved evidence. Read the whole report; optionally perform the offline replay below.

**Optional contribution detail — use verified facts if adding an example:**

> My responsibilities covered LLM/provider integration, end-to-end wiring, experiment operations, reproducibility and quality assurance. I personally [designed / implemented / reviewed / checked] __________; one concrete decision or finding was __________, supported by __________. Codex or Claude Code assisted with __________, and I personally checked __________.

**Name and review date:** __________

The agreed responsibilities above are context, not proof of a particular implementation action. Describe actual work, including review or interpretation when that is what you personally did. Do not claim independent authorship of AI-generated material. The report already contains the group-confirmed allocation and AI-assistance disclosure. A longer per-person account is optional; add detail only where it clarifies actual human and AI contributions.

## Shared final review

- [ ] All three can explain the main result, one direct-method failure and one extraction failure without reading a script.
- [ ] Confirm generation is the main 4,000-attempt study; earlier repair/fictional/wording results are separate. The 24 optional reordered conditions in the latest design were not run.
- [ ] Discuss privacy, unequal inconvenience, hard versus soft requirements and user control. Explain why optimality does not establish fairness or real-world reliability.
- [ ] Review all findings and resolve or explicitly disclose remaining uncertainty. Do not mark unreviewed cases as complete.
- [x] Confirm the actual work distribution across the group and disclose Codex and Claude Code. Optional personal examples can clarify the allocation but are not a separate course-required form.
- [ ] Confirm the remaining single-day/30-minute and preferred-start-only scope clarification against the TA feedback. Qwen/GLM model acceptance has already been reported by the team.
- [ ] Confirm names, student IDs and emails in the **local private report only**; rebuild and inspect the final public/private PDFs after edits.
- [ ] Check the final report format: at most ten body pages, single column, single spaced, at least 11-point text and one-inch margins; cover/references excluded.
- [ ] Rehearse the prepared slides and script, create a recording if requested, and check timing for 15 minutes plus five-minute Q&A, and check current Canvas submission arrangements.

**Team review discussion date:** __________
**Remaining actions, owner and due date:** __________

## Optional reproducibility check

- [ ] A teammate performs the [offline replay](evidence.md) in a clean compatible environment. Record the command, outcome and any discrepancy. No live model calls are required.
- [ ] Keep a verified private backup off this computer. Do not upload private identity details or credentials to the public repository.

## References for the review

- [Current report](submission-report.md) and [claim-to-evidence index](claim-evidence.md).
- [Selected original requests and saved evidence](reviews/human-review-packet.md).
- [Resource definitions, worked example and human-review guidance](report-details.md).
- [Full course-delivery checklist](submission-checklist.md) and [presentation guide](../presentation/rehearsal.md).

The practical sample and role-specific checks are team review guidance. Course requirements concerning contributions, AI disclosure, report format and presentation are mapped to the supplied guidelines in the submission checklist. Completing this worksheet does not retroactively make the benchmark held out or establish full-dataset human review.
