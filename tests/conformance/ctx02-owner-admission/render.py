#!/usr/bin/env python3
"""Render CTX02 owner-admission conformance instructions."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit suite.json and rerun render.py. -->", "", "# CTX02 owner-admission conformance", "", "> Machine-canonical suite; this Markdown is a generated projection.", "", f"- Subject: `{data['subject']}`", f"- Tests: `{len(data['tests'])}`", "", "## Commands", "", "| Test | Command |", "| --- | --- |"]
    for item in data["tests"]:
        lines.append(f"| `{item['test_id']}` | `{' '.join(item['command'])}` |")
    lines += ["", "## Protected surfaces", ""]
    lines.extend(f"- `{path}` — `{digest}`" for path, digest in data["protected_hashes"].items())
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
