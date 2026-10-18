# Fictional scheduling drafts for human review

These twelve scenarios were drafted with Codex at Yong Qing’s request. They are **AI-assisted development drafts**, not independently human-written cases or reviewed evaluation data. Gold specifications are in `benchmarks/fixtures/realistic-drafts-v1.json`; references, rationale and review status remain evaluator-only. No live model run is authorized by this packet.

A reviewer should first interpret each public scenario, then compare the gold specification, witness or contradiction, objectives and original repair context. Record ambiguity corrections in a new version; do not mark approval without an actual review.

## realistic-draft-01: Shared media studio

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 8 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

A small media club has one recording booth R0. Mira (P0) and Devon (P1), as well as the booth, are available throughout [0,8). Mira needs two slots to record A0 in the booth and one slot afterward to edit A2 at a desk; editing does not use the booth. Devon has a two-slot booth interview A1 that must start at slot 2. All three activities may otherwise take place within [0,8). Recording A0 must finish before editing A2 begins. Starting A0 outside [0,1) costs 3 preference points; starting A2 outside [4,5) costs 2. There are no other preferences.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 9 feasible assignments; optimum (0,). Human prose/gold review pending.

## realistic-draft-02: Shared laboratory instrument

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 4 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

Three students P0, P1 and P2 each need the same measurement instrument R0 for a separate two-slot experiment: A0 belongs to P0, A1 to P1 and A2 to P2. The students and instrument are available only during [0,4), and each experiment must also fit in [0,4). Experiments cannot be split or shortened. There are no precedence requirements, fixed appointments or preferences.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.

## realistic-draft-03: Personal study session

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 8 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

I am P0 and my study partner is P1. I am free during [0,8), while P1 is free during [2,8). My one-slot reading activity A0 may use either [0,2) or [4,6). Our two-slot discussion A1 needs both of us and must fit in [2,8). P1 then needs one slot for notes A2 within [4,8). Reading must finish before discussion, and discussion must finish before notes. No room or other resource is required. A1 starts outside [2,3) incur penalty 4; A2 starts outside [6,7) incur penalty 1. Nothing else is preferred.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 21 feasible assignments; optimum (0,). Human prose/gold review pending.

## realistic-draft-04: Personal rehearsal windows

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 4 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

I, P0, need a continuous three-slot solo rehearsal A0. My booking permits two separate windows, [0,2) and [2,4); a rehearsal may not span their boundary, even though the endpoints meet. A0 itself is allowed within [0,4). My collaborator P1 is free throughout [0,4) and independently needs a one-slot checklist activity A1 within [0,4). Neither activity requires a shared resource, and they need not be ordered. There are no preferences.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.

## realistic-draft-05: Community science demonstration

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 8 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

At a community science demonstration, hosts P0 and P1 and apparatus R0 are available throughout [0,8). Every activity has that same allowed window. P0 spends one slot setting up A0 using R0. The hosts then need two slots together for A1, without R0; A1 cannot start before slot 2 and must follow A0. P1 also needs a separate two-slot apparatus demonstration A2 using R0, finishing no later than slot 6. Finally P0 needs one slot for A3 after A1, without apparatus. Starting A1 outside [2,3) costs 3 points; starting A2 outside [2,3) costs 5. There are no other preferences or order requirements.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 38 feasible assignments; optimum (3,). Human prose/gold review pending.

## realistic-draft-06: Personal video production deadline

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 8 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

For my personal video project, I (P0) spend two slots recording A0, editor P1 spends two slots editing A1, and reviewer P2 spends one slot checking A2. Everyone and every activity is available within [0,8), with no shared equipment. Editing must follow recording and checking must follow editing. The check must finish by slot 4. Activities are mandatory and have the stated durations; there are no preferences.

Minimize the total stated preference penalty while satisfying every hard requirement.

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.

## realistic-draft-07: Personal craft bookings after an interruption

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 4 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

I am P0, coordinating my own craft activity A0 alongside P1's A1 and P2's A2. Each activity takes one slot and requires its owner and the shared craft table R0. People and table are available throughout [0,4). Activity windows remain A0 [0,2), A1 [1,3), and A2 [0,3). The new interruption blocks P0 during [0,1); all other facts stay as stated. There are no preferences or precedence requirements.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 0}, {"activity_id": "A1", "start_slot": 1}, {"activity_id": "A2", "start_slot": 2}]

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 1 feasible assignments; optimum (3, 4, 0). Human prose/gold review pending.

## realistic-draft-08: Personal tutorial deadline change

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 6 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

I am P0 and am available throughout [0,6). I need two slots of preparation A0 followed by two slots of tutorial work A1. Both activities can otherwise fit anywhere in [0,6), and neither uses a resource. A new deadline requires A1 to finish by slot 3. Preparation must still finish before A1 starts. There are no preferences.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 0}, {"activity_id": "A1", "start_slot": 2}]

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.

## realistic-draft-09: Shared consultation room rescheduling

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 8 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

The shared consultation room R0 and people P0 and P1 are available throughout [0,8); every activity also has that window. P0 has a one-slot room appointment A0, P1 needs the room for a two-slot session A1, and P0 has a one-slot paperwork activity A2 without the room. A0's appointment has moved from slot 0 to a fixed start at slot 2. There are no precedence requirements. A1 incurs penalty 2 when it starts outside [3,4); there are no other preferences.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 0}, {"activity_id": "A1", "start_slot": 2}, {"activity_id": "A2", "start_slot": 1}]

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 35 feasible assignments; optimum (2, 3, 0). Human prose/gold review pending.

## realistic-draft-10: Shared library booth closure

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 4 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

P0 and P1 each need an uninterrupted two-slot recording in the same library booth R0: A0 for P0 and A1 for P1. People, booth and both activities have window [0,4). A new maintenance closure blocks R0 during [1,2). All activity durations remain unchanged, with no preferences or other ordering constraints.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 0}, {"activity_id": "A1", "start_slot": 2}]

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.

## realistic-draft-11: Personal audio project earlier deadline

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 6 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

For my personal audio project I, P0, use workstation R0 for three one-slot activities: outline A0, record A1, then check A2. I, the workstation and all activities have availability [0,6). Each step must finish before the next begins. The new deadline requires A2 to finish by slot 3. A0 incurs penalty 2 outside start window [0,1); no other preferences apply.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 3}, {"activity_id": "A1", "start_slot": 4}, {"activity_id": "A2", "start_slot": 5}]

Evaluator-only review note: AI-assisted fictional personal draft. Complete independent enumeration: 1 feasible assignments; optimum (3, 9, 0). Human prose/gold review pending.

## realistic-draft-12: Shared loading equipment appointments

Use Monday 5 October 2026, starting at 09:00 in UTC+08:00. Slot zero is 09:00; each slot is 30 minutes, and this request has 6 slots. All times below are slot numbers. Intervals [a,b) include a and exclude b. An activity must fit wholly inside one stated window for itself and every participant/resource; adjacent windows remain separate. Every listed activity is mandatory and non-preemptive. Participants and resources have capacity one. There are no travel, setup or other unstated requirements.

Two teams share loading equipment R0. P0 represents team A0 and P1 represents team A1; each loading activity takes two slots and needs its representative and R0. All availability windows are [0,6). A0's fixed appointment has moved from slot 0 to slot 2; A1 retains its fixed start at slot 2. Neither appointment can be split, omitted or moved away from its fixed start. No preferences apply.

This is the complete updated request; the original schedule is supplied separately. Minimize the number of activities whose start changes, then total absolute start shift in slots, then preference penalty, in that order.

Common original schedule: [{"activity_id": "A0", "start_slot": 0}, {"activity_id": "A1", "start_slot": 2}]

Evaluator-only review note: AI-assisted fictional shared draft. Complete independent enumeration: 0 feasible assignments; optimum None. Human prose/gold review pending.
