#!/usr/bin/env python3
"""Render the human projection of the NORMALIZE-01 owner decision."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `decision.json`; it is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selected option: `{data['selection']['option_id']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Accepted normalization digest: `{data['accepted_candidate']['sha256']}`",
        "",
        "## Selection",
        "",
        data["selection"]["rationale"],
        "",
        f"Source: {data['selection']['selection_source']}",
        "",
        "## Resolved defaults",
        "",
        "| ID | Question | Selection | Consequence |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["resolved_defaults"]:
        lines.append("| " + " | ".join(esc(item[key]) for key in ("decision_id", "question", "selection", "effect")) + " |")

    lines.extend(["", "## Admissibility", ""])
    lines.extend([
        f"- Route outcome: `{data['admissibility']['route_outcome']}`",
        f"- Request digest: `{data['admissibility']['request_digest']}`",
        f"- Materialization order: `{data['admissibility']['materialization_order']}`",
        f"- Limitation: {data['admissibility']['ordering_limitation']}",
        "",
        "## Effects and limits",
        "",
        data["normalization_result"]["effect"],
        "",
    ])
    lines.extend(f"- {item}" for item in data["non_effects"])
    lines.extend(["", "## Successor blockers", ""])
    lines.extend(f"- {item}" for item in data["successor_blockers"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
