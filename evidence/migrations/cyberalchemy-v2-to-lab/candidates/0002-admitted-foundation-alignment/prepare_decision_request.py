#!/usr/bin/env python3
"""Generate the one-checkpoint, four-decision request after product validation PASS."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"
OUTPUT = ROOT / "receipts/decision-request/decision-request-set.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(LAB).as_posix(), "sha256": sha(path)}


def main() -> int:
    receipt_path = ROOT / "receipts/validation.json"
    receipt = load(receipt_path)
    if receipt.get("result") != "PASS" or receipt.get("assessment", {}).get("product_candidate") != "TESTED":
        print("DECISION_REQUEST=BLOCK\nREASON=product-candidate-not-tested")
        return 1
    manifest_path = ROOT / "manifest.json"
    common_invalidation = ["candidate manifest digest changes", "validation receipt digest changes", "selected source digest changes", "target precondition changes"]
    requests = [
        {
            "request_id": "CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL", "sequence": 1, "decision_kind": "product-approval", "owner_ref": "role:cyberalchemy-lab-product-owner", "authority_scope_ref": "scope:repository-migration-product",
            "targets": [target(manifest_path), target(receipt_path)], "requested_outcome": "approve", "requested_effect": "approve exact tested migration product only", "depends_on": [], "invalidation_conditions": common_invalidation,
        },
        {
            "request_id": "CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION", "sequence": 2, "decision_kind": "definition-admission", "owner_ref": "role:definition-owner", "authority_scope_ref": "scope:repository-migration-manifest-definition",
            "targets": [target(DEFINITION_ROOT / "definitions/repository-migration-manifest/v1/definition.json"), target(DEFINITION_ROOT / "registry-postimage.json"), target(DEFINITION_ROOT / "receipts/validation.json")], "requested_outcome": "approve", "requested_effect": "admit exact Repository Migration Manifest Definition and synchronized registry postimage", "depends_on": ["CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL"], "invalidation_conditions": common_invalidation + ["Definition candidate or validation receipt changes"],
        },
        {
            "request_id": "CAL-MIGRATION-0002-DR3-ARTIFACT-TYPE-ADMISSION", "sequence": 3, "decision_kind": "artifact-type-admission", "owner_ref": "role:artifact-type-owner", "authority_scope_ref": "scope:repository-migration-manifest-artifact-type",
            "targets": [target(TYPE_ROOT / "artifact.json"), target(TYPE_ROOT / "schema.json"), target(TYPE_ROOT / "receipts/validation.json")], "requested_outcome": "approve", "requested_effect": "admit exact Repository Migration Manifest/v1 Artifact Type contract", "depends_on": ["CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL", "CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION"], "invalidation_conditions": common_invalidation + ["Artifact Type candidate, schema, or validation receipt changes"],
        },
        {
            "request_id": "CAL-MIGRATION-0002-DR4-EXECUTION-AUTHORIZATION", "sequence": 4, "decision_kind": "migration-execution-authorization", "owner_ref": "role:repository-migration-owner", "authority_scope_ref": "scope:cyberalchemy-v2-to-lab-additive-copy",
            "targets": [target(ROOT / "migration.json"), target(ROOT / "copy-allowlist.json"), target(ROOT / "expected-postimage.json"), target(ROOT / "rollback.json")], "requested_outcome": "approve", "requested_effect": "authorize exact additive copy allowlist with no overwrite, source mutation, deletion, commit, push, publication, release, or deployment", "depends_on": ["CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL", "CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION", "CAL-MIGRATION-0002-DR3-ARTIFACT-TYPE-ADMISSION"], "invalidation_conditions": common_invalidation + ["migration, allowlist, postimage, or rollback digest changes"],
        },
    ]
    request_set = {
        "schema_version": "cyberalchemy-lab-migration-decision-request-set/v1", "decision_request_set_id": "CAL-CAV2-TO-LAB-MIGRATION-DECISION-REQUEST-SET-0002", "status": "awaiting-owner-decision", "authority_effect": "none",
        "candidate_manifest": target(manifest_path), "validation_receipt": target(receipt_path), "interaction_count": 1, "decision_mode": "single-checkpoint-ordered-independent-decisions",
        "semantic_definition_refs": ["craft.definition.decision-checkpoint@1.0.0-candidate.1", "craft.definition.decision-request-set@1.0.0-candidate.1", "craft.definition.user-decision-preference@1.0.0-candidate.1", "craft.definition.workflow-decision-profile@1.0.0-candidate.1"],
        "requests": requests,
        "claim_ceiling": "This request set presents four decisions once but grants none. Every outcome must be explicit and independently recorded before any effect.",
    }
    errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(ROOT / "decision-request-set.schema.json")).iter_errors(request_set))
    if errors:
        print("DECISION_REQUEST=BLOCK")
        print(json.dumps(errors))
        return 1
    dump(OUTPUT, request_set)
    command = f"APPROVE-CYBERALCHEMY-V2-TO-LAB-MIGRATION-V2 set={sha(OUTPUT)} manifest={sha(manifest_path)} receipt={sha(receipt_path)} outcomes=DR1:approve,DR2:approve,DR3:approve,DR4:approve"
    projection = ["<!-- GENERATED FILE: canonical data is decision-request-set.json. -->", "", "# CyberAlchemy-v2 to Lab Migration Decision Request Set", "", "One interaction presents four ordered, independently governed decisions.", ""]
    for item in requests:
        projection += [f"## {item['sequence']}. {item['decision_kind']}", "", f"- Request: `{item['request_id']}`", f"- Owner: `{item['owner_ref']}`", f"- Effect: {item['requested_effect']}", f"- Depends on: `{', '.join(item['depends_on']) if item['depends_on'] else 'none'}`", ""]
    projection += ["## Exact command", "", "```text", command, "```", "", "## Claim ceiling", "", request_set["claim_ceiling"]]
    (OUTPUT.with_name("DECISION-REQUEST-SET.md")).write_text("\n".join(projection).rstrip() + "\n", encoding="utf-8")
    print("DECISION_REQUEST=PASS")
    print(f"SET_SHA256={sha(OUTPUT)}")
    print(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
