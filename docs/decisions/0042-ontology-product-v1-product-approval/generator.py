#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    subject = data["subject"]
    approval = data["product_approval"]
    lines = [
        "<!-- Generated from decision.json. Do not edit. -->", "",
        "# Ontology Product v1 Product approval", "",
        f"- Decision: `{data['decision_id']}`",
        f"- Gate: `{data['gate_id']}`",
        f"- Status: `{data['status']}`",
        f"- Decided at: `{data['decided_at']}`",
        f"- Authority effect: `{data['authority_effect']}`", "",
        "## Exact approved subject", "",
        f"- Product: `{subject['product_ref']}`",
        f"- Candidate: `{subject['product_candidate_id']}`",
        f"- Candidate version: `{subject['product_candidate_version']}`",
        f"- Candidate digest: `{subject['product_candidate_sha256']}`",
        f"- Candidate receipt digest: `{subject['candidate_validation_sha256']}`",
        f"- Product-test receipt digest: `{subject['product_test_sha256']}`", "",
        "## Decision source", "",
        f"`{data['decision_source']['verbatim']}`", "",
        "## Product approval", "",
        f"- State: `{approval['state']}`",
        f"- Scope: {approval['scope']}",
        f"- Evidence: `{approval['structural_checks']}/9` structural checks and `{approval['rust_product_tests']}/9` Rust Product tests",
        f"- Graph: `{approval['nodes']}` nodes, `{approval['relations']}` relations, `{approval['typed_residue']}` typed residues", "",
        "## Non-effects", "",
    ]
    lines.extend(f"- {item}" for item in data["non_effects"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "decision.json").read_text(encoding="utf-8"))
    (ROOT / "DECISION.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
