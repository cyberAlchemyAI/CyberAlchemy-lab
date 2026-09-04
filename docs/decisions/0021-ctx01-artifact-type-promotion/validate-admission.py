#!/usr/bin/env python3
"""Validate the exact CTX01 artifact-type admission overlay."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"
RECEIPT = ROOT / "receipts/admission-validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_renderer():
    import importlib.util
    path = ROOT / "render-decision.py"
    spec = importlib.util.spec_from_file_location("ctx01_decision_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def main() -> int:
    decision = load(SOURCE)
    gate_request = load(ROOT / decision["admissibility"]["request_ref"])
    gate_receipt = load(ROOT / decision["admissibility"]["receipt_ref"])
    promotion = load(ROOT / decision["promotion_request"]["path"])
    promotion_receipt = load(ROOT / decision["promotion_request"]["validation_path"])
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("decision-identity", decision.get("decision_id") == "CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION" and decision.get("status") == "owner-admitted", {"id": decision.get("decision_id"), "status": decision.get("status")})
    selection = decision.get("selection", {})
    check("exact-owner-selection", selection.get("option_id") == selection.get("selection_token") == "ADMIT-CTX01-ARTIFACT-TYPES-V1" and selection.get("selected_role") == "artifact-type-owner" and selection.get("selected_by_principal") == "person:<vrondelli>", selection)
    owner_path = LAB / decision["authority_basis"]["owner_registry_path"]
    owners = load(owner_path)["role_assignments"]
    check("owner-authority-current", sha(owner_path) == decision["authority_basis"]["owner_registry_sha256"] and any(item.get("role_id") == "artifact-type-owner" and item.get("principal_id") == "person:<vrondelli>" for item in owners), sha(owner_path))
    check("admissibility-inputs-current", sha(ROOT / decision["admissibility"]["request_ref"]) == decision["admissibility"]["request_sha256"] and sha(ROOT / decision["admissibility"]["receipt_ref"]) == decision["admissibility"]["receipt_sha256"] and canonical_digest(gate_request) == decision["admissibility"]["request_digest"] == gate_receipt.get("requestDigest"), decision["admissibility"])
    check("selected-option-admissible", gate_receipt.get("routeOutcome") == "gate" and selection.get("option_id") in gate_receipt.get("admissibleOptionIds", []) and decision["admissibility"]["selected_option_admissible"] is True, gate_receipt)
    check("promotion-request-current-and-pass", sha(ROOT / decision["promotion_request"]["path"]) == decision["promotion_request"]["sha256"] and sha(ROOT / decision["promotion_request"]["validation_path"]) == decision["promotion_request"]["validation_sha256"] and promotion_receipt.get("result") == "PASS" and promotion_receipt.get("summary", {}).get("total") == 14, {"request": sha(ROOT / decision["promotion_request"]["path"]), "receipt": sha(ROOT / decision["promotion_request"]["validation_path"]), "summary": promotion_receipt.get("summary")})
    successor = decision["accepted_successor_registration"]
    successor_path = LAB / successor["path"]
    successor_receipt_path = LAB / successor["validation_receipt_path"]
    successor_receipt = load(successor_receipt_path)
    check("successor-current-and-pass", sha(successor_path) == successor["sha256"] and sha(successor_receipt_path) == successor["validation_receipt_sha256"] and successor_receipt.get("result") == "PASS" and successor_receipt.get("summary", {}).get("total") == 13, {"artifact": sha(successor_path), "receipt": sha(successor_receipt_path), "summary": successor_receipt.get("summary")})
    check("predecessor-preserved", sha(LAB / successor["predecessor_path"]) == successor["predecessor_sha256"], sha(LAB / successor["predecessor_path"]))
    evidence = decision["evidence_basis"]
    pack_path, pack_receipt_path = LAB / evidence["pack_path"], LAB / evidence["validation_path"]
    suite_path = LAB / evidence["conformance_path"]
    check("aggregate-evidence-current", sha(pack_path) == evidence["pack_sha256"] and sha(pack_receipt_path) == evidence["validation_sha256"] and load(pack_receipt_path).get("result") == "PASS" and sha(suite_path) == evidence["conformance_sha256"] and load(suite_path).get("result") == "PASS", {"pack": sha(pack_path), "pack_receipt": sha(pack_receipt_path), "suite": sha(suite_path)})
    pack = load(pack_path)
    admitted = decision["admitted_artifact_types"]
    check("exact-seven-type-set", [item["artifact_type_ref"] for item in admitted] == [item["artifact_type_ref"] for item in pack["artifact_types"]] and len(admitted) == 7, [item["artifact_type_ref"] for item in admitted])
    material_results = []
    for item in admitted:
        material_results.append({"ref": item["artifact_type_ref"], "artifact": sha(LAB / item["artifact_path"]) == item["artifact_sha256"], "schema": sha(LAB / item["schema_path"]) == item["schema_sha256"]})
    check("admitted-materials-current", all(row["artifact"] and row["schema"] for row in material_results), material_results)
    registered = {item["artifact_type_ref"] for item in load(successor_path)["registered_types"]}
    check("admitted-types-registered-by-successor", {item["artifact_type_ref"] for item in admitted} <= registered and len(registered) == 16, sorted(registered))
    check("candidate-bytes-preserved", all(load(LAB / item["artifact_path"]).get("status") == "candidate-unadmitted" and load(LAB / item["artifact_path"]).get("authority_effect") == "none" for item in admitted), "authority supplied by decision overlay, not candidate mutation")
    check("machine-canonical-human-generated", decision.get("source_direction", {}).get("canonical") == "decision.json" and decision.get("source_direction", {}).get("human_projection") == "DECISION.md" and decision.get("source_direction", {}).get("projection_policy") == "generated-only" and OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == load_renderer()(decision), decision.get("source_direction"))
    check("operational-effects-excluded", decision.get("admission_result", {}).get("operational_owner_bindings_created") == 0 and decision.get("admission_result", {}).get("context_instances_created") == 0 and all(term in decision.get("claim_ceiling", "") for term in ("does not admit tooling", "bind operational owners", "create context-metamodel instances", "stable release")), decision.get("admission_result"))
    check("definition-authority-unchanged", sha(LAB / "authority/definitions/registry.json") == "78284ea33543aae5d0cfecb7d5090aa8702388051486eec69ffc368c656d5e8f", sha(LAB / "authority/definitions/registry.json"))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-artifact-type-admission-validation/v1", "subject": decision["decision_id"], "result": result, "authority_effect": "evidence-for-exact-owner-decision-overlay", "checks": checks, "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)}, "admission_state": "complete-ctx01-artifact-type-admission" if result == "PASS" else "not_evaluable", "next_gate": "operational-owner-binding-not-authorized-by-this-decision", "claim_ceiling": decision["claim_ceiling"]}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_ARTIFACT_TYPE_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
