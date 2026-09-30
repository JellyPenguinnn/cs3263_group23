"""Check the installed distribution and its source-matched assets without inference.

Run after a noneditable wheel install: python scripts/check_installed.py.
This intentionally rejects editable imports so CI cannot accidentally test the
checkout while claiming that the distributed package was qualified.
"""

import hashlib
from importlib import metadata, resources
import json
from pathlib import Path
import platform
import sysconfig

import scheduling
from scheduling.evaluation.benchmark import render, tiny_fixtures
from scheduling.pipelines.direct import build_messages
from scheduling.pipelines.solver_augmented import build_extraction_messages


def main():
    checkout = Path(__file__).resolve().parents[1]
    installed = Path(scheduling.__file__).resolve()
    library = Path(sysconfig.get_path("purelib")).resolve()
    if not installed.is_relative_to(library):
        raise ValueError("Qualification requires a noneditable installed package")
    hashes = {}
    for case in (tiny_fixtures()[0], tiny_fixtures()[-1]):
        view = render(case)
        messages = build_messages(
            view.text,
            task_type=view.task_type,
            required_activity_ids=view.activity_ids,
            original_schedule=(
                view.original_schedule.to_list() if view.original_schedule else None
            ),
        )
        expected = checkout / "prompts/direct" / f"{view.task_type}.txt"
        assert messages[0].content == expected.read_text(encoding="utf-8")
        hashes[str(expected.relative_to(checkout))] = hashlib.sha256(
            messages[0].content.encode()
        ).hexdigest()
        extracted = build_extraction_messages(view)
        expected = checkout / "prompts/extraction/specification.txt"
        assert extracted[0].content == expected.read_text(encoding="utf-8")
        hashes[str(expected.relative_to(checkout))] = hashlib.sha256(
            extracted[0].content.encode()
        ).hexdigest()
    for package, relative in (
        ("scheduling.providers", "issuer-chain.crt"),
        ("scheduling.dashboard", "static/index.html"),
        ("scheduling.dashboard", "static/app.js"),
        ("scheduling.dashboard", "static/style.css"),
    ):
        payload = resources.files(package).joinpath(relative).read_bytes()
        source = checkout / "src" / package.replace(".", "/") / relative
        assert payload == source.read_bytes(), f"Packaged asset differs: {relative}"
        hashes[str(source.relative_to(checkout))] = hashlib.sha256(payload).hexdigest()
    print(
        json.dumps(
            {
                "evidence": "installed_assets_only_zero_model_calls",
                "distribution_version": metadata.version("cs3263-scheduling"),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "installed_import": str(installed),
                "asset_sha256": hashes,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
