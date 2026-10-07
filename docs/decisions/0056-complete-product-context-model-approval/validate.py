#!/usr/bin/env python3
"""Validate the complete Product context model approval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
SELECTION = LAB / "authority/product-context/selected/v1/selection.json"


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
    selection = load(SELECTION)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    for key in ["model", "example", "validation_receipt"]:
        item = authorization[key]
        check(f"{key}-exact", sha(LAB / item["path"]) == item["sha256"], item)
    check("approval-bound", decision["authorization"]["sha256"] == sha(ROOT / "authorization.json") and decision["selection_record"]["sha256"] == sha(SELECTION), decision["decision_id"])
    check("selection-bound", selection["model"] == authorization["model"] and selection["example"] == authorization["example"] and selection["validation_receipt"] == authorization["validation_receipt"], selection["model_id"])
    check("separate-admission-boundary", selection["separate_decision_required_per_item"] is True and decision["result"]["artifact_types_admitted"] == 0 and decision["result"]["consumer_activations"] == 0, decision["result"])
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-product-context-approval-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves exact model selection and the separate admission boundary; it does not admit or activate any component.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"PRODUCT_CONTEXT_MODEL_APPROVAL={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
