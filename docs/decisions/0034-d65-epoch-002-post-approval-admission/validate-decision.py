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
DECISION = HERE / "decision.json"
SCHEMA = HERE / "decision-schema.json"
RECEIPT = HERE / "decision-validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = decision.get("decision_source", {})
    selected = decision.get("selected_option", {})
    admission = decision.get("admission", {})
    downstream = decision.get("downstream_authority", {})
    if source.get("kind") != "explicit-user-selection" or source.get("verbatim") != "D65PADM-1" or source.get("selected_option_id") != "D65PADM-1":
        errors.append("explicit D65PADM-1 owner selection is absent")
    if selected != {"option_id": "D65PADM-1", "effect": "admission-only"}:
        errors.append("selected option is not exact D65PADM-1")
    if set(decision.get("alternatives", [])) != {"D65PADM-2", "D65PADM-3", "D65PADM-4"}:
        errors.append("alternatives are incomplete")
    if admission.get("state") != "admitted" or admission.get("activation_state") != "inactive":
        errors.append("admission state or inactive boundary is invalid")
    if admission.get("identity") != decision.get("candidate_refs", {}).get("product_manifest_sha256"):
        errors.append("admission identity differs from exact product manifest")
    if downstream.get("implementation_admitted") is not True:
        errors.append("implementation admission is not represented")
    required_false = (
        "runtime_activated", "migration_authorized", "cutover_authorized",
        "cutover_performed", "publication_authorized", "release_authorized",
        "deployment_authorized", "external_effect_authorized",
    )
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream authority ceiling is violated")
    if downstream.get("separate_activation_and_cutover_decision_required") is not True:
        errors.append("separate activation and cutover boundary is missing")
    if decision.get("authority_effect") != "admission-only":
        errors.append("authority effect exceeds admission only")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(decision)]
    add("decision-schema", not errors, errors)

    refs = decision.get("candidate_refs", {})
    drift = []
    for prefix in ("admission_candidate", "candidate_validation", "admissibility_request", "admissibility_receipt", "rehearsal_receipt", "product_manifest", "product_approval_decision"):
        path = LAB / str(refs.get(f"{prefix}_path", ""))
        actual = digest(path) if path.is_file() else None
        if actual != refs.get(f"{prefix}_sha256"):
            drift.append({"input": prefix, "path": str(path), "actual": actual})
    add("exact-input-currentness", not drift, drift)

    candidate = load(LAB / refs["admission_candidate_path"])
    candidate_validation = load(LAB / refs["candidate_validation_path"])
    rehearsal = load(LAB / refs["rehearsal_receipt_path"])
    closure = (
        candidate.get("candidate_id") == decision.get("admission", {}).get("admission_candidate_id")
        and candidate.get("decision_state") == "not-decided"
        and candidate.get("downstream_authority", {}).get("implementation_admitted") is False
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("candidate_frozen") is True
        and candidate_validation.get("decision_gate_ready") is True
        and candidate_validation.get("decision_state") == "not-decided"
        and rehearsal.get("result") == "PASS"
        and rehearsal.get("rollback_result") == "PASS"
        and rehearsal.get("mutation_probes_passed") == rehearsal.get("mutation_probes_total") == 8
        and rehearsal.get("protected_byte_drift") == []
    )
    add("frozen-candidate-and-rehearsal-closure", closure, {"candidate": candidate_validation.get("result"), "rehearsal": rehearsal.get("result")})

    admissibility_request = load(LAB / refs["admissibility_request_path"])
    admissibility_receipt = load(LAB / refs["admissibility_receipt_path"])
    canonical_request = json.dumps(admissibility_request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    admissible = (
        admissibility_receipt.get("requestDigest") == hashlib.sha256(canonical_request).hexdigest()
        and admissibility_receipt.get("routeOutcome") == "gate"
        and admissibility_receipt.get("decisionGateRequired") is True
        and set(admissibility_receipt.get("admissibleOptionIds", [])) == {"D65PADM-1", "D65PADM-2", "D65PADM-3", "D65PADM-4"}
    )
    add("option-admissibility", admissible, {"route_outcome": admissibility_receipt.get("routeOutcome")})

    semantics = semantic_errors(decision)
    add("owner-selection-and-admission-ceiling", not semantics, semantics)

    probes = []
    for probe_id, mutate in (
        ("manifest-digest-substitution", lambda value: value["candidate_refs"].__setitem__("product_manifest_sha256", "0" * 64)),
        ("option-substitution", lambda value: value["selected_option"].__setitem__("option_id", "D65PADM-2")),
        ("activation-escalation", lambda value: value["downstream_authority"].__setitem__("runtime_activated", True)),
        ("cutover-escalation", lambda value: value["downstream_authority"].__setitem__("cutover_authorized", True)),
    ):
        mutated = copy.deepcopy(decision)
        mutate(mutated)
        if probe_id == "manifest-digest-substitution":
            caught = mutated["candidate_refs"]["product_manifest_sha256"] != digest(LAB / mutated["candidate_refs"]["product_manifest_path"])
        else:
            caught = bool(semantic_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("decision-mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-post-approval-admission-decision-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "admission_state": "admitted" if result == "PASS" else "not_evaluable",
        "product_manifest_sha256": refs.get("product_manifest_sha256"),
        "implementation_admitted": result == "PASS",
        "runtime_activated": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "admission-only" if result == "PASS" else "none",
        "inputs": [{"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)}, {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)}, {"path": refs.get("admission_candidate_path"), "sha256": refs.get("admission_candidate_sha256")}],
        "claim_ceiling": "PASS proves only exact D65PADM-1 admission of the approved and rehearsed epoch-002 implementation product as inactive. It grants no activation, migration, cutover, publication, release, deployment, credential use, destructive action, or external effect."
    }
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("decision_id", "gate_id", "result", "failed_checks", "admission_state", "implementation_admitted", "runtime_activated", "cutover_authorized", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
