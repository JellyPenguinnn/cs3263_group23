"""Prepare controlled candidates offline; final mode needs a prior policy decision."""

import argparse
from pathlib import Path
from scheduling.evaluation.preparation import CandidatePolicy, prepare
from scheduling.evaluation.runner import read


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument(
        "--policy",
        type=Path,
        help="Versioned CandidatePolicy JSON; default is a development pilot",
    )
    p.add_argument("--mode", choices=("development", "final"), default="development")
    p.add_argument(
        "--freeze",
        type=Path,
        help="Actual prior policy/model decision; never inferred from test receipts",
    )
    a = p.parse_args()
    result = prepare(
        a.directory,
        CandidatePolicy(**read(a.policy)) if a.policy else CandidatePolicy(),
        a.seed,
        read(a.registry),
        mode=a.mode,
        freeze=read(a.freeze) if a.freeze else None,
    )
    print(
        {
            k: result[k]
            for k in (
                "mode",
                "case_count",
                "family_count",
                "quota_complete",
                "coupled_sat_repairs",
            )
        }
    )
    return 0 if result["quota_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
