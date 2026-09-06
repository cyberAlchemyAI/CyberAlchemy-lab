#!/usr/bin/env python3
"""Render the CTX08 conformance suite view."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "suite.json"
OUTPUT = ROOT / "TESTING.md"


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit suite.json and rerun render.py. -->",
        "",
        "# CTX08 normalized context successor conformance",
        "",
        "> Machine-canonical suite; this Markdown is a generated projection.",
        "",
        f"- Suite: `{data['suite_id']}`",
        f"- Subject: `{data['subject']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Bound materials",
        "",
        "| Name | Path | Digest |",
        "| --- | --- | --- |",
    ]
    for item in data["bound_materials"]:
        lines.append(f"| `{item['name']}` | `{item['path']}` | `{item['sha256']}` |")
    lines.extend(["", "## Tests", ""])
    for item in data["tests"]:
        lines.extend([f"### {item['test_id']}", "", f"Command: `{' '.join(item['command'])}`", "", "Expected stdout:", ""])
        lines.extend(f"- `{line}`" for line in item["expected_stdout"])
        lines.append("")
    lines.extend(["## Success gate", "", data["success_gate"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
