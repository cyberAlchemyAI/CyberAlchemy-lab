#!/usr/bin/env python3
"""Validate the exact context-operational owner admission overlay."""

import hashlib
import importlib.util
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


def renderer():
    path = ROOT / "render-decision.py"
    spec = importlib.util.spec_from_file_location("ctx02_decision_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def main() -> int:
    decision = load(SOURCE)
    gate_request = load(ROOT / decision["admissibility"]["request_ref"])
    gate_receipt = load(ROOT / decision["admissibility"]["receipt_ref"])
    promotion_path = ROOT / decision["promotion_request"]["path"]
    promotion_receipt_path = ROOT / decision["promotion_request"]["validation_path"]
    promotion_receipt = load(promotion_receipt_path)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("decision-identity", decision.get("decision_id") == "CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION" and decision.get("status") == "owner-admitted", {"id": decision.get("decision_id"), "status": decision.get("status")})
    selection = decision["selection"]
    check("exact-owner-selection", selection.get("option_id") == selection.get("selection_token") == "ADMIT-CTX02-OPERATIONAL-OWNERS-V1" and selection.get("selected_by_principal") == "person:<vrondelli>" and "Exact user instruction" in selection.get("selection_source", ""), selection)
    foundation = decision["authority_basis"]
    foundation_path = LAB / foundation["foundation_decision_path"]
    foundation_data = load(foundation_path)
    check("bootstrap-owner-authority-current", sha(foundation_path) == foundation["foundation_decision_sha256"] and foundation_data.get("bootstrap_owner_identity", {}).get("principal_id") == foundation["bootstrap_principal"] and foundation["owner_registry_artifact_type_ref"] in foundation_data.get("admitted_artifact_types", []), sha(foundation_path))
    check("admissibility-current", sha(ROOT / decision["admissibility"]["request_ref"]) == decision["admissibility"]["request_sha256"] and sha(ROOT / decision["admissibility"]["receipt_ref"]) == decision["admissibility"]["receipt_sha256"] and canonical_digest(gate_request) == decision["admissibility"]["request_digest"] == gate_receipt.get("requestDigest"), decision["admissibility"])
    check("selected-option-admissible", gate_receipt.get("routeOutcome") == "gate" and selection["option_id"] in gate_receipt.get("admissibleOptionIds", []) and decision["admissibility"]["selected_option_admissible"] is True, gate_receipt)
    promotion = decision["promotion_request"]
    check("promotion-request-current-and-pass", sha(promotion_path) == promotion["sha256"] and sha(promotion_receipt_path) == promotion["validation_sha256"] and promotion_receipt.get("result") == "PASS" and promotion_receipt.get("summary", {}).get("total") == promotion["validation_checks"], {"request": sha(promotion_path), "receipt": sha(promotion_receipt_path), "summary": promotion_receipt.get("summary")})
    successor = decision["accepted_successor_registry"]
    successor_path = LAB / successor["path"]
    successor_human = LAB / successor["human_projection_path"]
    successor_receipt_path = LAB / successor["validation_receipt_path"]
    successor_data, successor_receipt = load(successor_path), load(successor_receipt_path)
    check("successor-current-and-pass", sha(successor_path) == successor["sha256"] and sha(successor_human) == successor["human_projection_sha256"] and sha(successor_receipt_path) == successor["validation_receipt_sha256"] and successor_receipt.get("result") == "PASS" and successor_receipt.get("summary", {}).get("total") == successor["validation_checks"], {"machine": sha(successor_path), "human": sha(successor_human), "receipt": sha(successor_receipt_path)})
    predecessor_path = LAB / successor["predecessor_path"]
    predecessor_data = load(predecessor_path)
    check("predecessor-preserved", sha(predecessor_path) == successor["predecessor_sha256"], sha(predecessor_path))
    ctx01 = decision["ctx01_prerequisite"]
    ctx01_path, ctx01_receipt_path = LAB / ctx01["decision_path"], LAB / ctx01["validation_path"]
    check("ctx01-prerequisite-current", sha(ctx01_path) == ctx01["decision_sha256"] and load(ctx01_path).get("status") == "owner-admitted" and sha(ctx01_receipt_path) == ctx01["validation_sha256"] and load(ctx01_receipt_path).get("result") == "PASS", {"decision": sha(ctx01_path), "receipt": sha(ctx01_receipt_path)})
    predecessor_roles = {item["role_id"] for item in predecessor_data["role_assignments"]}
    successor_roles = {item["role_id"] for item in successor_data["role_assignments"]}
    admitted_roles = {item["role_id"] for item in decision["admitted_operational_roles"]}
    check("exact-role-delta-admitted", predecessor_roles == set(decision["preserved_foundation_role_ids"]) and successor_roles - predecessor_roles == admitted_roles and len(admitted_roles) == 10, {"preserved": sorted(predecessor_roles), "admitted": sorted(admitted_roles)})
    check("principal-and-separation-exact", all(item["principal_id"] == "person:<vrondelli>" for item in decision["admitted_operational_roles"]) and all(item["principal_id"] == "person:<vrondelli>" and item["decision_separation"] == "required" for item in successor_data["role_assignments"]), "all 15 assignments resolve to one principal with separate decisions")
    check("candidate-bytes-remain-predecision", successor_data.get("status") == "candidate-unadmitted" and successor_data.get("authority_effect") == "none", {"status": successor_data.get("status"), "effect": successor_data.get("authority_effect")})
    result_data = decision["admission_result"]
    check("admission-cardinality", result_data == {"result": "complete-context-operational-owner-admission", "foundation_roles_preserved": 5, "operational_roles_admitted": 10, "current_role_count": 15, "context_instances_created": 0}, result_data)
    check("projection-determinism-and-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == renderer()(decision), str(OUTPUT))
    check("successor-effects-excluded", all(term in decision.get("claim_ceiling", "") for term in ("only ten exact operational role bindings", "does not create", "migration", "stable release")) and any("No Bounded Context" in item for item in decision["excluded_effects"]), decision.get("claim_ceiling"))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-owner-registry-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-owner-registry-decision-overlay",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "admission_state": "complete-context-operational-owner-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "context-and-language-candidate-authorship-requires-route-reentry",
        "claim_ceiling": decision["claim_ceiling"]
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX02_OWNER_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
