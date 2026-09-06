#!/usr/bin/env python3
"""Render the post-admission CTX00 conformance suite."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX00 post-admission conformance",
        "",
        "> Generated from `suite.json`; this view is not canonical.",
        "",
        f"- Suite: `{data['suite_id']}`",
        f"- Status: `{data['status']}`",
        f"- Subject: `{data['subject']}`",
        "",
        "## Tests",
        "",
        "| Test | Command | Expected output |",
        "| --- | --- | --- |",
    ]
    for test in data["tests"]:
        command = " ".join(test["command"])
        expected = "; ".join(test["expected_stdout"])
        lines.append(f"| `{test['test_id']}` | `{command}` | `{expected}` |")
    lines.extend([
        "",
        "## Success condition",
        "",
        data["success_condition"],
        "",
        "## Historical suite boundary",
        "",
        data["historical_suite_boundary"],
        "",
        "## Run",
        "",
        "```bash",
        "python3 tests/conformance/ctx00-admission/run.py",
        "```",
        "",
        "## Claim ceiling",
        "",
        data["claim_ceiling"],
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
