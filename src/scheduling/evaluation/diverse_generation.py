"""Bounded, structurally varied generation challenge; no provider calls.

Ten generator mechanisms remain ten conservative construction families. A local
UNSAT certificate is not evidence of difficult global infeasibility search.
"""
from collections import Counter
from dataclasses import fields, replace
import hashlib
from pathlib import Path
import random

from scheduling.evaluation.balanced_generation import _unary_starts, profile, verify_certificate as verify_arithmetic_certificate
from scheduling.evaluation.benchmark import difficulty, render
from scheduling.evaluation.cases import AuthoredBenchmarkCase, AuthoredRendering, BenchmarkCase, case_bundle
from scheduling.evaluation.manifests import structural_audit, structural_fingerprint
from scheduling.evaluation.scoring import digest
from scheduling.schema import (Activity, Deadline, Entity, FixedStart, Precedence,
    PreferredStart, ProblemSpec, ReleaseTime, Schedule, Window, to_data)
from scheduling.validation import validate_schedule

VERSION = "diverse-generation-v1"
DEFAULT_SEED = 32661017
CAMPAIGN_POLICY = "diverse-generation-campaign-1"
MODELS = ("qwen3.6:35b", "x-test-1")
EXPECTED_RESPONSE_MODELS = {"qwen3.6:35b": "qwen3.6:35b", "x-test-1": "glm-5.3-flash"}
CALLS = {"controlled": 2000}
MECHANISMS = ("room_contention", "participant_contention", "fragmented_packing",
    "precedence_chain", "precedence_fork_join", "appointment_collision",
    "release_deadline_chain", "participant_crossing", "resource_person_crossing",
    "mixed_order_resource")
STRATA = ("easy", "moderate", "hard", "very_hard", "extreme")
TIERS = STRATA
SIZES = dict(zip(STRATA, (8, 12, 16, 24, 32)))
HORIZONS = dict(zip(STRATA, (16, 20, 24, 28, 32)))
PAIRS_PER_CELL = 10
CERTIFICATE_MAX_NODES = 200000
COUNTS = {"unique_cases": 1000, "SAT": 500, "UNSAT": 500,
    "construction_families": 10, "matched_label_pairs": 500,
    "scheduling_attempts_per_model": 2000, "both_models_scheduling_attempts": 4000,
    "default_rendering": "canonical", "additional_wording_attempts": 0,
    "optional_wording_variants": 24}
BUDGET_PER_MODEL = {"scheduling_completions": 2000, "capability_completions": 2,
    "metadata_requests": 1, "total_http_requests": 2003,
    "max_output_tokens_per_completion": 32768, "reserved_output_tokens": 2002 * 32768,
    "input_tokens_additional": True, "connect_timeout_seconds": 30,
    "read_timeout_seconds": 1800, "retries": 0}


def induced_feasibility(spec, activity_ids, *, max_nodes=CERTIFICATE_MAX_NODES):
    """Independent finite-domain enumeration of an induced hard subproblem.

    It uses primitive arithmetic domains, pairwise resource/participant overlap
    and precedence only. Omitting outside activities weakens constraints, so a
    proved UNSAT subset implies whole-problem UNSAT. Exhaustion is UNKNOWN.
    """
    activities = {a.id: a for a in spec.activities}
    if (type(max_nodes) is not int or not 1 <= max_nodes <= CERTIFICATE_MAX_NODES
            or not isinstance(activity_ids, (tuple, list)) or not 1 <= len(activity_ids) <= 6
            or any(not isinstance(a, str) for a in activity_ids)
            or len(set(activity_ids)) != len(activity_ids) or not set(activity_ids) <= activities.keys()):
        raise ValueError("Invalid bounded certificate domain")
    ids = tuple(activity_ids)
    domains = {a: _unary_starts(spec, activities[a]) for a in ids}
    edges = {(c.before, c.after) for c in spec.constraints if isinstance(c, Precedence)
             and c.before in ids and c.after in ids}
    assignment, nodes = {}, 0

    def compatible(a, start, b, other):
        aa, bb = activities[a], activities[b]
        end, other_end = start + aa.duration_slots, other + bb.duration_slots
        if ((a, b) in edges and end > other) or ((b, a) in edges and other_end > start):
            return False
        shared = (set(aa.participant_ids) & set(bb.participant_ids)
                  or set(aa.resource_ids) & set(bb.resource_ids))
        return not shared or end <= other or other_end <= start

    def search():
        nonlocal nodes
        if len(assignment) == len(ids):
            return "SAT"
        remaining = {}
        for a in ids:
            if a not in assignment:
                remaining[a] = [s for s in domains[a] if all(
                    compatible(a, s, b, t) for b, t in assignment.items())]
                if not remaining[a]:
                    return "UNSAT"
        a = min(remaining, key=lambda x: (len(remaining[x]), x))
        for start in remaining[a]:
            if nodes >= max_nodes:
                return "UNKNOWN"
            nodes += 1
            assignment[a] = start
            result = search()
            del assignment[a]
            if result != "UNSAT":
                return result
        return "UNSAT"

    status = search()
    return {"status": status, "visited_nodes": nodes}


def verify_certificate(spec, certificate, witness=None):
    if not isinstance(certificate, dict):
        return False
    if certificate.get("kind") == "capacity":
        return verify_arithmetic_certificate(spec, certificate, witness)
    if certificate == {"kind": "sat_witness"}:
        return validate_schedule(spec, witness).hard_feasible
    if (set(certificate) != {"kind", "activity_ids", "max_nodes"}
            or certificate.get("kind") != "induced_exhaustion"
            or certificate.get("max_nodes") != CERTIFICATE_MAX_NODES):
        return False
    try:
        return induced_feasibility(spec, certificate["activity_ids"],
                                   max_nodes=certificate["max_nodes"])["status"] == "UNSAT"
    except ValueError:
        return False


def _core(mechanism, rng, label):
    """Return a paired numeric core plus the SAT construction schedule.

    Windows and rule numeric values may differ across labels; types, counts,
    durations, resource incidence and precedence topology do not.
    """
    unsat = label == "UNSAT"
    d = [rng.choice((2, 3)) for _ in range(4)]
    if sum(d) > 10:
        d = [2, 2, 3, 3]
    assignments = [("P1",), ("P2",), ("P1",), ("P2",)]
    rooms = [(), (), (), ()]
    starts = [0, d[0], d[0] + d[1], sum(d[:3])]
    windows = [(Window(0, sum(d)),)] * 4
    rules = []
    if mechanism in ("room_contention", "participant_contention"):
        if mechanism == "room_contention":
            rooms = [("R1",)] * 4
        else:
            assignments = [("P1",)] * 4
        slack = rng.randrange(0, 3)
        limit = sum(d) - int(unsat) + (0 if unsat else slack)
        windows = [(Window(0, limit),)] * 4
    elif mechanism == "fragmented_packing":
        # Two disconnected windows: aggregate time is sufficient in UNSAT but
        # each window fits only one of three mandatory indivisible activities.
        width = rng.choice((2, 3))
        d = [width] * 3
        assignments = [("P1",), ("P2",), ("P1",)]
        rooms = [("R1",)] * 3
        first_end = 2 * width - int(unsat)
        windows = [(Window(0, first_end), Window(2 * width + 1, 4 * width))] * 3
        starts = [0, width, 2 * width + 1]
    elif mechanism in ("precedence_chain", "release_deadline_chain"):
        offset = rng.choice((1, 2)) if mechanism == "release_deadline_chain" else 0
        starts = [s + offset for s in starts]
        end = offset + sum(d)
        windows = [(Window(offset, end + 1),)] * 4
        rules += [Precedence(f"C{i}", f"A{i + 1}", f"A{i + 2}") for i in range(3)]
        if mechanism == "release_deadline_chain":
            rules.append(ReleaseTime("C_release", "A1", offset))
            rules.append(Deadline("C_mid", "A2", starts[2]))
        rules.append(Deadline("C_end", "A4", end - int(unsat)))
    elif mechanism == "precedence_fork_join":
        starts = [0, d[0], d[0], d[0] + max(d[1], d[2])]
        assignments = [("P1",), ("P1",), ("P2",), ("P1",)]
        end = starts[3] + d[3]
        windows = [(Window(0, end + 1),)] * 4
        rules += [Precedence(f"C{i}", f"A{a + 1}", f"A{b + 1}")
                  for i, (a, b) in enumerate(((0, 1), (0, 2), (1, 3), (2, 3)))]
        rules.append(Deadline("C_end", "A4", end - int(unsat)))
    elif mechanism == "appointment_collision":
        d = d[:2]
        assignments = [("P1",)] * 2
        rooms = [(), ()]
        starts = [0, d[0]]
        windows = [(Window(0, sum(d) + 2),)] * 2
        rules = [FixedStart("C_fixed0", "A1", 0),
                 FixedStart("C_fixed1", "A2", d[0] - int(unsat))]
    elif mechanism in ("participant_crossing", "resource_person_crossing"):
        width = rng.choice((2, 3))
        d = [width] * 3
        starts = [0, 0, width]
        assignments = [("P1",), ("P2",), ("P1", "P2")]
        rooms = [(), (), ()]
        if mechanism == "resource_person_crossing":
            assignments[2] = ("P1",)
            rooms = [(), ("R1",), ("R1",)]
        # The joint activity has an individually nonempty domain; complementary
        # occupied windows leave no common participant/resource intersection.
        windows = [(Window(0, width),),
                   (Window(width if unsat else 0, 2 * width if unsat else width),),
                   (Window(0, 2 * width),)]
    elif mechanism == "mixed_order_resource":
        d = [rng.choice((2, 3)), 2, 2, 2]
        assignments = [("P1",), ("P2",), ("P1",), ("P2",)]
        rooms = [("R1",), ("R1",), (), ()]
        starts = [0, d[0], d[0], d[0] + d[1]]
        end = max(starts[i] + d[i] for i in range(4))
        windows = [(Window(0, end),)] * 4
        rules = [Precedence("C0", "A1", "A3"), Precedence("C1", "A2", "A4"),
                 Deadline("C2", "A3", end - int(unsat)),
                 Deadline("C3", "A4", end - int(unsat))]
    else:
        raise ValueError("Unknown mechanism")
    return d, assignments, rooms, windows, starts, rules


def scope_horizon(mechanism, stratum):
    if mechanism in ("room_contention", "participant_contention"):
        return dict(zip(STRATA, (16, 24, 32, 40, 48)))[stratum]
    return HORIZONS[stratum]


def scope_start(mechanism, stratum):
    hour = "09" if stratum == "easy" else "00" if mechanism in ("room_contention", "participant_contention") else "07"
    return f"2026-10-26T{hour}:00:00+08:00"


def _global_capacity(seed, mechanism, stratum, index, label):
    """All mandatory activities share the bottleneck; no tiny embedded core.

    The UNSAT member has total mandatory demand exceeding common availability
    by one slot. This is global capacity reasoning, not claimed NP-hard search.
    """
    rng = random.Random(int(digest([VERSION, seed, mechanism, stratum, index]), 16))
    n, horizon = SIZES[stratum], scope_horizon(mechanism, stratum)
    durations = [rng.choice((1, 2)) for _ in range(n)]
    while sum(durations) > horizon:
        candidates = [i for i, d in enumerate(durations) if d > 1]
        durations[rng.choice(candidates)] -= 1
    demand = sum(durations)
    slack = rng.randrange(min(3, horizon - demand) + 1)
    limit = demand - 1 if label == "UNSAT" else demand + slack
    people_count = {8: 2, 12: 3, 16: 4, 24: 6, 32: 8}[n]
    room_count = 1 if n <= 12 else 2 if n <= 24 else 3
    full = (Window(0, horizon),)
    participants = [Entity(f"P{i + 1}", (Window(0, limit),) if mechanism == "participant_contention" and i == 0 else full)
                    for i in range(people_count)]
    resources = [Entity(f"R{i + 1}", (Window(0, limit),) if mechanism == "room_contention" and i == 0 else full)
                 for i in range(room_count)]
    activities, starts, rules = [], {}, []
    cursor = 0
    for i, duration in enumerate(durations):
        ident = f"A{i + 1}"
        starts[ident] = cursor
        if mechanism == "participant_contention":
            people = ("P1",) if i % people_count == 0 else ("P1", f"P{i % people_count + 1}")
            rooms = (f"R{rng.randrange(room_count) + 1}",) if i % 2 else ()
        else:
            people = (f"P{rng.randrange(people_count) + 1}",)
            rooms = ("R1",) if room_count == 1 or i % 3 else ("R1", f"R{rng.randrange(1, room_count) + 1}")
        # Wide, varied unary windows avoid fixing a trivial full ordering. Every
        # window admits the constructed SAT schedule and at least one UNSAT start.
        lo = max(0, cursor - rng.randrange(1, max(3, horizon // 3)))
        hi = min(horizon, cursor + duration + rng.randrange(1, max(3, horizon // 3)))
        activities.append(Activity(ident, duration, people, rooms, (Window(lo, hi),)))
        if i >= 2 and rng.random() < .45:
            rules.append(Precedence(f"C_edge{i}", f"A{rng.randrange(i) + 1}", ident))
        cursor += duration
    if index % 4 in (1, 3):
        target = activities[n // 3]
        rules.append(Deadline("C_profile_deadline", target.id, starts[target.id] + target.duration_slots + 1))
    if index % 4 in (2, 3):
        rules.append(FixedStart("C_profile_fixed", activities[0].id, 0))
    for i, activity in enumerate(activities):
        if i % 2 == index % 2:
            preferred = rng.randrange(max(1, horizon - 4))
            rules.append(PreferredStart(f"PREF{i}", activity.id, preferred,
                                        min(horizon, preferred + rng.choice((2, 4, 6))), rng.choice((1, 2, 3))))
    names = [f"A{i + 1}" for i in range(n)]
    rng.shuffle(names)
    rename = {f"A{i + 1}": names[i] for i in range(n)}
    activities = [replace(a, id=rename[a.id]) for a in activities]
    rules = [replace(c, before=rename[c.before], after=rename[c.after]) if isinstance(c, Precedence)
             else replace(c, activity_id=rename[c.activity_id]) for c in rules]
    starts = {rename[a]: start for a, start in starts.items()}
    rng.shuffle(activities)
    rng.shuffle(rules)
    pair_id = "dg-pair-" + digest([VERSION, seed, mechanism, stratum, index])[:20]
    case_id = "dg-" + digest([pair_id, label])[:24]
    group_id = "diverse-family-" + mechanism.replace("_", "-")
    spec = ProblemSpec("1.0", case_id, "generation", horizon, 30,
        scope_start(mechanism, stratum), "+08:00", tuple(participants), tuple(resources), tuple(activities), tuple(rules))
    witness = Schedule.from_list([{"activity_id": a, "start_slot": start} for a, start in starts.items()])
    case = BenchmarkCase(case_id, group_id, "development", "controlled", mechanism, stratum,
        spec, witness=witness if label == "SAT" else None, expected_label=label,
        justification="Whole-instance shared-capacity pair with independent arithmetic certificate; human review pending.")
    cert = ({"kind": "sat_witness"} if label == "SAT" else
            {"kind": "capacity", "target_kind": "resource" if mechanism == "room_contention" else "participant",
             "target_id": "R1" if mechanism == "room_contention" else "P1", "activity_ids": sorted(starts)})
    return case, cert, pair_id


def _construct(seed, mechanism, stratum, index, label):
    if mechanism in ("room_contention", "participant_contention"):
        return _global_capacity(seed, mechanism, stratum, index, label)
    rng = random.Random(int(digest([VERSION, seed, mechanism, stratum, index]), 16))
    n, horizon = SIZES[stratum], HORIZONS[stratum]
    people_count = {8: 2, 12: 3, 16: 4, 24: 6, 32: 8}[n]
    room_count = 1 if n <= 12 else 2 if n <= 24 else 3
    d, people, rooms, windows, starts, rules = _core(mechanism, rng, label)
    core_count = len(d)
    # Core construction consumes identical RNG calls on paired labels.
    full = (Window(0, horizon),)
    activities = [Activity(f"A{i + 1}", d[i], people[i], rooms[i], windows[i]) for i in range(core_count)]
    witness_starts = {f"A{i + 1}": starts[i] for i in range(core_count)}
    # Unsat unary edits never drive background generation: use the SAT witness
    # geometry, retaining exact incidence/type/count pairing.
    occupied = {f"P{i + 1}": [] for i in range(people_count)}
    room_busy = {f"R{i + 1}": [] for i in range(room_count)}
    for i in range(core_count):
        for p in people[i]:
            occupied[p].append((starts[i], starts[i] + d[i]))
        for r in rooms[i]:
            room_busy[r].append((starts[i], starts[i] + d[i]))
    for i in range(core_count, n):
        duration = rng.choice((2, 2, 3))
        predecessors = list(range(i))
        rng.shuffle(predecessors)
        choices = []
        for predecessor in predecessors:
            earliest = witness_starts[f"A{predecessor + 1}"] + activities[predecessor].duration_slots
            for p in occupied:
                for start in range(earliest, horizon - duration + 1):
                    if all(start + duration <= a or start >= b for a, b in occupied[p]):
                        choices.append((start, rng.random(), p))
                        break
            if choices:
                break
        if not choices:
            raise ValueError("Construction exhausted the bounded calendar")
        start, _, p = min(choices)
        entity_ids = [p]
        if n >= 16 and rng.random() < .35:
            candidates = [other for other in occupied if other != p and all(
                start + duration <= a or start >= b for a, b in occupied[other])]
            if candidates:
                entity_ids.append(rng.choice(candidates))
        resource_ids = []
        candidates = [r for r in room_busy if all(start + duration <= a or start >= b for a, b in room_busy[r])]
        if candidates and rng.random() < .7:
            resource_ids.append(rng.choice(candidates))
        lo = max(0, start - rng.randrange(0, 3 + STRATA.index(stratum)))
        hi = min(horizon, start + duration + rng.randrange(0, 3 + STRATA.index(stratum)))
        availability = (Window(lo, hi),)
        # Additional disjoint windows offer genuine alternatives, not aliases.
        if i % 4 == 0 and lo >= duration + 2:
            availability = (Window(0, duration + 1), Window(lo, hi))
        ident = f"A{i + 1}"
        activities.append(Activity(ident, duration, tuple(sorted(entity_ids)), tuple(resource_ids), availability))
        witness_starts[ident] = start
        for entity in entity_ids:
            occupied[entity].append((start, start + duration))
        for entity in resource_ids:
            room_busy[entity].append((start, start + duration))
        # Every added activity is coupled by a mandatory precedence edge to the
        # existing network; large tiers are not disconnected filler text.
        rules.append(Precedence(f"C_bg{i}", f"A{predecessor + 1}", ident))
        earlier = [j for j in range(i) if witness_starts[f"A{j + 1}"] + activities[j].duration_slots <= start and j != predecessor]
        if earlier and i % 3 == 0:
            rules.append(Precedence(f"C_extra{i}", f"A{rng.choice(earlier) + 1}", ident))
    # Presence profiles cycle evenly in each label; mandatory core rules may
    # constrain which profiles are possible, but can never predict the label.
    if index % 4 in (1, 3):
        target = activities[-1]
        rules.append(Deadline("C_profile_deadline", target.id,
                              witness_starts[target.id] + target.duration_slots))
    if index % 4 in (2, 3):
        target = activities[-2]
        rules.append(FixedStart("C_profile_fixed", target.id, witness_starts[target.id]))
    for i, activity in enumerate(activities):
        if i % 2 == index % 2:
            preferred = rng.randrange(0, max(1, horizon - 4))
            rules.append(PreferredStart(f"PREF{i}", activity.id, preferred,
                                        min(horizon, preferred + rng.choice((2, 4, 6))), rng.choice((1, 2, 3))))
    names = [f"A{i + 1}" for i in range(n)]
    rng.shuffle(names)
    rename = {f"A{i + 1}": names[i] for i in range(n)}
    activities = [replace(a, id=rename[a.id]) for a in activities]
    renamed_rules = []
    for rule in rules:
        if isinstance(rule, Precedence):
            renamed_rules.append(replace(rule, before=rename[rule.before], after=rename[rule.after]))
        else:
            renamed_rules.append(replace(rule, activity_id=rename[rule.activity_id]))
    rules = renamed_rules
    witness_starts = {rename[a]: start for a, start in witness_starts.items()}
    rng.shuffle(activities)
    rng.shuffle(rules)
    pair_id = "dg-pair-" + digest([VERSION, seed, mechanism, stratum, index])[:20]
    # group_id deliberately retains the coarse generator family for inference;
    # matched-pair IDs live in proofs, not an inflated independence declaration.
    group_id = "diverse-family-" + mechanism.replace("_", "-")
    case_id = "dg-" + digest([pair_id, label])[:24]
    spec = ProblemSpec("1.0", case_id, "generation", horizon, 30,
        scope_start(mechanism, stratum), "+08:00",
        tuple(Entity(p, full) for p in occupied), tuple(Entity(r, full) for r in room_busy),
        tuple(activities), tuple(rules))
    witness = Schedule.from_list([{"activity_id": a, "start_slot": s} for a, s in witness_starts.items()])
    case = BenchmarkCase(case_id, group_id, "development", "controlled", mechanism, stratum,
        spec, witness=witness if label == "SAT" else None, expected_label=label,
        justification="Constructed paired scheduling challenge; independent arithmetic feasibility evidence; human meaning review pending.")
    cert = ({"kind": "sat_witness"} if label == "SAT" else
            {"kind": "induced_exhaustion", "activity_ids": [rename[f"A{i + 1}"] for i in range(core_count)],
             "max_nodes": CERTIFICATE_MAX_NODES})
    return case, cert, pair_id


def _authored(case):
    return AuthoredBenchmarkCase(**{f.name: getattr(case, f.name) for f in fields(BenchmarkCase)},
        authored_renderings=tuple(AuthoredRendering(v, render(case, v, 3263).text,
            "llm_assisted", VERSION, "Complete deterministic templates; independent human meaning review pending.")
            for v in ("canonical", "reordered")), gold_author_reference=VERSION)


def optional_wording_selection(cases):
    """24 pre-outcome variants, round-robin across mechanism/size/label strata."""
    pairs = {}
    for case in cases:
        key = (case.sweep, case.level, digest(_paired_signature(case.problem)))
        pairs.setdefault(key, []).append(case)
    selected, used = [], set()
    for k in range(12):
        mechanism = MECHANISMS[k % len(MECHANISMS)]
        stratum = STRATA[(k // len(MECHANISMS) + k) % len(STRATA)]
        key = next(key for key in sorted(pairs) if key[:2] == (mechanism, stratum) and key not in used)
        used.add(key)
        pair = pairs[key]
        if len(pair) != 2 or {c.expected_label for c in pair} != {"SAT", "UNSAT"}:
            raise ValueError("Wording selection lost matched label pairing")
        selected.extend({"case_id": case.case_id, "variant_id": "reordered"}
                        for case in sorted(pair, key=lambda c: c.expected_label))
    return selected


def _paired_signature(spec):
    return {"activities": [(a.id, a.duration_slots, a.participant_ids, a.resource_ids, len(a.availability)) for a in spec.activities],
            "entity_counts": [len(spec.participants), len(spec.resources)],
            "constraints": [(c.kind, getattr(c, "activity_id", None), getattr(c, "before", None),
                              getattr(c, "after", None)) for c in spec.constraints]}


def normalized_hard_fingerprint(spec):
    """Ignore IDs, list order, preferences, dates and a uniform slot-origin shift.

    The existing colored graph fingerprint is conservative, not a mathematical
    equivalence prover. Uniform shifting includes entity windows and the horizon.
    """
    bounds = [w.start for row in (*spec.participants, *spec.resources, *spec.activities)
              for w in row.availability]
    bounds += [c.slot for c in spec.constraints if isinstance(c, (ReleaseTime, Deadline, FixedStart))]
    origin = min(bounds, default=0)
    if not origin:
        return structural_fingerprint(spec)
    def windows(row):
        return replace(row, availability=tuple(Window(w.start - origin, w.end - origin) for w in row.availability))
    rules = tuple(replace(c, slot=c.slot - origin) if isinstance(c, (ReleaseTime, Deadline, FixedStart)) else c
                  for c in spec.constraints if not isinstance(c, PreferredStart))
    shifted = replace(spec, horizon_slots=spec.horizon_slots - origin,
                      participants=tuple(windows(p) for p in spec.participants),
                      resources=tuple(windows(r) for r in spec.resources),
                      activities=tuple(windows(a) for a in spec.activities), constraints=rules)
    return structural_fingerprint(shifted)


def topology_fingerprint(spec):
    """Describe hard incidence/precedence topology with all numeric bounds erased."""
    window = (Window(0, 1),)
    rules = []
    for rule in spec.constraints:
        if isinstance(rule, Precedence):
            rules.append(rule)
        elif isinstance(rule, (ReleaseTime, Deadline, FixedStart)):
            rules.append(replace(rule, slot=1 if isinstance(rule, Deadline) else 0))
    reduced = replace(spec, horizon_slots=1,
        participants=tuple(replace(p, availability=window) for p in spec.participants),
        resources=tuple(replace(r, availability=window) for r in spec.resources),
        activities=tuple(replace(a, duration_slots=1, availability=window) for a in spec.activities),
        constraints=tuple(rules))
    return structural_fingerprint(reduced)


def interaction_components(spec):
    adjacent = {a.id: set() for a in spec.activities}
    for i, a in enumerate(spec.activities):
        for b in spec.activities[i + 1:]:
            if set(a.participant_ids) & set(b.participant_ids) or set(a.resource_ids) & set(b.resource_ids):
                adjacent[a.id].add(b.id)
                adjacent[b.id].add(a.id)
    for c in spec.constraints:
        if isinstance(c, Precedence):
            adjacent[c.before].add(c.after)
            adjacent[c.after].add(c.before)
    unseen, sizes = set(adjacent), []
    while unseen:
        todo, component = [min(unseen)], set()
        while todo:
            current = todo.pop()
            if current not in component:
                component.add(current)
                todo.extend(adjacent[current] - component)
        unseen -= component
        sizes.append(len(component))
    return sorted(sizes, reverse=True)


def check_design(cases, proofs):
    cases = tuple(cases)
    expected = Counter({(m, s, label): PAIRS_PER_CELL for m in MECHANISMS for s in STRATA for label in ("SAT", "UNSAT")})
    if len(cases) != 1000 or len({c.case_id for c in cases}) != 1000:
        raise ValueError("Diverse generation requires 1000 unique cases")
    if Counter((c.sweep, c.level, c.expected_label) for c in cases) != expected:
        raise ValueError("Mechanism/stratum/label balance changed")
    pairs, fingerprints, topologies = {}, set(), {m: set() for m in MECHANISMS}
    for case in cases:
        spec = case.problem
        if (not isinstance(case, AuthoredBenchmarkCase) or case.kind != "controlled"
                or case.split != "development" or spec.task_type != "generation" or case.context
                or len(spec.activities) != SIZES[case.level] or spec.horizon_slots != scope_horizon(case.sweep, case.level)
                or spec.slot_minutes != 30 or spec.horizon_start != scope_start(case.sweep, case.level)
                or spec.timezone != "+08:00"):
            raise ValueError("Diverse generation scope changed")
        if any(not _unary_starts(spec, a) for a in spec.activities):
            raise ValueError("Unary-empty cases are outside the interaction challenge")
        key = normalized_hard_fingerprint(spec)
        if key in fingerprints:
            raise ValueError("Repeated normalized hard structure; names/objectives do not create new cases")
        fingerprints.add(key)
        topologies[case.sweep].add(topology_fingerprint(spec))
        if interaction_components(spec) != [len(spec.activities)]:
            raise ValueError("Every activity must join the coupled hard-constraint network")
        pair_id = proofs[case.case_id]["pair_id"]
        pairs.setdefault(pair_id, []).append(case)
        base = BenchmarkCase(**{f.name: getattr(case, f.name) for f in fields(BenchmarkCase)})
        if {r.variant_id for r in case.authored_renderings} != {"canonical", "reordered"}:
            raise ValueError("Missing declared renderings")
        for row in case.authored_renderings:
            if (row.text != render(base, row.variant_id, 3263).text or row.creation_method != "llm_assisted"
                    or row.author_reference != VERSION or row.review_status != "pending"):
                raise ValueError("Rendering meaning/provenance differs from complete templates")
            if any(token in row.text for token in (case.case_id, case.group_id, pair_id, VERSION, "UNSAT")):
                raise ValueError("Evaluator-only metadata leaked into public request")
    if len(pairs) != 500:
        raise ValueError("Expected 500 matched label pairs")
    for pair in pairs.values():
        if (len(pair) != 2 or {c.expected_label for c in pair} != {"SAT", "UNSAT"}
                or len({(c.sweep, c.level, c.group_id) for c in pair}) != 1
                or _paired_signature(pair[0].problem) != _paired_signature(pair[1].problem)):
            raise ValueError("Matched pair differs in constraint types, incidence or activity durations")
    if len({c.group_id for c in cases}) != 10:
        raise ValueError("Related pairs must remain in ten conservative construction families")
    return {"unique_cases": 1000, "SAT": 500, "UNSAT": 500,
        "construction_families": 10, "matched_label_pairs": 500, "unique_hard_structures": len(fingerprints),
        "certificate_label_counts": dict(Counter(proofs[c.case_id]["certificate"]["kind"] for c in cases)),
        "all_unary_domains_nonempty": True, "paired_constraint_types_and_counts_equal": True,
        "all_interaction_graphs_connected": True,
        "unique_topology_signatures": len(set().union(*topologies.values())),
        "topology_signatures_by_mechanism": {m: len(v) for m, v in topologies.items()},
        "geometry_by_stratum_label": {s: {label: {key: {"minimum": min(proofs[c.case_id]["difficulty"][key] for c in cases if c.level == s and c.expected_label == label), "maximum": max(proofs[c.case_id]["difficulty"][key] for c in cases if c.level == s and c.expected_label == label)} for key in ("mean_unary_slack", "interaction_density", "resource_contention")} for label in ("SAT", "UNSAT")} for s in STRATA},
        "profile_label_counts": {p: dict(Counter(c.expected_label for c in cases if profile(c.problem) == p))
                                  for p in sorted({profile(c.problem) for c in cases})},
        "mechanism_label_counts": {m: dict(Counter(c.expected_label for c in cases if c.sweep == m)) for m in MECHANISMS},
        "stratum_label_counts": {s: dict(Counter(c.expected_label for c in cases if c.level == s)) for s in STRATA}}


def verify_suite(cases, proofs):
    cases = tuple(cases)
    if not isinstance(proofs, dict) or set(proofs) != {c.case_id for c in cases}:
        raise ValueError("Proof membership differs from cases")
    keys = {"problem_sha256", "pair_id", "certificate", "construction_witness", "independent_certificate_checked",
            "reference_status", "reference_optimality_proven", "expected_objective", "difficulty"}
    for case in cases:
        row = proofs[case.case_id]
        if not isinstance(row, dict) or set(row) != keys or row["problem_sha256"] != digest(case.problem):
            raise ValueError("Proof fields or problem binding differ")
        if (row["independent_certificate_checked"] is not True
                or not verify_certificate(case.problem, row["certificate"], row["construction_witness"])
                or row["difficulty"] != difficulty(case.problem)):
            raise ValueError("Independent certificate or difficulty evidence failed")
        if case.expected_label == "SAT":
            actual = validate_schedule(case.problem, case.witness)
            if (row["certificate"] != {"kind": "sat_witness"} or not actual.hard_feasible
                    or row["reference_status"] != "OPTIMAL" or row["reference_optimality_proven"] is not True
                    or not isinstance(row["expected_objective"], list)
                    or tuple(row["expected_objective"]) != case.expected_objective
                    or actual.objectives.as_tuple() != case.expected_objective):
                raise ValueError("SAT reference evidence inconsistent")
        elif (row["certificate"].get("kind") not in ("induced_exhaustion", "capacity") or case.witness is not None
                or case.expected_objective is not None or row["construction_witness"] is not None
                or row["reference_status"] != "INFEASIBLE" or row["reference_optimality_proven"] is not False
                or row["expected_objective"] is not None):
            raise ValueError("UNSAT reference evidence inconsistent")
    coverage = check_design(cases, proofs)
    coverage["independently_checked_certificates"] = len(cases)
    return coverage


def validate_manifest(cases, proofs, manifest):
    cases = tuple(cases)
    coverage = verify_suite(cases, proofs)
    expected = {"format_version": "1.0", "dataset_version": VERSION, "campaign_policy": CAMPAIGN_POLICY,
        "case_bundle_sha256": digest(case_bundle(cases)), "proofs_sha256": digest(proofs), "coverage": coverage,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "counts": COUNTS, "models": list(MODELS), "expected_response_models": EXPECTED_RESPONSE_MODELS,
        "budget_per_model": BUDGET_PER_MODEL, "structural_audit": structural_audit(cases),
        "optional_wording_selection": optional_wording_selection(cases), "new_model_calls": 0}
    if not isinstance(manifest, dict) or any(manifest.get(k) != v for k, v in expected.items()):
        raise ValueError("Diverse manifest differs from source-bound independently verified dataset")
    return coverage


def build_suite(seed=DEFAULT_SEED, reference_seconds=60):
    from scheduling.solver import SolverLimits, solve
    cases, proofs = [], {}
    for mechanism in MECHANISMS:
        for stratum in STRATA:
            for index in range(PAIRS_PER_CELL):
                for label in ("SAT", "UNSAT"):
                    case, cert, pair_id = _construct(seed, mechanism, stratum, index, label)
                    construction = to_data(case.witness)
                    if not verify_certificate(case.problem, cert, case.witness):
                        raise ValueError(f"Independent construction certificate failed: {mechanism}/{stratum}/{index}/{label}")
                    reference = solve(case.problem, SolverLimits(reference_seconds))
                    if label == "SAT":
                        if not reference.optimality_proven or reference.schedule is None:
                            raise ValueError(f"Reference optimum unresolved: {mechanism}/{stratum}/{index}")
                        case = replace(case, witness=reference.schedule, expected_objective=reference.objectives.as_tuple())
                    elif reference.status != "INFEASIBLE":
                        raise ValueError("Reference disagrees with independent UNSAT certificate")
                    cases.append(_authored(case))
                    proofs[case.case_id] = {"problem_sha256": digest(case.problem), "pair_id": pair_id,
                        "certificate": cert, "construction_witness": construction, "independent_certificate_checked": True,
                        "reference_status": reference.status, "reference_optimality_proven": reference.optimality_proven,
                        "expected_objective": list(case.expected_objective) if case.expected_objective is not None else None,
                        "difficulty": difficulty(case.problem)}
    result = tuple(cases)
    verify_suite(result, proofs)
    return result, proofs
