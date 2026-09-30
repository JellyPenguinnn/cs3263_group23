"""Bounded source-family construction. Development pilots never become final data."""

from collections import Counter
from dataclasses import asdict, dataclass, replace
import hashlib
from pathlib import Path
import random
import time

from scheduling.schema import (
    Activity,
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    Precedence,
    PreferredStart,
    ProblemSpec,
    RepairContext,
    Window,
    to_data,
)
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule
from scheduling.evaluation.benchmark import difficulty, render
from scheduling.evaluation.cases import BenchmarkCase, case_bundle
from scheduling.evaluation.manifests import (
    FINGERPRINT_VERSION,
    check_development_registry,
    development_registry,
    structural_audit,
    structural_fingerprint,
)
from scheduling.evaluation.runner import write_new
from scheduling.evaluation.scoring import digest, check_reference

SWEEPS = ("activity_count", "slack", "interaction_density", "resource_contention")
EVENTS = ("blocked", "deadline", "fixed_start")


@dataclass(frozen=True)
class CandidatePolicy:
    version: str = "source-family-v1"
    families_per_cell: int = 2  # Development pilot; compact=4, working target=10.
    proposals_per_family: int = 20
    reference_seconds: float = 5
    wall_seconds: float = 180
    rendering_seed: int = 3263

    def __post_init__(self):
        if self.version != "source-family-v1":
            raise ValueError("Unsupported construction policy")
        if type(self.families_per_cell) is not int or self.families_per_cell not in (
            2,
            4,
            10,
        ):
            raise ValueError("Use 2 pilot, 4 compact or 10 target families per cell")
        if (
            type(self.proposals_per_family) is not int
            or not 1 <= self.proposals_per_family <= 100
        ):
            raise ValueError("Proposal count must be bounded by 1..100")
        SolverLimits(self.reference_seconds)
        SolverLimits(self.wall_seconds)
        if type(self.rendering_seed) is not int or self.rendering_seed < 0:
            raise ValueError("Rendering seed must be a nonnegative integer")


def generator_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _source(seed, cell, ordinal, attempt, policy):
    sweep, level = cell
    token = digest([policy.version, seed, sweep, level, ordinal, attempt])
    rng = random.Random(int(token, 16))
    group = "family-" + token[:24]
    count = (4, 8, 12)[level] if sweep == "activity_count" else 8
    slack = (1, 3, 6)[level] if sweep == "slack" else 4
    durations = [rng.randint(1, 3) for _ in range(count)]
    cursor = rng.randint(0, 3)
    starts = []
    for i, d in enumerate(durations):
        starts.append(cursor)
        gap_room = min(1, 48 - cursor - d - sum(durations[i + 1 :]))
        cursor += d + rng.randint(0, gap_room)
    width = Window(0, 48)
    resources = (Entity("R", (width,)), Entity("Rpair", (width,)))
    participants = tuple(Entity(f"P{i}", (width,)) for i in range(count))
    pair = rng.randrange(count - 1)
    share_count = (
        (0, count // 2, count)[level] if sweep == "resource_contention" else count // 2
    )
    sharing = set(rng.sample(range(count), share_count))
    activities = tuple(
        Activity(
            f"A{i}",
            d,
            (f"P{i}",),
            tuple(
                r
                for r, used in (("R", i in sharing), ("Rpair", i in (pair, pair + 1)))
                if used
            ),
            (
                Window(
                    max(0, starts[i] - rng.randint(1, slack)),
                    min(48, starts[i] + d + rng.randint(1, slack)),
                ),
            ),
        )
        for i, d in enumerate(durations)
    )
    # Adjacent forward edges are non-transitive; keep only edges that actually
    # rule out a unary-domain combination. No model response enters construction.
    edge_count = (
        (0, count // 3, count - 1)[level]
        if sweep == "interaction_density"
        else count // 3
    )
    eligible = [
        i
        for i in range(count - 1)
        if activities[i].availability[0].end > activities[i + 1].availability[0].start
    ]
    edges = rng.sample(eligible, min(edge_count, len(eligible)))
    constraints = [Precedence(f"p{i}", f"A{i}", f"A{i+1}") for i in edges]
    for i in range(count):
        constraints += [
            PreferredStart(
                f"prefer{i}", f"A{i}", starts[i], starts[i] + 1, rng.randint(2, 5)
            ),
            PreferredStart(
                f"compete{i}",
                f"A{i}",
                (starts[i] + 1) % 48,
                (starts[i] + 1) % 48 + 1,
                1,
            ),
        ]
    event = EVENTS[
        (
            SWEEPS.index(sweep) * 3 * policy.families_per_cell
            + level * policy.families_per_cell
            + ordinal
        )
        % 3
    ]
    label = "SAT" if ordinal % 2 == 0 else "UNSAT"
    if label == "UNSAT" and event == "fixed_start":
        constraints.append(FixedStart("anchor", f"A{pair+1}", starts[pair + 1]))
    if label == "UNSAT" and event == "deadline":
        constraints.append(FixedStart("anchor", f"A{pair}", starts[pair]))
        if pair not in edges:
            constraints.append(Precedence("event_precedence", f"A{pair}", f"A{pair+1}"))
    original = ProblemSpec(
        "1.0",
        group + "-original",
        "generation",
        48,
        30,
        "2026-10-05T00:00:00+08:00",
        "+08:00",
        participants,
        resources,
        activities,
        tuple(constraints),
    )
    return group, original, pair, event, label


def _update(original, old, pair, event, label):
    ids = [a.id for a in original.activities]
    target = ids[pair]
    starts = old.starts()
    if event == "fixed_start":
        rule = FixedStart("event", target, starts[ids[pair + 1]])
        mechanism = "shared_resource_collision"
    elif event == "deadline":
        target = ids[pair + 1]
        bound = (
            (
                starts[ids[pair]]
                + original.activities[pair].duration_slots
                + original.activities[pair + 1].duration_slots
                - 1
            )
            if label == "UNSAT"
            else (starts[target] + original.activities[pair + 1].duration_slots - 1)
        )
        rule = Deadline("event", target, bound)
        mechanism = "precedence_deadline" if label == "UNSAT" else "tightened_deadline"
    else:
        window = original.activities[pair].availability[0]
        lower, upper = (
            (window.start, window.end)
            if label == "UNSAT"
            else (starts[target], starts[target] + 1)
        )
        rule = BlockedInterval("event", "participant", f"P{pair}", lower, upper)
        mechanism = "unary_availability" if label == "UNSAT" else "participant_block"
    return replace(original, constraints=original.constraints + (rule,)), mechanism


def _reference(spec, result, context=None):
    return {
        "problem_sha256": digest(spec),
        "context_sha256": digest(context),
        "result": to_data(result),
    }


def prepare(directory, policy, seed, registry, *, mode="development", freeze=None):
    """Write a new packet and ledger. A final draw requires a prior policy decision.

    All inspected pilot specs, including rejected candidates, enter the cumulative
    registry. Final candidates remain pending human gold/wording review.
    """
    directory = Path(directory)
    known = set(check_development_registry(registry))
    if type(seed) is not int or seed < 0 or mode not in ("development", "final"):
        raise ValueError("Invalid draw seed/mode")
    if mode == "final":
        required = {
            "format_version",
            "policy_sha256",
            "generator_sha256",
            "registry_sha256",
            "draw_seed",
            "policy_review_reference",
            "model_decision_reference",
        }
        if (
            not isinstance(freeze, dict)
            or set(freeze) != required
            or freeze["format_version"] != "1.0"
        ):
            raise ValueError("Final draw requires an explicit frozen-policy decision")
        if (
            freeze["policy_sha256"] != digest(policy)
            or freeze["generator_sha256"] != generator_hash()
            or freeze["registry_sha256"] != digest(registry)
            or type(freeze["draw_seed"]) is not int
            or freeze["draw_seed"] != seed
            or any(
                not isinstance(freeze[k], str) or not freeze[k].strip()
                for k in ("policy_review_reference", "model_decision_reference")
            )
        ):
            raise ValueError("Frozen policy/source/registry/seed or decision mismatch")
        if policy.families_per_cell == 2:
            raise ValueError("Pilot size is not a final-study design")
    elif freeze is not None:
        raise ValueError("Development draw cannot claim policy freeze")
    directory.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    selected, inspected, ledger, records, references, seen = [], [], [], {}, {}, set()
    requested = len(SWEEPS) * 3 * policy.families_per_cell

    def bounded_solve(spec, context=None):
        remaining = max(0, policy.wall_seconds - (time.monotonic() - start))
        return solve(
            spec, SolverLimits(min(policy.reference_seconds, remaining)), context
        )

    def inspect(spec, group, sweep, level):
        # Every proposed hard structure is retained, even when no repair case can
        # be formed because the original reference is unresolved.
        spec = replace(spec, task_type="generation")
        c = BenchmarkCase(
            spec.instance_id,
            group,
            "development" if mode == "development" else "test",
            "controlled",
            sweep,
            str(level),
            spec,
        )
        inspected.append(c)
        write_new(directory / ("proposal-" + spec.instance_id + ".json"), to_data(c))

    for sweep in SWEEPS:
        for level in range(3):
            for ordinal in range(policy.families_per_cell):
                for attempt in range(policy.proposals_per_family):
                    if time.monotonic() - start >= policy.wall_seconds:
                        break
                    group, original, pair, event, label = _source(
                        seed, (sweep, level), ordinal, attempt, policy
                    )
                    inspect(original, group, sweep, level)
                    entry = {
                        "family": group,
                        "sweep": sweep,
                        "level": level,
                        "ordinal": ordinal,
                        "attempt": attempt,
                        "event": event,
                        "requested_label": label,
                    }
                    ledger.append(entry)
                    old = bounded_solve(original)
                    entry["original_reference"] = _reference(original, old)
                    if old.status != "OPTIMAL" or not old.optimality_proven:
                        entry["reason"] = "original_reference_unresolved"
                        continue
                    if not validate_schedule(original, old.schedule).hard_feasible:
                        raise ValueError(
                            "Original witness fails independent validation"
                        )
                    updated, mechanism = _update(
                        original, old.schedule, pair, event, label
                    )
                    updated = replace(updated, instance_id=group + "-updated")
                    inspect(updated, group, sweep, level)
                    keys = {structural_fingerprint(s) for s in (original, updated)}
                    entry.update(mechanism=mechanism, hard_fingerprints=sorted(keys))
                    if (
                        label == "UNSAT"
                        and event != "blocked"
                        and 0 in difficulty(updated)["unary_start_counts"]
                    ):
                        entry["reason"] = "binary_mechanism_has_unary_wipeout"
                        continue
                    overlap = keys & known
                    if overlap or keys & seen:
                        entry["reason"] = (
                            "development_overlap"
                            if overlap
                            else "related_family_already_selected"
                        )
                        continue
                    pair_cases, pair_refs = [], {}
                    for task in ("generation", "repair"):
                        spec = replace(
                            updated, instance_id=group + "-" + task, task_type=task
                        )
                        context = (
                            RepairContext(old.schedule) if task == "repair" else None
                        )
                        result = bounded_solve(spec, context)
                        pair_refs[spec.instance_id] = _reference(spec, result, context)
                        # Resolve before assigning a label, witness or optimum.
                        if result.status not in ("OPTIMAL", "INFEASIBLE") or (
                            result.status == "OPTIMAL" and not result.optimality_proven
                        ):
                            entry["reason"] = "updated_reference_unresolved"
                            break
                        actual = "SAT" if result.status == "OPTIMAL" else "UNSAT"
                        if actual != label:
                            entry["reason"] = "label_quota_mismatch"
                            break
                        c = BenchmarkCase(
                            spec.instance_id,
                            group,
                            "development" if mode == "development" else "test",
                            "controlled",
                            sweep,
                            str(level),
                            spec,
                            original if context else None,
                            old.schedule if context else None,
                            event if context else None,
                            result.schedule,
                            actual,
                            result.objectives.as_tuple() if result.objectives else None,
                            "Reference checked; independent human gold/text review pending",
                        )
                        ref = _reference(spec, result, context)
                        check_reference(c, ref)
                        pair_cases.append(c)
                        pair_refs[c.case_id] = ref
                    entry["updated_references"] = pair_refs
                    if len(pair_cases) != 2:
                        continue
                    selected.extend(pair_cases)
                    references.update(pair_refs)
                    seen.update(keys)
                    entry["reason"] = "selected"
                    for c in pair_cases:
                        records[c.case_id] = {
                            "case_id": c.case_id,
                            "group_id": group,
                            "source_family_id": group,
                            "split": c.split,
                            "sha256": digest(c),
                            "creation_method": "procedural",
                            "fixture_review": "pending",
                            "language_review": "pending",
                            "mechanism": mechanism,
                            "event": event,
                            "realized_difficulty": difficulty(c.problem),
                            "renderings": {
                                v: digest(render(c, v, policy.rendering_seed))
                                for v in ("canonical", "paraphrase", "reordered")
                            },
                        }
                    break
    audit = structural_audit(selected)
    if len(set(audit["family_for_group"].values())) != len(selected) // 2:
        raise ValueError(
            "Selected groups are structurally related; refuse inflated family count"
        )
    coupled = sum(
        c.context is not None
        and c.expected_objective is not None
        and c.expected_objective[0] > 1
        for c in selected
    )
    complete = len(selected) == 2 * requested and coupled > 0
    manifest = {
        "format_version": "2.0",
        "fingerprint_version": FINGERPRINT_VERSION,
        "dataset_version": policy.version,
        "status": (
            "pending_human_review" if mode == "final" else "development_policy_pilot"
        ),
        "human_fixture_review": "pending",
        "human_language_review": "pending",
        "policy": asdict(policy),
        "policy_sha256": digest(policy),
        "generator_sha256": generator_hash(),
        "seed": seed,
        "mode": mode,
        "policy_freeze": freeze,
        "input_registry_sha256": digest(registry),
        "case_count": len(selected),
        "family_count": len(selected) // 2,
        "requested_families": requested,
        "quota_complete": complete,
        "counts": dict(
            Counter(
                f"{c.sweep}/{c.level}/{c.problem.task_type}/{c.expected_label}"
                for c in selected
            )
        ),
        "repair_events": dict(Counter(c.event for c in selected if c.context)),
        "mechanisms": dict(Counter(r["mechanism"] for r in records.values())),
        "coupled_sat_repairs": coupled,
        "positive_preference_cases": sum(
            c.expected_objective is not None and c.expected_objective[-1] > 0
            for c in selected
        ),
        "structural_audit": audit,
        "cases": list(records.values()),
        "limitations": [
            "Known construction mechanisms, not unseen generators or guaranteed absence from pretraining.",
            "Sweeps have coupled covariates; realized values do not establish causal difficulty.",
            "Blocked UNSAT uses unary wipeout, fixed UNSAT a shared-resource collision, deadline UNSAT a precedence bound.",
            "No independently human-written scenarios or completed human review.",
        ],
    }
    for name, value in (
        ("cases.json", case_bundle(selected)),
        ("inspected.json", case_bundle(inspected)),
        ("manifest.json", manifest),
        ("ledger.json", ledger),
        ("references.json", references),
    ):
        write_new(directory / name, value)
    if mode == "development":
        addition = (
            development_registry({"pilot/" + digest(case_bundle(inspected)): inspected})
            if inspected
            else development_registry({})
        )
        sources = {s["reference"]: s for s in registry["sources"]}
        for source in addition["sources"]:
            if (
                source["reference"] in sources
                and sources[source["reference"]] != source
            ):
                raise ValueError("Registry source reference collision")
            sources[source["reference"]] = source
        cumulative = {
            **registry,
            "fingerprints": sorted(known | set(addition["fingerprints"])),
            "sources": [sources[k] for k in sorted(sources)],
        }
        check_development_registry(cumulative)
        write_new(directory / "development-registry.json", cumulative)
    return manifest
