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
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"


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
    approval = decision.get("product_approval", {})
    downstream = decision.get("downstream_authority", {})
    if source.get("kind") != "explicit-user-selection" or source.get("verbatim") != "D65PAPP-1":
        errors.append("explicit D65PAPP-1 owner selection is absent")
    if source.get("selected_option_id") != "D65PAPP-1" or selected != {"option_id": "D65PAPP-1", "effect": "product-approval-only"}:
        errors.append("selected option is not exact D65PAPP-1")
    if set(decision.get("alternatives", [])) != {"D65PAPP-2", "D65PAPP-3", "D65PAPP-4"}:
        errors.append("alternatives are incomplete")
    if approval.get("state") != "approved" or approval.get("identity") != decision.get("candidate_refs", {}).get("manifest_sha256"):
        errors.append("approval does not bind the exact manifest identity")
    if approval.get("product_tests") != "PASS" or approval.get("product_test_checks") != 7 or approval.get("mutation_probes") != 4:
        errors.append("approval exceeds or omits tested-product evidence")
    required_false = {
        "implementation_admitted", "ontology_admitted", "activated",
        "migration_authorized", "cutover_authorized", "cutover_performed",
        "publication_authorized", "release_authorized", "deployment_authorized",
        "external_effect_authorized",
    }
    if any(downstream.get(key) is not False for key in required_false) or downstream.get("separate_decision_required") is not True:
        errors.append("downstream authority ceiling is violated")
    if decision.get("authority_effect") != "product-approval-only":
        errors.append("authority effect exceeds product approval")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(decision)]
    add("decision-schema", not schema_errors, schema_errors)

    admissibility = decision.get("admissibility", {})
    request_path = LAB / str(admissibility.get("request_path", ""))
    receipt_path = LAB / str(admissibility.get("receipt_path", ""))
    admissibility_failures: list[str] = []
    if not request_path.is_file() or digest(request_path) != admissibility.get("request_sha256"):
        admissibility_failures.append("request-digest-mismatch")
    if not receipt_path.is_file() or digest(receipt_path) != admissibility.get("receipt_sha256"):
        admissibility_failures.append("receipt-digest-mismatch")
    if not admissibility_failures:
        request = load(request_path)
        receipt = load(receipt_path)
        canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if receipt.get("requestDigest") != hashlib.sha256(canonical).hexdigest():
            admissibility_failures.append("canonical-request-digest-mismatch")
        if receipt.get("routeOutcome") != "gate" or receipt.get("decisionGateRequired") is not True:
            admissibility_failures.append("decision-gate-not-required")
        if set(receipt.get("admissibleOptionIds", [])) != {"D65PAPP-1", "D65PAPP-2", "D65PAPP-3", "D65PAPP-4"}:
            admissibility_failures.append("admissible-option-set-mismatch")
    add("option-admissibility", not admissibility_failures, admissibility_failures)

    refs = decision.get("candidate_refs", {})
    ref_failures: list[str] = []
    artifacts: dict[str, Path] = {}
    for name in ("manifest", "product_test_evidence", "approval_request"):
        path = LAB / str(refs.get(f"{name}_path", ""))
        artifacts[name] = path
        if not path.is_file() or digest(path) != refs.get(f"{name}_sha256"):
            ref_failures.append(f"{name}-digest-mismatch")
    add("immutable-product-refs", not ref_failures, ref_failures)

    evidence = load(artifacts["product_test_evidence"])
    request = load(artifacts["approval_request"])
    options = {item.get("option_id"): item for item in request.get("options", [])}
    eligible = (
        evidence.get("result") == "PASS"
        and evidence.get("product_candidate_frozen") is True
        and evidence.get("product_approval_eligible") is True
        and evidence.get("manifest_sha256") == refs.get("manifest_sha256")
        and request.get("eligibility") == "eligible"
        and request.get("decision_state") == "not-decided"
        and request.get("manifest_sha256") == refs.get("manifest_sha256")
        and request.get("product_test_evidence_sha256") == refs.get("product_test_evidence_sha256")
        and options.get("D65PAPP-1", {}).get("authority_effect") == "product-approval-only"
    )
    add("approval-eligibility", eligible, {"evidence_result": evidence.get("result"), "request_eligibility": request.get("eligibility")})

    semantics = semantic_errors(decision)
    add("owner-selection-and-claim-ceiling", not semantics, semantics)

    probes: list[dict[str, str]] = []
    mutations = {
        "manifest-digest-substitution": ("candidate_refs", "manifest_sha256", "0" * 64),
        "option-substitution": ("selected_option", "option_id", "D65PAPP-2"),
        "cutover-escalation": ("downstream_authority", "cutover_authorized", True),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        if probe_id == "manifest-digest-substitution":
            caught = caught or mutated["candidate_refs"]["manifest_sha256"] != digest(artifacts["manifest"])
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-epoch-002-product-approval-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "stage_state": "PRODUCT_APPROVED" if result == "PASS" else "not_evaluable",
        "checks": checks,
        "failed_checks": failed,
        "product_candidate_id": refs.get("product_candidate_id"),
        "manifest_sha256": refs.get("manifest_sha256"),
        "product_approval": "approved" if result == "PASS" else "not_evaluable",
        "implementation_admitted": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "product-approval-only" if result == "PASS" else "none",
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": refs.get("manifest_path"), "sha256": refs.get("manifest_sha256")},
            {"path": refs.get("product_test_evidence_path"), "sha256": refs.get("product_test_evidence_sha256")},
            {"path": refs.get("approval_request_path"), "sha256": refs.get("approval_request_sha256")},
        ],
        "claim_ceiling": "PASS proves only that D65PAPP-1 approved the exact frozen tested product. It grants no admission, activation, migration, cutover, publication, release, deployment, credential, destructive action, or external effect.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("decision_id", "gate_id", "result", "failed_checks", "stage_state", "product_approval", "implementation_admitted", "cutover_authorized", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
