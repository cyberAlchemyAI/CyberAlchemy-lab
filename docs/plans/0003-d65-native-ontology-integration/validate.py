#!/usr/bin/env python3
"""Validate the direct CAV2-D65 integration planning candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
PLAN_DIR = SCRIPT.parent
LAB = SCRIPT.parents[3]
CORE = LAB.parent / "domainspec-core"
SOURCE = PLAN_DIR / "d65-plan.json"
VIEW = PLAN_DIR / "PLAN.md"
RECEIPT = PLAN_DIR / "receipts/plan-validation.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definition_selector_bytes(path: Path, definition_id: str) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    selected: list[str] = []
    active = False
    for line in lines:
        if line.startswith(f"## {definition_id}:"):
            active = True
        elif active and line.startswith("## "):
            break
        if active:
            selected.append(line)
    return "".join(selected).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    plan = load(SOURCE)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    expected_chain = [
        "canonical_definitions",
        "cyberalchemy_product_ontology",
        "capability_local_business_ontology",
        "domainspec_v2_authored_source",
        "deterministic_compiled_graph",
        "system_ontology",
        "exact_implementation_binding",
        "static_conformance",
        "runtime_evidence_when_claimed",
    ]
    method = plan.get("method", {})
    record(
        "direct-d65-method",
        method.get("primary") == "CAV2-D65-direct"
        and method.get("construction_chain") == expected_chain
        and method.get("invoke_dependency") == "forbidden",
        {"primary": method.get("primary"), "invoke_dependency": method.get("invoke_dependency")},
    )

    selected = plan["selected_dependencies"]
    d65_path = CORE / selected["d65_definition"]["path"]
    selector_digest = hashlib.sha256(definition_selector_bytes(d65_path, "CAV2-D65")).hexdigest() if d65_path.is_file() else None
    dependency_failures: list[dict[str, str]] = []
    if selector_digest != selected["d65_definition"]["selector_sha256"]:
        dependency_failures.append({"dependency": "d65_definition", "failure": "selector-digest-mismatch"})
    binding_shape = CORE / selected["construction_binding_shape"]["path"]
    if not binding_shape.is_file() or digest(binding_shape) != selected["construction_binding_shape"]["sha256"]:
        dependency_failures.append({"dependency": "construction_binding_shape", "failure": "digest-mismatch"})
    for key in (
        "accepted_w8_decision",
        "accepted_w8_manifest",
        "accepted_w8_verdict",
        "context_architecture",
        "governed_node_architecture",
        "project_owner_decision",
        "source_epoch_decision",
        "source_epoch_reconciliation_validation",
        "definition_pack",
        "handled_definitions",
        "definition_validation",
        "definition_owner_request",
        "definition_owner_decision",
        "product_ontology_profile",
        "product_capability",
        "product_ontology_nodes",
        "product_ontology_relations",
        "product_ontology_residue",
        "product_ontology_validation",
        "product_ontology_owner_request",
        "product_ontology_admissibility_request",
        "product_ontology_admissibility_receipt",
        "product_ontology_owner_decision",
        "business_ontology_profile",
        "business_ontology_sources",
        "business_ontology_nodes",
        "business_ontology_relations",
        "business_ontology_contracts",
        "business_ontology_policies",
        "business_ontology_workflows",
        "business_ontology_failures",
        "business_ontology_residue",
        "business_ontology_schema",
        "business_ontology_readme",
        "business_ontology_validator",
        "business_ontology_validation",
        "business_ontology_owner_request",
        "business_ontology_admissibility_request",
        "business_ontology_admissibility_receipt",
        "business_ontology_owner_decision",
        "domainspec_source_profile",
        "domainspec_source_sources",
        "domainspec_source_business_mapping",
        "domainspec_source_event_contract",
        "domainspec_source_event_payload_schema",
        "domainspec_source_development_profile",
        "domainspec_source_profile_registry",
        "domainspec_source_project",
        "domainspec_source_feature",
        "domainspec_source_residue",
        "domainspec_source_schema",
        "domainspec_source_readme",
        "domainspec_source_validator",
        "domainspec_source_compile_check",
        "domainspec_source_hostile_checks",
        "domainspec_source_validation",
        "domainspec_source_hostile_receipt",
        "domainspec_source_owner_request",
        "domainspec_source_admissibility_request",
        "domainspec_source_admissibility_receipt",
        "domainspec_source_owner_decision",
        "system_ontology_profile",
        "system_ontology_sources",
        "system_ontology_compiler",
        "system_ontology_graph",
        "system_ontology_source_manifest",
        "system_ontology_event_contract",
        "system_ontology_projection",
        "system_ontology_compile_receipt",
        "system_ontology_validator",
        "system_ontology_validation",
        "system_ontology_hostile_checks",
        "system_ontology_hostile_receipt",
        "system_ontology_owner_request",
        "system_ontology_admissibility_request",
        "system_ontology_admissibility_receipt",
        "system_ontology_owner_decision",
        "versioned_system_graph_manifest",
        "versioned_system_graph",
        "versioned_system_graph_view",
        "versioned_system_graph_validator",
        "versioned_system_graph_validation",
    ):
        ref = selected[key]
        path = CORE / ref["path"] if ref.get("repository") == str(CORE) else LAB / ref["path"]
        if not path.is_file() or digest(path) != ref["sha256"]:
            dependency_failures.append({"dependency": key, "failure": "digest-mismatch"})
    record(
        "selected-dependency-currentness",
        not dependency_failures,
        {"selector_sha256": selector_digest, "failures": dependency_failures},
    )

    stages = plan.get("stages", [])
    ids = [stage.get("stage_id") for stage in stages]
    expected_ids = ["D65-P0", "D65-S1", "D65-S2", "D65-S3", "D65-S4", "D65-S5", "D65-S6", "D65-S7", "D65-S8"]
    dependency_order_pass = ids == expected_ids
    for index, stage in enumerate(stages):
        expected_depends = [] if index == 0 else [expected_ids[index - 1]]
        dependency_order_pass = dependency_order_pass and stage.get("depends_on") == expected_depends
    record("stage-order-and-predecessors", dependency_order_pass, {"stage_ids": ids})

    gate_ids = [stage.get("gate_id") for stage in stages]
    gate_pass = len(gate_ids) == len(set(gate_ids)) == len(stages) and all(gate_ids)
    record("one-distinct-gate-per-stage", bool(gate_pass), {"gate_ids": gate_ids})

    validation_ids = [value for stage in stages for value in stage.get("validation_ids", [])]
    record(
        "validation-coverage",
        bool(stages) and all(stage.get("validation_ids") for stage in stages) and len(validation_ids) == len(set(validation_ids)),
        {"validation_count": len(validation_ids), "duplicate_count": len(validation_ids) - len(set(validation_ids))},
    )

    project = plan.get("selected_owner", {})
    project_path = CORE / project.get("project_path", "")
    goal_path = CORE / project.get("goal_path", "")
    project_doc = load(project_path) if project_path.is_file() else {}
    goal_doc = load(goal_path) if goal_path.is_file() else {}
    source_registry = load(CORE / "cyberAlchemy-v2/goals/sources.json")
    source_by_id = {item.get("id"): item for item in source_registry.get("sources", [])}
    source_epoch_decision = load(CORE / selected["source_epoch_decision"]["path"])
    source_epoch_validation = load(CORE / selected["source_epoch_reconciliation_validation"]["path"])
    selected_source_drifts: list[str] = []
    ambient_source_drifts: list[str] = []
    definitions_source = source_by_id.get("SRC-CAV2-DEFINITIONS", {})
    definitions_path = CORE / definitions_source.get("path", "")
    p0_selectors = {
        "CAV2-D59": "f9589997351dcd40f5c37f970568aab3a09345c1b8ab6331860d5533d2c7a674",
        "CAV2-D60": "3dc9faeecf91410b8b6a00aa8fd847d474031bd207e91743e72507dee6c526db",
        "CAV2-D63": "2dfd918a50e8e19b2f5af1f4c6e0e2f7505578df2e6592af78928a811cfb9a0b",
        "CAV2-D65": "ba524beb8fb408f9abcd0805644f59ec2dbfcd810de24ac99c87296f843ba4ff",
    }
    if not definitions_path.is_file():
        selected_source_drifts.append("missing source: SRC-CAV2-DEFINITIONS")
    else:
        for definition_id, expected in p0_selectors.items():
            actual = hashlib.sha256(definition_selector_bytes(definitions_path, definition_id)).hexdigest()
            if actual != expected:
                selected_source_drifts.append(f"selector digest drift: {definition_id}")
        if definitions_source.get("sha256") != digest(definitions_path):
            ambient_source_drifts.append("whole-file digest drift: SRC-CAV2-DEFINITIONS outside selected P0 selectors")
    product_source = source_by_id.get("SRC-CAV2-PRODUCT-THESIS", {})
    product_path = CORE / product_source.get("path", "")
    if not product_path.is_file() or product_source.get("sha256") != digest(product_path):
        selected_source_drifts.append("source digest drift: SRC-CAV2-PRODUCT-THESIS")
    project_gate_pass = (
        project.get("state") == "registered-candidates"
        and project.get("registration_authorized") is True
        and project.get("carrier_registration") == "authored-and-discovered"
        and project.get("goals_package_validation", {}).get("result") == "BLOCK"
        and project.get("goals_package_validation", {}).get("material_digest") == "9b10a944c3359ef7ac1889502e9ab73f42aef456c0cf30a3a0f6efe034191f88"
        and project.get("goals_package_validation", {}).get("selected_dependency_blockers") == selected_source_drifts
        and project.get("goals_package_validation", {}).get("aggregate_blocker_count") == 20
        and not selected_source_drifts
        and source_epoch_decision.get("decision_id") == "CA2-DECISION-ONTOLOGY-RUNTIME-INTEGRATION-SOURCE-EPOCHS-002"
        and source_epoch_decision.get("status") == "selected"
        and source_epoch_decision.get("selected_epoch", {}).get("selected_sha256") == product_source.get("sha256")
        and source_epoch_decision.get("selected_epoch", {}).get("selector_sha256") == "f242f5156e9590d874667d896e4c63c11e5161879d1d91cd543e1632008a25d8"
        and source_epoch_decision.get("next_gate") == "G-D65-BINDING"
        and source_epoch_validation.get("result") == "PASS"
        and source_epoch_validation.get("selected_source_epoch_sha256") == product_source.get("sha256")
        and stages[0].get("state") == "PASS"
        and stages[1].get("state") == "PASS"
        and stages[2].get("state") == "PASS"
        and stages[3].get("state") == "PASS"
        and stages[4].get("state") == "PASS"
        and stages[5].get("state") == "PASS"
        and stages[6].get("state") == "BLOCK"
        and all(stage.get("state") == "not_evaluable" for stage in stages[7:])
        and project_doc.get("project_id") == project.get("project_id")
        and goal_doc.get("goal_id") == project.get("goal_id")
        and goal_doc.get("project_ref") == project.get("project_id")
        and project.get("goal_id") in project_doc.get("goal_refs", [])
        and project.get("project_sha256") == digest(project_path)
        and project.get("goal_sha256") == digest(goal_path)
    )
    record(
        "project-first-fail-closed",
        project_gate_pass,
        {
            "project_state": project.get("state"),
            "project_id": project_doc.get("project_id"),
            "goal_id": goal_doc.get("goal_id"),
            "selected_source_drifts": selected_source_drifts,
            "ambient_source_drifts": ambient_source_drifts,
            "definitions_stage_state": stages[1].get("state"),
            "product_stage_state": stages[2].get("state"),
            "business_stage_state": stages[3].get("state"),
            "next_stage_state": stages[4].get("state"),
        },
    )

    candidate = plan.get("definition_candidate", {})
    validation_doc = load(LAB / selected["definition_validation"]["path"])
    request_doc = load(LAB / selected["definition_owner_request"]["path"])
    decision_doc = load(LAB / selected["definition_owner_decision"]["path"])
    record(
        "definition-candidate-owner-selected",
        candidate.get("state") == "owner-selected-for-d65-s1"
        and candidate.get("validation_result") == "PASS"
        and candidate.get("gate_state") == "PASS"
        and candidate.get("owner_decision_state") == "selected"
        and candidate.get("selected_option_id") == "D65DEF-1"
        and candidate.get("concept_summary") == {
            "canonical_reuses": 5,
            "local_specializations": 5,
            "local_proposals": 3,
            "open_dispositions": 0,
            "canonical_promotions": 0,
        }
        and validation_doc.get("result") == "PASS"
        and validation_doc.get("gate_id") == "G-D65-DEFINITIONS"
        and validation_doc.get("gate_state") == "BLOCK"
        and request_doc.get("status") == "pending-owner-selection"
        and request_doc.get("gate_id") == "G-D65-DEFINITIONS"
        and decision_doc.get("status") == "selected"
        and decision_doc.get("decision_source", {}).get("token") == "D65DEF-1"
        and decision_doc.get("candidate_refs", {}).get("definition_pack_sha256") == selected["definition_pack"]["sha256"]
        and decision_doc.get("next_gate") == "G-D65-PRODUCT",
        {
            "pack_id": candidate.get("pack_id"),
            "validation_result": validation_doc.get("result"),
            "preselection_gate_state": validation_doc.get("gate_state"),
            "owner_decision_state": decision_doc.get("status"),
        },
    )

    product_candidate = plan.get("product_ontology_candidate", {})
    product_validation = load(LAB / selected["product_ontology_validation"]["path"])
    product_request = load(LAB / selected["product_ontology_owner_request"]["path"])
    product_admissibility = load(LAB / selected["product_ontology_admissibility_receipt"]["path"])
    product_decision = load(LAB / selected["product_ontology_owner_decision"]["path"])
    record(
        "product-ontology-candidate-owner-admitted",
        plan.get("revision") == 14
        and plan.get("supersedes_plan_sha256") == "507b1ad9ca90488bb52b90668a8d940236ec135e674fabeb8048f1437f1a2d1b"
        and product_candidate.get("state") == "owner-admitted-for-d65-s2"
        and product_candidate.get("validation_result") == "PASS"
        and product_candidate.get("gate_state") == "PASS"
        and product_candidate.get("owner_decision_state") == "selected"
        and product_candidate.get("owner_decision_ref") == "CAL-D65PROD-0016"
        and product_candidate.get("selected_option_id") == "D65PROD-1"
        and product_candidate.get("adoption_state") == "admitted-for-integration-epoch-001"
        and product_candidate.get("candidate_summary") == {
            "nodes": 16,
            "relation_types": 7,
            "relations": 15,
            "handled_definition_bindings": 13,
            "owner_routes": 5,
            "residue_items": 4,
        }
        and product_validation.get("result") == "PASS"
        and product_validation.get("gate_id") == "G-D65-PRODUCT"
        and product_validation.get("gate_state") == "BLOCK"
        and product_request.get("status") == "pending-owner-admission"
        and product_request.get("gate_id") == "G-D65-PRODUCT"
        and product_admissibility.get("routeOutcome") == "gate"
        and set(product_admissibility.get("presentedOptionIds", [])) == {"D65PROD-1", "D65PROD-2", "D65PROD-3", "D65PROD-4"}
        and product_decision.get("status") == "selected"
        and product_decision.get("decision_source", {}).get("token") == "D65PROD-1"
        and product_decision.get("next_gate") == "G-D65-BUSINESS"
        and product_decision.get("candidate_refs", {}).get("product_capability_sha256") == selected["product_capability"]["sha256"],
        {
            "revision": plan.get("revision"),
            "candidate_state": product_candidate.get("state"),
            "validation_result": product_validation.get("result"),
            "gate_state": product_validation.get("gate_state"),
            "admissibility_route": product_admissibility.get("routeOutcome"),
            "owner_decision_state": product_decision.get("status"),
        },
    )

    business_candidate = plan.get("business_ontology_candidate", {})
    business_validation = load(LAB / selected["business_ontology_validation"]["path"])
    business_request = load(LAB / selected["business_ontology_owner_request"]["path"])
    business_admissibility = load(LAB / selected["business_ontology_admissibility_receipt"]["path"])
    business_decision = load(LAB / selected["business_ontology_owner_decision"]["path"])
    record(
        "business-ontology-candidate-owner-admitted",
        business_candidate.get("ontology_id") == "CAL-ONTOLOGY-ONTOLOGY-RUNTIME-INTEGRATION-BUSINESS"
        and business_candidate.get("capability_id") == "CA2-CAP-CONSUME-GOVERNED-EVENT-CALCULATED-ONTOLOGY-PROJECTIONS"
        and business_candidate.get("state") == "owner-admitted-for-d65-s3"
        and business_candidate.get("ontology_type") == "business-domain"
        and business_candidate.get("branch") == "business"
        and business_candidate.get("materialization") == "package-required"
        and business_candidate.get("gate_id") == "G-D65-BUSINESS"
        and business_candidate.get("validation_result") == "PASS"
        and business_candidate.get("gate_state") == "PASS"
        and business_candidate.get("owner_decision_state") == "selected"
        and business_candidate.get("owner_request_ref") == "CAL-D65BIZ-REQUEST-001"
        and business_candidate.get("owner_decision_ref") == "CAL-D65BIZ-0018"
        and business_candidate.get("selected_option_id") == "D65BIZ-1"
        and business_candidate.get("adoption_state") == "admitted-for-integration-epoch-001"
        and business_candidate.get("business_system_bridge_state") == "contract-defined-no-system-endpoint-or-realization-claimed"
        and business_candidate.get("candidate_summary") == {
            "nodes": 26,
            "relation_types": 12,
            "relations": 35,
            "contracts": 8,
            "policies": 3,
            "workflows": 2,
            "failures": 13,
            "residue_items": 5,
        }
        and business_validation.get("result") == "PASS"
        and business_validation.get("gate_id") == "G-D65-BUSINESS"
        and business_validation.get("gate_state") == "BLOCK"
        and not business_validation.get("failed_checks")
        and business_request.get("status") == "pending-owner-admission"
        and business_request.get("gate_id") == "G-D65-BUSINESS"
        and business_admissibility.get("routeOutcome") == "gate"
        and set(business_admissibility.get("presentedOptionIds", [])) == {"D65BIZ-1", "D65BIZ-2", "D65BIZ-3", "D65BIZ-4"}
        and business_candidate.get("admissibility_route") == "gate"
        and business_decision.get("status") == "selected"
        and business_decision.get("decision_source", {}).get("token") == "D65BIZ-1"
        and business_decision.get("next_gate") == "G-D65-DOMAINSPEC-SOURCE"
        and business_decision.get("candidate_refs", {}).get("profile_sha256") == selected["business_ontology_profile"]["sha256"]
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and stages[3].get("state") == "PASS"
        and stages[4].get("state") == "PASS"
        and stages[5].get("state") == "PASS"
        and stages[6].get("state") == "BLOCK"
        and all(stage.get("state") == "not_evaluable" for stage in stages[7:]),
        {
            "revision": plan.get("revision"),
            "candidate_state": business_candidate.get("state"),
            "validation_result": business_validation.get("result"),
            "gate_state": business_validation.get("gate_state"),
            "admissibility_route": business_admissibility.get("routeOutcome"),
            "owner_decision_state": business_decision.get("status"),
            "first_blocking_gate": plan.get("first_blocking_gate"),
        },
    )

    binding_stage = next((stage for stage in stages if stage.get("stage_id") == "D65-S6"), {})
    record(
        "binding-owner-isolation",
        "Exactly one bounded native exact-implementation-binding author" in binding_stage.get("delegation_requirement", "")
        and binding_stage.get("depends_on") == ["D65-S5"],
        {"delegation_requirement": binding_stage.get("delegation_requirement")},
    )

    source_candidate = plan.get("domainspec_source_candidate", {})
    source_validation = load(LAB / selected["domainspec_source_validation"]["path"])
    source_hostile = load(LAB / selected["domainspec_source_hostile_receipt"]["path"])
    source_request = load(LAB / selected["domainspec_source_owner_request"]["path"])
    source_admissibility = load(LAB / selected["domainspec_source_admissibility_receipt"]["path"])
    source_decision = load(LAB / selected["domainspec_source_owner_decision"]["path"])
    record(
        "domainspec-source-candidate-owner-admitted",
        source_candidate.get("package_id") == "cal-ontology-runtime-integration-domainspec-source-epoch-001"
        and source_candidate.get("state") == "owner-admitted-for-d65-s4"
        and source_candidate.get("profile_state") == "development-only-binding-admitted-for-integration-epoch-001"
        and source_candidate.get("validation_result") == "PASS"
        and source_candidate.get("hostile_validation_result") == "PASS"
        and source_candidate.get("gate_state") == "PASS"
        and source_candidate.get("owner_decision_state") == "selected"
        and source_candidate.get("owner_decision_ref") == "CAL-D65SRC-0019"
        and source_candidate.get("selected_option_id") == "D65SRC-1"
        and source_candidate.get("adoption_state") == "admitted-for-integration-epoch-001"
        and source_candidate.get("admissibility_route") == "gate"
        and source_candidate.get("candidate_summary") == {
            "business_nodes_mapped": 26,
            "business_relations_mapped": 35,
            "business_contracts_mapped": 8,
            "business_failures_mapped": 13,
            "domainspec_nodes": 41,
            "canonical_domainspec_edges": 43,
            "event_streams": 5,
            "event_definitions": 5,
            "projections": 3,
            "exact_governance_joins": 2,
            "deterministic_double_compile": True,
            "materialized_graph": False,
            "system_ontology": False,
        }
        and source_validation.get("result") == "PASS"
        and source_validation.get("gate_state") == "BLOCK"
        and source_validation.get("compile_result", {}).get("minted", {}).get("deterministic_double_compile") is True
        and source_validation.get("compile_result", {}).get("event_sourcing", {}).get("deterministic_double_compile") is True
        and source_hostile.get("result") == "PASS"
        and source_request.get("status") == "pending-owner-admission"
        and source_request.get("gate_id") == "G-D65-DOMAINSPEC-SOURCE"
        and source_admissibility.get("routeOutcome") == "gate"
        and set(source_admissibility.get("presentedOptionIds", [])) == {"D65SRC-1", "D65SRC-2", "D65SRC-3", "D65SRC-4"}
        and source_decision.get("status") == "selected"
        and source_decision.get("decision_source", {}).get("normalized_option_id") == "D65SRC-1"
        and source_decision.get("next_gate") == "G-D65-COMPILE"
        and source_decision.get("candidate_refs", {}).get("profile_sha256") == selected["domainspec_source_profile"]["sha256"]
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and stages[4].get("state") == "PASS"
        and stages[5].get("state") == "PASS"
        and stages[6].get("state") == "BLOCK"
        and all(stage.get("state") == "not_evaluable" for stage in stages[7:]),
        {
            "candidate_state": source_candidate.get("state"),
            "validation_result": source_validation.get("result"),
            "hostile_result": source_hostile.get("result"),
            "gate_state": source_candidate.get("gate_state"),
            "admissibility_route": source_admissibility.get("routeOutcome"),
            "owner_decision_state": source_decision.get("status"),
            "first_blocking_gate": plan.get("first_blocking_gate"),
        },
    )

    system_candidate = plan.get("system_ontology_candidate", {})
    system_profile = load(LAB / selected["system_ontology_profile"]["path"])
    system_graph = load(LAB / selected["system_ontology_graph"]["path"])
    system_manifest = load(LAB / selected["system_ontology_source_manifest"]["path"])
    system_event = load(LAB / selected["system_ontology_event_contract"]["path"])
    system_projection = load(LAB / selected["system_ontology_projection"]["path"])
    system_compile = load(LAB / selected["system_ontology_compile_receipt"]["path"])
    system_validation = load(LAB / selected["system_ontology_validation"]["path"])
    system_hostile = load(LAB / selected["system_ontology_hostile_receipt"]["path"])
    system_request = load(LAB / selected["system_ontology_owner_request"]["path"])
    system_admissibility = load(LAB / selected["system_ontology_admissibility_receipt"]["path"])
    system_decision = load(LAB / selected["system_ontology_owner_decision"]["path"])
    version_manifest = load(LAB / selected["versioned_system_graph_manifest"]["path"])
    version_graph = load(LAB / selected["versioned_system_graph"]["path"])
    version_validation = load(LAB / selected["versioned_system_graph_validation"]["path"])
    version_state = plan.get("versioned_system_graph", {})
    record(
        "system-ontology-candidate-owner-admitted",
        system_candidate.get("package_id") == "cal-ontology-runtime-integration-system-ontology-epoch-001"
        and system_candidate.get("ontology_id") == "cal.ontology-runtime-integration.system-runtime.epoch-001"
        and system_candidate.get("state") == "owner-admitted-for-d65-s5"
        and system_candidate.get("gate_id") == "G-D65-COMPILE"
        and system_candidate.get("validation_result") == "PASS"
        and system_candidate.get("hostile_validation_result") == "PASS"
        and system_candidate.get("gate_state") == "PASS"
        and system_candidate.get("owner_request_ref") == "CAL-D65SYS-REQUEST-001"
        and system_candidate.get("owner_decision_state") == "selected"
        and system_candidate.get("owner_decision_ref") == "CAL-D65SYS-0020"
        and system_candidate.get("selected_option_id") == "D65SYS-1"
        and system_candidate.get("adoption_state") == "admitted-for-integration-epoch-001"
        and system_candidate.get("admissibility_route") == "gate"
        and system_candidate.get("candidate_summary") == {
            "domainspec_nodes": 41,
            "canonical_domainspec_edges": 43,
            "provenance_records": 84,
            "event_streams": 5,
            "event_definitions": 5,
            "projections": 3,
            "exact_governance_joins": 2,
            "runtime_obligations": 12,
            "deterministic_internal_double_compile": True,
            "deterministic_external_double_compile": True,
            "graph_system_ontology_equality": True,
            "hostile_cases": 3,
            "materialized_graph": True,
            "system_ontology": True,
            "implementation_binding_present": False,
        }
        and system_profile.get("status") == "candidate-not-admitted"
        and system_profile.get("owner_gate") == "G-D65-COMPILE"
        and len(system_graph.get("nodes", [])) == 41
        and len(system_graph.get("edges", [])) == 43
        and len(system_manifest.get("records", [])) == 84
        and [len(system_event.get(key, [])) for key in ("streams", "events", "projections", "joins")] == [5, 5, 3, 2]
        and system_projection.get("semantic_graph", {}).get("nodes") == system_graph.get("nodes")
        and system_projection.get("semantic_graph", {}).get("edges") == system_graph.get("edges")
        and system_projection.get("event_calculus", {}).get("contract") == system_event
        and system_compile.get("result") == "PASS"
        and system_compile.get("deterministic_internal_double_compile") is True
        and system_validation.get("result") == "PASS"
        and system_validation.get("gate_state") == "BLOCK"
        and system_hostile.get("result") == "PASS"
        and system_request.get("status") == "pending-owner-admission"
        and system_request.get("gate_id") == "G-D65-COMPILE"
        and system_admissibility.get("routeOutcome") == "gate"
        and set(system_admissibility.get("presentedOptionIds", [])) == {"D65SYS-1", "D65SYS-2", "D65SYS-3", "D65SYS-4"}
        and system_decision.get("status") == "selected"
        and system_decision.get("selection", {}).get("option_id") == "D65SYS-1"
        and system_decision.get("next_gate") == "G-D65-BINDING"
        and system_decision.get("candidate_refs", {}).get("graph_sha256") == selected["system_ontology_graph"]["sha256"]
        and version_manifest.get("version_id") == "cal-ontology-runtime-integration-v1"
        and version_manifest.get("admission_decision", {}).get("sha256") == selected["system_ontology_owner_decision"]["sha256"]
        and version_manifest.get("canonical_replay_source") is False
        and version_graph == system_graph
        and version_validation.get("result") == "PASS"
        and version_state.get("validation_result") == "PASS"
        and version_state.get("canonical_replay_source") is False
        and version_state.get("source_graph_sha256") == version_state.get("versioned_graph_sha256") == selected["system_ontology_graph"]["sha256"]
        and plan.get("status") == "system-ontology-admitted-binding-gate-blocked"
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and stages[5].get("state") == "PASS"
        and stages[6].get("state") == "BLOCK"
        and all(stage.get("state") == "not_evaluable" for stage in stages[7:]),
        {
            "candidate_state": system_candidate.get("state"),
            "validation_result": system_validation.get("result"),
            "hostile_result": system_hostile.get("result"),
            "gate_state": system_candidate.get("gate_state"),
            "admissibility_route": system_admissibility.get("routeOutcome"),
            "first_blocking_gate": plan.get("first_blocking_gate"),
        },
    )

    continuation = plan.get("owner_continuation", {})
    record(
        "admission-cutover-separation",
        continuation.get("after_stage") == "D65-S8"
        and continuation.get("state") == "not_evaluable"
        and "cannot be inferred" in continuation.get("rule", ""),
        continuation,
    )
    record(
        "no-execution-authority",
        plan.get("execution", {}).get("authorized") is False
        and plan.get("execution", {}).get("first_executable_stage") is None
        and plan.get("authority_effect") == "none",
        plan.get("execution"),
    )

    view = VIEW.read_text(encoding="utf-8") if VIEW.is_file() else ""
    record(
        "human-view-boundary",
        "Canonical source: `d65-plan.json`" in view
        and "Invoke is not part of this lifecycle" in view
        and "Capability-local business ontology candidate" in view
        and "CAL-D65BIZ-0018" in view
        and "D65-S4 DomainSpec source candidate" in view
        and "CAL-D65SRC-0019" in view
        and "CAL-D65SYS-REQUEST-001" in view
        and "CAL-D65SYS-0020" in view
        and "CA2-DECISION-ONTOLOGY-RUNTIME-INTEGRATION-SOURCE-EPOCHS-002" in view
        and "cal-ontology-runtime-integration-v1" in view
        and "D65SYS-1" in view
        and "G-D65-DOMAINSPEC-SOURCE" in view
        and "G-D65-COMPILE" in view
        and "G-D65-BINDING" in view
        and "G-INTEGRATION-ADMISSION-CUTOVER" in view,
        {"view_present": bool(view)},
    )

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-native-integration-plan-validation/v1",
        "plan_id": plan.get("plan_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "planning_state": plan.get("status"),
        "first_gate": "G-D65-BINDING",
        "execution_authorized": False,
        "inputs": [
            {"path": str(SOURCE.relative_to(LAB)), "sha256": digest(SOURCE)},
            {"path": str(VIEW.relative_to(LAB)), "sha256": digest(VIEW)},
            {"path": str(SCRIPT.relative_to(LAB)), "sha256": digest(SCRIPT)},
        ],
        "authority_effect": "none",
        "claim_ceiling": "PASS validates the direct D65 plan structure, Project-Goal closure, selector-level source currentness, exact D65DEF-1, D65PROD-1, D65BIZ-1, D65SRC-1, D65SYS-1, and the provenance-bound version 1 graph copy. D65-S6 remains blocked at G-D65-BINDING; no implementation binding or implementation stage is authorized.",
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "plan_id": receipt["plan_id"],
        "result": result,
        "failed_checks": failed,
        "planning_state": receipt["planning_state"],
        "first_gate": receipt["first_gate"],
        "execution_authorized": False,
    }, indent=2, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
