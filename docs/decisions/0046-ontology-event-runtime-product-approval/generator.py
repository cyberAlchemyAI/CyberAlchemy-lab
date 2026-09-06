#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def render(data: dict) -> str:
    subject = data["subject"]
    approval = data["product_approval"]
    lines = [
        "<!-- Generated from decision.json. Do not edit. -->",
        "",
        "# Ontology event-runtime Product approval",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Gate: `{data['gate_id']}`",
        f"- Status: `{data['status']}`",
        f"- Decided at: `{data['decided_at']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Exact approved subject",
        "",
        f"- Product: `{subject['product_ref']}`",
        f"- Candidate: `{subject['product_candidate_id']}`",
        f"- Candidate digest: `{subject['product_candidate_sha256']}`",
        f"- Binding digest: `{subject['binding_sha256']}`",
        f"- Product-test receipt digest: `{subject['product_test_sha256']}`",
        "",
        "## Decision source",
        "",
        f"`{data['decision_source']['verbatim']}`",
        "",
        "## Product approval",
        "",
        f"- State: `{approval['state']}`",
        f"- Scope: {approval['scope']}",
        f"- Rust tests: `{approval['rust_test_cases']}` cases in each of `{approval['deterministic_rust_runs']}` runs",
        f"- Validator tests: `{approval['candidate_validator_tests']}`",
        f"- CLI materializations: `{approval['cli_materializations']}`",
        f"- Initial graph: `{approval['node_count']}` nodes and `{approval['relation_count']}` relations",
        f"- Initial histories: `{approval['semantic_event_count']}` semantic and `{approval['governance_event_count']}` governance events",
        f"- Latest snapshots: `{approval['latest_snapshot_count']}`",
        "",
        "## Next frontier",
        "",
        f"- Stage: `{data['next_frontier']['stage']}`",
        f"- Eligible: `{str(data['next_frontier']['eligible']).lower()}`",
        f"- Permitted effect: {data['next_frontier']['permitted_effect']}",
        f"- Excluded effect: {data['next_frontier']['excluded_effect']}",
        "",
        "## Non-effects",
        "",
    ]
    lines.extend(f"- {item}" for item in data["non_effects"])
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads((ROOT / "decision.json").read_text(encoding="utf-8"))
    (ROOT / "DECISION.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
