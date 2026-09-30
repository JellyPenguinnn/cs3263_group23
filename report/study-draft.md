# Direct LLM Reasoning versus Constraint-Solver-Augmented Scheduling

CS3263 Group 23 — Tea Li Hao, Tham Yao Xiang, Woo Yong Qing.

**Working report source, 30 September 2026.** AI-assisted draft for human revision;
not a submission, completed review or frozen-study report. Private student
identifiers belong only on the submission title page. Numerical findings below
are development evidence. See [claim index](claim-evidence.md) and
[contribution record](contributions.md).

## Abstract draft

We study schedule generation and repair on a single-day grid with fixed activity
durations and participant/resource assignments. We compare one language-model
call that proposes a schedule with one call that extracts a specification for a
fixed CP-SAT compiler. An independent validator checks both against gold
requirements. Repair minimizes moved activities, total time shift and preference
violations in that order. The implemented system preserves parsing failures,
extraction discrepancies, proof status and usage. Development results reveal
that a solver may correctly solve a mistranslated problem. Final model selection,
reviewed fresh data and the frozen comparison remain outstanding; no final
effect size or superiority claim is made here.

## 1. Motivation and questions — target 0.75 pages

A shared room becoming unavailable can require moving activities whose own
requirements did not change. Rebuilding a feasible timetable from scratch may
also disrupt more commitments than necessary. We ask when direct model reasoning
is sufficient, when formal solving helps, what causes failures, and how repair
and equivalent wording affect outcomes. Our prototype proposes schedules; it
does not contact participants or edit calendars.

We deliberately restrict the domain to mandatory, non-preemptive activities,
fixed participants, capacity-one resources and 30-minute slots on one day.
This supports explicit mathematical checks while excluding task assignment,
travel inference and multi-day planning. These restrictions limit realism.

## 2. Related work and contribution — target 0.75 pages

NATURAL PLAN evaluates planning with task information supplied in the input,
including calendar scheduling [1]. We likewise separate scheduling from external
information retrieval, but add a common-start repair comparison. Minimal
perturbation research formalizes limiting changes when a constraint problem
changes [2]; our complete schedules and particular three-component objective
are a narrower design choice. Neither repair nor CP-SAT is a new algorithm here.

Huang and Zhang examine language models as planning formalizers and observe
degradation with more natural descriptions in their PDDL study [3]. This
motivates measuring extraction fidelity separately from the solver result; it
does not predict our scheduling scores. CP-SAT integrates constraint, SAT and
linear techniques [4]. We use its established implementation with a fixed
compiler. Our intended contribution is a bounded, reproducible comparison of
generation, repair, interpretation failures and wording sensitivity. The
wording component is planned, not measured by the existing canonical-only run.

## 3. Formalization and repair — target 1.50 pages

For every mandatory activity i, let its integer start be s_i, fixed duration d_i,
and end e_i = s_i + d_i. The horizon is H <= 48 slots. D_i contains starts in
0,...,H-d_i satisfying every unary requirement: release, deadline, fixed start,
blocked intervals, and full containment within one available window for each
required activity, participant and resource. Adjacent half-open intervals are
allowed; a task cannot bridge a gap between windows.

The CSP consists of variables s_i, domains D_i and hard constraints. Precedence
i → j requires e_i <= s_j. Each shared entity induces non-overlapping intervals.
An empty domain is a valid contradiction, not malformed input. The product of
domain sizes bounds naive combinations; it is not an observed CP-SAT search count.

Generation minimizes P(s), the sum of weights for preferred start windows missed
by the schedule. Repair minimizes the lexicographic tuple

```text
M(s) = sum_i [s_i != old_i]
T(s) = sum_i abs(s_i - old_i)
P(s) = sum_k weight_k * [s_activity(k) outside preferred_start_window_k]
minimize (M(s), T(s), P(s)) lexicographically
```

CP-SAT first proves the optimum of M, fixes it, then does the same for T before
minimizing P. All stages share one time budget and use zero absolute/relative
optimality gaps. A timeout retains a valid incumbent but does not establish
unproved later priorities. `UNKNOWN` is not `INFEASIBLE`; `FEASIBLE` is not
`OPTIMAL`. Secondary objective gaps are interpretable only when preceding
components equal their proven reference optima.

**Worked example.** A, B and C each last one slot and share resource R over
[0,3). Their original legal starts are A={0,1}, B={1,2}, C={0,1,2}; the original
schedule is (0,1,2). A participant block removes A's start 0. A must start 1,
forcing B to 2 and C to 0. This is the only feasible repair, with (M,T,P)=(3,4,0).
B and C move although their unary requirements were unchanged. Fixing them at
their old positions would incorrectly report infeasibility. Independent tiny
enumeration, the arithmetic validator and CP-SAT check this example (C2).

## 4. System and evidence boundaries — target 1.00 page

```mermaid
flowchart LR
  G[Evaluator-only gold case] --> R[Public renderer]
  R --> V[Same description and original schedule]
  V --> A[One direct call / strict schedule parser]
  V --> B[One extraction call / schema parser]
  B --> S[Fixed CP-SAT compiler]
  G --> O[Gold reference solver]
  G --> I[Independent arithmetic validator]
  A --> I
  S --> I
  O --> E[Scoring and conditional objective comparison]
  I --> E
  E --> D[Immutable records / replay / read-only dashboard]
```

Both paths receive equivalent public information; the direct arm receives no
solver, oracle or repair feedback. B uses a neutral request ID rather than a
label-bearing evaluator ID. Its extracted specification must pass the canonical
schema before compilation. Duplicate keys, wrappers and unsupported fields
remain failures; the parser does not insert omitted requirements.

The validator recomputes hard feasibility and objectives without calling CP-SAT
or using its constraint-building helpers. The reference solver supplies gold
feasibility and proven optima, while tiny independent enumeration checks the
compiler. Solver success concerns the extracted specification, which may omit
source requirements. Explanations keep that proof separate from gold acceptance
and bind new standalone proof claims to their exact input/context (C1).

The serial runner durably reserves requests before sending, records failures and
usage, refuses incompatible resume, and replays stored outputs without inference.
Missing usage is unavailable, not zero. Output reservations do not cap aggregate
input-plus-output tokens or currency. Historical SoCLaaS sampling and reasoning
controls were server defaults; a solver seed does not make model calls deterministic.

## 5. Dataset and protocol — target 1.50 pages

The expanded development packet has 100 known synthetic cases: 64 from v2 and
36 from v3, grouped into 41 conservative source families. Each task has 25 SAT
and 25 UNSAT cases; related cases are not independent observations. Fourteen IDs
occurred in earlier live pilots. All text was canonical. Twelve separate
AI-assisted fictional drafts exercise authored-text consumers; they are not
independently human-written scenarios (C3).

The planned final study uses fresh instances from a reviewed construction policy,
not a claim of unseen generators or freedom from pretraining contamination.
Both original and updated repair structures must avoid all recorded development
structures, including calendar/ID renamings. A second member reviews gold and
language. Realistic provenance must reflect actual authorship.

**Final decisions pending:** eligible model/backend, verified effective settings,
selected prompt, construction policy, actual reviews, study size, compatible
frozen blocks and explicit execution cap. The proposed 600-call target and
312-call compact alternative are planning envelopes. Canonical controlled,
realistic and selected language blocks have separate estimands. Additional
wordings cannot give selected cases extra primary weight.

We will report validity on gold-SAT cases, UNSAT accuracy, all-attempt accepted
answers, failure categories, conditional objective quality and resources. Paired
comparisons retain A/B pairs and source-family grouping. The final analysis must
record its interval method, seed, denominators and achieved family counts before
outcomes. Tiny constructed strata cannot establish population difficulty thresholds.

## 6. Development findings and final-results slots — target 2.50 pages

The following are **development findings only**, reproduced from saved aggregates
for `expanded-development-100-20260930-01` (C4–C6). Both arms used `qwen3.6:35b`,
unchanged prompts, 16,384 output tokens per request, no retries, 30-second B solves
and 60-second reference budgets. No new experiment generated this table.

| Task | A accepted | B accepted | A valid on SAT | B valid on SAT | A correct UNSAT | B correct UNSAT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Generation | 23/50 | 48/50 | 17/25 | 24/25 | 6/25 | 24/25 |
| Repair | 12/50 | 49/50 | 8/25 | 25/25 | 4/25 | 24/25 |

All failed attempts remain in denominators. B's three failures were two omitted
fixed appointments and one malformed JSON response. A schema-valid extraction
therefore does not establish correct interpretation. Ten structural mismatches
include eight independently certified equivalent encodings; the structural
metric and separate bounded semantic certificate must not be conflated (C5).

For example, the failed fixed-appointment repair requires A0 and A1 to start
at slot 1 while sharing capacity-one Rpair for one slot each. Both requirements
cannot hold. Omitting A0’s appointment instead lets the unchanged original
schedule appear optimal with zero disruption, although A0 remains at slot 3.
The validator rejects it. Independent enumeration of the conflicting pair and
restoring only the missing field in a diagnostic copy establish this failure’s
mechanism; no correction enters primary scores (C5).

The 200 calls reported 465,251 tokens with complete usage coverage. Mean model
latency was 1.895 seconds for A and 10.115 seconds for B. CP-SAT averaged 4.69 ms
over the 99 B attempts that reached it. This conditional timing suggests that
solver speed was not the dominant cost on these small development instances.
There was no measured currency cost (C6).

The data support a development comparison under this particular construction and
configuration. They do not establish production reliability, final held-out
performance, a causal improvement over older settings, or robustness to wording.

Final results must replace or clearly separate this development section with:
(i) canonical task/label outcomes and paired difficulty plots, (ii) repair quality
with validity/proof denominators, (iii) extraction failures, (iv) matched language
transitions and (v) resource tails and missing counts. These slots are intentionally
unfilled until F4/F5 supplies reviewed evidence; no expected scores are inserted.

## 7. Responsible AI and limitations — target 1.00 page

**Unequal inconvenience.** In the preserved development case
`dev-3263-interaction_density-1-repair`, participant P7 bears one moved activity
and 30 minutes of shift while P0–P6 bear none. This shows concentration, not proof
that a feasible fairer solution exists. Shared events count for each participant;
fixed assignments do not solve fair workload allocation (C7).

**Objective side effect.** A tiny independently enumerated repair admits a
two-move/two-slot solution but chooses one move/four slots under the stated
priority. Avoiding an extra moved commitment can therefore require greater total
shift. The choice should be disclosed to users rather than called universally
best (C8).

**Negotiability and privacy.** A supplied deadline is hard unless explicitly
modelled otherwise. The system cannot decide which unstated commitment may be
relaxed. Only fictional data are used; real routines could reveal identity even
after renaming. Future real calendars would require consent and a retention plan.
The interface presents proposals without sending invitations or editing calendars.

**Instruction-like text.** A synthetic prompt-boundary regression keeps an
embedded “ignore all rules” string in the user-data message, outside system
instructions. This checks construction, not empirical adversarial robustness of
a model. A fixed compiler prevents executing generated code but cannot prevent
all extraction mistakes (C9).

Members must supply their own interpretation of these cases. Other limits include
generator bias, small dependent samples, single-day/fixed-assignment assumptions,
unknown hosted weight revisions, default inference settings and pending realistic
and language-condition evidence.

## 8. Synthesis, contributions and AI disclosure — target 1.00 page

The implementation makes feasibility, optimality and interpretation independently
inspectable. The coupled example explains why local changes can require global
repair; the saved failures explain why a correct solver does not guarantee a
correct answer to natural language. Final conclusions await the frozen study and
should remain informative even if direct reasoning proves competitive.

Codex assisted code, tests, this draft and evidence linkage under member direction.
Branch names and assigned tasks do not establish independent human authorship,
review or hours. The [contribution log](contributions.md) records observed actions
and leaves human interpretation/review explicitly pending. No submission receipt,
teaching-team approval or rehearsal is claimed.

## References — outside the planned body

1. Zheng, H. S., et al. (2024). *NATURAL PLAN: Benchmarking LLMs on Natural Language Planning*. [arXiv:2406.04520](https://arxiv.org/abs/2406.04520).
2. Barták, R., Müller, T., and Rudová, H. *Minimal Perturbation Problem — A Formal View*. [Authors' paper](https://www.unitime.org/papers/ercimprelimin03.pdf).
3. Huang, C., and Zhang, L. (2025). *On the Limit of Language Models as Planning Formalizers*. ACL, pp. 4880–4904. [doi:10.18653/v1/2025.acl-long.242](https://aclanthology.org/2025.acl-long.242/).
4. Perron, L., Didier, F., and Gay, S. (2023). *The CP-SAT-LP Solver*. CP 2023, LIPIcs 280, pp. 3:1–3:2. [doi:10.4230/LIPIcs.CP.2023.3](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2023.3).

These four source records were checked for this draft; related scheduling and
language-robustness literature listed in planning Section 16 still needs final
selection and human synthesis. Markdown is the single working report source.
Its section budgets total ten pages, but no rendered page/font/margin compliance
is claimed. Final typesetting, figure placement and the course-format audit remain
F6 delivery work.
