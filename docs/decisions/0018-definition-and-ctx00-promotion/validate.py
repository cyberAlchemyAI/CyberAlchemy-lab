#!/usr/bin/env python3
"""Validate the decision-ready Definition and CTX-00 promotion request."""

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
    gate_request_path = ROOT / "admissibility-request.json"
    gate_receipt_path = ROOT / "admissibility-receipt.json"
    gate_request = load(gate_request_path)
    gate_receipt = load(gate_receipt_path)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("request-identity", request["request_id"] == "CAL-REQUEST-0018-DEFINITION-AND-CTX00-PROMOTION" and request["authority_effect"] == "none", {"request_id": request["request_id"], "authority_effect": request["authority_effect"]})
    owner_path = LAB / request["owner_gate"]["binding_path"]
    owners = load(owner_path)
    owner_pairs = {(x["role_id"], x["principal_id"]) for x in owners["role_assignments"]}
    check("owner-gate-current", sha(owner_path) == request["owner_gate"]["binding_sha256"] and (request["owner_gate"]["role_id"], request["owner_gate"]["principal_id"]) in owner_pairs, {"sha256": sha(owner_path), "binding": [request["owner_gate"]["role_id"], request["owner_gate"]["principal_id"]]})
    for label, binding in (("candidate", request["bound_candidate"]), ("pack", request["bound_successor_pack"])):
        path = LAB / binding["path"]
        receipt_path = LAB / binding["validation_path"]
        receipt = load(receipt_path)
        check(f"{label}-current", sha(path) == binding["sha256"], sha(path))
        check(f"{label}-validation-current", sha(receipt_path) == binding["validation_sha256"] and receipt["result"] == "PASS" and receipt["summary"]["total"] == binding["validation_checks"], {"sha256": sha(receipt_path), "result": receipt["result"], "summary": receipt["summary"]})
    candidate = load(LAB / request["bound_candidate"]["path"])
    check("selected-definition-closure", request["selected_definition_ids"] == [x["definition_id"] for x in candidate["definitions"]], request["selected_definition_ids"])
    for label, binding in request["proposed_postimages"].items():
        check(f"postimage-{label}-current", sha(LAB / binding["path"]) == binding["sha256"], sha(LAB / binding["path"]))
    live_path = LAB / request["live_preimage"]["registry_path"]
    check("live-preimage-current", sha(live_path) == request["live_preimage"]["registry_sha256"] and len(load(live_path)["entries"]) == request["live_preimage"]["entry_count"], {"sha256": sha(live_path), "entries": len(load(live_path)["entries"])})
    check("gate-request-bound", gate_request["decisionId"] == request["decision_id"] and request["recommended_option_id"] in [x["optionId"] for x in gate_request["candidates"]], gate_request["decisionId"])
    check("gate-prefilter-pass", gate_receipt["routeOutcome"] == "gate" and request["recommended_option_id"] in gate_receipt["admissibleOptionIds"] and gate_receipt["requestDigest"] == canonical_digest(gate_request), gate_receipt)
    check("no-selection-recorded", request["status"] == "awaiting-definition-owner-selection" and request["authority_effect"] == "none", request["status"])
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(request), str(OUTPUT))
    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-promotion-request-validation/v1", "subject": request["request_id"], "result": result, "decision_gate_result": "BLOCK", "blocker": "exact-definition-owner-selection-required", "authority_effect": "none", "checks": checks, "summary": {"passed": sum(x["result"] == "PASS" for x in checks), "total": len(checks)}, "claim_ceiling": "PASS makes this request ready for human review; it does not select or perform promotion."}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEFINITION_CTX00_PROMOTION_REQUEST_VALIDATION={result}")
    print("DECISION_GATE=BLOCK exact-definition-owner-selection-required")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
