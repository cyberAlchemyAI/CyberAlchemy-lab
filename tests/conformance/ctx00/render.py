#!/usr/bin/env python3
"""Render CTX-00 test instructions from the canonical suite."""

import json
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit suite.json and run render.py. -->", "", "# Test the CTX-00 semantic candidate", "", "> Generated from `suite.json`; the suite definition is canonical.", "", "From the CyberAlchemy Lab repository root, run:", "", "```bash", "python3 tests/conformance/ctx00/run.py", "```", "", "## Included checks", ""]
    for item in data["tests"]:
        lines.extend([f"### {item['test_id']}", "", f"`{shlex.join(item['command'])}`", "", f"Expected exit code: `{item['expected_exit_code']}`", ""])
    lines.extend(["## Success condition", "", data["success_condition"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
