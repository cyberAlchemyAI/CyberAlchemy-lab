#!/usr/bin/env python3
"""Validate the exact 60-Definition integrated Lab model admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CANDIDATE_ROOT = LAB / "authority/definitions/candidates/0013-integrated-lab-definition-model"
REGISTRY = LAB / "authority/definitions/registry.json"
INDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DRIFT = LAB / "authority/definitions/drift-audit.json"
DECISION_ID = "CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    candidate = load(CANDIDATE_ROOT / "candidate.json")
    source_receipt = load(CANDIDATE_ROOT / "receipts/validation.json")
    registry = load(REGISTRY)
    drift = load(DRIFT)
    decision = load(ROOT / "decision.json")
    authorization = load(ROOT / "authorization.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    ids = {x["definition_id"] for x in candidate["definitions"]}
    entries = [x for x in registry["entries"] if x["definition_id"] in ids]
    digest_map = source_receipt["materials"]["definition_digests"]
    exact_entries = all(
        x["lifecycle_state"] == "admitted" and x.get("admission_decision_ref") == DECISION_ID
        and x["sha256"] == digest_map[x["definition_id"]] for x in entries
    )
    exact_current = all(registry["current_lookup"].get(x["definition_id"]) == f"{x['definition_id']}@{x['version']}" for x in candidate["definitions"])
    check("authorization-binds-reviewed-pack", authorization["candidate"]["sha256"] == sha(CANDIDATE_ROOT / "candidate.json") == "a355adf57079efb45a5e0c8431e6cb2b9e7b57536264465ad69c02af53296994", authorization["candidate"])
    check("candidate-validation-pass", source_receipt.get("result") == "PASS" and source_receipt.get("summary") == {"failed": 0, "passed": 19, "total": 19}, source_receipt.get("summary"))
    check("exact-approved-set", len(ids) == 60 and len(candidate["definitions"]) == 60, sorted(ids))
    check("decision-owner-admitted", decision.get("status") == "owner-admitted" and decision.get("decision_id") == DECISION_ID, decision.get("status"))
    check(
        "registry-preserves-admission-poststate",
        len(registry["entries"]) >= 179 and len(registry["current_lookup"]) >= 173,
        {
            "admission_poststate": {"versions": 179, "current": 173},
            "current_registry": {
                "versions": len(registry["entries"]),
                "current": len(registry["current_lookup"]),
            },
        },
    )
    check("exact-entries-admitted", len(entries) == 60 and exact_entries, {"count": len(entries), "exact": exact_entries})
    check("current-selections", exact_current, {"selected": sum(1 for x in candidate["definitions"] if registry["current_lookup"].get(x["definition_id"]) == f"{x['definition_id']}@{x['version']}"), "expected": 60})
    index_text = INDEX.read_text(encoding="utf-8")
    check(
        "index-projection",
        all(f"`{x['definition_id']}@{x['version']}`" in index_text for x in candidate["definitions"]),
        sha(INDEX),
    )
    check("drift-binds-registry", drift.get("registry_sha256") == sha(REGISTRY) and drift["summary"].get("integrated_lab_model_definitions") == "60-admitted-current", drift.get("registry_sha256"))
    check("downstream-effects-separated", decision["admission_result"] == {"artifact_types_admitted": 0, "canonical_definition_versions": 179, "consumer_activations": 0, "current_definition_identities": 173, "definitions_admitted": 60, "endpoint_pairs_admitted": 0, "relation_kinds_admitted": 0, "result": "complete"}, decision["admission_result"])

    failed = [x for x in checks if x["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-admission-validation/v1", "subject": DECISION_ID,
        "result": "PASS" if not failed else "FAIL", "authority_effect": "evidence-only", "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {"authorization_sha256": sha(ROOT / "authorization.json"), "decision_sha256": sha(ROOT / "decision.json"), "candidate_sha256": sha(CANDIDATE_ROOT / "candidate.json"), "source_validation_sha256": sha(CANDIDATE_ROOT / "receipts/validation.json"), "registry_sha256": sha(REGISTRY), "index_sha256": sha(INDEX), "drift_audit_sha256": sha(DRIFT)},
        "claim_ceiling": "PASS proves exact admission of the 60 Definition versions and registry projections only. It does not admit downstream carriers, relations, qualifiers, ontology records, runtimes, or consumers.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"INTEGRATED_LAB_DEFINITION_ADMISSION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
