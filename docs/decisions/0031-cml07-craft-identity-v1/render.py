#!/usr/bin/env python3
"""Render human projections for CML-07 final admission decision 0031."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_authorization(data: dict) -> str:
    return (
        "<!-- GENERATED FILE: canonical source is authorization.json. -->\n\n"
        "# CML-07 Craft Identity v1 Authorization\n\n"
        f"- Authorization: `{data['authorization_id']}`\n"
        f"- Principal: `{data['principal_id']}`\n"
        f"- Status: `{data['status']}`\n"
        f"- Decision boundary: `{data['decision_boundary']}`\n"
        f"- Approval interactions: `{data['approval_interactions']}`\n"
        f"- Manifest: `{data['manifest']['sha256']}`\n"
        f"- Validation receipt: `{data['validation_receipt']['sha256']}`\n\n"
        "## Separation\n\n"
        f"{data['decision_separation']}\n\n"
        "## Authority ceiling\n\n"
        f"{data['authority_ceiling']}\n"
    )


def render_decision(data: dict) -> str:
    carriers = "".join(
        f"- `{item['identity_ref']}` — `{item['artifact_type_ref']}` — owner `role:{item['owner_role']}`\n"
        for item in data["admitted_carriers"]
    )
    relations = "".join(
        f"- `{item['relation_id']}`: `{item['source_ref']}` — **{item['relation_kind']}** → `{item['target_ref']}`\n"
        for item in data["admitted_relations"]
    )
    result = data["admission_result"]
    conformance = data["recognized_conformance"]
    return (
        "<!-- GENERATED FILE: canonical source is decision.json. -->\n\n"
        "# CML-07 Craft Identity v1 Final Admission\n\n"
        f"- Decision: `{data['decision_id']}`\n"
        f"- Status: `{data['status']}`\n"
        f"- Approval interactions: `{result['approval_interactions']}`\n"
        f"- Identity carriers admitted: `{result['identity_carriers_admitted']}`\n"
        f"- Identity relations admitted: `{result['identity_relations_admitted']}`\n"
        f"- CML-07 status: `{result['cml07_status']}`\n\n"
        "## Admitted carriers\n\n"
        f"{carriers}\n"
        "## Admitted relations\n\n"
        f"{relations}\n"
        "## Scoped conformance recognized\n\n"
        f"- Validation: `{conformance['validation_result']}`\n"
        f"- Schema conformance: `{conformance['schema_conformance']}`\n"
        f"- Identity-contract conformance: `{conformance['identity_contract_conformance']}`\n"
        f"- Implementation conformance: `{conformance['implementation_conformance']}`\n"
        f"- Runtime conformance: `{conformance['runtime_conformance']}`\n\n"
        "## Preserved boundaries\n\n"
        f"- Candidate files rewritten: `{result['candidate_files_rewritten']}`\n"
        f"- Craft root Bounded Context: `{result['craft_root_bounded_context']}`\n"
        f"- Goal achievement: `{result['goal_achievement']}`\n"
        f"- Migration completion: `{result['migration_completion']}`\n\n"
        "## Claim ceiling\n\n"
        f"{data['claim_ceiling']}\n"
    )


def main() -> int:
    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    (ROOT / "AUTHORIZATION.md").write_text(render_authorization(authorization), encoding="utf-8")
    (ROOT / "DECISION.md").write_text(render_decision(decision), encoding="utf-8")
    print("CML07_DECISION_PROJECTIONS=GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
