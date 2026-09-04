#!/usr/bin/env python3
"""Validate the context-operations owner-registry successor candidate."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[5]
PREDECESSOR = ROOT.parents[1] / "owners.json"
SCHEMA = LAB / "authority/foundation/v1/schema.json"
FOUNDATION_DECISION = LAB / "docs/decisions/0013-foundation-01-admission/decision.json"
CTX01_DECISION = LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json"
CTX01_ADMISSION_RECEIPT = LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/receipts/admission-validation.json"
FOUNDATION_RENDERER = LAB / "authority/foundation/v1/render.py"
RECEIPT = ROOT / "receipts/validation.json"

EXPECTED = {
    PREDECESSOR: "bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d",
    SCHEMA: "b09e0dbac01d29e7877b7131cf931334e89a87b9defa24e60a1a0bec59c100f9",
    FOUNDATION_DECISION: "2aec4fc4cee04804047dbdfecdf521837b0bd1b006fc6b7ea55f46c9a15b4f52",
    CTX01_DECISION: "dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23",
    CTX01_ADMISSION_RECEIPT: "f12de31c189a8c1679b9641a7a61b131c380135240a2c58caa367a2596fb9096",
    FOUNDATION_RENDERER: "ae0f0561fd272121382ae8e077908f735aa31a9686bb2f87057015a5b91b4ac2",
}
FOUNDATION_ROLES = {"artifact-mechanics-owner", "artifact-type-owner", "definition-owner", "source-admission-owner", "evidence-conformance-owner"}
OPERATIONAL_ROLES = {
    "lab-architecture-owner",
    "governance-context-owner",
    "ontology-lifecycle-context-owner",
    "governance-language-owner",
    "ontology-lifecycle-language-owner",
    "coordination-context-owner",
    "context-map-owner",
    "capability-instance-owner",
    "context-migration-owner",
    "context-lineage-owner",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    candidate, predecessor, schema = load(SOURCE), load(PREDECESSOR), load(SCHEMA)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    owner_schema = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/ownerRegistry"}
    errors = [error.message for error in Draft202012Validator(owner_schema).iter_errors(candidate)]
    check("owner-registry-schema-valid", not errors, errors)
    check("candidate-no-authority", candidate.get("status") == "candidate-unadmitted" and candidate.get("authority_effect") == "none", {"status": candidate.get("status"), "authority_effect": candidate.get("authority_effect")})
    check("bound-inputs-current", all(sha(path) == digest for path, digest in EXPECTED.items()), {str(path.relative_to(LAB)): sha(path) for path in EXPECTED})
    assignments = candidate["role_assignments"]
    predecessor_assignments = {item["role_id"]: item for item in predecessor["role_assignments"]}
    candidate_assignments = {item["role_id"]: item for item in assignments}
    check("foundation-role-preservation", set(predecessor_assignments) == FOUNDATION_ROLES and all(candidate_assignments.get(role) == value for role, value in predecessor_assignments.items()), sorted(predecessor_assignments))
    check("operational-role-closure", set(candidate_assignments) - FOUNDATION_ROLES == OPERATIONAL_ROLES and len(assignments) == 15, sorted(set(candidate_assignments) - FOUNDATION_ROLES))
    check("role-and-assignment-identity-unique", len(candidate_assignments) == len(assignments) and len({item["assignment_id"] for item in assignments}) == len(assignments), {"roles": len(candidate_assignments), "assignments": len({item["assignment_id"] for item in assignments})})
    check("principal-preserved", candidate["principals"] == predecessor["principals"] and candidate.get("owner_ref") == "person:<vrondelli>" and all(item["principal_id"] == "person:<vrondelli>" for item in assignments), candidate["principals"])
    check("decision-separation-universal", all(item.get("decision_separation") == "required" for item in assignments) and "no field or role is silently inferred from another" in candidate.get("separation_rule", ""), candidate.get("separation_rule"))
    context_pair = [candidate_assignments["governance-context-owner"], candidate_assignments["ontology-lifecycle-context-owner"]]
    language_pair = [candidate_assignments["governance-language-owner"], candidate_assignments["ontology-lifecycle-language-owner"]]
    check("context-authority-non-collapse", "excludes Ontology Lifecycle" in context_pair[0]["scope"] and "excludes Governance" in context_pair[1]["scope"], [item["scope"] for item in context_pair])
    check("language-authority-non-collapse", "excludes Ontology Lifecycle" in language_pair[0]["scope"] and "excludes Governance" in language_pair[1]["scope"] and all("canonical Definition promotion" in item["scope"] for item in language_pair), [item["scope"] for item in language_pair])
    check("map-migration-lineage-separate", "endpoint context admission" in candidate_assignments["context-map-owner"]["scope"] and "destructive execution" in candidate_assignments["context-migration-owner"]["scope"] and "inferring equivalence" in candidate_assignments["context-lineage-owner"]["scope"], {role: candidate_assignments[role]["scope"] for role in ("context-map-owner", "context-migration-owner", "context-lineage-owner")})
    check("admitted-predecessors-resolve", load(FOUNDATION_DECISION).get("status") == "owner-admitted" and load(CTX01_DECISION).get("status") == "owner-admitted" and load(CTX01_ADMISSION_RECEIPT).get("result") == "PASS", {"foundation": load(FOUNDATION_DECISION).get("status"), "ctx01": load(CTX01_DECISION).get("status"), "receipt": load(CTX01_ADMISSION_RECEIPT).get("result")})
    rendered_a, rendered_b = render(candidate), render(candidate)
    check("projection-determinism-and-parity", rendered_a == rendered_b and OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a, hashlib.sha256(rendered_a.encode()).hexdigest())
    check("claim-ceiling-bounded", all(term in candidate.get("claim_ceiling", "") for term in ("does not admit", "activate any new role", "create a context", "stable release")), candidate.get("claim_ceiling"))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-owner-registry-successor-validation/v1",
        "subject": candidate["record_id"],
        "candidate_epoch": "0002-context-operations",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "promotion_eligibility": "eligible-for-exact-owner-registry-promotion-decision" if result == "PASS" else "blocked",
        "materials": {"owners_json_sha256": sha(SOURCE), "owners_md_sha256": sha(OUTPUT) if OUTPUT.is_file() else None, "predecessor_sha256": sha(PREDECESSOR)},
        "claim_ceiling": "PASS proves representation, predecessor preservation, role orthogonality, and exact bindings only; it does not admit or activate any new role."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX02_OWNER_REGISTRY_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
