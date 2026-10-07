#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def render_instance(data: dict) -> str:
    def ref(value):
        return f"`{value}`" if value is not None else "none"

    lines = [
        "<!-- GENERATED FILE: edit coordination-context.json and run generator.py. -->",
        "",
        f"# {data['coordination_context_id']}",
        "",
        f"- Version: `{data['version']}`",
        f"- Product: {ref(data['product_ref'])}",
        f"- Project: {ref(data['project_ref'])}",
        f"- Goal: {ref(data['goal_ref'])}",
        f"- Owner: `{data['owner_ref']}`",
        f"- Lifecycle: `{data['lifecycle_state']}`",
        f"- Predecessor: {ref(data['predecessor_ref'])}",
        "",
        "## Purpose",
        "",
        data["purpose"],
        "",
        "## Subject scope",
        "",
        data["subject_scope"]["statement"],
        "",
        "## Bounded Context references",
        "",
    ]
    lines.extend(f"- `{value}`" for value in data["bounded_context_refs"])
    if not data["bounded_context_refs"]:
        lines.append("- none")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_artifact(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit artifact.json and run generator.py. -->",
        "",
        "# Coordination Context Artifact Type v2",
        "",
        f"- Artifact Type: `{data['artifact_type_ref']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Distinct validation purpose",
        "",
        data["distinct_validation_purpose"],
        "",
        "## Orthogonality rules",
        "",
    ]
    lines.extend(
        f"- **{item['rule_id']}**: {item['statement']}"
        for item in data["orthogonality_rules"]
    )
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    artifact = json.loads((ROOT / "artifact.json").read_text())
    fixture = json.loads((ROOT / "fixtures/valid/product-project-goal.json").read_text())
    (ROOT / "ARTIFACT.md").write_text(render_artifact(artifact))
    (ROOT / "fixtures/valid/COORDINATION-CONTEXT.md").write_text(
        render_instance(fixture)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
