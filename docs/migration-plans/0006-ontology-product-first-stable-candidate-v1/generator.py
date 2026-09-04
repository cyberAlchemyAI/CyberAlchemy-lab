#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    construction = data["product_construction"]
    boundary = data["approval_boundary"]
    lines = [
        "<!-- Generated from plan.json. Do not edit. -->", "",
        "# Ontology Product L4 first-stable candidate plan", "",
        f"- Plan: `{data['plan_id']}`",
        f"- Status: `{data['status']}`",
        f"- Route: `{data['route']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Unit: `{data['execution_unit']['unit_id']}`", "",
        "## Product construction frontier", "",
        f"`{construction['frontier']}`", "",
        "### Runnable now", "",
    ]
    lines.extend(f"- {item}" for item in construction["runnable_now"])
    lines += ["", "### Done criteria", ""]
    lines.extend(f"- {item}" for item in construction["done_criteria"])
    lines += ["", "## Operational support residue", ""]
    lines.extend(
        f"- {item['task']} — owner `{item['owner']}`; {item['blocking_posture']}."
        for item in data["operational_support"]
    )
    lines += [
        "", "## Single approval boundary", "",
        boundary["decision"], "",
        f"If approved: `{boundary['effect_if_approved']}`.", "",
        "Approval does not grant:", "",
    ]
    lines.extend(f"- {item}" for item in boundary["not_granted"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    (ROOT / "PLAN.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
