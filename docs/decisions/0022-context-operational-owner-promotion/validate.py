#!/usr/bin/env python3
"""Validate the decision-ready context-operational owner promotion request."""

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main() -> int:
    request = load(SOURCE)
    gate_request = load(ROOT / "admissibility-request.json")
    gate_receipt = load(ROOT / "admissibility-receipt.json")
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("request-identity", request.get("request_id") == "CAL-REQUEST-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION" and request.get("authority_effect") == "none", {"id": request.get("request_id"), "effect": request.get("authority_effect")})
    owner_decision_path = LAB / request["owner_gate"]["binding_path"]
    owner_decision = load(owner_decision_path)
    check("bootstrap-owner-gate-current", sha(owner_decision_path) == request["owner_gate"]["binding_sha256"] and owner_decision.get("bootstrap_owner_identity", {}).get("principal_id") == request["owner_gate"]["principal_id"] and "cal.artifact-type.owner-registry/v1" in owner_decision.get("admitted_artifact_types", []), sha(owner_decision_path))
    candidate_binding = request["bound_candidate"]
    candidate_path, candidate_receipt_path = LAB / candidate_binding["path"], LAB / candidate_binding["validation_path"]
    candidate, candidate_receipt = load(candidate_path), load(candidate_receipt_path)
    check("candidate-current", sha(candidate_path) == candidate_binding["sha256"] and sha(LAB / candidate_binding["human_path"]) == candidate_binding["human_sha256"], {"machine": sha(candidate_path), "human": sha(LAB / candidate_binding["human_path"])})
    check("candidate-validation-current", sha(candidate_receipt_path) == candidate_binding["validation_sha256"] and candidate_receipt.get("result") == "PASS" and candidate_receipt.get("summary", {}).get("total") == candidate_binding["validation_checks"], {"sha256": sha(candidate_receipt_path), "summary": candidate_receipt.get("summary")})
    predecessor = request["admitted_predecessor"]
    predecessor_path = LAB / predecessor["path"]
    check("predecessor-current", sha(predecessor_path) == predecessor["sha256"] and len(load(predecessor_path)["role_assignments"]) == predecessor["role_count"], sha(predecessor_path))
    ctx01 = request["ctx01_prerequisite"]
    ctx01_path, ctx01_receipt_path = LAB / ctx01["path"], LAB / ctx01["validation_path"]
    check("ctx01-admission-current", sha(ctx01_path) == ctx01["sha256"] and load(ctx01_path).get("status") == "owner-admitted" and sha(ctx01_receipt_path) == ctx01["validation_sha256"] and load(ctx01_receipt_path).get("result") == "PASS", {"decision": sha(ctx01_path), "receipt": sha(ctx01_receipt_path)})
    predecessor_roles = {item["role_id"] for item in load(predecessor_path)["role_assignments"]}
    candidate_roles = {item["role_id"] for item in candidate["role_assignments"]}
    check("ten-role-postimage-closure", candidate_roles - predecessor_roles == set(request["proposed_role_ids"]) and len(request["proposed_role_ids"]) == len(set(request["proposed_role_ids"])) == 10, sorted(candidate_roles - predecessor_roles))
    check("gate-request-bound", gate_request.get("decisionId") == request["decision_id"] and request["recommended_option_id"] in [item["optionId"] for item in gate_request["candidates"]], gate_request.get("decisionId"))
    check("gate-prefilter-pass", gate_receipt.get("routeOutcome") == "gate" and set(gate_receipt.get("admissibleOptionIds", [])) == {item["optionId"] for item in gate_request["candidates"]} and gate_receipt.get("requestDigest") == canonical_digest(gate_request), gate_receipt)
    check("no-selection-recorded", request.get("status") == "awaiting-bootstrap-owner-selection" and request.get("authority_effect") == "none", request.get("status"))
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(request), str(OUTPUT))
    check("successor-effects-separated", "records no selection" in request.get("claim_ceiling", "") and any("Does not admit any context" in item for item in request["non_effects"]) and "Context Map pattern selection separate" in request["next_step_if_admitted"], {"claim": request.get("claim_ceiling"), "next": request["next_step_if_admitted"]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-owner-registry-promotion-request-validation/v1", "subject": request["request_id"], "result": result, "decision_gate_result": "BLOCK", "blocker": "exact-bootstrap-owner-selection-required", "authority_effect": "none", "checks": checks, "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)}, "claim_ceiling": "PASS makes the exact owner-registry successor ready for human selection; it does not admit or activate any role."}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX02_OWNER_PROMOTION_REQUEST_VALIDATION={result}")
    print("DECISION_GATE=BLOCK exact-bootstrap-owner-selection-required")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
