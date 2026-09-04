#!/usr/bin/env python3
"""Validate the CTX04 Governance-to-Ontology-Lifecycle Context Map candidate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from render import OUTPUT as PACK_OUTPUT, SOURCE as PACK_SOURCE, render as render_pack

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
MAP_PATH = LAB / "contexts/maps/governance-ontology-lifecycle/v1/map.json"
MAP_OUTPUT = LAB / "contexts/maps/governance-ontology-lifecycle/v1/MAP.md"
SHARED_SCHEMA = LAB / "tooling/schemas/ctx01/v1/schema.json"
SHARED_GENERATOR = LAB / "tooling/generators/ctx01_artifact.py"
RECEIPT = ROOT / "receipts/validation.json"

UPSTREAM = "cal.context.governance/v1"
DOWNSTREAM = "cal.context.ontology-lifecycle/v1"
PATTERN = "candidate:ddd.upstream-downstream.published-language.anticorruption-layer/v1"
RELATIONSHIP_ID = "cal.context-relationship.governance-to-ontology-lifecycle.authority-decision-feed"
EXPECTED_CONTRACTS = {
    "cal.context.governance/v1",
    "cal.language.governance/v1",
    "cal.context.ontology-lifecycle/v1",
    "cal.language.ontology-lifecycle/v1",
    "cal.definition.context-map@1.0.0-candidate.1",
}
EXPECTED_TRANSLATIONS = {
    "cav2.governance-model#node:GovernanceDecision",
    "ontology-lifecycle.governance-event",
    "ontology-lifecycle.exact-semantic-event-reference",
}
EXPECTED_OWNERS = {
    "role:context-map-owner",
    "role:governance-context-owner",
    "role:governance-language-owner",
    "role:ontology-lifecycle-context-owner",
    "role:ontology-lifecycle-language-owner",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_instance_renderer():
    spec = importlib.util.spec_from_file_location("ctx01_instance_renderer", SHARED_GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_instance


def directional_contract_valid(relationship: dict) -> bool:
    return (
        relationship.get("source_context_ref") == UPSTREAM
        and relationship.get("target_context_ref") == DOWNSTREAM
        and relationship.get("direction") == "source-to-target"
        and relationship.get("relationship_kind_ref") == PATTERN
        and "transfer information, never authority" in relationship.get("authority_boundary", "")
    )


def main() -> int:
    pack = load(PACK_SOURCE)
    context_map = load(MAP_PATH)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    actual_inputs = {}
    inputs_current = True
    for item in pack["selected_inputs"]:
        path = LAB / item["path"]
        actual = sha(path) if path.is_file() else None
        actual_inputs[item["input_id"]] = actual
        inputs_current = inputs_current and actual == item["sha256"]
    check("selected-input-digest-closure", inputs_current, actual_inputs)

    schema = load(SHARED_SCHEMA)
    map_schema = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/contextMap"}
    schema_errors = sorted(error.message for error in Draft202012Validator(map_schema).iter_errors(context_map))
    check("context-map-schema-valid", not schema_errors, schema_errors)
    check("candidate-posture-no-effect", context_map.get("status") == "candidate-unadmitted" and context_map.get("authority_effect") == "none" and context_map.get("classification", {}).get("authority_kind") == "coordination-authority", {"status": context_map.get("status"), "effect": context_map.get("authority_effect"), "classification": context_map.get("classification")})

    artifact_type_decision = load(LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json")
    admitted_type_refs = {item["artifact_type_ref"] for item in artifact_type_decision.get("admitted_artifact_types", [])}
    check("context-map-artifact-type-admitted", artifact_type_decision.get("status") == "owner-admitted" and "cal.artifact-type.context-map/v1" in admitted_type_refs, {"status": artifact_type_decision.get("status"), "admitted": sorted(admitted_type_refs)})

    endpoint_decision = load(LAB / "docs/decisions/0023-governance-and-ontology-lifecycle-context-promotion/decision.json")
    endpoint_receipt = load(LAB / "docs/decisions/0023-governance-and-ontology-lifecycle-context-promotion/receipts/admission-validation.json")
    admitted_ids = {item["artifact_id"] for item in endpoint_decision["admitted_artifacts"] if item["decision_overlay_status"] == "admitted"}
    check("endpoint-admission-current", endpoint_decision.get("status") == "owner-admitted" and endpoint_receipt.get("result") == "PASS" and {"cal.context.governance", "cal.context.ontology-lifecycle", "cal.language.governance", "cal.language.ontology-lifecycle"} <= admitted_ids, {"decision": endpoint_decision.get("status"), "receipt": endpoint_receipt.get("result"), "admitted": sorted(admitted_ids)})

    governance_context = load(LAB / "contexts/governance/v1/context.json")
    governance_language = load(LAB / "contexts/governance/v1/language.json")
    lifecycle_context = load(LAB / "contexts/ontology-lifecycle/v1/context.json")
    lifecycle_language = load(LAB / "contexts/ontology-lifecycle/v1/language.json")
    check("exact-endpoint-identity-closure", context_map["context_refs"] == [UPSTREAM, DOWNSTREAM] and governance_context["context_id"] == "cal.context.governance" and lifecycle_context["context_id"] == "cal.context.ontology-lifecycle", {"map": context_map["context_refs"], "governance": governance_context["context_id"], "ontology_lifecycle": lifecycle_context["context_id"]})

    placement = load(LAB / "docs/decisions/0016-ontology-lifecycle-context-placement/decision.json")["selected_context_model"]["governance_boundary"]
    check("prior-upstream-downstream-decision-preserved", placement.get("upstream_context") == "Governance" and placement.get("downstream_context") == "Ontology Lifecycle" and placement.get("dependency_direction") == "Ontology Lifecycle -> Governance" and placement.get("reverse_dependency_default") == "forbidden-unless-separately-authored-and-owner-selected", placement)

    relationships = context_map["relationships"]
    relationship = relationships[0]
    check("single-directional-relationship", len(relationships) == 1 and relationship.get("relationship_id") == RELATIONSHIP_ID and directional_contract_valid(relationship), relationship)
    check("selected-pattern-exact", pack["selected_pattern"]["pattern_ref"] == relationship["relationship_kind_ref"] == PATTERN and pack["selected_pattern"]["relationship_count"] == 1, pack["selected_pattern"])
    check("contract-reference-closure", set(relationship["contract_refs"]) == EXPECTED_CONTRACTS, relationship["contract_refs"])

    governance_concepts = set(governance_language["concept_refs"])
    lifecycle_concepts = set(lifecycle_language["concept_refs"])
    check("translation-reference-language-closure", set(relationship["translation_refs"]) == EXPECTED_TRANSLATIONS and "cav2.governance-model#node:GovernanceDecision" in governance_concepts and (EXPECTED_TRANSLATIONS - {"cav2.governance-model#node:GovernanceDecision"}) <= lifecycle_concepts, {"translations": relationship["translation_refs"], "governance_resolved": "cav2.governance-model#node:GovernanceDecision" in governance_concepts, "lifecycle_resolved": sorted((EXPECTED_TRANSLATIONS - {"cav2.governance-model#node:GovernanceDecision"}) & lifecycle_concepts)})
    info = relationship["information_boundary"]
    check("information-boundary-complete", all(term in info for term in ("exact immutable owner-decision envelope", "source digest", "authority scope", "Exact Semantic Event Reference", "Typed Residue", "do not cross")), info)
    authority = relationship["authority_boundary"]
    check("authority-non-transfer-complete", all(term in authority for term in ("sole semantic and decision authority", "cannot create", "reinterpret", "transfer information, never authority")), authority)

    owner_registry = load(LAB / "authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json")
    active_roles = {f"role:{item['role_id']}" for item in owner_registry["role_assignments"] if item["principal_id"] == "person:<vrondelli>" and item["decision_separation"] == "required"}
    check("map-and-endpoint-owner-closure", set(context_map["owner_refs"]) == set(relationship["owner_refs"]) == EXPECTED_OWNERS and EXPECTED_OWNERS <= active_roles, {"map": context_map["owner_refs"], "relationship": relationship["owner_refs"], "active": sorted(EXPECTED_OWNERS & active_roles)})
    check("reverse-dependency-absent", not any(item.get("source_context_ref") == DOWNSTREAM and item.get("target_context_ref") == UPSTREAM for item in relationships) and any("reverse" in item for item in context_map["residue_refs"]), {"relationships": len(relationships), "residue": context_map["residue_refs"]})

    facets = pack.get("four_facet_contract", {})
    check("four-facet-contract-complete", set(facets) == {"classification", "schema", "human_continuation", "machine_checkable"} and all(facets.values()), facets)

    render_instance = load_instance_renderer()
    rendered_a = render_instance(context_map, "context-map")
    rendered_b = render_instance(context_map, "context-map")
    map_parity = MAP_OUTPUT.is_file() and MAP_OUTPUT.read_text(encoding="utf-8") == rendered_a == rendered_b
    pack_rendered = render_pack(pack)
    pack_parity = PACK_OUTPUT.is_file() and PACK_OUTPUT.read_text(encoding="utf-8") == pack_rendered
    check("deterministic-generated-projections", map_parity and pack_parity, {"map": map_parity, "pack": pack_parity})
    check("canonical-machine-direction", context_map["source_direction"]["canonical"] == "map.json" and context_map["source_direction"]["human_projection"] == "MAP.md" and context_map["source_direction"]["projection_policy"] == "generated-only" and context_map["source_direction"]["generator_sha256"] == sha(SHARED_GENERATOR), context_map["source_direction"])

    hostile_reverse = copy.deepcopy(relationship)
    hostile_reverse["source_context_ref"], hostile_reverse["target_context_ref"] = hostile_reverse["target_context_ref"], hostile_reverse["source_context_ref"]
    check("hostile-reverse-edge-rejected", not directional_contract_valid(hostile_reverse), hostile_reverse)
    hostile_authority = copy.deepcopy(relationship)
    hostile_authority["authority_boundary"] = "The relationship transfers authority to Ontology Lifecycle."
    check("hostile-authority-transfer-rejected", not directional_contract_valid(hostile_authority), hostile_authority["authority_boundary"])
    check("claim-ceilings-bounded", all(term in context_map.get("claim_ceiling", "") for term in ("does not admit the map", "reverse dependency", "runtime adapter", "stable release")) and all(term in pack.get("claim_ceiling", "") for term in ("does not admit the map", "reverse dependency", "runtime integration", "stable release")), {"map": context_map.get("claim_ceiling"), "pack": pack.get("claim_ceiling")})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-context-map-candidate-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "promotion_eligibility": "eligible-for-exact-context-map-owner-review" if result == "PASS" else "blocked",
        "materials": {"map_json_sha256": sha(MAP_PATH), "map_md_sha256": sha(MAP_OUTPUT) if MAP_OUTPUT.is_file() else None, "map_pack_json_sha256": sha(PACK_SOURCE), "map_pack_md_sha256": sha(PACK_OUTPUT) if PACK_OUTPUT.is_file() else None},
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX04_CONTEXT_MAP_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
