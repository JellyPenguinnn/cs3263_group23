# Tiny direct-component demonstration

These are public synthetic examples and explicitly canned replies, not the shared
benchmark fixtures, recorded model outputs, or independent validation evidence.
Run from the repository root after the README installation steps:

```sh
.venv/bin/scheduling direct-offline --text-file presentation/tiny-generation.txt --response-file presentation/canned-generation.json --task-type generation --activity-id A --activity-id B
.venv/bin/scheduling direct-offline --text-file presentation/tiny-repair.txt --response-file presentation/canned-repair.json --task-type repair --activity-id A --activity-id B --original-schedule presentation/tiny-original.json
```

Explain the example in this order:

1. A and B each last one 30-minute slot, use P, and require A before B.
2. The old schedule A=0, B=2 meets the original requirements.
3. P becomes unavailable in [0,1), so A must move. The candidate A=1, B=2 moves
   one activity by one slot and keeps B unchanged. At least one activity and one
   slot must change; this candidate meets those lower bounds with no preferences.
4. The parser checks structure and ID coverage. Gold feasibility and objective
   validation are a separate pending integration with Yong Qing's component.

The live development calls are stored privately under
`runs/lihao-components-20260929-01/`, with source snapshots and checksums. The
live generation answer was A=0, B=1, whereas the canned example uses A=0, B=2;
both respect the tiny original constraints. Do not present the canned answer as
the model's answer. The common old repair schedule remains A=0, B=2 regardless
of a model's generated schedule.

For a future, separately authorized live check, load credentials as documented in
README, create an ignored output directory, and use `scheduling direct-live` with
an explicit model, output-token limit and new output filename. Each invocation
makes at most one completion call. The two-call authorization of 29 September
has been consumed; these demo commands remain entirely offline.
