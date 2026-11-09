# Selected human-review case packet

**Status (9 November 2026):** the team reports that all 24 cases below were reviewed against their gold specifications with no request/gold mismatches found. The packet text that follows was prepared before that review.

Use the [fill-in checklist](../process/human-review-checklist.md). Read each original request and write your interpretation before opening its gold/recorded-output section. All times in the specifications below are slot indices; each slot is 30 minutes from the stated horizon start. An availability interval constrains the entire activity; a preferred-start interval constrains its start only.

This is a retrospective review aid, not a new experiment or evidence of completed human review. C01–C20 cover all ten mechanisms and all five sizes: one SAT and one UNSAT case per mechanism, using size 8/12/16/24/32 in sorted-mechanism order, repeated twice. Within each mechanism/size/label cell, select the lexicographically first case ID; selection does not use model outcomes. Cases within each pair are ordered by ID. They are a coverage pair, not necessarily a matched construction pair. E1–E4 are deliberately selected explanatory examples from the report. This sample does not establish full-dataset semantic validity or estimate an error rate.

Source: [immutable archive manifest](../../results/diverse-evidence-manifest.json), SHA-256 `5d92d69ba67d97369c16ccd14ad98a4b9ec4c1995832d4920579b7485ce9abae`. Both archives and every used member were checksum-verified. Requests are copied verbatim from saved public views; gold fields and outputs below are projections of saved records. No model calls, new solving, or changes to existing evidence.

## C01

**Appointment collision · 8 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,16) and has capacity one.
Activity A2 lasts 3 slots; participants: P2; resources: R1; availability: [3,6).
Activity A5 lasts 3 slots; participants: P1; resources: none; availability: [0,8).
Activity A3 lasts 3 slots; participants: P2; resources: none; availability: [9,13).
Activity A1 lasts 3 slots; participants: P1; resources: none; availability: [0,8).
Activity A8 lasts 2 slots; participants: P1; resources: R1; availability: [9,13).
Activity A7 lasts 2 slots; participants: P1; resources: R1; availability: [5,9).
Activity A6 lasts 3 slots; participants: P2; resources: none; availability: [5,11).
Activity A4 lasts 2 slots; participants: P1; resources: none; availability: [0,3), [9,13).
Starting A3 outside [7,9) incurs penalty 1; starting inside incurs zero.
A5 must start exactly at slot 0.
Starting A7 outside [6,12) incurs penalty 1; starting inside incurs zero.
A6 must finish before or when A8 starts.
A2 must finish before or when A6 starts.
A5 must finish before or when A6 starts.
A7 must finish at or before slot 8.
A5 must finish before or when A2 starts.
A8 must start exactly at slot 11.
A6 must finish before or when A4 starts.
Starting A1 outside [0,2) incurs penalty 2; starting inside incurs zero.
A6 must finish before or when A3 starts.
Starting A6 outside [8,12) incurs penalty 1; starting inside incurs zero.
A1 must start exactly at slot 3.
A5 must finish before or when A7 starts.
A5 must finish before or when A8 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-0a6ac877c0439beb9ec7bb84`. Gold label: **SAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 16) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A2 | 3 | P2 | R1 | [3, 6) |
| A5 | 3 | P1 | None | [0, 8) |
| A3 | 3 | P2 | None | [9, 13) |
| A1 | 3 | P1 | None | [0, 8) |
| A8 | 2 | P1 | R1 | [9, 13) |
| A7 | 2 | P1 | R1 | [5, 9) |
| A6 | 3 | P2 | None | [5, 11) |
| A4 | 2 | P1 | None | [0, 3), [9, 13) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A3","end":9,"id":"PREF5","start":7,"type":"preferred_start","weight":1}`
- `{"activity_id":"A5","id":"C_fixed0","slot":0,"type":"fixed_start"}`
- `{"activity_id":"A7","end":12,"id":"PREF7","start":6,"type":"preferred_start","weight":1}`
- `{"after":"A8","before":"A6","id":"C_bg6","type":"precedence"}`
- `{"after":"A6","before":"A2","id":"C_bg3","type":"precedence"}`
- `{"after":"A6","before":"A5","id":"C_extra3","type":"precedence"}`
- `{"activity_id":"A7","id":"C_profile_deadline","slot":8,"type":"deadline"}`
- `{"after":"A2","before":"A5","id":"C_bg2","type":"precedence"}`
- `{"activity_id":"A8","id":"C_profile_fixed","slot":11,"type":"fixed_start"}`
- `{"after":"A4","before":"A6","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A1","end":2,"id":"PREF1","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A3","before":"A6","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A6","end":12,"id":"PREF3","start":8,"type":"preferred_start","weight":1}`
- `{"activity_id":"A1","id":"C_fixed1","slot":3,"type":"fixed_start"}`
- `{"after":"A7","before":"A5","id":"C_bg7","type":"precedence"}`
- `{"after":"A8","before":"A5","id":"C_extra6","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":4,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 3
  },
  {
    "activity_id": "A2",
    "start_slot": 3
  },
  {
    "activity_id": "A3",
    "start_slot": 9
  },
  {
    "activity_id": "A4",
    "start_slot": 9
  },
  {
    "activity_id": "A5",
    "start_slot": 0
  },
  {
    "activity_id": "A6",
    "start_slot": 6
  },
  {
    "activity_id": "A7",
    "start_slot": 6
  },
  {
    "activity_id": "A8",
    "start_slot": 11
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | SAT | accepted | `[4]` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[4]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[4]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[4]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 3
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 9
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 6
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 4,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    4
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/2d5d3572b648fa3cb6b00ef65235e02efcef35a85cb664534c3f7c9489df541d.json`. SHA-256: `28fe3f7fc7b5b21b796210fec91f6b3764f7c586801d04b29d5bef6741d65ccd`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/48e3a07baf1b8ac2d947c0f02b2fe3753db483d81e7f3cec00b8a0537ba32f53.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 3
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 9
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 6
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 4,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    4
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/bca1f38c07c8359a06b019c7cad487c9f513c9cdacd9b0796e4fc4b105e18709.json`. SHA-256: `5057ef33841de526b23555def6d67a02c990019ec382497d8365f9cf81fe049a`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/48e3a07baf1b8ac2d947c0f02b2fe3753db483d81e7f3cec00b8a0537ba32f53.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 3
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 9
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 6
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 4,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    4
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/848df5edc1d72bb78fc64eecf8f149a432225d51a2dedf8e665bd9146cb4b570.json`. SHA-256: `67af56d959700e1c0df1733d44bbc9619df9667ffcaac2dbcc35a714875b6e53`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/48e3a07baf1b8ac2d947c0f02b2fe3753db483d81e7f3cec00b8a0537ba32f53.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 3
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 9
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 6
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 4,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    4
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/a494b2c2052d80a314cb2d4a664cf641d1fca7bddcf70829359dcaa447c758a3.json`. SHA-256: `c72700190797a88aeaf234e5ceb067b8675dd59ea5fce00ffa78d6eca756348b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/48e3a07baf1b8ac2d947c0f02b2fe3753db483d81e7f3cec00b8a0537ba32f53.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C02

**Appointment collision · 8 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,16) and has capacity one.
Activity A4 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A1 lasts 3 slots; participants: P1; resources: R1; availability: [6,11).
Activity A8 lasts 2 slots; participants: P2; resources: R1; availability: [2,5).
Activity A6 lasts 2 slots; participants: P1; resources: R1; availability: [2,6).
Activity A3 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A7 lasts 2 slots; participants: P2; resources: none; availability: [4,10).
Activity A2 lasts 2 slots; participants: P2; resources: none; availability: [4,8).
Activity A5 lasts 2 slots; participants: P1; resources: R1; availability: [9,13).
A3 must start exactly at slot 0.
Starting A8 outside [4,8) incurs penalty 1; starting inside incurs zero.
A4 must finish before or when A7 starts.
A4 must finish before or when A2 starts.
Starting A7 outside [6,10) incurs penalty 2; starting inside incurs zero.
A3 must finish before or when A2 starts.
Starting A3 outside [9,15) incurs penalty 1; starting inside incurs zero.
A7 must start exactly at slot 6.
A4 must finish before or when A1 starts.
Starting A6 outside [10,12) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A7 starts.
A4 must start exactly at slot 1.
A3 must finish before or when A8 starts.
A1 must finish before or when A5 starts.
A8 must finish before or when A6 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-193e6bddd3080ee9d61d55d3`. Gold label: **UNSAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 16) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A4 | 2 | P1 | None | [0, 6) |
| A1 | 3 | P1 | R1 | [6, 11) |
| A8 | 2 | P2 | R1 | [2, 5) |
| A6 | 2 | P1 | R1 | [2, 6) |
| A3 | 2 | P1 | None | [0, 6) |
| A7 | 2 | P2 | None | [4, 10) |
| A2 | 2 | P2 | None | [4, 8) |
| A5 | 2 | P1 | R1 | [9, 13) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A3","id":"C_fixed0","slot":0,"type":"fixed_start"}`
- `{"activity_id":"A8","end":8,"id":"PREF2","start":4,"type":"preferred_start","weight":1}`
- `{"after":"A7","before":"A4","id":"C_extra6","type":"precedence"}`
- `{"after":"A2","before":"A4","id":"C_bg3","type":"precedence"}`
- `{"activity_id":"A7","end":10,"id":"PREF6","start":6,"type":"preferred_start","weight":2}`
- `{"after":"A2","before":"A3","id":"C_extra3","type":"precedence"}`
- `{"activity_id":"A3","end":15,"id":"PREF0","start":9,"type":"preferred_start","weight":1}`
- `{"activity_id":"A7","id":"C_profile_fixed","slot":6,"type":"fixed_start"}`
- `{"after":"A1","before":"A4","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A6","end":12,"id":"PREF4","start":10,"type":"preferred_start","weight":3}`
- `{"after":"A7","before":"A2","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A4","id":"C_fixed1","slot":1,"type":"fixed_start"}`
- `{"after":"A8","before":"A3","id":"C_bg2","type":"precedence"}`
- `{"after":"A5","before":"A1","id":"C_bg7","type":"precedence"}`
- `{"after":"A6","before":"A8","id":"C_bg4","type":"precedence"}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/1154085e2d83c4e84c1bf367191270bc4625f725b90c36b36b3b8596bdf98a87.json`. SHA-256: `3c836cdbde95cf42a65ef4f25c3626c3aaa774a095a1b6a6a556fb828ca233bb`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ec1b86fcd167ae2c7b90eabf81db6a17db5ca9f84e4855fa42318977c77498a.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/b9396c8cc812c753fc17377a2889c637f8ff7bf525913de93b6327187786c4ea.json`. SHA-256: `d95d9c05f426ebcbc243cfe7e03ee6826957819fbf305e2d653da870fe3e6d5e`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ec1b86fcd167ae2c7b90eabf81db6a17db5ca9f84e4855fa42318977c77498a.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/546687861da4d05b1018e08832f31be0cc7ea808fe0ede084a8b1a48afa9aef4.json`. SHA-256: `d73b172962704a5108441fd9fef10d62141800df68e54119c8d9d62fb741144d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ec1b86fcd167ae2c7b90eabf81db6a17db5ca9f84e4855fa42318977c77498a.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/ebc3ea58c8f67aacf559038f54c63f996f2add6905f3da9450975dbf084845d7.json`. SHA-256: `a98420a771e66705e7d91b6ecf53c9a2548e8397fca85acfd425abcebb718157`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ec1b86fcd167ae2c7b90eabf81db6a17db5ca9f84e4855fa42318977c77498a.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C03

**Fragmented packing · 12 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 20 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,20) and has capacity one.
Participant P2 is available in [0,20) and has capacity one.
Participant P3 is available in [0,20) and has capacity one.
Resource R1 is available in [0,20) and has capacity one.
Activity A8 lasts 2 slots; participants: P3; resources: none; availability: [9,14).
Activity A11 lasts 3 slots; participants: P1; resources: none; availability: [3,8).
Activity A12 lasts 2 slots; participants: P3; resources: R1; availability: [11,18).
Activity A10 lasts 2 slots; participants: P2; resources: R1; availability: [9,15).
Activity A6 lasts 2 slots; participants: P3; resources: none; availability: [0,3), [9,11).
Activity A3 lasts 3 slots; participants: P3; resources: none; availability: [4,12).
Activity A4 lasts 2 slots; participants: P2; resources: none; availability: [3,9).
Activity A9 lasts 3 slots; participants: P1; resources: R1; availability: [0,6), [7,12).
Activity A5 lasts 2 slots; participants: P2; resources: none; availability: [9,14).
Activity A7 lasts 2 slots; participants: P1; resources: none; availability: [9,16).
Activity A1 lasts 3 slots; participants: P1; resources: R1; availability: [0,6), [7,12).
Activity A2 lasts 3 slots; participants: P2; resources: R1; availability: [0,6), [7,12).
A11 must finish before or when A4 starts.
A6 must finish before or when A7 starts.
A2 must finish before or when A12 starts.
A2 must finish before or when A3 starts.
Starting A9 outside [7,9) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A10 starts.
Starting A10 outside [0,2) incurs penalty 3; starting inside incurs zero.
A3 must finish before or when A5 starts.
Starting A5 outside [6,12) incurs penalty 3; starting inside incurs zero.
Starting A4 outside [4,6) incurs penalty 3; starting inside incurs zero.
A9 must finish before or when A5 starts.
A2 must finish before or when A8 starts.
A9 must finish before or when A3 starts.
Starting A1 outside [4,10) incurs penalty 1; starting inside incurs zero.
A9 must finish before or when A11 starts.
Starting A6 outside [12,18) incurs penalty 1; starting inside incurs zero.
A3 must finish before or when A6 starts.
A4 must finish before or when A8 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-026c2ff23afbd457193e36cf`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 20 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 20) |
| P2 | [0, 20) |
| P3 | [0, 20) |
| R1 | [0, 20) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A8 | 2 | P3 | None | [9, 14) |
| A11 | 3 | P1 | None | [3, 8) |
| A12 | 2 | P3 | R1 | [11, 18) |
| A10 | 2 | P2 | R1 | [9, 15) |
| A6 | 2 | P3 | None | [0, 3), [9, 11) |
| A3 | 3 | P3 | None | [4, 12) |
| A4 | 2 | P2 | None | [3, 9) |
| A9 | 3 | P1 | R1 | [0, 6), [7, 12) |
| A5 | 2 | P2 | None | [9, 14) |
| A7 | 2 | P1 | None | [9, 16) |
| A1 | 3 | P1 | R1 | [0, 6), [7, 12) |
| A2 | 3 | P2 | R1 | [0, 6), [7, 12) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A4","before":"A11","id":"C_bg8","type":"precedence"}`
- `{"after":"A7","before":"A6","id":"C_bg5","type":"precedence"}`
- `{"after":"A12","before":"A2","id":"C_bg11","type":"precedence"}`
- `{"after":"A3","before":"A2","id":"C_bg3","type":"precedence"}`
- `{"activity_id":"A9","end":9,"id":"PREF0","start":7,"type":"preferred_start","weight":3}`
- `{"after":"A10","before":"A2","id":"C_bg10","type":"precedence"}`
- `{"activity_id":"A10","end":2,"id":"PREF10","start":0,"type":"preferred_start","weight":3}`
- `{"after":"A5","before":"A3","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A5","end":12,"id":"PREF6","start":6,"type":"preferred_start","weight":3}`
- `{"activity_id":"A4","end":6,"id":"PREF8","start":4,"type":"preferred_start","weight":3}`
- `{"after":"A5","before":"A9","id":"C_extra6","type":"precedence"}`
- `{"after":"A8","before":"A2","id":"C_extra9","type":"precedence"}`
- `{"after":"A3","before":"A9","id":"C_extra3","type":"precedence"}`
- `{"activity_id":"A1","end":10,"id":"PREF2","start":4,"type":"preferred_start","weight":1}`
- `{"after":"A11","before":"A9","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A6","end":18,"id":"PREF4","start":12,"type":"preferred_start","weight":1}`
- `{"after":"A6","before":"A3","id":"C_bg4","type":"precedence"}`
- `{"after":"A8","before":"A4","id":"C_bg9","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":10,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 7
  },
  {
    "activity_id": "A10",
    "start_slot": 11
  },
  {
    "activity_id": "A11",
    "start_slot": 3
  },
  {
    "activity_id": "A12",
    "start_slot": 13
  },
  {
    "activity_id": "A2",
    "start_slot": 3
  },
  {
    "activity_id": "A3",
    "start_slot": 6
  },
  {
    "activity_id": "A4",
    "start_slot": 7
  },
  {
    "activity_id": "A5",
    "start_slot": 9
  },
  {
    "activity_id": "A6",
    "start_slot": 9
  },
  {
    "activity_id": "A7",
    "start_slot": 11
  },
  {
    "activity_id": "A8",
    "start_slot": 11
  },
  {
    "activity_id": "A9",
    "start_slot": 0
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[10]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/7a42fa245eed2481ee215993a61aba02d7356adc871d549889c9d1a72e395898.json`. SHA-256: `ee2e91170b3e6817b8dc7fdb0d6b2328d9803bbb00528bf441a3e5a14cdc11a1`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/8e51fa1d345cafabaf4d1cff332cbeed4625a9fe410f31e8e6cc0311462f92a9.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A10",
      "start_slot": 11
    },
    {
      "activity_id": "A11",
      "start_slot": 3
    },
    {
      "activity_id": "A12",
      "start_slot": 13
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 6
    },
    {
      "activity_id": "A4",
      "start_slot": 7
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 11
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/2ccab7f1f43c375907bd2275549e71d23e1a6608bbc7badd32248badf0227bc2.json`. SHA-256: `8bc9447f3f9392e437870fd1188e13ab81d934d7fd9e147834f2bf21471d87ed`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/8e51fa1d345cafabaf4d1cff332cbeed4625a9fe410f31e8e6cc0311462f92a9.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A10",
      "start_slot": 11
    },
    {
      "activity_id": "A11",
      "start_slot": 3
    },
    {
      "activity_id": "A12",
      "start_slot": 13
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 6
    },
    {
      "activity_id": "A4",
      "start_slot": 6
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 11
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/74407bb37494b6ade42780dcdbd65c3b6b4a2e29e82a855a4982d528d8188bef.json`. SHA-256: `c9a4bb348b9c4646e772127b556916e73f9dda10760047ce38487a1db42b65e8`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/8e51fa1d345cafabaf4d1cff332cbeed4625a9fe410f31e8e6cc0311462f92a9.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A10",
      "start_slot": 11
    },
    {
      "activity_id": "A11",
      "start_slot": 3
    },
    {
      "activity_id": "A12",
      "start_slot": 13
    },
    {
      "activity_id": "A2",
      "start_slot": 3
    },
    {
      "activity_id": "A3",
      "start_slot": 6
    },
    {
      "activity_id": "A4",
      "start_slot": 7
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 11
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/bb06171d8e69a2bd93294289199f2262d448b30d0c0bc51dd2669e2ab5f23877.json`. SHA-256: `a8cf322cdb9e1a139821c3498a687371e6766a564ad59f425f99a6eebd7152c3`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/8e51fa1d345cafabaf4d1cff332cbeed4625a9fe410f31e8e6cc0311462f92a9.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C04

**Fragmented packing · 12 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 20 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,20) and has capacity one.
Participant P2 is available in [0,20) and has capacity one.
Participant P3 is available in [0,20) and has capacity one.
Resource R1 is available in [0,20) and has capacity one.
Activity A1 lasts 3 slots; participants: P3; resources: none; availability: [10,14).
Activity A7 lasts 3 slots; participants: P3; resources: R1; availability: [14,17).
Activity A11 lasts 3 slots; participants: P1; resources: R1; availability: [0,5), [7,12).
Activity A3 lasts 3 slots; participants: P3; resources: none; availability: [3,10).
Activity A10 lasts 2 slots; participants: P3; resources: none; availability: [9,12).
Activity A8 lasts 3 slots; participants: P2; resources: R1; availability: [0,5), [7,12).
Activity A5 lasts 2 slots; participants: P3; resources: none; availability: [0,7).
Activity A4 lasts 3 slots; participants: P2; resources: none; availability: [9,15).
Activity A2 lasts 2 slots; participants: P2; resources: none; availability: [6,11).
Activity A12 lasts 3 slots; participants: P1; resources: R1; availability: [0,5), [7,12).
Activity A6 lasts 2 slots; participants: P2; resources: none; availability: [6,12).
Activity A9 lasts 2 slots; participants: P1; resources: R1; availability: [0,3), [7,13).
A8 must finish before or when A3 starts.
A11 must finish before or when A5 starts.
A8 must finish before or when A6 starts.
A1 must finish before or when A7 starts.
A12 must finish before or when A9 starts.
A8 must finish before or when A4 starts.
A11 must finish before or when A2 starts.
A5 must finish before or when A6 starts.
Starting A1 outside [6,10) incurs penalty 1; starting inside incurs zero.
Starting A6 outside [3,9) incurs penalty 1; starting inside incurs zero.
A2 must finish before or when A10 starts.
Starting A11 outside [8,12) incurs penalty 2; starting inside incurs zero.
Starting A9 outside [1,3) incurs penalty 2; starting inside incurs zero.
Starting A5 outside [5,7) incurs penalty 1; starting inside incurs zero.
A8 must finish before or when A1 starts.
A8 must finish before or when A2 starts.
Starting A12 outside [9,13) incurs penalty 1; starting inside incurs zero.
A3 must finish before or when A4 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-0aaa895de71ab761f57233aa`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 20 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 20) |
| P2 | [0, 20) |
| P3 | [0, 20) |
| R1 | [0, 20) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A1 | 3 | P3 | None | [10, 14) |
| A7 | 3 | P3 | R1 | [14, 17) |
| A11 | 3 | P1 | R1 | [0, 5), [7, 12) |
| A3 | 3 | P3 | None | [3, 10) |
| A10 | 2 | P3 | None | [9, 12) |
| A8 | 3 | P2 | R1 | [0, 5), [7, 12) |
| A5 | 2 | P3 | None | [0, 7) |
| A4 | 3 | P2 | None | [9, 15) |
| A2 | 2 | P2 | None | [6, 11) |
| A12 | 3 | P1 | R1 | [0, 5), [7, 12) |
| A6 | 2 | P2 | None | [6, 12) |
| A9 | 2 | P1 | R1 | [0, 3), [7, 13) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A3","before":"A8","id":"C_bg5","type":"precedence"}`
- `{"after":"A5","before":"A11","id":"C_bg4","type":"precedence"}`
- `{"after":"A6","before":"A8","id":"C_bg6","type":"precedence"}`
- `{"after":"A7","before":"A1","id":"C_bg11","type":"precedence"}`
- `{"after":"A9","before":"A12","id":"C_bg8","type":"precedence"}`
- `{"after":"A4","before":"A8","id":"C_extra9","type":"precedence"}`
- `{"after":"A2","before":"A11","id":"C_extra3","type":"precedence"}`
- `{"after":"A6","before":"A5","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A1","end":10,"id":"PREF10","start":6,"type":"preferred_start","weight":1}`
- `{"activity_id":"A6","end":9,"id":"PREF6","start":3,"type":"preferred_start","weight":1}`
- `{"after":"A10","before":"A2","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A11","end":12,"id":"PREF0","start":8,"type":"preferred_start","weight":2}`
- `{"activity_id":"A9","end":3,"id":"PREF8","start":1,"type":"preferred_start","weight":2}`
- `{"activity_id":"A5","end":7,"id":"PREF4","start":5,"type":"preferred_start","weight":1}`
- `{"after":"A1","before":"A8","id":"C_bg10","type":"precedence"}`
- `{"after":"A2","before":"A8","id":"C_bg3","type":"precedence"}`
- `{"activity_id":"A12","end":13,"id":"PREF2","start":9,"type":"preferred_start","weight":1}`
- `{"after":"A4","before":"A3","id":"C_bg9","type":"precedence"}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | INVALID_OUTPUT | invalid_output | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer failed the required output/schema contract."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/2c7846197a46a8b5dc21a79f1814b2031550846769be007fb8be42a5621b3ae7.json`. SHA-256: `7d137b0565bfd5bad7a1af43f5dcb4fc48f79da058c19c75025a75c188b8cacd`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/5c3466fccd894b318582a33d2ac95fc811d0f02821ba3db87499a4818e8d7ef7.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/663c548e522d5763d196cff5b47527e18e627916e29e4a2ac80077e69dd33393.json`. SHA-256: `434c2d68d49d739dc2bf96121480d3b85a88c955b738b796000c42db61f576df`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/5c3466fccd894b318582a33d2ac95fc811d0f02821ba3db87499a4818e8d7ef7.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/f05b5a7bee0cec062f9e7fd46c7c89a1283b5590d3766b3a8ebe732339cf6437.json`. SHA-256: `c22877cf02567b85a4e0cd2f69084defd050457c2aff9ae2f4e5c2315d0d6b0f`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/5c3466fccd894b318582a33d2ac95fc811d0f02821ba3db87499a4818e8d7ef7.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4ae7d98ff0093173730ec3fbcbdd79757a3856740b7a8bbc53010f64f760992c.json`. SHA-256: `5e00f6cc6a5eefa37738605e50f517db7792d3a670a4ddd32a6fc104f59ac313`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/5c3466fccd894b318582a33d2ac95fc811d0f02821ba3db87499a4818e8d7ef7.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C05

**Mixed order resource · 16 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 24 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,24) and has capacity one.
Participant P2 is available in [0,24) and has capacity one.
Participant P3 is available in [0,24) and has capacity one.
Participant P4 is available in [0,24) and has capacity one.
Resource R1 is available in [0,24) and has capacity one.
Resource R2 is available in [0,24) and has capacity one.
Activity A3 lasts 2 slots; participants: P1, P4; resources: R1; availability: [5,10).
Activity A12 lasts 3 slots; participants: P3; resources: none; availability: [3,12).
Activity A8 lasts 2 slots; participants: P1, P4; resources: none; availability: [4,7).
Activity A13 lasts 2 slots; participants: P2; resources: R2; availability: [8,11).
Activity A14 lasts 2 slots; participants: P4; resources: none; availability: [3,12).
Activity A4 lasts 2 slots; participants: P2; resources: R1; availability: [0,6).
Activity A15 lasts 2 slots; participants: P1; resources: none; availability: [9,14).
Activity A9 lasts 2 slots; participants: P1; resources: R1; availability: [5,8).
Activity A7 lasts 2 slots; participants: P3; resources: R1; availability: [4,8).
Activity A5 lasts 2 slots; participants: P1; resources: R1; availability: [0,6).
Activity A10 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A2 lasts 2 slots; participants: P2; resources: none; availability: [0,6).
Activity A6 lasts 2 slots; participants: P3; resources: none; availability: [0,3), [7,15).
Activity A1 lasts 2 slots; participants: P4; resources: R1; availability: [7,16).
Activity A16 lasts 2 slots; participants: P2; resources: R2; availability: [10,14).
Activity A11 lasts 3 slots; participants: P2; resources: R2; availability: [3,13).
A4 must finish before or when A6 starts.
A7 must finish before or when A3 starts.
A2 must finish before or when A11 starts.
A10 must finish before or when A15 starts.
A7 must finish before or when A12 starts.
Starting A15 outside [7,9) incurs penalty 3; starting inside incurs zero.
A7 must finish before or when A14 starts.
Starting A8 outside [7,11) incurs penalty 3; starting inside incurs zero.
A10 must finish before or when A6 starts.
A2 must finish before or when A16 starts.
A4 must finish before or when A13 starts.
A2 must finish before or when A9 starts.
A4 must finish before or when A2 starts.
A4 must finish before or when A8 starts.
Starting A6 outside [3,7) incurs penalty 3; starting inside incurs zero.
A15 must start exactly at slot 10.
Starting A11 outside [15,17) incurs penalty 1; starting inside incurs zero.
Starting A10 outside [7,11) incurs penalty 2; starting inside incurs zero.
Starting A3 outside [16,18) incurs penalty 1; starting inside incurs zero.
A4 must finish before or when A7 starts.
Starting A14 outside [19,24) incurs penalty 2; starting inside incurs zero.
Starting A5 outside [11,13) incurs penalty 3; starting inside incurs zero.
A5 must finish before or when A8 starts.
A10 must finish at or before slot 6.
A5 must finish before or when A10 starts.
A14 must finish before or when A1 starts.
A2 must finish at or before slot 6.
A3 must finish before or when A16 starts.
A8 must finish before or when A12 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-22c2f6f726dc12980d0c395d`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 24 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 24) |
| P2 | [0, 24) |
| P3 | [0, 24) |
| P4 | [0, 24) |
| R1 | [0, 24) |
| R2 | [0, 24) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A3 | 2 | P1, P4 | R1 | [5, 10) |
| A12 | 3 | P3 | None | [3, 12) |
| A8 | 2 | P1, P4 | None | [4, 7) |
| A13 | 2 | P2 | R2 | [8, 11) |
| A14 | 2 | P4 | None | [3, 12) |
| A4 | 2 | P2 | R1 | [0, 6) |
| A15 | 2 | P1 | None | [9, 14) |
| A9 | 2 | P1 | R1 | [5, 8) |
| A7 | 2 | P3 | R1 | [4, 8) |
| A5 | 2 | P1 | R1 | [0, 6) |
| A10 | 2 | P1 | None | [0, 6) |
| A2 | 2 | P2 | None | [0, 6) |
| A6 | 2 | P3 | None | [0, 3), [7, 15) |
| A1 | 2 | P4 | R1 | [7, 16) |
| A16 | 2 | P2 | R2 | [10, 14) |
| A11 | 3 | P2 | R2 | [3, 13) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A6","before":"A4","id":"C_bg12","type":"precedence"}`
- `{"after":"A3","before":"A7","id":"C_bg10","type":"precedence"}`
- `{"after":"A11","before":"A2","id":"C_bg4","type":"precedence"}`
- `{"after":"A15","before":"A10","id":"C_bg14","type":"precedence"}`
- `{"after":"A12","before":"A7","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A15","end":9,"id":"PREF14","start":7,"type":"preferred_start","weight":3}`
- `{"after":"A14","before":"A7","id":"C_bg8","type":"precedence"}`
- `{"activity_id":"A8","end":11,"id":"PREF6","start":7,"type":"preferred_start","weight":3}`
- `{"after":"A6","before":"A10","id":"C_extra12","type":"precedence"}`
- `{"after":"A16","before":"A2","id":"C_extra15","type":"precedence"}`
- `{"after":"A13","before":"A4","id":"C_bg11","type":"precedence"}`
- `{"after":"A9","before":"A2","id":"C_bg7","type":"precedence"}`
- `{"after":"A2","before":"A4","id":"C1","type":"precedence"}`
- `{"after":"A8","before":"A4","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A6","end":7,"id":"PREF12","start":3,"type":"preferred_start","weight":3}`
- `{"activity_id":"A15","id":"C_profile_fixed","slot":10,"type":"fixed_start"}`
- `{"activity_id":"A11","end":17,"id":"PREF4","start":15,"type":"preferred_start","weight":1}`
- `{"activity_id":"A10","end":11,"id":"PREF2","start":7,"type":"preferred_start","weight":2}`
- `{"activity_id":"A3","end":18,"id":"PREF10","start":16,"type":"preferred_start","weight":1}`
- `{"after":"A7","before":"A4","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A14","end":24,"id":"PREF8","start":19,"type":"preferred_start","weight":2}`
- `{"activity_id":"A5","end":13,"id":"PREF0","start":11,"type":"preferred_start","weight":3}`
- `{"after":"A8","before":"A5","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A10","id":"C2","slot":6,"type":"deadline"}`
- `{"after":"A10","before":"A5","id":"C0","type":"precedence"}`
- `{"after":"A1","before":"A14","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A2","id":"C3","slot":6,"type":"deadline"}`
- `{"after":"A16","before":"A3","id":"C_bg15","type":"precedence"}`
- `{"after":"A12","before":"A8","id":"C_bg9","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":18,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 10
  },
  {
    "activity_id": "A10",
    "start_slot": 2
  },
  {
    "activity_id": "A11",
    "start_slot": 6
  },
  {
    "activity_id": "A12",
    "start_slot": 6
  },
  {
    "activity_id": "A13",
    "start_slot": 9
  },
  {
    "activity_id": "A14",
    "start_slot": 6
  },
  {
    "activity_id": "A15",
    "start_slot": 10
  },
  {
    "activity_id": "A16",
    "start_slot": 11
  },
  {
    "activity_id": "A2",
    "start_slot": 4
  },
  {
    "activity_id": "A3",
    "start_slot": 8
  },
  {
    "activity_id": "A4",
    "start_slot": 2
  },
  {
    "activity_id": "A5",
    "start_slot": 0
  },
  {
    "activity_id": "A6",
    "start_slot": 9
  },
  {
    "activity_id": "A7",
    "start_slot": 4
  },
  {
    "activity_id": "A8",
    "start_slot": 4
  },
  {
    "activity_id": "A9",
    "start_slot": 6
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[18]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[18]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[18]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/d7af6ad6307368ab50c5deebe01a5e7d02e3271a50a379a38f8b435d0b3854e9.json`. SHA-256: `4d3a36ec58b6bdaf4915c1d272013f349361556c4629812f091649aba1a99e03`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2cf80047f97d9a62198256ed6182dcdc270d6bbdfbfae4a07b3b620c501d52d6.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 9
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 10
    },
    {
      "activity_id": "A16",
      "start_slot": 11
    },
    {
      "activity_id": "A2",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 18,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    18
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/0209287841aab5c23db0c6fa8c545a9e99a3cf623f73b759bd16b57f6c64c8b5.json`. SHA-256: `56d6dcbf4657494efaabb6008fedd116a57a7cadd4a34d7f41110af26efb5a9c`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2cf80047f97d9a62198256ed6182dcdc270d6bbdfbfae4a07b3b620c501d52d6.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 9
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 10
    },
    {
      "activity_id": "A16",
      "start_slot": 11
    },
    {
      "activity_id": "A2",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 18,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    18
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/1bfd520ea28dab5a9e73bcca12d4b2fd30cdfff3de508735ed85f724a97de4fc.json`. SHA-256: `4d9bd0c34e3170af5d4270b080a76820188320c2c2e896fdd8464346ca64f570`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2cf80047f97d9a62198256ed6182dcdc270d6bbdfbfae4a07b3b620c501d52d6.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 9
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 10
    },
    {
      "activity_id": "A16",
      "start_slot": 11
    },
    {
      "activity_id": "A2",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 18,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    18
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/c8c96d1f1f131c07c7d4e62be513f1bdaec8c14432679be0210f2709647fcf01.json`. SHA-256: `b9a2e7cac8e3b84df356a376090a6552e6dbff3e0cc087071a141388a817eff7`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2cf80047f97d9a62198256ed6182dcdc270d6bbdfbfae4a07b3b620c501d52d6.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C06

**Mixed order resource · 16 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 24 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,24) and has capacity one.
Participant P2 is available in [0,24) and has capacity one.
Participant P3 is available in [0,24) and has capacity one.
Participant P4 is available in [0,24) and has capacity one.
Resource R1 is available in [0,24) and has capacity one.
Resource R2 is available in [0,24) and has capacity one.
Activity A13 lasts 2 slots; participants: P4; resources: R2; availability: [5,9).
Activity A11 lasts 2 slots; participants: P1, P2; resources: R1; availability: [2,9).
Activity A5 lasts 2 slots; participants: P1; resources: R1; availability: [0,6).
Activity A16 lasts 2 slots; participants: P1, P4; resources: R1; availability: [0,8).
Activity A15 lasts 2 slots; participants: P1; resources: none; availability: [10,16).
Activity A9 lasts 3 slots; participants: P3; resources: none; availability: [1,6).
Activity A6 lasts 2 slots; participants: P2; resources: none; availability: [0,6).
Activity A10 lasts 3 slots; participants: P3; resources: R2; availability: [5,11).
Activity A4 lasts 2 slots; participants: P3; resources: none; availability: [3,8).
Activity A12 lasts 3 slots; participants: P3; resources: R1; availability: [7,15).
Activity A8 lasts 2 slots; participants: P4; resources: R2; availability: [0,8).
Activity A3 lasts 2 slots; participants: P2; resources: R2; availability: [10,14).
Activity A1 lasts 2 slots; participants: P2; resources: R1; availability: [0,6).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A14 lasts 3 slots; participants: P2; resources: none; availability: [0,4), [5,15).
Activity A7 lasts 3 slots; participants: P1, P4; resources: R1; availability: [7,15).
A15 must finish at or before slot 13.
Starting A1 outside [5,9) incurs penalty 2; starting inside incurs zero.
Starting A6 outside [18,22) incurs penalty 2; starting inside incurs zero.
A1 must finish before or when A4 starts.
A11 must finish before or when A14 starts.
A5 must finish before or when A9 starts.
Starting A13 outside [5,9) incurs penalty 3; starting inside incurs zero.
A8 must finish before or when A13 starts.
A13 must finish before or when A15 starts.
A10 must finish before or when A3 starts.
A2 must finish at or before slot 5.
Starting A3 outside [0,4) incurs penalty 2; starting inside incurs zero.
A2 must finish before or when A13 starts.
Starting A15 outside [15,21) incurs penalty 1; starting inside incurs zero.
Starting A4 outside [1,5) incurs penalty 2; starting inside incurs zero.
A8 must finish before or when A14 starts.
A11 must finish before or when A10 starts.
A5 must finish before or when A2 starts.
A16 must finish before or when A11 starts.
A6 must finish at or before slot 5.
A10 must finish before or when A12 starts.
A2 must finish before or when A16 starts.
A13 must finish before or when A7 starts.
Starting A7 outside [15,17) incurs penalty 1; starting inside incurs zero.
A1 must finish before or when A6 starts.
A11 must finish before or when A15 starts.
Starting A9 outside [19,21) incurs penalty 2; starting inside incurs zero.
A5 must finish before or when A8 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-4223d2e0d112593a5b534873`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 24 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 24) |
| P2 | [0, 24) |
| P3 | [0, 24) |
| P4 | [0, 24) |
| R1 | [0, 24) |
| R2 | [0, 24) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A13 | 2 | P4 | R2 | [5, 9) |
| A11 | 2 | P1, P2 | R1 | [2, 9) |
| A5 | 2 | P1 | R1 | [0, 6) |
| A16 | 2 | P1, P4 | R1 | [0, 8) |
| A15 | 2 | P1 | None | [10, 16) |
| A9 | 3 | P3 | None | [1, 6) |
| A6 | 2 | P2 | None | [0, 6) |
| A10 | 3 | P3 | R2 | [5, 11) |
| A4 | 2 | P3 | None | [3, 8) |
| A12 | 3 | P3 | R1 | [7, 15) |
| A8 | 2 | P4 | R2 | [0, 8) |
| A3 | 2 | P2 | R2 | [10, 14) |
| A1 | 2 | P2 | R1 | [0, 6) |
| A2 | 2 | P1 | None | [0, 6) |
| A14 | 3 | P2 | None | [0, 4), [5, 15) |
| A7 | 3 | P1, P4 | R1 | [7, 15) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A15","id":"C_profile_deadline","slot":13,"type":"deadline"}`
- `{"activity_id":"A1","end":9,"id":"PREF1","start":5,"type":"preferred_start","weight":2}`
- `{"activity_id":"A6","end":22,"id":"PREF3","start":18,"type":"preferred_start","weight":2}`
- `{"after":"A4","before":"A1","id":"C_bg7","type":"precedence"}`
- `{"after":"A14","before":"A11","id":"C_extra12","type":"precedence"}`
- `{"after":"A9","before":"A5","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A13","end":9,"id":"PREF9","start":5,"type":"preferred_start","weight":3}`
- `{"after":"A13","before":"A8","id":"C_bg9","type":"precedence"}`
- `{"after":"A15","before":"A13","id":"C_bg15","type":"precedence"}`
- `{"after":"A3","before":"A10","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A2","id":"C2","slot":5,"type":"deadline"}`
- `{"activity_id":"A3","end":4,"id":"PREF13","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A13","before":"A2","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A15","end":21,"id":"PREF15","start":15,"type":"preferred_start","weight":1}`
- `{"activity_id":"A4","end":5,"id":"PREF7","start":1,"type":"preferred_start","weight":2}`
- `{"after":"A14","before":"A8","id":"C_bg12","type":"precedence"}`
- `{"after":"A10","before":"A11","id":"C_bg10","type":"precedence"}`
- `{"after":"A2","before":"A5","id":"C0","type":"precedence"}`
- `{"after":"A11","before":"A16","id":"C_bg8","type":"precedence"}`
- `{"activity_id":"A6","id":"C3","slot":5,"type":"deadline"}`
- `{"after":"A12","before":"A10","id":"C_bg14","type":"precedence"}`
- `{"after":"A16","before":"A2","id":"C_bg4","type":"precedence"}`
- `{"after":"A7","before":"A13","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A7","end":17,"id":"PREF11","start":15,"type":"preferred_start","weight":1}`
- `{"after":"A6","before":"A1","id":"C1","type":"precedence"}`
- `{"after":"A15","before":"A11","id":"C_extra15","type":"precedence"}`
- `{"activity_id":"A9","end":21,"id":"PREF5","start":19,"type":"preferred_start","weight":2}`
- `{"after":"A8","before":"A5","id":"C_bg6","type":"precedence"}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | INVALID_OUTPUT | invalid_output | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer failed the required output/schema contract."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4beee656240bd92909e1e70a755cca5e0848cde469b35f871cb9072431b1e424.json`. SHA-256: `6e9fcf207f5d5525013db98999e5874cf45960971b9d2ff9046cca77169579f7`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/7ae0fe15a2591d5a3f5fb5107052dc163fde1ca2b2ea14da2d5d65d0b6f484ab.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": {
          "after": "A2",
          "before": "A16",
          "type": "precedence"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "after": "A5",
          "before": "A2",
          "type": "precedence"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 2,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 0,
    "structurally_equivalent": false
  },
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/e302ebe618b9906ec6abf77bd63721bd29295a5047265fe85d04936e1118a5d9.json`. SHA-256: `b897a93463139e2b49ecac0dfbf31b136de2004b3e1c00f6f01394b8b1d95ce3`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/7ae0fe15a2591d5a3f5fb5107052dc163fde1ca2b2ea14da2d5d65d0b6f484ab.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/8370dd1be1cf0905693ce2e2c5247055ca7f5beb012598b81247f82522c245e7.json`. SHA-256: `ebecf7798e2ddc167a9732a79cf1a1d8b56e3b2fcb72a77c7059875c997893ca`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/7ae0fe15a2591d5a3f5fb5107052dc163fde1ca2b2ea14da2d5d65d0b6f484ab.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/d5720a74689755565b91e838b6fad9c46c3953c4c8d08638c7302f7bdde0e432.json`. SHA-256: `52231a0eef30b4a058d9ff814db00587c480f3b069a808db58f6b009963e1a46`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/7ae0fe15a2591d5a3f5fb5107052dc163fde1ca2b2ea14da2d5d65d0b6f484ab.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C07

**Participant contention · 24 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T00:00:00+08:00, timezone +08:00. There are 40 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,36) and has capacity one.
Participant P2 is available in [0,40) and has capacity one.
Participant P3 is available in [0,40) and has capacity one.
Participant P4 is available in [0,40) and has capacity one.
Participant P5 is available in [0,40) and has capacity one.
Participant P6 is available in [0,40) and has capacity one.
Resource R1 is available in [0,40) and has capacity one.
Resource R2 is available in [0,40) and has capacity one.
Activity A15 lasts 1 slots; participants: P1, P4; resources: R1; availability: [0,7).
Activity A8 lasts 2 slots; participants: P1, P4; resources: R1; availability: [17,27).
Activity A24 lasts 1 slots; participants: P1; resources: none; availability: [0,9).
Activity A14 lasts 2 slots; participants: P1, P5; resources: none; availability: [11,26).
Activity A23 lasts 2 slots; participants: P1; resources: none; availability: [23,36).
Activity A18 lasts 2 slots; participants: P1; resources: none; availability: [5,21).
Activity A3 lasts 2 slots; participants: P1, P6; resources: R1; availability: [0,13).
Activity A2 lasts 1 slots; participants: P1, P6; resources: R1; availability: [15,34).
Activity A7 lasts 1 slots; participants: P1, P3; resources: none; availability: [28,40).
Activity A9 lasts 2 slots; participants: P1, P2; resources: R2; availability: [0,11).
Activity A5 lasts 1 slots; participants: P1, P4; resources: R1; availability: [9,15).
Activity A11 lasts 2 slots; participants: P1, P5; resources: none; availability: [20,40).
Activity A4 lasts 2 slots; participants: P1, P5; resources: none; availability: [0,9).
Activity A6 lasts 1 slots; participants: P1, P2; resources: R2; availability: [10,19).
Activity A20 lasts 1 slots; participants: P1, P5; resources: none; availability: [3,24).
Activity A10 lasts 2 slots; participants: P1, P2; resources: R1; availability: [16,40).
Activity A13 lasts 1 slots; participants: P1, P3; resources: none; availability: [17,31).
Activity A22 lasts 2 slots; participants: P1, P2; resources: R1; availability: [10,23).
Activity A19 lasts 1 slots; participants: P1, P6; resources: R2; availability: [9,24).
Activity A21 lasts 1 slots; participants: P1, P3; resources: none; availability: [4,19).
Activity A12 lasts 1 slots; participants: P1, P4; resources: R1; availability: [27,32).
Activity A17 lasts 2 slots; participants: P1, P6; resources: R1; availability: [30,40).
Activity A16 lasts 1 slots; participants: P1; resources: none; availability: [14,26).
Activity A1 lasts 1 slots; participants: P1, P3; resources: none; availability: [0,6).
A2 must finish before or when A17 starts.
A3 must finish before or when A6 starts.
Starting A16 outside [24,28) incurs penalty 1; starting inside incurs zero.
Starting A23 outside [28,32) incurs penalty 3; starting inside incurs zero.
Starting A7 outside [30,32) incurs penalty 2; starting inside incurs zero.
Starting A13 outside [28,32) incurs penalty 2; starting inside incurs zero.
A4 must finish before or when A3 starts.
Starting A21 outside [23,27) incurs penalty 3; starting inside incurs zero.
Starting A18 outside [8,12) incurs penalty 2; starting inside incurs zero.
Starting A1 outside [25,27) incurs penalty 2; starting inside incurs zero.
A24 must finish before or when A1 starts.
A6 must finish before or when A2 starts.
Starting A24 outside [20,26) incurs penalty 2; starting inside incurs zero.
A15 must finish before or when A4 starts.
A24 must start exactly at slot 0.
Starting A4 outside [33,37) incurs penalty 2; starting inside incurs zero.
A20 must finish before or when A16 starts.
A9 must finish before or when A10 starts.
Starting A11 outside [22,26) incurs penalty 2; starting inside incurs zero.
A16 must finish before or when A7 starts.
Starting A14 outside [28,34) incurs penalty 1; starting inside incurs zero.
Starting A20 outside [13,15) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-01ec17d777f7eceec11b5470`. Gold label: **SAT**. Horizon: `2026-10-26T00:00:00+08:00`; timezone `+08:00`; 40 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 36) |
| P2 | [0, 40) |
| P3 | [0, 40) |
| P4 | [0, 40) |
| P5 | [0, 40) |
| P6 | [0, 40) |
| R1 | [0, 40) |
| R2 | [0, 40) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A15 | 1 | P1, P4 | R1 | [0, 7) |
| A8 | 2 | P1, P4 | R1 | [17, 27) |
| A24 | 1 | P1 | None | [0, 9) |
| A14 | 2 | P1, P5 | None | [11, 26) |
| A23 | 2 | P1 | None | [23, 36) |
| A18 | 2 | P1 | None | [5, 21) |
| A3 | 2 | P1, P6 | R1 | [0, 13) |
| A2 | 1 | P1, P6 | R1 | [15, 34) |
| A7 | 1 | P1, P3 | None | [28, 40) |
| A9 | 2 | P1, P2 | R2 | [0, 11) |
| A5 | 1 | P1, P4 | R1 | [9, 15) |
| A11 | 2 | P1, P5 | None | [20, 40) |
| A4 | 2 | P1, P5 | None | [0, 9) |
| A6 | 1 | P1, P2 | R2 | [10, 19) |
| A20 | 1 | P1, P5 | None | [3, 24) |
| A10 | 2 | P1, P2 | R1 | [16, 40) |
| A13 | 1 | P1, P3 | None | [17, 31) |
| A22 | 2 | P1, P2 | R1 | [10, 23) |
| A19 | 1 | P1, P6 | R2 | [9, 24) |
| A21 | 1 | P1, P3 | None | [4, 19) |
| A12 | 1 | P1, P4 | R1 | [27, 32) |
| A17 | 2 | P1, P6 | R1 | [30, 40) |
| A16 | 1 | P1 | None | [14, 26) |
| A1 | 1 | P1, P3 | None | [0, 6) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A17","before":"A2","id":"C_edge23","type":"precedence"}`
- `{"after":"A6","before":"A3","id":"C_edge7","type":"precedence"}`
- `{"activity_id":"A16","end":28,"id":"PREF12","start":24,"type":"preferred_start","weight":1}`
- `{"activity_id":"A23","end":32,"id":"PREF18","start":28,"type":"preferred_start","weight":3}`
- `{"activity_id":"A7","end":32,"id":"PREF20","start":30,"type":"preferred_start","weight":2}`
- `{"activity_id":"A13","end":32,"id":"PREF14","start":28,"type":"preferred_start","weight":2}`
- `{"after":"A3","before":"A4","id":"C_edge5","type":"precedence"}`
- `{"activity_id":"A21","end":27,"id":"PREF8","start":23,"type":"preferred_start","weight":3}`
- `{"activity_id":"A18","end":12,"id":"PREF6","start":8,"type":"preferred_start","weight":2}`
- `{"activity_id":"A1","end":27,"id":"PREF2","start":25,"type":"preferred_start","weight":2}`
- `{"after":"A1","before":"A24","id":"C_edge2","type":"precedence"}`
- `{"after":"A2","before":"A6","id":"C_edge17","type":"precedence"}`
- `{"activity_id":"A24","end":26,"id":"PREF0","start":20,"type":"preferred_start","weight":2}`
- `{"after":"A4","before":"A15","id":"C_edge4","type":"precedence"}`
- `{"activity_id":"A24","id":"C_profile_fixed","slot":0,"type":"fixed_start"}`
- `{"activity_id":"A4","end":37,"id":"PREF4","start":33,"type":"preferred_start","weight":2}`
- `{"after":"A16","before":"A20","id":"C_edge12","type":"precedence"}`
- `{"after":"A10","before":"A9","id":"C_edge19","type":"precedence"}`
- `{"activity_id":"A11","end":26,"id":"PREF22","start":22,"type":"preferred_start","weight":2}`
- `{"after":"A7","before":"A16","id":"C_edge20","type":"precedence"}`
- `{"activity_id":"A14","end":34,"id":"PREF16","start":28,"type":"preferred_start","weight":1}`
- `{"activity_id":"A20","end":15,"id":"PREF10","start":13,"type":"preferred_start","weight":1}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":10,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 1
  },
  {
    "activity_id": "A10",
    "start_slot": 26
  },
  {
    "activity_id": "A11",
    "start_slot": 22
  },
  {
    "activity_id": "A12",
    "start_slot": 29
  },
  {
    "activity_id": "A13",
    "start_slot": 28
  },
  {
    "activity_id": "A14",
    "start_slot": 15
  },
  {
    "activity_id": "A15",
    "start_slot": 2
  },
  {
    "activity_id": "A16",
    "start_slot": 24
  },
  {
    "activity_id": "A17",
    "start_slot": 33
  },
  {
    "activity_id": "A18",
    "start_slot": 8
  },
  {
    "activity_id": "A19",
    "start_slot": 21
  },
  {
    "activity_id": "A2",
    "start_slot": 25
  },
  {
    "activity_id": "A20",
    "start_slot": 13
  },
  {
    "activity_id": "A21",
    "start_slot": 7
  },
  {
    "activity_id": "A22",
    "start_slot": 19
  },
  {
    "activity_id": "A23",
    "start_slot": 31
  },
  {
    "activity_id": "A24",
    "start_slot": 0
  },
  {
    "activity_id": "A3",
    "start_slot": 10
  },
  {
    "activity_id": "A4",
    "start_slot": 3
  },
  {
    "activity_id": "A5",
    "start_slot": 14
  },
  {
    "activity_id": "A6",
    "start_slot": 12
  },
  {
    "activity_id": "A7",
    "start_slot": 30
  },
  {
    "activity_id": "A8",
    "start_slot": 17
  },
  {
    "activity_id": "A9",
    "start_slot": 5
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[10]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/818275eb3a37fdc77d20c55d9d034c8c19b605e6d07796d6127e918df4ccfd88.json`. SHA-256: `b8cf7f3026c35ffcad6e96552c0bf618f9a0ee2b296a2d2bba862fcb90c4fd03`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/e8ed70fae188a153573dfeb137bdccd79cd0902abc22acd81d19a5a49b2220a8.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 1
    },
    {
      "activity_id": "A10",
      "start_slot": 26
    },
    {
      "activity_id": "A11",
      "start_slot": 22
    },
    {
      "activity_id": "A12",
      "start_slot": 29
    },
    {
      "activity_id": "A13",
      "start_slot": 28
    },
    {
      "activity_id": "A14",
      "start_slot": 15
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 24
    },
    {
      "activity_id": "A17",
      "start_slot": 33
    },
    {
      "activity_id": "A18",
      "start_slot": 8
    },
    {
      "activity_id": "A19",
      "start_slot": 21
    },
    {
      "activity_id": "A2",
      "start_slot": 25
    },
    {
      "activity_id": "A20",
      "start_slot": 13
    },
    {
      "activity_id": "A21",
      "start_slot": 7
    },
    {
      "activity_id": "A22",
      "start_slot": 19
    },
    {
      "activity_id": "A23",
      "start_slot": 31
    },
    {
      "activity_id": "A24",
      "start_slot": 0
    },
    {
      "activity_id": "A3",
      "start_slot": 10
    },
    {
      "activity_id": "A4",
      "start_slot": 3
    },
    {
      "activity_id": "A5",
      "start_slot": 14
    },
    {
      "activity_id": "A6",
      "start_slot": 12
    },
    {
      "activity_id": "A7",
      "start_slot": 30
    },
    {
      "activity_id": "A8",
      "start_slot": 17
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/00aa77fb3a32ed1336b5380b3f001d0e92b20054bdcaf6b23946f765784783f9.json`. SHA-256: `0b3c6b6474c0da54ccf3984c520a4cfdfe2db100ec4406684091a9d21205af32`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/e8ed70fae188a153573dfeb137bdccd79cd0902abc22acd81d19a5a49b2220a8.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 1
    },
    {
      "activity_id": "A10",
      "start_slot": 34
    },
    {
      "activity_id": "A11",
      "start_slot": 23
    },
    {
      "activity_id": "A12",
      "start_slot": 27
    },
    {
      "activity_id": "A13",
      "start_slot": 28
    },
    {
      "activity_id": "A14",
      "start_slot": 21
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 25
    },
    {
      "activity_id": "A17",
      "start_slot": 32
    },
    {
      "activity_id": "A18",
      "start_slot": 9
    },
    {
      "activity_id": "A19",
      "start_slot": 18
    },
    {
      "activity_id": "A2",
      "start_slot": 15
    },
    {
      "activity_id": "A20",
      "start_slot": 14
    },
    {
      "activity_id": "A21",
      "start_slot": 11
    },
    {
      "activity_id": "A22",
      "start_slot": 16
    },
    {
      "activity_id": "A23",
      "start_slot": 29
    },
    {
      "activity_id": "A24",
      "start_slot": 0
    },
    {
      "activity_id": "A3",
      "start_slot": 5
    },
    {
      "activity_id": "A4",
      "start_slot": 3
    },
    {
      "activity_id": "A5",
      "start_slot": 12
    },
    {
      "activity_id": "A6",
      "start_slot": 13
    },
    {
      "activity_id": "A7",
      "start_slot": 31
    },
    {
      "activity_id": "A8",
      "start_slot": 19
    },
    {
      "activity_id": "A9",
      "start_slot": 7
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/38ad56b115b11a38c0dd2099e6b72569c3ae3ef7987811b773af16f3f78340d5.json`. SHA-256: `45a2ae6ae2ac0720eee00930cb542304bf05c9ffe0316eed416dd3f490a4afe1`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/e8ed70fae188a153573dfeb137bdccd79cd0902abc22acd81d19a5a49b2220a8.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 1
    },
    {
      "activity_id": "A10",
      "start_slot": 26
    },
    {
      "activity_id": "A11",
      "start_slot": 22
    },
    {
      "activity_id": "A12",
      "start_slot": 29
    },
    {
      "activity_id": "A13",
      "start_slot": 28
    },
    {
      "activity_id": "A14",
      "start_slot": 15
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 24
    },
    {
      "activity_id": "A17",
      "start_slot": 33
    },
    {
      "activity_id": "A18",
      "start_slot": 8
    },
    {
      "activity_id": "A19",
      "start_slot": 21
    },
    {
      "activity_id": "A2",
      "start_slot": 25
    },
    {
      "activity_id": "A20",
      "start_slot": 13
    },
    {
      "activity_id": "A21",
      "start_slot": 7
    },
    {
      "activity_id": "A22",
      "start_slot": 19
    },
    {
      "activity_id": "A23",
      "start_slot": 31
    },
    {
      "activity_id": "A24",
      "start_slot": 0
    },
    {
      "activity_id": "A3",
      "start_slot": 10
    },
    {
      "activity_id": "A4",
      "start_slot": 3
    },
    {
      "activity_id": "A5",
      "start_slot": 14
    },
    {
      "activity_id": "A6",
      "start_slot": 12
    },
    {
      "activity_id": "A7",
      "start_slot": 30
    },
    {
      "activity_id": "A8",
      "start_slot": 17
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/44b07bd6709fb62de25889399365eb511bd9726301b4f1e18878051e8d02473a.json`. SHA-256: `6c008c16c4c3be151406795f44d015152fa8246056726bf2bc5c3cb5b9890182`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/e8ed70fae188a153573dfeb137bdccd79cd0902abc22acd81d19a5a49b2220a8.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C08

**Participant contention · 24 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T00:00:00+08:00, timezone +08:00. There are 40 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,33) and has capacity one.
Participant P2 is available in [0,40) and has capacity one.
Participant P3 is available in [0,40) and has capacity one.
Participant P4 is available in [0,40) and has capacity one.
Participant P5 is available in [0,40) and has capacity one.
Participant P6 is available in [0,40) and has capacity one.
Resource R1 is available in [0,40) and has capacity one.
Resource R2 is available in [0,40) and has capacity one.
Activity A16 lasts 1 slots; participants: P1, P4; resources: R1; availability: [6,22).
Activity A12 lasts 1 slots; participants: P1, P3; resources: none; availability: [19,36).
Activity A17 lasts 2 slots; participants: P1, P2; resources: R1; availability: [16,39).
Activity A10 lasts 1 slots; participants: P1, P5; resources: none; availability: [13,20).
Activity A13 lasts 1 slots; participants: P1; resources: none; availability: [3,21).
Activity A18 lasts 1 slots; participants: P1, P5; resources: none; availability: [4,13).
Activity A3 lasts 2 slots; participants: P1, P5; resources: none; availability: [28,34).
Activity A6 lasts 1 slots; participants: P1, P6; resources: R2; availability: [21,36).
Activity A1 lasts 1 slots; participants: P1, P3; resources: none; availability: [11,22).
Activity A24 lasts 2 slots; participants: P1, P6; resources: R1; availability: [0,13).
Activity A7 lasts 2 slots; participants: P1; resources: none; availability: [7,28).
Activity A14 lasts 2 slots; participants: P1, P3; resources: none; availability: [0,8).
Activity A11 lasts 1 slots; participants: P1, P4; resources: R1; availability: [4,7).
Activity A2 lasts 2 slots; participants: P1, P3; resources: none; availability: [0,21).
Activity A5 lasts 1 slots; participants: P1, P4; resources: R2; availability: [13,24).
Activity A19 lasts 2 slots; participants: P1; resources: none; availability: [0,7).
Activity A23 lasts 1 slots; participants: P1, P6; resources: R1; availability: [19,33).
Activity A15 lasts 2 slots; participants: P1, P5; resources: none; availability: [12,30).
Activity A9 lasts 2 slots; participants: P1; resources: none; availability: [22,32).
Activity A20 lasts 1 slots; participants: P1, P4; resources: R2; availability: [28,38).
Activity A21 lasts 2 slots; participants: P1, P6; resources: R2; availability: [6,23).
Activity A8 lasts 1 slots; participants: P1, P2; resources: R1; availability: [9,24).
Activity A4 lasts 1 slots; participants: P1, P2; resources: R1; availability: [0,21).
Activity A22 lasts 1 slots; participants: P1, P2; resources: R1; availability: [0,5).
Starting A22 outside [32,36) incurs penalty 1; starting inside incurs zero.
A24 must finish before or when A15 starts.
Starting A16 outside [24,28) incurs penalty 3; starting inside incurs zero.
Starting A23 outside [14,16) incurs penalty 1; starting inside incurs zero.
A24 must finish before or when A8 starts.
Starting A17 outside [1,5) incurs penalty 2; starting inside incurs zero.
Starting A4 outside [18,24) incurs penalty 1; starting inside incurs zero.
A22 must finish before or when A9 starts.
A14 must finish before or when A5 starts.
Starting A21 outside [8,10) incurs penalty 2; starting inside incurs zero.
Starting A8 outside [16,22) incurs penalty 2; starting inside incurs zero.
A19 must finish before or when A2 starts.
A18 must finish before or when A1 starts.
A10 must finish before or when A23 starts.
A2 must finish at or before slot 14.
Starting A6 outside [34,38) incurs penalty 1; starting inside incurs zero.
A19 must finish before or when A21 starts.
Starting A20 outside [34,40) incurs penalty 1; starting inside incurs zero.
Starting A5 outside [0,6) incurs penalty 2; starting inside incurs zero.
A8 must finish before or when A3 starts.
Starting A11 outside [32,36) incurs penalty 2; starting inside incurs zero.
A22 must finish before or when A18 starts.
Starting A24 outside [2,6) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-048235a303abd98445509337`. Gold label: **UNSAT**. Horizon: `2026-10-26T00:00:00+08:00`; timezone `+08:00`; 40 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 33) |
| P2 | [0, 40) |
| P3 | [0, 40) |
| P4 | [0, 40) |
| P5 | [0, 40) |
| P6 | [0, 40) |
| R1 | [0, 40) |
| R2 | [0, 40) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A16 | 1 | P1, P4 | R1 | [6, 22) |
| A12 | 1 | P1, P3 | None | [19, 36) |
| A17 | 2 | P1, P2 | R1 | [16, 39) |
| A10 | 1 | P1, P5 | None | [13, 20) |
| A13 | 1 | P1 | None | [3, 21) |
| A18 | 1 | P1, P5 | None | [4, 13) |
| A3 | 2 | P1, P5 | None | [28, 34) |
| A6 | 1 | P1, P6 | R2 | [21, 36) |
| A1 | 1 | P1, P3 | None | [11, 22) |
| A24 | 2 | P1, P6 | R1 | [0, 13) |
| A7 | 2 | P1 | None | [7, 28) |
| A14 | 2 | P1, P3 | None | [0, 8) |
| A11 | 1 | P1, P4 | R1 | [4, 7) |
| A2 | 2 | P1, P3 | None | [0, 21) |
| A5 | 1 | P1, P4 | R2 | [13, 24) |
| A19 | 2 | P1 | None | [0, 7) |
| A23 | 1 | P1, P6 | R1 | [19, 33) |
| A15 | 2 | P1, P5 | None | [12, 30) |
| A9 | 2 | P1 | None | [22, 32) |
| A20 | 1 | P1, P4 | R2 | [28, 38) |
| A21 | 2 | P1, P6 | R2 | [6, 23) |
| A8 | 1 | P1, P2 | R1 | [9, 24) |
| A4 | 1 | P1, P2 | R1 | [0, 21) |
| A22 | 1 | P1, P2 | R1 | [0, 5) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A22","end":36,"id":"PREF1","start":32,"type":"preferred_start","weight":1}`
- `{"after":"A15","before":"A24","id":"C_edge16","type":"precedence"}`
- `{"activity_id":"A16","end":28,"id":"PREF9","start":24,"type":"preferred_start","weight":3}`
- `{"activity_id":"A23","end":16,"id":"PREF17","start":14,"type":"preferred_start","weight":1}`
- `{"after":"A8","before":"A24","id":"C_edge13","type":"precedence"}`
- `{"activity_id":"A17","end":5,"id":"PREF19","start":1,"type":"preferred_start","weight":2}`
- `{"activity_id":"A4","end":24,"id":"PREF7","start":18,"type":"preferred_start","weight":1}`
- `{"after":"A9","before":"A22","id":"C_edge18","type":"precedence"}`
- `{"after":"A5","before":"A14","id":"C_edge15","type":"precedence"}`
- `{"activity_id":"A21","end":10,"id":"PREF11","start":8,"type":"preferred_start","weight":2}`
- `{"activity_id":"A8","end":22,"id":"PREF13","start":16,"type":"preferred_start","weight":2}`
- `{"after":"A2","before":"A19","id":"C_edge8","type":"precedence"}`
- `{"after":"A1","before":"A18","id":"C_edge14","type":"precedence"}`
- `{"after":"A23","before":"A10","id":"C_edge17","type":"precedence"}`
- `{"activity_id":"A2","id":"C_profile_deadline","slot":14,"type":"deadline"}`
- `{"activity_id":"A6","end":38,"id":"PREF23","start":34,"type":"preferred_start","weight":1}`
- `{"after":"A21","before":"A19","id":"C_edge11","type":"precedence"}`
- `{"activity_id":"A20","end":40,"id":"PREF21","start":34,"type":"preferred_start","weight":1}`
- `{"activity_id":"A5","end":6,"id":"PREF15","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A3","before":"A8","id":"C_edge22","type":"precedence"}`
- `{"activity_id":"A11","end":36,"id":"PREF3","start":32,"type":"preferred_start","weight":2}`
- `{"after":"A18","before":"A22","id":"C_edge4","type":"precedence"}`
- `{"activity_id":"A24","end":6,"id":"PREF5","start":2,"type":"preferred_start","weight":1}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/466b016cb1d413db588a02686fa5d9fd7e62711b520f7ee6643b6e9942afd9b8.json`. SHA-256: `e1eda888221892ee3d4942be81ec1f06a6643490345927b7d3ac61e6046375de`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/6a310063af253ecf8d2ee37a9c993ee4bf56baa94c36477078d40afdbeba5044.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/fce85ba8ec1adf7715d36f6112c3b12e9d42c5dfe05820370b4e19a001b03f0f.json`. SHA-256: `d787cd178ddfc43e0e62be880088daf31a338ea29f40a453334c9afd6079d59f`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/6a310063af253ecf8d2ee37a9c993ee4bf56baa94c36477078d40afdbeba5044.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/60771a1ff3759d06a88e211434e410256ee5da6f4fab3d24a47d12efa63866b3.json`. SHA-256: `678425bd3a7eb335bbb9f834a28aa038567f376e2d2669dc9e9bffd9fc5e508f`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/6a310063af253ecf8d2ee37a9c993ee4bf56baa94c36477078d40afdbeba5044.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/f5dcd9aa96a1a34b3b62a3716c23b236026951cf99c85b4d5a87d224ea45dc3d.json`. SHA-256: `261d4a5d624d69fd5e3c2b201e976aa33bbd3a68bc1ab4cb3c8f859e03a7433b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/6a310063af253ecf8d2ee37a9c993ee4bf56baa94c36477078d40afdbeba5044.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C09

**Participant crossing · 32 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 32 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,32) and has capacity one.
Participant P2 is available in [0,32) and has capacity one.
Participant P3 is available in [0,32) and has capacity one.
Participant P4 is available in [0,32) and has capacity one.
Participant P5 is available in [0,32) and has capacity one.
Participant P6 is available in [0,32) and has capacity one.
Participant P7 is available in [0,32) and has capacity one.
Participant P8 is available in [0,32) and has capacity one.
Resource R1 is available in [0,32) and has capacity one.
Resource R2 is available in [0,32) and has capacity one.
Resource R3 is available in [0,32) and has capacity one.
Activity A18 lasts 2 slots; participants: P8; resources: R3; availability: [0,9).
Activity A9 lasts 2 slots; participants: P3; resources: R1; availability: [3,13).
Activity A17 lasts 2 slots; participants: P5; resources: R2; availability: [0,8).
Activity A3 lasts 2 slots; participants: P7; resources: none; availability: [0,3), [6,12).
Activity A23 lasts 2 slots; participants: P6, P7; resources: none; availability: [8,15).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [0,2).
Activity A4 lasts 2 slots; participants: P8; resources: none; availability: [1,8).
Activity A5 lasts 2 slots; participants: P5; resources: none; availability: [6,16).
Activity A13 lasts 2 slots; participants: P6; resources: R3; availability: [0,8).
Activity A21 lasts 2 slots; participants: P6, P8; resources: none; availability: [8,18).
Activity A1 lasts 2 slots; participants: P3; resources: R1; availability: [4,10).
Activity A7 lasts 3 slots; participants: P1; resources: none; availability: [3,13).
Activity A16 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [9,20).
Activity A6 lasts 2 slots; participants: P4; resources: R2; availability: [5,13).
Activity A19 lasts 3 slots; participants: P2; resources: none; availability: [4,12).
Activity A12 lasts 2 slots; participants: P6; resources: none; availability: [0,14).
Activity A32 lasts 2 slots; participants: P6; resources: none; availability: [7,15).
Activity A28 lasts 3 slots; participants: P1; resources: R3; availability: [12,17).
Activity A8 lasts 3 slots; participants: P1; resources: none; availability: [2,14).
Activity A20 lasts 2 slots; participants: P8; resources: none; availability: [0,14).
Activity A14 lasts 2 slots; participants: P6; resources: none; availability: [0,7).
Activity A15 lasts 2 slots; participants: P4, P7; resources: R3; availability: [5,10).
Activity A24 lasts 2 slots; participants: P2; resources: R3; availability: [9,16).
Activity A22 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [5,11).
Activity A26 lasts 3 slots; participants: P4, P7; resources: R1; availability: [0,5).
Activity A27 lasts 3 slots; participants: P3; resources: R1; availability: [0,4), [6,14).
Activity A31 lasts 3 slots; participants: P5; resources: none; availability: [0,10).
Activity A25 lasts 2 slots; participants: P1; resources: none; availability: [2,12).
Activity A11 lasts 2 slots; participants: P1, P2; resources: none; availability: [0,4).
Activity A10 lasts 2 slots; participants: P2; resources: none; availability: [2,4).
Activity A29 lasts 2 slots; participants: P8; resources: R3; availability: [0,3), [8,12).
Activity A30 lasts 2 slots; participants: P5; resources: R2; availability: [3,15).
A22 must finish before or when A23 starts.
A25 must finish before or when A15 starts.
Starting A12 outside [18,24) incurs penalty 2; starting inside incurs zero.
A11 must finish before or when A25 starts.
A10 must finish before or when A18 starts.
A23 must finish before or when A28 starts.
A1 must finish before or when A23 starts.
Starting A32 outside [12,18) incurs penalty 1; starting inside incurs zero.
Starting A31 outside [16,22) incurs penalty 3; starting inside incurs zero.
A12 must finish before or when A3 starts.
A23 must finish before or when A21 starts.
A2 must finish before or when A21 starts.
Starting A25 outside [8,14) incurs penalty 1; starting inside incurs zero.
A11 must finish before or when A5 starts.
A2 must finish before or when A4 starts.
A26 must finish before or when A22 starts.
Starting A4 outside [20,24) incurs penalty 3; starting inside incurs zero.
A10 must finish before or when A26 starts.
A26 must finish before or when A9 starts.
Starting A30 outside [20,24) incurs penalty 1; starting inside incurs zero.
A15 must finish before or when A1 starts.
Starting A16 outside [12,16) incurs penalty 3; starting inside incurs zero.
A26 must finish before or when A12 starts.
Starting A6 outside [11,17) incurs penalty 1; starting inside incurs zero.
A31 must finish before or when A7 starts.
A17 must finish before or when A27 starts.
A11 must finish before or when A30 starts.
Starting A24 outside [2,4) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A8 starts.
A17 must finish before or when A19 starts.
Starting A27 outside [0,4) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A20 starts.
A2 must finish before or when A17 starts.
A20 must finish before or when A29 starts.
A9 must finish before or when A30 starts.
A8 must finish before or when A24 starts.
A32 must finish before or when A24 starts.
A4 must finish before or when A20 starts.
A8 must finish before or when A16 starts.
Starting A29 outside [13,17) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A13 starts.
A2 must finish before or when A14 starts.
Starting A2 outside [25,27) incurs penalty 2; starting inside incurs zero.
A13 must finish before or when A8 starts.
Starting A5 outside [20,22) incurs penalty 3; starting inside incurs zero.
A11 must finish before or when A31 starts.
A7 must finish before or when A16 starts.
A2 must finish before or when A26 starts.
A26 must finish before or when A32 starts.
Starting A22 outside [2,6) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A25 starts.
A17 must finish before or when A4 starts.
A8 must finish before or when A6 starts.
Starting A11 outside [21,27) incurs penalty 2; starting inside incurs zero.
Starting A3 outside [14,16) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-0f9064a585c1e0a074b5e825`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 32 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 32) |
| P2 | [0, 32) |
| P3 | [0, 32) |
| P4 | [0, 32) |
| P5 | [0, 32) |
| P6 | [0, 32) |
| P7 | [0, 32) |
| P8 | [0, 32) |
| R1 | [0, 32) |
| R2 | [0, 32) |
| R3 | [0, 32) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A18 | 2 | P8 | R3 | [0, 9) |
| A9 | 2 | P3 | R1 | [3, 13) |
| A17 | 2 | P5 | R2 | [0, 8) |
| A3 | 2 | P7 | None | [0, 3), [6, 12) |
| A23 | 2 | P6, P7 | None | [8, 15) |
| A2 | 2 | P1 | None | [0, 2) |
| A4 | 2 | P8 | None | [1, 8) |
| A5 | 2 | P5 | None | [6, 16) |
| A13 | 2 | P6 | R3 | [0, 8) |
| A21 | 2 | P6, P8 | None | [8, 18) |
| A1 | 2 | P3 | R1 | [4, 10) |
| A7 | 3 | P1 | None | [3, 13) |
| A16 | 2 | P2 | R2 | [0, 3), [9, 20) |
| A6 | 2 | P4 | R2 | [5, 13) |
| A19 | 3 | P2 | None | [4, 12) |
| A12 | 2 | P6 | None | [0, 14) |
| A32 | 2 | P6 | None | [7, 15) |
| A28 | 3 | P1 | R3 | [12, 17) |
| A8 | 3 | P1 | None | [2, 14) |
| A20 | 2 | P8 | None | [0, 14) |
| A14 | 2 | P6 | None | [0, 7) |
| A15 | 2 | P4, P7 | R3 | [5, 10) |
| A24 | 2 | P2 | R3 | [9, 16) |
| A22 | 2 | P2 | R2 | [0, 3), [5, 11) |
| A26 | 3 | P4, P7 | R1 | [0, 5) |
| A27 | 3 | P3 | R1 | [0, 4), [6, 14) |
| A31 | 3 | P5 | None | [0, 10) |
| A25 | 2 | P1 | None | [2, 12) |
| A11 | 2 | P1, P2 | None | [0, 4) |
| A10 | 2 | P2 | None | [2, 4) |
| A29 | 2 | P8 | R3 | [0, 3), [8, 12) |
| A30 | 2 | P5 | R2 | [3, 15) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A23","before":"A22","id":"C_extra21","type":"precedence"}`
- `{"after":"A15","before":"A25","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A12","end":24,"id":"PREF14","start":18,"type":"preferred_start","weight":2}`
- `{"after":"A25","before":"A11","id":"C_bg12","type":"precedence"}`
- `{"after":"A18","before":"A10","id":"C_bg29","type":"precedence"}`
- `{"after":"A28","before":"A23","id":"C_bg25","type":"precedence"}`
- `{"after":"A23","before":"A1","id":"C_bg21","type":"precedence"}`
- `{"activity_id":"A32","end":18,"id":"PREF22","start":12,"type":"preferred_start","weight":1}`
- `{"activity_id":"A31","end":22,"id":"PREF8","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A12","id":"C_bg20","type":"precedence"}`
- `{"after":"A21","before":"A23","id":"C_bg27","type":"precedence"}`
- `{"after":"A21","before":"A2","id":"C_extra27","type":"precedence"}`
- `{"activity_id":"A25","end":14,"id":"PREF12","start":8,"type":"preferred_start","weight":1}`
- `{"after":"A5","before":"A11","id":"C_bg26","type":"precedence"}`
- `{"after":"A4","before":"A2","id":"C_extra6","type":"precedence"}`
- `{"after":"A22","before":"A26","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A4","end":24,"id":"PREF6","start":20,"type":"preferred_start","weight":3}`
- `{"after":"A26","before":"A10","id":"C_bg3","type":"precedence"}`
- `{"after":"A9","before":"A26","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A30","end":24,"id":"PREF18","start":20,"type":"preferred_start","weight":1}`
- `{"after":"A1","before":"A15","id":"C_bg17","type":"precedence"}`
- `{"activity_id":"A16","end":16,"id":"PREF24","start":12,"type":"preferred_start","weight":3}`
- `{"after":"A12","before":"A26","id":"C_bg14","type":"precedence"}`
- `{"activity_id":"A6","end":17,"id":"PREF10","start":11,"type":"preferred_start","weight":1}`
- `{"after":"A7","before":"A31","id":"C_bg23","type":"precedence"}`
- `{"after":"A27","before":"A17","id":"C_bg28","type":"precedence"}`
- `{"after":"A30","before":"A11","id":"C_bg18","type":"precedence"}`
- `{"activity_id":"A24","end":4,"id":"PREF30","start":2,"type":"preferred_start","weight":2}`
- `{"after":"A8","before":"A17","id":"C_extra9","type":"precedence"}`
- `{"after":"A19","before":"A17","id":"C_bg19","type":"precedence"}`
- `{"activity_id":"A27","end":4,"id":"PREF28","start":0,"type":"preferred_start","weight":3}`
- `{"after":"A20","before":"A2","id":"C_extra15","type":"precedence"}`
- `{"after":"A17","before":"A2","id":"C_bg5","type":"precedence"}`
- `{"after":"A29","before":"A20","id":"C_bg16","type":"precedence"}`
- `{"after":"A30","before":"A9","id":"C_extra18","type":"precedence"}`
- `{"after":"A24","before":"A8","id":"C_bg30","type":"precedence"}`
- `{"after":"A24","before":"A32","id":"C_extra30","type":"precedence"}`
- `{"after":"A20","before":"A4","id":"C_bg15","type":"precedence"}`
- `{"after":"A16","before":"A8","id":"C_extra24","type":"precedence"}`
- `{"activity_id":"A29","end":17,"id":"PREF16","start":13,"type":"preferred_start","weight":2}`
- `{"after":"A13","before":"A17","id":"C_bg7","type":"precedence"}`
- `{"after":"A14","before":"A2","id":"C_bg31","type":"precedence"}`
- `{"activity_id":"A2","end":27,"id":"PREF0","start":25,"type":"preferred_start","weight":2}`
- `{"after":"A8","before":"A13","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A5","end":22,"id":"PREF26","start":20,"type":"preferred_start","weight":3}`
- `{"after":"A31","before":"A11","id":"C_bg8","type":"precedence"}`
- `{"after":"A16","before":"A7","id":"C_bg24","type":"precedence"}`
- `{"after":"A26","before":"A2","id":"C_extra3","type":"precedence"}`
- `{"after":"A32","before":"A26","id":"C_bg22","type":"precedence"}`
- `{"activity_id":"A22","end":6,"id":"PREF4","start":2,"type":"preferred_start","weight":2}`
- `{"after":"A25","before":"A17","id":"C_extra12","type":"precedence"}`
- `{"after":"A4","before":"A17","id":"C_bg6","type":"precedence"}`
- `{"after":"A6","before":"A8","id":"C_bg10","type":"precedence"}`
- `{"activity_id":"A11","end":27,"id":"PREF2","start":21,"type":"preferred_start","weight":2}`
- `{"activity_id":"A3","end":16,"id":"PREF20","start":14,"type":"preferred_start","weight":2}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/c71fa5cedb9e6a9390462efd09a2c33dbdf6cc13d104288e15066bb2d84429d7.json`. SHA-256: `994a6b880fc64be40f505bba5b923651db0a08794c9cacc7490619f65e560c85`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/779419959ed3701328489d0de9be8f88b6fb8a0bdacdf5a4e06108647ed493c6.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/1de47036ad61d42d67197c0a82ee34b48a5c99442e55e0d831679e9dd021fead.json`. SHA-256: `19fdf18c74eafa6d5eb1bf5263804cb46e29b69cb550e7c667e60d3786fccf3e`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/779419959ed3701328489d0de9be8f88b6fb8a0bdacdf5a4e06108647ed493c6.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/bbc3fe4427828f7c069a09621ed0bba2e0e09babeafc5d8e83db43430c66138c.json`. SHA-256: `6d76de2b91cd806d9b1a52fcbd3ce4d9a97ca51c82c44c3f3b023adf786bf468`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/779419959ed3701328489d0de9be8f88b6fb8a0bdacdf5a4e06108647ed493c6.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/aa9c1f17c11e25e9c9f88ebaea322135def097d825da4e8d0d18d01ce44fb12b.json`. SHA-256: `22ad00afd61013644acf36b4adf6bc96bc422f5a7bbb6cf2f25cbcf3e1bbf592`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/779419959ed3701328489d0de9be8f88b6fb8a0bdacdf5a4e06108647ed493c6.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C10

**Participant crossing · 32 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 32 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,32) and has capacity one.
Participant P2 is available in [0,32) and has capacity one.
Participant P3 is available in [0,32) and has capacity one.
Participant P4 is available in [0,32) and has capacity one.
Participant P5 is available in [0,32) and has capacity one.
Participant P6 is available in [0,32) and has capacity one.
Participant P7 is available in [0,32) and has capacity one.
Participant P8 is available in [0,32) and has capacity one.
Resource R1 is available in [0,32) and has capacity one.
Resource R2 is available in [0,32) and has capacity one.
Resource R3 is available in [0,32) and has capacity one.
Activity A18 lasts 2 slots; participants: P8; resources: R3; availability: [0,9).
Activity A9 lasts 2 slots; participants: P3; resources: R1; availability: [3,13).
Activity A17 lasts 2 slots; participants: P5; resources: R2; availability: [0,8).
Activity A3 lasts 2 slots; participants: P7; resources: none; availability: [0,3), [6,12).
Activity A23 lasts 2 slots; participants: P6, P7; resources: none; availability: [8,15).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [0,2).
Activity A4 lasts 2 slots; participants: P8; resources: none; availability: [1,8).
Activity A5 lasts 2 slots; participants: P5; resources: none; availability: [6,16).
Activity A13 lasts 2 slots; participants: P6; resources: R3; availability: [0,8).
Activity A21 lasts 2 slots; participants: P6, P8; resources: none; availability: [8,18).
Activity A1 lasts 2 slots; participants: P3; resources: R1; availability: [4,10).
Activity A7 lasts 3 slots; participants: P1; resources: none; availability: [3,13).
Activity A16 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [9,20).
Activity A6 lasts 2 slots; participants: P4; resources: R2; availability: [5,13).
Activity A19 lasts 3 slots; participants: P2; resources: none; availability: [4,12).
Activity A12 lasts 2 slots; participants: P6; resources: none; availability: [0,14).
Activity A32 lasts 2 slots; participants: P6; resources: none; availability: [7,15).
Activity A28 lasts 3 slots; participants: P1; resources: R3; availability: [12,17).
Activity A8 lasts 3 slots; participants: P1; resources: none; availability: [2,14).
Activity A20 lasts 2 slots; participants: P8; resources: none; availability: [0,14).
Activity A14 lasts 2 slots; participants: P6; resources: none; availability: [0,7).
Activity A15 lasts 2 slots; participants: P4, P7; resources: R3; availability: [5,10).
Activity A24 lasts 2 slots; participants: P2; resources: R3; availability: [9,16).
Activity A22 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [5,11).
Activity A26 lasts 3 slots; participants: P4, P7; resources: R1; availability: [0,5).
Activity A27 lasts 3 slots; participants: P3; resources: R1; availability: [0,4), [6,14).
Activity A31 lasts 3 slots; participants: P5; resources: none; availability: [0,10).
Activity A25 lasts 2 slots; participants: P1; resources: none; availability: [2,12).
Activity A11 lasts 2 slots; participants: P1, P2; resources: none; availability: [0,4).
Activity A10 lasts 2 slots; participants: P2; resources: none; availability: [0,2).
Activity A29 lasts 2 slots; participants: P8; resources: R3; availability: [0,3), [8,12).
Activity A30 lasts 2 slots; participants: P5; resources: R2; availability: [3,15).
A22 must finish before or when A23 starts.
A25 must finish before or when A15 starts.
Starting A12 outside [18,24) incurs penalty 2; starting inside incurs zero.
A11 must finish before or when A25 starts.
A10 must finish before or when A18 starts.
A23 must finish before or when A28 starts.
A1 must finish before or when A23 starts.
Starting A32 outside [12,18) incurs penalty 1; starting inside incurs zero.
Starting A31 outside [16,22) incurs penalty 3; starting inside incurs zero.
A12 must finish before or when A3 starts.
A23 must finish before or when A21 starts.
A2 must finish before or when A21 starts.
Starting A25 outside [8,14) incurs penalty 1; starting inside incurs zero.
A11 must finish before or when A5 starts.
A2 must finish before or when A4 starts.
A26 must finish before or when A22 starts.
Starting A4 outside [20,24) incurs penalty 3; starting inside incurs zero.
A10 must finish before or when A26 starts.
A26 must finish before or when A9 starts.
Starting A30 outside [20,24) incurs penalty 1; starting inside incurs zero.
A15 must finish before or when A1 starts.
Starting A16 outside [12,16) incurs penalty 3; starting inside incurs zero.
A26 must finish before or when A12 starts.
Starting A6 outside [11,17) incurs penalty 1; starting inside incurs zero.
A31 must finish before or when A7 starts.
A17 must finish before or when A27 starts.
A11 must finish before or when A30 starts.
Starting A24 outside [2,4) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A8 starts.
A17 must finish before or when A19 starts.
Starting A27 outside [0,4) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A20 starts.
A2 must finish before or when A17 starts.
A20 must finish before or when A29 starts.
A9 must finish before or when A30 starts.
A8 must finish before or when A24 starts.
A32 must finish before or when A24 starts.
A4 must finish before or when A20 starts.
A8 must finish before or when A16 starts.
Starting A29 outside [13,17) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A13 starts.
A2 must finish before or when A14 starts.
Starting A2 outside [25,27) incurs penalty 2; starting inside incurs zero.
A13 must finish before or when A8 starts.
Starting A5 outside [20,22) incurs penalty 3; starting inside incurs zero.
A11 must finish before or when A31 starts.
A7 must finish before or when A16 starts.
A2 must finish before or when A26 starts.
A26 must finish before or when A32 starts.
Starting A22 outside [2,6) incurs penalty 2; starting inside incurs zero.
A17 must finish before or when A25 starts.
A17 must finish before or when A4 starts.
A8 must finish before or when A6 starts.
Starting A11 outside [21,27) incurs penalty 2; starting inside incurs zero.
Starting A3 outside [14,16) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-2781e8410ac2dcdbbb7d9e20`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 32 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 32) |
| P2 | [0, 32) |
| P3 | [0, 32) |
| P4 | [0, 32) |
| P5 | [0, 32) |
| P6 | [0, 32) |
| P7 | [0, 32) |
| P8 | [0, 32) |
| R1 | [0, 32) |
| R2 | [0, 32) |
| R3 | [0, 32) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A18 | 2 | P8 | R3 | [0, 9) |
| A9 | 2 | P3 | R1 | [3, 13) |
| A17 | 2 | P5 | R2 | [0, 8) |
| A3 | 2 | P7 | None | [0, 3), [6, 12) |
| A23 | 2 | P6, P7 | None | [8, 15) |
| A2 | 2 | P1 | None | [0, 2) |
| A4 | 2 | P8 | None | [1, 8) |
| A5 | 2 | P5 | None | [6, 16) |
| A13 | 2 | P6 | R3 | [0, 8) |
| A21 | 2 | P6, P8 | None | [8, 18) |
| A1 | 2 | P3 | R1 | [4, 10) |
| A7 | 3 | P1 | None | [3, 13) |
| A16 | 2 | P2 | R2 | [0, 3), [9, 20) |
| A6 | 2 | P4 | R2 | [5, 13) |
| A19 | 3 | P2 | None | [4, 12) |
| A12 | 2 | P6 | None | [0, 14) |
| A32 | 2 | P6 | None | [7, 15) |
| A28 | 3 | P1 | R3 | [12, 17) |
| A8 | 3 | P1 | None | [2, 14) |
| A20 | 2 | P8 | None | [0, 14) |
| A14 | 2 | P6 | None | [0, 7) |
| A15 | 2 | P4, P7 | R3 | [5, 10) |
| A24 | 2 | P2 | R3 | [9, 16) |
| A22 | 2 | P2 | R2 | [0, 3), [5, 11) |
| A26 | 3 | P4, P7 | R1 | [0, 5) |
| A27 | 3 | P3 | R1 | [0, 4), [6, 14) |
| A31 | 3 | P5 | None | [0, 10) |
| A25 | 2 | P1 | None | [2, 12) |
| A11 | 2 | P1, P2 | None | [0, 4) |
| A10 | 2 | P2 | None | [0, 2) |
| A29 | 2 | P8 | R3 | [0, 3), [8, 12) |
| A30 | 2 | P5 | R2 | [3, 15) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A23","before":"A22","id":"C_extra21","type":"precedence"}`
- `{"after":"A15","before":"A25","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A12","end":24,"id":"PREF14","start":18,"type":"preferred_start","weight":2}`
- `{"after":"A25","before":"A11","id":"C_bg12","type":"precedence"}`
- `{"after":"A18","before":"A10","id":"C_bg29","type":"precedence"}`
- `{"after":"A28","before":"A23","id":"C_bg25","type":"precedence"}`
- `{"after":"A23","before":"A1","id":"C_bg21","type":"precedence"}`
- `{"activity_id":"A32","end":18,"id":"PREF22","start":12,"type":"preferred_start","weight":1}`
- `{"activity_id":"A31","end":22,"id":"PREF8","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A12","id":"C_bg20","type":"precedence"}`
- `{"after":"A21","before":"A23","id":"C_bg27","type":"precedence"}`
- `{"after":"A21","before":"A2","id":"C_extra27","type":"precedence"}`
- `{"activity_id":"A25","end":14,"id":"PREF12","start":8,"type":"preferred_start","weight":1}`
- `{"after":"A5","before":"A11","id":"C_bg26","type":"precedence"}`
- `{"after":"A4","before":"A2","id":"C_extra6","type":"precedence"}`
- `{"after":"A22","before":"A26","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A4","end":24,"id":"PREF6","start":20,"type":"preferred_start","weight":3}`
- `{"after":"A26","before":"A10","id":"C_bg3","type":"precedence"}`
- `{"after":"A9","before":"A26","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A30","end":24,"id":"PREF18","start":20,"type":"preferred_start","weight":1}`
- `{"after":"A1","before":"A15","id":"C_bg17","type":"precedence"}`
- `{"activity_id":"A16","end":16,"id":"PREF24","start":12,"type":"preferred_start","weight":3}`
- `{"after":"A12","before":"A26","id":"C_bg14","type":"precedence"}`
- `{"activity_id":"A6","end":17,"id":"PREF10","start":11,"type":"preferred_start","weight":1}`
- `{"after":"A7","before":"A31","id":"C_bg23","type":"precedence"}`
- `{"after":"A27","before":"A17","id":"C_bg28","type":"precedence"}`
- `{"after":"A30","before":"A11","id":"C_bg18","type":"precedence"}`
- `{"activity_id":"A24","end":4,"id":"PREF30","start":2,"type":"preferred_start","weight":2}`
- `{"after":"A8","before":"A17","id":"C_extra9","type":"precedence"}`
- `{"after":"A19","before":"A17","id":"C_bg19","type":"precedence"}`
- `{"activity_id":"A27","end":4,"id":"PREF28","start":0,"type":"preferred_start","weight":3}`
- `{"after":"A20","before":"A2","id":"C_extra15","type":"precedence"}`
- `{"after":"A17","before":"A2","id":"C_bg5","type":"precedence"}`
- `{"after":"A29","before":"A20","id":"C_bg16","type":"precedence"}`
- `{"after":"A30","before":"A9","id":"C_extra18","type":"precedence"}`
- `{"after":"A24","before":"A8","id":"C_bg30","type":"precedence"}`
- `{"after":"A24","before":"A32","id":"C_extra30","type":"precedence"}`
- `{"after":"A20","before":"A4","id":"C_bg15","type":"precedence"}`
- `{"after":"A16","before":"A8","id":"C_extra24","type":"precedence"}`
- `{"activity_id":"A29","end":17,"id":"PREF16","start":13,"type":"preferred_start","weight":2}`
- `{"after":"A13","before":"A17","id":"C_bg7","type":"precedence"}`
- `{"after":"A14","before":"A2","id":"C_bg31","type":"precedence"}`
- `{"activity_id":"A2","end":27,"id":"PREF0","start":25,"type":"preferred_start","weight":2}`
- `{"after":"A8","before":"A13","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A5","end":22,"id":"PREF26","start":20,"type":"preferred_start","weight":3}`
- `{"after":"A31","before":"A11","id":"C_bg8","type":"precedence"}`
- `{"after":"A16","before":"A7","id":"C_bg24","type":"precedence"}`
- `{"after":"A26","before":"A2","id":"C_extra3","type":"precedence"}`
- `{"after":"A32","before":"A26","id":"C_bg22","type":"precedence"}`
- `{"activity_id":"A22","end":6,"id":"PREF4","start":2,"type":"preferred_start","weight":2}`
- `{"after":"A25","before":"A17","id":"C_extra12","type":"precedence"}`
- `{"after":"A4","before":"A17","id":"C_bg6","type":"precedence"}`
- `{"after":"A6","before":"A8","id":"C_bg10","type":"precedence"}`
- `{"activity_id":"A11","end":27,"id":"PREF2","start":21,"type":"preferred_start","weight":2}`
- `{"activity_id":"A3","end":16,"id":"PREF20","start":14,"type":"preferred_start","weight":2}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":27,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 8
  },
  {
    "activity_id": "A10",
    "start_slot": 0
  },
  {
    "activity_id": "A11",
    "start_slot": 2
  },
  {
    "activity_id": "A12",
    "start_slot": 6
  },
  {
    "activity_id": "A13",
    "start_slot": 4
  },
  {
    "activity_id": "A14",
    "start_slot": 2
  },
  {
    "activity_id": "A15",
    "start_slot": 6
  },
  {
    "activity_id": "A16",
    "start_slot": 13
  },
  {
    "activity_id": "A17",
    "start_slot": 2
  },
  {
    "activity_id": "A18",
    "start_slot": 2
  },
  {
    "activity_id": "A19",
    "start_slot": 7
  },
  {
    "activity_id": "A2",
    "start_slot": 0
  },
  {
    "activity_id": "A20",
    "start_slot": 6
  },
  {
    "activity_id": "A21",
    "start_slot": 12
  },
  {
    "activity_id": "A22",
    "start_slot": 5
  },
  {
    "activity_id": "A23",
    "start_slot": 10
  },
  {
    "activity_id": "A24",
    "start_slot": 10
  },
  {
    "activity_id": "A25",
    "start_slot": 4
  },
  {
    "activity_id": "A26",
    "start_slot": 2
  },
  {
    "activity_id": "A27",
    "start_slot": 10
  },
  {
    "activity_id": "A28",
    "start_slot": 13
  },
  {
    "activity_id": "A29",
    "start_slot": 8
  },
  {
    "activity_id": "A3",
    "start_slot": 8
  },
  {
    "activity_id": "A30",
    "start_slot": 7
  },
  {
    "activity_id": "A31",
    "start_slot": 4
  },
  {
    "activity_id": "A32",
    "start_slot": 8
  },
  {
    "activity_id": "A4",
    "start_slot": 4
  },
  {
    "activity_id": "A5",
    "start_slot": 9
  },
  {
    "activity_id": "A6",
    "start_slot": 11
  },
  {
    "activity_id": "A7",
    "start_slot": 10
  },
  {
    "activity_id": "A8",
    "start_slot": 6
  },
  {
    "activity_id": "A9",
    "start_slot": 5
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[27]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[27]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[27]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/a04c52e9b0f54c058948822543a9d107a06a687d5f78348994773cf8e6dee240.json`. SHA-256: `2e10a731607a4072c9c541aa7862e7c20f49d52236212807399bd17d4b0cb77d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/fceaef0bc2a8106f1476ae1ab4a93dc2bb63a5685f97cc1170338ef41d943104.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 8
    },
    {
      "activity_id": "A10",
      "start_slot": 0
    },
    {
      "activity_id": "A11",
      "start_slot": 2
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 4
    },
    {
      "activity_id": "A14",
      "start_slot": 2
    },
    {
      "activity_id": "A15",
      "start_slot": 6
    },
    {
      "activity_id": "A16",
      "start_slot": 13
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 6
    },
    {
      "activity_id": "A21",
      "start_slot": 12
    },
    {
      "activity_id": "A22",
      "start_slot": 5
    },
    {
      "activity_id": "A23",
      "start_slot": 10
    },
    {
      "activity_id": "A24",
      "start_slot": 10
    },
    {
      "activity_id": "A25",
      "start_slot": 4
    },
    {
      "activity_id": "A26",
      "start_slot": 2
    },
    {
      "activity_id": "A27",
      "start_slot": 10
    },
    {
      "activity_id": "A28",
      "start_slot": 13
    },
    {
      "activity_id": "A29",
      "start_slot": 8
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A30",
      "start_slot": 7
    },
    {
      "activity_id": "A31",
      "start_slot": 4
    },
    {
      "activity_id": "A32",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 4
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 11
    },
    {
      "activity_id": "A7",
      "start_slot": 10
    },
    {
      "activity_id": "A8",
      "start_slot": 6
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 27,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    27
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/072e4c87d1e3942dda6209d6b17952062420d461c7b0a8a46693ef28d75b836e.json`. SHA-256: `18c14de9ee09e9d0ead72f350bde93eb72b9c009937284855dcae425a3958d2b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/fceaef0bc2a8106f1476ae1ab4a93dc2bb63a5685f97cc1170338ef41d943104.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 8
    },
    {
      "activity_id": "A10",
      "start_slot": 0
    },
    {
      "activity_id": "A11",
      "start_slot": 2
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 4
    },
    {
      "activity_id": "A14",
      "start_slot": 2
    },
    {
      "activity_id": "A15",
      "start_slot": 6
    },
    {
      "activity_id": "A16",
      "start_slot": 14
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 6
    },
    {
      "activity_id": "A21",
      "start_slot": 14
    },
    {
      "activity_id": "A22",
      "start_slot": 5
    },
    {
      "activity_id": "A23",
      "start_slot": 10
    },
    {
      "activity_id": "A24",
      "start_slot": 10
    },
    {
      "activity_id": "A25",
      "start_slot": 4
    },
    {
      "activity_id": "A26",
      "start_slot": 2
    },
    {
      "activity_id": "A27",
      "start_slot": 10
    },
    {
      "activity_id": "A28",
      "start_slot": 12
    },
    {
      "activity_id": "A29",
      "start_slot": 8
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A30",
      "start_slot": 9
    },
    {
      "activity_id": "A31",
      "start_slot": 4
    },
    {
      "activity_id": "A32",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 4
    },
    {
      "activity_id": "A5",
      "start_slot": 7
    },
    {
      "activity_id": "A6",
      "start_slot": 11
    },
    {
      "activity_id": "A7",
      "start_slot": 9
    },
    {
      "activity_id": "A8",
      "start_slot": 6
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 27,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    27
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/2d077bd85596ed6396540f88a40a0384cf114560fc01725a713e78653b919caa.json`. SHA-256: `52512180f2839754f7e24abe8e7471d7830de95d3a118ad216f56c761dbddc34`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/fceaef0bc2a8106f1476ae1ab4a93dc2bb63a5685f97cc1170338ef41d943104.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 8
    },
    {
      "activity_id": "A10",
      "start_slot": 0
    },
    {
      "activity_id": "A11",
      "start_slot": 2
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 4
    },
    {
      "activity_id": "A14",
      "start_slot": 2
    },
    {
      "activity_id": "A15",
      "start_slot": 6
    },
    {
      "activity_id": "A16",
      "start_slot": 13
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 6
    },
    {
      "activity_id": "A21",
      "start_slot": 12
    },
    {
      "activity_id": "A22",
      "start_slot": 5
    },
    {
      "activity_id": "A23",
      "start_slot": 10
    },
    {
      "activity_id": "A24",
      "start_slot": 10
    },
    {
      "activity_id": "A25",
      "start_slot": 4
    },
    {
      "activity_id": "A26",
      "start_slot": 2
    },
    {
      "activity_id": "A27",
      "start_slot": 10
    },
    {
      "activity_id": "A28",
      "start_slot": 13
    },
    {
      "activity_id": "A29",
      "start_slot": 8
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A30",
      "start_slot": 7
    },
    {
      "activity_id": "A31",
      "start_slot": 4
    },
    {
      "activity_id": "A32",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 4
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 11
    },
    {
      "activity_id": "A7",
      "start_slot": 10
    },
    {
      "activity_id": "A8",
      "start_slot": 6
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 27,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    27
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/daed74f25c8635aeec2fea6646cf6f9f1b70be39dff04a8ae25a19ad6250c1b8.json`. SHA-256: `2e422802484d58e6bf191babf963b4f46c1fafa5c15ea3a069f96293a9970623`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/fceaef0bc2a8106f1476ae1ab4a93dc2bb63a5685f97cc1170338ef41d943104.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C11

**Precedence chain · 8 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,16) and has capacity one.
Activity A6 lasts 2 slots; participants: P1; resources: R1; availability: [6,9).
Activity A1 lasts 2 slots; participants: P1; resources: none; availability: [0,10).
Activity A8 lasts 2 slots; participants: P1; resources: R1; availability: [0,6).
Activity A7 lasts 2 slots; participants: P2; resources: none; availability: [0,10).
Activity A5 lasts 2 slots; participants: P2; resources: R1; availability: [4,9).
Activity A2 lasts 3 slots; participants: P2; resources: R1; availability: [0,4), [8,13).
Activity A3 lasts 3 slots; participants: P2; resources: none; availability: [0,10).
Activity A4 lasts 2 slots; participants: P1; resources: none; availability: [0,10).
A4 must finish before or when A8 starts.
Starting A8 outside [4,10) incurs penalty 1; starting inside incurs zero.
Starting A3 outside [11,13) incurs penalty 3; starting inside incurs zero.
A8 must finish before or when A5 starts.
A3 must finish before or when A1 starts.
A6 must finish at or before slot 9.
Starting A6 outside [10,12) incurs penalty 2; starting inside incurs zero.
Starting A7 outside [4,6) incurs penalty 2; starting inside incurs zero.
A8 must finish before or when A6 starts.
A4 must finish before or when A3 starts.
A1 must finish before or when A7 starts.
A7 must finish before or when A2 starts.
A7 must finish at or before slot 8.
A3 must finish before or when A5 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-03a09ff7b635071f5da4e226`. Gold label: **UNSAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 16) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A6 | 2 | P1 | R1 | [6, 9) |
| A1 | 2 | P1 | None | [0, 10) |
| A8 | 2 | P1 | R1 | [0, 6) |
| A7 | 2 | P2 | None | [0, 10) |
| A5 | 2 | P2 | R1 | [4, 9) |
| A2 | 3 | P2 | R1 | [0, 4), [8, 13) |
| A3 | 3 | P2 | None | [0, 10) |
| A4 | 2 | P1 | None | [0, 10) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A8","before":"A4","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A8","end":10,"id":"PREF5","start":4,"type":"preferred_start","weight":1}`
- `{"activity_id":"A3","end":13,"id":"PREF1","start":11,"type":"preferred_start","weight":3}`
- `{"after":"A5","before":"A8","id":"C_extra6","type":"precedence"}`
- `{"after":"A1","before":"A3","id":"C1","type":"precedence"}`
- `{"activity_id":"A6","id":"C_profile_deadline","slot":9,"type":"deadline"}`
- `{"activity_id":"A6","end":12,"id":"PREF7","start":10,"type":"preferred_start","weight":2}`
- `{"activity_id":"A7","end":6,"id":"PREF3","start":4,"type":"preferred_start","weight":2}`
- `{"after":"A6","before":"A8","id":"C_bg7","type":"precedence"}`
- `{"after":"A3","before":"A4","id":"C0","type":"precedence"}`
- `{"after":"A7","before":"A1","id":"C2","type":"precedence"}`
- `{"after":"A2","before":"A7","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A7","id":"C_end","slot":8,"type":"deadline"}`
- `{"after":"A5","before":"A3","id":"C_bg6","type":"precedence"}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | INVALID_OUTPUT | invalid_output | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer failed the required output/schema contract."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/a7894eb847694a657759a73f1d169cc99c7553855c9f87114a26f31559914c17.json`. SHA-256: `3845d2142cf5dbe59f8810a057d02c0d9a8889c50b45aeac9c81aeeb4ab5c813`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d7e6419cd623b9e1ccec72ef017ca50f344015cbe0ae987a1c2646deddbc427b.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": {
          "activity_id": "A8",
          "slot": 9,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 1,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 0,
    "structurally_equivalent": false
  },
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4f59af9ffe384ccb880a419fd002d326e7f893930d4014a4a855ff442924a06c.json`. SHA-256: `4809759dab372baf9bb206f8d24dad54401a84ff7af689272dd4b1df10a2ae68`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d7e6419cd623b9e1ccec72ef017ca50f344015cbe0ae987a1c2646deddbc427b.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/7621d7a4cb9d403b0490e5f40ad993c09f3c68e2a0863ac3d5f99f5e951e1c66.json`. SHA-256: `2d6dbf324334317228dd89d2ae3e6f273af7e320a4b80e0bd979d39a975ab741`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d7e6419cd623b9e1ccec72ef017ca50f344015cbe0ae987a1c2646deddbc427b.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/8d4e0a71b7092721aa774103f4e3bc139b629234705a778ddff66a3591baa980.json`. SHA-256: `a76ca04d808c141bed0b4e93dee35c367eb52e31b500c106e29ceb27e7bba1b4`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d7e6419cd623b9e1ccec72ef017ca50f344015cbe0ae987a1c2646deddbc427b.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C12

**Precedence chain · 8 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,16) and has capacity one.
Activity A3 lasts 2 slots; participants: P2; resources: R1; availability: [9,13).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [8,12).
Activity A5 lasts 3 slots; participants: P2; resources: none; availability: [0,11).
Activity A4 lasts 2 slots; participants: P1; resources: R1; availability: [0,4).
Activity A7 lasts 2 slots; participants: P2; resources: R1; availability: [4,9).
Activity A8 lasts 2 slots; participants: P1; resources: none; availability: [0,11).
Activity A6 lasts 2 slots; participants: P1; resources: none; availability: [0,11).
Activity A1 lasts 3 slots; participants: P2; resources: none; availability: [0,11).
A7 must start exactly at slot 5.
A5 must finish before or when A7 starts.
Starting A1 outside [11,13) incurs penalty 1; starting inside incurs zero.
A5 must finish before or when A8 starts.
A1 must finish before or when A3 starts.
A1 must finish before or when A2 starts.
Starting A3 outside [3,7) incurs penalty 1; starting inside incurs zero.
A8 must finish before or when A1 starts.
Starting A2 outside [7,9) incurs penalty 3; starting inside incurs zero.
A1 must finish at or before slot 10.
A6 must finish before or when A4 starts.
A6 must finish before or when A5 starts.
Starting A5 outside [9,11) incurs penalty 1; starting inside incurs zero.
A3 must finish at or before slot 12.
A6 must finish before or when A7 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-072dea3c1469fea21496558d`. Gold label: **SAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 16) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A3 | 2 | P2 | R1 | [9, 13) |
| A2 | 2 | P1 | None | [8, 12) |
| A5 | 3 | P2 | None | [0, 11) |
| A4 | 2 | P1 | R1 | [0, 4) |
| A7 | 2 | P2 | R1 | [4, 9) |
| A8 | 2 | P1 | None | [0, 11) |
| A6 | 2 | P1 | None | [0, 11) |
| A1 | 3 | P2 | None | [0, 11) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A7","id":"C_profile_fixed","slot":5,"type":"fixed_start"}`
- `{"after":"A7","before":"A5","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A1","end":13,"id":"PREF3","start":11,"type":"preferred_start","weight":1}`
- `{"after":"A8","before":"A5","id":"C1","type":"precedence"}`
- `{"after":"A3","before":"A1","id":"C_bg7","type":"precedence"}`
- `{"after":"A2","before":"A1","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A3","end":7,"id":"PREF7","start":3,"type":"preferred_start","weight":1}`
- `{"after":"A1","before":"A8","id":"C2","type":"precedence"}`
- `{"activity_id":"A2","end":9,"id":"PREF5","start":7,"type":"preferred_start","weight":3}`
- `{"activity_id":"A1","id":"C_end","slot":10,"type":"deadline"}`
- `{"after":"A4","before":"A6","id":"C_bg4","type":"precedence"}`
- `{"after":"A5","before":"A6","id":"C0","type":"precedence"}`
- `{"activity_id":"A5","end":11,"id":"PREF1","start":9,"type":"preferred_start","weight":1}`
- `{"activity_id":"A3","id":"C_profile_deadline","slot":12,"type":"deadline"}`
- `{"after":"A7","before":"A6","id":"C_bg6","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":6,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 7
  },
  {
    "activity_id": "A2",
    "start_slot": 10
  },
  {
    "activity_id": "A3",
    "start_slot": 10
  },
  {
    "activity_id": "A4",
    "start_slot": 2
  },
  {
    "activity_id": "A5",
    "start_slot": 2
  },
  {
    "activity_id": "A6",
    "start_slot": 0
  },
  {
    "activity_id": "A7",
    "start_slot": 5
  },
  {
    "activity_id": "A8",
    "start_slot": 5
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[6]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[6]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[6]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4fcf6b770971e5f43fe6d164f4b731a5a9c179c842ec9db916d538f7a4c2cf33.json`. SHA-256: `f8887e345206524077e3c3392bdbdd6f20729f108b821d0a21293556d301f622`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/941325bba37e39e602758564eba68cce3dd1b4883a0a6a19120f87bfee39f316.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 10
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 5
    },
    {
      "activity_id": "A8",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    6
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/cffb27ed393f06941115c16e92b701ff49e2ba8508017dfb7436011656ddd1b6.json`. SHA-256: `3c66862cf683d33048aacb8fe665c9e15e9ff2cd5de0e65ab1e2eef1504b1e83`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/941325bba37e39e602758564eba68cce3dd1b4883a0a6a19120f87bfee39f316.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 10
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 5
    },
    {
      "activity_id": "A8",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    6
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/2418b6b20fe7ea5d369772bbdf4011aeaeb4e8636d7f90e5a967f5a14c8811ed.json`. SHA-256: `6c945e08e46aea2f8670a677bba40347dc0ada3fedb94396467ffa416e9affab`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/941325bba37e39e602758564eba68cce3dd1b4883a0a6a19120f87bfee39f316.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 10
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 5
    },
    {
      "activity_id": "A8",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    6
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/97dc55f0c13d4b6c48f18223f615933b8d112070a2afc660ad1d8f10593a82ac.json`. SHA-256: `18921d60f6bb59c9b9beccdd8efecdb67e7bd51b98bb14775d801abede9ab65d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/941325bba37e39e602758564eba68cce3dd1b4883a0a6a19120f87bfee39f316.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C13

**Precedence fork join · 12 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 20 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,20) and has capacity one.
Participant P2 is available in [0,20) and has capacity one.
Participant P3 is available in [0,20) and has capacity one.
Resource R1 is available in [0,20) and has capacity one.
Activity A12 lasts 2 slots; participants: P2; resources: none; availability: [0,9).
Activity A1 lasts 2 slots; participants: P3; resources: R1; availability: [14,17).
Activity A2 lasts 3 slots; participants: P3; resources: none; availability: [3,9).
Activity A7 lasts 2 slots; participants: P2; resources: none; availability: [0,3), [9,16).
Activity A4 lasts 2 slots; participants: P2; resources: none; availability: [8,12).
Activity A10 lasts 2 slots; participants: P3; resources: R1; availability: [8,13).
Activity A3 lasts 2 slots; participants: P2; resources: R1; availability: [2,9).
Activity A8 lasts 2 slots; participants: P3; resources: R1; availability: [0,3), [5,10).
Activity A6 lasts 2 slots; participants: P1; resources: none; availability: [0,9).
Activity A5 lasts 3 slots; participants: P1; resources: none; availability: [0,9).
Activity A9 lasts 3 slots; participants: P1; resources: none; availability: [0,9).
Activity A11 lasts 2 slots; participants: P1; resources: none; availability: [7,10).
A9 must finish at or before slot 7.
A7 must finish before or when A1 starts.
A12 must finish before or when A9 starts.
Starting A8 outside [0,4) incurs penalty 3; starting inside incurs zero.
A8 must finish before or when A4 starts.
Starting A3 outside [12,16) incurs penalty 1; starting inside incurs zero.
A6 must finish before or when A2 starts.
Starting A1 outside [4,8) incurs penalty 1; starting inside incurs zero.
Starting A5 outside [0,4) incurs penalty 1; starting inside incurs zero.
A5 must finish before or when A12 starts.
A5 must finish before or when A6 starts.
A9 must finish before or when A11 starts.
A9 must finish before or when A8 starts.
A6 must finish before or when A9 starts.
A5 must finish before or when A2 starts.
A6 must finish before or when A3 starts.
Starting A7 outside [7,11) incurs penalty 2; starting inside incurs zero.
Starting A12 outside [12,16) incurs penalty 1; starting inside incurs zero.
A4 must finish before or when A7 starts.
A8 must finish before or when A10 starts.
A12 must finish before or when A3 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-02211f1d803e51e17858c0fe`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 20 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 20) |
| P2 | [0, 20) |
| P3 | [0, 20) |
| R1 | [0, 20) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A12 | 2 | P2 | None | [0, 9) |
| A1 | 2 | P3 | R1 | [14, 17) |
| A2 | 3 | P3 | None | [3, 9) |
| A7 | 2 | P2 | None | [0, 3), [9, 16) |
| A4 | 2 | P2 | None | [8, 12) |
| A10 | 2 | P3 | R1 | [8, 13) |
| A3 | 2 | P2 | R1 | [2, 9) |
| A8 | 2 | P3 | R1 | [0, 3), [5, 10) |
| A6 | 2 | P1 | None | [0, 9) |
| A5 | 3 | P1 | None | [0, 9) |
| A9 | 3 | P1 | None | [0, 9) |
| A11 | 2 | P1 | None | [7, 10) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A9","id":"C_end","slot":7,"type":"deadline"}`
- `{"after":"A1","before":"A7","id":"C_bg10","type":"precedence"}`
- `{"after":"A9","before":"A12","id":"C3","type":"precedence"}`
- `{"activity_id":"A8","end":4,"id":"PREF4","start":0,"type":"preferred_start","weight":3}`
- `{"after":"A4","before":"A8","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A3","end":16,"id":"PREF6","start":12,"type":"preferred_start","weight":1}`
- `{"after":"A2","before":"A6","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A1","end":8,"id":"PREF10","start":4,"type":"preferred_start","weight":1}`
- `{"activity_id":"A5","end":4,"id":"PREF0","start":0,"type":"preferred_start","weight":1}`
- `{"after":"A12","before":"A5","id":"C1","type":"precedence"}`
- `{"after":"A6","before":"A5","id":"C0","type":"precedence"}`
- `{"after":"A11","before":"A9","id":"C_bg5","type":"precedence"}`
- `{"after":"A8","before":"A9","id":"C_bg4","type":"precedence"}`
- `{"after":"A9","before":"A6","id":"C2","type":"precedence"}`
- `{"after":"A2","before":"A5","id":"C_extra9","type":"precedence"}`
- `{"after":"A3","before":"A6","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A7","end":11,"id":"PREF8","start":7,"type":"preferred_start","weight":2}`
- `{"activity_id":"A12","end":16,"id":"PREF2","start":12,"type":"preferred_start","weight":1}`
- `{"after":"A7","before":"A4","id":"C_bg8","type":"precedence"}`
- `{"after":"A10","before":"A8","id":"C_bg11","type":"precedence"}`
- `{"after":"A3","before":"A12","id":"C_extra6","type":"precedence"}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | ERROR | provider_error | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The provider attempt failed; this is not evidence of a reasoning failure."
  ],
  "provider_error": "http_502"
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/5c314bcd44136255c74092ce0919eed5592816eff2bc54541ed7c74f4dc46a22.json`. SHA-256: `cc250ee1f33b5aee32082e60276c4173977af8ca4d499c2dd4eb82756d32a2c0`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/645d53a159052d4bee2231a737bf7e29333b30c3303b1adaf68053ce897fbe02.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/083c554b83a93bb72b85cea5b5db7396e53c9f455695e31401d5677e695e1897.json`. SHA-256: `d8606eff044c05e67b98359e6f88db02edceac76f97e88a6ea64f702a29ad288`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/645d53a159052d4bee2231a737bf7e29333b30c3303b1adaf68053ce897fbe02.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/ce45fab9e20f114d87fa8823bdef99f300db26633496738fca8409db20ab5461.json`. SHA-256: `00bd2a5d0ed1f60f6767271056cc07b06dda9e545620017745fb501ebf5beae5`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/645d53a159052d4bee2231a737bf7e29333b30c3303b1adaf68053ce897fbe02.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/d7e0e0ee6463f0c7d4d8487031191e8c2edf50557819b00c1d516f71f03f99c3.json`. SHA-256: `46f17e44720bef574d20352893da1ce8fe3244ebea116c53852ac204582a5738`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/645d53a159052d4bee2231a737bf7e29333b30c3303b1adaf68053ce897fbe02.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C14

**Precedence fork join · 12 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 20 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,20) and has capacity one.
Participant P2 is available in [0,20) and has capacity one.
Participant P3 is available in [0,20) and has capacity one.
Resource R1 is available in [0,20) and has capacity one.
Activity A10 lasts 3 slots; participants: P1; resources: none; availability: [0,8).
Activity A1 lasts 2 slots; participants: P1; resources: none; availability: [9,12).
Activity A9 lasts 2 slots; participants: P1; resources: none; availability: [0,8).
Activity A2 lasts 2 slots; participants: P3; resources: R1; availability: [10,15).
Activity A11 lasts 2 slots; participants: P2; resources: none; availability: [4,10).
Activity A3 lasts 2 slots; participants: P3; resources: R1; availability: [0,4).
Activity A12 lasts 2 slots; participants: P1; resources: none; availability: [0,8).
Activity A4 lasts 3 slots; participants: P3; resources: R1; availability: [4,11).
Activity A8 lasts 3 slots; participants: P2; resources: none; availability: [0,4), [5,13).
Activity A5 lasts 2 slots; participants: P3; resources: R1; availability: [7,11).
Activity A6 lasts 3 slots; participants: P2; resources: none; availability: [0,8).
Activity A7 lasts 2 slots; participants: P1; resources: none; availability: [4,11).
A12 must finish before or when A10 starts.
A2 must finish at or before slot 12.
A6 must finish before or when A9 starts.
A12 must finish before or when A2 starts.
A6 must finish before or when A8 starts.
A6 must finish before or when A5 starts.
A10 must finish before or when A7 starts.
A4 must finish before or when A5 starts.
A12 must finish before or when A7 starts.
Starting A2 outside [9,15) incurs penalty 3; starting inside incurs zero.
A10 must finish before or when A9 starts.
A10 must finish before or when A11 starts.
A12 must finish before or when A3 starts.
A10 must finish before or when A4 starts.
Starting A5 outside [13,19) incurs penalty 2; starting inside incurs zero.
A10 must finish before or when A1 starts.
Starting A3 outside [8,14) incurs penalty 2; starting inside incurs zero.
A9 must finish at or before slot 7.
Starting A11 outside [10,12) incurs penalty 1; starting inside incurs zero.
A12 must finish before or when A6 starts.
Starting A10 outside [8,12) incurs penalty 1; starting inside incurs zero.
Starting A9 outside [6,12) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-5637a6027e00c6a45c2a2581`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 20 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 20) |
| P2 | [0, 20) |
| P3 | [0, 20) |
| R1 | [0, 20) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A10 | 3 | P1 | None | [0, 8) |
| A1 | 2 | P1 | None | [9, 12) |
| A9 | 2 | P1 | None | [0, 8) |
| A2 | 2 | P3 | R1 | [10, 15) |
| A11 | 2 | P2 | None | [4, 10) |
| A3 | 2 | P3 | R1 | [0, 4) |
| A12 | 2 | P1 | None | [0, 8) |
| A4 | 3 | P3 | R1 | [4, 11) |
| A8 | 3 | P2 | None | [0, 4), [5, 13) |
| A5 | 2 | P3 | R1 | [7, 11) |
| A6 | 3 | P2 | None | [0, 8) |
| A7 | 2 | P1 | None | [4, 11) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A10","before":"A12","id":"C0","type":"precedence"}`
- `{"activity_id":"A2","id":"C_profile_deadline","slot":12,"type":"deadline"}`
- `{"after":"A9","before":"A6","id":"C3","type":"precedence"}`
- `{"after":"A2","before":"A12","id":"C_bg11","type":"precedence"}`
- `{"after":"A8","before":"A6","id":"C_bg8","type":"precedence"}`
- `{"after":"A5","before":"A6","id":"C_extra9","type":"precedence"}`
- `{"after":"A7","before":"A10","id":"C_bg6","type":"precedence"}`
- `{"after":"A5","before":"A4","id":"C_bg9","type":"precedence"}`
- `{"after":"A7","before":"A12","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A2","end":15,"id":"PREF11","start":9,"type":"preferred_start","weight":3}`
- `{"after":"A9","before":"A10","id":"C2","type":"precedence"}`
- `{"after":"A11","before":"A10","id":"C_bg5","type":"precedence"}`
- `{"after":"A3","before":"A12","id":"C_bg7","type":"precedence"}`
- `{"after":"A4","before":"A10","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A5","end":19,"id":"PREF9","start":13,"type":"preferred_start","weight":2}`
- `{"after":"A1","before":"A10","id":"C_bg10","type":"precedence"}`
- `{"activity_id":"A3","end":14,"id":"PREF7","start":8,"type":"preferred_start","weight":2}`
- `{"activity_id":"A9","id":"C_end","slot":7,"type":"deadline"}`
- `{"activity_id":"A11","end":12,"id":"PREF5","start":10,"type":"preferred_start","weight":1}`
- `{"after":"A6","before":"A12","id":"C1","type":"precedence"}`
- `{"activity_id":"A10","end":12,"id":"PREF1","start":8,"type":"preferred_start","weight":1}`
- `{"activity_id":"A9","end":12,"id":"PREF3","start":6,"type":"preferred_start","weight":2}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":8,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 10
  },
  {
    "activity_id": "A10",
    "start_slot": 2
  },
  {
    "activity_id": "A11",
    "start_slot": 5
  },
  {
    "activity_id": "A12",
    "start_slot": 0
  },
  {
    "activity_id": "A2",
    "start_slot": 10
  },
  {
    "activity_id": "A3",
    "start_slot": 2
  },
  {
    "activity_id": "A4",
    "start_slot": 5
  },
  {
    "activity_id": "A5",
    "start_slot": 8
  },
  {
    "activity_id": "A6",
    "start_slot": 2
  },
  {
    "activity_id": "A7",
    "start_slot": 7
  },
  {
    "activity_id": "A8",
    "start_slot": 7
  },
  {
    "activity_id": "A9",
    "start_slot": 5
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[8]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[8]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[8]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/39251fa7472924fa119c3a7493cd5b70877263785671c8ab564561bc158ddeb2.json`. SHA-256: `056cb3fe70d56b40962877dbf915dad1d2da7719101b541d187f08e900f4ca4e`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/f2324cafb45c9236ba313acce19f6cecec02b2f095331de2c598c8a82ee68808.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 5
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 5
    },
    {
      "activity_id": "A5",
      "start_slot": 8
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 7
    },
    {
      "activity_id": "A8",
      "start_slot": 7
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    8
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/dc22971294e3aab2a4caeb33a4e92f190b0fad1e8ba9af9cd5d02df577056336.json`. SHA-256: `692fc9601207172a01b5f701b5cd666323503e671ac958f679606b57f26b72af`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/f2324cafb45c9236ba313acce19f6cecec02b2f095331de2c598c8a82ee68808.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 5
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 5
    },
    {
      "activity_id": "A5",
      "start_slot": 8
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 7
    },
    {
      "activity_id": "A8",
      "start_slot": 7
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    8
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/7ba8f45d842656c598e07d51264628917c6316e3b21e5343a732a73164adc6b1.json`. SHA-256: `85bddd9107f4aea6687ec5752c2505f3309dde37b381ad646c1e932e2b5906a9`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/f2324cafb45c9236ba313acce19f6cecec02b2f095331de2c598c8a82ee68808.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 10
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 5
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A2",
      "start_slot": 10
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 5
    },
    {
      "activity_id": "A5",
      "start_slot": 8
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 7
    },
    {
      "activity_id": "A8",
      "start_slot": 7
    },
    {
      "activity_id": "A9",
      "start_slot": 5
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    8
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/477dad46894cb2666353734b6570811b36676d52d9a9688886569de51edc00a8.json`. SHA-256: `df717289bb73796171fb2a80b07c02580e66806afd98164e9f43560754ec05b2`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/f2324cafb45c9236ba313acce19f6cecec02b2f095331de2c598c8a82ee68808.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C15

**Release deadline chain · 16 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 24 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,24) and has capacity one.
Participant P2 is available in [0,24) and has capacity one.
Participant P3 is available in [0,24) and has capacity one.
Participant P4 is available in [0,24) and has capacity one.
Resource R1 is available in [0,24) and has capacity one.
Resource R2 is available in [0,24) and has capacity one.
Activity A16 lasts 2 slots; participants: P4; resources: R2; availability: [10,15).
Activity A1 lasts 2 slots; participants: P1, P4; resources: R2; availability: [0,3), [8,11).
Activity A7 lasts 2 slots; participants: P3; resources: R2; availability: [4,9).
Activity A12 lasts 2 slots; participants: P3; resources: R1; availability: [0,3), [5,11).
Activity A4 lasts 3 slots; participants: P1; resources: R2; availability: [13,17).
Activity A9 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [4,12).
Activity A5 lasts 2 slots; participants: P3; resources: R1; availability: [10,17).
Activity A14 lasts 3 slots; participants: P3; resources: none; availability: [11,14).
Activity A13 lasts 3 slots; participants: P1, P4; resources: R1; availability: [3,7).
Activity A2 lasts 3 slots; participants: P2; resources: none; availability: [2,13).
Activity A10 lasts 3 slots; participants: P1; resources: R1; availability: [8,18).
Activity A3 lasts 3 slots; participants: P2; resources: none; availability: [8,19).
Activity A11 lasts 2 slots; participants: P3, P4; resources: R1; availability: [6,9).
Activity A15 lasts 3 slots; participants: P2; resources: none; availability: [2,13).
Activity A8 lasts 2 slots; participants: P1; resources: none; availability: [2,13).
Activity A6 lasts 2 slots; participants: P1; resources: none; availability: [2,13).
A8 must finish before or when A2 starts.
Starting A13 outside [0,4) incurs penalty 2; starting inside incurs zero.
A11 must finish before or when A16 starts.
A15 must finish at or before slot 7.
A8 must finish before or when A1 starts.
A15 must finish before or when A8 starts.
A8 must finish before or when A10 starts.
A6 must finish before or when A15 starts.
A15 must finish before or when A11 starts.
A15 must finish before or when A9 starts.
A14 must finish before or when A5 starts.
Starting A15 outside [10,16) incurs penalty 2; starting inside incurs zero.
Starting A11 outside [14,20) incurs penalty 3; starting inside incurs zero.
A7 must finish before or when A3 starts.
A2 must finish before or when A16 starts.
A6 must finish before or when A13 starts.
A3 must start exactly at slot 12.
A15 must finish before or when A4 starts.
A6 must finish before or when A7 starts.
A11 must finish before or when A12 starts.
A4 must finish at or before slot 17.
Starting A10 outside [3,7) incurs penalty 2; starting inside incurs zero.
A7 must finish before or when A4 starts.
A6 must start at or after slot 2.
A13 must finish before or when A14 starts.
Starting A14 outside [8,10) incurs penalty 3; starting inside incurs zero.
A2 must finish at or before slot 11.
Starting A2 outside [14,16) incurs penalty 3; starting inside incurs zero.
Starting A5 outside [16,18) incurs penalty 2; starting inside incurs zero.
A13 must finish before or when A9 starts.
A11 must finish before or when A14 starts.
Starting A4 outside [6,10) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-034077d49082a8ca4b142bdc`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 24 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 24) |
| P2 | [0, 24) |
| P3 | [0, 24) |
| P4 | [0, 24) |
| R1 | [0, 24) |
| R2 | [0, 24) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A16 | 2 | P4 | R2 | [10, 15) |
| A1 | 2 | P1, P4 | R2 | [0, 3), [8, 11) |
| A7 | 2 | P3 | R2 | [4, 9) |
| A12 | 2 | P3 | R1 | [0, 3), [5, 11) |
| A4 | 3 | P1 | R2 | [13, 17) |
| A9 | 2 | P2 | R2 | [0, 3), [4, 12) |
| A5 | 2 | P3 | R1 | [10, 17) |
| A14 | 3 | P3 | None | [11, 14) |
| A13 | 3 | P1, P4 | R1 | [3, 7) |
| A2 | 3 | P2 | None | [2, 13) |
| A10 | 3 | P1 | R1 | [8, 18) |
| A3 | 3 | P2 | None | [8, 19) |
| A11 | 2 | P3, P4 | R1 | [6, 9) |
| A15 | 3 | P2 | None | [2, 13) |
| A8 | 2 | P1 | None | [2, 13) |
| A6 | 2 | P1 | None | [2, 13) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A2","before":"A8","id":"C2","type":"precedence"}`
- `{"activity_id":"A13","end":4,"id":"PREF7","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A16","before":"A11","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A15","id":"C_mid","slot":7,"type":"deadline"}`
- `{"after":"A1","before":"A8","id":"C_bg4","type":"precedence"}`
- `{"after":"A8","before":"A15","id":"C1","type":"precedence"}`
- `{"after":"A10","before":"A8","id":"C_bg13","type":"precedence"}`
- `{"after":"A15","before":"A6","id":"C0","type":"precedence"}`
- `{"after":"A11","before":"A15","id":"C_bg5","type":"precedence"}`
- `{"after":"A9","before":"A15","id":"C_extra12","type":"precedence"}`
- `{"after":"A5","before":"A14","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A15","end":16,"id":"PREF1","start":10,"type":"preferred_start","weight":2}`
- `{"activity_id":"A11","end":20,"id":"PREF5","start":14,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A7","id":"C_bg14","type":"precedence"}`
- `{"after":"A16","before":"A2","id":"C_bg6","type":"precedence"}`
- `{"after":"A13","before":"A6","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A3","id":"C_profile_fixed","slot":12,"type":"fixed_start"}`
- `{"after":"A4","before":"A15","id":"C_bg15","type":"precedence"}`
- `{"after":"A7","before":"A6","id":"C_bg10","type":"precedence"}`
- `{"after":"A12","before":"A11","id":"C_bg8","type":"precedence"}`
- `{"activity_id":"A4","id":"C_profile_deadline","slot":17,"type":"deadline"}`
- `{"activity_id":"A10","end":7,"id":"PREF13","start":3,"type":"preferred_start","weight":2}`
- `{"after":"A4","before":"A7","id":"C_extra15","type":"precedence"}`
- `{"activity_id":"A6","id":"C_release","slot":2,"type":"release"}`
- `{"after":"A14","before":"A13","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A14","end":10,"id":"PREF9","start":8,"type":"preferred_start","weight":3}`
- `{"activity_id":"A2","id":"C_end","slot":11,"type":"deadline"}`
- `{"activity_id":"A2","end":16,"id":"PREF3","start":14,"type":"preferred_start","weight":3}`
- `{"activity_id":"A5","end":18,"id":"PREF11","start":16,"type":"preferred_start","weight":2}`
- `{"after":"A9","before":"A13","id":"C_bg12","type":"precedence"}`
- `{"after":"A14","before":"A11","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A4","end":10,"id":"PREF15","start":6,"type":"preferred_start","weight":2}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/58cd87649431a79a18c8459428886e01a3925d8673f719fd13e649472d704594.json`. SHA-256: `be0266b7a60013dd1a07c5ec1fe7875bf3f2a835ad7b29ad3e2df59c038f96a7`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/15c1ddf69c9ea808356a8deccdb22b035724d96ec4ff82579fa5ea8555ebcda6.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": null,
        "count": 1,
        "expected": {
          "after": "A12",
          "before": "A11",
          "type": "precedence"
        },
        "kind": "omitted"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 1,
    "structurally_equivalent": false
  },
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/fdfd403779d3298d626704f6efc9fb641bdacab7464dd881d5c1612ad4638a3f.json`. SHA-256: `8c5210ae906ea0d6b2f95c9c647a51143ec3720ae29582ab326a8f85429cb492`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/15c1ddf69c9ea808356a8deccdb22b035724d96ec4ff82579fa5ea8555ebcda6.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/b7d54c7da5bc55a9e63dd685d6e60656740386ce9c01e611639a3aa0975346f3.json`. SHA-256: `a06c6b4d9a68b4edd6ff8e376abf4323d547485c06094f134a67e0488d38193b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/15c1ddf69c9ea808356a8deccdb22b035724d96ec4ff82579fa5ea8555ebcda6.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/de97a05aa9a1623ea69566bea224c58771ce8e1bbe3085c820742d7bb696113b.json`. SHA-256: `9eebac091b4e3a7767cb647ccdbefbcf87d1dbf67509e55a4398b0c5b9c61a0d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/15c1ddf69c9ea808356a8deccdb22b035724d96ec4ff82579fa5ea8555ebcda6.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C16

**Release deadline chain · 16 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 24 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,24) and has capacity one.
Participant P2 is available in [0,24) and has capacity one.
Participant P3 is available in [0,24) and has capacity one.
Participant P4 is available in [0,24) and has capacity one.
Resource R1 is available in [0,24) and has capacity one.
Resource R2 is available in [0,24) and has capacity one.
Activity A3 lasts 2 slots; participants: P1, P3; resources: R2; availability: [9,17).
Activity A13 lasts 2 slots; participants: P3; resources: R2; availability: [15,21).
Activity A9 lasts 2 slots; participants: P3, P4; resources: R2; availability: [0,3), [6,10).
Activity A8 lasts 2 slots; participants: P1, P4; resources: R1; availability: [14,20).
Activity A5 lasts 2 slots; participants: P1; resources: none; availability: [2,13).
Activity A1 lasts 2 slots; participants: P4; resources: none; availability: [0,3), [12,16).
Activity A7 lasts 3 slots; participants: P1; resources: none; availability: [2,13).
Activity A14 lasts 3 slots; participants: P2; resources: R1; availability: [11,18).
Activity A4 lasts 3 slots; participants: P2; resources: none; availability: [2,13).
Activity A2 lasts 2 slots; participants: P1, P3; resources: R2; availability: [8,17).
Activity A11 lasts 2 slots; participants: P2; resources: R1; availability: [13,21).
Activity A6 lasts 2 slots; participants: P4; resources: R1; availability: [7,11).
Activity A12 lasts 2 slots; participants: P2; resources: none; availability: [2,13).
Activity A10 lasts 2 slots; participants: P1, P3; resources: none; availability: [7,14).
Activity A16 lasts 2 slots; participants: P2; resources: R1; availability: [2,8).
Activity A15 lasts 2 slots; participants: P4; resources: none; availability: [0,3), [8,14).
A9 must finish before or when A15 starts.
Starting A9 outside [12,16) incurs penalty 3; starting inside incurs zero.
A6 must finish before or when A2 starts.
A2 must finish before or when A8 starts.
A5 must finish before or when A2 starts.
Starting A1 outside [8,10) incurs penalty 2; starting inside incurs zero.
A13 must finish before or when A11 starts.
Starting A13 outside [16,22) incurs penalty 2; starting inside incurs zero.
A16 must finish before or when A10 starts.
A12 must finish at or before slot 6.
A5 must finish before or when A12 starts.
A1 must finish before or when A11 starts.
A7 must finish before or when A10 starts.
A12 must finish before or when A9 starts.
A5 must finish before or when A14 starts.
A7 must finish before or when A4 starts.
Starting A7 outside [16,22) incurs penalty 1; starting inside incurs zero.
Starting A14 outside [19,23) incurs penalty 1; starting inside incurs zero.
A16 must finish before or when A1 starts.
A7 must finish before or when A6 starts.
A12 must finish before or when A13 starts.
Starting A5 outside [2,8) incurs penalty 3; starting inside incurs zero.
A12 must finish before or when A16 starts.
A2 must finish before or when A1 starts.
A12 must finish before or when A7 starts.
A4 must finish at or before slot 12.
Starting A15 outside [16,20) incurs penalty 2; starting inside incurs zero.
A5 must start at or after slot 2.
Starting A10 outside [3,9) incurs penalty 1; starting inside incurs zero.
A10 must finish before or when A3 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-15cbe326f87fa8d55043752d`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 24 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 24) |
| P2 | [0, 24) |
| P3 | [0, 24) |
| P4 | [0, 24) |
| R1 | [0, 24) |
| R2 | [0, 24) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A3 | 2 | P1, P3 | R2 | [9, 17) |
| A13 | 2 | P3 | R2 | [15, 21) |
| A9 | 2 | P3, P4 | R2 | [0, 3), [6, 10) |
| A8 | 2 | P1, P4 | R1 | [14, 20) |
| A5 | 2 | P1 | None | [2, 13) |
| A1 | 2 | P4 | None | [0, 3), [12, 16) |
| A7 | 3 | P1 | None | [2, 13) |
| A14 | 3 | P2 | R1 | [11, 18) |
| A4 | 3 | P2 | None | [2, 13) |
| A2 | 2 | P1, P3 | R2 | [8, 17) |
| A11 | 2 | P2 | R1 | [13, 21) |
| A6 | 2 | P4 | R1 | [7, 11) |
| A12 | 2 | P2 | None | [2, 13) |
| A10 | 2 | P1, P3 | None | [7, 14) |
| A16 | 2 | P2 | R1 | [2, 8) |
| A15 | 2 | P4 | None | [0, 3), [8, 14) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A15","before":"A9","id":"C_bg8","type":"precedence"}`
- `{"activity_id":"A9","end":16,"id":"PREF4","start":12,"type":"preferred_start","weight":3}`
- `{"after":"A2","before":"A6","id":"C_bg9","type":"precedence"}`
- `{"after":"A8","before":"A2","id":"C_bg13","type":"precedence"}`
- `{"after":"A2","before":"A5","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A1","end":10,"id":"PREF12","start":8,"type":"preferred_start","weight":2}`
- `{"after":"A11","before":"A13","id":"C_bg15","type":"precedence"}`
- `{"activity_id":"A13","end":22,"id":"PREF14","start":16,"type":"preferred_start","weight":2}`
- `{"after":"A10","before":"A16","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A12","id":"C_mid","slot":6,"type":"deadline"}`
- `{"after":"A12","before":"A5","id":"C0","type":"precedence"}`
- `{"after":"A11","before":"A1","id":"C_extra15","type":"precedence"}`
- `{"after":"A10","before":"A7","id":"C_bg6","type":"precedence"}`
- `{"after":"A9","before":"A12","id":"C_bg4","type":"precedence"}`
- `{"after":"A14","before":"A5","id":"C_bg10","type":"precedence"}`
- `{"after":"A4","before":"A7","id":"C2","type":"precedence"}`
- `{"activity_id":"A7","end":22,"id":"PREF2","start":16,"type":"preferred_start","weight":1}`
- `{"activity_id":"A14","end":23,"id":"PREF10","start":19,"type":"preferred_start","weight":1}`
- `{"after":"A1","before":"A16","id":"C_extra12","type":"precedence"}`
- `{"after":"A6","before":"A7","id":"C_bg7","type":"precedence"}`
- `{"after":"A13","before":"A12","id":"C_bg14","type":"precedence"}`
- `{"activity_id":"A5","end":8,"id":"PREF0","start":2,"type":"preferred_start","weight":3}`
- `{"after":"A16","before":"A12","id":"C_bg5","type":"precedence"}`
- `{"after":"A1","before":"A2","id":"C_bg12","type":"precedence"}`
- `{"after":"A7","before":"A12","id":"C1","type":"precedence"}`
- `{"activity_id":"A4","id":"C_end","slot":12,"type":"deadline"}`
- `{"activity_id":"A15","end":20,"id":"PREF8","start":16,"type":"preferred_start","weight":2}`
- `{"activity_id":"A5","id":"C_release","slot":2,"type":"release"}`
- `{"activity_id":"A10","end":9,"id":"PREF6","start":3,"type":"preferred_start","weight":1}`
- `{"after":"A3","before":"A10","id":"C_bg11","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":10,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 14
  },
  {
    "activity_id": "A10",
    "start_slot": 9
  },
  {
    "activity_id": "A11",
    "start_slot": 18
  },
  {
    "activity_id": "A12",
    "start_slot": 4
  },
  {
    "activity_id": "A13",
    "start_slot": 16
  },
  {
    "activity_id": "A14",
    "start_slot": 12
  },
  {
    "activity_id": "A15",
    "start_slot": 11
  },
  {
    "activity_id": "A16",
    "start_slot": 6
  },
  {
    "activity_id": "A2",
    "start_slot": 11
  },
  {
    "activity_id": "A3",
    "start_slot": 13
  },
  {
    "activity_id": "A4",
    "start_slot": 9
  },
  {
    "activity_id": "A5",
    "start_slot": 2
  },
  {
    "activity_id": "A6",
    "start_slot": 9
  },
  {
    "activity_id": "A7",
    "start_slot": 6
  },
  {
    "activity_id": "A8",
    "start_slot": 16
  },
  {
    "activity_id": "A9",
    "start_slot": 6
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[10]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[10]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4edd0b6839032fc3f8e25d04f7622509126430774940bb501427303e5903ef6e.json`. SHA-256: `aeb53776384561f6a93f0302d1fb3ed6f4dd9037129a091c25b1016e3c3a71fa`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/16856e21f5a89df12da3b22f5f584b0e712a19c58eb9fdcb82defff9542d5bf7.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 9
    },
    {
      "activity_id": "A11",
      "start_slot": 18
    },
    {
      "activity_id": "A12",
      "start_slot": 4
    },
    {
      "activity_id": "A13",
      "start_slot": 16
    },
    {
      "activity_id": "A14",
      "start_slot": 12
    },
    {
      "activity_id": "A15",
      "start_slot": 11
    },
    {
      "activity_id": "A16",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 11
    },
    {
      "activity_id": "A3",
      "start_slot": 13
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 16
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/e43ae03022f439ab32c1577a74cfda32f53f38e33f2f8b9d32e167c2204b9f6c.json`. SHA-256: `521cfd15b848ad1c70d40bc9f299fadb33330b73548db77ffa5b08aa8d870939`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/16856e21f5a89df12da3b22f5f584b0e712a19c58eb9fdcb82defff9542d5bf7.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 10
    },
    {
      "activity_id": "A11",
      "start_slot": 18
    },
    {
      "activity_id": "A12",
      "start_slot": 4
    },
    {
      "activity_id": "A13",
      "start_slot": 16
    },
    {
      "activity_id": "A14",
      "start_slot": 12
    },
    {
      "activity_id": "A15",
      "start_slot": 11
    },
    {
      "activity_id": "A16",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 12
    },
    {
      "activity_id": "A3",
      "start_slot": 14
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 16
    },
    {
      "activity_id": "A9",
      "start_slot": 7
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/8b3dfaea03683b470b0e12fae4c1dcc0823f55042cd0ca962639751c6bf2383b.json`. SHA-256: `0cb4f1407240ff249087f2b1183e2f6f5e3b37388b228b2b708f8727b6a1f2f3`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/16856e21f5a89df12da3b22f5f584b0e712a19c58eb9fdcb82defff9542d5bf7.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 9
    },
    {
      "activity_id": "A11",
      "start_slot": 18
    },
    {
      "activity_id": "A12",
      "start_slot": 4
    },
    {
      "activity_id": "A13",
      "start_slot": 16
    },
    {
      "activity_id": "A14",
      "start_slot": 12
    },
    {
      "activity_id": "A15",
      "start_slot": 11
    },
    {
      "activity_id": "A16",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 11
    },
    {
      "activity_id": "A3",
      "start_slot": 13
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 16
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 10,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    10
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/63e9665ecbdacefaaee18002d34a813255a4d31455348cac1549494a1a9ed818.json`. SHA-256: `c29b6c3c3400460be53f7e1465837bb5c7b9b70401a829b76e13a6b8713dd364`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/16856e21f5a89df12da3b22f5f584b0e712a19c58eb9fdcb82defff9542d5bf7.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C17

**Resource person crossing · 24 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 28 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,28) and has capacity one.
Participant P2 is available in [0,28) and has capacity one.
Participant P3 is available in [0,28) and has capacity one.
Participant P4 is available in [0,28) and has capacity one.
Participant P5 is available in [0,28) and has capacity one.
Participant P6 is available in [0,28) and has capacity one.
Resource R1 is available in [0,28) and has capacity one.
Resource R2 is available in [0,28) and has capacity one.
Activity A18 lasts 3 slots; participants: P2; resources: R1; availability: [3,6).
Activity A9 lasts 2 slots; participants: P1; resources: none; availability: [3,13).
Activity A3 lasts 2 slots; participants: P4; resources: none; availability: [11,14).
Activity A10 lasts 3 slots; participants: P2; resources: R1; availability: [2,12).
Activity A13 lasts 3 slots; participants: P6; resources: none; availability: [8,16).
Activity A20 lasts 2 slots; participants: P4; resources: none; availability: [7,13).
Activity A24 lasts 2 slots; participants: P3, P6; resources: none; availability: [4,11).
Activity A5 lasts 2 slots; participants: P4; resources: none; availability: [2,7).
Activity A17 lasts 2 slots; participants: P6; resources: none; availability: [5,9).
Activity A7 lasts 2 slots; participants: P1; resources: none; availability: [0,3), [10,16).
Activity A6 lasts 3 slots; participants: P5; resources: none; availability: [7,15).
Activity A23 lasts 2 slots; participants: P2; resources: R1; availability: [5,13).
Activity A8 lasts 2 slots; participants: P2; resources: none; availability: [7,13).
Activity A16 lasts 2 slots; participants: P3, P6; resources: R1; availability: [10,20).
Activity A22 lasts 3 slots; participants: P5; resources: R2; availability: [4,12).
Activity A12 lasts 2 slots; participants: P1, P4; resources: none; availability: [8,12).
Activity A14 lasts 2 slots; participants: P6; resources: none; availability: [0,7).
Activity A2 lasts 3 slots; participants: P1; resources: R1; availability: [0,6).
Activity A19 lasts 2 slots; participants: P3; resources: R2; availability: [0,10).
Activity A15 lasts 2 slots; participants: P3; resources: none; availability: [0,3), [5,8).
Activity A4 lasts 2 slots; participants: P4; resources: none; availability: [0,9).
Activity A1 lasts 3 slots; participants: P1; resources: none; availability: [0,3).
Activity A21 lasts 3 slots; participants: P2, P5; resources: none; availability: [3,7).
Activity A11 lasts 3 slots; participants: P3; resources: R2; availability: [0,4), [7,16).
Starting A20 outside [2,6) incurs penalty 1; starting inside incurs zero.
Starting A6 outside [9,15) incurs penalty 1; starting inside incurs zero.
Starting A21 outside [4,8) incurs penalty 2; starting inside incurs zero.
A5 must finish before or when A13 starts.
A18 must finish before or when A20 starts.
A24 must finish before or when A11 starts.
A18 must finish before or when A21 starts.
A18 must finish before or when A19 starts.
Starting A4 outside [3,5) incurs penalty 1; starting inside incurs zero.
A2 must finish before or when A17 starts.
A15 must finish before or when A12 starts.
A10 must finish before or when A23 starts.
Starting A3 outside [8,14) incurs penalty 1; starting inside incurs zero.
A1 must finish before or when A13 starts.
A1 must finish before or when A4 starts.
A16 must start exactly at slot 13.
A1 must finish before or when A20 starts.
A8 must finish before or when A16 starts.
A18 must finish before or when A22 starts.
A18 must finish before or when A12 starts.
A14 must finish before or when A5 starts.
A22 must finish before or when A6 starts.
A3 must finish at or before slot 14.
Starting A12 outside [11,17) incurs penalty 3; starting inside incurs zero.
Starting A19 outside [23,25) incurs penalty 2; starting inside incurs zero.
A1 must finish before or when A7 starts.
A17 must finish before or when A3 starts.
A2 must finish before or when A15 starts.
A23 must finish before or when A8 starts.
Starting A17 outside [2,4) incurs penalty 2; starting inside incurs zero.
A2 must finish before or when A22 starts.
A4 must finish before or when A9 starts.
Starting A8 outside [10,16) incurs penalty 3; starting inside incurs zero.
A1 must finish before or when A14 starts.
A15 must finish before or when A24 starts.
A21 must finish before or when A10 starts.
A4 must finish before or when A5 starts.
A18 must finish before or when A4 starts.
Starting A23 outside [1,7) incurs penalty 3; starting inside incurs zero.
Starting A18 outside [22,24) incurs penalty 1; starting inside incurs zero.
A1 must finish before or when A19 starts.
Starting A9 outside [4,8) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-09a1950909e5a30f386bfcbd`. Gold label: **UNSAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 28 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 28) |
| P2 | [0, 28) |
| P3 | [0, 28) |
| P4 | [0, 28) |
| P5 | [0, 28) |
| P6 | [0, 28) |
| R1 | [0, 28) |
| R2 | [0, 28) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A18 | 3 | P2 | R1 | [3, 6) |
| A9 | 2 | P1 | None | [3, 13) |
| A3 | 2 | P4 | None | [11, 14) |
| A10 | 3 | P2 | R1 | [2, 12) |
| A13 | 3 | P6 | None | [8, 16) |
| A20 | 2 | P4 | None | [7, 13) |
| A24 | 2 | P3, P6 | None | [4, 11) |
| A5 | 2 | P4 | None | [2, 7) |
| A17 | 2 | P6 | None | [5, 9) |
| A7 | 2 | P1 | None | [0, 3), [10, 16) |
| A6 | 3 | P5 | None | [7, 15) |
| A23 | 2 | P2 | R1 | [5, 13) |
| A8 | 2 | P2 | None | [7, 13) |
| A16 | 2 | P3, P6 | R1 | [10, 20) |
| A22 | 3 | P5 | R2 | [4, 12) |
| A12 | 2 | P1, P4 | None | [8, 12) |
| A14 | 2 | P6 | None | [0, 7) |
| A2 | 3 | P1 | R1 | [0, 6) |
| A19 | 2 | P3 | R2 | [0, 10) |
| A15 | 2 | P3 | None | [0, 3), [5, 8) |
| A4 | 2 | P4 | None | [0, 9) |
| A1 | 3 | P1 | None | [0, 3) |
| A21 | 3 | P2, P5 | None | [3, 7) |
| A11 | 3 | P3 | R2 | [0, 4), [7, 16) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A20","end":6,"id":"PREF21","start":2,"type":"preferred_start","weight":1}`
- `{"activity_id":"A6","end":15,"id":"PREF17","start":9,"type":"preferred_start","weight":1}`
- `{"activity_id":"A21","end":8,"id":"PREF7","start":4,"type":"preferred_start","weight":2}`
- `{"after":"A13","before":"A5","id":"C_extra18","type":"precedence"}`
- `{"after":"A20","before":"A18","id":"C_bg21","type":"precedence"}`
- `{"after":"A11","before":"A24","id":"C_bg16","type":"precedence"}`
- `{"after":"A21","before":"A18","id":"C_bg7","type":"precedence"}`
- `{"after":"A19","before":"A18","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A4","end":5,"id":"PREF3","start":3,"type":"preferred_start","weight":1}`
- `{"after":"A17","before":"A2","id":"C_bg5","type":"precedence"}`
- `{"after":"A12","before":"A15","id":"C_bg15","type":"precedence"}`
- `{"after":"A23","before":"A10","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A3","end":14,"id":"PREF23","start":8,"type":"preferred_start","weight":1}`
- `{"after":"A13","before":"A1","id":"C_bg18","type":"precedence"}`
- `{"after":"A4","before":"A1","id":"C_extra3","type":"precedence"}`
- `{"activity_id":"A16","id":"C_profile_fixed","slot":13,"type":"fixed_start"}`
- `{"after":"A20","before":"A1","id":"C_extra21","type":"precedence"}`
- `{"after":"A16","before":"A8","id":"C_bg22","type":"precedence"}`
- `{"after":"A22","before":"A18","id":"C_extra6","type":"precedence"}`
- `{"after":"A12","before":"A18","id":"C_extra15","type":"precedence"}`
- `{"after":"A5","before":"A14","id":"C_bg12","type":"precedence"}`
- `{"after":"A6","before":"A22","id":"C_bg17","type":"precedence"}`
- `{"activity_id":"A3","id":"C_profile_deadline","slot":14,"type":"deadline"}`
- `{"activity_id":"A12","end":17,"id":"PREF15","start":11,"type":"preferred_start","weight":3}`
- `{"activity_id":"A19","end":25,"id":"PREF9","start":23,"type":"preferred_start","weight":2}`
- `{"after":"A7","before":"A1","id":"C_bg20","type":"precedence"}`
- `{"after":"A3","before":"A17","id":"C_bg23","type":"precedence"}`
- `{"after":"A15","before":"A2","id":"C_bg4","type":"precedence"}`
- `{"after":"A8","before":"A23","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A17","end":4,"id":"PREF5","start":2,"type":"preferred_start","weight":2}`
- `{"after":"A22","before":"A2","id":"C_bg6","type":"precedence"}`
- `{"after":"A9","before":"A4","id":"C_bg19","type":"precedence"}`
- `{"activity_id":"A8","end":16,"id":"PREF13","start":10,"type":"preferred_start","weight":3}`
- `{"after":"A14","before":"A1","id":"C_bg8","type":"precedence"}`
- `{"after":"A24","before":"A15","id":"C_bg14","type":"precedence"}`
- `{"after":"A10","before":"A21","id":"C_bg10","type":"precedence"}`
- `{"after":"A5","before":"A4","id":"C_extra12","type":"precedence"}`
- `{"after":"A4","before":"A18","id":"C_bg3","type":"precedence"}`
- `{"activity_id":"A23","end":7,"id":"PREF11","start":1,"type":"preferred_start","weight":3}`
- `{"activity_id":"A18","end":24,"id":"PREF1","start":22,"type":"preferred_start","weight":1}`
- `{"after":"A19","before":"A1","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A9","end":8,"id":"PREF19","start":4,"type":"preferred_start","weight":1}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/f81ddd1d603e70640dd3198c51e1bb132e3dd72e1b3f4e31dabf499168faed1b.json`. SHA-256: `2ae39275eaf31856f42e429a22296f316cc2be07ea71a24b36fcbbc285cf0959`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ad36123e1bfe2a8605e6b98d2ab8841370d0f09a5cd1ecf3dd2705e5fd8a67c.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/e2c700f3cf37d2ed40984ca3fc688200152053287a260d99f49f41cafd9f4730.json`. SHA-256: `209930da24260485a83ee7205d50ee730d5989a6c6d89258f761fac09bb741be`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ad36123e1bfe2a8605e6b98d2ab8841370d0f09a5cd1ecf3dd2705e5fd8a67c.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/fadfc3043c656d273f645b5391857e1a4aac89440d7213e6708230901859d498.json`. SHA-256: `16c15807539f5a1ce8733bc40b6012068e6ee912d6a0cce7a8f584318cb6ea2d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ad36123e1bfe2a8605e6b98d2ab8841370d0f09a5cd1ecf3dd2705e5fd8a67c.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/5c5db5c2996a0b451eea6d46f8f1badaaf6d040d32303d5224cdb1786199b532.json`. SHA-256: `362237823b83236d24cbd4e3ff6947d99dbe0cad414ea4aa4cd6ea0a3aa686c1`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/3ad36123e1bfe2a8605e6b98d2ab8841370d0f09a5cd1ecf3dd2705e5fd8a67c.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C18

**Resource person crossing · 24 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 28 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,28) and has capacity one.
Participant P2 is available in [0,28) and has capacity one.
Participant P3 is available in [0,28) and has capacity one.
Participant P4 is available in [0,28) and has capacity one.
Participant P5 is available in [0,28) and has capacity one.
Participant P6 is available in [0,28) and has capacity one.
Resource R1 is available in [0,28) and has capacity one.
Resource R2 is available in [0,28) and has capacity one.
Activity A21 lasts 2 slots; participants: P6; resources: none; availability: [7,13).
Activity A18 lasts 2 slots; participants: P1; resources: R1; availability: [0,4).
Activity A7 lasts 2 slots; participants: P1; resources: R1; availability: [0,10).
Activity A13 lasts 2 slots; participants: P5; resources: none; availability: [7,9).
Activity A5 lasts 2 slots; participants: P6; resources: none; availability: [0,3), [6,16).
Activity A22 lasts 2 slots; participants: P2, P6; resources: R2; availability: [10,19).
Activity A1 lasts 2 slots; participants: P2; resources: R1; availability: [0,2).
Activity A4 lasts 3 slots; participants: P2, P5; resources: none; availability: [0,4), [6,13).
Activity A17 lasts 2 slots; participants: P3, P6; resources: none; availability: [0,6).
Activity A10 lasts 3 slots; participants: P4; resources: none; availability: [0,9).
Activity A20 lasts 3 slots; participants: P5; resources: none; availability: [0,9).
Activity A9 lasts 3 slots; participants: P3, P4; resources: none; availability: [3,10).
Activity A12 lasts 2 slots; participants: P4; resources: R2; availability: [7,15).
Activity A11 lasts 2 slots; participants: P2, P6; resources: R2; availability: [5,13).
Activity A6 lasts 2 slots; participants: P2; resources: none; availability: [0,6).
Activity A15 lasts 2 slots; participants: P3, P6; resources: R2; availability: [0,5).
Activity A3 lasts 2 slots; participants: P3; resources: R1; availability: [6,13).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [0,2).
Activity A16 lasts 2 slots; participants: P2; resources: R2; availability: [1,7).
Activity A19 lasts 2 slots; participants: P1; resources: R1; availability: [6,13).
Activity A8 lasts 2 slots; participants: P4; resources: R2; availability: [6,17).
Activity A23 lasts 2 slots; participants: P1; resources: none; availability: [11,17).
Activity A14 lasts 2 slots; participants: P1, P3; resources: R1; availability: [0,3), [5,16).
Activity A24 lasts 2 slots; participants: P5; resources: none; availability: [2,9).
Starting A20 outside [4,6) incurs penalty 3; starting inside incurs zero.
A6 must finish before or when A20 starts.
A1 must finish before or when A15 starts.
A10 must finish before or when A16 starts.
Starting A1 outside [21,25) incurs penalty 1; starting inside incurs zero.
A2 must finish before or when A10 starts.
A6 must finish before or when A19 starts.
A15 must finish before or when A7 starts.
A1 must finish before or when A24 starts.
A9 must finish before or when A21 starts.
A19 must finish before or when A4 starts.
A14 must finish before or when A8 starts.
A11 must finish before or when A14 starts.
A1 must finish before or when A17 starts.
Starting A23 outside [3,5) incurs penalty 2; starting inside incurs zero.
Starting A8 outside [16,18) incurs penalty 3; starting inside incurs zero.
A15 must finish before or when A13 starts.
A11 must finish before or when A5 starts.
A18 must finish before or when A21 starts.
A19 must finish before or when A12 starts.
A15 must finish before or when A23 starts.
Starting A11 outside [13,15) incurs penalty 3; starting inside incurs zero.
Starting A6 outside [9,15) incurs penalty 1; starting inside incurs zero.
A9 must finish before or when A14 starts.
A8 must finish before or when A22 starts.
A1 must finish before or when A10 starts.
A17 must finish before or when A9 starts.
A7 must finish before or when A12 starts.
A2 must finish before or when A13 starts.
A23 must finish at or before slot 13.
A16 must finish before or when A11 starts.
A14 must finish before or when A3 starts.
Starting A16 outside [23,27) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A9 starts.
Starting A9 outside [13,15) incurs penalty 3; starting inside incurs zero.
Starting A3 outside [11,13) incurs penalty 1; starting inside incurs zero.
A6 must finish before or when A17 starts.
Starting A10 outside [21,27) incurs penalty 2; starting inside incurs zero.
Starting A13 outside [1,7) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A6 starts.
Starting A21 outside [13,15) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-0d56371f3693977d89cb1520`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 28 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 28) |
| P2 | [0, 28) |
| P3 | [0, 28) |
| P4 | [0, 28) |
| P5 | [0, 28) |
| P6 | [0, 28) |
| R1 | [0, 28) |
| R2 | [0, 28) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A21 | 2 | P6 | None | [7, 13) |
| A18 | 2 | P1 | R1 | [0, 4) |
| A7 | 2 | P1 | R1 | [0, 10) |
| A13 | 2 | P5 | None | [7, 9) |
| A5 | 2 | P6 | None | [0, 3), [6, 16) |
| A22 | 2 | P2, P6 | R2 | [10, 19) |
| A1 | 2 | P2 | R1 | [0, 2) |
| A4 | 3 | P2, P5 | None | [0, 4), [6, 13) |
| A17 | 2 | P3, P6 | None | [0, 6) |
| A10 | 3 | P4 | None | [0, 9) |
| A20 | 3 | P5 | None | [0, 9) |
| A9 | 3 | P3, P4 | None | [3, 10) |
| A12 | 2 | P4 | R2 | [7, 15) |
| A11 | 2 | P2, P6 | R2 | [5, 13) |
| A6 | 2 | P2 | None | [0, 6) |
| A15 | 2 | P3, P6 | R2 | [0, 5) |
| A3 | 2 | P3 | R1 | [6, 13) |
| A2 | 2 | P1 | None | [0, 2) |
| A16 | 2 | P2 | R2 | [1, 7) |
| A19 | 2 | P1 | R1 | [6, 13) |
| A8 | 2 | P4 | R2 | [6, 17) |
| A23 | 2 | P1 | None | [11, 17) |
| A14 | 2 | P1, P3 | R1 | [0, 3), [5, 16) |
| A24 | 2 | P5 | None | [2, 9) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A20","end":6,"id":"PREF13","start":4,"type":"preferred_start","weight":3}`
- `{"after":"A20","before":"A6","id":"C_bg13","type":"precedence"}`
- `{"after":"A15","before":"A1","id":"C_bg4","type":"precedence"}`
- `{"after":"A16","before":"A10","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A1","end":25,"id":"PREF1","start":21,"type":"preferred_start","weight":1}`
- `{"after":"A10","before":"A2","id":"C_bg3","type":"precedence"}`
- `{"after":"A19","before":"A6","id":"C_bg14","type":"precedence"}`
- `{"after":"A7","before":"A15","id":"C_bg8","type":"precedence"}`
- `{"after":"A24","before":"A1","id":"C_bg10","type":"precedence"}`
- `{"after":"A21","before":"A9","id":"C_bg21","type":"precedence"}`
- `{"after":"A4","before":"A19","id":"C_bg16","type":"precedence"}`
- `{"after":"A8","before":"A14","id":"C_bg17","type":"precedence"}`
- `{"after":"A14","before":"A11","id":"C_bg12","type":"precedence"}`
- `{"after":"A17","before":"A1","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A23","end":5,"id":"PREF23","start":3,"type":"preferred_start","weight":2}`
- `{"activity_id":"A8","end":18,"id":"PREF17","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A13","before":"A15","id":"C_extra15","type":"precedence"}`
- `{"after":"A5","before":"A11","id":"C_bg20","type":"precedence"}`
- `{"after":"A21","before":"A18","id":"C_extra21","type":"precedence"}`
- `{"after":"A12","before":"A19","id":"C_bg18","type":"precedence"}`
- `{"after":"A23","before":"A15","id":"C_bg23","type":"precedence"}`
- `{"activity_id":"A11","end":15,"id":"PREF11","start":13,"type":"preferred_start","weight":3}`
- `{"activity_id":"A6","end":15,"id":"PREF5","start":9,"type":"preferred_start","weight":1}`
- `{"after":"A14","before":"A9","id":"C_extra12","type":"precedence"}`
- `{"after":"A22","before":"A8","id":"C_bg22","type":"precedence"}`
- `{"after":"A10","before":"A1","id":"C_extra3","type":"precedence"}`
- `{"after":"A9","before":"A17","id":"C_bg9","type":"precedence"}`
- `{"after":"A12","before":"A7","id":"C_extra18","type":"precedence"}`
- `{"after":"A13","before":"A2","id":"C_bg15","type":"precedence"}`
- `{"activity_id":"A23","id":"C_profile_deadline","slot":13,"type":"deadline"}`
- `{"after":"A11","before":"A16","id":"C_bg11","type":"precedence"}`
- `{"after":"A3","before":"A14","id":"C_bg19","type":"precedence"}`
- `{"activity_id":"A16","end":27,"id":"PREF7","start":23,"type":"preferred_start","weight":3}`
- `{"after":"A9","before":"A2","id":"C_extra9","type":"precedence"}`
- `{"activity_id":"A9","end":15,"id":"PREF9","start":13,"type":"preferred_start","weight":3}`
- `{"activity_id":"A3","end":13,"id":"PREF19","start":11,"type":"preferred_start","weight":1}`
- `{"after":"A17","before":"A6","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A10","end":27,"id":"PREF3","start":21,"type":"preferred_start","weight":2}`
- `{"activity_id":"A13","end":7,"id":"PREF15","start":1,"type":"preferred_start","weight":3}`
- `{"after":"A6","before":"A2","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A21","end":15,"id":"PREF21","start":13,"type":"preferred_start","weight":1}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":22,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 0
  },
  {
    "activity_id": "A10",
    "start_slot": 2
  },
  {
    "activity_id": "A11",
    "start_slot": 7
  },
  {
    "activity_id": "A12",
    "start_slot": 9
  },
  {
    "activity_id": "A13",
    "start_slot": 7
  },
  {
    "activity_id": "A14",
    "start_slot": 9
  },
  {
    "activity_id": "A15",
    "start_slot": 2
  },
  {
    "activity_id": "A16",
    "start_slot": 5
  },
  {
    "activity_id": "A17",
    "start_slot": 4
  },
  {
    "activity_id": "A18",
    "start_slot": 2
  },
  {
    "activity_id": "A19",
    "start_slot": 6
  },
  {
    "activity_id": "A2",
    "start_slot": 0
  },
  {
    "activity_id": "A20",
    "start_slot": 4
  },
  {
    "activity_id": "A21",
    "start_slot": 9
  },
  {
    "activity_id": "A22",
    "start_slot": 13
  },
  {
    "activity_id": "A23",
    "start_slot": 11
  },
  {
    "activity_id": "A24",
    "start_slot": 2
  },
  {
    "activity_id": "A3",
    "start_slot": 11
  },
  {
    "activity_id": "A4",
    "start_slot": 9
  },
  {
    "activity_id": "A5",
    "start_slot": 11
  },
  {
    "activity_id": "A6",
    "start_slot": 2
  },
  {
    "activity_id": "A7",
    "start_slot": 4
  },
  {
    "activity_id": "A8",
    "start_slot": 11
  },
  {
    "activity_id": "A9",
    "start_slot": 6
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[22]` |
| GLM5.3 Flash | Direct | No | SAT | gold_invalid_schedule | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[22]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/504e590a44b87af121c037b963c392632ee2283c118052933ade1d6a36c5bf39.json`. SHA-256: `964b5ce48992ac9a0468678114f9ed1a069d408c7bd4e8ae6dcaf0921128c445`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/bb18aa0ca5f398d2bc721df6f48a4ff7c15bceea160a559e9c5bf9585999961f.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 0
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 7
    },
    {
      "activity_id": "A12",
      "start_slot": 9
    },
    {
      "activity_id": "A13",
      "start_slot": 7
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 5
    },
    {
      "activity_id": "A17",
      "start_slot": 4
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 4
    },
    {
      "activity_id": "A21",
      "start_slot": 9
    },
    {
      "activity_id": "A22",
      "start_slot": 13
    },
    {
      "activity_id": "A23",
      "start_slot": 11
    },
    {
      "activity_id": "A24",
      "start_slot": 2
    },
    {
      "activity_id": "A3",
      "start_slot": 11
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 11
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 22,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    22
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/b7313d3f6e4edcf08f1246dec57aeba49524d6551ea2a7eb9157b5fd2446ea29.json`. SHA-256: `551541ac17a1196bd53b9a34f7cb6f9249e4a630b829e109d0e7c5e29facc70a`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/bb18aa0ca5f398d2bc721df6f48a4ff7c15bceea160a559e9c5bf9585999961f.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 0
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 7
    },
    {
      "activity_id": "A12",
      "start_slot": 9
    },
    {
      "activity_id": "A13",
      "start_slot": 7
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 5
    },
    {
      "activity_id": "A17",
      "start_slot": 4
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 4
    },
    {
      "activity_id": "A21",
      "start_slot": 11
    },
    {
      "activity_id": "A22",
      "start_slot": 18
    },
    {
      "activity_id": "A23",
      "start_slot": 11
    },
    {
      "activity_id": "A24",
      "start_slot": 2
    },
    {
      "activity_id": "A3",
      "start_slot": 11
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 9
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 16
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": false,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 19,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": [
      {
        "activity_ids": [
          "A22"
        ],
        "category": "activity_availability",
        "constraint_id": null
      },
      {
        "activity_ids": [
          "A8"
        ],
        "category": "activity_availability",
        "constraint_id": null
      }
    ]
  },
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The returned schedule violates the evaluator's gold requirements.",
    "Gold validation found: activity_availability."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/c2efe41e33c3ed74c1b7b7c77c336c7ab59fe1ef1c2e5a4c0b95801531cad214.json`. SHA-256: `6235e393feca08e2e2e915e26ac1009e60cbf4e2cde7797d73ee9a620611be28`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/bb18aa0ca5f398d2bc721df6f48a4ff7c15bceea160a559e9c5bf9585999961f.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 0
    },
    {
      "activity_id": "A10",
      "start_slot": 2
    },
    {
      "activity_id": "A11",
      "start_slot": 7
    },
    {
      "activity_id": "A12",
      "start_slot": 9
    },
    {
      "activity_id": "A13",
      "start_slot": 7
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 2
    },
    {
      "activity_id": "A16",
      "start_slot": 5
    },
    {
      "activity_id": "A17",
      "start_slot": 4
    },
    {
      "activity_id": "A18",
      "start_slot": 2
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 0
    },
    {
      "activity_id": "A20",
      "start_slot": 4
    },
    {
      "activity_id": "A21",
      "start_slot": 9
    },
    {
      "activity_id": "A22",
      "start_slot": 13
    },
    {
      "activity_id": "A23",
      "start_slot": 11
    },
    {
      "activity_id": "A24",
      "start_slot": 2
    },
    {
      "activity_id": "A3",
      "start_slot": 11
    },
    {
      "activity_id": "A4",
      "start_slot": 9
    },
    {
      "activity_id": "A5",
      "start_slot": 11
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 4
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 22,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    22
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/74c91623ecec8895ebfe0f3a5f402a08ad95c7d9c3ed77d131a9bfeed0c5f270.json`. SHA-256: `9f6a59c87063efbf4aca1465df1bb08f09a7febea3c628a0d2fa3b42ef8c3843`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/bb18aa0ca5f398d2bc721df6f48a4ff7c15bceea160a559e9c5bf9585999961f.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C19

**Room contention · 32 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T00:00:00+08:00, timezone +08:00. There are 48 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,48) and has capacity one.
Participant P2 is available in [0,48) and has capacity one.
Participant P3 is available in [0,48) and has capacity one.
Participant P4 is available in [0,48) and has capacity one.
Participant P5 is available in [0,48) and has capacity one.
Participant P6 is available in [0,48) and has capacity one.
Participant P7 is available in [0,48) and has capacity one.
Participant P8 is available in [0,48) and has capacity one.
Resource R1 is available in [0,47) and has capacity one.
Resource R2 is available in [0,48) and has capacity one.
Resource R3 is available in [0,48) and has capacity one.
Activity A15 lasts 2 slots; participants: P2; resources: R1; availability: [0,18).
Activity A23 lasts 2 slots; participants: P1; resources: R1; availability: [19,25).
Activity A4 lasts 1 slots; participants: P5; resources: R1; availability: [25,48).
Activity A14 lasts 1 slots; participants: P3; resources: R1, R3; availability: [25,44).
Activity A2 lasts 1 slots; participants: P5; resources: R1, R3; availability: [19,39).
Activity A10 lasts 2 slots; participants: P3; resources: R1; availability: [40,46).
Activity A25 lasts 1 slots; participants: P6; resources: R1, R3; availability: [32,41).
Activity A27 lasts 1 slots; participants: P5; resources: R1; availability: [18,39).
Activity A6 lasts 2 slots; participants: P6; resources: R1; availability: [0,17).
Activity A32 lasts 1 slots; participants: P5; resources: R1, R2; availability: [1,24).
Activity A21 lasts 1 slots; participants: P6; resources: R1; availability: [12,21).
Activity A9 lasts 1 slots; participants: P7; resources: R1; availability: [31,37).
Activity A11 lasts 2 slots; participants: P1; resources: R1; availability: [2,22).
Activity A22 lasts 2 slots; participants: P1; resources: R1; availability: [32,48).
Activity A12 lasts 1 slots; participants: P7; resources: R1; availability: [40,46).
Activity A16 lasts 2 slots; participants: P3; resources: R1, R2; availability: [36,48).
Activity A26 lasts 1 slots; participants: P8; resources: R1, R2; availability: [2,31).
Activity A19 lasts 2 slots; participants: P8; resources: R1, R2; availability: [13,23).
Activity A28 lasts 1 slots; participants: P8; resources: R1; availability: [14,29).
Activity A1 lasts 1 slots; participants: P6; resources: R1, R3; availability: [0,18).
Activity A29 lasts 1 slots; participants: P7; resources: R1; availability: [29,42).
Activity A13 lasts 1 slots; participants: P1; resources: R1; availability: [21,31).
Activity A5 lasts 2 slots; participants: P7; resources: R1, R3; availability: [16,42).
Activity A8 lasts 1 slots; participants: P2; resources: R1; availability: [22,36).
Activity A18 lasts 2 slots; participants: P1; resources: R1; availability: [12,30).
Activity A7 lasts 2 slots; participants: P5; resources: R1; availability: [16,35).
Activity A24 lasts 2 slots; participants: P3; resources: R1; availability: [6,22).
Activity A20 lasts 2 slots; participants: P6; resources: R1; availability: [0,12).
Activity A30 lasts 1 slots; participants: P2; resources: R1; availability: [24,40).
Activity A17 lasts 2 slots; participants: P6; resources: R1, R3; availability: [0,12).
Activity A3 lasts 2 slots; participants: P4; resources: R1, R2; availability: [34,44).
Activity A31 lasts 2 slots; participants: P6; resources: R1; availability: [0,21).
Starting A8 outside [39,41) incurs penalty 3; starting inside incurs zero.
Starting A21 outside [36,38) incurs penalty 1; starting inside incurs zero.
A32 must finish before or when A9 starts.
Starting A15 outside [33,35) incurs penalty 3; starting inside incurs zero.
A26 must finish before or when A21 starts.
A31 must finish before or when A22 starts.
Starting A30 outside [9,13) incurs penalty 1; starting inside incurs zero.
Starting A26 outside [42,48) incurs penalty 2; starting inside incurs zero.
A32 must finish before or when A25 starts.
A7 must finish before or when A12 starts.
A11 must finish at or before slot 20.
Starting A14 outside [42,44) incurs penalty 2; starting inside incurs zero.
Starting A23 outside [8,10) incurs penalty 2; starting inside incurs zero.
Starting A6 outside [40,44) incurs penalty 1; starting inside incurs zero.
A17 must start exactly at slot 0.
Starting A2 outside [0,2) incurs penalty 1; starting inside incurs zero.
Starting A4 outside [26,30) incurs penalty 1; starting inside incurs zero.
A24 must finish before or when A13 starts.
Starting A31 outside [28,30) incurs penalty 1; starting inside incurs zero.
A6 must finish before or when A32 starts.
Starting A13 outside [42,46) incurs penalty 3; starting inside incurs zero.
Starting A22 outside [18,20) incurs penalty 2; starting inside incurs zero.
Starting A1 outside [1,3) incurs penalty 2; starting inside incurs zero.
A31 must finish before or when A4 starts.
Starting A12 outside [15,19) incurs penalty 1; starting inside incurs zero.
Starting A3 outside [7,13) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-038429f4f0897776a0b74b83`. Gold label: **UNSAT**. Horizon: `2026-10-26T00:00:00+08:00`; timezone `+08:00`; 48 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 48) |
| P2 | [0, 48) |
| P3 | [0, 48) |
| P4 | [0, 48) |
| P5 | [0, 48) |
| P6 | [0, 48) |
| P7 | [0, 48) |
| P8 | [0, 48) |
| R1 | [0, 47) |
| R2 | [0, 48) |
| R3 | [0, 48) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A15 | 2 | P2 | R1 | [0, 18) |
| A23 | 2 | P1 | R1 | [19, 25) |
| A4 | 1 | P5 | R1 | [25, 48) |
| A14 | 1 | P3 | R1, R3 | [25, 44) |
| A2 | 1 | P5 | R1, R3 | [19, 39) |
| A10 | 2 | P3 | R1 | [40, 46) |
| A25 | 1 | P6 | R1, R3 | [32, 41) |
| A27 | 1 | P5 | R1 | [18, 39) |
| A6 | 2 | P6 | R1 | [0, 17) |
| A32 | 1 | P5 | R1, R2 | [1, 24) |
| A21 | 1 | P6 | R1 | [12, 21) |
| A9 | 1 | P7 | R1 | [31, 37) |
| A11 | 2 | P1 | R1 | [2, 22) |
| A22 | 2 | P1 | R1 | [32, 48) |
| A12 | 1 | P7 | R1 | [40, 46) |
| A16 | 2 | P3 | R1, R2 | [36, 48) |
| A26 | 1 | P8 | R1, R2 | [2, 31) |
| A19 | 2 | P8 | R1, R2 | [13, 23) |
| A28 | 1 | P8 | R1 | [14, 29) |
| A1 | 1 | P6 | R1, R3 | [0, 18) |
| A29 | 1 | P7 | R1 | [29, 42) |
| A13 | 1 | P1 | R1 | [21, 31) |
| A5 | 2 | P7 | R1, R3 | [16, 42) |
| A8 | 1 | P2 | R1 | [22, 36) |
| A18 | 2 | P1 | R1 | [12, 30) |
| A7 | 2 | P5 | R1 | [16, 35) |
| A24 | 2 | P3 | R1 | [6, 22) |
| A20 | 2 | P6 | R1 | [0, 12) |
| A30 | 1 | P2 | R1 | [24, 40) |
| A17 | 2 | P6 | R1, R3 | [0, 12) |
| A3 | 2 | P4 | R1, R2 | [34, 44) |
| A31 | 2 | P6 | R1 | [0, 21) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A8","end":41,"id":"PREF19","start":39,"type":"preferred_start","weight":3}`
- `{"activity_id":"A21","end":38,"id":"PREF11","start":36,"type":"preferred_start","weight":1}`
- `{"after":"A9","before":"A32","id":"C_edge22","type":"precedence"}`
- `{"activity_id":"A15","end":35,"id":"PREF7","start":33,"type":"preferred_start","weight":3}`
- `{"after":"A21","before":"A26","id":"C_edge11","type":"precedence"}`
- `{"after":"A22","before":"A31","id":"C_edge31","type":"precedence"}`
- `{"activity_id":"A30","end":13,"id":"PREF23","start":9,"type":"preferred_start","weight":1}`
- `{"activity_id":"A26","end":48,"id":"PREF9","start":42,"type":"preferred_start","weight":2}`
- `{"after":"A25","before":"A32","id":"C_edge24","type":"precedence"}`
- `{"after":"A12","before":"A7","id":"C_edge29","type":"precedence"}`
- `{"activity_id":"A11","id":"C_profile_deadline","slot":20,"type":"deadline"}`
- `{"activity_id":"A14","end":44,"id":"PREF21","start":42,"type":"preferred_start","weight":2}`
- `{"activity_id":"A23","end":10,"id":"PREF13","start":8,"type":"preferred_start","weight":2}`
- `{"activity_id":"A6","end":44,"id":"PREF1","start":40,"type":"preferred_start","weight":1}`
- `{"activity_id":"A17","id":"C_profile_fixed","slot":0,"type":"fixed_start"}`
- `{"activity_id":"A2","end":2,"id":"PREF15","start":0,"type":"preferred_start","weight":1}`
- `{"activity_id":"A4","end":30,"id":"PREF25","start":26,"type":"preferred_start","weight":1}`
- `{"after":"A13","before":"A24","id":"C_edge17","type":"precedence"}`
- `{"activity_id":"A31","end":30,"id":"PREF5","start":28,"type":"preferred_start","weight":1}`
- `{"after":"A32","before":"A6","id":"C_edge6","type":"precedence"}`
- `{"activity_id":"A13","end":46,"id":"PREF17","start":42,"type":"preferred_start","weight":3}`
- `{"activity_id":"A22","end":20,"id":"PREF31","start":18,"type":"preferred_start","weight":2}`
- `{"activity_id":"A1","end":3,"id":"PREF3","start":1,"type":"preferred_start","weight":2}`
- `{"after":"A4","before":"A31","id":"C_edge25","type":"precedence"}`
- `{"activity_id":"A12","end":19,"id":"PREF29","start":15,"type":"preferred_start","weight":1}`
- `{"activity_id":"A3","end":13,"id":"PREF27","start":7,"type":"preferred_start","weight":2}`

**Saved reference:** `INFEASIBLE`; objective values `null`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Infeasibility review:** derive a concrete capacity, precedence or window contradiction from the request. If you cannot verify one, record that limitation; the saved reference status alone does not complete human verification.

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | Yes | UNSAT | accepted | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Direct | Yes | UNSAT | accepted | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | UNSAT | accepted | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/33501c7b5a92e9154c22a20583d08c03190110bdc9d91cdd8408c7355d6a2442.json`. SHA-256: `4035f934c42e5226ae527adba0c0b6199c6d9473126be6f26bb6f4485824b989`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/53f33d10ec1bda93532c7c2889f7ab503314317502582a90b5b9a553c2da2ea2.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": {
          "end": 48,
          "start": 47,
          "target_id": "R1",
          "target_kind": "resource",
          "type": "blocked"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 1,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 0,
    "structurally_equivalent": false
  },
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/02dcbd15f51ccdfacd781285136b715b323c0521e179b7268a0c05f09594ff4e.json`. SHA-256: `f75aabee88840df5e06899980c1c2f0b322970513922bf9d6e39d14cce1378f2`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/53f33d10ec1bda93532c7c2889f7ab503314317502582a90b5b9a553c2da2ea2.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/9c6bf6815af10516260892efa34e52e193d4fc49fcf95e4bb5a708a2413cbbcc.json`. SHA-256: `7599b007786e3229ecb564fb910f051fbc06754a5eddcc202b8814c5863f9b14`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/53f33d10ec1bda93532c7c2889f7ab503314317502582a90b5b9a553c2da2ea2.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/658cb93ec7e967408e69c949b83ae122411eb74b688f433f8e7b6f8f0bd94597.json`. SHA-256: `6f39cd615662d2738de81123572e1e04ea4b1323d8ca96996b3521db70df1f65`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/53f33d10ec1bda93532c7c2889f7ab503314317502582a90b5b9a553c2da2ea2.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## C20

**Room contention · 32 activities · Reviewer: Li Hao.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T00:00:00+08:00, timezone +08:00. There are 48 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,48) and has capacity one.
Participant P2 is available in [0,48) and has capacity one.
Participant P3 is available in [0,48) and has capacity one.
Participant P4 is available in [0,48) and has capacity one.
Participant P5 is available in [0,48) and has capacity one.
Participant P6 is available in [0,48) and has capacity one.
Participant P7 is available in [0,48) and has capacity one.
Participant P8 is available in [0,48) and has capacity one.
Resource R1 is available in [0,48) and has capacity one.
Resource R2 is available in [0,48) and has capacity one.
Resource R3 is available in [0,48) and has capacity one.
Activity A17 lasts 2 slots; participants: P1; resources: R1; availability: [22,48).
Activity A31 lasts 2 slots; participants: P7; resources: R1; availability: [30,48).
Activity A13 lasts 1 slots; participants: P8; resources: R1; availability: [35,48).
Activity A7 lasts 1 slots; participants: P5; resources: R1, R3; availability: [31,46).
Activity A3 lasts 2 slots; participants: P4; resources: R1; availability: [15,28).
Activity A11 lasts 1 slots; participants: P6; resources: R1, R3; availability: [41,48).
Activity A6 lasts 2 slots; participants: P3; resources: R1, R3; availability: [0,17).
Activity A14 lasts 2 slots; participants: P8; resources: R1; availability: [29,47).
Activity A5 lasts 1 slots; participants: P5; resources: R1; availability: [32,39).
Activity A23 lasts 1 slots; participants: P2; resources: R1; availability: [14,19).
Activity A15 lasts 2 slots; participants: P3; resources: R1, R2; availability: [21,47).
Activity A32 lasts 1 slots; participants: P7; resources: R1, R3; availability: [13,16).
Activity A30 lasts 2 slots; participants: P2; resources: R1; availability: [0,17).
Activity A8 lasts 1 slots; participants: P4; resources: R1; availability: [9,30).
Activity A22 lasts 1 slots; participants: P1; resources: R1; availability: [0,21).
Activity A27 lasts 2 slots; participants: P2; resources: R1; availability: [37,48).
Activity A24 lasts 2 slots; participants: P1; resources: R1, R3; availability: [15,33).
Activity A10 lasts 2 slots; participants: P2; resources: R1; availability: [4,23).
Activity A28 lasts 2 slots; participants: P8; resources: R1; availability: [31,44).
Activity A2 lasts 2 slots; participants: P6; resources: R1; availability: [0,18).
Activity A9 lasts 1 slots; participants: P2; resources: R1, R2; availability: [6,30).
Activity A4 lasts 1 slots; participants: P8; resources: R1, R3; availability: [1,17).
Activity A26 lasts 2 slots; participants: P3; resources: R1; availability: [0,6).
Activity A21 lasts 1 slots; participants: P3; resources: R1; availability: [7,22).
Activity A25 lasts 2 slots; participants: P8; resources: R1; availability: [13,31).
Activity A18 lasts 1 slots; participants: P7; resources: R1, R3; availability: [0,9).
Activity A12 lasts 1 slots; participants: P4; resources: R1, R2; availability: [30,38).
Activity A1 lasts 2 slots; participants: P5; resources: R1; availability: [8,27).
Activity A19 lasts 2 slots; participants: P4; resources: R1, R2; availability: [12,26).
Activity A16 lasts 1 slots; participants: P6; resources: R1; availability: [20,39).
Activity A29 lasts 1 slots; participants: P8; resources: R1; availability: [17,38).
Activity A20 lasts 1 slots; participants: P8; resources: R1; availability: [10,26).
A24 must finish before or when A16 starts.
A32 must finish before or when A29 starts.
Starting A4 outside [14,16) incurs penalty 1; starting inside incurs zero.
A18 must finish before or when A30 starts.
Starting A23 outside [4,10) incurs penalty 2; starting inside incurs zero.
A8 must finish before or when A24 starts.
Starting A7 outside [2,8) incurs penalty 2; starting inside incurs zero.
A8 must finish at or before slot 17.
Starting A14 outside [13,15) incurs penalty 3; starting inside incurs zero.
A18 must start exactly at slot 0.
A4 must finish before or when A31 starts.
A18 must finish before or when A19 starts.
A19 must finish before or when A3 starts.
A24 must finish before or when A12 starts.
A26 must finish before or when A14 starts.
A2 must finish before or when A13 starts.
A24 must finish before or when A11 starts.
Starting A25 outside [26,30) incurs penalty 1; starting inside incurs zero.
Starting A28 outside [4,6) incurs penalty 2; starting inside incurs zero.
Starting A29 outside [41,45) incurs penalty 3; starting inside incurs zero.
Starting A19 outside [9,13) incurs penalty 3; starting inside incurs zero.
Starting A20 outside [19,25) incurs penalty 3; starting inside incurs zero.
A12 must finish before or when A27 starts.
Starting A12 outside [33,39) incurs penalty 3; starting inside incurs zero.
Starting A5 outside [13,17) incurs penalty 3; starting inside incurs zero.
Starting A21 outside [23,27) incurs penalty 3; starting inside incurs zero.
Starting A26 outside [10,12) incurs penalty 1; starting inside incurs zero.
A30 must finish before or when A22 starts.
A1 must finish before or when A17 starts.
Starting A32 outside [9,11) incurs penalty 2; starting inside incurs zero.
Starting A13 outside [7,11) incurs penalty 2; starting inside incurs zero.
Starting A2 outside [29,31) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-147021efe8e5b6307b38828c`. Gold label: **SAT**. Horizon: `2026-10-26T00:00:00+08:00`; timezone `+08:00`; 48 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 48) |
| P2 | [0, 48) |
| P3 | [0, 48) |
| P4 | [0, 48) |
| P5 | [0, 48) |
| P6 | [0, 48) |
| P7 | [0, 48) |
| P8 | [0, 48) |
| R1 | [0, 48) |
| R2 | [0, 48) |
| R3 | [0, 48) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A17 | 2 | P1 | R1 | [22, 48) |
| A31 | 2 | P7 | R1 | [30, 48) |
| A13 | 1 | P8 | R1 | [35, 48) |
| A7 | 1 | P5 | R1, R3 | [31, 46) |
| A3 | 2 | P4 | R1 | [15, 28) |
| A11 | 1 | P6 | R1, R3 | [41, 48) |
| A6 | 2 | P3 | R1, R3 | [0, 17) |
| A14 | 2 | P8 | R1 | [29, 47) |
| A5 | 1 | P5 | R1 | [32, 39) |
| A23 | 1 | P2 | R1 | [14, 19) |
| A15 | 2 | P3 | R1, R2 | [21, 47) |
| A32 | 1 | P7 | R1, R3 | [13, 16) |
| A30 | 2 | P2 | R1 | [0, 17) |
| A8 | 1 | P4 | R1 | [9, 30) |
| A22 | 1 | P1 | R1 | [0, 21) |
| A27 | 2 | P2 | R1 | [37, 48) |
| A24 | 2 | P1 | R1, R3 | [15, 33) |
| A10 | 2 | P2 | R1 | [4, 23) |
| A28 | 2 | P8 | R1 | [31, 44) |
| A2 | 2 | P6 | R1 | [0, 18) |
| A9 | 1 | P2 | R1, R2 | [6, 30) |
| A4 | 1 | P8 | R1, R3 | [1, 17) |
| A26 | 2 | P3 | R1 | [0, 6) |
| A21 | 1 | P3 | R1 | [7, 22) |
| A25 | 2 | P8 | R1 | [13, 31) |
| A18 | 1 | P7 | R1, R3 | [0, 9) |
| A12 | 1 | P4 | R1, R2 | [30, 38) |
| A1 | 2 | P5 | R1 | [8, 27) |
| A19 | 2 | P4 | R1, R2 | [12, 26) |
| A16 | 1 | P6 | R1 | [20, 39) |
| A29 | 1 | P8 | R1 | [17, 38) |
| A20 | 1 | P8 | R1 | [10, 26) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A16","before":"A24","id":"C_edge20","type":"precedence"}`
- `{"after":"A29","before":"A32","id":"C_edge17","type":"precedence"}`
- `{"activity_id":"A4","end":16,"id":"PREF3","start":14,"type":"preferred_start","weight":1}`
- `{"after":"A30","before":"A18","id":"C_edge2","type":"precedence"}`
- `{"activity_id":"A23","end":10,"id":"PREF11","start":4,"type":"preferred_start","weight":2}`
- `{"after":"A24","before":"A8","id":"C_edge18","type":"precedence"}`
- `{"activity_id":"A7","end":8,"id":"PREF27","start":2,"type":"preferred_start","weight":2}`
- `{"activity_id":"A8","id":"C_profile_deadline","slot":17,"type":"deadline"}`
- `{"activity_id":"A14","end":15,"id":"PREF29","start":13,"type":"preferred_start","weight":3}`
- `{"activity_id":"A18","id":"C_profile_fixed","slot":0,"type":"fixed_start"}`
- `{"after":"A31","before":"A4","id":"C_edge26","type":"precedence"}`
- `{"after":"A19","before":"A18","id":"C_edge15","type":"precedence"}`
- `{"after":"A3","before":"A19","id":"C_edge16","type":"precedence"}`
- `{"after":"A12","before":"A24","id":"C_edge21","type":"precedence"}`
- `{"after":"A14","before":"A26","id":"C_edge29","type":"precedence"}`
- `{"after":"A13","before":"A2","id":"C_edge31","type":"precedence"}`
- `{"after":"A11","before":"A24","id":"C_edge30","type":"precedence"}`
- `{"activity_id":"A25","end":30,"id":"PREF19","start":26,"type":"preferred_start","weight":1}`
- `{"activity_id":"A28","end":6,"id":"PREF25","start":4,"type":"preferred_start","weight":2}`
- `{"activity_id":"A29","end":45,"id":"PREF17","start":41,"type":"preferred_start","weight":3}`
- `{"activity_id":"A19","end":13,"id":"PREF15","start":9,"type":"preferred_start","weight":3}`
- `{"activity_id":"A20","end":25,"id":"PREF13","start":19,"type":"preferred_start","weight":3}`
- `{"after":"A27","before":"A12","id":"C_edge28","type":"precedence"}`
- `{"activity_id":"A12","end":39,"id":"PREF21","start":33,"type":"preferred_start","weight":3}`
- `{"activity_id":"A5","end":17,"id":"PREF23","start":13,"type":"preferred_start","weight":3}`
- `{"activity_id":"A21","end":27,"id":"PREF7","start":23,"type":"preferred_start","weight":3}`
- `{"activity_id":"A26","end":12,"id":"PREF1","start":10,"type":"preferred_start","weight":1}`
- `{"after":"A22","before":"A30","id":"C_edge4","type":"precedence"}`
- `{"after":"A17","before":"A1","id":"C_edge22","type":"precedence"}`
- `{"activity_id":"A32","end":11,"id":"PREF9","start":9,"type":"preferred_start","weight":2}`
- `{"activity_id":"A13","end":11,"id":"PREF31","start":7,"type":"preferred_start","weight":2}`
- `{"activity_id":"A2","end":31,"id":"PREF5","start":29,"type":"preferred_start","weight":1}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":24,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 20
  },
  {
    "activity_id": "A10",
    "start_slot": 17
  },
  {
    "activity_id": "A11",
    "start_slot": 47
  },
  {
    "activity_id": "A12",
    "start_slot": 33
  },
  {
    "activity_id": "A13",
    "start_slot": 46
  },
  {
    "activity_id": "A14",
    "start_slot": 36
  },
  {
    "activity_id": "A15",
    "start_slot": 38
  },
  {
    "activity_id": "A16",
    "start_slot": 30
  },
  {
    "activity_id": "A17",
    "start_slot": 42
  },
  {
    "activity_id": "A18",
    "start_slot": 0
  },
  {
    "activity_id": "A19",
    "start_slot": 12
  },
  {
    "activity_id": "A2",
    "start_slot": 7
  },
  {
    "activity_id": "A20",
    "start_slot": 19
  },
  {
    "activity_id": "A21",
    "start_slot": 11
  },
  {
    "activity_id": "A22",
    "start_slot": 10
  },
  {
    "activity_id": "A23",
    "start_slot": 16
  },
  {
    "activity_id": "A24",
    "start_slot": 28
  },
  {
    "activity_id": "A25",
    "start_slot": 26
  },
  {
    "activity_id": "A26",
    "start_slot": 1
  },
  {
    "activity_id": "A27",
    "start_slot": 44
  },
  {
    "activity_id": "A28",
    "start_slot": 31
  },
  {
    "activity_id": "A29",
    "start_slot": 25
  },
  {
    "activity_id": "A3",
    "start_slot": 22
  },
  {
    "activity_id": "A30",
    "start_slot": 3
  },
  {
    "activity_id": "A31",
    "start_slot": 40
  },
  {
    "activity_id": "A32",
    "start_slot": 15
  },
  {
    "activity_id": "A4",
    "start_slot": 14
  },
  {
    "activity_id": "A5",
    "start_slot": 34
  },
  {
    "activity_id": "A6",
    "start_slot": 5
  },
  {
    "activity_id": "A7",
    "start_slot": 35
  },
  {
    "activity_id": "A8",
    "start_slot": 9
  },
  {
    "activity_id": "A9",
    "start_slot": 24
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[24]` |
| GLM5.3 Flash | Direct | No | SAT | gold_invalid_schedule | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[24]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/689fe1881a8ec97b211ed14d865f03badb37a98557b41393700f834b06994bfe.json`. SHA-256: `e49760d6fbad6b01ca1aac7804ded394a6deadcd7cecfbb46eb4990e78c3d9bd`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/df51b6d4b8b418ce2670139f60ae7ce10dbea82ba145aefeda0a9413fd0236d9.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 20
    },
    {
      "activity_id": "A10",
      "start_slot": 17
    },
    {
      "activity_id": "A11",
      "start_slot": 47
    },
    {
      "activity_id": "A12",
      "start_slot": 33
    },
    {
      "activity_id": "A13",
      "start_slot": 46
    },
    {
      "activity_id": "A14",
      "start_slot": 36
    },
    {
      "activity_id": "A15",
      "start_slot": 38
    },
    {
      "activity_id": "A16",
      "start_slot": 30
    },
    {
      "activity_id": "A17",
      "start_slot": 42
    },
    {
      "activity_id": "A18",
      "start_slot": 0
    },
    {
      "activity_id": "A19",
      "start_slot": 12
    },
    {
      "activity_id": "A2",
      "start_slot": 7
    },
    {
      "activity_id": "A20",
      "start_slot": 19
    },
    {
      "activity_id": "A21",
      "start_slot": 11
    },
    {
      "activity_id": "A22",
      "start_slot": 10
    },
    {
      "activity_id": "A23",
      "start_slot": 16
    },
    {
      "activity_id": "A24",
      "start_slot": 28
    },
    {
      "activity_id": "A25",
      "start_slot": 26
    },
    {
      "activity_id": "A26",
      "start_slot": 1
    },
    {
      "activity_id": "A27",
      "start_slot": 44
    },
    {
      "activity_id": "A28",
      "start_slot": 31
    },
    {
      "activity_id": "A29",
      "start_slot": 25
    },
    {
      "activity_id": "A3",
      "start_slot": 22
    },
    {
      "activity_id": "A30",
      "start_slot": 3
    },
    {
      "activity_id": "A31",
      "start_slot": 40
    },
    {
      "activity_id": "A32",
      "start_slot": 15
    },
    {
      "activity_id": "A4",
      "start_slot": 14
    },
    {
      "activity_id": "A5",
      "start_slot": 34
    },
    {
      "activity_id": "A6",
      "start_slot": 5
    },
    {
      "activity_id": "A7",
      "start_slot": 35
    },
    {
      "activity_id": "A8",
      "start_slot": 9
    },
    {
      "activity_id": "A9",
      "start_slot": 24
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 24,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    24
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/11fdbc76ff301169504d1373120e15e73b0c98df5bebc8ded27c712be3e15941.json`. SHA-256: `52fb702bb70cb8f6b693e95ecbb9847ad6c2be7f1809faba637c1b189274cda0`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/df51b6d4b8b418ce2670139f60ae7ce10dbea82ba145aefeda0a9413fd0236d9.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 22
    },
    {
      "activity_id": "A10",
      "start_slot": 5
    },
    {
      "activity_id": "A11",
      "start_slot": 41
    },
    {
      "activity_id": "A12",
      "start_slot": 33
    },
    {
      "activity_id": "A13",
      "start_slot": 35
    },
    {
      "activity_id": "A14",
      "start_slot": 29
    },
    {
      "activity_id": "A15",
      "start_slot": 39
    },
    {
      "activity_id": "A16",
      "start_slot": 45
    },
    {
      "activity_id": "A17",
      "start_slot": 46
    },
    {
      "activity_id": "A18",
      "start_slot": 0
    },
    {
      "activity_id": "A19",
      "start_slot": 12
    },
    {
      "activity_id": "A2",
      "start_slot": 7
    },
    {
      "activity_id": "A20",
      "start_slot": 19
    },
    {
      "activity_id": "A21",
      "start_slot": 18
    },
    {
      "activity_id": "A22",
      "start_slot": 17
    },
    {
      "activity_id": "A23",
      "start_slot": 16
    },
    {
      "activity_id": "A24",
      "start_slot": 20
    },
    {
      "activity_id": "A25",
      "start_slot": 26
    },
    {
      "activity_id": "A26",
      "start_slot": 1
    },
    {
      "activity_id": "A27",
      "start_slot": 37
    },
    {
      "activity_id": "A28",
      "start_slot": 31
    },
    {
      "activity_id": "A29",
      "start_slot": 36
    },
    {
      "activity_id": "A3",
      "start_slot": 24
    },
    {
      "activity_id": "A30",
      "start_slot": 10
    },
    {
      "activity_id": "A31",
      "start_slot": 42
    },
    {
      "activity_id": "A32",
      "start_slot": 15
    },
    {
      "activity_id": "A4",
      "start_slot": 14
    },
    {
      "activity_id": "A5",
      "start_slot": 34
    },
    {
      "activity_id": "A6",
      "start_slot": 3
    },
    {
      "activity_id": "A7",
      "start_slot": 44
    },
    {
      "activity_id": "A8",
      "start_slot": 9
    },
    {
      "activity_id": "A9",
      "start_slot": 28
    }
  ],
  "validation": {
    "hard_feasible": false,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 24,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": [
      {
        "activity_ids": [
          "A16"
        ],
        "category": "activity_availability",
        "constraint_id": null
      }
    ]
  },
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The returned schedule violates the evaluator's gold requirements.",
    "Gold validation found: activity_availability."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/699cf8dff5498bca1a4a6e7b1419b32ca94489c02888daa2e788f33692392085.json`. SHA-256: `e9c950ae33a4f939b4788dec39fc23d47e12ecdaf0148386fde430d88d89bfa2`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/df51b6d4b8b418ce2670139f60ae7ce10dbea82ba145aefeda0a9413fd0236d9.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 20
    },
    {
      "activity_id": "A10",
      "start_slot": 17
    },
    {
      "activity_id": "A11",
      "start_slot": 47
    },
    {
      "activity_id": "A12",
      "start_slot": 33
    },
    {
      "activity_id": "A13",
      "start_slot": 46
    },
    {
      "activity_id": "A14",
      "start_slot": 36
    },
    {
      "activity_id": "A15",
      "start_slot": 38
    },
    {
      "activity_id": "A16",
      "start_slot": 30
    },
    {
      "activity_id": "A17",
      "start_slot": 42
    },
    {
      "activity_id": "A18",
      "start_slot": 0
    },
    {
      "activity_id": "A19",
      "start_slot": 12
    },
    {
      "activity_id": "A2",
      "start_slot": 7
    },
    {
      "activity_id": "A20",
      "start_slot": 19
    },
    {
      "activity_id": "A21",
      "start_slot": 11
    },
    {
      "activity_id": "A22",
      "start_slot": 10
    },
    {
      "activity_id": "A23",
      "start_slot": 16
    },
    {
      "activity_id": "A24",
      "start_slot": 28
    },
    {
      "activity_id": "A25",
      "start_slot": 26
    },
    {
      "activity_id": "A26",
      "start_slot": 1
    },
    {
      "activity_id": "A27",
      "start_slot": 44
    },
    {
      "activity_id": "A28",
      "start_slot": 31
    },
    {
      "activity_id": "A29",
      "start_slot": 25
    },
    {
      "activity_id": "A3",
      "start_slot": 22
    },
    {
      "activity_id": "A30",
      "start_slot": 3
    },
    {
      "activity_id": "A31",
      "start_slot": 40
    },
    {
      "activity_id": "A32",
      "start_slot": 15
    },
    {
      "activity_id": "A4",
      "start_slot": 14
    },
    {
      "activity_id": "A5",
      "start_slot": 34
    },
    {
      "activity_id": "A6",
      "start_slot": 5
    },
    {
      "activity_id": "A7",
      "start_slot": 35
    },
    {
      "activity_id": "A8",
      "start_slot": 9
    },
    {
      "activity_id": "A9",
      "start_slot": 24
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 24,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    24
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/6f28c62bec0f7d716581195cfe700e6ad4c8cdc0645b1041095d21efca183cc9.json`. SHA-256: `f6f3e803706d0c1a37fe27b57b67241cccebce8d160b6928a04c04bdaebc9a3c`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/df51b6d4b8b418ce2670139f60ae7ce10dbea82ba145aefeda0a9413fd0236d9.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## E1

**Room contention · 8 activities · Reviewer: All three.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,10) and has capacity one.
Activity A6 lasts 2 slots; participants: P1; resources: R1; availability: [2,11).
Activity A7 lasts 1 slots; participants: P1; resources: R1; availability: [3,11).
Activity A5 lasts 1 slots; participants: P2; resources: R1; availability: [0,5).
Activity A3 lasts 1 slots; participants: P1; resources: R1; availability: [1,8).
Activity A1 lasts 1 slots; participants: P1; resources: R1; availability: [2,9).
Activity A8 lasts 1 slots; participants: P2; resources: R1; availability: [0,3).
Activity A2 lasts 2 slots; participants: P2; resources: R1; availability: [6,12).
Activity A4 lasts 1 slots; participants: P1; resources: R1; availability: [0,4).
Starting A8 outside [10,16) incurs penalty 3; starting inside incurs zero.
A8 must finish before or when A3 starts.
A5 must finish before or when A7 starts.
A3 must finish before or when A6 starts.
A7 must finish before or when A2 starts.
A8 must start exactly at slot 0.
Starting A4 outside [10,16) incurs penalty 1; starting inside incurs zero.
Starting A1 outside [11,15) incurs penalty 2; starting inside incurs zero.
Starting A7 outside [6,10) incurs penalty 1; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-3fd5174321284caacab1f4a9`. Gold label: **SAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 10) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A6 | 2 | P1 | R1 | [2, 11) |
| A7 | 1 | P1 | R1 | [3, 11) |
| A5 | 1 | P2 | R1 | [0, 5) |
| A3 | 1 | P1 | R1 | [1, 8) |
| A1 | 1 | P1 | R1 | [2, 9) |
| A8 | 1 | P2 | R1 | [0, 3) |
| A2 | 2 | P2 | R1 | [6, 12) |
| A4 | 1 | P1 | R1 | [0, 4) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A8","end":16,"id":"PREF0","start":10,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A8","id":"C_edge3","type":"precedence"}`
- `{"after":"A7","before":"A5","id":"C_edge6","type":"precedence"}`
- `{"after":"A6","before":"A3","id":"C_edge5","type":"precedence"}`
- `{"after":"A2","before":"A7","id":"C_edge7","type":"precedence"}`
- `{"activity_id":"A8","id":"C_profile_fixed","slot":0,"type":"fixed_start"}`
- `{"activity_id":"A4","end":16,"id":"PREF2","start":10,"type":"preferred_start","weight":1}`
- `{"activity_id":"A1","end":15,"id":"PREF4","start":11,"type":"preferred_start","weight":2}`
- `{"activity_id":"A7","end":10,"id":"PREF6","start":6,"type":"preferred_start","weight":1}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":6,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 7
  },
  {
    "activity_id": "A2",
    "start_slot": 8
  },
  {
    "activity_id": "A3",
    "start_slot": 1
  },
  {
    "activity_id": "A4",
    "start_slot": 2
  },
  {
    "activity_id": "A5",
    "start_slot": 3
  },
  {
    "activity_id": "A6",
    "start_slot": 4
  },
  {
    "activity_id": "A7",
    "start_slot": 6
  },
  {
    "activity_id": "A8",
    "start_slot": 0
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[6]` |
| GLM5.3 Flash | Direct | No | SAT | gold_invalid_schedule | `null` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[6]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/1eb9b8bce0381b67e305f03f5335ae96b8edef2fd8119449fc6022244c6dc116.json`. SHA-256: `deede02cb589235eaf70364f39086bf79ec875921fc9b80cb440cb56c3029572`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d68061e896e6acac5c8272e8e7e9e17059c380d7b77e009c447a728e83dcbda3.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 8
    },
    {
      "activity_id": "A3",
      "start_slot": 1
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 3
    },
    {
      "activity_id": "A6",
      "start_slot": 4
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    6
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/e81f581d8980a870ce86bfd9e5d80284fd789ea8ea18e4f40d23fba948d69b72.json`. SHA-256: `2b16f5de765f7a3669aa39a7256db9fb4658042d8b28f61e0201d0d549433ca9`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d68061e896e6acac5c8272e8e7e9e17059c380d7b77e009c447a728e83dcbda3.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 5
    },
    {
      "activity_id": "A2",
      "start_slot": 7
    },
    {
      "activity_id": "A3",
      "start_slot": 1
    },
    {
      "activity_id": "A4",
      "start_slot": 4
    },
    {
      "activity_id": "A5",
      "start_slot": 4
    },
    {
      "activity_id": "A6",
      "start_slot": 2
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": false,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": [
      {
        "activity_ids": [
          "A4"
        ],
        "category": "activity_availability",
        "constraint_id": null
      },
      {
        "activity_ids": [
          "A5",
          "A4"
        ],
        "category": "resource_overlap",
        "constraint_id": null
      }
    ]
  },
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The returned schedule violates the evaluator's gold requirements.",
    "Gold validation found: activity_availability, resource_overlap."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/c6e8938fded99db88efdc7a833a65b7046c188ec85891a287681a291f4a9df13.json`. SHA-256: `8357b8111c8ca6e7442c6a6eb31837fafe1f4bca0fb335b6fe3f7417071e8969`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d68061e896e6acac5c8272e8e7e9e17059c380d7b77e009c447a728e83dcbda3.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 7
    },
    {
      "activity_id": "A2",
      "start_slot": 8
    },
    {
      "activity_id": "A3",
      "start_slot": 1
    },
    {
      "activity_id": "A4",
      "start_slot": 2
    },
    {
      "activity_id": "A5",
      "start_slot": 3
    },
    {
      "activity_id": "A6",
      "start_slot": 4
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 0
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 6,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    6
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/cb0fad0d24ffd7db5993c4052ccc0166c6b538bad335ea36f7b347aa1dc6f3f0.json`. SHA-256: `79b640ebe20a7ac99b902b4fb589663ad08db9e414dbe3cab87989271fce4ee5`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/d68061e896e6acac5c8272e8e7e9e17059c380d7b77e009c447a728e83dcbda3.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## E2

**Appointment collision · 8 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T09:00:00+08:00, timezone +08:00. There are 16 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,16) and has capacity one.
Participant P2 is available in [0,16) and has capacity one.
Resource R1 is available in [0,16) and has capacity one.
Activity A6 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A1 lasts 2 slots; participants: P1; resources: none; availability: [4,6).
Activity A5 lasts 2 slots; participants: P2; resources: R1; availability: [0,4).
Activity A2 lasts 3 slots; participants: P2; resources: none; availability: [4,10).
Activity A7 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A8 lasts 2 slots; participants: P2; resources: R1; availability: [2,7).
Activity A3 lasts 2 slots; participants: P1; resources: R1; availability: [7,12).
Activity A4 lasts 2 slots; participants: P1; resources: none; availability: [0,3), [5,9).
A6 must finish before or when A5 starts.
A5 must finish before or when A1 starts.
A7 must start exactly at slot 2.
A6 must finish before or when A2 starts.
A6 must start exactly at slot 0.
A7 must finish before or when A8 starts.
A7 must finish before or when A1 starts.
A6 must finish before or when A8 starts.
Starting A1 outside [0,2) incurs penalty 2; starting inside incurs zero.
A8 must finish before or when A4 starts.
Starting A6 outside [9,15) incurs penalty 3; starting inside incurs zero.
A7 must finish before or when A3 starts.
Starting A4 outside [8,10) incurs penalty 1; starting inside incurs zero.
Starting A5 outside [5,9) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-901f5127b3f63880cc499f19`. Gold label: **SAT**. Horizon: `2026-10-26T09:00:00+08:00`; timezone `+08:00`; 16 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 16) |
| P2 | [0, 16) |
| R1 | [0, 16) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A6 | 2 | P1 | None | [0, 6) |
| A1 | 2 | P1 | None | [4, 6) |
| A5 | 2 | P2 | R1 | [0, 4) |
| A2 | 3 | P2 | None | [4, 10) |
| A7 | 2 | P1 | None | [0, 6) |
| A8 | 2 | P2 | R1 | [2, 7) |
| A3 | 2 | P1 | R1 | [7, 12) |
| A4 | 2 | P1 | None | [0, 3), [5, 9) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A5","before":"A6","id":"C_bg2","type":"precedence"}`
- `{"after":"A1","before":"A5","id":"C_extra6","type":"precedence"}`
- `{"activity_id":"A7","id":"C_fixed1","slot":2,"type":"fixed_start"}`
- `{"after":"A2","before":"A6","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A6","id":"C_fixed0","slot":0,"type":"fixed_start"}`
- `{"after":"A8","before":"A7","id":"C_extra3","type":"precedence"}`
- `{"after":"A1","before":"A7","id":"C_bg6","type":"precedence"}`
- `{"after":"A8","before":"A6","id":"C_bg3","type":"precedence"}`
- `{"activity_id":"A1","end":2,"id":"PREF6","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A4","before":"A8","id":"C_bg4","type":"precedence"}`
- `{"activity_id":"A6","end":15,"id":"PREF0","start":9,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A7","id":"C_bg7","type":"precedence"}`
- `{"activity_id":"A4","end":10,"id":"PREF4","start":8,"type":"preferred_start","weight":1}`
- `{"activity_id":"A5","end":9,"id":"PREF2","start":5,"type":"preferred_start","weight":2}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":8,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 4
  },
  {
    "activity_id": "A2",
    "start_slot": 7
  },
  {
    "activity_id": "A3",
    "start_slot": 8
  },
  {
    "activity_id": "A4",
    "start_slot": 6
  },
  {
    "activity_id": "A5",
    "start_slot": 2
  },
  {
    "activity_id": "A6",
    "start_slot": 0
  },
  {
    "activity_id": "A7",
    "start_slot": 2
  },
  {
    "activity_id": "A8",
    "start_slot": 4
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | SAT | gold_invalid_schedule | `null` |
| Qwen3.6 35B A3B | Solver-assisted | No | UNSAT | false_unsat | `null` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[8]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[8]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 4
    },
    {
      "activity_id": "A2",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 7
    },
    {
      "activity_id": "A4",
      "start_slot": 6
    },
    {
      "activity_id": "A5",
      "start_slot": 0
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 2
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    }
  ],
  "validation": {
    "hard_feasible": false,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": [
      {
        "activity_ids": [
          "A2",
          "A8"
        ],
        "category": "participant_overlap",
        "constraint_id": null
      },
      {
        "activity_ids": [
          "A3",
          "A4"
        ],
        "category": "participant_overlap",
        "constraint_id": null
      },
      {
        "activity_ids": [
          "A6",
          "A5"
        ],
        "category": "precedence",
        "constraint_id": "C_bg2"
      }
    ]
  },
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The returned schedule violates the evaluator's gold requirements.",
    "Gold validation found: participant_overlap, precedence."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/87db870ea95995f17e7a66ae3c6619a2d9ed282bf570129def2a7c464db4272a.json`. SHA-256: `b7a7f1089bb1ae4e6007a5f5036f31a8f0a8c0f2030ec5204335033c262726e4`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/00cd6c3f5b4e9a1b97ac31b85226ebf2537ba4965c8088e790402da1750db95d.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": {
          "activity_id": "A1",
          "slot": 4,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A2",
          "slot": 4,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A3",
          "slot": 7,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A4",
          "slot": 8,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A5",
          "slot": 4,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A6",
          "slot": 2,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A8",
          "slot": 2,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      },
      {
        "actual": {
          "activity_id": "A8",
          "slot": 4,
          "type": "deadline"
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 8,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 0,
    "structurally_equivalent": false
  },
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation.",
    "Independent validation found a concrete schedule accepted by one specification and rejected by the other, demonstrating a hard-feasibility difference on that witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/3d005cfc79ee78cfde0333691438c5eb042f0b4f7fbb9f0f2aeec7c070a82927.json`. SHA-256: `1a5dbd76c9e68b3480ace42e3a801d5929f2af4430d5e077587411198a30e80a`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/00cd6c3f5b4e9a1b97ac31b85226ebf2537ba4965c8088e790402da1750db95d.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 4
    },
    {
      "activity_id": "A2",
      "start_slot": 6
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 6
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 2
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    8
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/bf7fa30eb79f0e97ff81de42fd7d0851c217594535858e6205985d6168e86ac5.json`. SHA-256: `42e1916aba782bf732b6cb652de7860ece62533f8451c3f55a0b6b103f646c4b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/00cd6c3f5b4e9a1b97ac31b85226ebf2537ba4965c8088e790402da1750db95d.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 4
    },
    {
      "activity_id": "A2",
      "start_slot": 7
    },
    {
      "activity_id": "A3",
      "start_slot": 8
    },
    {
      "activity_id": "A4",
      "start_slot": 6
    },
    {
      "activity_id": "A5",
      "start_slot": 2
    },
    {
      "activity_id": "A6",
      "start_slot": 0
    },
    {
      "activity_id": "A7",
      "start_slot": 2
    },
    {
      "activity_id": "A8",
      "start_slot": 4
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 8,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    8
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/b064c0842aae08388a5e25f7242d7f940092b70004dadc30837d12c1f3a85286.json`. SHA-256: `581dc58e4452df6ee121542d5ac40374f4fcd9f60d6b40a24d7cd4ea51f96297`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/00cd6c3f5b4e9a1b97ac31b85226ebf2537ba4965c8088e790402da1750db95d.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## E3

**Mixed order resource · 32 activities · Reviewer: Yao Xiang.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 32 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,32) and has capacity one.
Participant P2 is available in [0,32) and has capacity one.
Participant P3 is available in [0,32) and has capacity one.
Participant P4 is available in [0,32) and has capacity one.
Participant P5 is available in [0,32) and has capacity one.
Participant P6 is available in [0,32) and has capacity one.
Participant P7 is available in [0,32) and has capacity one.
Participant P8 is available in [0,32) and has capacity one.
Resource R1 is available in [0,32) and has capacity one.
Resource R2 is available in [0,32) and has capacity one.
Resource R3 is available in [0,32) and has capacity one.
Activity A1 lasts 2 slots; participants: P4; resources: none; availability: [6,16).
Activity A13 lasts 2 slots; participants: P7; resources: R1; availability: [10,19).
Activity A26 lasts 2 slots; participants: P7; resources: none; availability: [1,9).
Activity A19 lasts 3 slots; participants: P2; resources: R3; availability: [5,10).
Activity A5 lasts 2 slots; participants: P2, P5; resources: none; availability: [0,3), [5,17).
Activity A3 lasts 2 slots; participants: P4; resources: R2; availability: [0,7).
Activity A20 lasts 2 slots; participants: P5; resources: none; availability: [0,3), [4,14).
Activity A27 lasts 2 slots; participants: P2; resources: none; availability: [0,6).
Activity A17 lasts 2 slots; participants: P3; resources: none; availability: [0,8).
Activity A12 lasts 2 slots; participants: P1; resources: R1; availability: [0,6).
Activity A24 lasts 2 slots; participants: P8; resources: R2; availability: [1,10).
Activity A30 lasts 2 slots; participants: P7; resources: none; availability: [6,17).
Activity A16 lasts 2 slots; participants: P3; resources: none; availability: [12,14).
Activity A15 lasts 2 slots; participants: P6; resources: none; availability: [4,11).
Activity A4 lasts 3 slots; participants: P1; resources: R3; availability: [9,15).
Activity A25 lasts 3 slots; participants: P8; resources: R2; availability: [1,13).
Activity A32 lasts 2 slots; participants: P2; resources: R1; availability: [0,6).
Activity A21 lasts 3 slots; participants: P8; resources: R1; availability: [6,14).
Activity A29 lasts 2 slots; participants: P3, P6; resources: R1; availability: [0,9).
Activity A31 lasts 3 slots; participants: P3; resources: none; availability: [3,12).
Activity A10 lasts 2 slots; participants: P1; resources: none; availability: [3,9).
Activity A28 lasts 2 slots; participants: P5, P6; resources: R3; availability: [0,9).
Activity A22 lasts 2 slots; participants: P7; resources: none; availability: [0,3), [7,15).
Activity A9 lasts 3 slots; participants: P1; resources: none; availability: [6,14).
Activity A6 lasts 2 slots; participants: P2, P5; resources: R2; availability: [3,13).
Activity A11 lasts 3 slots; participants: P5; resources: none; availability: [1,9).
Activity A7 lasts 3 slots; participants: P3, P6; resources: R1; availability: [1,9).
Activity A2 lasts 2 slots; participants: P1; resources: none; availability: [0,6).
Activity A8 lasts 3 slots; participants: P6; resources: R2; availability: [6,18).
Activity A23 lasts 2 slots; participants: P7; resources: R3; availability: [3,10).
Activity A14 lasts 3 slots; participants: P4; resources: none; availability: [3,10).
Activity A18 lasts 3 slots; participants: P4; resources: none; availability: [9,18).
A23 must finish before or when A20 starts.
A27 must finish before or when A26 starts.
A17 must finish before or when A13 starts.
A24 must finish before or when A22 starts.
A12 must finish before or when A2 starts.
A14 must finish before or when A1 starts.
Starting A9 outside [20,26) incurs penalty 1; starting inside incurs zero.
A2 must finish before or when A23 starts.
A28 must finish before or when A22 starts.
A29 must finish before or when A19 starts.
A32 must finish before or when A27 starts.
A27 must finish at or before slot 6.
A28 must finish before or when A19 starts.
A7 must finish before or when A31 starts.
Starting A30 outside [14,16) incurs penalty 3; starting inside incurs zero.
A6 must finish before or when A5 starts.
A25 must finish before or when A21 starts.
A28 must finish before or when A24 starts.
A27 must finish before or when A14 starts.
A28 must finish before or when A23 starts.
Starting A14 outside [26,28) incurs penalty 1; starting inside incurs zero.
A12 must finish before or when A28 starts.
Starting A10 outside [0,2) incurs penalty 2; starting inside incurs zero.
A12 must finish before or when A17 starts.
Starting A27 outside [13,17) incurs penalty 1; starting inside incurs zero.
A27 must finish before or when A4 starts.
A16 must finish at or before slot 14.
A6 must finish before or when A13 starts.
Starting A1 outside [25,31) incurs penalty 1; starting inside incurs zero.
A7 must finish before or when A30 starts.
A2 must finish before or when A29 starts.
A1 must finish before or when A8 starts.
Starting A28 outside [9,11) incurs penalty 1; starting inside incurs zero.
A23 must finish before or when A25 starts.
A1 must finish before or when A4 starts.
A2 must finish before or when A11 starts.
A7 must finish before or when A16 starts.
A20 must finish before or when A18 starts.
Starting A31 outside [25,29) incurs penalty 1; starting inside incurs zero.
A12 must finish before or when A3 starts.
A11 must finish before or when A8 starts.
Starting A15 outside [7,13) incurs penalty 3; starting inside incurs zero.
Starting A16 outside [2,8) incurs penalty 3; starting inside incurs zero.
Starting A18 outside [11,13) incurs penalty 3; starting inside incurs zero.
A25 must finish before or when A6 starts.
A13 must start exactly at slot 12.
A2 must finish at or before slot 6.
A19 must finish before or when A15 starts.
A3 must finish before or when A30 starts.
Starting A8 outside [2,6) incurs penalty 2; starting inside incurs zero.
Starting A32 outside [10,12) incurs penalty 3; starting inside incurs zero.
Starting A4 outside [0,6) incurs penalty 1; starting inside incurs zero.
A24 must finish before or when A9 starts.
A28 must finish before or when A7 starts.
Starting A19 outside [19,23) incurs penalty 2; starting inside incurs zero.
A29 must finish before or when A10 starts.
Starting A26 outside [3,7) incurs penalty 2; starting inside incurs zero.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-93645cd68c645d31d613fa2b`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 32 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 32) |
| P2 | [0, 32) |
| P3 | [0, 32) |
| P4 | [0, 32) |
| P5 | [0, 32) |
| P6 | [0, 32) |
| P7 | [0, 32) |
| P8 | [0, 32) |
| R1 | [0, 32) |
| R2 | [0, 32) |
| R3 | [0, 32) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A1 | 2 | P4 | None | [6, 16) |
| A13 | 2 | P7 | R1 | [10, 19) |
| A26 | 2 | P7 | None | [1, 9) |
| A19 | 3 | P2 | R3 | [5, 10) |
| A5 | 2 | P2, P5 | None | [0, 3), [5, 17) |
| A3 | 2 | P4 | R2 | [0, 7) |
| A20 | 2 | P5 | None | [0, 3), [4, 14) |
| A27 | 2 | P2 | None | [0, 6) |
| A17 | 2 | P3 | None | [0, 8) |
| A12 | 2 | P1 | R1 | [0, 6) |
| A24 | 2 | P8 | R2 | [1, 10) |
| A30 | 2 | P7 | None | [6, 17) |
| A16 | 2 | P3 | None | [12, 14) |
| A15 | 2 | P6 | None | [4, 11) |
| A4 | 3 | P1 | R3 | [9, 15) |
| A25 | 3 | P8 | R2 | [1, 13) |
| A32 | 2 | P2 | R1 | [0, 6) |
| A21 | 3 | P8 | R1 | [6, 14) |
| A29 | 2 | P3, P6 | R1 | [0, 9) |
| A31 | 3 | P3 | None | [3, 12) |
| A10 | 2 | P1 | None | [3, 9) |
| A28 | 2 | P5, P6 | R3 | [0, 9) |
| A22 | 2 | P7 | None | [0, 3), [7, 15) |
| A9 | 3 | P1 | None | [6, 14) |
| A6 | 2 | P2, P5 | R2 | [3, 13) |
| A11 | 3 | P5 | None | [1, 9) |
| A7 | 3 | P3, P6 | R1 | [1, 9) |
| A2 | 2 | P1 | None | [0, 6) |
| A8 | 3 | P6 | R2 | [6, 18) |
| A23 | 2 | P7 | R3 | [3, 10) |
| A14 | 3 | P4 | None | [3, 10) |
| A18 | 3 | P4 | None | [9, 18) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"after":"A20","before":"A23","id":"C_bg20","type":"precedence"}`
- `{"after":"A26","before":"A27","id":"C_bg17","type":"precedence"}`
- `{"after":"A13","before":"A17","id":"C_extra30","type":"precedence"}`
- `{"after":"A22","before":"A24","id":"C_bg24","type":"precedence"}`
- `{"after":"A2","before":"A12","id":"C0","type":"precedence"}`
- `{"after":"A1","before":"A14","id":"C_bg11","type":"precedence"}`
- `{"activity_id":"A9","end":26,"id":"PREF23","start":20,"type":"preferred_start","weight":1}`
- `{"after":"A23","before":"A2","id":"C_extra6","type":"precedence"}`
- `{"after":"A22","before":"A28","id":"C_extra24","type":"precedence"}`
- `{"after":"A19","before":"A29","id":"C_bg9","type":"precedence"}`
- `{"after":"A27","before":"A32","id":"C1","type":"precedence"}`
- `{"activity_id":"A27","id":"C3","slot":6,"type":"deadline"}`
- `{"after":"A19","before":"A28","id":"C_extra9","type":"precedence"}`
- `{"after":"A31","before":"A7","id":"C_bg25","type":"precedence"}`
- `{"activity_id":"A30","end":16,"id":"PREF27","start":14,"type":"preferred_start","weight":3}`
- `{"after":"A5","before":"A6","id":"C_bg28","type":"precedence"}`
- `{"after":"A21","before":"A25","id":"C_bg22","type":"precedence"}`
- `{"after":"A24","before":"A28","id":"C_bg10","type":"precedence"}`
- `{"after":"A14","before":"A27","id":"C_bg7","type":"precedence"}`
- `{"after":"A23","before":"A28","id":"C_bg6","type":"precedence"}`
- `{"activity_id":"A14","end":28,"id":"PREF7","start":26,"type":"preferred_start","weight":1}`
- `{"after":"A28","before":"A12","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A10","end":2,"id":"PREF13","start":0,"type":"preferred_start","weight":2}`
- `{"after":"A17","before":"A12","id":"C_bg12","type":"precedence"}`
- `{"activity_id":"A27","end":17,"id":"PREF3","start":13,"type":"preferred_start","weight":1}`
- `{"after":"A4","before":"A27","id":"C_extra15","type":"precedence"}`
- `{"activity_id":"A16","id":"C_profile_deadline","slot":14,"type":"deadline"}`
- `{"after":"A13","before":"A6","id":"C_bg30","type":"precedence"}`
- `{"activity_id":"A1","end":31,"id":"PREF11","start":25,"type":"preferred_start","weight":1}`
- `{"after":"A30","before":"A7","id":"C_bg27","type":"precedence"}`
- `{"after":"A29","before":"A2","id":"C_bg4","type":"precedence"}`
- `{"after":"A8","before":"A1","id":"C_bg21","type":"precedence"}`
- `{"activity_id":"A28","end":11,"id":"PREF5","start":9,"type":"preferred_start","weight":1}`
- `{"after":"A25","before":"A23","id":"C_bg8","type":"precedence"}`
- `{"after":"A4","before":"A1","id":"C_bg15","type":"precedence"}`
- `{"after":"A11","before":"A2","id":"C_bg14","type":"precedence"}`
- `{"after":"A16","before":"A7","id":"C_bg31","type":"precedence"}`
- `{"after":"A18","before":"A20","id":"C_bg29","type":"precedence"}`
- `{"activity_id":"A31","end":29,"id":"PREF25","start":25,"type":"preferred_start","weight":1}`
- `{"after":"A3","before":"A12","id":"C_bg18","type":"precedence"}`
- `{"after":"A8","before":"A11","id":"C_extra21","type":"precedence"}`
- `{"activity_id":"A15","end":13,"id":"PREF19","start":7,"type":"preferred_start","weight":3}`
- `{"activity_id":"A16","end":8,"id":"PREF31","start":2,"type":"preferred_start","weight":3}`
- `{"activity_id":"A18","end":13,"id":"PREF29","start":11,"type":"preferred_start","weight":3}`
- `{"after":"A6","before":"A25","id":"C_bg26","type":"precedence"}`
- `{"activity_id":"A13","id":"C_profile_fixed","slot":12,"type":"fixed_start"}`
- `{"activity_id":"A2","id":"C2","slot":6,"type":"deadline"}`
- `{"after":"A15","before":"A19","id":"C_bg19","type":"precedence"}`
- `{"after":"A30","before":"A3","id":"C_extra27","type":"precedence"}`
- `{"activity_id":"A8","end":6,"id":"PREF21","start":2,"type":"preferred_start","weight":2}`
- `{"activity_id":"A32","end":12,"id":"PREF1","start":10,"type":"preferred_start","weight":3}`
- `{"activity_id":"A4","end":6,"id":"PREF15","start":0,"type":"preferred_start","weight":1}`
- `{"after":"A9","before":"A24","id":"C_bg23","type":"precedence"}`
- `{"after":"A7","before":"A28","id":"C_bg16","type":"precedence"}`
- `{"activity_id":"A19","end":23,"id":"PREF9","start":19,"type":"preferred_start","weight":2}`
- `{"after":"A10","before":"A29","id":"C_bg13","type":"precedence"}`
- `{"activity_id":"A26","end":7,"id":"PREF17","start":3,"type":"preferred_start","weight":2}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":19,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 9
  },
  {
    "activity_id": "A10",
    "start_slot": 6
  },
  {
    "activity_id": "A11",
    "start_slot": 4
  },
  {
    "activity_id": "A12",
    "start_slot": 0
  },
  {
    "activity_id": "A13",
    "start_slot": 12
  },
  {
    "activity_id": "A14",
    "start_slot": 6
  },
  {
    "activity_id": "A15",
    "start_slot": 9
  },
  {
    "activity_id": "A16",
    "start_slot": 12
  },
  {
    "activity_id": "A17",
    "start_slot": 2
  },
  {
    "activity_id": "A18",
    "start_slot": 11
  },
  {
    "activity_id": "A19",
    "start_slot": 6
  },
  {
    "activity_id": "A2",
    "start_slot": 2
  },
  {
    "activity_id": "A20",
    "start_slot": 7
  },
  {
    "activity_id": "A21",
    "start_slot": 9
  },
  {
    "activity_id": "A22",
    "start_slot": 8
  },
  {
    "activity_id": "A23",
    "start_slot": 4
  },
  {
    "activity_id": "A24",
    "start_slot": 4
  },
  {
    "activity_id": "A25",
    "start_slot": 6
  },
  {
    "activity_id": "A26",
    "start_slot": 6
  },
  {
    "activity_id": "A27",
    "start_slot": 4
  },
  {
    "activity_id": "A28",
    "start_slot": 2
  },
  {
    "activity_id": "A29",
    "start_slot": 4
  },
  {
    "activity_id": "A3",
    "start_slot": 2
  },
  {
    "activity_id": "A30",
    "start_slot": 14
  },
  {
    "activity_id": "A31",
    "start_slot": 9
  },
  {
    "activity_id": "A32",
    "start_slot": 2
  },
  {
    "activity_id": "A4",
    "start_slot": 12
  },
  {
    "activity_id": "A5",
    "start_slot": 11
  },
  {
    "activity_id": "A6",
    "start_slot": 9
  },
  {
    "activity_id": "A7",
    "start_slot": 6
  },
  {
    "activity_id": "A8",
    "start_slot": 11
  },
  {
    "activity_id": "A9",
    "start_slot": 8
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | UNSAT | false_unsat | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[19]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[19]` |
| GLM5.3 Flash | Solver-assisted | No | SAT | gold_invalid_schedule | `null` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "UNSAT was returned for a gold problem with a validated feasible witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/75c31f67f2af5095ebb9f752cd96789f3b1ac759078d9feb1fadc29448d22388.json`. SHA-256: `fd5a90655461d7b78bbc8d68fff134fa685e9c8ff9d5797f3712543d4fbc67dc`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2f26287e2dd92edbbac8f9d7418369ec4d77def7b01515d4f5660cbe8edf7bac.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 9
    },
    {
      "activity_id": "A10",
      "start_slot": 6
    },
    {
      "activity_id": "A11",
      "start_slot": 4
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A13",
      "start_slot": 12
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 9
    },
    {
      "activity_id": "A16",
      "start_slot": 12
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 11
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 2
    },
    {
      "activity_id": "A20",
      "start_slot": 7
    },
    {
      "activity_id": "A21",
      "start_slot": 9
    },
    {
      "activity_id": "A22",
      "start_slot": 8
    },
    {
      "activity_id": "A23",
      "start_slot": 4
    },
    {
      "activity_id": "A24",
      "start_slot": 4
    },
    {
      "activity_id": "A25",
      "start_slot": 6
    },
    {
      "activity_id": "A26",
      "start_slot": 6
    },
    {
      "activity_id": "A27",
      "start_slot": 4
    },
    {
      "activity_id": "A28",
      "start_slot": 2
    },
    {
      "activity_id": "A29",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A30",
      "start_slot": 14
    },
    {
      "activity_id": "A31",
      "start_slot": 9
    },
    {
      "activity_id": "A32",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 12
    },
    {
      "activity_id": "A5",
      "start_slot": 11
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 8
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 19,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    19
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/786103142c3c7cc9004cf4d4a5861285e39a6b074926a8983f3d001e549b6f7f.json`. SHA-256: `237f5734f748b79a02757196c388a63f9bc3284614b28ba1f417a4bc733ba44c`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2f26287e2dd92edbbac8f9d7418369ec4d77def7b01515d4f5660cbe8edf7bac.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 9
    },
    {
      "activity_id": "A10",
      "start_slot": 6
    },
    {
      "activity_id": "A11",
      "start_slot": 4
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A13",
      "start_slot": 12
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 9
    },
    {
      "activity_id": "A16",
      "start_slot": 12
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 12
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 2
    },
    {
      "activity_id": "A20",
      "start_slot": 7
    },
    {
      "activity_id": "A21",
      "start_slot": 9
    },
    {
      "activity_id": "A22",
      "start_slot": 8
    },
    {
      "activity_id": "A23",
      "start_slot": 4
    },
    {
      "activity_id": "A24",
      "start_slot": 4
    },
    {
      "activity_id": "A25",
      "start_slot": 6
    },
    {
      "activity_id": "A26",
      "start_slot": 6
    },
    {
      "activity_id": "A27",
      "start_slot": 4
    },
    {
      "activity_id": "A28",
      "start_slot": 2
    },
    {
      "activity_id": "A29",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A30",
      "start_slot": 14
    },
    {
      "activity_id": "A31",
      "start_slot": 9
    },
    {
      "activity_id": "A32",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 12
    },
    {
      "activity_id": "A5",
      "start_slot": 11
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 14
    },
    {
      "activity_id": "A9",
      "start_slot": 8
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 19,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    19
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/043aaff3aa32ea485326f6ab9be08c6108d78cddf4414897cc004db5faa7c29f.json`. SHA-256: `7ebce6a2a34c91adc7f04a5def2cd0924fe71f892a62a032281ce2892a7fa20b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2f26287e2dd92edbbac8f9d7418369ec4d77def7b01515d4f5660cbe8edf7bac.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 9
    },
    {
      "activity_id": "A10",
      "start_slot": 4
    },
    {
      "activity_id": "A11",
      "start_slot": 4
    },
    {
      "activity_id": "A12",
      "start_slot": 0
    },
    {
      "activity_id": "A13",
      "start_slot": 12
    },
    {
      "activity_id": "A14",
      "start_slot": 6
    },
    {
      "activity_id": "A15",
      "start_slot": 9
    },
    {
      "activity_id": "A16",
      "start_slot": 12
    },
    {
      "activity_id": "A17",
      "start_slot": 2
    },
    {
      "activity_id": "A18",
      "start_slot": 11
    },
    {
      "activity_id": "A19",
      "start_slot": 6
    },
    {
      "activity_id": "A2",
      "start_slot": 2
    },
    {
      "activity_id": "A20",
      "start_slot": 7
    },
    {
      "activity_id": "A21",
      "start_slot": 9
    },
    {
      "activity_id": "A22",
      "start_slot": 8
    },
    {
      "activity_id": "A23",
      "start_slot": 4
    },
    {
      "activity_id": "A24",
      "start_slot": 4
    },
    {
      "activity_id": "A25",
      "start_slot": 6
    },
    {
      "activity_id": "A26",
      "start_slot": 6
    },
    {
      "activity_id": "A27",
      "start_slot": 4
    },
    {
      "activity_id": "A28",
      "start_slot": 2
    },
    {
      "activity_id": "A29",
      "start_slot": 4
    },
    {
      "activity_id": "A3",
      "start_slot": 2
    },
    {
      "activity_id": "A30",
      "start_slot": 14
    },
    {
      "activity_id": "A31",
      "start_slot": 9
    },
    {
      "activity_id": "A32",
      "start_slot": 2
    },
    {
      "activity_id": "A4",
      "start_slot": 12
    },
    {
      "activity_id": "A5",
      "start_slot": 11
    },
    {
      "activity_id": "A6",
      "start_slot": 9
    },
    {
      "activity_id": "A7",
      "start_slot": 6
    },
    {
      "activity_id": "A8",
      "start_slot": 11
    },
    {
      "activity_id": "A9",
      "start_slot": 6
    }
  ],
  "validation": {
    "hard_feasible": false,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 19,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": [
      {
        "activity_ids": [
          "A29",
          "A10"
        ],
        "category": "precedence",
        "constraint_id": "C_bg13"
      }
    ]
  },
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": null,
        "count": 1,
        "expected": {
          "activity_id": "A2",
          "slot": 6,
          "type": "deadline"
        },
        "kind": "omitted"
      },
      {
        "actual": null,
        "count": 1,
        "expected": {
          "after": "A10",
          "before": "A29",
          "type": "precedence"
        },
        "kind": "omitted"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 2,
    "structurally_equivalent": false
  },
  "observations": [
    "The returned schedule violates the evaluator's gold requirements.",
    "Gold validation found: precedence.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation.",
    "Independent validation found a concrete schedule accepted by one specification and rejected by the other, demonstrating a hard-feasibility difference on that witness."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/d4253d4cc1258632f7a50be19c224e354e7c37e5824dd279ef47b234e6e3b69d.json`. SHA-256: `998477b6f31872ad4e39b3f9e7c50b8372a60e0124b495e0b106ee04b983641b`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/2f26287e2dd92edbbac8f9d7418369ec4d77def7b01515d4f5660cbe8edf7bac.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)

## E4

**Release deadline chain · 24 activities · Reviewer: Yong Qing.**

### Original request

```text
Schedule every activity exactly once. Slot zero is 2026-10-26T07:00:00+08:00, timezone +08:00. There are 28 slots of 30 minutes. All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply.
Participant P1 is available in [0,28) and has capacity one.
Participant P2 is available in [0,28) and has capacity one.
Participant P3 is available in [0,28) and has capacity one.
Participant P4 is available in [0,28) and has capacity one.
Participant P5 is available in [0,28) and has capacity one.
Participant P6 is available in [0,28) and has capacity one.
Resource R1 is available in [0,28) and has capacity one.
Resource R2 is available in [0,28) and has capacity one.
Activity A20 lasts 2 slots; participants: P6; resources: R2; availability: [5,15).
Activity A9 lasts 3 slots; participants: P5; resources: R2; availability: [8,20).
Activity A7 lasts 2 slots; participants: P2; resources: none; availability: [9,15).
Activity A12 lasts 3 slots; participants: P3; resources: R2; availability: [4,9).
Activity A6 lasts 3 slots; participants: P2; resources: R1; availability: [12,22).
Activity A1 lasts 2 slots; participants: P3; resources: none; availability: [10,20).
Activity A16 lasts 2 slots; participants: P5; resources: none; availability: [12,18).
Activity A10 lasts 2 slots; participants: P1, P4; resources: R1; availability: [0,3), [6,14).
Activity A22 lasts 2 slots; participants: P2; resources: R1; availability: [0,3), [4,9).
Activity A5 lasts 2 slots; participants: P2; resources: none; availability: [1,12).
Activity A19 lasts 3 slots; participants: P3; resources: none; availability: [16,20).
Activity A23 lasts 2 slots; participants: P2; resources: none; availability: [1,12).
Activity A11 lasts 3 slots; participants: P1; resources: none; availability: [1,12).
Activity A4 lasts 2 slots; participants: P5, P6; resources: none; availability: [6,16).
Activity A13 lasts 2 slots; participants: P6; resources: none; availability: [0,3), [9,15).
Activity A24 lasts 2 slots; participants: P1, P4; resources: none; availability: [10,18).
Activity A21 lasts 2 slots; participants: P1, P6; resources: R2; availability: [0,3), [11,23).
Activity A18 lasts 2 slots; participants: P3; resources: none; availability: [10,18).
Activity A8 lasts 3 slots; participants: P4; resources: none; availability: [10,23).
Activity A2 lasts 2 slots; participants: P2; resources: R2; availability: [0,3), [6,18).
Activity A14 lasts 3 slots; participants: P3; resources: none; availability: [5,15).
Activity A17 lasts 2 slots; participants: P5; resources: none; availability: [6,16).
Activity A15 lasts 3 slots; participants: P1; resources: none; availability: [1,12).
Activity A3 lasts 2 slots; participants: P1, P4; resources: R1; availability: [12,19).
Starting A19 outside [21,27) incurs penalty 3; starting inside incurs zero.
A11 must finish before or when A20 starts.
A15 must finish before or when A5 starts.
A12 must finish before or when A9 starts.
A11 must finish before or when A14 starts.
A4 must finish before or when A8 starts.
A4 must finish before or when A3 starts.
A23 must finish at or before slot 11.
A15 must start at or after slot 1.
Starting A12 outside [16,20) incurs penalty 3; starting inside incurs zero.
A2 must finish before or when A1 starts.
A5 must finish before or when A11 starts.
A23 must finish before or when A2 starts.
A15 must finish before or when A22 starts.
A5 must finish at or before slot 6.
A2 must finish before or when A8 starts.
Starting A1 outside [7,9) incurs penalty 3; starting inside incurs zero.
Starting A2 outside [22,28) incurs penalty 3; starting inside incurs zero.
A5 must finish before or when A22 starts.
A22 must finish before or when A24 starts.
A2 must finish before or when A6 starts.
A24 must finish before or when A1 starts.
A11 must finish before or when A18 starts.
A5 must finish before or when A12 starts.
Starting A15 outside [17,23) incurs penalty 3; starting inside incurs zero.
Starting A11 outside [16,20) incurs penalty 3; starting inside incurs zero.
A4 must finish before or when A7 starts.
A11 must finish before or when A17 starts.
Starting A14 outside [5,9) incurs penalty 3; starting inside incurs zero.
Starting A21 outside [16,18) incurs penalty 3; starting inside incurs zero.
A11 must finish before or when A10 starts.
A20 must finish before or when A19 starts.
A9 must finish before or when A21 starts.
Starting A18 outside [23,25) incurs penalty 3; starting inside incurs zero.
A14 must finish before or when A9 starts.
Starting A22 outside [9,11) incurs penalty 2; starting inside incurs zero.
A15 must finish before or when A14 starts.
A7 must finish before or when A16 starts.
Starting A13 outside [1,3) incurs penalty 1; starting inside incurs zero.
A23 must finish before or when A13 starts.
A17 must finish before or when A4 starts.
A11 must finish before or when A23 starts.
Starting A10 outside [2,8) incurs penalty 3; starting inside incurs zero.
A10 must finish before or when A3 starts.
Minimize the total preference penalty subject to all hard requirements.
```

**Before opening the evidence:** identify the hard constraints and preferences, decide whether a schedule seems possible, and record one reason. Uncertainty is an acceptable review finding.

<details>
<summary>Gold specification, reference result and recorded outputs — open after your own interpretation</summary>

Case ID: `dg-a7542bcaf35f7024ab973f3c`. Gold label: **SAT**. Horizon: `2026-10-26T07:00:00+08:00`; timezone `+08:00`; 28 slots of 30 minutes. All activities are mandatory and all shared entities have capacity one.

**Gold availability and activities**

| Entity | Availability (slots) |
| --- | --- |
| P1 | [0, 28) |
| P2 | [0, 28) |
| P3 | [0, 28) |
| P4 | [0, 28) |
| P5 | [0, 28) |
| P6 | [0, 28) |
| R1 | [0, 28) |
| R2 | [0, 28) |

| Activity | Duration (slots) | Participants | Resources | Availability (slots) |
| --- | ---: | --- | --- | --- |
| A20 | 2 | P6 | R2 | [5, 15) |
| A9 | 3 | P5 | R2 | [8, 20) |
| A7 | 2 | P2 | None | [9, 15) |
| A12 | 3 | P3 | R2 | [4, 9) |
| A6 | 3 | P2 | R1 | [12, 22) |
| A1 | 2 | P3 | None | [10, 20) |
| A16 | 2 | P5 | None | [12, 18) |
| A10 | 2 | P1, P4 | R1 | [0, 3), [6, 14) |
| A22 | 2 | P2 | R1 | [0, 3), [4, 9) |
| A5 | 2 | P2 | None | [1, 12) |
| A19 | 3 | P3 | None | [16, 20) |
| A23 | 2 | P2 | None | [1, 12) |
| A11 | 3 | P1 | None | [1, 12) |
| A4 | 2 | P5, P6 | None | [6, 16) |
| A13 | 2 | P6 | None | [0, 3), [9, 15) |
| A24 | 2 | P1, P4 | None | [10, 18) |
| A21 | 2 | P1, P6 | R2 | [0, 3), [11, 23) |
| A18 | 2 | P3 | None | [10, 18) |
| A8 | 3 | P4 | None | [10, 23) |
| A2 | 2 | P2 | R2 | [0, 3), [6, 18) |
| A14 | 3 | P3 | None | [5, 15) |
| A17 | 2 | P5 | None | [6, 16) |
| A15 | 3 | P1 | None | [1, 12) |
| A3 | 2 | P1, P4 | R1 | [12, 19) |

**Gold constraint records** — `preferred_start` is soft; all other listed constraints are hard.

- `{"activity_id":"A19","end":27,"id":"PREF22","start":21,"type":"preferred_start","weight":3}`
- `{"after":"A20","before":"A11","id":"C_bg11","type":"precedence"}`
- `{"after":"A5","before":"A15","id":"C0","type":"precedence"}`
- `{"after":"A9","before":"A12","id":"C_bg15","type":"precedence"}`
- `{"after":"A14","before":"A11","id":"C_bg6","type":"precedence"}`
- `{"after":"A8","before":"A4","id":"C_extra21","type":"precedence"}`
- `{"after":"A3","before":"A4","id":"C_bg9","type":"precedence"}`
- `{"activity_id":"A23","id":"C_end","slot":11,"type":"deadline"}`
- `{"activity_id":"A15","id":"C_release","slot":1,"type":"release"}`
- `{"activity_id":"A12","end":20,"id":"PREF10","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A1","before":"A2","id":"C_extra18","type":"precedence"}`
- `{"after":"A11","before":"A5","id":"C1","type":"precedence"}`
- `{"after":"A2","before":"A23","id":"C_bg8","type":"precedence"}`
- `{"after":"A22","before":"A15","id":"C_extra12","type":"precedence"}`
- `{"activity_id":"A5","id":"C_mid","slot":6,"type":"deadline"}`
- `{"after":"A8","before":"A2","id":"C_bg21","type":"precedence"}`
- `{"activity_id":"A1","end":9,"id":"PREF18","start":7,"type":"preferred_start","weight":3}`
- `{"activity_id":"A2","end":28,"id":"PREF8","start":22,"type":"preferred_start","weight":3}`
- `{"after":"A22","before":"A5","id":"C_bg12","type":"precedence"}`
- `{"after":"A24","before":"A22","id":"C_bg13","type":"precedence"}`
- `{"after":"A6","before":"A2","id":"C_bg19","type":"precedence"}`
- `{"after":"A1","before":"A24","id":"C_bg18","type":"precedence"}`
- `{"after":"A18","before":"A11","id":"C_bg14","type":"precedence"}`
- `{"after":"A12","before":"A5","id":"C_bg10","type":"precedence"}`
- `{"activity_id":"A15","end":23,"id":"PREF0","start":17,"type":"preferred_start","weight":3}`
- `{"activity_id":"A11","end":20,"id":"PREF2","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A7","before":"A4","id":"C_bg17","type":"precedence"}`
- `{"after":"A17","before":"A11","id":"C_bg5","type":"precedence"}`
- `{"activity_id":"A14","end":9,"id":"PREF6","start":5,"type":"preferred_start","weight":3}`
- `{"activity_id":"A21","end":18,"id":"PREF20","start":16,"type":"preferred_start","weight":3}`
- `{"after":"A10","before":"A11","id":"C_bg4","type":"precedence"}`
- `{"after":"A19","before":"A20","id":"C_bg22","type":"precedence"}`
- `{"after":"A21","before":"A9","id":"C_bg20","type":"precedence"}`
- `{"activity_id":"A18","end":25,"id":"PREF14","start":23,"type":"preferred_start","weight":3}`
- `{"after":"A9","before":"A14","id":"C_extra15","type":"precedence"}`
- `{"activity_id":"A22","end":11,"id":"PREF12","start":9,"type":"preferred_start","weight":2}`
- `{"after":"A14","before":"A15","id":"C_extra6","type":"precedence"}`
- `{"after":"A16","before":"A7","id":"C_bg23","type":"precedence"}`
- `{"activity_id":"A13","end":3,"id":"PREF16","start":1,"type":"preferred_start","weight":1}`
- `{"after":"A13","before":"A23","id":"C_bg16","type":"precedence"}`
- `{"after":"A4","before":"A17","id":"C_bg7","type":"precedence"}`
- `{"after":"A23","before":"A11","id":"C2","type":"precedence"}`
- `{"activity_id":"A10","end":8,"id":"PREF4","start":2,"type":"preferred_start","weight":3}`
- `{"after":"A3","before":"A10","id":"C_extra9","type":"precedence"}`

**Saved reference:** `OPTIMAL`; objective values `{"moved_count":null,"preference_penalty":30,"total_shift_slots":null}`. The reference shares CP-SAT/compiler code with the solver-assisted method: do not treat it as fully independent objective verification.

**Construction witness** (not necessarily the preference-optimal schedule):
```json
[
  {
    "activity_id": "A1",
    "start_slot": 14
  },
  {
    "activity_id": "A10",
    "start_slot": 9
  },
  {
    "activity_id": "A11",
    "start_slot": 6
  },
  {
    "activity_id": "A12",
    "start_slot": 6
  },
  {
    "activity_id": "A13",
    "start_slot": 13
  },
  {
    "activity_id": "A14",
    "start_slot": 9
  },
  {
    "activity_id": "A15",
    "start_slot": 1
  },
  {
    "activity_id": "A16",
    "start_slot": 16
  },
  {
    "activity_id": "A17",
    "start_slot": 9
  },
  {
    "activity_id": "A18",
    "start_slot": 12
  },
  {
    "activity_id": "A19",
    "start_slot": 17
  },
  {
    "activity_id": "A2",
    "start_slot": 11
  },
  {
    "activity_id": "A20",
    "start_slot": 9
  },
  {
    "activity_id": "A21",
    "start_slot": 16
  },
  {
    "activity_id": "A22",
    "start_slot": 6
  },
  {
    "activity_id": "A23",
    "start_slot": 9
  },
  {
    "activity_id": "A24",
    "start_slot": 11
  },
  {
    "activity_id": "A3",
    "start_slot": 13
  },
  {
    "activity_id": "A4",
    "start_slot": 11
  },
  {
    "activity_id": "A5",
    "start_slot": 4
  },
  {
    "activity_id": "A6",
    "start_slot": 15
  },
  {
    "activity_id": "A7",
    "start_slot": 13
  },
  {
    "activity_id": "A8",
    "start_slot": 15
  },
  {
    "activity_id": "A9",
    "start_slot": 13
  }
]
```

**Recorded outcomes**

| Model | Method | Accepted | Pipeline status | Recorded category | Objective values |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6 35B A3B | Direct | No | ERROR | provider_error | `null` |
| Qwen3.6 35B A3B | Solver-assisted | Yes | SAT | accepted | `[30]` |
| GLM5.3 Flash | Direct | Yes | SAT | accepted | `[33]` |
| GLM5.3 Flash | Solver-assisted | Yes | SAT | accepted | `[30]` |

Acceptance means a gold-valid schedule or a correct infeasibility answer; it does not by itself mean preference-optimal. Read errors as recorded: provider failures are not scheduling mistakes. Structural extraction differences alone do not prove a semantic error.

<details><summary>Qwen3.6 35B A3B — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": null,
  "validation": null,
  "objective_values": null,
  "objective_gaps": [
    null
  ],
  "extraction_comparison": null,
  "observations": [
    "The provider attempt failed; this is not evidence of a reasoning failure."
  ],
  "provider_error": "http_502"
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/a47255243c634d067b04d85371e44533ffe62018b51c881bdf8db799fd97786c.json`. SHA-256: `2e12297c92f4e0f5f0668671e93c7d6bcdf3bda30db5cf76a9b4860fe684a1d2`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/82e5321be2b5817f3303b9af5192e1379ac28652cee181f10e954bac53c6bbf1.json`.

</details>

<details><summary>Qwen3.6 35B A3B — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 9
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 13
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 1
    },
    {
      "activity_id": "A16",
      "start_slot": 16
    },
    {
      "activity_id": "A17",
      "start_slot": 9
    },
    {
      "activity_id": "A18",
      "start_slot": 12
    },
    {
      "activity_id": "A19",
      "start_slot": 17
    },
    {
      "activity_id": "A2",
      "start_slot": 11
    },
    {
      "activity_id": "A20",
      "start_slot": 9
    },
    {
      "activity_id": "A21",
      "start_slot": 16
    },
    {
      "activity_id": "A22",
      "start_slot": 6
    },
    {
      "activity_id": "A23",
      "start_slot": 9
    },
    {
      "activity_id": "A24",
      "start_slot": 11
    },
    {
      "activity_id": "A3",
      "start_slot": 13
    },
    {
      "activity_id": "A4",
      "start_slot": 11
    },
    {
      "activity_id": "A5",
      "start_slot": 4
    },
    {
      "activity_id": "A6",
      "start_slot": 15
    },
    {
      "activity_id": "A7",
      "start_slot": 13
    },
    {
      "activity_id": "A8",
      "start_slot": 15
    },
    {
      "activity_id": "A9",
      "start_slot": 13
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 30,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    30
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [
      {
        "actual": null,
        "count": 1,
        "expected": {
          "activity_id": "A15",
          "slot": 1,
          "type": "release"
        },
        "kind": "omitted"
      },
      {
        "actual": {
          "activity_id": "A15",
          "end": 12,
          "start": 1,
          "type": "preferred_start",
          "weight": 0
        },
        "count": 1,
        "expected": null,
        "kind": "invented"
      }
    ],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 1,
    "mismatches": [
      "constraints"
    ],
    "omitted_constraints": 1,
    "structurally_equivalent": false
  },
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The extracted specification differs structurally from gold. This alone does not prove semantic error or causation."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-qwen36-20261018-portable.tar.gz](../../results/archives/diverse-2000-qwen36-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/c1d7869f29dd8bd5ae009b56229f3ad6870822d3e5e756e58186103462dbba69.json`. SHA-256: `325d2947d2a4106fdb9115ddcc740cfe7c3d464d0a58c93cdefcfac6fab60c38`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/82e5321be2b5817f3303b9af5192e1379ac28652cee181f10e954bac53c6bbf1.json`.

</details>

<details><summary>GLM5.3 Flash — Direct: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 9
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 13
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 1
    },
    {
      "activity_id": "A16",
      "start_slot": 15
    },
    {
      "activity_id": "A17",
      "start_slot": 9
    },
    {
      "activity_id": "A18",
      "start_slot": 12
    },
    {
      "activity_id": "A19",
      "start_slot": 16
    },
    {
      "activity_id": "A2",
      "start_slot": 11
    },
    {
      "activity_id": "A20",
      "start_slot": 9
    },
    {
      "activity_id": "A21",
      "start_slot": 20
    },
    {
      "activity_id": "A22",
      "start_slot": 7
    },
    {
      "activity_id": "A23",
      "start_slot": 9
    },
    {
      "activity_id": "A24",
      "start_slot": 11
    },
    {
      "activity_id": "A3",
      "start_slot": 13
    },
    {
      "activity_id": "A4",
      "start_slot": 11
    },
    {
      "activity_id": "A5",
      "start_slot": 4
    },
    {
      "activity_id": "A6",
      "start_slot": 15
    },
    {
      "activity_id": "A7",
      "start_slot": 13
    },
    {
      "activity_id": "A8",
      "start_slot": 15
    },
    {
      "activity_id": "A9",
      "start_slot": 17
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 33,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    33
  ],
  "objective_gaps": [
    3
  ],
  "extraction_comparison": null,
  "observations": [
    "The answer met the primary gold acceptance criterion.",
    "The valid schedule is worse at a proven comparable objective stage; primary acceptance is unchanged."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/4ffbbe48c36b04daae820c2d14b4bedd54de33e7e6b17caadfbb066f337f8002.json`. SHA-256: `fd42fc1f167a65c12c5e46878c134d7cead7c912a951813c30929a7fad624177`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/82e5321be2b5817f3303b9af5192e1379ac28652cee181f10e954bac53c6bbf1.json`.

</details>

<details><summary>GLM5.3 Flash — Solver-assisted: schedule and diagnostics</summary>

```json
{
  "schedule": [
    {
      "activity_id": "A1",
      "start_slot": 14
    },
    {
      "activity_id": "A10",
      "start_slot": 9
    },
    {
      "activity_id": "A11",
      "start_slot": 6
    },
    {
      "activity_id": "A12",
      "start_slot": 6
    },
    {
      "activity_id": "A13",
      "start_slot": 13
    },
    {
      "activity_id": "A14",
      "start_slot": 9
    },
    {
      "activity_id": "A15",
      "start_slot": 1
    },
    {
      "activity_id": "A16",
      "start_slot": 16
    },
    {
      "activity_id": "A17",
      "start_slot": 9
    },
    {
      "activity_id": "A18",
      "start_slot": 12
    },
    {
      "activity_id": "A19",
      "start_slot": 17
    },
    {
      "activity_id": "A2",
      "start_slot": 11
    },
    {
      "activity_id": "A20",
      "start_slot": 9
    },
    {
      "activity_id": "A21",
      "start_slot": 16
    },
    {
      "activity_id": "A22",
      "start_slot": 6
    },
    {
      "activity_id": "A23",
      "start_slot": 9
    },
    {
      "activity_id": "A24",
      "start_slot": 11
    },
    {
      "activity_id": "A3",
      "start_slot": 13
    },
    {
      "activity_id": "A4",
      "start_slot": 11
    },
    {
      "activity_id": "A5",
      "start_slot": 4
    },
    {
      "activity_id": "A6",
      "start_slot": 15
    },
    {
      "activity_id": "A7",
      "start_slot": 13
    },
    {
      "activity_id": "A8",
      "start_slot": 15
    },
    {
      "activity_id": "A9",
      "start_slot": 13
    }
  ],
  "validation": {
    "hard_feasible": true,
    "objectives": {
      "moved_count": null,
      "preference_penalty": 30,
      "total_shift_slots": null
    },
    "structural_valid": true,
    "violations": []
  },
  "objective_values": [
    30
  ],
  "objective_gaps": [
    0
  ],
  "extraction_comparison": {
    "constraint_differences": [],
    "differences": [],
    "format_version": "2.0",
    "invented_constraints": 0,
    "mismatches": [],
    "omitted_constraints": 0,
    "structurally_equivalent": true
  },
  "observations": [
    "The answer met the primary gold acceptance criterion."
  ],
  "provider_error": null
}
```

Original archive: [diverse-2000-glm53flash-20261018-portable.tar.gz](../../results/archives/diverse-2000-glm53flash-20261018-portable.tar.gz). Member: `runs/controlled/controlled/attempts/b6ea19588ac249f4ef619a55792ca56d742bbb234a1b5d01fa5ea43c9e5dde83.json`. SHA-256: `b07a0c58ba1cd4b9fa06ce87c3dd5463dfed4314378202312507f35802ed963d`. Full model response and extracted specification remain in that member. Reference member: `runs/controlled/controlled/references/82e5321be2b5817f3303b9af5192e1379ac28652cee181f10e954bac53c6bbf1.json`.

</details>

</details>

[Return to checklist](../process/human-review-checklist.md)
