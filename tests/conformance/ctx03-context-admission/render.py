#!/usr/bin/env python3
"""Render CTX03 context-language admission conformance instructions."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX03 context-language admission conformance",
        "",
        "> Machine-canonical suite; this Markdown is a generated projection.",
        "",
        f"- Subject: `{data['subject']}`",
        f"- Tests: `{len(data['tests'])}`",
        "",
        "## Commands",
        "",
        "| Test | Command |",
        "| --- | --- |",
    ]
    for item in data["tests"]:
        lines.append(f"| `{item['test_id']}` | `{' '.join(item['command'])}` |")
    lines.extend(["", "## Protected surfaces", ""])
    lines.extend(f"- `{path}` — `{digest}`" for path, digest in data["protected_hashes"].items())
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
