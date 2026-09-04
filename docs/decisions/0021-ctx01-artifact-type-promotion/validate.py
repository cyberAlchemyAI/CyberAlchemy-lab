#!/usr/bin/env python3
"""Validate the decision-ready CTX01 artifact-type promotion request."""

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

    check("request-identity", request.get("request_id") == "CAL-REQUEST-0021-CTX01-ARTIFACT-TYPE-PROMOTION" and request.get("authority_effect") == "none", {"request_id": request.get("request_id"), "authority_effect": request.get("authority_effect")})
    owner_path = LAB / request["owner_gate"]["binding_path"]
    owners = load(owner_path)["role_assignments"]
    check("owner-gate-current", sha(owner_path) == request["owner_gate"]["binding_sha256"] and any(item.get("role_id") == request["owner_gate"]["role_id"] and item.get("principal_id") == request["owner_gate"]["principal_id"] for item in owners), sha(owner_path))
    for label, binding in (("successor", request["bound_successor_registration"]), ("pack", request["bound_ctx01_pack"])):
        path, receipt_path = LAB / binding["path"], LAB / binding["validation_path"]
        receipt = load(receipt_path)
        check(f"{label}-current", sha(path) == binding["sha256"], sha(path))
        check(f"{label}-validation-current", sha(receipt_path) == binding["validation_sha256"] and receipt.get("result") == "PASS" and receipt.get("summary", {}).get("total") == binding["validation_checks"], {"sha256": sha(receipt_path), "summary": receipt.get("summary")})
    conformance = request["bound_conformance"]
    conformance_path = LAB / conformance["path"]
    conformance_receipt = load(conformance_path)
    check("conformance-current", sha(conformance_path) == conformance["sha256"] and conformance_receipt.get("result") == "PASS" and conformance_receipt.get("summary", {}).get("total") == conformance["tests"], {"sha256": sha(conformance_path), "summary": conformance_receipt.get("summary")})
    stale_predecessors = [item["decision_id"] for item in request["admitted_predecessors"] if sha(LAB / item["path"]) != item["sha256"] or load(LAB / item["path"]).get("status") != "owner-admitted"]
    check("admitted-predecessors-current", not stale_predecessors, stale_predecessors)
    pack_refs = [item["artifact_type_ref"] for item in load(LAB / request["bound_ctx01_pack"]["path"])["artifact_types"]]
    check("seven-type-closure", request["artifact_type_refs"] == pack_refs and len(pack_refs) == 7, pack_refs)
    check("gate-request-bound", gate_request.get("decisionId") == request["decision_id"] and request["recommended_option_id"] in [item["optionId"] for item in gate_request["candidates"]], gate_request.get("decisionId"))
    check("gate-prefilter-pass", gate_receipt.get("routeOutcome") == "gate" and request["recommended_option_id"] in gate_receipt.get("admissibleOptionIds", []) and gate_receipt.get("requestDigest") == canonical_digest(gate_request), gate_receipt)
    check("no-selection-recorded", request.get("status") == "awaiting-artifact-type-owner-selection" and request.get("authority_effect") == "none", request.get("status"))
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(request), str(OUTPUT))
    check("separation-boundary", "operational owners" in " ".join(request["non_effects"]) and "context instance" in request["next_step_if_admitted"], {"non_effects": request["non_effects"], "next": request["next_step_if_admitted"]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-promotion-request-validation/v1",
        "subject": request["request_id"],
        "result": result,
        "decision_gate_result": "BLOCK",
        "blocker": "exact-artifact-type-owner-selection-required",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "claim_ceiling": "PASS makes this request ready for owner selection; it does not select or perform admission."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_ARTIFACT_TYPE_PROMOTION_REQUEST_VALIDATION={result}")
    print("DECISION_GATE=BLOCK exact-artifact-type-owner-selection-required")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
