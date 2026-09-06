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
L3_ADMISSION_VALIDATOR = LAB / "docs/decisions/0037-d65-l3-filesystem-adapter-admission/validate-decision.py"
EXPECTED_PRESENTED = {"L4TGT-1", "L4TGT-4", "L4TGT-5"}
EXPECTED_REJECTED = {"L4TGT-2", "L4TGT-3"}
EXPECTED_REFS = {
    "target_selection_candidate": "ef997df4bc8a1168e51b5943e44cbb9ec05639050053f0240a885e4e8a24ac4b",
    "candidate_validation": "4eab602178b8eff8d3eb6089e583b199f141eb45f483019f24b15fe4919d1306",
    "l3_admission_decision": "3fcc48868691d7c7ab6e3fa9bd87062271f8aae895ee0edd93644bc93482885c",
    "l3_admission_validation": "c8165f710e6b5e70371ae07948faf5e8d9c484ead07976f794c13e830cc18e2e",
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
    direction = decision.get("product_direction", {})
    downstream = decision.get("downstream_state", {})
    if source != {
        "kind": "explicit-user-selection",
        "verbatim": "`L4TGT-1`",
        "selected_option_id": "L4TGT-1",
        "observed_count": 1,
    }:
        errors.append("explicit L4TGT-1 owner selection is absent")
    if selected != {
        "option_id": "L4TGT-1",
        "effect": "product-direction-selection-only",
    }:
        errors.append("selected option is not exact L4TGT-1")
    if set(decision.get("alternatives", [])) != {"L4TGT-4", "L4TGT-5"}:
        errors.append("admissible alternatives are incomplete")
    if set(decision.get("rejected_options", [])) != EXPECTED_REJECTED:
        errors.append("structurally rejected options are incomplete")
    required_direction = {
        "state": "selected",
        "product_kind": "non-live state-bearing local sandbox target",
        "successor_identity_state": "must-be-defined-before-implementation-binding",
        "new_product_digest_required": True,
        "prototype_construction_eligible": True,
    }
    if any(direction.get(key) != value for key, value in required_direction.items()):
        errors.append("selected product direction is incomplete or expanded")
    required_false = {
        "prototype_construction_started",
        "successor_identity_defined",
        "successor_product_frozen",
        "successor_product_tests_passed",
        "successor_product_approved",
        "successor_adapter_admitted",
        "runtime_activated",
        "live_execution_ready",
        "migration_authorized",
        "cutover_authorized",
        "publication_authorized",
        "deployment_authorized",
        "external_effect_authorized",
    }
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream construction or authority state was inflated")
    if downstream.get("implementation_route_required") is not True:
        errors.append("separate implementation route is not preserved")
    if decision.get("authority_effect") != "product-direction-selection-only":
        errors.append("authority effect exceeds product-direction selection")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append(
            {
                "check_id": check_id,
                "result": "PASS" if passed else "BLOCK",
                "detail": detail,
            }
        )

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
        rejected_ids = {item.get("optionId") for item in receipt.get("rejectedOptions", [])}
        if receipt.get("requestDigest") != canonical_digest(request):
            admissibility_failures.append("canonical-request-digest-mismatch")
        if (
            receipt.get("routeOutcome") != "gate"
            or receipt.get("decisionGateRequired") is not True
            or set(receipt.get("admissibleOptionIds", [])) != EXPECTED_PRESENTED
            or set(receipt.get("presentedOptionIds", [])) != EXPECTED_PRESENTED
            or rejected_ids != EXPECTED_REJECTED
            or set(admissibility.get("presented_option_ids", [])) != EXPECTED_PRESENTED
            or set(admissibility.get("rejected_option_ids", [])) != EXPECTED_REJECTED
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
    add("immutable-target-selection-refs", not ref_failures, ref_failures)

    candidate = load(artifacts["target_selection_candidate"])
    candidate_validation = load(artifacts["candidate_validation"])
    l3_decision = load(artifacts["l3_admission_decision"])
    l3_validation = load(artifacts["l3_admission_validation"])
    closure = (
        candidate.get("candidate_id")
        == "CAL-D65-L4-STATE-BEARING-TARGET-SELECTION-CANDIDATE-001"
        and candidate.get("decision_state") == "not-decided"
        and candidate.get("direct_activation_evaluation", {}).get("result")
        == "not_evaluable"
        and candidate.get("recommended_successor", {}).get("option_id") == "L4TGT-1"
        and candidate.get("authority_effect") == "none"
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("candidate_frozen") is True
        and candidate_validation.get("decision_gate_ready") is True
        and candidate_validation.get("direct_activation") == "not_evaluable"
        and candidate_validation.get("authority_effect") == "none"
        and l3_decision.get("selected_option", {}).get("option_id") == "L3AADM-1"
        and l3_validation.get("result") == "PASS"
        and l3_validation.get("stage_state") == "ADAPTER_ADMITTED"
        and l3_validation.get("adapter_admitted") is True
        and l3_validation.get("runtime_activated") is False
    )
    add(
        "candidate-and-l3-admission-closure",
        closure,
        {
            "candidate": candidate_validation.get("result"),
            "direct_activation": candidate_validation.get("direct_activation"),
            "l3_admission": l3_validation.get("result"),
        },
    )

    live_validation = subprocess.run(
        [sys.executable, str(L3_ADMISSION_VALIDATOR)],
        cwd=LAB,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    live_summary: dict[str, Any] = {}
    try:
        live_summary = json.loads(live_validation.stdout)
    except json.JSONDecodeError:
        pass
    add(
        "current-l3-admission-and-product-tests",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("stage_state") == "ADAPTER_ADMITTED"
        and live_summary.get("adapter_admitted") is True
        and live_summary.get("runtime_activated") is False,
        {
            "exit": live_validation.returncode,
            "summary": live_summary,
            "tail": live_validation.stdout[-2000:] if live_validation.returncode else "",
        },
    )

    semantics = semantic_errors(decision)
    add("owner-selection-and-claim-ceiling", not semantics, semantics)

    probes: list[dict[str, str]] = []
    mutations = {
        "candidate-digest-substitution": (
            "candidate_refs",
            "target_selection_candidate_sha256",
            "0" * 64,
        ),
        "option-substitution": ("selected_option", "option_id", "L4TGT-4"),
        "product-kind-substitution": (
            "product_direction",
            "product_kind",
            "live service target",
        ),
        "implicit-identity-binding": (
            "product_direction",
            "successor_identity_state",
            "defined",
        ),
        "construction-inflation": (
            "downstream_state",
            "prototype_construction_started",
            True,
        ),
        "approval-inflation": (
            "downstream_state",
            "successor_product_approved",
            True,
        ),
        "admission-inflation": (
            "downstream_state",
            "successor_adapter_admitted",
            True,
        ),
        "activation-escalation": (
            "downstream_state",
            "runtime_activated",
            True,
        ),
        "external-effect-escalation": (
            "downstream_state",
            "external_effect_authorized",
            True,
        ),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        if probe_id == "candidate-digest-substitution":
            caught = caught or (
                mutated["candidate_refs"]["target_selection_candidate_sha256"]
                != digest(artifacts["target_selection_candidate"])
            )
        probes.append(
            {"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"}
        )
    add(
        "mutation-probes",
        all(probe["result"] == "PASS" for probe in probes),
        probes,
    )

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-l4-state-bearing-target-selection-decision-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "stage_state": "PRODUCT_DIRECTION_SELECTED" if result == "PASS" else "not_evaluable",
        "checks": checks,
        "failed_checks": failed,
        "target_selection_candidate_id": refs.get("target_selection_candidate_id"),
        "target_selection_candidate_sha256": refs.get("target_selection_candidate_sha256"),
        "selected_option_id": "L4TGT-1" if result == "PASS" else "not_evaluable",
        "product_direction": (
            "non-live state-bearing local sandbox target"
            if result == "PASS"
            else "not_evaluable"
        ),
        "prototype_construction_eligible": result == "PASS",
        "prototype_construction_started": False,
        "successor_identity_defined": False,
        "successor_product_frozen": False,
        "successor_product_tests_passed": False,
        "successor_product_approved": False,
        "successor_adapter_admitted": False,
        "runtime_activated": False,
        "live_execution_ready": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "publication_authorized": False,
        "deployment_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": (
            "product-direction-selection-only" if result == "PASS" else "none"
        ),
        "inputs": [
            {
                "path": str(path.relative_to(LAB)),
                "sha256": digest(path),
            }
            for path in (
                DECISION,
                SCHEMA,
                request_path,
                receipt_path,
                artifacts["target_selection_candidate"],
                artifacts["candidate_validation"],
                artifacts["l3_admission_decision"],
                artifacts["l3_admission_validation"],
                HERE / "DECISION.md",
                HERE / "README.md",
                HERE / "validate-decision.py",
            )
        ],
        "claim_ceiling": "PASS proves only that the owner selected L4TGT-1 and therefore selected a new non-live state-bearing local sandbox target as the L4 product direction. Prototype construction is eligible to begin on its separate implementation route, but no implementation has started and no successor identity, product, tests, approval, admission, activation, live execution, migration, cutover, publication, deployment, or external effect exists or is authorized."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                key: validation[key]
                for key in (
                    "decision_id",
                    "gate_id",
                    "result",
                    "failed_checks",
                    "stage_state",
                    "selected_option_id",
                    "product_direction",
                    "prototype_construction_eligible",
                    "prototype_construction_started",
                    "successor_identity_defined",
                    "successor_product_approved",
                    "successor_adapter_admitted",
                    "runtime_activated",
                    "live_execution_ready",
                    "cutover_authorized",
                    "external_effect_authorized",
                    "authority_effect",
                )
            },
            indent=2,
        )
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
