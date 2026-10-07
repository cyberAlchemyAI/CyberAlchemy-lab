#!/usr/bin/env python3
"""Validate the Product duplicate resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
RESOLUTION = LAB / "authority/artifact-types/resolutions/migration-26/v1/product.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    resolution = load(RESOLUTION)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    candidate = resolution["candidate"]
    carrier = resolution["authoritative_carrier"]
    check("authorization-bound", decision["authorization"]["sha256"] == sha(ROOT / "authorization.json") and decision["resolution_record"]["sha256"] == sha(RESOLUTION), authorization["interpreted_scope"])
    check("candidate-exact", sha(LAB / candidate["artifact_path"]) == candidate["artifact_sha256"] and sha(LAB / candidate["schema_path"]) == candidate["schema_sha256"], candidate)
    check("existing-carrier-exact", sha(LAB / carrier["artifact_path"]) == carrier["artifact_sha256"] and sha(LAB / carrier["schema_path"]) == carrier["schema_sha256"], carrier)
    existing_decision = load(LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json")
    admitted = next((item for item in existing_decision["admitted_artifact_types"] if item["artifact_type_ref"] == carrier["artifact_type_ref"]), None)
    check("existing-carrier-admitted", admitted is not None and admitted["decision_overlay_status"] == "admitted-current" and carrier["admission_decision_ref"] == existing_decision["decision_id"], admitted)
    check("no-duplicate-admission", resolution["artifact_types_admitted"] == 0 and decision["result"]["artifact_types_admitted"] == 0 and resolution["queue_state"] == "closed-without-duplicate-admission", resolution["queue_state"])
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact candidate was resolved to an exact already admitted carrier without a duplicate admission.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"PRODUCT_DUPLICATE_RESOLUTION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
