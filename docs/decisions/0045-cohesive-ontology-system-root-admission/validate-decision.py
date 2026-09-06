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
RECEIPT = HERE / "receipts" / "decision-validation.json"
CANDIDATE_VALIDATOR = HERE / "validate.py"
EXPECTED_OPTIONS = {"CLOSYS-ADM-1", "CLOSYS-ADM-2", "CLOSYS-ADM-3", "CLOSYS-ADM-4"}
EXPECTED_REFS = {
    "admission_candidate": "ef3c79eb6bb662fa024c5fc0375fca242aa6b75e37483eae88362d33d7f69895",
    "candidate_validation": "93685c53e648e881d646fd07e3e357e78c9a7c906d4c5b90de5800dc9a431e02",
    "product_approval_decision": "1e490e296f0e497268fe5da88c95b150f7b5802148379e73fd19fafe93ab2b18",
    "product_approval_validation": "ad8afc5bc9669db9c17ac58b86d44438502be49a5163dc08d0b12e43c7dcf79b",
    "ontology_system": "977ab3235bc52b3feddc2e8c4e7103349d763ab802f5982534ac409fd1e2c8c9",
}
EXPECTED_RESIDUE = {
    "CAL-RES-DOMAINSPEC-SUCCESSOR-COLLISION",
    "CAL-RES-ONTOLOGY-REVIEWS-BLOCKED",
    "CAL-RES-ONTOLOGY-PACKAGE-TYPE-UNADMITTED",
    "CAL-RES-PRODUCT-RUNTIME-REALIZATION-UNPROVEN",
    "CAL-RES-STALE-STATUS-PROJECTION",
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
        "kind": "explicit-user-selection",
        "verbatim": "`CLOSYS-ADM-1`",
        "selected_option_id": "CLOSYS-ADM-1",
        "observed_count": 1,
    }:
        errors.append("explicit CLOSYS-ADM-1 owner selection is absent")
    if decision.get("selected_option") != {"option_id": "CLOSYS-ADM-1", "effect": "root-admission-only"}:
        errors.append("selected option is not exact CLOSYS-ADM-1")
    if set(decision.get("alternatives", [])) != {"CLOSYS-ADM-2", "CLOSYS-ADM-3", "CLOSYS-ADM-4"}:
        errors.append("alternatives are incomplete")

    admission = decision.get("root_admission", {})
    required_admission = {
        "state": "admitted",
        "root_component_id": "CAL-LAB-ONTOLOGY-SYSTEM",
        "root_system_id": "cal.ontology-system.lab-cohesion",
        "ontology_type": "business-system-bridge",
        "scope": "exact cohesive root and 15-relation composition overlay over the approved ontology-system bytes only",
        "candidate_identity": EXPECTED_REFS["admission_candidate"],
        "ontology_system_identity": EXPECTED_REFS["ontology_system"],
        "component_count": 14,
        "relation_count": 15,
        "catalog_package_count": 20,
        "review_group_count": 10,
        "navigation_authority": True,
        "composition_overlay_authority": True,
        "replay_source": False,
    }
    if any(admission.get(key) != value for key, value in required_admission.items()):
        errors.append("root admission identity or scope is not exact")

    preserved = decision.get("preserved_child_authority", {})
    expected_preserved = {
        "already_admitted_components_remain_admitted": 8,
        "approved_not_admitted_components_remain_approved_not_admitted": 1,
        "accepted_not_admitted_components_remain_accepted_not_admitted": 1,
        "candidate_only_components_remain_candidate_only": 4,
        "child_ontologies_admitted_by_this_decision": 0,
        "owner_routes_transferred": 0,
        "domainspec_profiles_selected": 0,
    }
    if preserved != expected_preserved:
        errors.append("child authority states are not exactly preserved")

    truth = decision.get("canonical_truth_boundary", {})
    if truth.get("root_is_replay_source") is not False or "event histories" not in truth.get("canonical", ""):
        errors.append("canonical event-history truth boundary is not preserved")
    if set(decision.get("retained_residue_ids", [])) != EXPECTED_RESIDUE:
        errors.append("typed residue set is incomplete")

    downstream = decision.get("downstream_authority", {})
    if downstream.get("cohesive_root_admitted") is not True:
        errors.append("cohesive root admission was not recorded")
    required_false = set(downstream) - {
        "cohesive_root_admitted",
        "separate_child_and_operational_decisions_required",
    }
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream authority ceiling is violated")
    if downstream.get("separate_child_and_operational_decisions_required") is not True:
        errors.append("separate child and operational decisions are not preserved")
    if decision.get("authority_effect") != "root-admission-only":
        errors.append("authority effect exceeds root admission")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if not DECISION.is_file():
        print(json.dumps({
            "decision_id": "CAL-ONTOLOGY-SYSTEM-ROOT-ADMISSION-0045",
            "gate_id": "G-CAL-COHESIVE-ONTOLOGY-SYSTEM-ROOT-ADMISSION",
            "result": "BLOCK",
            "failed_checks": ["explicit-owner-selection-absent"],
            "stage_state": "ROOT_ADMISSION_CANDIDATE_READY",
            "cohesive_root_admitted": False,
            "authority_effect": "none",
        }, indent=2))
        return 1

    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [
        error.message
        for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(decision)
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
        request, receipt = load(request_path), load(receipt_path)
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
        if refs.get(f"{name}_sha256") != expected or not path.is_file() or digest(path) != expected:
            ref_failures.append(f"{name}-digest-mismatch")
    add("immutable-admission-refs", not ref_failures, ref_failures)

    candidate = load(artifacts["admission_candidate"])
    candidate_validation = load(artifacts["candidate_validation"])
    product_decision = load(artifacts["product_approval_decision"])
    product_validation = load(artifacts["product_approval_validation"])
    model = load(artifacts["ontology_system"])
    closure = (
        candidate.get("candidate_id") == refs.get("admission_candidate_id")
        and candidate.get("status") == "frozen-awaiting-owner-decision"
        and candidate.get("decision_state") == "not-decided"
        and candidate.get("authority_effect") == "none"
        and candidate_validation.get("result") == "PASS"
        and candidate_validation.get("decision_gate_ready") is True
        and candidate_validation.get("root_admission_authorized") is False
        and product_decision.get("selected_option", {}).get("option_id") == "CLOSYS-PAPP-1"
        and product_validation.get("stage_state") == "PRODUCT_APPROVED"
        and product_validation.get("cohesive_root_admitted") is False
        and len(model.get("components", [])) == 14
        and len(model.get("relations", [])) == 15
        and [item.get("relation_id") for item in model.get("relations", [])]
        == candidate.get("admission_scope", {}).get("relation_ids")
    )
    add("candidate-product-and-model-closure", closure, {
        "candidate": candidate_validation.get("result"),
        "product_approval": product_validation.get("result"),
        "components": len(model.get("components", [])),
        "relations": len(model.get("relations", [])),
    })

    live_validation = subprocess.run(
        [sys.executable, str(CANDIDATE_VALIDATOR)],
        cwd=LAB,
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
        "current-candidate-validation",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("candidate_sha256") == EXPECTED_REFS["admission_candidate"]
        and live_summary.get("decision_gate_ready") is True,
        {"exit": live_validation.returncode, "summary": live_summary, "tail": live_validation.stdout[-2000:] if live_validation.returncode else ""},
    )

    semantics = semantic_errors(decision)
    add("owner-selection-and-claim-ceiling", not semantics, semantics)

    projection = (HERE / "DECISION.md").read_text(encoding="utf-8") if (HERE / "DECISION.md").is_file() else ""
    projection_markers = [
        "CAL-ONTOLOGY-SYSTEM-ROOT-ADMISSION-0045",
        "CLOSYS-ADM-1",
        "CAL-LAB-ONTOLOGY-SYSTEM",
        EXPECTED_REFS["admission_candidate"],
        "Child ontologies admitted by this decision: `0`",
        "No runtime adoption",
    ]
    add("human-projection", all(marker in projection for marker in projection_markers), {"missing": [marker for marker in projection_markers if marker not in projection]})

    probes = []
    mutations = {
        "candidate-digest-substitution": ("candidate_refs", "admission_candidate_sha256", "0" * 64),
        "option-substitution": ("selected_option", "option_id", "CLOSYS-ADM-2"),
        "root-identity-substitution": ("root_admission", "root_system_id", "cal.ontology-system.other"),
        "child-admission-escalation": ("preserved_child_authority", "child_ontologies_admitted_by_this_decision", 1),
        "domainspec-selection-escalation": ("preserved_child_authority", "domainspec_profiles_selected", 1),
        "replay-source-collapse": ("canonical_truth_boundary", "root_is_replay_source", True),
        "runtime-adoption-escalation": ("downstream_authority", "runtime_adopted", True),
        "migration-escalation": ("downstream_authority", "migration_authorized", True),
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
        "schema_version": "cyberalchemy-lab-cohesive-ontology-system-root-admission-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "stage_state": "ROOT_ADMITTED" if result == "PASS" else "not_evaluable",
        "checks": checks,
        "failed_checks": failed,
        "admission_candidate_id": refs.get("admission_candidate_id"),
        "admission_candidate_sha256": refs.get("admission_candidate_sha256"),
        "candidate_validation_sha256": refs.get("candidate_validation_sha256"),
        "root_component_id": decision.get("root_admission", {}).get("root_component_id"),
        "root_system_id": decision.get("root_admission", {}).get("root_system_id"),
        "root_admission": "admitted" if result == "PASS" else "not_evaluable",
        "cohesive_root_admitted": result == "PASS",
        "child_ontologies_admitted_by_this_decision": 0,
        "runtime_adopted": False,
        "activated": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "publication_authorized": False,
        "deployment_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "root-admission-only" if result == "PASS" else "none",
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (
                DECISION,
                SCHEMA,
                request_path,
                receipt_path,
                artifacts["admission_candidate"],
                artifacts["candidate_validation"],
                artifacts["product_approval_decision"],
                artifacts["product_approval_validation"],
                artifacts["ontology_system"],
                HERE / "DECISION.md",
                HERE / "validate-decision.py",
            )
        ],
        "claim_ceiling": "PASS proves only that the owner selected CLOSYS-ADM-1 and admitted the exact Product-approved cohesive root and composition overlay as an authoritative navigation layer. Every child authority state remains unchanged, and no runtime adoption, activation, migration, cutover, publication, release, deployment, source retirement, credential, destructive action, or external effect is authorized or performed.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation if not args.write_receipt else {
        key: validation[key]
        for key in (
            "decision_id",
            "gate_id",
            "result",
            "failed_checks",
            "stage_state",
            "root_component_id",
            "root_system_id",
            "root_admission",
            "cohesive_root_admitted",
            "child_ontologies_admitted_by_this_decision",
            "runtime_adopted",
            "activated",
            "migration_authorized",
            "cutover_authorized",
            "external_effect_authorized",
            "authority_effect",
        )
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
