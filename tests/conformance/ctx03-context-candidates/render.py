#!/usr/bin/env python3
"""Render the CTX03 conformance suite projection."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX03 context candidate conformance",
        "",
        "> Generated from `suite.json`; this view is not canonical.",
        "",
        f"- Suite: `{data['suite_id']}`",
        f"- Subject: `{data['subject']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Tests",
        "",
    ]
    for test in data["tests"]:
        lines.extend([
            f"### {test['test_id']}",
            "",
            f"- Command: `{' '.join(test['command'])}`",
            f"- Expected exit: `{test['expected_exit_code']}`",
            f"- Expected output: `{'; '.join(test['expected_stdout'])}`",
            "",
        ])
    lines.extend(["## Success condition", "", data["success_condition"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
