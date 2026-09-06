#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
DECISION = HERE / "decision.json"
SCHEMA = HERE / "decision-schema.json"
RECEIPT = HERE / "receipts/decision-validation.json"
L4_VALIDATOR = LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/v1/validate-l4.py"
EXPECTED_OPTIONS = {"L4AADM-1", "L4AADM-2", "L4AADM-3", "L4AADM-4"}
EXPECTED_REFS = {
    "admission_candidate": "daf71bbbb1bdfa1ad533d3410b65dfd355c252c7bfb6bb80377bc7c1bb976eb0",
    "candidate_validation": "cf37917e15714caf04bc79695455caa1f4084faf50d89012f630cd88b0e140ec",
    "product_approval_decision": "6f57ea86f8547fece058fa70e01c7afe4ed65bc97ec6b3a4f66f774a1f6301f3",
    "product_approval_validation": "a2030d07bcec5e53b41a8754c525166cc56773a1ee3710a656f5a7b1dd81eb96",
    "sandbox_evidence": "bc9f367f18ce9530e6a8cd78a6d8b3edcbe788c753505847e7e5b999e1d4ddb3",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def semantic_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if decision.get("decision_source") != {
        "kind": "explicit-user-selection", "verbatim": "`L4AADM-1`",
        "selected_option_id": "L4AADM-1", "observed_count": 1,
    }:
        errors.append("explicit L4AADM-1 owner selection is absent")
    if decision.get("selected_option") != {"option_id": "L4AADM-1", "effect": "adapter-admission-only"}:
        errors.append("selected option is not exact L4AADM-1")
    if set(decision.get("alternatives", [])) != {"L4AADM-2", "L4AADM-3", "L4AADM-4"}:
        errors.append("alternatives are incomplete")
    admission = decision.get("adapter_admission", {})
    required_admission = {
        "state": "admitted",
        "identity": "cal.prototype.rust-state-bearing-sandbox-target/epoch-003",
        "scope": "non-live bounded sandbox activation observation and explicit teardown only",
        "candidate_identity": EXPECTED_REFS["admission_candidate"],
        "caller_supplied_path": False, "credential_kind": "none", "network": False,
        "production_data": False, "live": False,
        "state_survives_activation_observation": True,
        "explicit_teardown_required": True,
        "engine_substitution_allowed": False,
        "migration_allowed": False, "cutover_allowed": False,
        "runtime_activated": False, "cleanup_required": True,
        "external_effects": False,
    }
    if any(admission.get(key) != value for key, value in required_admission.items()):
        errors.append("adapter admission identity or scope is not exact")
    downstream = decision.get("downstream_authority", {})
    required_false = {
        "implementation_admitted", "ontology_admitted", "runtime_activated",
        "live_execution_ready", "migration_authorized", "cutover_authorized",
        "cutover_performed", "publication_authorized", "release_authorized",
        "deployment_authorized", "credentials_authorized",
        "destructive_action_authorized", "external_effect_authorized",
    }
    if downstream.get("adapter_admitted") is not True:
        errors.append("adapter admission was not recorded")
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream authority ceiling is violated")
    if downstream.get("separate_activation_and_effect_decisions_required") is not True:
        errors.append("separate activation and effect decisions are not preserved")
    if decision.get("authority_effect") != "adapter-admission-only":
        errors.append("authority effect exceeds adapter admission")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if not DECISION.is_file():
        print(json.dumps({
            "decision_id": "CAL-D65-L4AADM-0040",
            "gate_id": "G-D65-L4-STATE-BEARING-SANDBOX-ADAPTER-ADMISSION",
            "result": "BLOCK", "failed_checks": ["explicit-owner-selection-absent"],
            "stage_state": "ADAPTER_ADMISSION_CANDIDATE_READY",
            "adapter_admission": "not-decided", "adapter_admitted": False,
            "runtime_activated": False, "live_execution_ready": False,
            "cutover_authorized": False, "external_effect_authorized": False,
            "authority_effect": "none",
        }, indent=2))
        return 1

    decision = load(DECISION)
    checks: list[dict[str, Any]] = []
    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(decision)]
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
        request, receipt = load(request_path), load(receipt_path)
        if receipt.get("requestDigest") != canonical_digest(request):
            admissibility_failures.append("canonical-request-digest-mismatch")
        if receipt.get("routeOutcome") != "gate" or receipt.get("decisionGateRequired") is not True or set(receipt.get("admissibleOptionIds", [])) != EXPECTED_OPTIONS or set(receipt.get("presentedOptionIds", [])) != EXPECTED_OPTIONS or receipt.get("rejectedOptions") != []:
            admissibility_failures.append("admissibility-gate-mismatch")
    add("option-admissibility", not admissibility_failures, admissibility_failures)

    refs = decision.get("candidate_refs", {})
    ref_failures, artifacts = [], {}
    for name, expected in EXPECTED_REFS.items():
        path = LAB / str(refs.get(f"{name}_path", ""))
        artifacts[name] = path
        if refs.get(f"{name}_sha256") != expected or not path.is_file() or digest(path) != expected:
            ref_failures.append(f"{name}-digest-mismatch")
    add("immutable-admission-refs", not ref_failures, ref_failures)

    candidate = load(artifacts["admission_candidate"])
    candidate_validation = load(artifacts["candidate_validation"])
    product_decision = load(artifacts["product_approval_decision"])
    product_validation = load(artifacts["product_approval_validation"])
    evidence = load(artifacts["sandbox_evidence"])
    closure = (
        candidate.get("candidate_id") == "CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-ADAPTER-ADMISSION-CANDIDATE-001"
        and candidate.get("decision_state") == "not-decided"
        and candidate.get("authority_effect") == "none"
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("candidate_frozen") is True
        and candidate_validation.get("decision_gate_ready") is True
        and product_decision.get("selected_option", {}).get("option_id") == "L4PAPP-1"
        and product_validation.get("stage_state") == "PRODUCT_APPROVED"
        and evidence.get("result") == "PASS"
        and evidence.get("rust_tests_per_run") == 35
        and evidence.get("contract", {}).get("invariant_count") == 7
        and evidence.get("state_survives_activation_observation") is True
        and evidence.get("explicit_teardown_verified") is True
        and evidence.get("runtime_activated") is False
        and evidence.get("external_effects") is False
    )
    add("candidate-product-and-sandbox-closure", closure, {"candidate": candidate_validation.get("result"), "product_approval": product_validation.get("result"), "sandbox": evidence.get("result")})

    live_validation = subprocess.run(
        [sys.executable, str(L4_VALIDATOR)], cwd=L4_VALIDATOR.parent,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        live_summary = json.loads(live_validation.stdout)
    except json.JSONDecodeError:
        live_summary = {}
    add("current-product-tests", live_validation.returncode == 0 and live_summary.get("result") == "PASS" and live_summary.get("rust_tests_per_run") == 35 and live_summary.get("invariants") == 7, {"exit": live_validation.returncode, "summary": live_summary, "tail": live_validation.stdout[-2000:] if live_validation.returncode else ""})

    semantics = semantic_errors(decision)
    add("owner-selection-and-claim-ceiling", not semantics, semantics)
    probes = []
    mutations = {
        "candidate-digest-substitution": ("candidate_refs", "admission_candidate_sha256", "0" * 64),
        "option-substitution": ("selected_option", "option_id", "L4AADM-2"),
        "adapter-identity-substitution": ("adapter_admission", "identity", "cal.prototype.other-adapter"),
        "scope-expansion": ("adapter_admission", "scope", "live sandbox"),
        "engine-substitution-escalation": ("adapter_admission", "engine_substitution_allowed", True),
        "activation-escalation": ("downstream_authority", "runtime_activated", True),
        "cutover-escalation": ("downstream_authority", "cutover_authorized", True),
        "external-effect-escalation": ("downstream_authority", "external_effect_authorized", True),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        if probe_id == "candidate-digest-substitution":
            caught = caught or mutated["candidate_refs"]["admission_candidate_sha256"] != digest(artifacts["admission_candidate"])
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(probe["result"] == "PASS" for probe in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-l4-state-bearing-sandbox-adapter-admission-validation/v1",
        "decision_id": decision.get("decision_id"), "gate_id": decision.get("gate_id"),
        "result": result, "stage_state": "ADAPTER_ADMITTED" if result == "PASS" else "not_evaluable",
        "checks": checks, "failed_checks": failed,
        "admission_candidate_id": refs.get("admission_candidate_id"),
        "admission_candidate_sha256": refs.get("admission_candidate_sha256"),
        "adapter_identity": decision.get("adapter_admission", {}).get("identity"),
        "adapter_scope": decision.get("adapter_admission", {}).get("scope"),
        "adapter_admission": "admitted" if result == "PASS" else "not_evaluable",
        "adapter_admitted": result == "PASS", "implementation_admitted": False,
        "runtime_activated": False, "live_execution_ready": False,
        "migration_authorized": False, "cutover_authorized": False,
        "cutover_performed": False, "publication_authorized": False,
        "deployment_authorized": False, "external_effect_authorized": False,
        "authority_effect": "adapter-admission-only" if result == "PASS" else "none",
        "inputs": [{"path": str(path.relative_to(LAB)), "sha256": digest(path)} for path in (
            DECISION, SCHEMA, request_path, receipt_path,
            artifacts["admission_candidate"], artifacts["candidate_validation"],
            artifacts["product_approval_decision"], artifacts["product_approval_validation"],
            artifacts["sandbox_evidence"], HERE / "DECISION.md", HERE / "README.md",
            HERE / "validate-decision.py",
        )],
        "claim_ceiling": "PASS proves only that the owner selected L4AADM-1 and admitted the exact product-approved state-bearing sandbox adapter for bounded non-live activation observation and explicit teardown. No governed runtime activation, live execution, migration, cutover, publication, release, deployment, credential, destructive action, or external effect is authorized or performed.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in (
        "decision_id", "gate_id", "result", "failed_checks", "stage_state",
        "adapter_identity", "adapter_scope", "adapter_admission", "adapter_admitted",
        "implementation_admitted", "runtime_activated", "live_execution_ready",
        "cutover_authorized", "external_effect_authorized", "authority_effect",
    )}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
