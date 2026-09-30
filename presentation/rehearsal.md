# Fifteen-minute study presentation — working rehearsal guide

AI-assisted preparation, not a completed rehearsal or final deck. Use the
[report source](../report/study-draft.md) and [claim index](../report/claim-evidence.md).
Until the final study is available, label every numerical slide **development**.

| Elapsed time | Explain / show | Evidence and boundary |
| --- | --- | --- |
| 0–2 min | Shared-room disruption; questions and single-day scope | No real calendars or autonomous edits |
| 2–5 min | Start domains, shared-resource constraint, lexicographic repair; A0/B1/C2 → A1/B2/C0 | C2; affected-neighborhood freezing is unsound |
| 5–7 min | Two-path diagram; gold boundary; grouped dataset and canonical primary comparison | C1/C3; 41 development families, not 100 independent problems |
| 7–12 min | Task/label table, one successful repair, one omitted-fixed-start failure, resources | C4–C6; replace/add final results only after verified frozen analysis |
| 12–14 min | Unequal burden, objective trade-off, missing requirements/privacy, instruction-like input | C7–C9; prompt construction is not adversarial robustness |
| 14–15 min | What is supported, where each approach fails, current evidence limits | No unsupported model superiority or grade claim |

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
