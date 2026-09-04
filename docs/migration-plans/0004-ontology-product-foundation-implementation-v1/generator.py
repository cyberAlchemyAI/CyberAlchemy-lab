#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(plan: dict) -> str:
    construction = plan["product_construction"]
    lines = [
        "<!-- Generated from plan.json. Do not edit. -->",
        "",
        "# Ontology Product foundation implementation",
        "",
        f"- Plan: `{plan['plan_id']}`",
        f"- Unit: `{plan['execution_unit']['unit_id']}`",
        f"- Status: `{plan['status']}`",
        f"- Authority effect: `{plan['authority_effect']}`",
        "",
        "## Objective",
        "",
        plan["objective"],
        "",
        "## Product construction",
        "",
    ]
    lines.extend(f"- {item}" for item in construction["deliverables"])
    lines += ["", "## Done criteria", ""]
    lines.extend(f"- {item}" for item in construction["done_criteria"])
    lines += ["", "## Operational support", ""]
    for item in plan["operational_support"]:
        lines.append(f"- **{item['blocking_posture']}** — {item['task']} — owner `{item['owner']}` — affects `{item['affected_stage']}`")
    lines += ["", "## Validation", "", "```bash"]
    lines.extend(plan["validation"]["commands"])
    lines += ["```", "", "## Approval boundary", "", f"Mode: `{plan['approval_boundary']['mode']}`. This increment does not request approval.", "", "## Claim ceiling", "", plan["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    (ROOT / "PLAN.md").write_text(render(plan), encoding="utf-8")


if __name__ == "__main__":
    main()
