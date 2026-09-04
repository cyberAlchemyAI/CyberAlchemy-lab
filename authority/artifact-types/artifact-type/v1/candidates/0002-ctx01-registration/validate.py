#!/usr/bin/env python3
"""Validate the Artifact Type/v1 CTX01 registration successor candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parents[1]
LAB = ROOT.parents[5]
PREDECESSOR = V1_ROOT / "artifact.json"
SCHEMA = V1_ROOT / "schema.json"
PACK = LAB / "docs/artifact-type-packs/0001-ctx01/artifact-type-pack.json"
PACK_RECEIPT = LAB / "docs/artifact-type-packs/0001-ctx01/receipts/validation.json"
CTX01_RECEIPT = LAB / "tests/conformance/ctx01/receipts/last-run.json"
OWNER_REGISTRY = LAB / "authority/owners/foundation-01/v1/owners.json"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
FOUNDATION_RENDERER = LAB / "authority/foundation/v1/render.py"
RECEIPT = ROOT / "receipts/validation.json"

EXPECTED = {
    PREDECESSOR: "143577e9efa793cdf7447e38f5e25013e3006df3b21e9aa3aec4b30d10c19e56",
    PACK: "cc61afd091a549108a10aa744986acaf1409403926f23a049b0802c230a10d35",
    PACK_RECEIPT: "9ffbd190dfb1f0ccd49cdf2d2b74a2ace123c21d254c25cd1749b0567eedf694",
    CTX01_RECEIPT: "8d7b81c231641763b23b091bbb37292db1bd9e613e1820c9cfd77e3c2de75e3a",
    OWNER_REGISTRY: "bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d",
    DEFINITION_REGISTRY: "78284ea33543aae5d0cfecb7d5090aa8702388051486eec69ffc368c656d5e8f",
    FOUNDATION_RENDERER: "ae0f0561fd272121382ae8e077908f735aa31a9686bb2f87057015a5b91b4ac2",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    artifact, predecessor, schema = load(SOURCE), load(PREDECESSOR), load(SCHEMA)
    pack, pack_receipt, suite_receipt = load(PACK), load(PACK_RECEIPT), load(CTX01_RECEIPT)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(schema).iter_errors(artifact)]
    check("root-schema-valid", not schema_errors, schema_errors)
    check("candidate-no-authority", artifact.get("version") == "1.0.0-candidate.2" and artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none", {key: artifact.get(key) for key in ("version", "status", "authority_effect")})
    check("bound-inputs-current", all(sha(path) == expected for path, expected in EXPECTED.items()), {str(path.relative_to(LAB)): sha(path) for path in EXPECTED})
    old = {item["artifact_type_ref"]: item for item in predecessor["registered_types"]}
    new = {item["artifact_type_ref"]: item for item in artifact["registered_types"]}
    check("predecessor-registration-preservation", len(old) == 9 and all(new.get(key) == value for key, value in old.items()), sorted(old))
    expected_new = {item["artifact_type_ref"] for item in pack["artifact_types"]}
    check("seven-new-registration-closure", len(new) == 16 and set(new) - set(old) == expected_new, sorted(set(new) - set(old)))
    check("registration-axes-unique", len(new) == len(artifact["registered_types"]) and len({item["semantic_kind"] for item in artifact["registered_types"]}) == 16, {"refs": len(new), "kinds": len({item["semantic_kind"] for item in artifact["registered_types"]})})
    registrations = []
    for item in pack["artifact_types"]:
        registered = new.get(item["artifact_type_ref"], {})
        registrations.append({"ref": item["artifact_type_ref"], "path": registered.get("schema_path") == item["schema_path"], "digest": registered.get("schema_sha256") == item["schema_sha256"] == sha(LAB / item["schema_path"]), "purpose": bool(registered.get("distinct_validation_purpose"))})
    check("ctx01-registration-bindings-current", all(all(value for key, value in row.items() if key != "ref") for row in registrations), registrations)
    check("aggregate-evidence-pass", pack_receipt.get("result") == "PASS" and pack_receipt.get("summary") == {"failed": 0, "passed": 23, "total": 23} and suite_receipt.get("result") == "PASS" and suite_receipt.get("summary") == {"passed": 8, "total": 8}, {"pack": pack_receipt.get("summary"), "suite": suite_receipt.get("summary")})
    owners = load(OWNER_REGISTRY)["role_assignments"]
    check("artifact-type-owner-resolves", any(item.get("role_id") == "artifact-type-owner" and item.get("principal_id") == "person:<vrondelli>" for item in owners), "role:artifact-type-owner -> person:<vrondelli>")
    definition_ids = {item["definition_id"] for item in load(DEFINITION_REGISTRY)["entries"]}
    check("definition-closure-current", {item["definition_id"] for item in pack["artifact_types"]} <= definition_ids, sorted(definition_ids))
    rendered_a, rendered_b = render(artifact), render(artifact)
    check("projection-determinism-and-parity", rendered_a == rendered_b and OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a, hashlib.sha256(rendered_a.encode()).hexdigest())
    check("no-context-instances", all(not item["schema_path"].startswith("contexts/") for item in artifact["registered_types"]), [item["schema_path"] for item in artifact["registered_types"]])
    ceiling = artifact.get("claim_ceiling", "")
    check("separation-ceiling-explicit", all(term in ceiling for term in ("does not admit", "operational owners", "create contexts", "stable release")), ceiling)

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-registration-validation/v1",
        "subject": "cal.artifact-type.artifact-type/v1@1.0.0-candidate.2",
        "candidate_epoch": "0002-ctx01-registration",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "promotion_eligibility": "eligible-for-exact-artifact-type-owner-decision" if result == "PASS" else "blocked",
        "materials": {"artifact_json_sha256": sha(SOURCE), "artifact_md_sha256": sha(OUTPUT) if OUTPUT.is_file() else None, "predecessor_artifact_json_sha256": sha(PREDECESSOR), "ctx01_pack_sha256": sha(PACK), "ctx01_pack_receipt_sha256": sha(PACK_RECEIPT)},
        "claim_ceiling": "PASS proves the exact successor registration candidate and evidence closure only. It does not admit the successor or any CTX01 artifact type."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_ARTIFACT_TYPE_REGISTRATION_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
