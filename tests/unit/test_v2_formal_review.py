"""Independent certificates for v2 references; not human review or model evidence."""

from dataclasses import replace

import pytest

from scheduling.evaluation.benchmark import generate_development_v2
from scheduling.schema import BlockedInterval, Precedence
from tests.formal_support import assignment_objective, enumerate_answers


@pytest.fixture(scope="module")
def cases():
    generated, _, selection = generate_development_v2(3264)
    assert selection["quota_complete"] and len(generated) == 144
    return {c.case_id: c for c in generated}


def project(spec, ids):
    """Drop other activities and their rules: a relaxation, never a restriction."""

    def keep(rule):
        if isinstance(rule, Precedence):
            return rule.before in ids and rule.after in ids
        if isinstance(rule, BlockedInterval):
            return True  # An unused entity's block has no effect.
        return rule.activity_id in ids

    return replace(
        spec,
        task_type="generation",
        activities=tuple(a for a in spec.activities if a.id in ids),
        constraints=tuple(c for c in spec.constraints if keep(c)),
    )


@pytest.mark.parametrize("task", ["generation", "repair"])
def test_all_72_unsat_references_have_independent_pair_contradictions(cases, task):
    selected = [
        c
        for c in cases.values()
        if c.problem.task_type == task and c.expected_label == "UNSAT"
    ]
    assert len(selected) == 36
    for case in selected:
        pair = project(case.problem, {"A0", "A1"})
        assert all(
            enumerate_answers(project(pair, {a.id})) for a in pair.activities
        ), case.case_id
        # Every one of 48**2 assignments is checked by independent arithmetic.
        assert not enumerate_answers(pair), case.case_id
        # Removing resource contention from this relaxation restores feasibility:
        # contradiction is interacting, not just a hidden empty unary domain.
        unshared = replace(
            pair, activities=tuple(replace(a, resource_ids=()) for a in pair.activities)
        )
        assert enumerate_answers(unshared), case.case_id


def test_all_36_sat_generation_optima_attain_nonnegative_lower_bound(cases):
    selected = [
        c
        for c in cases.values()
        if c.problem.task_type == "generation" and c.expected_label == "SAT"
    ]
    assert len(selected) == 36
    for case in selected:
        actual = assignment_objective(case.problem, case.witness.starts())
        assert actual == case.expected_objective == (0,), case.case_id


def test_all_36_sat_repairs_have_independent_lexicographic_certificates(cases):
    selected = [c for c in cases.values() if c.context and c.expected_label == "SAT"]
    assert len(selected) == 36
    for case in selected:
        old = case.original_schedule.starts()
        assert assignment_objective(case.original_problem, old) == (0,), case.case_id
        assert assignment_objective(case.problem, old, old) is None, case.case_id
        # Old is infeasible, hence M >= 1; integer starts imply T >= M >= 1.
        # Enumerate ALL assignments with M=T=1, not only the intended event task.
        closest = []
        for key in sorted(old):
            for delta in (-1, 1):
                starts = {**old, key: old[key] + delta}
                value = assignment_objective(case.problem, starts, old)
                if value is not None:
                    closest.append((value, starts))
        assert closest, case.case_id
        best = min(value for value, _ in closest)
        assert best[:2] == (1, 1) and best == case.expected_objective, case.case_id
        assert assignment_objective(case.problem, case.witness.starts(), old) == best
        assert (best, case.witness.starts()) in closest


def test_every_selected_family_precedence_edge_has_a_counterexample(cases):
    families = [c for c in cases.values() if c.context]
    assert len(families) == 72
    checked = 0
    for case in families:
        spec, old = case.original_problem, case.original_schedule.starts()
        acts = {a.id: a for a in spec.activities}
        for rule in spec.constraints:
            if not isinstance(rule, Precedence):
                continue
            left, right = rule.before, rule.after
            gap = old[right] - old[left] - acts[left].duration_slots
            changed = {
                **old,
                right: old[left],
                left: old[left] + acts[right].duration_slots + gap,
            }
            relaxed = replace(
                spec, constraints=tuple(c for c in spec.constraints if c.id != rule.id)
            )
            assert assignment_objective(spec, changed) is None, (case.case_id, rule.id)
            assert assignment_objective(relaxed, changed) is not None, (
                case.case_id,
                rule.id,
            )
            checked += 1
    assert checked > 0


def test_v2_domains_and_every_recorded_exclusion_have_independent_support(cases):
    from scheduling.domain_analysis import analyze_domains
    from scheduling.schema import Deadline, FixedStart, ReleaseTime

    for case in cases.values():
        spec = case.problem
        data = spec.to_dict()
        acts = {a.id: a for a in spec.activities}
        analysis = analyze_domains(spec)
        for domain in analysis.domains:
            activity = acts[domain.activity_id]
            isolated = project(spec, {activity.id})
            independent = {
                starts[activity.id] for _, starts in enumerate_answers(isolated)
            }
            assert set(domain.legal_starts) == independent, (case.case_id, activity.id)
            rejected = set()
            for reason in domain.exclusions:
                for start in reason.rejected_starts:
                    assert start not in rejected and start not in independent
                    rejected.add(start)
                    end = start + activity.duration_slots
                    if reason.code == "horizon_fit":
                        assert (
                            reason.path == "$.horizon_slots"
                            and end > spec.horizon_slots
                        )
                    elif reason.code == "availability":
                        namespace, tail = reason.path[2:].split("[", 1)
                        index = int(tail.split("]", 1)[0])
                        row = data[namespace][index]
                        if namespace == "activities":
                            assert row["id"] == activity.id
                        else:
                            used = (
                                activity.participant_ids
                                if namespace == "participants"
                                else activity.resource_ids
                            )
                            assert row["id"] in used
                        assert not any(
                            w["start"] <= start and end <= w["end"]
                            for w in row["availability"]
                        )
                    else:
                        index = int(
                            reason.path.removeprefix("$.constraints[").removesuffix("]")
                        )
                        rule = spec.constraints[index]
                        assert (
                            reason.constraint_id == rule.id and reason.code == rule.kind
                        )
                        if type(rule) is ReleaseTime:
                            assert rule.activity_id == activity.id and start < rule.slot
                        elif type(rule) is Deadline:
                            assert rule.activity_id == activity.id and end > rule.slot
                        elif type(rule) is FixedStart:
                            assert (
                                rule.activity_id == activity.id and start != rule.slot
                            )
                        else:
                            assert isinstance(rule, BlockedInterval)
                            used = (
                                activity.participant_ids
                                if rule.target_kind == "participant"
                                else activity.resource_ids
                            )
                            assert (
                                rule.target_id in used
                                and start < rule.end
                                and rule.start < end
                            )
            assert rejected | independent == set(range(spec.horizon_slots))
