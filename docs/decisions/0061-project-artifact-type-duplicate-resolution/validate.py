#!/usr/bin/env python3
"""Validate the Project duplicate resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
RESOLUTION = LAB / "authority/artifact-types/resolutions/migration-26/v1/project.json"
EXISTING_DECISION = LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json"


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
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    candidate = resolution["candidate"]
    carrier = resolution["authoritative_carrier"]
    definition = resolution["semantic_definition"]
    check(
        "authorization-bound",
        decision["authorization"]["sha256"] == sha(ROOT / "authorization.json")
        and decision["resolution_record"]["sha256"] == sha(RESOLUTION),
        authorization["interpreted_scope"],
    )
    check(
        "candidate-exact",
        sha(LAB / candidate["artifact_path"]) == candidate["artifact_sha256"]
        and sha(LAB / candidate["schema_path"]) == candidate["schema_sha256"],
        candidate,
    )
    check(
        "existing-carrier-exact",
        sha(LAB / carrier["artifact_path"]) == carrier["artifact_sha256"]
        and sha(LAB / carrier["schema_path"]) == carrier["schema_sha256"],
        carrier,
    )
    existing_decision = load(EXISTING_DECISION)
    admitted = next(
        (item for item in existing_decision["admitted_artifact_types"] if item["artifact_type_ref"] == carrier["artifact_type_ref"]),
        None,
    )
    check(
        "existing-carrier-admitted",
        admitted is not None
        and admitted["decision_overlay_status"] == "admitted-current"
        and carrier["admission_decision_ref"] == existing_decision["decision_id"],
        admitted,
    )
    candidate_artifact = load(LAB / candidate["artifact_path"])
    carrier_artifact = load(LAB / carrier["artifact_path"])
    definition_ref = definition["definition_ref"]
    check(
        "semantic-overlap-exact",
        definition["sha256"] == sha(LAB / definition["path"])
        and candidate_artifact["semantic_definition_refs"] == [definition_ref]
        and definition_ref in carrier_artifact["semantic_definition_refs"],
        {
            "definition_ref": definition_ref,
            "candidate_refs": candidate_artifact["semantic_definition_refs"],
            "carrier_refs": carrier_artifact["semantic_definition_refs"],
        },
    )
    check(
        "residue-preserved",
        len(resolution["typed_residue"]) == 1
        and resolution["typed_residue"][0]["residue_id"] == "PROJECT-RESOLUTION-R1"
        and "does not establish complete field-level conformance" in resolution["typed_residue"][0]["consequence"],
        resolution["typed_residue"],
    )
    check(
        "no-duplicate-admission",
        resolution["artifact_types_admitted"] == 0
        and decision["result"]["artifact_types_admitted"] == 0
        and resolution["queue_state"] == "closed-without-duplicate-admission",
        resolution["queue_state"],
    )
    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-validation/v1",
        "subject": decision["decision_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "validation-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves the exact migration candidate was resolved to an exact already admitted Project Identity carrier without duplicate admission, while preserving the identified Definition coverage residue.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"PROJECT_DUPLICATE_RESOLUTION={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
