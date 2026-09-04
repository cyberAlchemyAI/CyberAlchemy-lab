#!/usr/bin/env python3
"""Validate CTX05 successor context, lineage, and migration candidates."""

import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"
SCHEMA_PATH = LAB / "tooling/schemas/ctx01/v1/schema.json"
GENERATOR_PATH = LAB / "tooling/generators/ctx01_artifact.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_generator():
    spec = importlib.util.spec_from_file_location("ctx01_artifact", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    pack = load(SOURCE)
    schema = load(SCHEMA_PATH)
    generator = load_generator()
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("pack-identity", pack.get("pack_id") == "CAL-CONTEXT-PACK-CTX05-0001" and pack.get("status") == "candidate-unadmitted" and pack.get("authority_effect") == "none", {"id": pack.get("pack_id"), "status": pack.get("status"), "effect": pack.get("authority_effect")})
    direction = pack["authorship_direction"]
    check("exact-authorship-direction", direction.get("principal") == "person:<vrondelli>" and direction.get("effect") == "candidate-authorship-and-validation-only" and "explicit `context_map_refs`" in direction.get("instruction", ""), direction)

    input_results = []
    for item in pack["selected_inputs"]:
        actual = sha(LAB / item["path"])
        input_results.append({"input_id": item["input_id"], "expected": item["sha256"], "actual": actual})
    check("selected-input-digest-closure", all(item["expected"] == item["actual"] for item in input_results), input_results)

    decision_ids = {"definition-and-ctx00-admission", "ctx01-artifact-type-admission", "context-owner-admission", "endpoint-context-admission", "context-map-admission"}
    decision_results = []
    for item in pack["selected_inputs"]:
        if item["input_id"] in decision_ids:
            data = load(LAB / item["path"])
            decision_results.append({"input_id": item["input_id"], "status": data.get("status")})
    check("prerequisite-decisions-current", len(decision_results) == 5 and all(item["status"] == "owner-admitted" for item in decision_results), decision_results)

    map_receipt_item = next(item for item in pack["selected_inputs"] if item["input_id"] == "context-map-admission-validation")
    map_receipt = load(LAB / map_receipt_item["path"])
    check("context-map-admission-evidence-pass", map_receipt.get("result") == "PASS" and map_receipt.get("admission_state") == "complete-governance-to-ontology-lifecycle-context-map-admission", {"result": map_receipt.get("result"), "state": map_receipt.get("admission_state")})

    artifact_results = []
    artifact_data = {}
    for item in pack["canonical_artifacts"]:
        path = LAB / item["path"]
        projection = LAB / item["projection"]
        artifact_data[item["artifact_id"]] = load(path)
        artifact_results.append({"artifact_id": item["artifact_id"], "machine": sha(path), "expected_machine": item["sha256"], "projection": sha(projection), "expected_projection": item["projection_sha256"]})
    check("seven-artifact-byte-bindings-current", len(artifact_results) == 7 and all(item["machine"] == item["expected_machine"] and item["projection"] == item["expected_projection"] for item in artifact_results), artifact_results)

    schema_kind = {
        "bounded-context": "boundedContext",
        "ubiquitous-language": "ubiquitousLanguage",
        "context-lineage-record": "contextLineageRecord",
        "context-migration-manifest": "contextMigrationManifest",
    }
    schema_results = []
    for item in pack["canonical_artifacts"]:
        validator = Draft202012Validator({"$ref": f"#/$defs/{schema_kind[item['artifact_type']]}", **schema})
        errors = [error.message for error in validator.iter_errors(artifact_data[item["artifact_id"]])]
        schema_results.append({"artifact_id": item["artifact_id"], "errors": errors})
    check("closed-schema-valid", all(not item["errors"] for item in schema_results), schema_results)
    check("all-candidates-non-effectful", all(data.get("status") == "candidate-unadmitted" and data.get("authority_effect") == "none" for data in artifact_data.values()), {key: [value.get("status"), value.get("authority_effect")] for key, value in artifact_data.items()})

    gov_context = artifact_data["cal.context.governance/v2"]
    gov_language = artifact_data["cal.language.governance/v2"]
    lifecycle_context = artifact_data["cal.context.ontology-lifecycle/v2"]
    lifecycle_language = artifact_data["cal.language.ontology-lifecycle/v2"]
    check("successor-context-identities-and-versions", gov_context["context_id"] == "cal.context.governance" and lifecycle_context["context_id"] == "cal.context.ontology-lifecycle" and all(item["version"] == "1.1.0-candidate.1" for item in (gov_context, gov_language, lifecycle_context, lifecycle_language)), {"governance": [gov_context["context_id"], gov_context["version"]], "ontology_lifecycle": [lifecycle_context["context_id"], lifecycle_context["version"]]})
    map_ref = "cal.context-map.governance-ontology-lifecycle/v1"
    check("explicit-single-map-reference", gov_context["context_map_refs"] == [map_ref] and lifecycle_context["context_map_refs"] == [map_ref], {"governance": gov_context["context_map_refs"], "ontology_lifecycle": lifecycle_context["context_map_refs"]})
    check("reciprocal-v2-context-language-pairs", gov_context["ubiquitous_language_ref"] == "cal.language.governance/v2" and gov_language["bounded_context_ref"] == "cal.context.governance/v2" and lifecycle_context["ubiquitous_language_ref"] == "cal.language.ontology-lifecycle/v2" and lifecycle_language["bounded_context_ref"] == "cal.context.ontology-lifecycle/v2", {"governance": [gov_context["ubiquitous_language_ref"], gov_language["bounded_context_ref"]], "ontology_lifecycle": [lifecycle_context["ubiquitous_language_ref"], lifecycle_language["bounded_context_ref"]]})

    gov_v1_language = load(LAB / "contexts/governance/v1/language.json")
    lifecycle_v1_language = load(LAB / "contexts/ontology-lifecycle/v1/language.json")
    vocabulary_fields = ("concept_refs", "expression_bindings", "relation_bindings")
    check("core-vocabularies-preserved", all(gov_language[field] == gov_v1_language[field] and lifecycle_language[field] == lifecycle_v1_language[field] for field in vocabulary_fields), {"fields": vocabulary_fields})

    context_map = load(LAB / "contexts/maps/governance-ontology-lifecycle/v1/map.json")
    relationship = context_map["relationships"][0]
    check("admitted-map-direction-preserved", len(context_map["relationships"]) == 1 and relationship["source_context_ref"] == "cal.context.governance/v1" and relationship["target_context_ref"] == "cal.context.ontology-lifecycle/v1" and relationship["direction"] == "source-to-target", relationship)
    check("map-endpoint-epoch-limitation-explicit", all(any("endpoint-remains-admitted-v1-predecessor" in residue for residue in context["residue_refs"]) for context in (gov_context, lifecycle_context)), {"governance": gov_context["residue_refs"], "ontology_lifecycle": lifecycle_context["residue_refs"]})

    gov_lineage = artifact_data["cal.context-lineage.governance.v1-to-v2"]
    lifecycle_lineage = artifact_data["cal.context-lineage.ontology-lifecycle.v1-to-v2"]
    check("exact-lineage-closure", gov_lineage["predecessor_context_ref"] == "cal.context.governance/v1" and gov_lineage["successor_context_refs"] == ["cal.context.governance/v2"] and lifecycle_lineage["predecessor_context_ref"] == "cal.context.ontology-lifecycle/v1" and lifecycle_lineage["successor_context_refs"] == ["cal.context.ontology-lifecycle/v2"] and all(item["lineage_kind"] == "successor" for item in (gov_lineage, lifecycle_lineage)), {"governance": [gov_lineage["predecessor_context_ref"], gov_lineage["successor_context_refs"]], "ontology_lifecycle": [lifecycle_lineage["predecessor_context_ref"], lifecycle_lineage["successor_context_refs"]]})
    check("lineage-inference-denied", all(item["equivalence_inferred"] is False and item["admission_inferred"] is False for item in (gov_lineage, lifecycle_lineage)), {"governance": [gov_lineage["equivalence_inferred"], gov_lineage["admission_inferred"]], "ontology_lifecycle": [lifecycle_lineage["equivalence_inferred"], lifecycle_lineage["admission_inferred"]]})

    migration = artifact_data["cal.context-migration.governance-ontology-lifecycle-v1-to-v2"]
    check("migration-identity-and-boundary", migration["migration_manifest_id"] == "cal.context-migration.governance-ontology-lifecycle-v1-to-v2" and migration["source_repository_ref"] == "repository:CyberAlchemy-lab" and migration["immutable"] is True, {"id": migration["migration_manifest_id"], "source": migration["source_repository_ref"], "immutable": migration["immutable"]})
    selections = {item["source_ref"]: item for item in migration["source_selections"]}
    preimages = {item["path"]: item["sha256"] for item in migration["preimages"]}
    source_current = all(sha(LAB / item["selector"].removeprefix("whole-file:")) == item["sha256"] and preimages.get(item["selector"].removeprefix("whole-file:")) == item["sha256"] for item in selections.values())
    check("source-selection-preimage-closure", len(selections) == len(preimages) == 5 and source_current, {"selections": selections, "preimages": preimages})
    dispositions = migration["dispositions"]
    check("one-disposition-per-source", len(dispositions) == len(selections) and {item["source_ref"] for item in dispositions} == set(selections) and len({item["source_ref"] for item in dispositions}) == len(dispositions), dispositions)
    destinations = {item["artifact_id"]: item["path"] for item in migration["destination_candidates"]}
    expected_destination_ids = {item["artifact_id"] for item in pack["canonical_artifacts"] if item["artifact_type"] != "context-migration-manifest"}
    check("destination-candidate-closure", set(destinations) == expected_destination_ids and all((LAB / path).is_file() for path in destinations.values()), destinations)
    postimage_results = []
    for item in migration["expected_postimages"]:
        match = re.search(r"sha256=([a-f0-9]{64})", item["expected_condition"])
        actual = sha(LAB / item["path"])
        postimage_results.append({"path": item["path"], "expected": match.group(1) if match else None, "actual": actual})
    check("expected-postimages-current", len(postimage_results) == 6 and all(item["expected"] == item["actual"] for item in postimage_results), postimage_results)
    order = migration["dependency_order"]
    check("dependency-order-complete", order[0] == "CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION" and order[-1] == "separate-migration-execution-decision" and len(order) == len(set(order)), order)

    owners = load(LAB / "authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json")
    assignments = {item["role_id"]: item for item in owners["role_assignments"]}
    gate_roles = {item["role_ref"].removeprefix("role:") for item in migration["owner_gates"]}
    check("owner-gates-active-and-separated", gate_roles <= set(assignments) and all(assignments[role]["principal_id"] == "person:<vrondelli>" and assignments[role]["decision_separation"] == "required" for role in gate_roles), {role: assignments.get(role) for role in sorted(gate_roles)})
    rollback = migration["rollback_boundary"]
    check("rollback-boundary-complete", all(term in rollback for term in ("no cutover", "undeleted", "restore every consumer", "five declared preimage digests", "preserve failed successor bytes", "new owner decision")), rollback)
    check("execution-authority-denied", migration["execution_authority"] is False and pack["migration_boundary"]["execution_authority"] is False, {"manifest": migration["execution_authority"], "pack": pack["migration_boundary"]["execution_authority"]})
    check("physical-source-relocation-excluded", any("No source-domain package" in item for item in migration["exclusions"]) and pack["migration_boundary"]["physical_source_package_relocation"] == "excluded-requires-successor-manifest", migration["exclusions"])

    projection_results = []
    for item in pack["canonical_artifacts"]:
        expected = generator.render_instance(artifact_data[item["artifact_id"]], item["artifact_type"])
        actual = (LAB / item["projection"]).read_text(encoding="utf-8")
        projection_results.append({"artifact_id": item["artifact_id"], "parity": actual == expected})
    check("deterministic-artifact-projections", all(item["parity"] for item in projection_results), projection_results)
    check("deterministic-pack-projection", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(pack), str(OUTPUT))

    hostile_migration = copy.deepcopy(migration)
    hostile_migration["execution_authority"] = True
    hostile_errors = list(Draft202012Validator({"$ref": "#/$defs/contextMigrationManifest", **schema}).iter_errors(hostile_migration))
    check("hostile-execution-authority-rejected", bool(hostile_errors), [error.message for error in hostile_errors])
    hostile_context = copy.deepcopy(gov_context)
    hostile_context["context_map_refs"] = []
    check("hostile-missing-map-reference-rejected", hostile_context["context_map_refs"] != [map_ref], hostile_context["context_map_refs"])
    hostile_lineage = copy.deepcopy(gov_lineage)
    hostile_lineage["equivalence_inferred"] = True
    hostile_lineage_errors = list(Draft202012Validator({"$ref": "#/$defs/contextLineageRecord", **schema}).iter_errors(hostile_lineage))
    check("hostile-inferred-lineage-rejected", bool(hostile_lineage_errors), [error.message for error in hostile_lineage_errors])
    check("claim-ceiling-preserved", all(term in pack["claim_ceiling"] for term in ("does not admit", "physical source relocation", "migration execution", "stable release")), pack["claim_ceiling"])

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-context-successor-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "current_gate_state": pack["current_gate"] if result == "PASS" else "not_evaluable",
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX05_CONTEXT_SUCCESSOR_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
