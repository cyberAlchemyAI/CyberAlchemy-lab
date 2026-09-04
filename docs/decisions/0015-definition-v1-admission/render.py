#!/usr/bin/env python3
"""Render the Definition/v1 artifact-type admission decision."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    candidate = data["accepted_candidate"]
    contract = data["admitted_contract"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `decision.json`; it is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Principal: `{data['selection']['selected_by_principal']}`",
        f"- Owner role: `{data['selection']['selected_under_role']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Admitted type: `{contract['artifact_type_ref']}`",
        f"- Candidate source version: `{candidate['candidate_version']}`",
        f"- Candidate digest: `{candidate['sha256']}`",
        "",
        "## Effect",
        "",
        contract["effect"],
        "",
        contract["candidate_state_overlay"],
        "",
        "## Contract scope",
        "",
    ]
    lines.extend(f"- {item}" for item in contract["scope"])
    lines.extend([
        "",
        "## Decision Gate",
        "",
        f"- Result: `{data['admission_result']['decision_gate_result']}`",
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
