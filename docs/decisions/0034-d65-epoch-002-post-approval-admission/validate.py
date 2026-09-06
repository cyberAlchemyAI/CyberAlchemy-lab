#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CANDIDATE = HERE / "admission-candidate.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "candidate-validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boundary_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    downstream = candidate.get("downstream_authority", {})
    required_false = (
        "implementation_admitted", "runtime_activated", "migration_authorized",
        "cutover_authorized", "cutover_performed", "publication_authorized",
        "release_authorized", "deployment_authorized", "external_effect_authorized",
    )
    if candidate.get("decision_state") != "not-decided":
        errors.append("candidate contains an owner decision")
    if candidate.get("authority_effect") != "none":
        errors.append("candidate carries authority")
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream authority ceiling is violated")
    if downstream.get("separate_activation_and_cutover_decision_required") is not True:
        errors.append("separate activation and cutover decision is not preserved")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    candidate = load(CANDIDATE)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(candidate)]
    add("candidate-schema", not errors, errors)

    refs: list[tuple[str, str, str]] = []
    for section, pairs in (
        ("approved_product", (("manifest_path", "manifest_sha256"), ("product_approval_decision_path", "product_approval_decision_sha256"), ("product_approval_validation_path", "product_approval_validation_sha256"))),
        ("rehearsal_evidence", (("plan_path", "plan_sha256"), ("contract_path", "contract_sha256"), ("canonical_events_path", "canonical_events_sha256"), ("receipt_path", "receipt_sha256"))),
        ("admissibility", (("request_path", "request_sha256"), ("receipt_path", "receipt_sha256"))),
    ):
        value = candidate[section]
        for path_key, hash_key in pairs:
            refs.append((section, value[path_key], value[hash_key]))
    drift = []
    for section, path_text, expected in refs:
        path = LAB / path_text
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            drift.append({"section": section, "path": path_text, "expected": expected, "actual": actual})
    add("exact-input-currentness", not drift, drift)

    product_validation = load(LAB / candidate["approved_product"]["product_approval_validation_path"])
    rehearsal = load(LAB / candidate["rehearsal_evidence"]["receipt_path"])
    closure = (
        product_validation.get("result") == "PASS"
        and product_validation.get("product_approval") == "approved"
        and product_validation.get("manifest_sha256") == candidate["approved_product"]["manifest_sha256"]
        and rehearsal.get("result") == "PASS"
        and rehearsal.get("deterministic_runs") == 2
        and rehearsal.get("rust_public_contract_tests_per_run") == 4
        and rehearsal.get("mutation_probes_passed") == rehearsal.get("mutation_probes_total") == 8
        and rehearsal.get("rollback_result") == "PASS"
        and rehearsal.get("protected_byte_drift") == []
        and rehearsal.get("final_gate_eligible") is True
        and rehearsal.get("admission_authorized") is False
        and rehearsal.get("cutover_authorized") is False
    )
    add("approved-product-and-rehearsal-closure", closure, {"product_approval": product_validation.get("result"), "rehearsal": rehearsal.get("result")})

    admissibility = candidate["admissibility"]
    request = load(LAB / admissibility["request_path"])
    receipt = load(LAB / admissibility["receipt_path"])
    request_digest = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    option_ids = {option.get("option_id") for option in candidate.get("options", [])}
    admissible = (
        receipt.get("requestDigest") == request_digest
        and receipt.get("routeOutcome") == "gate"
        and receipt.get("decisionGateRequired") is True
        and set(receipt.get("admissibleOptionIds", [])) == option_ids == {"D65PADM-1", "D65PADM-2", "D65PADM-3", "D65PADM-4"}
    )
    add("decision-gate-admissibility", admissible, {"route_outcome": receipt.get("routeOutcome"), "option_ids": sorted(option_ids)})

    boundary = boundary_errors(candidate)
    add("authority-ceiling", not boundary, boundary)

    probes = []
    for probe_id, mutate in (
        ("product-digest-drift", lambda value: value["approved_product"].__setitem__("manifest_sha256", "0" * 64)),
        ("implicit-owner-selection", lambda value: value.__setitem__("decision_state", "selected")),
        ("cutover-escalation", lambda value: value["downstream_authority"].__setitem__("cutover_authorized", True)),
    ):
        mutated = copy.deepcopy(candidate)
        mutate(mutated)
        if probe_id == "product-digest-drift":
            caught = mutated["approved_product"]["manifest_sha256"] != digest(LAB / mutated["approved_product"]["manifest_path"])
        else:
            caught = bool(boundary_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("candidate-mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-post-approval-admission-candidate-validation/v1",
        "candidate_id": candidate.get("candidate_id"),
        "gate_id": candidate.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "candidate_frozen": result == "PASS",
        "decision_gate_ready": result == "PASS",
        "decision_state": "not-decided",
        "admissible_option_ids": sorted(option_ids),
        "admission_authorized": False,
        "activation_authorized": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "authority_effect": "none",
        "inputs": [{"path": str(CANDIDATE.relative_to(LAB)), "sha256": digest(CANDIDATE)}, {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)}, {"path": candidate["rehearsal_evidence"]["receipt_path"], "sha256": candidate["rehearsal_evidence"]["receipt_sha256"]}],
        "claim_ceiling": "PASS proves only that one exact post-approval admission candidate is frozen, source-current, rehearsal-proven, and ready for its owner gate. It is not an admission decision and grants no activation, migration, cutover, publication, release, deployment, or external effect."
    }
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("candidate_id", "gate_id", "result", "failed_checks", "candidate_frozen", "decision_gate_ready", "decision_state", "admission_authorized", "cutover_authorized", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
