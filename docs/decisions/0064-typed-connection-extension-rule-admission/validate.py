#!/usr/bin/env python3
"""Validate the Typed Connection Extension Rule Definition admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
REGISTRY = LAB / "authority/definitions/registry.json"
INDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DRIFT = LAB / "authority/definitions/drift-audit.json"
DEFINITION = LAB / "authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/definition.json"
SOURCE_VALIDATION = LAB / "authority/definitions/candidates/0012-typed-connection-extension-rule/receipts/validation.json"
DECISION_ID = "CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION"
DEFINITION_ID = "cal.definition.typed-connection-extension-rule"
DEFINITION_REF = f"{DEFINITION_ID}@1.0.0-candidate.1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    registry = load(REGISTRY)
    drift = load(DRIFT)
    decision = load(ROOT / "decision.json")
    authorization = load(ROOT / "authorization.json")
    source_validation = load(SOURCE_VALIDATION)
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    entries = [item for item in registry["entries"] if item["definition_id"] == DEFINITION_ID]
    check("authorization-binds-approved-definition", authorization["definition"]["sha256"] == sha(DEFINITION) == "9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962", authorization["definition"])
    check("candidate-validation-pass", source_validation.get("result") == "PASS" and source_validation.get("summary") == {"failed": 0, "passed": 19, "total": 19}, source_validation.get("summary"))
    check("decision-owner-admitted", decision.get("status") == "owner-admitted" and decision.get("decision_id") == DECISION_ID, decision.get("status"))
    check("registry-counts", len(registry["entries"]) == 119 and len(registry["current_lookup"]) == 113, {"versions": len(registry["entries"]), "current": len(registry["current_lookup"])})
    check("exact-entry-admitted", len(entries) == 1 and entries[0]["lifecycle_state"] == "admitted" and entries[0]["admission_decision_ref"] == DECISION_ID and entries[0]["sha256"] == sha(DEFINITION), entries)
    check("current-selection", registry["current_lookup"].get(DEFINITION_ID) == DEFINITION_REF, registry["current_lookup"].get(DEFINITION_ID))
    check("index-projection", DEFINITION_REF in INDEX.read_text(encoding="utf-8") and DECISION_ID in INDEX.read_text(encoding="utf-8"), sha(INDEX))
    check("drift-binds-registry", drift.get("registry_sha256") == sha(REGISTRY) and drift["summary"].get("typed_connection_extension_rule") == "admitted-current", drift.get("registry_sha256"))
    check("downstream-effects-separated", decision["admission_result"] == {"canonical_definition_versions": 119, "consumer_activations": 0, "current_definition_identities": 113, "definitions_admitted": 1, "endpoint_pairs_admitted": 0, "relation_kinds_admitted": 0, "result": "complete"}, decision["admission_result"])

    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-admission-validation/v1",
        "subject": DECISION_ID,
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "evidence-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "authorization_sha256": sha(ROOT / "authorization.json"),
            "decision_sha256": sha(ROOT / "decision.json"),
            "definition_sha256": sha(DEFINITION),
            "registry_sha256": sha(REGISTRY),
            "index_sha256": sha(INDEX),
            "drift_audit_sha256": sha(DRIFT),
        },
        "claim_ceiling": "PASS proves the exact Definition admission and registry projection only. It does not admit Relation Kinds, endpoint pairs, qualifier schemas, endpoint carriers, Typed Relations, instances, consumers, or runtimes.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"TYPED_CONNECTION_EXTENSION_RULE_ADMISSION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
