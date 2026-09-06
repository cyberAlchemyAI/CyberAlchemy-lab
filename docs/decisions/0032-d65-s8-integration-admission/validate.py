#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
DECISION = HERE / "decision.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    decision = load(DECISION)
    schema = load(SCHEMA)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = [error.message for error in Draft202012Validator(schema).iter_errors(decision)]
    record("decision-schema", not errors, {"errors": errors})

    source = decision.get("decision_source", {})
    ordered = decision.get("ordered_decisions", [])
    normalized = source.get("normalized_order", [])
    record(
        "explicit-ordered-owner-selection",
        source.get("kind") == "explicit-user-selection"
        and source.get("verbatim") == "1 then 2"
        and normalized == ["D65S8ADM-1", "D65CUTPREP-1"]
        and [item.get("option_id") for item in ordered] == normalized
        and [item.get("sequence") for item in ordered] == [1, 2],
        {"source": source, "ordered_option_ids": [item.get("option_id") for item in ordered]},
    )

    admissibility_failures: list[str] = []
    admissibility_detail: dict[str, Any] = {}
    expected_options = {
        "admission": {"D65S8ADM-1", "D65S8ADM-2", "D65S8ADM-3", "D65S8ADM-4"},
        "successor_preparation": {"D65CUTPREP-1", "D65CUTPREP-2", "D65CUTPREP-3"},
    }
    for name, expected in expected_options.items():
        refs = decision.get("admissibility", {}).get(name, {})
        request_path = LAB / str(refs.get("request_path", ""))
        receipt_path = LAB / str(refs.get("receipt_path", ""))
        if not request_path.is_file() or digest(request_path) != refs.get("request_sha256"):
            admissibility_failures.append(f"{name}-request-digest-mismatch")
            continue
        if not receipt_path.is_file() or digest(receipt_path) != refs.get("receipt_sha256"):
            admissibility_failures.append(f"{name}-receipt-digest-mismatch")
            continue
        receipt = load(receipt_path)
        request = load(request_path)
        canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        expected_request_digest = hashlib.sha256(canonical).hexdigest()
        valid = (
            receipt.get("requestDigest") == expected_request_digest
            and receipt.get("routeOutcome") == "gate"
            and receipt.get("decisionGateRequired") is True
            and set(receipt.get("admissibleOptionIds", [])) == expected
            and set(receipt.get("presentedOptionIds", [])) == expected
            and refs.get("selected_option_id") in expected
        )
        if not valid:
            admissibility_failures.append(f"{name}-receipt-content-mismatch")
        admissibility_detail[name] = {
            "request_digest": expected_request_digest,
            "route_outcome": receipt.get("routeOutcome"),
            "selected_option_id": refs.get("selected_option_id"),
        }
    record("option-admissibility", not admissibility_failures, {"failures": admissibility_failures, **admissibility_detail})

    refs = decision.get("candidate_refs", {})
    candidate_failures: list[str] = []
    artifacts: dict[str, Path] = {}
    for name in ("manifest", "verdict", "validator", "readme"):
        path = LAB / str(refs.get(f"{name}_path", ""))
        artifacts[name] = path
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            candidate_failures.append(f"{name}-digest-mismatch")

    manifest = load(artifacts["manifest"])
    verdict = load(artifacts["verdict"])
    selected_dependency_failures: list[str] = []
    for item in manifest.get("dependencies", []) + manifest.get("d65_s7_postimages", []):
        path = LAB / str(item.get("path", ""))
        if not path.is_file() or digest(path) != item.get("sha256"):
            selected_dependency_failures.append(str(item.get("role", item.get("path", "unknown"))))

    validations = verdict.get("validations", [])
    validation_ids = {item.get("validation_id") for item in validations if item.get("result") == "PASS"}
    hostile = next((item for item in validations if item.get("validation_id") == "VAL-VACUITY"), {})
    hostile_probes = hostile.get("detail", {}).get("hostile_probes", [])
    record(
        "immutable-d65-s8-candidate",
        not candidate_failures
        and not selected_dependency_failures
        and manifest.get("stage_id") == "D65-S8"
        and manifest.get("acceptance_critical_residue") == []
        and verdict.get("result") == "PASS"
        and verdict.get("blockers") == []
        and verdict.get("acceptance_critical_residue") == []
        and validation_ids == set(manifest.get("validation_ids", []))
        and len(validation_ids) == 6
        and len(hostile_probes) == 6
        and all(item.get("result") == "PASS" for item in hostile_probes),
        {
            "candidate_failures": candidate_failures,
            "selected_dependency_failures": selected_dependency_failures,
            "verdict": verdict.get("result"),
            "validation_ids": sorted(validation_ids),
            "hostile_probe_count": len(hostile_probes),
        },
    )

    admitted = decision.get("admitted_integration_epoch", {})
    run_validation = next((item for item in validations if item.get("validation_id") == "VAL-INTEGRATION-TWICE"), {})
    run_detail = run_validation.get("detail", {})
    record(
        "admitted-epoch-closure",
        admitted.get("epoch_id") == manifest.get("epoch_id") == verdict.get("epoch_id")
        and admitted.get("ontology_id") == manifest.get("ontology_id") == verdict.get("ontology_id")
        and admitted.get("stage_id") == "D65-S8"
        and admitted.get("conformance_result") == "PASS"
        and admitted.get("validation_count") == len(validation_ids) == 6
        and admitted.get("tests_per_run") == run_detail.get("run_1", {}).get("test_count") == run_detail.get("run_2", {}).get("test_count") == 22
        and admitted.get("deterministic_runs") == 2
        and admitted.get("hostile_probe_count") == len(hostile_probes) == 6
        and admitted.get("acceptance_critical_residue") == []
        and admitted.get("identity") == refs.get("manifest_sha256"),
        {"epoch_id": admitted.get("epoch_id"), "identity": admitted.get("identity")},
    )

    successor = decision.get("successor_preparation", {})
    cutover = decision.get("cutover", {})
    forbidden = successor.get("forbidden_effects", [])
    record(
        "successor-and-cutover-boundary",
        successor.get("authorized") is True
        and successor.get("route") == "CA2-ROUTE-PLAN"
        and len(successor.get("required_outputs", [])) >= 5
        and any("lib.rs" in item for item in forbidden)
        and any("migrate or cut over" in item for item in forbidden)
        and cutover == {
            "authorized": False,
            "performed": False,
            "decision_required": True,
            "candidate_required": True,
        }
        and decision.get("remaining_gate") == "G-INTEGRATION-ADMISSION-CUTOVER/cutover",
        {"route": successor.get("route"), "cutover": cutover},
    )

    record(
        "authority-ceiling",
        decision.get("authority_effect") == "admit-exact-d65-s8-epoch-and-authorize-reviewed-cutover-candidate-preparation-only"
        and len(decision.get("non_effects", [])) >= 8
        and any("does not export" in item for item in decision.get("non_effects", []))
        and any("does not migrate or cut over" in item for item in decision.get("non_effects", []))
        and any("does not authorize publication" in item for item in decision.get("non_effects", [])),
        {"authority_effect": decision.get("authority_effect")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-s8-integration-admission-validation/v1",
        "decision_id": decision.get("decision_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "resolved_gate_component": "G-INTEGRATION-ADMISSION-CUTOVER/admission" if result == "PASS" else None,
        "remaining_gate": "G-INTEGRATION-ADMISSION-CUTOVER/cutover",
        "successor_preparation_authorized": result == "PASS",
        "cutover_authorized": False,
        "cutover_performed": False,
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": str(Path(__file__).relative_to(LAB)), "sha256": digest(Path(__file__))},
            {"path": refs.get("manifest_path"), "sha256": refs.get("manifest_sha256")},
            {"path": refs.get("verdict_path"), "sha256": refs.get("verdict_sha256")},
        ],
        "authority_effect": decision.get("authority_effect") if result == "PASS" else "none",
        "claim_ceiling": "PASS proves only exact D65-S8 epoch admission and authorization to prepare a separate reviewed export/cutover candidate. It does not export adapters, mutate accepted runtime bytes, migrate, cut over, publish, release, deploy, or create external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision_id": receipt["decision_id"],
        "result": result,
        "failed_checks": failed,
        "resolved_gate_component": receipt["resolved_gate_component"],
        "remaining_gate": receipt["remaining_gate"],
        "successor_preparation_authorized": receipt["successor_preparation_authorized"],
        "cutover_authorized": False,
        "cutover_performed": False,
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
