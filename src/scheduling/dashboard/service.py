"""Read-only dashboard views over independently revalidated run records."""

from pathlib import Path
import threading

from scheduling.evaluation.cases import load_cases
from scheduling.schema import to_data
from scheduling.evaluation.metrics import summarize
from scheduling.evaluation.liveness import probe_run_liveness
from scheduling.evaluation.runner import read, replay
from scheduling.evaluation.scoring import check_reference, digest


class BusyError(ValueError):
    pass


def fingerprint(path):
    files = [path / "manifest.json", path / "cases.json"]
    files += sorted((path / "attempts").glob("*.json"))
    files += sorted((path / "references").glob("*.json"))
    for file in files:
        if not file.resolve().is_relative_to(path.resolve()):
            raise ValueError("Run files must stay inside the run directory")
    return tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files)


def snapshot(path):
    """Take a consistent, revalidated view without trusting stored evaluation rows."""
    before = (fingerprint(path), probe_run_liveness(path))
    rows, progress = replay(path)
    manifest = read(path / "manifest.json")
    cases = load_cases(path / "cases.json")
    attempts = {}
    activity = []
    evaluated = {
        (r["case_id"], r["variant_id"], r["repeat"], r["approach"]): r for r in rows
    }
    for file in sorted((path / "attempts").glob("*.json")):
        record = read(file)
        identity = (
            record["payload"]["identity"]
            if record["state"] == "completed"
            else record["identity"]
        )
        key = (
            identity["case_id"],
            identity["variant_id"],
            identity["repeat"],
            identity["approach"],
        )
        row = evaluated[key]
        activity.append(
            {
                "case_id": identity["case_id"],
                "approach": identity["approach"],
                "started_utc": record.get("started_utc"),
                "state": (
                    "completed"
                    if record["state"] == "completed"
                    else "pending_or_interrupted"
                ),
                "category": row["category"],
                "accepted": row["accepted"],
                "pipeline_status": row["pipeline_status"],
            }
        )
        if record["state"] == "completed":
            payload = record["payload"]
            if digest(payload) != record["sha256"]:
                raise ValueError("Attempt checksum mismatch")
            identity = payload["identity"]
            key = (
                identity["case_id"],
                identity["variant_id"],
                identity["repeat"],
                identity["approach"],
            )
            attempts[key] = payload
    references = {}
    for case in cases:
        file = path / "references" / (digest(case.case_id) + ".json")
        if file.exists():
            record = read(file)
            if digest(record["reference"]) != record["sha256"]:
                raise ValueError("Reference checksum mismatch")
            check_reference(case, record["reference"])
            references[case.case_id] = record["reference"]["result"]
    liveness = before[1]
    active = liveness == "active"
    if before != (fingerprint(path), probe_run_liveness(path)):
        raise BusyError("Run changed during refresh; retrying shortly")
    # A reserved request is still running, not a failed model answer.
    scored = [
        r for r in rows if not active or r["category"] != "interrupted_or_uncertain"
    ]
    return {
        "rows": rows,
        "summary": summarize(scored),
        "progress": progress,
        "manifest": manifest,
        "cases": [to_data(case) for case in cases],
        "attempts": attempts,
        "references": references,
        "active": active,
        "liveness": liveness,
        "signature": before,
        "activity": sorted(
            activity, key=lambda r: r["started_utc"] or "", reverse=True
        )[:8],
    }


class Dashboard:
    def __init__(self, runs_dir, *, run_dir=None):
        self.root = Path(runs_dir).resolve()
        self.selected = Path(run_dir).resolve() if run_dir else None
        self.lock = threading.RLock()
        self.cache = {}

    def catalog(self):
        paths = []
        for file in self.root.glob("*/manifest.json"):
            if (
                not file.parent.resolve().is_relative_to(self.root)
                or not (file.parent / "cases.json").exists()
            ):
                continue
            try:
                manifest = read(file)
                if (
                    isinstance(manifest, dict)
                    and "contract" in manifest
                    and "case_bundle_sha256" in manifest["contract"]
                ):
                    paths.append(file.parent)
            except (OSError, ValueError, TypeError):
                continue
        if self.selected is not None and self.selected not in paths:
            paths.append(self.selected)
        # IDs are opaque, never interpreted as filesystem paths from the browser.
        return {
            digest(str(p.resolve()))[:20]: p for p in sorted(set(paths), reverse=True)
        }

    def bootstrap(self):
        runs = self.catalog()
        return {
            "runs": [{"id": key, "name": path.name} for key, path in runs.items()],
            "selected": next((k for k, p in runs.items() if p == self.selected), None),
        }

    def get_run(self, key):
        path = self.catalog().get(key)
        if path is None:
            raise LookupError("Run not found")
        with self.lock:
            signature = (fingerprint(path), probe_run_liveness(path))
            cached = self.cache.get(key)
            if cached is None or cached[0] != signature:
                data = snapshot(path)
                self.cache[key] = (data["signature"], data)
                while len(self.cache) > 4:
                    self.cache.pop(next(iter(self.cache)))
            return self.cache[key][1]

    def overview(self, key):
        data = self.get_run(key)
        return {
            k: data[k]
            for k in ("summary", "progress", "manifest", "active", "liveness", "activity")
        } | {
            "case_count": len(data["cases"]),
            "revision": digest((data["signature"], data["active"])),
            "slices": sorted(
                {(r["kind"], r["variant_id"], r["repeat"]) for r in data["rows"]}
            ),
        }

    def case_page(
        self,
        key,
        *,
        query="",
        task="",
        outcome="",
        offset=0,
        kind="controlled",
        variant="canonical",
        repeat=0,
    ):
        data = self.get_run(key)
        items = []
        indexed = {}
        for row in data["rows"]:
            if row["variant_id"] == variant and row["repeat"] == repeat:
                indexed.setdefault(row["case_id"], {})[row["approach"]] = row
        for i, case in enumerate(data["cases"]):
            if (
                case["kind"] != kind
                or query.lower() not in case["case_id"].lower()
                or (task and case["problem"]["task_type"] != task)
            ):
                continue
            pair = indexed.get(case["case_id"], {})
            rejected = any(
                r["accepted"] is False and r["category"] != "interrupted_or_uncertain"
                for r in pair.values()
            )
            if outcome == "rejected" and not rejected:
                continue
            if outcome == "accepted" and not (
                len(pair) == 2 and all(r["accepted"] is True for r in pair.values())
            ):
                continue
            items.append(
                {
                    "id": i,
                    "case_id": case["case_id"],
                    "task_type": case["problem"]["task_type"],
                    "activity_count": len(case["problem"]["activities"]),
                    "sweep": case["sweep"],
                    "rows": pair,
                }
            )
        return {
            "total": len(items),
            "offset": offset,
            "items": items[offset : offset + 20],
        }

    def case_detail(self, key, index, variant="canonical", repeat=0):
        data = self.get_run(key)
        if not 0 <= index < len(data["cases"]):
            raise LookupError("Case not found")
        case = data["cases"][index]
        responses = {}
        for approach in ("direct", "solver_augmented"):
            responses[approach] = data["attempts"].get(
                (case["case_id"], variant, repeat, approach)
            )
        return {
            "case": case,
            "reference": data["references"].get(case["case_id"]),
            "responses": responses,
            "rows": [
                r
                for r in data["rows"]
                if r["case_id"] == case["case_id"]
                and r["variant_id"] == variant
                and r["repeat"] == repeat
            ],
        }
