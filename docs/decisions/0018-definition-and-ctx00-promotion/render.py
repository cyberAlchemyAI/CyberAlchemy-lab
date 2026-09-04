#!/usr/bin/env python3
"""Render the Definition and CTX-00 promotion request."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "promotion-request.json"
OUTPUT = ROOT / "PROMOTION-REQUEST.md"


def render(data: dict) -> str:
    candidate = data["bound_candidate"]
    pack = data["bound_successor_pack"]
    lines = ["<!-- GENERATED FILE: edit promotion-request.json and run render.py. -->", "", "# Definition and CTX-00 promotion request", "", "> Generated from the machine-canonical request. No option is selected.", "", f"- Request: `{data['request_id']}`", f"- Status: `{data['status']}`", f"- Owner gate: `{data['owner_gate']['role_id']}` → `{data['owner_gate']['principal_id']}`", f"- Recommended option: `{data['recommended_option_id']}`", "", "## Decision", "", data["decision_question"], "", "## Bound evidence", "", f"- Candidate: `{candidate['sha256']}` — `{candidate['validation_result']}` {candidate['validation_checks']}/{candidate['validation_checks']}", f"- Successor pack: `{pack['sha256']}` — `{pack['validation_result']}` {pack['validation_checks']}/{pack['validation_checks']}", f"- Live registry preimage: `{data['live_preimage']['registry_sha256']}` with `{data['live_preimage']['entry_count']}` entries", "", "## Selected Definition IDs", ""]
    lines.extend(f"- `{item}`" for item in data["selected_definition_ids"])
    lines.extend(["", "## Effect if admitted", "", data["decision_effect_if_admitted"], "", "## Non-effects", ""])
    lines.extend(f"- {item}" for item in data["non_effects"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")
