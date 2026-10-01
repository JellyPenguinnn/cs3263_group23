# Fifteen-minute study presentation — working rehearsal guide

AI-assisted preparation, not a completed rehearsal or final deck. Use the
[report source](../report/study-draft.md) and [claim index](../report/claim-evidence.md).
Until the final study is available, label every numerical slide **development**.

This is a slide-by-slide storyboard, not an existing slide deck. Speaker assignments
are proposed for the team to confirm: Li Hao introduces/integrates, Yao Xiang explains
the formulation, and Yong Qing explains evaluation; all must understand every section.
The final deck should reuse the same few readable evidence views, not screenshots of code.

| Slide / elapsed time | Main message and visual | Evidence / proposed speaker |
| --- | --- | --- |
| 1 / 0–2 min | One changed commitment can force several moves. Show the concrete shared-room problem, scope and research questions | Development scenario; Li Hao |
| 2 / 2–3:30 | Start variables, legal domains and shared-resource constraints define a CSP; a proof concerns the encoded problem | C1; Yao Xiang |
| 3 / 3:30–5 | Walk A0/B1/C2 → A1/B2/C0; all three activities move and summed shift is four slots. State `(M,T,P)` priorities | C2/C8; Yao Xiang |
| 4 / 5–7 | Same public request, direct versus extraction+CP-SAT, independent gold validator. Show the two-path diagram and sampling design | C1/C3; 41 development families, not 100 independent cases; Yong Qing |
| 5 / 7–9 | Separate SAT validity and UNSAT accuracy by task; show paired accepted-answer differences with uncertainty | C4/C13; development-only, not final model results; Yong Qing |
| 6 / 9–10:30 | An omitted fixed appointment makes an infeasible request appear solvable. Show one saved before/after failure and gold rejection | C5; no corrected primary answer; Yao Xiang |
| 7 / 10:30–12 | More valid answers cost more extraction time/tokens; repair-quality comparisons are conditional on validity | C6/C14; 99 solver executions, not 100; Yong Qing |
| 8 / 12–14 | Global minimum disruption can burden one person; requirements and objective priorities need user control. Explain privacy and prompt-boundary limits | C7–C9; Li Hao |
| 9 / 14–15 | State what this evidence supports, where either method may be preferable, and the scope of the final study | Bounded conclusions; Li Hao |

At most one short saved-record demonstration belongs inside slides 6–7; it must
fit their time budget. Current material uses `qwen3.6:35b` development data.
The selected next development target `qwen3.8:27b` is not a result, completed
qualification or final-course model decision. Replace or clearly separate the
results section only when final-study claims are verified.

Use [the existing offline demo](README.md) or replay the saved expanded run. For
the latter, obtain its reviewed raw-record archive first. No model call is needed:

```sh
.venv/bin/scheduling explain --run-dir runs/expanded-development-100-20260930-01 \
  --case-id dev-v2-3264-slack-0-fixed_start-unsat-0-repair \
  --approach solver_augmented --format json
```

The example preserves B's missing updated appointment and gold rejection. Do not
edit the extraction to make the demonstration successful. Keep a screen recording
of the same saved evidence as a later fallback; none has been recorded in this
session. Present canned fallback answers explicitly as integration tests.

For the five-minute Q&A, every member should answer: why CP-SAT; why (M,T,P);
how independent validation differs from reference solving; why UNKNOWN is not
UNSAT; why extraction can invalidate source-level correctness; how families and
exclusions work; whether the final model meets course requirements; and when
direct reasoning may be preferable. Actual speaker assignments and timed rehearsal
results must be recorded by the team.

## Q&A preparation

These are answer points for members to explain in their own words, not a record
that anybody has rehearsed them.

| Question | Answer boundary / evidence |
| --- | --- |
| Why CP-SAT? Is the solver itself the contribution? | Fixed integer time domains and coupled constraints fit CP-SAT. The contribution is the bounded comparison and failure analysis; CP-SAT and minimum-perturbation repair are established methods. |
| Why solve three objectives sequentially? | A weighted sum can trade a higher-priority objective against a lower one. Exact sequential proof fixes each optimum before proceeding; a timeout limits the proof claim. C2/C8. |
| Could solver and gold share the same bug? | Yes. The independent arithmetic validator and exhaustive tiny checks reduce this risk; they do not prove every compiler/input is correct. C2/C12. |
| Does 97/100 mean 97% deployment reliability? | No. This is a balanced synthetic development packet with related families and canonical wording; realistic language, model selection and final study remain separate. C3/C4. |
| Why are the uncertainty intervals grouped? | Several cases descend from a common source. Resampling source families preserves that dependence and A/B pairing; it does not eliminate generator bias. C13. |
| Why not count a semantically equivalent extraction as a structural match? | They measure different properties. Keep the original structural score and report bounded equivalence certificates separately. C5. |
| Is B's repair quality better on every request? | Quality is conditional on a valid output and a proven reference. B had 25 valid repairs and A eight; unequal survivor groups are not an unconditional quality comparison. C14. |
| Is a changed serving fingerprint proof of new weights? | No. It shows reported backend variation. The retained execution policy and model eligibility decision are separate from claims about weight identity. C10. |
| When might direct reasoning be preferable? | It was faster and used fewer tokens here; simpler or unsupported/ambiguous tasks may change the trade-off. Do not claim an untested difficulty threshold or guaranteed future trend. C6. |
| How does the project satisfy responsible AI? | Explain the concrete burden/objective examples, privacy boundaries and limits of formalization. Formal validation does not establish fairness or resolve unstated negotiability. C7–C9. |

## Human rehearsal record — not yet completed

Record the actual date, speakers, slide/deck version, elapsed time, questions each
member answered, weak explanations and assigned corrections. Verify that the saved
example runs offline, charts are legible and every numeric slide names its model,
run stage and denominator. A teammate should independently question the formal
and empirical claims. Leave entries pending until these actions occur; see the
[submission checklist](../report/submission-checklist.md) for course delivery.
