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
EXPECTED_OPTIONS = {"L4PAPP-1", "L4PAPP-2", "L4PAPP-3", "L4PAPP-4"}
EXPECTED_REFS = {
    "product_candidate": "20b1b9ecdbf13d97ead2015f0e1dea4a88cad0abe02f93c5ba2daf4b0bd9a08b",
    "product_test_evidence": "bc9f367f18ce9530e6a8cd78a6d8b3edcbe788c753505847e7e5b999e1d4ddb3",
    "approval_request": "c030e56ed1dabd66966c189b023a7ffa9d45b37f68775f8cb0085fec42e1f4f6",
    "packet_validation": "e7858200458d97d5d32a3700cace65018947bbbb2c1c07e897f9d92dde38dab9",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def semantic_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = decision.get("decision_source", {})
    selected = decision.get("selected_option", {})
    approval = decision.get("product_approval", {})
    downstream = decision.get("downstream_authority", {})
    if (
        source.get("kind") != "explicit-user-selection"
        or source.get("verbatim") != "`L4PAPP-1`"
        or source.get("selected_option_id") != "L4PAPP-1"
        or source.get("observed_count") != 1
    ):
        errors.append("explicit L4PAPP-1 owner selection is absent")
    if selected != {"option_id": "L4PAPP-1", "effect": "product-approval-only"}:
        errors.append("selected option is not exact L4PAPP-1")
    if set(decision.get("alternatives", [])) != {
        "L4PAPP-2", "L4PAPP-3", "L4PAPP-4"
    }:
        errors.append("alternatives are incomplete")
    refs = decision.get("candidate_refs", {})
    if (
        approval.get("state") != "approved"
        or approval.get("identity") != refs.get("product_candidate_sha256")
        or approval.get("product_tests") != "PASS"
        or approval.get("deterministic_runs") != 2
        or approval.get("rust_tests_per_run") != 35
        or approval.get("invariant_count") != 7
        or approval.get("state_survives_activation_observation") is not True
        or approval.get("explicit_teardown_verified") is not True
    ):
        errors.append("approval exceeds or omits tested-product evidence")
    required_false = {
        "adapter_admitted", "implementation_admitted", "ontology_admitted",
        "runtime_activated", "live_execution_ready", "migration_authorized",
        "cutover_authorized", "cutover_performed", "publication_authorized",
        "release_authorized", "deployment_authorized", "credentials_authorized",
        "destructive_action_authorized", "external_effect_authorized",
    }
    if (
        any(downstream.get(key) is not False for key in required_false)
        or downstream.get("separate_decision_required") is not True
    ):
        errors.append("downstream authority ceiling is violated")
    if decision.get("authority_effect") != "product-approval-only":
        errors.append("authority effect exceeds product approval")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if not DECISION.is_file():
        print(json.dumps({
            "decision_id": "CAL-D65-L4PAPP-0039",
            "gate_id": "G-D65-L4-STATE-BEARING-SANDBOX-PRODUCT-APPROVAL",
            "result": "BLOCK",
            "failed_checks": ["explicit-owner-selection-absent"],
            "stage_state": "PRODUCT_APPROVAL_PACKET_READY",
            "product_approval": "not-decided",
            "adapter_admitted": False,
            "runtime_activated": False,
            "live_execution_ready": False,
            "cutover_authorized": False,
            "external_effect_authorized": False,
            "authority_effect": "none",
        }, indent=2))
        return 1

    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({
            "check_id": check_id,
            "result": "PASS" if passed else "BLOCK",
            "detail": detail,
        })

    schema_errors = [
        error.message
        for error in Draft202012Validator(
            load(SCHEMA), format_checker=FormatChecker()
        ).iter_errors(decision)
    ]
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
        if receipt.get("requestDigest") != canonical_digest(request):
            admissibility_failures.append("canonical-request-digest-mismatch")
        if (
            receipt.get("routeOutcome") != "gate"
            or receipt.get("decisionGateRequired") is not True
            or set(receipt.get("admissibleOptionIds", [])) != EXPECTED_OPTIONS
            or set(receipt.get("presentedOptionIds", [])) != EXPECTED_OPTIONS
            or receipt.get("rejectedOptions") != []
        ):
            admissibility_failures.append("admissibility-gate-mismatch")
    add("option-admissibility", not admissibility_failures, admissibility_failures)

    refs = decision.get("candidate_refs", {})
    ref_failures: list[str] = []
    artifacts: dict[str, Path] = {}
    for name, expected in EXPECTED_REFS.items():
        path = LAB / str(refs.get(f"{name}_path", ""))
        artifacts[name] = path
        if (
            refs.get(f"{name}_sha256") != expected
            or not path.is_file()
            or digest(path) != expected
        ):
            ref_failures.append(f"{name}-digest-mismatch")
    add("immutable-product-refs", not ref_failures, ref_failures)

    packet = load(artifacts["packet_validation"])
    evidence = load(artifacts["product_test_evidence"])
    approval_request = load(artifacts["approval_request"])
    closure = (
        packet.get("result") == "PASS"
        and packet.get("stage_state") == "PRODUCT_APPROVAL_PACKET_READY"
        and packet.get("product_approval_eligible") is True
        and packet.get("decision_state") == "not-decided"
        and packet.get("authority_effect") == "none"
        and evidence.get("result") == "PASS"
        and evidence.get("rust_tests_per_run") == 35
        and evidence.get("deterministic_runs") == 2
        and evidence.get("contract", {}).get("invariant_count") == 7
        and evidence.get("state_survives_activation_observation") is True
        and evidence.get("explicit_teardown_verified") is True
        and evidence.get("runtime_activated") is False
        and evidence.get("external_effects") is False
        and approval_request.get("decision_state") == "not-decided"
        and approval_request.get("authority_effect") == "none"
        and {item.get("option_id"): item.get("authority_effect") for item in approval_request.get("options", [])}.get("L4PAPP-1")
        == "product-approval-only"
    )
    add("tested-product-and-packet-closure", closure, {
        "packet": packet.get("result"),
        "tests": evidence.get("result"),
        "request_state": approval_request.get("decision_state"),
    })

    live_validation = subprocess.run(
        [sys.executable, str(L4_VALIDATOR)],
        cwd=L4_VALIDATOR.parent,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        live_summary = json.loads(live_validation.stdout)
    except json.JSONDecodeError:
        live_summary = {}
    add(
        "current-product-tests",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("rust_tests_per_run") == 35
        and live_summary.get("invariants") == 7
        and live_summary.get("state_survives_activation_observation") is True,
        {"exit": live_validation.returncode, "summary": live_summary,
         "tail": live_validation.stdout[-2000:] if live_validation.returncode else ""},
    )

    semantics = semantic_errors(decision)
    add("owner-selection-and-claim-ceiling", not semantics, semantics)

    probes: list[dict[str, str]] = []
    mutations = {
        "candidate-digest-substitution": ("candidate_refs", "product_candidate_sha256", "0" * 64),
        "option-substitution": ("selected_option", "option_id", "L4PAPP-2"),
        "runtime-activation-escalation": ("downstream_authority", "runtime_activated", True),
        "cutover-escalation": ("downstream_authority", "cutover_authorized", True),
        "approval-effect-escalation": ("selected_option", "effect", "external-effect"),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        if probe_id == "candidate-digest-substitution":
            caught = caught or (
                mutated["candidate_refs"]["product_candidate_sha256"]
                != digest(artifacts["product_candidate"])
            )
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(probe["result"] == "PASS" for probe in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-l4-product-approval-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "stage_state": "PRODUCT_APPROVED" if result == "PASS" else "not_evaluable",
        "checks": checks,
        "failed_checks": failed,
        "product_candidate_id": refs.get("product_candidate_id"),
        "product_candidate_sha256": refs.get("product_candidate_sha256"),
        "product_test_evidence_sha256": refs.get("product_test_evidence_sha256"),
        "product_approval": "approved" if result == "PASS" else "not_evaluable",
        "adapter_admitted": False,
        "implementation_admitted": False,
        "runtime_activated": False,
        "live_execution_ready": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "publication_authorized": False,
        "deployment_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "product-approval-only" if result == "PASS" else "none",
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (
                DECISION, SCHEMA, request_path, receipt_path,
                artifacts["product_candidate"], artifacts["product_test_evidence"],
                artifacts["approval_request"], artifacts["packet_validation"],
                HERE / "APPROVAL.md", HERE / "validate-decision.py",
            )
        ],
        "claim_ceiling": "PASS proves only that the product owner selected L4PAPP-1 for the exact frozen tested L4 product. It grants no adapter, implementation, or ontology admission, governed runtime activation, live execution, migration, cutover, publication, release, deployment, credential, destructive action, or external effect.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        key: validation[key]
        for key in (
            "decision_id", "gate_id", "result", "failed_checks", "stage_state",
            "product_approval", "adapter_admitted", "runtime_activated",
            "live_execution_ready", "cutover_authorized",
            "external_effect_authorized", "authority_effect",
        )
    }, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
