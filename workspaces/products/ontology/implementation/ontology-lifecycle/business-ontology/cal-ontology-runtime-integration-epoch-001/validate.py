#!/usr/bin/env python3
"""Validate the D65-S3 capability-local business-ontology candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CORE = LAB.parent / "domainspec-core"
PROFILE = HERE / "profile.json"
SOURCES = HERE / "sources.json"
NODES = HERE / "nodes.json"
RELATIONS = HERE / "relations.json"
CONTRACTS = HERE / "contracts.json"
POLICIES = HERE / "policies.json"
WORKFLOWS = HERE / "workflows.json"
FAILURES = HERE / "failures.json"
RESIDUE = HERE / "residue.json"
SCHEMA = HERE / "schema.json"
README = HERE / "README.md"
REQUEST = HERE / "owner-decision-request.json"
RECEIPT = HERE / "receipts/validation.json"

ONTOLOGY_ID = "CAL-ONTOLOGY-ONTOLOGY-RUNTIME-INTEGRATION-BUSINESS"
CAPABILITY_ID = "CA2-CAP-CONSUME-GOVERNED-EVENT-CALCULATED-ONTOLOGY-PROJECTIONS"
EXPECTED_ROLE_COUNTS = {
    "actor": 3,
    "business_rule": 5,
    "capability": 1,
    "domain_concept": 9,
    "outcome": 3,
    "policy": 3,
    "workflow": 2,
}
EXPECTED_CONTRACT_DEFINITIONS = {
    "CAL-HDEF-INTEGRATION-BUSINESS-SYSTEM-BRIDGE",
    "CAL-HDEF-INTEGRATION-CONTEXT-SELECTOR",
    "CAL-HDEF-INTEGRATION-CANONICAL-EVENT-CUT",
    "CAL-HDEF-INTEGRATION-EVENT-CALCULATED-PROJECTION",
    "CAL-HDEF-INTEGRATION-CONTEXT-PROJECTION-BINDING",
    "CAL-HDEF-INTEGRATION-CHALLENGE-ROUTE",
    "CAL-HDEF-INTEGRATION-EPOCH",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_root(raw: str) -> Path:
    if raw == str(CORE):
        return CORE
    if raw == str(LAB):
        return LAB
    raise ValueError(f"unregistered repository: {raw}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    documents = {
        "profile": load(PROFILE),
        "sources": load(SOURCES),
        "nodes": load(NODES),
        "relations": load(RELATIONS),
        "contracts": load(CONTRACTS),
        "policies": load(POLICIES),
        "workflows": load(WORKFLOWS),
        "failures": load(FAILURES),
        "residue": load(RESIDUE),
        "decision_request": load(REQUEST),
    }
    schema = load(SCHEMA)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_failures: dict[str, list[str]] = {}
    for name, document in documents.items():
        errors = [error.message for error in Draft202012Validator(schema["$defs"][name]).iter_errors(document)]
        if errors:
            schema_failures[name] = errors
    record("package-schema", not schema_failures, schema_failures or {"documents": sorted(documents)})

    profile = documents["profile"]
    record(
        "business-domain-package-profile",
        profile.get("ontology_id") == ONTOLOGY_ID
        and profile.get("ontology_type") == "business-domain"
        and profile.get("branch") == "business"
        and profile.get("materialization") == "package-required"
        and profile.get("candidate_status") == "validated-candidate-awaiting-owner-admission"
        and profile.get("owner_gate") == "G-D65-BUSINESS"
        and profile.get("authority_effect") == "none",
        {
            "ontology_id": profile.get("ontology_id"),
            "type": profile.get("ontology_type"),
            "branch": profile.get("branch"),
            "gate": profile.get("owner_gate"),
        },
    )

    source_items = documents["sources"].get("sources", [])
    source_ids = [item.get("source_id") for item in source_items]
    source_failures: list[dict[str, str]] = []
    for source in source_items:
        source_id = str(source.get("source_id"))
        try:
            path = repository_root(str(source.get("repository"))) / str(source.get("path"))
        except ValueError as error:
            source_failures.append({"source_id": source_id, "failure": str(error)})
            continue
        if not path.is_file():
            source_failures.append({"source_id": source_id, "failure": "missing"})
            continue
        mode = source.get("currentness_mode")
        if mode == "whole-file":
            if digest(path) != source.get("sha256"):
                source_failures.append({"source_id": source_id, "failure": "digest-drift"})
        elif mode == "plan-preimage":
            expected = source.get("sha256")
            current_plan = load(path)
            carried = current_plan.get("selected_dependencies", {}).get("business_ontology_profile", {}).get("sha256")
            descendant = current_plan.get("revision", 0) >= 8 and carried == digest(PROFILE)
            if digest(path) != expected and current_plan.get("supersedes_plan_sha256") != expected and not descendant:
                source_failures.append({"source_id": source_id, "failure": "preimage-not-in-current-plan-chain"})
        else:
            source_failures.append({"source_id": source_id, "failure": f"unsupported-currentness-mode:{mode}"})
    record(
        "selected-source-currentness",
        len(source_items) == 8 and len(source_ids) == len(set(source_ids)) and not source_failures,
        {"source_count": len(source_items), "failures": source_failures},
    )

    product_decision = load(LAB / "docs/decisions/0016-d65-product-ontology-admission/decision.json")
    plan = load(LAB / "docs/plans/0003-d65-native-ontology-integration/d65-plan.json")
    stage_by_id = {item.get("stage_id"): item for item in plan.get("stages", [])}
    predecessor = profile.get("predecessor", {})
    record(
        "admitted-product-predecessor",
        product_decision.get("status") == "selected"
        and product_decision.get("decision_source", {}).get("token") == "D65PROD-1"
        and product_decision.get("next_gate") == "G-D65-BUSINESS"
        and predecessor.get("owner_decision_ref") == product_decision.get("decision_id")
        and predecessor.get("gate_state") == "PASS"
        and stage_by_id.get("D65-S2", {}).get("state") == "PASS"
        and stage_by_id.get("D65-S3", {}).get("state") == "BLOCK",
        {
            "decision_id": product_decision.get("decision_id"),
            "selection": product_decision.get("decision_source", {}).get("token"),
            "s2": stage_by_id.get("D65-S2", {}).get("state"),
            "s3": stage_by_id.get("D65-S3", {}).get("state"),
        },
    )

    nodes = documents["nodes"].get("nodes", [])
    node_by_id = {item.get("id"): item for item in nodes}
    role_counts = {role: sum(item.get("role") == role for item in nodes) for role in EXPECTED_ROLE_COUNTS}
    node_failures = [
        str(item.get("id"))
        for item in nodes
        if item.get("role") not in EXPECTED_ROLE_COUNTS
        or item.get("authority_effect") != "none"
        or not item.get("source_refs")
        or not set(item.get("source_refs", [])).issubset(set(source_ids))
        or not item.get("owner_route")
        or not item.get("challenge_route")
        or item.get("evidence_confidence") not in {"low", "medium", "high"}
        or item.get("commitment_confidence") not in {"open", "conditional", "committed"}
        or not item.get("forbidden_inference")
    ]
    record(
        "business-node-model-closure",
        len(nodes) == 26 and len(node_by_id) == 26 and role_counts == EXPECTED_ROLE_COUNTS and not node_failures,
        {"node_count": len(nodes), "role_counts": role_counts, "failures": node_failures},
    )

    vocabulary = documents["relations"].get("relation_vocabulary", [])
    vocabulary_by_type = {item.get("type"): item for item in vocabulary}
    relations = documents["relations"].get("relations", [])
    relation_ids = [item.get("id") for item in relations]
    relation_failures: list[str] = []
    for relation in relations:
        relation_type = vocabulary_by_type.get(relation.get("type"), {})
        source = node_by_id.get(relation.get("source"), {})
        target = node_by_id.get(relation.get("target"), {})
        if (
            not source
            or not target
            or source.get("role") not in relation_type.get("source_roles", [])
            or target.get("role") not in relation_type.get("target_roles", [])
            or not set(relation.get("source_refs", [])).issubset(set(source_ids))
            or relation.get("authority_effect") != "none"
        ):
            relation_failures.append(str(relation.get("id")))
    record(
        "typed-relation-endpoint-closure",
        len(vocabulary) == len(vocabulary_by_type) == 12
        and len(relations) == len(set(relation_ids)) == 35
        and not relation_failures,
        {"vocabulary_count": len(vocabulary), "relation_count": len(relations), "failures": relation_failures},
    )

    handled = load(LAB / "ontology-lifecycle/definitions/cal-ontology-runtime-integration-epoch-001/handled-definitions.json")
    handled_ids = {item.get("record_id") for item in handled.get("records", [])}
    contracts = documents["contracts"].get("contracts", [])
    contract_by_id = {item.get("contract_id"): item for item in contracts}
    contract_failures = [
        str(item.get("contract_id"))
        for item in contracts
        if item.get("subject_ref") not in node_by_id
        or item.get("handled_definition_ref") not in handled_ids
        or not item.get("required_fields")
        or not item.get("invariants")
        or not item.get("allowed_readings")
        or not item.get("forbidden_collapses")
        or not item.get("owner_route")
        or not item.get("challenge_route")
        or not set(item.get("source_refs", [])).issubset(set(source_ids))
        or item.get("authority_effect") != "none"
    ]
    record(
        "business-contract-closure",
        len(contracts) == len(contract_by_id) == 8
        and {item.get("handled_definition_ref") for item in contracts} == EXPECTED_CONTRACT_DEFINITIONS
        and not contract_failures,
        {"contract_count": len(contracts), "definition_refs": sorted({item.get("handled_definition_ref") for item in contracts}), "failures": contract_failures},
    )

    bridge = contract_by_id.get("CAL-BIZ-CONTRACT-BUSINESS-SYSTEM-BRIDGE", {})
    relation_text = json.dumps(relations, sort_keys=True)
    record(
        "nonvacuous-bridge-boundary",
        bridge.get("instantiation_state") == "contract-defined-no-system-endpoint-or-realization-claimed"
        and len(bridge.get("business_endpoint_requirements", [])) >= 4
        and len(bridge.get("future_system_endpoint_requirements", [])) >= 5
        and any("every endpoint resolves" in item for item in bridge.get("invariants", []))
        and "realized_by" not in vocabulary_by_type
        and "system-runtime component" not in relation_text
        and any(item.get("failure_id") == "CAL-BIZ-FAIL-SYSTEM-ENDPOINT-UNAVAILABLE" for item in documents["failures"].get("failures", [])),
        {
            "instantiation_state": bridge.get("instantiation_state"),
            "business_requirements": len(bridge.get("business_endpoint_requirements", [])),
            "future_system_requirements": len(bridge.get("future_system_endpoint_requirements", [])),
            "realization_relation_present": "realized_by" in vocabulary_by_type,
        },
    )

    failures = documents["failures"].get("failures", [])
    failure_by_id = {item.get("failure_id"): item for item in failures}
    residues = documents["residue"].get("residue", [])
    residue_by_id = {item.get("id"): item for item in residues}
    failure_failures = [
        str(item.get("failure_id"))
        for item in failures
        if item.get("residue_route") not in residue_by_id
        or not item.get("condition")
        or not item.get("result")
        or not item.get("blocked_successors")
        or not item.get("owner_route")
        or not item.get("challenge_route")
        or item.get("authority_effect") != "none"
    ]
    record(
        "fail-closed-outcome-closure",
        len(failures) == len(failure_by_id) == 13
        and not failure_failures
        and {
            "CAL-BIZ-FAIL-EVENT-GAP",
            "CAL-BIZ-FAIL-MIXED-CURSOR",
            "CAL-BIZ-FAIL-GOVERNANCE-JOIN",
            "CAL-BIZ-FAIL-NONCANONICAL-REPLAY-SOURCE",
            "CAL-BIZ-FAIL-NONDETERMINISTIC-PROJECTION",
            "CAL-BIZ-FAIL-SYSTEM-ENDPOINT-UNAVAILABLE",
        }.issubset(set(failure_by_id)),
        {"failure_count": len(failures), "failures": failure_failures},
    )

    policies = documents["policies"].get("policies", [])
    policy_by_id = {item.get("policy_id"): item for item in policies}
    policy_failures = [
        str(item.get("policy_id"))
        for item in policies
        if item.get("subject_ref") not in node_by_id
        or not set(item.get("requires", [])).issubset(set(contract_by_id))
        or not set(item.get("on_failure_refs", [])).issubset(set(failure_by_id))
        or not item.get("collect_all_checks")
        or item.get("authority_effect") != "none"
    ]
    record("policy-closure", len(policies) == len(policy_by_id) == 3 and not policy_failures, {"policy_count": len(policies), "failures": policy_failures})

    workflows = documents["workflows"].get("workflows", [])
    workflow_by_id = {item.get("workflow_id"): item for item in workflows}
    workflow_failures: list[str] = []
    for workflow in workflows:
        if workflow.get("subject_ref") not in node_by_id or workflow.get("authority_effect") != "none":
            workflow_failures.append(str(workflow.get("workflow_id")))
            continue
        if not set(workflow.get("failure_refs", [])).issubset(set(failure_by_id)):
            workflow_failures.append(str(workflow.get("workflow_id")))
        if not set(workflow.get("success_outcome_refs", []) + [workflow.get("failure_outcome_ref")]).issubset(set(node_by_id)):
            workflow_failures.append(str(workflow.get("workflow_id")))
        for step in workflow.get("steps", []):
            refs = (
                set(step.get("requires_contract_refs", []))
                | ({step.get("requires_policy_ref")} if step.get("requires_policy_ref") else set())
                | set(step.get("requires_rule_refs", []))
            )
            if not refs.issubset(set(contract_by_id) | set(policy_by_id) | set(node_by_id)):
                workflow_failures.append(f"{workflow.get('workflow_id')}:{step.get('step_id')}")
    record("workflow-closure", len(workflows) == len(workflow_by_id) == 2 and not workflow_failures, {"workflow_count": len(workflows), "failures": workflow_failures})

    residue_failures = [
        str(item.get("id"))
        for item in residues
        if not set(item.get("subject_refs", [])).issubset(set(node_by_id))
        or not set(item.get("source_refs", [])).issubset(set(source_ids))
        or item.get("status") not in {"blocked", "deferred", "owner-review", "open"}
    ]
    record(
        "residue-and-successor-closure",
        len(residues) == len(residue_by_id) == 5
        and not residue_failures
        and residue_by_id.get("CAL-BIZ-RES-OWNER-ADMISSION", {}).get("acceptance_critical") is True
        and residue_by_id.get("CAL-BIZ-RES-FUTURE-SYSTEM-ENDPOINT", {}).get("status") == "deferred"
        and residue_by_id.get("CAL-BIZ-RES-DOMAINSPEC-SOURCE", {}).get("status") == "blocked",
        {"residue_count": len(residues), "failures": residue_failures},
    )

    request = documents["decision_request"]
    candidate_refs = request.get("candidate_refs", {})
    expected_ref_hashes = {
        "profile_sha256": digest(PROFILE),
        "sources_sha256": digest(SOURCES),
        "nodes_sha256": digest(NODES),
        "relations_sha256": digest(RELATIONS),
        "contracts_sha256": digest(CONTRACTS),
        "policies_sha256": digest(POLICIES),
        "workflows_sha256": digest(WORKFLOWS),
        "failures_sha256": digest(FAILURES),
        "residue_sha256": digest(RESIDUE),
        "schema_sha256": digest(SCHEMA),
        "readme_sha256": digest(README),
        "validator_sha256": digest(Path(__file__)),
    }
    record(
        "owner-decision-gate-prepared",
        request.get("request_id") == "CAL-D65BIZ-REQUEST-001"
        and request.get("gate_id") == "G-D65-BUSINESS"
        and request.get("status") == "pending-owner-admission"
        and candidate_refs == expected_ref_hashes
        and {item.get("option_id") for item in request.get("options", [])} == {"D65BIZ-1", "D65BIZ-2", "D65BIZ-3", "D65BIZ-4"}
        and request.get("authority_effect") == "none",
        {"request_status": request.get("status"), "candidate_hashes_match": candidate_refs == expected_ref_hashes},
    )

    blocked = profile.get("blocked_outputs", [])
    record(
        "direct-d65-authority-boundary",
        profile.get("authority_effect") == "none"
        and any("Invoke" in item for item in blocked)
        and any("D65-S4" in item for item in blocked)
        and any("Rust" in item for item in blocked)
        and stage_by_id.get("D65-S4", {}).get("state") == "not_evaluable"
        and plan.get("execution", {}).get("authorized") is False,
        {"blocked_output_count": len(blocked), "d65_s4": stage_by_id.get("D65-S4", {}).get("state"), "execution_authorized": plan.get("execution", {}).get("authorized")},
    )

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.business-ontology-validation/v1",
        "ontology_id": profile.get("ontology_id"),
        "result": result,
        "gate_id": "G-D65-BUSINESS",
        "gate_state": "BLOCK",
        "gate_blocker": "Ontology integration business-ontology owner admission is pending." if result == "PASS" else "Business-ontology candidate validation failed.",
        "checks": checks,
        "failed_checks": failed,
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (PROFILE, SOURCES, NODES, RELATIONS, CONTRACTS, POLICIES, WORKFLOWS, FAILURES, RESIDUE, SCHEMA, README, REQUEST, Path(__file__))
        ],
        "authority_effect": "none",
        "claim_ceiling": "PASS proves only candidate business meaning, endpoint and relation closure, contract and workflow completeness, fail-closed outcomes, nonvacuous future-system boundary, selected-source currentness, and a prepared owner gate. It does not admit D65-S3, make D65-S4 eligible, author DomainSpec source, realize a bridge, implement, migrate, cut over, publish, release, deploy, or create external effects.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "ontology_id": receipt["ontology_id"],
        "result": result,
        "failed_checks": failed,
        "gate_id": receipt["gate_id"],
        "gate_state": receipt["gate_state"],
        "gate_blocker": receipt["gate_blocker"],
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
