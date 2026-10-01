"""Check explicit frozen blocks, then export separate study estimands; no inference."""

import argparse
from pathlib import Path
from scheduling.evaluation.runner import read, write_new
from scheduling.evaluation.study import analyze_blocks, export_study


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "blocks",
        type=Path,
        help="JSON object: controlled, optional realistic/language paths relative to this file",
    )
    p.add_argument("directory", type=Path)
    p.add_argument("--no-archive", action="store_true")
    p.add_argument(
        "--development", action="store_true",
        help="Analyze explicitly development-labelled blocks; never grants frozen-study status",
    )
    p.add_argument(
        "--figures",
        action="store_true",
        help="Export existing diagnostic figures (requires plots extra)",
    )
    a = p.parse_args()
    if a.no_archive and a.figures:
        p.error("--figures requires archive export")
    blocks = {k: a.blocks.parent / v for k, v in read(a.blocks).items()}
    if a.no_archive:
        result = analyze_blocks(blocks, development=a.development)
        a.directory.mkdir(parents=True, exist_ok=False)
        write_new(a.directory / "analysis.json", result)
    else:
        result = export_study(
            blocks,
            a.directory,
            project_root=Path(__file__).resolve().parents[1],
            figures=a.figures,
            development=a.development,
        )
    print(result["counts"])


if __name__ == "__main__":
    main()
