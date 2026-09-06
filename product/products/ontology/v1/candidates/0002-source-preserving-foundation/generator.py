#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    lines = [
        "<!-- Generated from candidate.json. Do not edit. -->",
        "",
        "# Ontology Product source-preserving foundation",
        "",
        f"- Candidate: `{data['candidate_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Predecessor: `{data['predecessor']['candidate_ref']}`",
        "",
        "## Construction increment",
        "",
        f"- Unit: `{data['construction_increment']['unit_id']}`",
        f"- Source package: `{data['construction_increment']['source_package_ref']}`",
        f"- Artifact Type: `{data['construction_increment']['artifact_type_ref']}`",
        "",
        "## Acceptance criteria",
        "",
    ]
    lines.extend(f"- {item}" for item in data["acceptance_criteria"])
    lines += ["", "## Next Product frontier", ""]
    lines.extend(f"- {item}" for item in data["next_product_frontier"]["work"])
    lines += ["", "## Approval boundary", "", data["approval_boundary"], "", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    (ROOT / "CANDIDATE.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
