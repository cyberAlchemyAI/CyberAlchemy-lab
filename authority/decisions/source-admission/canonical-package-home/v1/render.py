#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit admissions.json and run render.py. -->",
        "",
        "# Canonical Package Home source admissions",
        "",
        f"- Record: `{data['record_id']}`",
        f"- Status: `{data['status']}`",
        f"- Owner: `{data['owner_ref']}` / `{data['owner_principal_ref']}`",
        "",
        "| Admission | Selector | Digest | Permitted use |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admissions"]:
        selector = f"{item['source_path']}:{item['start_line']}-{item['end_line']}"
        lines.append(f"| `{item['admission_id']}` | `{selector}` | `{item['selected_sha256']}` | {item['target_use']} |")
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    data = json.loads((ROOT / "admissions.json").read_text(encoding="utf-8"))
    (ROOT / "SOURCE-ADMISSIONS.md").write_text(render(data), encoding="utf-8")
