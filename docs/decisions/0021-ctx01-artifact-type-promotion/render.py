#!/usr/bin/env python3
"""Render the CTX01 artifact-type promotion request."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "promotion-request.json"
OUTPUT = ROOT / "PROMOTION-REQUEST.md"


def render(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit promotion-request.json and rerun render.py. -->", "", "# CTX01 artifact-type promotion request", "", "> Machine-canonical request; this Markdown is a generated projection.", "", f"- Status: `{data['status']}`", f"- Owner gate: `{data['owner_gate']['role_id']} -> {data['owner_gate']['principal_id']}`", f"- Recommended option: `{data['recommended_option_id']}`", "", "## Decision", "", data["decision_question"], "", "## Exact artifact types", ""]
    lines.extend(f"- `{item}`" for item in data["artifact_type_refs"])
    lines += ["", "## Effect if selected", "", data["decision_effect_if_admitted"], "", "## Non-effects", ""]
    lines.extend(f"- {item}" for item in data["non_effects"])
    lines += ["", "## Next step", "", data["next_step_if_admitted"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
