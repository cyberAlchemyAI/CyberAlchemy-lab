#!/usr/bin/env python3
"""Render the CTX05 conformance suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX05 context successor candidate conformance",
        "",
        "> Machine-canonical suite; this Markdown is a generated projection.",
        "",
        f"- Suite: `{data['suite_id']}`",
        f"- Subject: `{data['subject']}`",
        f"- Status: `{data['status']}`",
        "",
        "## Tests",
        "",
    ]
    for item in data["tests"]:
        lines.append(f"- `{item['test_id']}`: `{' '.join(item['command'])}`")
    lines.extend(["", "## Protected hashes", ""])
    lines.extend(f"- `{path}`: `{digest}`" for path, digest in data["protected_hashes"].items())
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
