#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    evidence = data["product_test_evidence"]
    approval = data["product_approval"]
    lines = [
        "<!-- Generated from candidate.json. Do not edit. -->", "",
        "# Ontology Product candidate 0004 — first stable candidate", "",
        f"- Candidate: `{data['candidate_id']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Predecessor: `{data['predecessor']['candidate_ref']}`", "",
        "## Exact Product-test evidence", "",
        f"- Receipt: `{data['product_test_evidence']['receipt_ref']}`",
        f"- Receipt digest: `{evidence['receipt_sha256']}`",
        f"- Selected source digest: `{evidence['selected_source_sha256']}`",
        f"- Package digest: `{evidence['package_sha256']}`",
        f"- Structural checks: `{evidence['structural_checks']}/9`",
        f"- Rust behavior tests: `{evidence['rust_product_tests']}/9`",
        f"- Graph: `{evidence['nodes']}` nodes, `{evidence['relations']}` relations, `{evidence['typed_residue']}` typed residues", "",
        "## Acceptance criteria", "",
    ]
    lines.extend(f"- {item}" for item in data["acceptance_criteria"])
    lines += [
        "", "## Single Product approval boundary", "",
        f"- Eligible: `{str(approval['eligible']).lower()}`",
        f"- Granted: `{str(approval['granted']).lower()}`",
        f"- Scope: `{approval['decision_scope']}`",
        f"- Binding: {approval['binding_rule']}", "",
        "Approval does not grant:", "",
    ]
    lines.extend(f"- {item}" for item in approval["not_granted"])
    lines += ["", "## Visible operational residue", ""]
    lines.extend(f"- {item}" for item in data["operational_residue"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    (ROOT / "CANDIDATE.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
