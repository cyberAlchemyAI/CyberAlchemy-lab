#!/usr/bin/env python3
"""Collect-all validator for one normalized CTX07 artifact-type candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

CONFIG = {
    "bounded-context": {"schema_def": "boundedContext", "identity": "context_id"},
    "context-map": {"schema_def": "contextMap", "identity": "context_map_id"},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_invariants(slug: str, instance: dict) -> list[tuple[str, bool, object]]:
    if slug == "bounded-context":
        forbidden = {"context_map_refs", "canonical_reverse_membership_index", "map_membership"}
        return [
            ("context-language-distinct", instance["context_id"] != instance["ubiquitous_language_ref"], {"context": instance["context_id"], "language": instance["ubiquitous_language_ref"]}),
            ("bounded-context-has-no-map-backreference", not forbidden.intersection(instance), sorted(forbidden.intersection(instance))),
        ]
    contexts = set(instance["context_refs"])
    relationships = instance["relationships"]
    relationship_ids = [item["relationship_id"] for item in relationships]
    referenced_contexts = {item[endpoint] for item in relationships for endpoint in ("source_context_ref", "target_context_ref")}
    return [
        ("map-endpoints-closed", all(item["source_context_ref"] in contexts and item["target_context_ref"] in contexts for item in relationships), sorted(contexts)),
        ("map-direction-not-reflexive", all(item["source_context_ref"] != item["target_context_ref"] for item in relationships), relationships),
        ("relationship-identities-unique", len(relationship_ids) == len(set(relationship_ids)), relationship_ids),
        ("map-endpoint-set-exact", referenced_contexts == contexts, {"declared": sorted(contexts), "related": sorted(referenced_contexts)}),
    ]


def run(package_root: Path, slug: str) -> int:
    lab = package_root.parents[3]
    config = CONFIG[slug]
    artifact_path = package_root / "artifact.json"
    schema_path = package_root / "schema.json"
    core_schema_path = lab / "tooling/schemas/ctx07/v2/schema.json"
    shared_generator_path = lab / "tooling/generators/ctx07_artifact.py"
    shared_validator_path = lab / "tooling/validators/ctx07_artifact_type.py"
    generator_path = package_root / "generator.py"
    validator_path = package_root / "validate.py"
    receipt_path = package_root / "receipts/validation.json"
    artifact = load(artifact_path)
    wrapper_schema = load(schema_path)
    core_schema = load(core_schema_path)
    validation_schema = dict(core_schema)
    validation_schema["$ref"] = f"#/$defs/{config['schema_def']}"
    Draft202012Validator.check_schema(validation_schema)
    validator = Draft202012Validator(validation_schema)
    valid_path = package_root / artifact["validation_contract"]["positive_witness"]
    valid_projection_path = package_root / artifact["validation_contract"]["positive_projection"]
    valid = load(valid_path)
    renderer = load_module("ctx07_renderer", shared_generator_path)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("artifact-identity", artifact.get("artifact_type_id") == f"cal.artifact-type.{slug}" and artifact.get("artifact_type_ref") == f"cal.artifact-type.{slug}/v2", {"id": artifact.get("artifact_type_id"), "ref": artifact.get("artifact_type_ref")})
    check("candidate-no-authority", artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none", {"status": artifact.get("status"), "authority_effect": artifact.get("authority_effect")})
    check("artifact-type-root-binding", artifact.get("classification", {}).get("artifact_type_ref") == "cal.artifact-type.artifact-type/v1", artifact.get("classification"))
    expected_wrapper = f"../../../../tooling/schemas/ctx07/v2/schema.json#/$defs/{config['schema_def']}"
    check("schema-wrapper-key", wrapper_schema.get("$ref") == expected_wrapper, wrapper_schema.get("$ref"))
    check("schema-digest-current", artifact.get("schema_digest") == sha256(schema_path), sha256(schema_path))

    shared_paths = {"schema": core_schema_path, "generator": shared_generator_path, "validator": shared_validator_path}
    shared_results = []
    for name, path in shared_paths.items():
        binding = artifact["shared_mechanics"][name]
        shared_results.append({"name": name, "path": binding["path"], "expected": binding["sha256"], "actual": sha256(path), "current": binding["sha256"] == sha256(path)})
    check("shared-mechanics-current", all(item["current"] for item in shared_results), shared_results)
    check("generator-digest-current", artifact["source_direction"]["generator_sha256"] == sha256(generator_path), sha256(generator_path))
    check("machine-human-direction", artifact["source_direction"]["canonical"] == "artifact.json" and artifact["source_direction"]["human_projection"] == "ARTIFACT.md" and artifact["source_direction"]["projection_policy"] == "generated-only", artifact["source_direction"])
    check("four-facets-complete", set(artifact.get("four_facets", {})) == {"classification", "schema", "human_continuation", "machine_checkable"}, sorted(artifact.get("four_facets", {})))
    check("orthogonality-rules-enforceable", len(artifact.get("orthogonality_rules", [])) >= 3 and all(item.get("validation_mode") in {"deterministic", "hybrid"} for item in artifact["orthogonality_rules"]), artifact["orthogonality_rules"])

    binding_results = []
    for binding_id, binding in artifact["prerequisite_bindings"].items():
        path = lab / binding["path"]
        actual = sha256(path) if path.is_file() else None
        binding_results.append({"binding_id": binding_id, "path": binding["path"], "expected": binding["sha256"], "actual": actual, "current": actual == binding["sha256"]})
    check("prerequisite-bindings-current", all(item["current"] for item in binding_results), binding_results)

    definition = artifact["definition_binding"]
    definition_path = lab / definition["path"]
    definition_record = load(definition_path)
    registry = load(lab / artifact["prerequisite_bindings"]["definition_registry"]["path"])
    exact_definition_ref = f"{definition['definition_id']}@{definition['version']}"
    registry_row = next((item for item in registry["entries"] if item["definition_id"] == definition["definition_id"] and item["version"] == definition["version"]), None)
    check("definition-binding-current", sha256(definition_path) == definition["sha256"] and definition_record["definition_id"] == definition["definition_id"] and definition_record["version"] == definition["version"], {"expected": definition["sha256"], "actual": sha256(definition_path)})
    check("definition-admitted-and-current", registry_row is not None and registry_row["sha256"] == definition["sha256"] and registry_row["lifecycle_state"] == "admitted" and registry["current_lookup"].get(definition["definition_id"]) == exact_definition_ref, {"row": registry_row, "lookup": registry["current_lookup"].get(definition["definition_id"])})

    predecessor = artifact["predecessor_artifact_type"]
    predecessor_path = lab / predecessor["path"]
    ctx01_decision = load(lab / predecessor["admission_decision_path"])
    admitted_row = next((item for item in ctx01_decision["admitted_artifact_types"] if item["artifact_type_ref"] == predecessor["artifact_type_ref"]), None)
    check("predecessor-artifact-type-preserved-and-admitted", sha256(predecessor_path) == predecessor["sha256"] and admitted_row is not None and admitted_row["artifact_sha256"] == predecessor["sha256"] and sha256(lab / predecessor["admission_decision_path"]) == predecessor["admission_decision_sha256"], {"actual": sha256(predecessor_path), "expected": predecessor["sha256"], "admitted_row": admitted_row})

    schema_errors = [error.message for error in validator.iter_errors(valid)]
    check("positive-witness-valid", not schema_errors, schema_errors)
    check("positive-identity-explicit", bool(valid.get(config["identity"])), valid.get(config["identity"]))
    check("positive-candidate-no-authority", valid.get("status") == "candidate-unadmitted" and valid.get("authority_effect") == "none", {"status": valid.get("status"), "authority_effect": valid.get("authority_effect")})
    check("fixture-generator-digest-current", valid["source_direction"]["generator_sha256"] == sha256(shared_generator_path), valid["source_direction"])

    invalid_results = []
    for path in sorted((package_root / "fixtures/invalid").glob("*.json")):
        invalid = load(path)
        errors = [error.message for error in validator.iter_errors(invalid)]
        try:
            semantic_failures = [check_id for check_id, ok, _ in semantic_invariants(slug, invalid) if not ok]
        except (KeyError, TypeError):
            semantic_failures = []
        invalid_results.append({"fixture": path.name, "schema_errors": errors, "semantic_failures": semantic_failures, "rejected": bool(errors or semantic_failures)})
    check("hostile-fixtures-rejected", len(invalid_results) >= 2 and all(item["rejected"] for item in invalid_results), invalid_results)
    for check_id, ok, detail in semantic_invariants(slug, valid):
        check(check_id, ok, detail)

    instance_a = renderer.render_instance(valid, slug)
    instance_b = renderer.render_instance(valid, slug)
    check("instance-two-run-determinism", instance_a == instance_b, hashlib.sha256(instance_a.encode()).hexdigest())
    check("instance-projection-parity", valid_projection_path.is_file() and valid_projection_path.read_text(encoding="utf-8") == instance_a, str(valid_projection_path.relative_to(lab)))
    artifact_a = renderer.render_artifact_type(artifact)
    artifact_b = renderer.render_artifact_type(artifact)
    artifact_projection = package_root / "ARTIFACT.md"
    check("artifact-two-run-determinism", artifact_a == artifact_b, hashlib.sha256(artifact_a.encode()).hexdigest())
    check("artifact-projection-parity", artifact_projection.is_file() and artifact_projection.read_text(encoding="utf-8") == artifact_a, str(artifact_projection.relative_to(lab)))

    membership_path = None
    if slug == "context-map":
        membership_path = package_root / artifact["validation_contract"]["generated_membership_projection"]
        map_digest = sha256(valid_path)
        map_source = (str(valid_path.relative_to(lab)), valid, map_digest)
        projection_a = renderer.build_membership_index([map_source])
        projection_b = renderer.build_membership_index([map_source])
        stored_projection = load(membership_path)
        projection_schema = dict(core_schema)
        projection_schema["$ref"] = "#/$defs/contextMapMembershipIndexProjection"
        projection_errors = [error.message for error in Draft202012Validator(projection_schema).iter_errors(stored_projection)]
        check("membership-projection-schema-valid", not projection_errors, projection_errors)
        check("membership-projection-two-run-determinism", projection_a == projection_b, hashlib.sha256((json.dumps(projection_a, indent=2, sort_keys=True) + "\n").encode()).hexdigest())
        check("membership-projection-parity", stored_projection == projection_a, stored_projection)
        check("membership-projection-noncanonical", stored_projection["canonical"] is False and stored_projection["authority_effect"] == "none" and all(item["path"].endswith("/map.json") for item in stored_projection["generated_from"]), stored_projection)

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx07-artifact-type-validation/v1",
        "artifact_type_ref": artifact.get("artifact_type_ref"),
        "candidate_version": artifact.get("version"),
        "result": result,
        "authority_effect": "evidence-only-does-not-admit-artifact-type",
        "checks": checks,
        "materials": {
            "artifact_json_sha256": sha256(artifact_path),
            "artifact_md_sha256": sha256(artifact_projection) if artifact_projection.is_file() else None,
            "schema_json_sha256": sha256(schema_path),
            "shared_schema_sha256": sha256(core_schema_path),
            "shared_generator_sha256": sha256(shared_generator_path),
            "shared_validator_sha256": sha256(shared_validator_path),
            "generator_sha256": sha256(generator_path),
            "validator_sha256": sha256(validator_path),
            "valid_fixture_sha256": sha256(valid_path),
            "valid_projection_sha256": sha256(valid_projection_path) if valid_projection_path.is_file() else None,
            "membership_projection_sha256": sha256(membership_path) if membership_path else None,
        },
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "claim_ceiling": artifact.get("claim_ceiling"),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX07_{slug.upper().replace('-', '_')}_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1
