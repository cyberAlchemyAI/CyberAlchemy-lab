#!/usr/bin/env python3
"""Validate the CTX03 Governance and Ontology Lifecycle candidates."""

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
DOMAINSPEC = LAB.parent / "domainspec-core"
RECEIPT = ROOT / "receipts/validation.json"
SHARED_SCHEMA = LAB / "tooling/schemas/ctx01/v1/schema.json"
SHARED_GENERATOR = LAB / "tooling/generators/ctx01_artifact.py"

ARTIFACTS = {
    "governance-context": (LAB / "contexts/governance/v1/context.json", LAB / "contexts/governance/v1/CONTEXT.md", "bounded-context"),
    "governance-language": (LAB / "contexts/governance/v1/language.json", LAB / "contexts/governance/v1/LANGUAGE.md", "ubiquitous-language"),
    "ontology-lifecycle-context": (LAB / "contexts/ontology-lifecycle/v1/context.json", LAB / "contexts/ontology-lifecycle/v1/CONTEXT.md", "bounded-context"),
    "ontology-lifecycle-language": (LAB / "contexts/ontology-lifecycle/v1/language.json", LAB / "contexts/ontology-lifecycle/v1/LANGUAGE.md", "ubiquitous-language"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_instance_renderer():
    spec = importlib.util.spec_from_file_location("ctx01_instance_renderer", SHARED_GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_instance


def main() -> int:
    pack = load(PACK_SOURCE)
    shared_schema = load(SHARED_SCHEMA)
    render_instance = load_instance_renderer()
    loaded = {name: load(paths[0]) for name, paths in ARTIFACTS.items()}
    gc = loaded["governance-context"]
    gl = loaded["governance-language"]
    oc = loaded["ontology-lifecycle-context"]
    ol = loaded["ontology-lifecycle-language"]
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    bound_actual = {}
    bound_ok = True
    for item in pack["selected_inputs"]:
        base = LAB if item["root"] == "lab" else DOMAINSPEC
        path = base / item["path"]
        actual = sha(path) if path.is_file() else None
        bound_actual[item["input_id"]] = actual
        bound_ok = bound_ok and actual == item["sha256"]
    check("selected-input-digest-closure", bound_ok, bound_actual)

    for name, data in loaded.items():
        definition = "boundedContext" if name.endswith("context") else "ubiquitousLanguage"
        instance_schema = {"$schema": shared_schema["$schema"], "$defs": shared_schema["$defs"], "$ref": f"#/$defs/{definition}"}
        errors = sorted(error.message for error in Draft202012Validator(instance_schema).iter_errors(data))
        check(f"{name}-schema-valid", not errors, errors)

    definition_decision = load(LAB / "docs/decisions/0018-definition-and-ctx00-promotion/decision.json")
    artifact_type_decision = load(LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json")
    owner_decision = load(LAB / "docs/decisions/0022-context-operational-owner-promotion/decision.json")
    check("predecessor-admissions-resolve", all(item.get("status") == "owner-admitted" for item in (definition_decision, artifact_type_decision, owner_decision)), {"definition": definition_decision.get("status"), "artifact_type": artifact_type_decision.get("status"), "owners": owner_decision.get("status")})

    owners = load(LAB / "authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json")
    assignments = {item["role_id"]: item for item in owners["role_assignments"]}
    required_roles = {"governance-context-owner", "ontology-lifecycle-context-owner", "governance-language-owner", "ontology-lifecycle-language-owner"}
    check("separate-owner-role-closure", required_roles <= set(assignments) and all(assignments[role]["principal_id"] == "person:<vrondelli>" and assignments[role]["decision_separation"] == "required" for role in required_roles), {role: assignments.get(role) for role in sorted(required_roles)})

    check("stable-distinct-identities", gc["context_id"] == "cal.context.governance" and oc["context_id"] == "cal.context.ontology-lifecycle" and gl["language_id"] == "cal.language.governance" and ol["language_id"] == "cal.language.ontology-lifecycle" and len({gc["context_id"], oc["context_id"], gl["language_id"], ol["language_id"]}) == 4, [gc["context_id"], oc["context_id"], gl["language_id"], ol["language_id"]])
    check("reciprocal-context-language-bindings", gc["ubiquitous_language_ref"] == f"{gl['language_id']}/v1" and gl["bounded_context_ref"] == f"{gc['context_id']}/v1" and oc["ubiquitous_language_ref"] == f"{ol['language_id']}/v1" and ol["bounded_context_ref"] == f"{oc['context_id']}/v1", {"governance": [gc["ubiquitous_language_ref"], gl["bounded_context_ref"]], "ontology_lifecycle": [oc["ubiquitous_language_ref"], ol["bounded_context_ref"]]})
    check("domain-model-structure-bindings", gc["domain_model_ref"] == "cav2.governance-model@candidate" and oc["domain_model_ref"] == "cal.ontology-lifecycle.business-domain.v2-candidate", {"governance": gc["domain_model_ref"], "ontology_lifecycle": oc["domain_model_ref"]})

    gov_nodes = load(DOMAINSPEC / "cyberAlchemy-v2/ontology/governance/nodes.json")["nodes"]
    gov_relations = load(DOMAINSPEC / "cyberAlchemy-v2/ontology/governance/relations.json")["relations"]
    expected_gov_concepts = {f"cav2.governance-model#node:{item['id']}" for item in gov_nodes}
    expected_gov_relations = {f"cav2.governance-model#relation:{item['id']}" for item in gov_relations}
    actual_gov_expressions = {item["concept_ref"] for item in gl["expression_bindings"] if item["disposition"] == "current"}
    check("governance-concept-surface-closed", set(gl["concept_refs"]) == expected_gov_concepts == actual_gov_expressions, {"source": len(expected_gov_concepts), "concept_refs": len(gl["concept_refs"]), "expressions": len(actual_gov_expressions)})
    check("governance-relation-surface-closed", {item["relation_ref"] for item in gl["relation_bindings"]} == expected_gov_relations, {"source": len(expected_gov_relations), "bindings": len(gl["relation_bindings"])})

    lifecycle_model = load(LAB / "ontology-lifecycle/business-ontology.json")
    expected_lifecycle_concepts = {item["id"] for item in lifecycle_model["concepts"]}
    expected_lifecycle_relations = {item["id"] for item in lifecycle_model["relationships"]}
    actual_lifecycle_expressions = {item["concept_ref"] for item in ol["expression_bindings"] if item["disposition"] == "current"}
    check("ontology-lifecycle-concept-surface-closed", set(ol["concept_refs"]) == expected_lifecycle_concepts == actual_lifecycle_expressions, {"source": len(expected_lifecycle_concepts), "concept_refs": len(ol["concept_refs"]), "expressions": len(actual_lifecycle_expressions)})
    check("ontology-lifecycle-relation-surface-closed", {item["relation_ref"] for item in ol["relation_bindings"]} == expected_lifecycle_relations, {"source": len(expected_lifecycle_relations), "bindings": len(ol["relation_bindings"])})

    check("context-map-remains-unselected", gc["context_map_refs"] == [] and oc["context_map_refs"] == [] and "Context Map" in gc["scope"]["exclusions"][-1] and "Context Map" in oc["scope"]["exclusions"][-1], {"governance": gc["context_map_refs"], "ontology_lifecycle": oc["context_map_refs"]})
    check("cross-context-non-collapse", "Ontology event history" in gc["scope"]["exclusions"][0] and "Governance axioms" in oc["scope"]["exclusions"][0] and any(item["expression"] == "Governance Event" and "not a Governance Decision" in item["disposition"] for item in ol["ambiguity_records"]) and any(item["expression"] == "Governance Event" and "Not a Governance context concept" in item["disposition"] for item in gl["ambiguity_records"]), {"governance_exclusion": gc["scope"]["exclusions"][0], "ontology_lifecycle_exclusion": oc["scope"]["exclusions"][0]})
    check("independent-state-axes", any(item["expression"] == "State" and all(term in item["disposition"] for term in ("Semantic State", "Governance State", "Lifecycle State")) for item in ol["ambiguity_records"]), [item for item in ol["ambiguity_records"] if item["expression"] == "State"])

    four_facets = pack.get("four_facet_contract", {})
    check("four-facet-contract-complete", set(four_facets) == {"identity", "structure", "relationships", "lifecycle_and_evidence"} and all(four_facets.values()), four_facets)
    check("candidate-lifecycle-and-evidence", all(data["status"] == "candidate-unadmitted" and data["authority_effect"] == "none" and data["evidence_refs"] and data["residue_refs"] for data in loaded.values()), {name: {"status": data["status"], "authority_effect": data["authority_effect"], "evidence": len(data["evidence_refs"]), "residue": len(data["residue_refs"])} for name, data in loaded.items()})
    check("semantic-authority-without-present-effect", all(data["classification"]["authority_kind"] == "semantic-authority" and data["authority_effect"] == "none" for data in loaded.values()), {name: data["classification"] for name, data in loaded.items()})

    projection_results = {}
    projection_ok = True
    for name, (source, output, slug) in ARTIFACTS.items():
        rendered_a = render_instance(load(source), slug)
        rendered_b = render_instance(load(source), slug)
        ok = rendered_a == rendered_b and output.is_file() and output.read_text(encoding="utf-8") == rendered_a
        projection_results[name] = {"parity": ok, "sha256": hashlib.sha256(rendered_a.encode()).hexdigest()}
        projection_ok = projection_ok and ok
    rendered_pack = render_pack(pack)
    pack_parity = PACK_OUTPUT.is_file() and PACK_OUTPUT.read_text(encoding="utf-8") == rendered_pack
    check("deterministic-generated-projections", projection_ok and pack_parity, {"artifacts": projection_results, "pack": pack_parity})
    check("canonical-machine-direction", all(data["source_direction"]["projection_policy"] == "generated-only" and data["source_direction"]["generator_sha256"] == sha(SHARED_GENERATOR) for data in loaded.values()), {name: data["source_direction"] for name, data in loaded.items()})

    hostile = copy.deepcopy(ol)
    hostile["status"] = "admitted"
    hostile_schema = {"$schema": shared_schema["$schema"], "$defs": shared_schema["$defs"], "$ref": "#/$defs/ubiquitousLanguage"}
    check("hostile-status-inflation-rejected", bool(list(Draft202012Validator(hostile_schema).iter_errors(hostile))), "An instance claiming admitted status must fail the candidate schema.")
    check("claim-ceilings-bounded", all(all(term in data["claim_ceiling"] for term in ("does not admit", "Context Map", "stable release")) for data in loaded.values()) and all(term in pack["claim_ceiling"] for term in ("does not admit", "Context Map", "stable release")), {name: data["claim_ceiling"] for name, data in loaded.items()})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    materials = {}
    for name, (source, output, _) in ARTIFACTS.items():
        materials[name] = {"canonical_sha256": sha(source), "projection_sha256": sha(output) if output.is_file() else None}
    receipt = {
        "schema_version": "cyberalchemy-lab-context-candidate-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "promotion_eligibility": "eligible-for-separate-context-and-language-owner-review" if result == "PASS" else "blocked",
        "materials": materials,
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX03_CONTEXT_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
