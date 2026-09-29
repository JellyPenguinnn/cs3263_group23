"""Synthetic development construction and complete public renderings; no held-out runs."""

from dataclasses import replace
from itertools import combinations
import random

from scheduling.evaluation.cases import BenchmarkCase
from scheduling.schema import (
    Activity,
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    NaturalLanguageView,
    Precedence,
    PreferredStart,
    ProblemSpec,
    ReleaseTime,
    Schedule,
    Window,
)


def _schedule(starts):
    return Schedule.from_list(
        [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
    )


def tiny_fixtures():
    windows = (Window(0, 4),)
    base = ProblemSpec(
        "1.0",
        "simple-sat",
        "generation",
        4,
        30,
        "2026-10-05T09:00:00+08:00",
        "+08:00",
        (Entity("P", windows),),
        (),
        (Activity("A", 1, ("P",), (), windows), Activity("B", 1, ("P",), (), windows)),
        (),
    )

    def case(spec, witness, explanation, label="SAT", objective=(0,), **kwargs):
        return BenchmarkCase(
            spec.instance_id,
            spec.instance_id,
            "development",
            "controlled",
            "fixture",
            spec.instance_id,
            spec,
            witness=witness,
            expected_label=label,
            expected_objective=objective,
            justification=explanation,
            **kwargs,
        )

    simple = case(
        base,
        _schedule({"A": 0, "B": 1}),
        "Adjacent one-slot tasks fit [0,4); nonnegative preference lower bound zero is attained.",
    )
    overlap = case(
        replace(base, instance_id="overlap", constraints=(FixedStart("a", "A", 0),)),
        _schedule({"A": 0, "B": 1}),
        "A is fixed at 0; B at 1 is adjacent and valid. Mutating B to 0 overlaps P.",
    )
    resource = replace(
        base,
        instance_id="shared-resource",
        participants=(),
        resources=(Entity("R", windows),),
        activities=tuple(
            replace(a, duration_slots=2, participant_ids=(), resource_ids=("R",))
            for a in base.activities
        ),
    )
    shared = case(
        resource,
        _schedule({"A": 0, "B": 2}),
        "Two duration-two tasks exactly fill four slots of R; simultaneous starts violate R capacity.",
    )
    precedence = case(
        replace(
            base,
            instance_id="precedence-deadline",
            constraints=(Precedence("p", "A", "B"), Deadline("d", "B", 2)),
        ),
        _schedule({"A": 0, "B": 1}),
        "A then B with B ending by 2 forces A0/B1; preference optimum zero.",
    )
    impossible = replace(
        resource,
        instance_id="proven-unsat",
        horizon_slots=3,
        resources=(Entity("R", (Window(0, 3),)),),
        activities=tuple(
            replace(a, availability=(Window(0, 3),)) for a in resource.activities
        ),
    )
    unsat = case(
        impossible,
        None,
        "Each task fits alone, but R needs four occupied slots in a three-slot horizon; impossible without overlap.",
        "UNSAT",
        None,
    )
    original = replace(
        base, instance_id="repair", constraints=(Precedence("p", "A", "B"),)
    )
    updated = replace(
        original,
        task_type="repair",
        constraints=original.constraints
        + (BlockedInterval("b", "participant", "P", 0, 1),),
    )
    repair = case(
        updated,
        _schedule({"A": 1, "B": 2}),
        "Original A0/B2 is valid. Blocking slot 0 forces at least one move and one shifted slot; A1/B2 attains both bounds with zero penalty.",
        objective=(1, 1, 0),
        original_problem=original,
        original_schedule=_schedule({"A": 0, "B": 2}),
        event="new blocked interval",
    )
    return simple, overlap, shared, precedence, unsat, repair


def generate_development(seed=3263):
    """24 provisional sweep cases; original repair schedules are pinned solver outputs."""
    from scheduling.solver import SolverLimits, solve

    rng = random.Random(seed)
    cases = []
    for sweep in (
        "activity_count",
        "slack",
        "interaction_density",
        "resource_contention",
    ):
        for level in range(3):
            n = (4, 8, 12)[level] if sweep == "activity_count" else 8
            radius = (0, 2, 8)[level] if sweep == "slack" else 4
            density = (0, 1, 2)[level] if sweep == "interaction_density" else 1
            resource_count = (
                (0, n // 2, n)[level] if sweep == "resource_contention" else n // 2
            )
            group = f"dev-{seed}-{sweep}-{level}"
            full = (Window(0, 48),)
            activities = tuple(
                Activity(
                    f"A{i}",
                    1,
                    (f"P{i}",),
                    ("R",) if i < resource_count else (),
                    (Window(max(0, 2 * i - radius), min(48, 2 * i + 1 + radius)),),
                )
                for i in range(n)
            )
            rules = [
                PreferredStart(f"pref{i}", f"A{i}", 2 * i, 2 * i + 1, rng.randint(1, 3))
                for i in range(n)
            ]
            for step in range(1, density + 1):
                rules += [
                    Precedence(f"p{step}-{i}", f"A{i}", f"A{i+step}")
                    for i in range(n - step)
                ]
            original = ProblemSpec(
                "1.0",
                group + "-generation",
                "generation",
                48,
                30,
                "2026-10-05T00:00:00+08:00",
                "+08:00",
                tuple(Entity(f"P{i}", full) for i in range(n)),
                (Entity("R", full),),
                activities,
                tuple(rules),
            )
            witness = _schedule({f"A{i}": 2 * i for i in range(n)})
            cases.append(
                BenchmarkCase(
                    original.instance_id,
                    group,
                    "development",
                    "controlled",
                    sweep,
                    str(level),
                    original,
                    witness=witness,
                    expected_label="SAT",
                    expected_objective=(0,),
                    justification="Constructed even-slot witness satisfies all constraints and every preference; zero is a global lower bound.",
                )
            )
            result = solve(original, SolverLimits(5, 0, 1))
            if result.schedule is None or not result.optimality_proven:
                raise ValueError(
                    "Development original schedule not proven; do not invent repair context"
                )
            old = result.schedule
            if level == 0:
                event, rule = "new blocked interval", BlockedInterval(
                    "event", "participant", "P0", 0, 1
                )
            elif level == 1:
                event, rule = "tightened deadline", Deadline(
                    "event", f"A{n-1}", 2 * (n - 1)
                )
            else:
                event, rule = "changed fixed appointment", FixedStart("event", "A0", 1)
                original = replace(
                    original,
                    constraints=original.constraints
                    + (FixedStart("old-fixed", "A0", 0),),
                )
                # The saved zero-penalty solver schedule already starts A0 at zero.
            updated = replace(
                original,
                instance_id=group + "-repair",
                task_type="repair",
                constraints=tuple(
                    c for c in original.constraints if c.id != "old-fixed"
                )
                + (rule,),
            )
            cases.append(
                BenchmarkCase(
                    updated.instance_id,
                    group,
                    "development",
                    "controlled",
                    sweep,
                    str(level),
                    updated,
                    original,
                    old,
                    event,
                    justification="Generated development disruption; feasibility and optimality await recorded reference solve and independent witness validation.",
                )
            )
    return tuple(cases)


def render(case, variant="canonical", rendering_seed=0):
    if variant not in ("canonical", "paraphrase", "reordered"):
        raise ValueError("Unsupported rendering variant")
    spec = case.problem

    def windows(items):
        return ", ".join(f"[{w.start},{w.end})" for w in items) or "none (unavailable)"

    def ids(items):
        return ", ".join(items) or "none"

    facts = []
    for name, rows in (
        ("Participant", spec.participants),
        ("Resource", spec.resources),
    ):
        for row in rows:
            facts.append(
                f"{name} {row.id} is available in {windows(row.availability)} and has capacity one."
            )
    for a in spec.activities:
        facts.append(
            f"Activity {a.id} lasts {a.duration_slots} slots; participants: {ids(a.participant_ids)}; resources: {ids(a.resource_ids)}; availability: {windows(a.availability)}."
        )
    for c in spec.constraints:
        if type(c) is ReleaseTime:
            text = f"{c.activity_id} must start at or after slot {c.slot}."
        elif type(c) is Deadline:
            text = f"{c.activity_id} must finish at or before slot {c.slot}."
        elif type(c) is FixedStart:
            text = f"{c.activity_id} must start exactly at slot {c.slot}."
        elif isinstance(c, Precedence):
            text = (
                f"{c.after} may start only once {c.before} has finished."
                if variant == "paraphrase"
                else f"{c.before} must finish before or when {c.after} starts."
            )
        elif isinstance(c, BlockedInterval):
            text = f"{c.target_kind.title()} {c.target_id} is blocked in [{c.start},{c.end})."
        elif isinstance(c, PreferredStart):
            text = f"Starting {c.activity_id} outside [{c.start},{c.end}) incurs penalty {c.weight}; starting inside incurs zero."
        else:
            raise ValueError("Unsupported renderer constraint")
        facts.append(text)
    if variant == "reordered":
        random.Random(rendering_seed).shuffle(facts)
    intro = (
        f"Schedule every activity exactly once. Slot zero is {spec.horizon_start}, timezone {spec.timezone}. "
        f"There are {spec.horizon_slots} slots of {spec.slot_minutes} minutes. "
        "All intervals are half-open, ending at start plus duration. Each activity must fit completely within one availability window for itself and every required entity. "
        "Activities sharing a participant or resource must not overlap. Only listed entities and constraints apply."
    )
    if variant == "paraphrase":
        intro = "Find a schedule satisfying all the following requirements. " + intro
    goal = (
        "This is the complete UPDATED problem. Use the supplied original schedule. Minimize moved activity count, then total absolute start shift in slots, then preference penalty, in that order."
        if case.context
        else "Minimize the total preference penalty subject to all hard requirements."
    )
    view = NaturalLanguageView(
        case.case_id,
        variant,
        spec.task_type,
        "\n".join([intro, *facts, goal]),
        tuple(a.id for a in spec.activities),
        case.original_schedule,
    )
    return view


def difficulty(spec):
    """Unary domain counts use direct arithmetic, independently of compiler domains."""
    counts = []
    people = {p.id: p for p in spec.participants}
    resources = {r.id: r for r in spec.resources}
    for a in spec.activities:
        count = 0
        for start in range(spec.horizon_slots):
            end = start + a.duration_slots
            groups = (
                [a.availability]
                + [people[k].availability for k in a.participant_ids]
                + [resources[k].availability for k in a.resource_ids]
            )
            valid = end <= spec.horizon_slots and all(
                any(w.start <= start and end <= w.end for w in ws) for ws in groups
            )
            for c in spec.constraints:
                if type(c) is ReleaseTime and c.activity_id == a.id:
                    valid &= start >= c.slot
                elif type(c) is Deadline and c.activity_id == a.id:
                    valid &= end <= c.slot
                elif type(c) is FixedStart and c.activity_id == a.id:
                    valid &= start == c.slot
                elif isinstance(c, BlockedInterval) and c.target_id in (
                    a.participant_ids
                    if c.target_kind == "participant"
                    else a.resource_ids
                ):
                    valid &= end <= c.start or start >= c.end
            count += bool(valid)
        counts.append(count)
    pairs = list(combinations(spec.activities, 2))
    edges = set()
    for a, b in pairs:
        if set(a.participant_ids) & set(b.participant_ids) or set(a.resource_ids) & set(
            b.resource_ids
        ):
            edges.add(frozenset((a.id, b.id)))
    edges.update(
        frozenset((c.before, c.after))
        for c in spec.constraints
        if isinstance(c, Precedence)
    )
    contention = sum(bool(set(a.resource_ids) & set(b.resource_ids)) for a, b in pairs)
    product = 1
    for count in counts:
        product *= count
    return {
        "activity_count": len(spec.activities),
        "unary_start_counts": counts,
        "start_domain_product": product,
        "mean_unary_slack": sum(counts) / len(counts) if counts else 0,
        "interaction_density": len(edges) / len(pairs) if pairs else 0,
        "resource_contention": contention / len(pairs) if pairs else 0,
    }


V2_SWEEPS = ("activity_count", "slack", "interaction_density", "resource_contention")
V2_EVENTS = ("blocked", "deadline", "fixed_start")


def _v2_candidate(seed, sweep, level, event, label, serial):
    """Witness-first construction; every precedence edge has a reversible pair."""
    import hashlib

    rng = random.Random(
        int.from_bytes(
            hashlib.sha256(
                f"{seed}/{sweep}/{level}/{event}/{label}/{serial}".encode()
            ).digest(),
            "big",
        )
    )
    n = (4, 8, 12)[level] if sweep == "activity_count" else 8
    radius = (1, 3, 6)[level] if sweep == "slack" else 3
    edge_level = level if sweep == "interaction_density" else 1
    sharing = (0.0, 0.5, 1.0)[level] if sweep == "resource_contention" else 0.5
    ident = f"dev-v2-{seed}-{sweep}-{level}-{event}-{label.lower()}-{serial}"
    full = (Window(0, 48),)
    d = rng.choice((1, 2))
    base = rng.randint(1, 3)
    # A1 is fixed; A0 can precede or follow it individually. UNSAT updates leave
    # only overlapping positions, so unary domains alone do not reveal the conflict.
    starts = {"A0": base + d + 1, "A1": base}
    durations = [d, d] + [rng.choice((1, 2)) for _ in range(n - 2)]
    cursor = base + 2 * d + 4
    for i in range(2, n):
        starts[f"A{i}"] = cursor
        cursor += durations[i] + (1 if n == 12 else rng.randint(1, 2))
    assert cursor <= 48
    assignments = [() for _ in range(n)]
    assignments[0] = assignments[1] = ("Rpair",)
    shuffled = list(range(2, n))
    rng.shuffle(shuffled)
    for i in shuffled[: round(sharing * (n - 2))]:
        assignments[i] = ("Rshared",)
    # Private participants identify events; an extra shared participant varies
    # participant contention without removing any activity's immutable assignment.
    shared_people = set(rng.sample(list(range(2, n)), min(3, n - 2)))
    activity_windows = [(Window(base, base + 2 * d + 3),)] * 2
    pair_edges = []
    for i in range(2, n, 2):
        j = i + 1
        lo = max(base + 2 * d + 3, starts[f"A{i}"] - radius)
        hi = min(48, starts[f"A{j}"] + durations[j] + radius)
        activity_windows.extend([(Window(lo, hi),), (Window(lo, hi),)])
        pair_edges.append((f"A{i}", f"A{j}"))
    edge_count = (0, max(1, len(pair_edges) // 2), len(pair_edges))[edge_level]
    rng.shuffle(pair_edges)
    rules = [FixedStart("anchor", "A1", base)]
    if event == "fixed_start":
        rules.append(FixedStart("old-event", "A0", starts["A0"]))
    rules += [
        Precedence(f"edge{i}", a, b) for i, (a, b) in enumerate(pair_edges[:edge_count])
    ]
    rules += [
        PreferredStart(
            f"pref{i}", f"A{i}", starts[f"A{i}"], starts[f"A{i}"] + 1, rng.randint(1, 4)
        )
        for i in range(n)
    ]
    spec = ProblemSpec(
        "1.0",
        ident + "-original",
        "generation",
        48,
        30,
        "2026-10-05T00:00:00+08:00",
        "+08:00",
        tuple(Entity(f"P{i}", full) for i in range(n)) + (Entity("Pshared", full),),
        (Entity("Rpair", full), Entity("Rshared", full)),
        tuple(
            Activity(
                f"A{i}",
                durations[i],
                (f"P{i}",) + (("Pshared",) if i in shared_people else ()),
                assignments[i],
                activity_windows[i],
            )
            for i in range(n)
        ),
        tuple(rules),
    )
    if label == "SAT":
        rule = {
            "blocked": BlockedInterval(
                "event", "participant", "P0", starts["A0"] + d - 1, starts["A0"] + d
            ),
            "deadline": Deadline("event", "A0", starts["A0"] + d - 1),
            "fixed_start": FixedStart("event", "A0", starts["A0"] - 1),
        }[event]
    else:
        rule = {
            "blocked": BlockedInterval(
                "event", "participant", "P0", base + d, base + 2 * d + 3
            ),
            "deadline": Deadline("event", "A0", base + d),
            "fixed_start": FixedStart("event", "A0", base),
        }[event]
    updated = replace(
        spec,
        constraints=tuple(c for c in spec.constraints if c.id != "old-event") + (rule,),
    )
    generation = replace(
        spec if label == "SAT" else updated, instance_id=ident + "-generation"
    )
    repair = replace(updated, instance_id=ident + "-repair", task_type="repair")
    return ident, spec, generation, repair, _schedule(starts)


def generate_development_v2(seed=3264, *, repetitions=1, reference_limits=None):
    """Balanced 144-case development matrix per repetition, with bounded selection.

    Three event types occur in every sweep/level/label cell. Never use model
    outcomes for selection. All exclusions and incomplete cells stay visible.
    """
    from collections import Counter
    from scheduling.solver import SolverLimits, solve
    from scheduling.validation import validate_schedule
    from scheduling.schema import RepairContext
    from scheduling.evaluation.manifests import structural_fingerprint

    if (
        type(seed) is not int
        or seed < 0
        or type(repetitions) is not int
        or not 1 <= repetitions <= 10
    ):
        raise ValueError("V2 requires a nonnegative seed and 1–10 repetitions")
    limits = reference_limits or SolverLimits(5, 0, 1)
    cases, records, exclusions, seen = [], {}, [], set()
    requested = 4 * 3 * 3 * 2 * 2 * repetitions
    constructed = 0
    for sweep in V2_SWEEPS:
        for level in range(3):
            for event in V2_EVENTS:
                for label in ("SAT", "UNSAT"):
                    for repeat in range(repetitions):
                        for retry in range(10):
                            serial = repeat * 10 + retry
                            group, original, gen, repair, witness = _v2_candidate(
                                seed, sweep, level, event, label, serial
                            )
                            constructed += 1
                            if not validate_schedule(original, witness).hard_feasible:
                                raise ValueError("Constructed original witness invalid")
                            old = solve(original, limits)
                            if not old.optimality_proven or old.schedule is None:
                                exclusions.append(
                                    {
                                        "candidate": group,
                                        "reason": "original_reference_unresolved",
                                        "status": old.status,
                                    }
                                )
                                continue
                            assert old.objectives.preference_penalty == 0
                            keys = {
                                structural_fingerprint(s)
                                for s in (original, gen, repair)
                            }
                            if keys & seen:
                                exclusions.append(
                                    {
                                        "candidate": group,
                                        "reason": "related_hard_structure_already_selected",
                                    }
                                )
                                continue
                            solved = [
                                solve(gen, limits),
                                solve(repair, limits, RepairContext(old.schedule)),
                            ]
                            if any(
                                r.status not in ("OPTIMAL", "INFEASIBLE")
                                for r in solved
                            ):
                                exclusions.append(
                                    {
                                        "candidate": group,
                                        "reason": "updated_reference_unresolved",
                                        "statuses": [r.status for r in solved],
                                    }
                                )
                                continue
                            if any(
                                (r.status == "OPTIMAL") != (label == "SAT")
                                for r in solved
                            ):
                                raise ValueError(
                                    "Constructed label disagrees with solver"
                                )
                            for spec, result in zip((gen, repair), solved):
                                is_repair = spec.task_type == "repair"
                                case = BenchmarkCase(
                                    spec.instance_id,
                                    group,
                                    "development",
                                    "controlled",
                                    sweep,
                                    str(level),
                                    spec,
                                    original if is_repair else None,
                                    old.schedule if is_repair else None,
                                    event if is_repair else None,
                                    result.schedule,
                                    label,
                                    (
                                        result.objectives.as_tuple()
                                        if result.schedule
                                        else None
                                    ),
                                    "SAT: independently checked witness and exact reference objective. UNSAT: A0 and fixed A1 require overlapping Rpair slots despite nonempty unary domains. Human review pending.",
                                )
                                cases.append(case)
                                records[case.case_id] = {
                                    "creation_method": "procedural",
                                    "code_authorship": "AI-assisted",
                                    "generation_seed": seed,
                                    "candidate_serial": serial,
                                    "event_type": event if is_repair else None,
                                    "construction_event": event,
                                    "gold_status": result.status,
                                    "gold_optimality_proven": result.optimality_proven,
                                    "reference_limits": {
                                        "time_limit_seconds": limits.time_limit_seconds,
                                        "random_seed": limits.random_seed,
                                        "num_workers": limits.num_workers,
                                    },
                                    "fixture_review": "pending",
                                    "language_review": "pending",
                                    "selection_reason": "predeclared_balanced_cell_without_model_outputs",
                                }
                            seen.update(keys)
                            break
                        else:
                            exclusions.append(
                                {
                                    "cell": [sweep, level, event, label, repeat],
                                    "reason": "quota_unfilled_after_10_candidates",
                                }
                            )
    selection = {
        "policy_version": "2.0",
        "policy": "Ten candidates per requested family; exclude unresolved references or prior hard fingerprints; never inspect model outcomes.",
        "requested_cases": requested,
        "selected_cases": len(cases),
        "constructed_families": constructed,
        "excluded_candidates": sum("candidate" in r for r in exclusions),
        "exclusions": exclusions,
        "quota_complete": len(cases) == requested,
        "repair_event_counts": dict(Counter(c.event for c in cases if c.context)),
    }
    return tuple(cases), records, selection
