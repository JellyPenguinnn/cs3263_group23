"""Counterbalanced, bounded generation confirmation; entirely offline.

This is AI-assisted development data, not a human-reviewed or held-out test set.
SAT/UNSAT pairs differ in numeric availability, not constraint-type presence.
Arithmetic certificates never call the compiler or its domain helpers.
"""

from collections import Counter
from dataclasses import fields, replace
import hashlib
from pathlib import Path
import random

from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import AuthoredBenchmarkCase, AuthoredRendering, BenchmarkCase, case_bundle
from scheduling.evaluation.scoring import digest
from scheduling.schema import (
    Activity, BlockedInterval, Deadline, Entity, FixedStart, Precedence,
    PreferredStart, ProblemSpec, ReleaseTime, Schedule, Window, to_data,
)
from scheduling.validation import validate_schedule

VERSION = "balanced-generation-v1"
DEFAULT_SEED = 32661015
CAMPAIGN_POLICY = "balanced-generation-campaign-1"
CALLS = {"controlled": 96}
MODELS = ("qwen3.6:35b", "x-test-1")
EXPECTED_RESPONSE_MODELS = {"qwen3.6:35b": "qwen3.6:35b", "x-test-1": "glm-5.3-flash"}
COUNTS = {"unique_cases": 48, "construction_families": 3, "matched_label_pairs": 24,
          "scheduling_attempts_per_model": 96, "both_models_scheduling_attempts": 192,
          "default_rendering": "canonical", "additional_wording_attempts": 0}
BUDGET_PER_MODEL = {
    "scheduling_completions": 96, "capability_completions": 2,
    "metadata_requests": 1, "total_http_requests": 99,
    "max_output_tokens_per_completion": 32768, "reserved_output_tokens": 98 * 32768,
    "input_tokens_additional": True, "connect_timeout_seconds": 30,
    "read_timeout_seconds": 1800, "retries": 0,
}
MECHANISMS = ("resource_capacity", "participant_capacity", "precedence_interaction")
LAYOUTS = ("loose", "tight")
PROFILES = ("neither", "deadline", "fixed_start", "both")


def profile(spec):
    kinds = {c.kind for c in spec.constraints}
    return ("both" if {"deadline", "fixed_start"} <= kinds else
            "deadline" if "deadline" in kinds else
            "fixed_start" if "fixed_start" in kinds else "neither")


def _unary_starts(spec, activity):
    """Enumerate unary feasibility from primitive arithmetic, independent of CP-SAT."""
    people = {p.id: p for p in spec.participants}
    rooms = {r.id: r for r in spec.resources}
    windows = [activity.availability]
    windows += [people[p].availability for p in activity.participant_ids]
    windows += [rooms[r].availability for r in activity.resource_ids]
    allowed = []
    for start in range(spec.horizon_slots - activity.duration_slots + 1):
        end = start + activity.duration_slots
        if not all(any(w.start <= start and end <= w.end for w in ws) for ws in windows):
            continue
        valid = True
        for rule in spec.constraints:
            if type(rule) is ReleaseTime and rule.activity_id == activity.id:
                valid &= start >= rule.slot
            elif type(rule) is Deadline and rule.activity_id == activity.id:
                valid &= end <= rule.slot
            elif type(rule) is FixedStart and rule.activity_id == activity.id:
                valid &= start == rule.slot
            elif isinstance(rule, BlockedInterval):
                required = (activity.participant_ids if rule.target_kind == "participant"
                            else activity.resource_ids)
                if rule.target_id in required:
                    valid &= end <= rule.start or start >= rule.end
        if valid:
            allowed.append(start)
    return tuple(allowed)


def verify_certificate(spec, certificate, witness=None):
    """Return whether a bounded, input-derived feasibility certificate is valid."""
    if not isinstance(certificate, dict):
        return False
    kind = certificate.get("kind")
    if kind == "sat_witness":
        return set(certificate) == {"kind"} and validate_schedule(spec, witness).hard_feasible
    expected = ({"kind", "target_kind", "target_id", "activity_ids"} if kind == "capacity"
                else {"kind", "activity_ids"} if kind == "precedence_window" else set())
    if not expected or set(certificate) != expected:
        return False
    ids = certificate["activity_ids"]
    activities = {a.id: a for a in spec.activities}
    if (not isinstance(ids, list) or not ids or any(not isinstance(a, str) for a in ids)
            or len(set(ids)) != len(ids) or not set(ids) <= activities.keys()):
        return False
    domains = {a: _unary_starts(spec, activities[a]) for a in ids}
    if any(not domain for domain in domains.values()):
        return False
    demand = sum(activities[a].duration_slots for a in ids)
    if kind == "capacity":
        if certificate["target_kind"] not in ("participant", "resource"):
            return False
        target = certificate["target_id"]
        if not isinstance(target, str) or any(target not in (
                activities[a].participant_ids if certificate["target_kind"] == "participant"
                else activities[a].resource_ids) for a in ids):
            return False
        occupied = {slot for a in ids for start in domains[a]
                    for slot in range(start, start + activities[a].duration_slots)}
        return demand > len(occupied)
    edges = {(c.before, c.after) for c in spec.constraints if isinstance(c, Precedence)}
    if any((a, b) not in edges for a, b in zip(ids, ids[1:])):
        return False
    earliest = min(domains[ids[0]])
    latest = max(domains[ids[-1]]) + activities[ids[-1]].duration_slots
    return demand > latest - earliest


def _schedule(starts):
    return Schedule.from_list([{"activity_id": a, "start_slot": s} for a, s in starts.items()])


def _construct(seed, mechanism, layout, constraint_profile, label):
    rng = random.Random(int(digest([VERSION, seed, mechanism, layout]), 16))
    names = [f"A{i + 1}" for i in range(8)]
    rng.shuffle(names)
    name = dict(enumerate(names))
    group = "balanced-family-" + digest([VERSION, seed, mechanism])[:20]
    case_id = "bg-" + digest([VERSION, seed, mechanism, layout, constraint_profile, label])[:24]
    full = (Window(0, 16),)
    offset = 0 if layout == "loose" else 2
    capacity = 14 if layout == "loose" else 12
    restricted = (Window(offset, offset + (capacity if label == "SAT" else 11)),)
    people = [Entity("P1", full), Entity("P2", full)]
    rooms = [Entity("R1", full)]
    durations = (2, 4, 2, 4, 2, 2, 2, 2)
    assignments = (0, 1, 0, 1, 0, 1, 0, 1)
    room_users = {0, 1, 2, 3}
    windows = [full] * 8
    starts = {0: offset, 1: offset + 2, 2: offset + 6, 3: offset + 8,
              4: offset + 2, 5: 0, 6: 14, 7: 12 if layout == "loose" else 2}
    rules = []
    deadline_slot, deadline_counterexample = 14, 14
    if mechanism == "resource_capacity":
        rooms[0] = Entity("R1", restricted)
        certificate = {"kind": "capacity", "target_kind": "resource", "target_id": "R1",
                       "activity_ids": [name[i] for i in range(4)]}
    elif mechanism == "participant_capacity":
        people[0] = Entity("P1", restricted)
        assignments = (0, 0, 0, 0, 1, 1, 1, 1)
        room_users = {0, 2, 4, 5}
        starts.update({4: offset + 2, 5: offset + 8, 7: 0})
        deadline_slot, deadline_counterexample = 10, 12
        certificate = {"kind": "capacity", "target_kind": "participant", "target_id": "P1",
                       "activity_ids": [name[i] for i in range(4)]}
    elif mechanism == "precedence_interaction":
        room_users = {0, 2, 5}
        windows[:4] = [restricted] * 4
        starts.update({5: 12 if layout == "loose" else 0, 7: 0 if layout == "loose" else 2})
        rules += [Precedence(f"C{i + 1}", name[i], name[i + 1]) for i in range(3)]
        deadline_slot, deadline_counterexample = 10, 14
        certificate = {"kind": "precedence_window", "activity_ids": [name[i] for i in range(4)]}
    else:
        raise ValueError("Unknown construction mechanism")
    activities = tuple(Activity(name[i], durations[i], (f"P{assignments[i] + 1}",),
                                ("R1",) if i in room_users else (), windows[i]) for i in range(8))
    if constraint_profile in ("deadline", "both"):
        rules.append(Deadline("C20", name[7], deadline_slot))
    if constraint_profile in ("fixed_start", "both"):
        rules.append(FixedStart("C21", name[6], 14))
    rules += [PreferredStart(f"C{30 + i}", name[i], 0, 6, 1) for i in range(8)]
    spec = ProblemSpec("1.0", case_id, "generation", 16, 30, "2026-10-26T09:00:00+08:00",
                       "+08:00", tuple(people), tuple(rooms), activities, tuple(rules))
    witness = _schedule({name[i]: s for i, s in starts.items()}) if label == "SAT" else None
    operative = {}
    if label == "SAT":
        certificate = {"kind": "sat_witness"}
        for kind, rule_id, activity, bad_start in (
                ("deadline", "C20", 7, deadline_counterexample), ("fixed_start", "C21", 6, 12)):
            if any(c.id == rule_id for c in rules):
                altered = dict(starts)
                altered[activity] = bad_start
                operative[kind] = {"constraint_id": rule_id, "counterexample_schedule":
                                   to_data(_schedule({name[i]: s for i, s in altered.items()}))}
    case = BenchmarkCase(case_id, group, "development", "controlled", mechanism, layout, spec,
                         witness=witness, expected_label=label,
                         justification="Input-derived arithmetic feasibility certificate; matched constraint-type design; human review pending.")
    return case, certificate, operative


def _authored(case):
    texts = ((variant, render(case, variant, 3263).text) for variant in ("canonical", "reordered"))
    return AuthoredBenchmarkCase(
        **{f.name: getattr(case, f.name) for f in fields(BenchmarkCase)},
        authored_renderings=tuple(AuthoredRendering(variant, text, "llm_assisted", VERSION,
            "Deterministic complete templates authored with Codex; independent human meaning review pending.")
            for variant, text in texts), gold_author_reference=VERSION)


def _signature(spec):
    """Type/count matching intentionally ignores only numeric scheduling restrictions."""
    return {
        "participants": [p.id for p in spec.participants],
        "resources": [r.id for r in spec.resources],
        "activities": [(a.id, a.duration_slots, a.participant_ids, a.resource_ids,
                        len(a.availability)) for a in spec.activities],
        "participant_windows": [len(p.availability) for p in spec.participants],
        "resource_windows": [len(r.availability) for r in spec.resources],
        "constraints": [to_data(c) for c in spec.constraints],
    }


def check_design(cases):
    cases = tuple(cases)
    if len(cases) != 48 or len({c.case_id for c in cases}) != 48:
        raise ValueError("Balanced generation requires 48 unique cases")
    expected = Counter((m, l, p, label) for m in MECHANISMS for l in LAYOUTS
                       for p in PROFILES for label in ("SAT", "UNSAT"))
    actual = Counter((c.sweep, c.level, profile(c.problem), c.expected_label) for c in cases)
    if actual != expected:
        raise ValueError("Mechanism/layout/profile/label balance changed")
    groups = {m: {c.group_id for c in cases if c.sweep == m} for m in MECHANISMS}
    if any(len(g) != 1 for g in groups.values()) or len({c.group_id for c in cases}) != 3:
        raise ValueError("All related variants must remain in three conservative construction families")
    for case in cases:
        spec = case.problem
        if (not isinstance(case, AuthoredBenchmarkCase) or case.split != "development"
                or case.kind != "controlled" or spec.task_type != "generation"
                or case.context is not None or len(spec.activities) != 8
                or len(spec.participants) != 2 or len(spec.resources) != 1
                or any(a.duration_slots not in (2, 3, 4) for a in spec.activities)
                or (spec.horizon_start, spec.horizon_slots, spec.slot_minutes, spec.timezone)
                != ("2026-10-26T09:00:00+08:00", 16, 30, "+08:00")):
            raise ValueError("Balanced generation scope changed")
        if any(not _unary_starts(spec, a) for a in spec.activities):
            raise ValueError("Every activity must retain a nonempty unary start domain")
        required_kinds = Counter({"preferred_start": 8})
        if case.sweep == "precedence_interaction":
            required_kinds["precedence"] = 3
        if profile(spec) in ("deadline", "both"):
            required_kinds["deadline"] = 1
        if profile(spec) in ("fixed_start", "both"):
            required_kinds["fixed_start"] = 1
        if Counter(c.kind for c in spec.constraints) != required_kinds:
            raise ValueError("Balanced generation constraint counts changed")
        if {r.variant_id for r in case.authored_renderings} != {"canonical", "reordered"}:
            raise ValueError("Balanced generation requires canonical and reordered renderings")
        for rendering in case.authored_renderings:
            # Regenerate from the formal facts, so omission/tampering cannot silently pass.
            base = BenchmarkCase(**{f.name: getattr(case, f.name) for f in fields(BenchmarkCase)})
            if rendering.text != render(base, rendering.variant_id, 3263).text:
                raise ValueError("Authored public text differs from its complete dated template")
            if rendering.creation_method != "llm_assisted" or rendering.author_reference != VERSION:
                raise ValueError("Public text provenance changed")
        for token in (case.case_id, case.group_id, "SAT", "UNSAT", VERSION):
            if any(token in r.text for r in case.authored_renderings):
                raise ValueError("Evaluator metadata reached public text")
    for m in MECHANISMS:
        for layout in LAYOUTS:
            for p in PROFILES:
                pair = [c for c in cases if (c.sweep, c.level, profile(c.problem)) == (m, layout, p)]
                if _signature(pair[0].problem) != _signature(pair[1].problem):
                    raise ValueError("Matched labels differ in assignments, constraint types/counts or rule values")
    return {
        "unique_cases": 48, "SAT": 24, "UNSAT": 24,
        "construction_families": 3, "matched_label_pairs": 24,
        "canonical_scheduling_attempts_per_model": 96,
        "profile_label_counts": {p: dict(Counter(c.expected_label for c in cases if profile(c.problem) == p)) for p in PROFILES},
        "mechanism_label_counts": {m: dict(Counter(c.expected_label for c in cases if c.sweep == m)) for m in MECHANISMS},
        "layout_label_counts": {l: dict(Counter(c.expected_label for c in cases if c.level == l)) for l in LAYOUTS},
        "all_unary_domains_nonempty": True, "paired_constraint_types_and_counts_equal": True,
        "calendar_date_in_every_rendering": True,
    }


def _check_operative(spec, evidence):
    expected = {c.kind: c for c in spec.constraints if isinstance(c, (Deadline, FixedStart))}
    if not isinstance(evidence, dict) or set(evidence) != set(expected):
        return False
    for kind, row in evidence.items():
        if (not isinstance(row, dict) or set(row) != {"constraint_id", "counterexample_schedule"}
                or row["constraint_id"] != expected[kind].id):
            return False
        # Validation accepts raw rows and rejects malformed schedules without parsing exceptions.
        schedule = row["counterexample_schedule"]
        full = validate_schedule(spec, schedule)
        reduced = replace(spec, constraints=tuple(c for c in spec.constraints if c.id != row["constraint_id"]))
        if (not validate_schedule(reduced, schedule).hard_feasible or full.hard_feasible
                or {v.constraint_id for v in full.violations} != {row["constraint_id"]}):
            return False
    return True


def verify_suite(cases, proofs):
    """Verify loaded case/proof alignment without model calls or trusting saved booleans."""
    cases = tuple(cases)
    coverage = check_design(cases)
    if not isinstance(proofs, dict) or set(proofs) != {c.case_id for c in cases}:
        raise ValueError("Proof membership differs from cases")
    keys = {"problem_sha256", "certificate", "construction_witness", "operative_constraints",
            "independent_certificate_checked", "reference_status", "reference_optimality_proven",
            "expected_objective"}
    for case in cases:
        proof = proofs[case.case_id]
        if not isinstance(proof, dict) or set(proof) != keys or proof["problem_sha256"] != digest(case.problem):
            raise ValueError("Proof fields or problem binding differ")
        cert = proof["certificate"]
        if not isinstance(cert, dict) or (cert.get("kind") == "sat_witness") != (case.expected_label == "SAT"):
            raise ValueError("Certificate kind disagrees with the expected label")
        if (proof["independent_certificate_checked"] is not True
                or not verify_certificate(case.problem, cert, proof["construction_witness"])):
            raise ValueError("Independent feasibility certificate failed")
        if case.expected_label == "SAT":
            checked = validate_schedule(case.problem, case.witness)
            if (not checked.hard_feasible or proof["reference_status"] != "OPTIMAL"
                    or proof["reference_optimality_proven"] is not True
                    or not isinstance(proof["expected_objective"], list)
                    or any(type(v) is not int for v in proof["expected_objective"])
                    or tuple(proof["expected_objective"]) != case.expected_objective
                    or checked.objectives.as_tuple() != case.expected_objective
                    or not _check_operative(case.problem, proof["operative_constraints"])):
                raise ValueError("SAT reference or operative-constraint evidence failed")
        elif (case.witness is not None or case.expected_objective is not None
              or proof["reference_status"] != "INFEASIBLE" or proof["expected_objective"] is not None
              or proof["construction_witness"] is not None or proof["operative_constraints"] != {}
              or proof["reference_optimality_proven"] is not False):
            raise ValueError("UNSAT proof carries inconsistent reference data")
    coverage["independently_checked_certificates"] = len(cases)
    coverage["operative_deadline_examples"] = 12
    coverage["operative_fixed_start_examples"] = 12
    return coverage


def validate_manifest(cases, proofs, manifest):
    """Bind dataset declarations to current source and independently checked contents."""
    from scheduling.evaluation.manifests import structural_audit

    cases = tuple(cases)
    coverage = verify_suite(cases, proofs)
    expected = {
        "format_version": "1.0", "dataset_version": VERSION, "campaign_policy": CAMPAIGN_POLICY,
        "case_bundle_sha256": digest(case_bundle(cases)), "proofs_sha256": digest(proofs),
        "coverage": coverage, "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "counts": COUNTS, "models": list(MODELS), "expected_response_models": EXPECTED_RESPONSE_MODELS,
        "budget_per_model": BUDGET_PER_MODEL, "structural_audit": structural_audit(cases),
        "new_model_calls": 0,
    }
    if not isinstance(manifest, dict) or any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Balanced generation manifest does not match current verified dataset/source contract")
    return coverage


def build_suite(seed=DEFAULT_SEED, reference_seconds=60):
    from scheduling.solver import SolverLimits, solve

    cases, proofs = [], {}
    for mechanism in MECHANISMS:
        for layout in LAYOUTS:
            for constraint_profile in PROFILES:
                for label in ("SAT", "UNSAT"):
                    case, certificate, operative = _construct(seed, mechanism, layout, constraint_profile, label)
                    construction_witness = to_data(case.witness)
                    if not verify_certificate(case.problem, certificate, case.witness):
                        raise ValueError("Construction failed independent arithmetic proof")
                    reference = solve(case.problem, SolverLimits(reference_seconds))
                    if label == "SAT":
                        if not reference.optimality_proven or reference.schedule is None:
                            raise ValueError("CP-SAT reference optimum was not proved within the preparation budget")
                        case = replace(case, witness=reference.schedule, expected_objective=reference.objectives.as_tuple())
                    elif reference.status != "INFEASIBLE":
                        raise ValueError("Independent certificate and CP-SAT feasibility disagree")
                    cases.append(_authored(case))
                    proofs[case.case_id] = {
                        "problem_sha256": digest(case.problem), "certificate": certificate,
                        "construction_witness": construction_witness, "operative_constraints": operative,
                        "independent_certificate_checked": True, "reference_status": reference.status,
                        "reference_optimality_proven": reference.optimality_proven,
                        "expected_objective": list(case.expected_objective) if case.expected_objective is not None else None,
                    }
    result = tuple(cases)
    verify_suite(result, proofs)
    return result, proofs
