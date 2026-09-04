#!/usr/bin/env python3
"""Validate the immutable successor CTX-00 Definition Pack."""

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


def main() -> int:
    pack = load(SOURCE)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("pack-identity", pack["pack_id"] == "DEFINE-PACK-CAL-CONTEXT-MIGRATION-METAMODEL-004" and pack["authority_effect"] == "none", {"pack_id": pack["pack_id"], "authority_effect": pack["authority_effect"]})
    predecessor = pack["predecessor"]
    predecessor_path = LAB / predecessor["path"]
    predecessor_receipt_path = LAB / predecessor["validation_path"]
    check("predecessor-preserved", sha(predecessor_path) == predecessor["sha256"] and sha(predecessor_receipt_path) == predecessor["validation_sha256"], {"pack": sha(predecessor_path), "receipt": sha(predecessor_receipt_path)})
    source_decision = pack["source_admission"]
    source_decision_path = LAB / source_decision["path"]
    source_data = load(source_decision_path)
    check("source-admission-current", sha(source_decision_path) == source_decision["sha256"] and source_data["status"] == "owner-admitted" and len(source_data["admitted_source_selections"]) == 7, {"sha256": sha(source_decision_path), "status": source_data["status"], "selections": len(source_data["admitted_source_selections"])})
    candidate = pack["candidate_set"]
    candidate_path = LAB / candidate["path"]
    candidate_receipt_path = LAB / candidate["validation_path"]
    candidate_data = load(candidate_path)
    candidate_receipt = load(candidate_receipt_path)
    check("candidate-set-current", sha(candidate_path) == candidate["sha256"] and candidate_data["candidate_id"] == candidate["candidate_id"], sha(candidate_path))
    check("candidate-evidence-current", sha(candidate_receipt_path) == candidate["validation_sha256"] and candidate_receipt["result"] == "PASS" and candidate_receipt["summary"]["total"] == candidate["validation_checks"], {"sha256": sha(candidate_receipt_path), "result": candidate_receipt["result"], "summary": candidate_receipt["summary"]})
    check("promotion-eligibility", candidate_receipt["promotion_eligibility"] == "eligible-for-exact-owner-decision" and candidate_receipt["evaluation"]["DEF-EVAL-07-DECISION"] == "NOT_EVALUABLE", candidate_receipt["evaluation"])
    check("definition-closure", len(pack["definition_ids"]) == 8 and set(pack["definition_ids"]) == {x["definition_id"] for x in candidate_data["definitions"]}, pack["definition_ids"])
    check("foundational-definition-first", pack["definition_ids"][0] == "cal.definition.definition", pack["definition_ids"][0])
    check("resolved-blockers-explicit", len(pack["resolved_predecessor_blockers"]) == 6, pack["resolved_predecessor_blockers"])
    check("remaining-gate-explicit", "definition owner" in pack["remaining_authority_gate"] and all(word in pack["remaining_authority_gate"] for word in ("admit", "revise", "defer", "stop")), pack["remaining_authority_gate"])
    check("successor-work-bounded", len(pack["successor_work_after_admission"]) == 5, pack["successor_work_after_admission"])
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(pack), str(OUTPUT))
    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-definition-pack-validation/v1", "subject": pack["pack_id"], "result": result, "authority_effect": "none", "checks": checks, "summary": {"passed": sum(x["result"] == "PASS" for x in checks), "total": len(checks)}, "claim_ceiling": "This receipt validates successor-pack closure and exact bound evidence only; it does not admit definitions or authorize successor construction."}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX00_SUCCESSOR_PACK_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
