"""Compiler-local unary domains and sufficient contradictions, not gold validation.

At most one reason per rejected start is retained (at most H <= 48 per activity).
Reasons are grouped without changing their meaning. No resource/precedence pruning
is performed, and nonempty domains do not establish feasibility.
"""

from collections import defaultdict
from dataclasses import dataclass
from math import prod

from scheduling.schema import (
    BlockedInterval,
    Deadline,
    FixedStart,
    Precedence,
    ProblemSpec,
    ReleaseTime,
)


@dataclass(frozen=True)
class StartExclusion:
    code: str
    path: str
    constraint_id: str | None
    rejected_starts: tuple[int, ...]


@dataclass(frozen=True)
class ActivityDomain:
    activity_id: str
    duration_slots: int
    legal_starts: tuple[int, ...]
    exclusions: tuple[StartExclusion, ...]


@dataclass(frozen=True)
class Contradiction:
    code: str
    activity_ids: tuple[str, ...]
    rule_paths: tuple[str, ...]
    constraint_ids: tuple[str, ...]


@dataclass(frozen=True)
class DomainAnalysis:
    domains: tuple[ActivityDomain, ...]
    contradictions: tuple[Contradiction, ...]
    search_space_upper_bound: int
    format_version: str = "1.0"
    scope: str = "supplied_specification_only"
    reasoning: str = (
        "unary_exclusions_and_sufficient_contradictions_not_minimum_conflicts"
    )


def _activity_domain(spec, activity, index, people, resources, unary):
    windows = [(f"$.activities[{index}].availability", activity.availability)]
    windows += [
        (f"$.participants[{people[p][0]}].availability", people[p][1].availability)
        for p in activity.participant_ids
    ]
    windows += [
        (f"$.resources[{resources[r][0]}].availability", resources[r][1].availability)
        for r in activity.resource_ids
    ]
    rejected, legal = defaultdict(list), []
    for start in range(spec.horizon_slots):
        end = start + activity.duration_slots
        reason = None
        if end > spec.horizon_slots:
            reason = ("horizon_fit", "$.horizon_slots", None)
        if reason is None:
            for path, allowed in windows:
                if not any(w.start <= start and end <= w.end for w in allowed):
                    reason = ("availability", path, None)
                    break
        if reason is None:
            for i, rule in unary:
                violated = (
                    type(rule) is ReleaseTime
                    and start < rule.slot
                    or type(rule) is Deadline
                    and end > rule.slot
                    or type(rule) is FixedStart
                    and start != rule.slot
                    or isinstance(rule, BlockedInterval)
                    and start < rule.end
                    and rule.start < end
                )
                if violated:
                    reason = (rule.kind, f"$.constraints[{i}]", rule.id)
                    break
        if reason is None:
            legal.append(start)
        else:
            rejected[reason].append(start)
    exclusions = tuple(
        StartExclusion(*key, tuple(starts))
        for key, starts in sorted(
            rejected.items(), key=lambda item: (item[0][1], item[0][0])
        )
    )
    return ActivityDomain(
        activity.id, activity.duration_slots, tuple(legal), exclusions
    )


def _precedence_cycle(spec):
    """Find one actual directed cycle, iteratively; positive durations prove UNSAT."""
    edges = defaultdict(list)
    for i, rule in enumerate(spec.constraints):
        if isinstance(rule, Precedence):
            edges[rule.before].append((rule.after, i, rule.id))
    colors, parent = {}, {}
    for root in sorted(a.id for a in spec.activities):
        if colors.get(root):
            continue
        colors[root] = 1
        stack = [(root, iter(sorted(edges[root])))]
        while stack:
            node, outgoing = stack[-1]
            edge = next(outgoing, None)
            if edge is None:
                colors[node] = 2
                stack.pop()
                continue
            target, index, rule_id = edge
            if colors.get(target) == 1:
                cycle = [(node, target, index, rule_id)]
                cursor = node
                while cursor != target:
                    before, i, rid = parent[cursor]
                    cycle.append((before, cursor, i, rid))
                    cursor = before
                cycle.reverse()
                return Contradiction(
                    "positive_duration_precedence_cycle",
                    tuple([row[0] for row in cycle] + [cycle[-1][1]]),
                    tuple(f"$.constraints[{row[2]}]" for row in cycle),
                    tuple(row[3] for row in cycle),
                )
            if not colors.get(target):
                parent[target] = node, index, rule_id
                colors[target] = 1
                stack.append((target, iter(sorted(edges[target]))))
    return None


def analyze_domains(spec: ProblemSpec) -> DomainAnalysis:
    """Return inspectable domains. This routine never invokes a solver."""
    people = {p.id: (i, p) for i, p in enumerate(spec.participants)}
    resources = {r.id: (i, r) for i, r in enumerate(spec.resources)}
    unary = defaultdict(list)
    for i, rule in enumerate(spec.constraints):
        if isinstance(rule, ReleaseTime):
            unary[rule.activity_id].append((i, rule))
        elif isinstance(rule, BlockedInterval):
            attribute = (
                "participant_ids"
                if rule.target_kind == "participant"
                else "resource_ids"
            )
            for activity in spec.activities:
                if rule.target_id in getattr(activity, attribute):
                    unary[activity.id].append((i, rule))
    domains = tuple(
        _activity_domain(spec, a, i, people, resources, unary[a.id])
        for i, a in enumerate(spec.activities)
    )
    contradictions = [
        Contradiction(
            "empty_unary_domain",
            (row.activity_id,),
            tuple(reason.path for reason in row.exclusions),
            tuple(
                reason.constraint_id
                for reason in row.exclusions
                if reason.constraint_id is not None
            ),
        )
        for row in domains
        if not row.legal_starts
    ]
    cycle = _precedence_cycle(spec)
    if cycle is not None:
        contradictions.append(cycle)
    return DomainAnalysis(
        domains, tuple(contradictions), prod(len(row.legal_starts) for row in domains)
    )
