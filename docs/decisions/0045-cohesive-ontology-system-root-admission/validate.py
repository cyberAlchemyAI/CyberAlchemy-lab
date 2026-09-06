#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
CANDIDATE = ROOT / "admission-candidate.json"
SCHEMA = ROOT / "schema.json"
REQUEST = ROOT / "admissibility-request.json"
ADMISSIBILITY = ROOT / "receipts" / "admissibility.json"
RECEIPT = ROOT / "receipts" / "candidate-validation.json"
EXPECTED_CANDIDATE = "ef3c79eb6bb662fa024c5fc0375fca242aa6b75e37483eae88362d33d7f69895"
EXPECTED_REQUEST = "8dc4a9deb6aa92d8fa9ff15ed15c402deb53c37df2bf4e25e7a45c4a6368e016"
EXPECTED_ADMISSIBILITY = "6a4e1c44614278058d206f3a6c731a130c01f803a09a50580eaba334883dd147"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(candidate: dict[str, Any], model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("status") != "frozen-awaiting-owner-decision" or candidate.get("decision_state") != "not-decided":
        errors.append("candidate-state-mismatch")
    if candidate.get("authority_effect") != "none":
        errors.append("candidate-authority-effect-mismatch")
    approved = candidate.get("approved_product", {})
    expected_approved_digests = {
        "product_candidate_sha256": "0aae6913d90fc836ff88d0714da695629a92cef81881f8569582eff8666dead5",
        "ontology_system_sha256": "977ab3235bc52b3feddc2e8c4e7103349d763ab802f5982534ac409fd1e2c8c9",
        "product_test_sha256": "26baa86798ebdcadf68f4925c9d0ddf66bc9b1e3b6bff4ba1e7cc3d46c523c42",
        "product_approval_decision_sha256": "1e490e296f0e497268fe5da88c95b150f7b5802148379e73fd19fafe93ab2b18",
        "product_approval_validation_sha256": "ad8afc5bc9669db9c17ac58b86d44438502be49a5163dc08d0b12e43c7dcf79b",
    }
    if any(approved.get(key) != value for key, value in expected_approved_digests.items()):
        errors.append("approved-product-digest-mismatch")
    scope = candidate.get("admission_scope", {})
    if (
        scope.get("root_component_id") != "CAL-LAB-ONTOLOGY-SYSTEM"
        or scope.get("root_system_id") != "cal.ontology-system.lab-cohesion"
        or scope.get("effect_if_selected") != "admit-exact-cohesive-root-and-composition-overlay-only"
        or scope.get("component_count") != 14
        or scope.get("relation_count") != 15
        or scope.get("catalog_package_count") != 20
        or scope.get("review_group_count") != 10
    ):
        errors.append("admission-scope-mismatch")
    model_relations = [item.get("relation_id") for item in model.get("relations", [])]
    if scope.get("relation_ids") != model_relations or len(set(model_relations)) != 15:
        errors.append("relation-overlay-mismatch")
    preserved = candidate.get("preserved_child_authority", {})
    expected_preserved = {
        "already_admitted_components_remain_admitted": 8,
        "approved_not_admitted_components_remain_approved_not_admitted": 1,
        "accepted_not_admitted_components_remain_accepted_not_admitted": 1,
        "candidate_only_components_remain_candidate_only": 4,
        "child_ontologies_admitted_by_this_candidate": 0,
        "owner_routes_transferred": 0,
        "domainspec_profiles_selected": 0,
    }
    if any(preserved.get(key) != value for key, value in expected_preserved.items()):
        errors.append("child-authority-preservation-mismatch")
    if "must not admit" not in preserved.get("forbidden_inference", ""):
        errors.append("child-authority-non-collapse-missing")
    truth = candidate.get("canonical_truth_boundary", {})
    if truth.get("root_is_replay_source") is not False or "event" not in truth.get("canonical", "").lower():
        errors.append("canonical-truth-boundary-mismatch")
    if set(candidate.get("retained_residue_ids", [])) != {item.get("residue_id") for item in model.get("residue", [])}:
        errors.append("residue-preservation-mismatch")
    options = candidate.get("options", [])
    option_ids = [item.get("option_id") for item in options]
    if option_ids != ["CLOSYS-ADM-1", "CLOSYS-ADM-2", "CLOSYS-ADM-3", "CLOSYS-ADM-4"]:
        errors.append("option-set-mismatch")
    if options and options[0].get("authority_effect") != "root-admission-only":
        errors.append("admission-option-effect-mismatch")
    downstream = candidate.get("downstream_authority", {})
    if any(value is not False for value in downstream.values()):
        errors.append("downstream-authority-escalation")
    return errors


def validate() -> dict[str, Any]:
    candidate = load(CANDIDATE)
    schema = load(SCHEMA)
    request = load(REQUEST)
    admissibility = load(ADMISSIBILITY)
    approved = candidate["approved_product"]
    model_path = LAB / approved["ontology_system_path"]
    model = load(model_path)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = sorted(Draft202012Validator(schema).iter_errors(candidate), key=lambda item: list(item.path))
    add("candidate-schema", not schema_errors, [error.message for error in schema_errors])
    add("candidate-frozen-identity", sha(CANDIDATE) == EXPECTED_CANDIDATE, {"actual": sha(CANDIDATE), "expected": EXPECTED_CANDIDATE})

    refs = {
        "product_candidate": (approved["product_candidate_path"], approved["product_candidate_sha256"]),
        "ontology_system": (approved["ontology_system_path"], approved["ontology_system_sha256"]),
        "product_test": (approved["product_test_path"], approved["product_test_sha256"]),
        "product_approval_decision": (approved["product_approval_decision_path"], approved["product_approval_decision_sha256"]),
        "product_approval_validation": (approved["product_approval_validation_path"], approved["product_approval_validation_sha256"]),
    }
    ref_failures = []
    for name, (relative, digest) in refs.items():
        path = LAB / relative
        if not path.is_file() or sha(path) != digest:
            ref_failures.append(name)
    add("exact-approved-product-bindings", not ref_failures, {"failures": ref_failures, "refs": refs})

    approval = load(LAB / approved["product_approval_decision_path"])
    approval_validation = load(LAB / approved["product_approval_validation_path"])
    approval_ok = (
        approval.get("status") == "selected"
        and approval.get("authority_effect") == "product-approval-only"
        and approval.get("product_approval", {}).get("state") == "approved"
        and approval.get("subject", {}).get("product_candidate_sha256") == approved["product_candidate_sha256"]
        and approval.get("downstream_authority", {}).get("cohesive_root_admitted") is False
        and approval_validation.get("result") == "PASS"
        and approval_validation.get("stage_state") == "PRODUCT_APPROVED"
        and approval_validation.get("cohesive_root_admitted") is False
    )
    add("product-approval-boundary", approval_ok, {"decision": approval.get("decision_id"), "validation": approval_validation.get("result")})

    product_validator_path = (LAB / approved["product_candidate_path"]).parent / "validate.py"
    spec = importlib.util.spec_from_file_location("cohesive_product_validator", product_validator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load cohesive Product validator")
    product_validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(product_validator)
    product_candidate = product_validator.load_json(product_validator.CANDIDATE_PATH)
    model_errors = product_validator.validate_model(model, product_candidate)
    add("current-product-model-validation", not model_errors, model_errors)

    semantic = semantic_errors(candidate, model)
    add("root-scope-and-authority-ceiling", not semantic, semantic)

    gate_ok = (
        sha(REQUEST) == EXPECTED_REQUEST
        and sha(ADMISSIBILITY) == EXPECTED_ADMISSIBILITY
        and request.get("decisionId") == "CAL-ONTOLOGY-SYSTEM-ROOT-ADMISSION-0045"
        and admissibility.get("decisionId") == request.get("decisionId")
        and admissibility.get("routeOutcome") == "gate"
        and set(admissibility.get("admissibleOptionIds", [])) == {"CLOSYS-ADM-1", "CLOSYS-ADM-2", "CLOSYS-ADM-3", "CLOSYS-ADM-4"}
    )
    add("decision-gate-admissibility", gate_ok, {"route": admissibility.get("routeOutcome"), "options": admissibility.get("admissibleOptionIds")})

    probes = []
    mutations = {
        "product-approval-digest-drift": ("approved_product", "product_approval_decision_sha256", "0" * 64),
        "candidate-authority-inflation": (None, "authority_effect", "admit"),
        "child-admission-inflation": ("preserved_child_authority", "child_ontologies_admitted_by_this_candidate", 1),
        "domainspec-selection-inflation": ("preserved_child_authority", "domainspec_profiles_selected", 1),
        "root-replay-source-collapse": ("canonical_truth_boundary", "root_is_replay_source", True),
        "downstream-activation-escalation": ("downstream_authority", "activated", True),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(candidate)
        if section is None:
            mutated[key] = value
        else:
            mutated[section][key] = value
        caught = bool(semantic_errors(mutated, model))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    return {
        "schema_version": "cyberalchemy-lab-cohesive-ontology-system-root-admission-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "candidate_sha256": sha(CANDIDATE),
        "gate_id": candidate["gate_id"],
        "result": "PASS" if not failed else "BLOCK",
        "failed_checks": failed,
        "checks": checks,
        "decision_gate_ready": not failed,
        "decision_state": "not-decided",
        "root_admission_authorized": False,
        "child_ontology_admission_authorized": False,
        "authority_effect": "none",
        "claim_ceiling": "PASS proves only that the exact cohesive-root admission candidate is current, Product-approved, scope-closed, non-vacuous, and ready for its owner gate. It is not an admission decision and grants no root or child admission or operational effect.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.write_receipt:
        if result["result"] != "PASS":
            raise SystemExit("refusing to write a BLOCK receipt")
        candidate = load(CANDIDATE)
        approved = candidate["approved_product"]
        inputs = [
            CANDIDATE,
            SCHEMA,
            ROOT / "README.md",
            ROOT / "validate.py",
            REQUEST,
            ADMISSIBILITY,
            LAB / approved["product_candidate_path"],
            LAB / approved["ontology_system_path"],
            LAB / approved["product_test_path"],
            LAB / approved["product_approval_decision_path"],
            LAB / approved["product_approval_validation_path"],
        ]
        receipt = copy.deepcopy(result)
        receipt["inputs"] = [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in inputs]
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
