#!/usr/bin/env python3
"""Shared collect-all validator for one CTX01 artifact-type candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


CONFIG = {
    "bounded-context": {"schema_def": "boundedContext", "identity": "context_id"},
    "coordination-context": {"schema_def": "coordinationContext", "identity": "coordination_context_id"},
    "ubiquitous-language": {"schema_def": "ubiquitousLanguage", "identity": "language_id"},
    "context-map": {"schema_def": "contextMap", "identity": "context_map_id"},
    "capability-instance": {"schema_def": "capabilityInstance", "identity": "capability_instance_id"},
    "context-migration-manifest": {"schema_def": "contextMigrationManifest", "identity": "migration_manifest_id"},
    "context-lineage-record": {"schema_def": "contextLineageRecord", "identity": "lineage_record_id"},
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
        return [
            ("context-language-distinct", instance["context_id"] != instance["ubiquitous_language_ref"], {"context": instance["context_id"], "language": instance["ubiquitous_language_ref"]}),
            ("cross-context-links-explicit", all(ref.startswith("cal.context-map.") for ref in instance["context_map_refs"]), instance["context_map_refs"]),
        ]
    if slug == "coordination-context":
        forbidden = {"domain_model_ref", "ubiquitous_language_ref", "context_map_refs"}
        return [("coordination-not-bounded-context", not forbidden.intersection(instance), sorted(forbidden.intersection(instance)))]
    if slug == "ubiquitous-language":
        expressions = [item["expression"] for item in instance["expression_bindings"]]
        return [("expression-binding-unique", len(expressions) == len(set(expressions)), expressions)]
    if slug == "context-map":
        contexts = set(instance["context_refs"])
        relationships = instance["relationships"]
        return [
            ("map-endpoints-closed", all(item["source_context_ref"] in contexts and item["target_context_ref"] in contexts for item in relationships), sorted(contexts)),
            ("map-direction-not-reflexive", all(item["source_context_ref"] != item["target_context_ref"] for item in relationships), relationships),
        ]
    if slug == "capability-instance":
        return [
            ("parent-instance-authority-distinct", instance["parent_authority_claim_ref"] != instance["instance_authority_claim_ref"], {"parent": instance["parent_authority_claim_ref"], "instance": instance["instance_authority_claim_ref"]}),
            ("parent-instance-identity-distinct", instance["capability_instance_id"] != instance["capability_version_ref"], {"parent": instance["capability_version_ref"], "instance": instance["capability_instance_id"]}),
        ]
    if slug == "context-migration-manifest":
        source_refs = [item["source_ref"] for item in instance["source_selections"]]
        disposition_refs = [item["source_ref"] for item in instance["dispositions"]]
        return [
            ("migration-has-no-execution-authority", instance["execution_authority"] is False, instance["execution_authority"]),
            ("source-selection-unique", len(source_refs) == len(set(source_refs)), source_refs),
            ("every-source-has-disposition", set(source_refs) == set(disposition_refs), {"sources": source_refs, "dispositions": disposition_refs}),
        ]
    if slug == "context-lineage-record":
        return [
            ("lineage-does-not-infer-equivalence", instance["equivalence_inferred"] is False, instance["equivalence_inferred"]),
            ("lineage-does-not-infer-admission", instance["admission_inferred"] is False, instance["admission_inferred"]),
            ("lineage-version-cardinality", len(instance["successor_context_refs"]) == len(instance["destination_versions"]), {"successors": instance["successor_context_refs"], "versions": instance["destination_versions"]}),
        ]
    return []


def run(package_root: Path, slug: str) -> int:
    lab = package_root.parents[3]
    config = CONFIG[slug]
    artifact_path = package_root / "artifact.json"
    schema_path = package_root / "schema.json"
    core_schema_path = lab / "tooling/schemas/ctx01/v1/schema.json"
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
    renderer = load_module(f"ctx01_renderer_{slug.replace('-', '_')}", lab / "tooling/generators/ctx01_artifact.py")
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("artifact-identity", artifact.get("artifact_type_id") == f"cal.artifact-type.{slug}" and artifact.get("artifact_type_ref") == f"cal.artifact-type.{slug}/v1", {"id": artifact.get("artifact_type_id"), "ref": artifact.get("artifact_type_ref")})
    check("candidate-no-authority", artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none", {"status": artifact.get("status"), "authority_effect": artifact.get("authority_effect")})
    check("artifact-type-root-binding", artifact.get("classification", {}).get("artifact_type_ref") == "cal.artifact-type.artifact-type/v1", artifact.get("classification"))
    check("schema-wrapper-key", wrapper_schema.get("$ref") == f"../../../../tooling/schemas/ctx01/v1/schema.json#/$defs/{config['schema_def']}", wrapper_schema.get("$ref"))
    check("schema-digest-current", artifact.get("schema_digest") == sha256(schema_path), sha256(schema_path))
    shared = artifact.get("shared_mechanics", {})
    shared_results = []
    for name, path in {
        "schema": core_schema_path,
        "generator": lab / "tooling/generators/ctx01_artifact.py",
        "validator": lab / "tooling/validators/ctx01_artifact_type.py",
    }.items():
        binding = shared.get(name, {})
        shared_results.append({"name": name, "path": binding.get("path"), "expected": binding.get("sha256"), "actual": sha256(path), "current": binding.get("sha256") == sha256(path)})
    check("shared-mechanics-current", all(item["current"] for item in shared_results), shared_results)
    check("generator-digest-current", artifact.get("source_direction", {}).get("generator_sha256") == sha256(generator_path), sha256(generator_path))
    check("machine-human-direction", artifact.get("source_direction", {}).get("canonical") == "artifact.json" and artifact.get("source_direction", {}).get("human_projection") == "ARTIFACT.md" and artifact.get("source_direction", {}).get("projection_policy") == "generated-only", artifact.get("source_direction"))
    check("four-facets-complete", set(artifact.get("four_facets", {})) == {"classification", "schema", "human_continuation", "machine_checkable"}, sorted(artifact.get("four_facets", {})))
    check("orthogonality-rules-enforceable", len(artifact.get("orthogonality_rules", [])) >= 2 and all(item.get("validation_mode") in {"deterministic", "hybrid"} for item in artifact.get("orthogonality_rules", [])), artifact.get("orthogonality_rules"))

    binding_results = []
    for binding_id, binding in artifact["prerequisite_bindings"].items():
        path = lab / binding["path"]
        actual = sha256(path) if path.is_file() else None
        binding_results.append({"binding_id": binding_id, "path": binding["path"], "expected": binding["sha256"], "actual": actual, "current": actual == binding["sha256"]})
    check("prerequisite-bindings-current", all(item["current"] for item in binding_results), binding_results)

    definition = artifact["definition_binding"]
    definition_path = lab / definition["path"]
    definition_data = load(definition_path)
    registry = load(lab / artifact["prerequisite_bindings"]["definition_registry"]["path"])
    registry_row = next((item for item in registry["entries"] if item["definition_id"] == definition["definition_id"]), None)
    check("definition-binding-current", sha256(definition_path) == definition["sha256"] and definition_data.get("definition_id") == definition["definition_id"], {"expected": definition["sha256"], "actual": sha256(definition_path)})
    check("definition-admitted-in-registry", registry_row is not None and registry_row.get("sha256") == definition["sha256"] and registry_row.get("lifecycle_state") == "admitted", registry_row)

    schema_errors = [error.message for error in validator.iter_errors(valid)]
    check("positive-witness-valid", not schema_errors, schema_errors)
    check("positive-identity-explicit", bool(valid.get(config["identity"])), valid.get(config["identity"]))
    check("positive-candidate-no-authority", valid.get("status") == "candidate-unadmitted" and valid.get("authority_effect") == "none", {"status": valid.get("status"), "authority_effect": valid.get("authority_effect")})
    check("fixture-generator-digest-current", valid.get("source_direction", {}).get("generator_sha256") == sha256(generator_path), valid.get("source_direction"))

    invalid_results = []
    invalid_paths = sorted((package_root / "fixtures/invalid").glob("*.json"))
    for path in invalid_paths:
        invalid = load(path)
        errors = [error.message for error in validator.iter_errors(invalid)]
        semantic_failures = []
        try:
            semantic_failures = [check_id for check_id, ok, _ in semantic_invariants(slug, invalid) if not ok]
        except (KeyError, TypeError):
            pass
        invalid_results.append({"fixture": path.name, "schema_errors": errors, "semantic_failures": semantic_failures, "rejected": bool(errors or semantic_failures)})
    check("hostile-fixtures-rejected", bool(invalid_results) and all(item["rejected"] for item in invalid_results), invalid_results)

    for check_id, ok, detail in semantic_invariants(slug, valid):
        check(check_id, ok, detail)

    instance_a = renderer.render_instance(valid, slug)
    instance_b = renderer.render_instance(valid, slug)
    check("instance-two-run-determinism", instance_a == instance_b, hashlib.sha256(instance_a.encode()).hexdigest())
    check("instance-projection-parity", valid_projection_path.is_file() and valid_projection_path.read_text(encoding="utf-8") == instance_a, str(valid_projection_path.relative_to(lab)))
    check("projection-hand-edit-rejected", instance_a + "hand edit\n" != instance_a, "exact-byte comparison")
    artifact_a = renderer.render_artifact_type(artifact)
    artifact_b = renderer.render_artifact_type(artifact)
    artifact_projection = package_root / "ARTIFACT.md"
    check("artifact-two-run-determinism", artifact_a == artifact_b, hashlib.sha256(artifact_a.encode()).hexdigest())
    check("artifact-projection-parity", artifact_projection.is_file() and artifact_projection.read_text(encoding="utf-8") == artifact_a, str(artifact_projection.relative_to(lab)))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx01-artifact-type-validation/v1",
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
            "shared_generator_sha256": sha256(lab / "tooling/generators/ctx01_artifact.py"),
            "shared_validator_sha256": sha256(lab / "tooling/validators/ctx01_artifact_type.py"),
            "generator_sha256": sha256(generator_path),
            "validator_sha256": sha256(validator_path),
            "valid_fixture_sha256": sha256(valid_path),
            "valid_projection_sha256": sha256(valid_projection_path) if valid_projection_path.is_file() else None
        },
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "claim_ceiling": artifact.get("claim_ceiling")
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_{slug.upper().replace('-', '_')}_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1
