#!/usr/bin/env python3
"""Prove common hostile registry mutations fail the admission contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_satisfies_admission(registry: dict, decision: dict) -> bool:
    admitted = {item["definition_id"]: item for item in decision["admitted_definitions"]}
    entries = registry.get("entries", [])
    rows = {item.get("definition_id"): item for item in entries}
    if len(entries) != len(rows) or set(rows) != set(admitted):
        return False
    if registry.get("status") != "owner-admitted" or registry.get("authority_effect") != decision["authority_effect"]:
        return False
    if registry.get("admission_decision_ref") != decision["decision_id"]:
        return False
    for definition_id, expected in admitted.items():
        row = rows[definition_id]
        if any(row.get(key) != expected[key] for key in ("version", "path", "sha256")):
            return False
        if row.get("lifecycle_state") != "admitted" or row.get("admission_decision_ref") != decision["decision_id"]:
            return False
    return True


def main() -> int:
    decision = load(LAB / "docs/decisions/0018-definition-and-ctx00-promotion/decision.json")
    registry = load(LAB / "authority/definitions/registry.json")
    cases = [registry_satisfies_admission(registry, decision)]

    missing = copy.deepcopy(registry)
    missing["entries"].pop()
    cases.append(not registry_satisfies_admission(missing, decision))

    changed_digest = copy.deepcopy(registry)
    changed_digest["entries"][0]["sha256"] = "0" * 64
    cases.append(not registry_satisfies_admission(changed_digest, decision))

    non_admitted = copy.deepcopy(registry)
    non_admitted["entries"][0]["lifecycle_state"] = "candidate"
    cases.append(not registry_satisfies_admission(non_admitted, decision))

    wrong_decision = copy.deepcopy(registry)
    wrong_decision["admission_decision_ref"] = "CAL-DECISION-WRONG"
    cases.append(not registry_satisfies_admission(wrong_decision, decision))

    status = "PASS" if len(cases) == 5 and all(cases) else "FAIL"
    print(f"CTX00_ADMISSION_HOSTILE={status}")
    print(f"CHECKS={sum(cases)}/{len(cases)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
