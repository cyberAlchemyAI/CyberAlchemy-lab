#!/usr/bin/env python3
"""Render the Ontology Lifecycle context-placement decision."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    model = data["selected_context_model"]
    boundary = model["governance_boundary"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `decision.json`; it is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selected option: `{selection['option_id']}`",
        f"- Principal: `{selection['selected_by_principal']}`",
        f"- Role posture: `{selection['selected_under_role']}` (`{selection['role_binding_status']}`)",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Selected model",
        "",
        f"Ontology Lifecycle is selected as the separate bounded-context candidate `{model['bounded_context_candidate_id']}`.",
        "",
        f"- Candidate path: `{model['candidate_target_path']}`",
        f"- Current package: `{model['current_package_path']}`",
        f"- Current disposition: `{model['current_package_disposition']}`",
        f"- Dependency direction: `{boundary['dependency_direction']}`",
        f"- Upstream: `{boundary['upstream_context']}`",
        f"- Downstream: `{boundary['downstream_context']}`",
        f"- Context-map pattern: `{boundary['context_map_pattern']}`",
        "",
        boundary["dependency_semantics"],
        "",
        "## Semantic scope",
        "",
    ]
    lines.extend(f"- {item}" for item in model["semantic_scope"])
    lines.extend(["", "## Semantic exclusions", ""])
    lines.extend(f"- {item}" for item in model["semantic_exclusions"])
    lines.extend(["", "## Non-collapse rules", ""])
    lines.extend(f"- {item}" for item in model["non_collapse_rules"])
    lines.extend([
        "",
        "## Decision Gate",
        "",
        f"- Result: `{data['decision_result']['decision_gate_result']}`",
        f"- Route: `{data['admissibility']['route_outcome']}`",
        f"- Request digest: `{data['admissibility']['request_digest']}`",
        f"- Limitation: {data['admissibility']['ordering_limitation']}",
        "",
        "## Residue transition",
        "",
        "### Resolved",
        "",
    ])
    lines.extend(f"- `{item['residue_id']}` — {item['resolution']}" for item in data["residue_transition"]["resolved"])
    lines.extend(["", "### Remaining", ""])
    lines.extend(f"- `{item['residue_id']}` — {item['condition']}" for item in data["residue_transition"]["remaining"])
    lines.extend(["", "## Explicit exclusions", ""])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
