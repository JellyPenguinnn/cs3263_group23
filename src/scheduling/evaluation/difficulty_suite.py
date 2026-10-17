"""Versioned easy-to-extreme development instances; no provider calls.

Construction tiers are hypotheses about difficulty, not measured model ability.
Gold SAT witnesses and UNSAT certificates are checked independently of CP-SAT;
reference optima are separately proved by CP-SAT before a packet is accepted.
"""

from collections import Counter
from dataclasses import fields, replace
import random

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import AuthoredBenchmarkCase, AuthoredRendering, BenchmarkCase
from scheduling.evaluation.scoring import digest
from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, Precedence,
    PreferredStart, ProblemSpec, Schedule, Window,
)
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule

VERSION = "difficulty-suite-v1"
CAMPAIGN_POLICY = "difficulty-campaign-1"
TIERS = ("easy", "moderate", "hard", "very_hard", "extreme")
SIZES = (4, 8, 12, 20, 32)
MECHANISMS = ("resource_bottleneck", "precedence_deadline", "coupled_repair")
CALLS = {"controlled": 120, "realistic": 40, "language": 40}


def _schedule(starts):
    return Schedule.from_list([{"activity_id": k, "start_slot": v} for k, v in starts.items()])


def _jobshop(rng, n, ident, mechanism, label, tier):
    """A witnessed multi-job schedule; original and a one-slot shift both fit."""
    jobs = 2 if n < 12 else 4
    ids = [f"A{i}" for i in range(n)]
    rng.shuffle(ids)
    full = (Window(0, 48),)
    durations = {a: rng.randint(1, 3) for a in ids}
    chains = [ids[j::jobs] for j in range(jobs)]
    machines = {a: f"R{rng.randrange(jobs)}" for a in ids}
    job_end, machine_end, starts = [0] * jobs, {f"R{i}": 0 for i in range(jobs)}, {}
    for step in range(max(map(len, chains))):
        order = list(range(jobs))
        rng.shuffle(order)
        for j in order:
            if step >= len(chains[j]):
                continue
            a = chains[j][step]
            starts[a] = max(job_end[j], machine_end[machines[a]])
            job_end[j] = machine_end[machines[a]] = starts[a] + durations[a]
    if max(job_end) > 45:
        raise ValueError("construction_horizon")
    activities = tuple(Activity(a, durations[a], (f"P{j}",), (machines[a],), full)
                       for j, chain in enumerate(chains) for a in chain)
    rules = [Precedence(f"chain-{j}-{i}", a, b)
             for j, chain in enumerate(chains) for i, (a, b) in enumerate(zip(chain, chain[1:]))]
    # Cross-job dependencies connect the chains without invalidating the witness.
    possible = [(a, b) for a in ids for b in ids
                if starts[a] + durations[a] <= starts[b]
                and next(j for j, c in enumerate(chains) if a in c)
                != next(j for j, c in enumerate(chains) if b in c)]
    rng.shuffle(possible)
    rules += [Precedence(f"cross-{i}", a, b) for i, (a, b) in enumerate(possible[:tier * 2])]
    # Breaks create fragmented resource calendars, while preserving both witnesses.
    if tier >= 2:
        for resource in machine_end:
            occupied = {s for a in ids if machines[a] == resource
                        for s in range(starts[a], starts[a] + durations[a] + 1)}
            free = [s for s in range(3, 44) if s not in occupied]
            if free:
                s = rng.choice(free)
                rules.append(BlockedInterval(f"break-{resource}", "resource", resource, s, s + 1))
    for i, a in enumerate(ids):
        # Preferences are independent of the construction witness, and may conflict.
        for k in range(2):
            s = rng.randrange(48 - durations[a] + 1)
            rules.append(PreferredStart(f"pref-{i}-{k}", a, s, s + 1, rng.randint(1, 9)))
    original = ProblemSpec("1.0", ident + "-original", "generation", 48, 30,
                           "2026-10-26T00:00:00+08:00", "+08:00",
                           tuple(Entity(f"P{j}", full) for j in range(jobs)),
                           tuple(Entity(f"R{j}", full) for j in range(jobs)),
                           activities, tuple(rules))
    if label == "SAT":
        a = rng.choice(ids)
        update = BlockedInterval("change", "participant",
                                 next(x.participant_ids[0] for x in activities if x.id == a),
                                 starts[a], starts[a] + 1)
        # A participant may have an earlier activity at this slot. The global shift
        # is valid when the target is that participant's first activity.
        j = int(update.target_id[1:])
        a = chains[j][0]
        update = replace(update, start=starts[a], end=starts[a] + 1)
        updated = replace(original, constraints=original.constraints + (update,))
        witness = _schedule({a: s + 1 for a, s in starts.items()})
        certificate = {"kind": "sat_witness"}
    elif mechanism == "resource_bottleneck":
        resource = max(machine_end, key=lambda r: sum(durations[a] for a in ids if machines[a] == r))
        subset = [a for a in ids if machines[a] == resource]
        bound = sum(durations[a] for a in subset) - 1
        updated = replace(original, constraints=original.constraints + tuple(
            Deadline(f"change-{a}", a, bound) for a in subset))
        witness = None
        certificate = {"kind": "resource_workload", "resource": resource,
                       "activities": subset, "deadline": bound}
    else:
        chain = max(chains, key=lambda c: sum(durations[a] for a in c))
        bound = sum(durations[a] for a in chain) - 1
        updated = replace(original, constraints=original.constraints + (Deadline("change", chain[-1], bound),))
        witness = None
        certificate = {"kind": "critical_path", "activities": chain, "deadline": bound}
    return original, updated, _schedule(starts), witness, certificate


def _cycle(rng, n, ident, label):
    ids = [f"A{i}" for i in range(n)]
    rng.shuffle(ids)
    offset = rng.randrange(48 - n)
    slots = list(range(offset, offset + n))
    full = (Window(0, 48),)
    old = dict(zip(ids, slots))
    alternate = dict(zip(ids, slots[1:] + slots[:1]))
    activities = tuple(Activity(a, 1, (f"P{i}",), ("R0",),
                                tuple(Window(s, s + 1) for s in sorted({old[a], alternate[a]})))
                       for i, a in enumerate(ids))
    rules = tuple(PreferredStart(f"pref-{a}", a, old[a], old[a] + 1, rng.randint(1, 9)) for a in ids)
    original = ProblemSpec("1.0", ident + "-original", "generation", 48, 30,
                           "2026-10-26T00:00:00+08:00", "+08:00",
                           tuple(Entity(f"P{i}", full) for i in range(n)),
                           (Entity("R0", full),), activities, rules)
    changes = (BlockedInterval("change", "participant", "P0", slots[0], slots[0] + 1),)
    if label == "UNSAT":
        changes += (FixedStart("retained-appointment", ids[-1], slots[-1]),)
    updated = replace(original, constraints=rules + changes)
    cert = {"kind": "sat_witness"} if label == "SAT" else {
        "kind": "unit_slot_capacity", "resource": "R0", "activities": ids}
    return original, updated, _schedule(old), _schedule(alternate) if label == "SAT" else None, cert


def verify_certificate(spec, certificate, witness=None):
    """Arithmetic proof checks: deliberately no calls to the solver or compiler."""
    kind = certificate["kind"]
    if kind == "sat_witness":
        # The certificate concerns updated hard feasibility only. Repair objective
        # values are checked separately with the original schedule/context.
        return witness is not None and validate_schedule(replace(spec, task_type="generation"), witness).hard_feasible
    activities = {a.id: a for a in spec.activities}
    ids = certificate["activities"]
    if len(set(ids)) != len(ids) or not ids or any(a not in activities for a in ids):
        return False
    if kind in ("resource_workload", "critical_path"):
        bound = certificate["deadline"]
        deadlines = {c.activity_id: c.slot for c in spec.constraints if isinstance(c, Deadline)}
        if kind == "resource_workload":
            if any(certificate["resource"] not in activities[a].resource_ids
                   or deadlines.get(a, spec.horizon_slots) > bound for a in ids):
                return False
        else:
            edges = {(c.before, c.after) for c in spec.constraints if isinstance(c, Precedence)}
            if deadlines.get(ids[-1], spec.horizon_slots) > bound or any(
                    (a, b) not in edges for a, b in zip(ids, ids[1:])):
                return False
        return sum(activities[a].duration_slots for a in ids) > bound
    if kind == "unit_slot_capacity":
        slots = set()
        for a in ids:
            activity = activities[a]
            if activity.duration_slots != 1 or certificate["resource"] not in activity.resource_ids:
                return False
            allowed = {s for w in activity.availability for s in range(w.start, w.end)}
            for c in spec.constraints:
                if isinstance(c, FixedStart) and c.activity_id == a:
                    allowed &= {c.slot}
                if isinstance(c, BlockedInterval) and (
                    (c.target_kind == "participant" and c.target_id in activity.participant_ids)
                    or (c.target_kind == "resource" and c.target_id in activity.resource_ids)
                ):
                    allowed -= set(range(c.start, c.end))
            if not allowed:  # This suite promises nonempty unary domains in UNSAT cases.
                return False
            slots |= allowed
        return len(slots) < len(ids)
    return False


def _clock(slot):
    return f"{slot // 2:02d}:{30 * (slot % 2):02d}"


def clock_render(case, scenario=False):
    """Fully specified clock-time prose; gold labels and proof metadata are absent."""
    spec = case.problem
    windows = lambda ws: ", ".join(f"{_clock(w.start)}–{_clock(w.end)}" for w in ws) or "no available time"
    facts = []
    if scenario:
        contexts = {"resource_bottleneck": "a community workshop sharing equipment",
                    "precedence_deadline": "an event crew coordinating preparation and delivery",
                    "coupled_repair": "a shared studio rescheduling its bookings"}
        facts.append(f"Please coordinate {contexts[case.sweep]} for Monday 26 October 2026.")
    facts.append("This is one fixed UTC+08:00 day. Slot 0 is 00:00; each slot is 30 minutes; "
                 "24:00 means the end of this day. Return start times as integer slot numbers. "
                 "All listed activities are mandatory, have fixed assignments, and cannot be interrupted. "
                 "A whole activity must fit inside one of each applicable availability window. "
                 "A window includes its beginning and excludes its end; adjacent windows remain separate. "
                 "Each participant and resource has capacity one. There are no travel, setup or unstated rules.")
    for name, entities in (("Participant", spec.participants), ("Resource", spec.resources)):
        for e in entities:
            facts.append(f"{name} {e.id} is available during {windows(e.availability)}.")
    for a in spec.activities:
        facts.append(f"Activity {a.id} takes {a.duration_slots * 30} minutes, involves "
                     f"{', '.join(a.participant_ids) or 'no participants'}, requires "
                     f"{', '.join(a.resource_ids) or 'no equipment'}, and may take place during {windows(a.availability)}.")
    for c in spec.constraints:
        if isinstance(c, Precedence):
            facts.append(f"{c.after} can begin only after {c.before} has finished; beginning at that finish time is allowed.")
        elif isinstance(c, Deadline):
            facts.append(f"{c.activity_id} must finish no later than {_clock(c.slot)}.")
        elif isinstance(c, FixedStart):
            facts.append(f"{c.activity_id} must begin at {_clock(c.slot)} exactly.")
        elif isinstance(c, BlockedInterval):
            facts.append(f"{c.target_kind.title()} {c.target_id} cannot be used during {_clock(c.start)}–{_clock(c.end)}.")
        elif isinstance(c, PreferredStart):
            facts.append(f"Add {c.weight} penalty points if {c.activity_id} starts outside "
                         f"{_clock(c.start)} (included) to {_clock(c.end)} (excluded); otherwise add zero. This is a preference, not a hard rule.")
        else:
            raise ValueError("Unsupported clock renderer constraint")
    facts.append("These are the complete updated requirements; the original schedule is provided separately. "
                 "Minimize moved activities first, total absolute start shift in slots second, and total preference penalty third."
                 if case.context else "Minimize total preference penalty while satisfying every hard requirement.")
    return "\n".join(facts)


def _authored(case):
    canonical = clock_render(case, scenario=True) if case.kind == "realistic" else render(case).text
    texts = {"canonical": canonical, "paraphrase": clock_render(case),
             "reordered": render(case, "reordered", 3263).text}
    return AuthoredBenchmarkCase(
        **{f.name: getattr(case, f.name) for f in fields(BenchmarkCase)},
        authored_renderings=tuple(AuthoredRendering(k, text, "llm_assisted", VERSION,
            "Deterministic complete templates authored with Codex; independent human meaning review pending.")
            for k, text in texts.items()), gold_author_reference=VERSION)


def build_suite(seed=32661013, reference_seconds=60):
    cases, proofs, rejected = [], {}, []
    for kind in ("controlled", "realistic"):
        for tier, (level, n) in enumerate(zip(TIERS, SIZES)):
            mechanisms = MECHANISMS if kind == "controlled" else (MECHANISMS[tier % 3],)
            for mechanism in mechanisms:
                for label in ("SAT", "UNSAT"):
                    token = digest([VERSION, seed, kind, level, mechanism, label])
                    group = "difficulty-" + token[:24]
                    # Geometric rejection only; never select using LLM results.
                    for attempt in range(30):
                        rng = random.Random(int(digest([token, attempt]), 16))
                        try:
                            values = (_cycle(rng, n, group, label) if mechanism == "coupled_repair"
                                      else _jobshop(rng, n, group, mechanism, label, tier))
                            break
                        except ValueError as e:
                            if str(e) != "construction_horizon":
                                raise
                            rejected.append({"group_id": group, "attempt": attempt, "reason": str(e)})
                    else:
                        raise ValueError("Construction could not fit the fixed single-day contract")
                    original, updated, old, witness, certificate = values
                    if not validate_schedule(original, old).hard_feasible or not verify_certificate(updated, certificate, witness):
                        raise ValueError(f"Independent construction proof failed: {group}")
                    for task in ("generation", "repair"):
                        spec = replace(updated, instance_id=group + "-" + task, task_type=task)
                        case = BenchmarkCase(spec.instance_id, group, "development", kind, mechanism, level, spec,
                            original if task == "repair" else None, old if task == "repair" else None,
                            "Updated availability or completion commitments" if task == "repair" else None,
                            witness, label, justification="Independent construction certificate and CP-SAT reference; human prose review pending.")
                        result = solve(spec, SolverLimits(reference_seconds), case.context)
                        if label == "SAT":
                            if not result.optimality_proven or result.schedule is None:
                                raise ValueError(f"Unproved reference optimum: {case.case_id} ({result.status})")
                            if not validate_schedule(spec, result.schedule, case.context).hard_feasible:
                                raise ValueError("Reference witness rejected independently")
                            case = replace(case, witness=result.schedule, expected_objective=result.objectives.as_tuple())
                        elif result.status != "INFEASIBLE":
                            raise ValueError(f"UNSAT certificate and solver disagree: {case.case_id}")
                        cases.append(_authored(case))
                        proofs[case.case_id] = {"certificate": certificate, "problem_sha256": digest(spec),
                            "independent_certificate_checked": True, "reference_status": result.status,
                            "reference_optimality_proven": result.optimality_proven,
                            "expected_objective": case.expected_objective}
    return tuple(c for c in cases if c.kind == "controlled"), tuple(c for c in cases if c.kind == "realistic"), proofs, rejected


def select_language(cases):
    """Two distinct source families per tier; task and SAT margins balance."""
    chosen = []
    for i, level in enumerate(TIERS):
        for task, label in (("generation", "SAT" if i % 2 == 0 else "UNSAT"),
                            ("repair", "UNSAT" if i % 2 == 0 else "SAT")):
            candidates = [c for c in cases if c.level == level and c.problem.task_type == task
                          and c.expected_label == label]
            chosen.append(min(candidates, key=lambda c: (MECHANISMS.index(c.sweep) - i % 3) % 3))
    return tuple(chosen)


def check_design(controlled, realistic):
    expected_mechanisms = {(tier, mechanism, task, label): 1 for tier in TIERS for mechanism in MECHANISMS
                           for task in ("generation", "repair") for label in ("SAT", "UNSAT")}
    if Counter((c.level, c.sweep, c.problem.task_type, c.expected_label) for c in controlled) != expected_mechanisms:
        raise ValueError("Controlled difficulty mechanisms changed")
    for cases, kind, each in ((controlled, "controlled", 3), (realistic, "realistic", 1)):
        expected = {(tier, task, label): each for tier in TIERS
                    for task in ("generation", "repair") for label in ("SAT", "UNSAT")}
        if Counter((c.level, c.problem.task_type, c.expected_label) for c in cases) != expected:
            raise ValueError("Difficulty suite tier/task/label balance changed")
        if any(c.kind != kind or c.split != "development" or not isinstance(c, AuthoredBenchmarkCase)
               or len(c.problem.activities) != SIZES[TIERS.index(c.level)]
               or {r.variant_id for r in c.authored_renderings} != {"canonical", "paraphrase", "reordered"}
               for c in cases):
            raise ValueError("Difficulty suite type/size contract changed")
