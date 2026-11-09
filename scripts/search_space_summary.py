#!/usr/bin/env python3
"""Summarize unary start-domain products for the 1,000 diverse generation cases.

Offline; no model calls. Reports log10 of the product of per-activity legal start
counts (before non-overlap/precedence interactions), grouped by activity count.
"""
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scheduling.domain_analysis import analyze_domains  # noqa: E402
from scheduling.schema import ProblemSpec  # noqa: E402


def main():
    cases = json.loads((ROOT / "benchmarks/fixtures/diverse-generation-v1/cases.json").read_text())["cases"]
    by_size, overall = {}, []
    for case in cases:
        spec = ProblemSpec.from_dict(case["problem"])
        sizes = [len(row.legal_starts) for row in analyze_domains(spec).domains]
        value = sum(math.log10(size) for size in sizes)
        by_size.setdefault(len(spec.activities), []).append(value)
        overall.append(value)
    summary = {"cases": len(overall), "log10_product": {
        "overall": {"min": round(min(overall), 2), "median": round(statistics.median(overall), 2), "max": round(max(overall), 2)},
        **{str(n): {"min": round(min(v), 2), "median": round(statistics.median(v), 2), "max": round(max(v), 2)}
           for n, v in sorted(by_size.items())}}}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
