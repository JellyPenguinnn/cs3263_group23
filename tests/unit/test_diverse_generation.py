"""Independent proof, paired design, structural diversity and provenance checks."""
from collections import Counter
from dataclasses import replace

import pytest

from scheduling.evaluation.diverse_generation import (
    DEFAULT_SEED, MECHANISMS, STRATA, SIZES, CERTIFICATE_MAX_NODES,
    _construct, _paired_signature, build_suite, induced_feasibility,
    interaction_components, normalized_hard_fingerprint, optional_wording_selection,
    verify_certificate, verify_suite,
)
from scheduling.schema import Deadline, FixedStart, Precedence, PreferredStart, ReleaseTime, Window
from scheduling.validation import validate_schedule


@pytest.fixture(scope="module")
def suite():
    return build_suite(reference_seconds=10)


def test_full_design_is_balanced_unique_coupled_and_independently_proved(suite):
    cases, proofs = suite
    coverage = verify_suite(cases, proofs)
    assert coverage["unique_cases"] == coverage["unique_hard_structures"] == 1000
    assert coverage["independently_checked_certificates"] == 1000
    assert coverage["construction_families"] == 10
    assert coverage["matched_label_pairs"] == 500
    assert coverage["all_interaction_graphs_connected"]
    assert coverage["unique_topology_signatures"] >= 400
    assert set(Counter(c.group_id for c in cases).values()) == {100}
    for counts in coverage["profile_label_counts"].values():
        assert counts["SAT"] == counts["UNSAT"]
    for mechanism in MECHANISMS:
        for tier in STRATA:
            assert Counter(c.expected_label for c in cases if (c.sweep, c.level) == (mechanism, tier)) == {"SAT": 10, "UNSAT": 10}
    assert {p["reference_status"] for p in proofs.values()} == {"OPTIMAL", "INFEASIBLE"}


def test_every_unsat_core_fails_on_matched_sat_not_names_or_human_booleans(suite):
    cases, proofs = suite
    pairs = {}
    for case in cases:
        pairs.setdefault(proofs[case.case_id]["pair_id"], {})[case.expected_label] = case
    for pair in pairs.values():
        sat, unsat = pair["SAT"], pair["UNSAT"]
        cert = proofs[unsat.case_id]["certificate"]
        assert not verify_certificate(sat.problem, cert)
        assert verify_certificate(unsat.problem, cert)
        assert _paired_signature(sat.problem) == _paired_signature(unsat.problem)
        assert validate_schedule(sat.problem, proofs[sat.case_id]["construction_witness"]).hard_feasible
        assert not verify_certificate(unsat.problem, {**cert, "trusted_label": "UNSAT"})
        assert not verify_certificate(unsat.problem, {**cert, "activity_ids": cert["activity_ids"][:1]})


def test_unknown_exhaustion_is_not_unsat():
    case, _, _ = _construct(DEFAULT_SEED, "precedence_chain", "easy", 0, "SAT")
    ids = [c.before for c in case.problem.constraints if isinstance(c, Precedence)][:2]
    ids = list(dict.fromkeys(ids))
    if len(ids) < 2:
        ids = [a.id for a in case.problem.activities[:2]]
    assert induced_feasibility(case.problem, ids, max_nodes=1)["status"] == "UNKNOWN"
    with pytest.raises(ValueError):
        induced_feasibility(case.problem, ids, max_nodes=CERTIFICATE_MAX_NODES + 1)


def test_precedence_certificate_requires_actual_precedence_edges():
    case, cert, _ = _construct(DEFAULT_SEED, "precedence_chain", "easy", 0, "UNSAT")
    without = replace(case.problem, constraints=tuple(c for c in case.problem.constraints if not isinstance(c, Precedence)))
    assert verify_certificate(case.problem, cert)
    assert not verify_certificate(without, cert)


def test_wording_selection_has_12_matched_pairs_balanced_within_mechanism(suite):
    cases, proofs = suite
    lookup = {c.case_id: c for c in cases}
    selected = optional_wording_selection(cases)
    assert len(selected) == len({r["case_id"] for r in selected}) == 24
    assert {r["variant_id"] for r in selected} == {"reordered"}
    selected_cases = [lookup[row["case_id"]] for row in selected]
    assert Counter(c.expected_label for c in selected_cases) == {"SAT": 12, "UNSAT": 12}
    assert set(Counter(proofs[c.case_id]["pair_id"] for c in selected_cases).values()) == {2}
    assert {c.sweep for c in selected_cases} == set(MECHANISMS)
    for mechanism in MECHANISMS:
        counts = Counter(c.expected_label for c in selected_cases if c.sweep == mechanism)
        assert counts["SAT"] == counts["UNSAT"]


def test_core_ids_and_positions_are_not_fixed_prefix(suite):
    cases, proofs = suite
    positions = []
    for case in cases:
        if case.expected_label != "UNSAT":
            continue
        core = set(proofs[case.case_id]["certificate"]["activity_ids"])
        order = [a.id for a in case.problem.activities]
        positions.append(tuple(sorted(order.index(a) for a in core)))
        assert len(core) == len(order) if proofs[case.case_id]["certificate"]["kind"] == "capacity" else len(core) <= 4
    assert len(set(positions)) > 100
    assert any(0 not in row for row in positions)


def test_fingerprint_ignores_date_ids_order_preferences_and_uniform_slot_shift():
    case, _, _ = _construct(DEFAULT_SEED, "precedence_chain", "easy", 0, "SAT")
    spec = case.problem
    names = {a.id: f"X{i}" for i, a in enumerate(spec.activities)}
    def shifted(row):
        kwargs = {"availability": tuple(Window(w.start + 3, w.end + 3) for w in row.availability)}
        if row.id in names:
            kwargs["id"] = names[row.id]
        return replace(row, **kwargs)
    rules = []
    for c in spec.constraints:
        if isinstance(c, Precedence):
            rules.append(replace(c, before=names[c.before], after=names[c.after]))
        elif isinstance(c, (ReleaseTime, Deadline, FixedStart)):
            rules.append(replace(c, activity_id=names[c.activity_id], slot=c.slot + 3))
        elif isinstance(c, PreferredStart):
            rules.append(replace(c, activity_id=names[c.activity_id], start=0, end=1, weight=99))
    changed = replace(spec, horizon_slots=spec.horizon_slots + 3,
        horizon_start="2026-10-27T07:00:00+08:00", participants=tuple(shifted(p) for p in spec.participants),
        resources=tuple(shifted(r) for r in spec.resources), activities=tuple(reversed([shifted(a) for a in spec.activities])),
        constraints=tuple(reversed(rules)))
    assert normalized_hard_fingerprint(spec) == normalized_hard_fingerprint(changed)


def test_proof_verification_does_not_call_cpsat(suite, monkeypatch):
    import scheduling.solver
    def forbidden(*args, **kwargs):
        raise AssertionError("Independent verification must not call CP-SAT")
    monkeypatch.setattr(scheduling.solver, "solve", forbidden)
    for case in suite[0]:
        row = suite[1][case.case_id]
        assert verify_certificate(case.problem, row["certificate"], row["construction_witness"])


@pytest.mark.parametrize("certificate", [None, [], {}, {"kind": []},
    {"kind": "induced_exhaustion", "activity_ids": [["A1"]], "max_nodes": CERTIFICATE_MAX_NODES},
    {"kind": "induced_exhaustion", "activity_ids": ["missing"], "max_nodes": CERTIFICATE_MAX_NODES}])
def test_malformed_certificates_fail_closed(certificate):
    case, _, _ = _construct(DEFAULT_SEED, "room_contention", "easy", 0, "UNSAT")
    assert not verify_certificate(case.problem, certificate)


def test_second_seed_changes_geometry_not_only_identifiers():
    fingerprints = []
    for seed in (DEFAULT_SEED, DEFAULT_SEED + 1):
        case, _, _ = _construct(seed, "participant_crossing", "extreme", 2, "SAT")
        assert interaction_components(case.problem) == [SIZES["extreme"]]
        fingerprints.append(normalized_hard_fingerprint(case.problem))
    assert fingerprints[0] != fingerprints[1]


def test_capacity_contradictions_require_all_activities_with_1840_deletion_witnesses(suite):
    from scheduling.evaluation.balanced_generation import _unary_starts
    from scheduling.schema import Schedule
    cases, proofs = suite
    sat_by_pair = {proofs[c.case_id]["pair_id"]: c for c in cases if c.expected_label == "SAT"}
    checked = 0
    for unsat in cases:
        cert = proofs[unsat.case_id]["certificate"]
        if cert["kind"] != "capacity":
            continue
        activities = unsat.problem.activities
        assert set(cert["activity_ids"]) == {a.id for a in activities}
        occupied = {slot for a in activities for start in _unary_starts(unsat.problem, a)
                    for slot in range(start, start + a.duration_slots)}
        assert sum(a.duration_slots for a in activities) - len(occupied) == 1
        sat = sat_by_pair[proofs[unsat.case_id]["pair_id"]]
        starts = Schedule.from_list(proofs[sat.case_id]["construction_witness"]).starts()
        for removed in activities:
            # Independent counterfactual: delete one mandatory activity and all
            # incident rules, then compress the original sequential witness by
            # exactly the one slot lost from shared capacity after that activity.
            rules = tuple(c for c in unsat.problem.constraints
                          if getattr(c, "activity_id", None) != removed.id
                          and (not isinstance(c, Precedence) or removed.id not in (c.before, c.after)))
            reduced = replace(unsat.problem, activities=tuple(a for a in activities if a.id != removed.id), constraints=rules)
            witness = Schedule.from_list([{"activity_id": a.id,
                "start_slot": starts[a.id] - int(starts[a.id] > starts[removed.id])}
                for a in activities if a.id != removed.id])
            assert validate_schedule(reduced, witness).hard_feasible
            checked += 1
    assert checked == 1840


def test_prepare_refuses_existing_directory_before_any_work(tmp_path, monkeypatch):
    from evaluation import prepare_diverse_generation
    def forbidden(*args, **kwargs):
        raise AssertionError("Existing evidence must be rejected before generation")
    monkeypatch.setattr(prepare_diverse_generation.design, "build_suite", forbidden)
    with pytest.raises(FileExistsError):
        prepare_diverse_generation.prepare(tmp_path)
