#!/usr/bin/env python3
"""Render the CTX07 artifact-type conformance suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX07 normalized artifact-type conformance",
        "",
        "> Generated from `suite.json`; this view is not canonical.",
        "",
        f"- Suite: `{data['suite_id']}`",
        f"- Subject: `{data['subject']}`",
        f"- Status: `{data['status']}`",
        "",
        "## Tests",
        "",
        "| Test | Command | Expected output |",
        "| --- | --- | --- |",
    ]
    for test in data["tests"]:
        lines.append(f"| `{test['test_id']}` | `{' '.join(test['command'])}` | `{' ; '.join(test['expected_stdout'])}` |")
    lines.extend(["", "## Run", "", "```bash", "python3 tests/conformance/ctx07-artifact-types/run.py", "```", "", "## Success condition", "", data["success_condition"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
