#!/usr/bin/env python3
"""Materialize Artifact Type/v3 and Definition/v2 metamodel successors."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
REGISTRY_PATH = LAB / "authority/artifact-types/candidates/0008-registry-snapshot-0002/registry.json"
DEFINITIONS_PATH = LAB / "authority/definitions/registry.json"
RELATIONS_PATH = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
SUCCESSOR_GENERATOR = LAB / "tooling/generators/artifact_type_successor.py"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definition_binding(name: str, definitions: dict) -> dict:
    did = f"cal.definition.{name}"
    ref = definitions["current_lookup"][did]
    row = next(item for item in definitions["entries"] if f"{item['definition_id']}@{item['version']}" == ref)
    return {"definition_ref": ref, "path": row["path"], "sha256": row["sha256"], "admission_posture": "admitted", "admission_decision_ref": row["admission_decision_ref"]}


def roles_for(kind: str, model: dict) -> list[dict]:
    roles = []
    for relation in model["entries"]:
        outgoing = sorted({pair["target_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        incoming = sorted({pair["source_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if outgoing: roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "source", "counterpart_kinds": outgoing})
        if incoming: roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "target", "counterpart_kinds": incoming})
    return sorted(roles, key=lambda row: (row["relation_kind_ref"], row["direction"]))


def shape(value: Any) -> dict:
    if value is None: return {"type": "null"}
    if isinstance(value, bool): return {"type": "boolean"}
    if isinstance(value, int): return {"type": "integer"}
    if isinstance(value, str): return {"type": "string", "minLength": 1}
    if isinstance(value, list):
        result = {"type": "array", "items": shape(value[0]) if value else {}}
        if value: result["minItems"] = 1
        if value and all(isinstance(item, str) for item in value): result["uniqueItems"] = True
        return result
    if isinstance(value, dict):
        return {"type": "object", "additionalProperties": False, "properties": {key: shape(item) for key, item in value.items()}, "required": list(value)}
    raise TypeError(type(value))


def successor_projection_module():
    spec = importlib.util.spec_from_file_location("successor_generator", SUCCESSOR_GENERATOR)
    module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module


def materialize_artifact_type_v3(registry: dict, definitions: dict, relations: dict) -> dict:
    target = LAB / "authority/artifact-types/artifact-type/v3"
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    predecessor = next(row for row in registry["admitted_contracts"] if row["artifact_type_ref"] == "cal.artifact-type.artifact-type/v2")
    binding = definition_binding("artifact-type", definitions)
    roles = roles_for("artifact-type", relations)
    artifact = {
        "schema_version": "cyberalchemy-lab-artifact-type/v3",
        "artifact_type_id": "cal.artifact-type.artifact-type",
        "artifact_type_ref": "cal.artifact-type.artifact-type/v3",
        "version": "3.0.0-candidate.1",
        "name": "Artifact Type",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v3", "semantic_kind": "artifact-type", "authority_kind": "none", "lifecycle_posture_ref": "candidate:step5-carrier-closure/v1"},
        "semantic_owner_ref": "role:artifact-type-owner",
        "semantic_definition_refs": [binding["definition_ref"]],
        "semantic_definition_bindings": [binding],
        "schema_ref": "cal.schema.artifact-type/v3",
        "schema_digest": "0" * 64,
        "predecessor_contract": {"artifact_type_ref": predecessor["artifact_type_ref"], "path": predecessor["artifact_path"], "sha256": predecessor["artifact_sha256"], "schema_path": predecessor["schema_path"], "schema_sha256": predecessor["schema_sha256"], "admission_decision_ref": predecessor["admission_decision_ref"]},
        "instance_contract": {"canonical_filename": "artifact.json", "human_filename": "ARTIFACT.md", "identity_field": "artifact_type_ref", "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-artifact-type/v3"}, "closed_representation": True, "required_semantic_fields": [], "forbidden_canonical_fields": ["implicit_admission", "embedded_status_as_effective_state", "directory_inference", "derived_authority"]},
        "distinct_validation_purpose": "Defines the complete closed contract for one Artifact Type descriptor, including semantic Definition bindings, instance schema, generated projection, validation, ownership, lifecycle posture, relation surface, typed residue, predecessor lineage, and claim ceiling.",
        "allowed_relation_kinds": sorted({role["relation_kind_ref"] for role in roles}),
        "relation_roles": roles,
        "orthogonality_rules": [
            {"rule_id": "AT3-TYPE-INSTANCE", "statement": "Artifact Type contract and artifact instance retain separate identities and lifecycle states."},
            {"rule_id": "AT3-DEFINITION-SCHEMA", "statement": "Semantic Definition, representation schema, validator, generated projection, admission decision, and activation remain separate governed artifacts and acts."},
            {"rule_id": "AT3-RELATION-SURFACE", "statement": "Reference-shaped fields do not create relations; only admitted Relation Kinds and exact Typed Relation instances connect endpoints."},
            {"rule_id": "AT3-SELF-APPLICATION", "statement": "Artifact Type/v3 may describe its own exact contract without inferring its admission, authority, or validity from self-description."},
        ],
        "registration_policy": {"legacy_registration_rule": "Preserve every admitted predecessor by exact path, digest, discriminator, and decision.", "new_registration_rule": "Require at least one current admitted semantic Definition, a closed schema, deterministic projection, executable validator, relation surface, owner, residue, and claim ceiling.", "candidate_rule": "Candidate validation has authority effect none.", "admission_rule": "Only an exact owner decision can admit reviewed bytes.", "non_effect": "Registration, schema validity, or registry inclusion does not admit an instance or activate a consumer."},
        "self_application": {"mode": "bounded-successor-self-description", "bound": "The schema validates this exact v3 descriptor shape and future v3 successor revisions under the same closed fields.", "non_effect": "Self-application creates no proof, admission, authority, or recursive runtime."},
        "registered_types": [{"artifact_type_ref": "cal.artifact-type.artifact-type/v3", "semantic_kind": "artifact-type", "semantic_definition_refs": [binding["definition_ref"]], "schema_path": "authority/artifact-types/artifact-type/v3/schema.json", "schema_selector": None, "schema_sha256": "0" * 64, "distinct_validation_purpose": "The metamodel carrier for governed Artifact Type contracts."}],
        "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": "tooling/generators/artifact_type_successor.py", "shared_generator_sha256": sha(SUCCESSOR_GENERATOR)},
        "four_facets": {"classification": "Artifact Type/v3 is the successor metamodel contract.", "schema": "schema.json closes every v3 metamodel field.", "human_continuation": "ARTIFACT.md and the self-witness projection are generated from canonical bytes.", "machine_checkable": "Self-conformance, predecessor preservation, Definition binding, relation surface, hostile cases, and projection parity are executable."},
        "validation_contract": {"validator_path": "authority/artifact-types/artifact-type/v3/validate.py", "positive_witness": "artifact.json", "positive_projection": "fixtures/valid/ARTIFACT-TYPE.md", "negative_witnesses": ["fixtures/invalid/authority.json", "fixtures/invalid/missing-definition.json", "fixtures/invalid/collapsed-as-schema.json", "fixtures/invalid/extra-field.json"], "assessment_scope": "metamodel-self-conformance-and-successor-contract", "admission_effect": "none", "required_checks": ["closed v3 self-schema", "exact admitted v2 predecessor", "current Artifact Type Definition", "closed relation surface", "four hostile rejections", "bounded self-application", "deterministic projections"]},
        "typed_residue": [{"residue_id": "AT3-R1", "missing": "Artifact Type owner admission for this exact v3 successor.", "owner_ref": "role:artifact-type-owner", "consequence": "v3 remains candidate-only and v2 remains admitted-current."}, {"residue_id": "AT3-R2", "missing": "Successor registry refresh and explicit consumer adoption after admission.", "owner_ref": "role:migration-consumer-owner", "consequence": "No existing carrier or consumer is silently rebound to v3."}],
        "claim_ceiling": "This candidate defines Artifact Type/v3 and validates its bounded self-description. PASS proves the exact schema, predecessor, Definition binding, relation surface, hostile cases, and projections; it does not admit v3, transition v2, admit another Artifact Type or instance, or activate a consumer or runtime."
    }
    artifact["instance_contract"]["required_semantic_fields"] = list(artifact)
    schema = shape(artifact)
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/artifact-type/v3", "title": "CyberAlchemy Lab Artifact Type v3 candidate"})
    for key, const in {"schema_version": artifact["schema_version"], "artifact_type_id": artifact["artifact_type_id"], "artifact_type_ref": artifact["artifact_type_ref"], "version": artifact["version"], "name": artifact["name"], "status": artifact["status"], "authority_effect": artifact["authority_effect"]}.items(): schema["properties"][key] = {"const": const}
    schema["properties"]["schema_digest"] = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
    schema["properties"]["registered_types"]["items"]["properties"]["schema_sha256"] = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
    dump(target / "schema.json", schema)
    artifact["schema_digest"] = sha(target / "schema.json")
    artifact["registered_types"][0]["schema_sha256"] = artifact["schema_digest"]
    dump(target / "artifact.json", artifact)
    invalid = copy.deepcopy(artifact); invalid["authority_effect"] = "admit"; dump(target / "fixtures/invalid/authority.json", invalid)
    invalid = copy.deepcopy(artifact); invalid["semantic_definition_refs"] = []; dump(target / "fixtures/invalid/missing-definition.json", invalid)
    invalid = copy.deepcopy(artifact); invalid["artifact_type_ref"] = "cal.artifact-type.schema/v1"; dump(target / "fixtures/invalid/collapsed-as-schema.json", invalid)
    invalid = copy.deepcopy(artifact); invalid["implicit_admission"] = True; dump(target / "fixtures/invalid/extra-field.json", invalid)
    shutil.copyfile(ROOT / "templates/artifact-type-v3-validate.py", target / "validate.py")
    module = successor_projection_module()
    (target / "ARTIFACT.md").write_text(module.render_artifact(artifact), encoding="utf-8")
    self_projection = target / "fixtures/valid/ARTIFACT-TYPE.md"
    self_projection.parent.mkdir(parents=True, exist_ok=True)
    self_projection.write_text(module.render_instance(artifact, artifact), encoding="utf-8")
    return {"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((target / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(target / "artifact.json"), "schema_sha256": sha(target / "schema.json"), "predecessor_ref": predecessor["artifact_type_ref"], "definition_ref": binding["definition_ref"]}


def replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items(): value = value.replace(old, new)
        return value
    if isinstance(value, list): return [replace_strings(item, replacements) for item in value]
    if isinstance(value, dict): return {key: replace_strings(item, replacements) for key, item in value.items()}
    return value


def materialize_definition_v2(registry: dict, definitions: dict, relations: dict) -> dict:
    source = LAB / "authority/artifact-types/definition/v1"
    target = LAB / "authority/artifact-types/definition/v2"
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    predecessor = next(row for row in registry["admitted_contracts"] if row["artifact_type_ref"] == "cal.artifact-type.definition/v1")
    binding = definition_binding("definition", definitions)
    roles = roles_for("definition", relations)
    relation_ids = [row["relation_kind_id"] for row in relations["entries"]]
    schema = replace_strings(load(source / "schema.json"), {"cyberalchemy-lab-definition/v1": "cyberalchemy-lab-definition/v2", "cal.artifact-type.definition/v1": "cal.artifact-type.definition/v2", "cal.schema.definition/v1": "cal.schema.definition/v2", "cal.generator.definition-markdown/v1": "cal.generator.definition-markdown/v2"})
    schema["$id"] = "https://cyberalchemy.local/schemas/definition/v2"
    schema["title"] = "CyberAlchemy Lab Definition v2 candidate instance"
    schema["$defs"]["typedRelation"]["properties"]["relation_kind_ref"] = {"enum": relation_ids}
    dump(target / "schema.json", schema)
    shutil.copyfile(source / "generator.py", target / "generator.py")
    generator_text = (target / "generator.py").read_text(encoding="utf-8").replace("Definition/v1", "Definition/v2").replace('cal.generator.definition-markdown/v1', 'cal.generator.definition-markdown/v2')
    (target / "generator.py").write_text(generator_text, encoding="utf-8")
    witness = replace_strings(load(source / "fixtures/valid/definition.json"), {"cyberalchemy-lab-definition/v1": "cyberalchemy-lab-definition/v2", "cal.artifact-type.definition/v1": "cal.artifact-type.definition/v2", "cal.schema.definition/v1": "cal.schema.definition/v2", "cal.generator.definition-markdown/v1": "cal.generator.definition-markdown/v2"})
    witness["schema_digest"] = sha(target / "schema.json")
    witness["source_direction"]["generator_sha256"] = sha(target / "generator.py")
    dump(target / "fixtures/valid/definition.json", witness)
    instance_contract = {"canonical_filename": "definition.json", "human_filename": "DEFINITION.md", "identity_field": "definition_id", "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-definition/v2"}, "closed_representation": True, "required_semantic_fields": schema["required"], "forbidden_canonical_fields": ["implicit_admission", "implicit_authority", "untyped_relation", "runtime_activation"]}
    artifact = {
        "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2", "artifact_type_id": "cal.artifact-type.definition", "artifact_type_ref": "cal.artifact-type.definition/v2", "version": "2.0.0-candidate.1", "name": "Definition", "status": "candidate-unadmitted", "authority_effect": "none",
        "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v2", "semantic_kind": "definition", "authority_kind": "semantic-authority", "lifecycle_posture_ref": "candidate:step5-carrier-closure/v1"},
        "artifact_type_root_binding": {"path": "authority/artifact-types/artifact-type/v2/artifact.json", "sha256": sha(LAB / "authority/artifact-types/artifact-type/v2/artifact.json"), "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"},
        "predecessor_contract": {"artifact_type_ref": predecessor["artifact_type_ref"], "path": predecessor["artifact_path"], "sha256": predecessor["artifact_sha256"], "schema_path": predecessor["schema_path"], "schema_sha256": predecessor["schema_sha256"], "admission_decision_ref": predecessor["admission_decision_ref"]},
        "semantic_owner_ref": "role:definition-owner", "semantic_definition_refs": [binding["definition_ref"]], "semantic_definition_bindings": [binding], "schema_ref": "cal.schema.definition/v2", "schema_digest": sha(target / "schema.json"), "instance_contract": instance_contract,
        "distinct_validation_purpose": "Carries one versioned semantic Definition with three synchronized voices, explicit scope, boundaries, provenance, consumers, drift route, evidence, residue, and Typed Relations restricted to the closed Relation Kind model.",
        "allowed_relation_kinds": sorted({role["relation_kind_ref"] for role in roles}), "relation_roles": roles,
        "orthogonality_rules": [{"rule_id": "DEF2-MEANING-CARRIER", "statement": "Definition meaning, Definition artifact instance, Definition Artifact Type, schema, source, and admission decision remain separate identities."}, {"rule_id": "DEF2-VOICE-SYNC", "statement": "Scientific, plain-language, and domain-context voices express one meaning and cannot create independent authority axes."}, {"rule_id": "DEF2-TYPED-RELATIONS", "statement": "Every embedded relation reference resolves to one of the 23 closed candidate Relation Kinds; embedding a reference does not create a Typed Relation instance."}, {"rule_id": "DEF2-AUTHORITY", "statement": "Schema validity, source provenance, evidence, or candidate status cannot imply admission, truth, implementation, activation, or external effect."}],
        "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": "tooling/generators/artifact_type_successor.py", "shared_generator_sha256": sha(SUCCESSOR_GENERATOR)},
        "four_facets": {"classification": "Candidate Definition/v2 successor under Artifact Type/v2.", "schema": "schema.json closes the Definition representation and exact Relation Kind vocabulary.", "human_continuation": "ARTIFACT.md and DEFINITION.md are deterministic projections from separate canonical descriptor and instance files.", "machine_checkable": "Predecessor, Definition binding, schema, 23-kind vocabulary, hostile fixtures, and both projections are executable."},
        "validation_contract": {"validator_path": "authority/artifact-types/definition/v2/validate.py", "positive_witness": "fixtures/valid/definition.json", "positive_projection": "fixtures/valid/DEFINITION.md", "negative_witnesses": ["fixtures/invalid/missing-domain-context.json", "fixtures/invalid/additional-property.json", "fixtures/invalid/undeclared-relation-kind.json", "fixtures/invalid/authority-field.json"], "assessment_scope": "definition-v2-schema-successor-relation-vocabulary-and-projection", "admission_effect": "none", "required_checks": ["exact admitted Definition/v1 predecessor", "current Definition Definition", "closed v2 schema", "23 Relation Kind vocabulary", "four hostile rejections", "Definition projection parity", "Artifact Type projection parity"]},
        "typed_residue": [{"residue_id": "DEF2-R1", "missing": "Artifact Type owner admission for this exact Definition/v2 successor.", "owner_ref": "role:artifact-type-owner", "consequence": "Definition/v2 remains candidate-only and Definition/v1 remains admitted-current."}, {"residue_id": "DEF2-R2", "missing": "Migration decisions for existing Definition/v1 instances and consumer adoption.", "owner_ref": "role:definition-owner", "consequence": "Existing Definitions remain governed by their current exact contracts until separately migrated."}],
        "claim_ceiling": "This candidate defines Definition/v2 with a closed 23-kind relation vocabulary. PASS proves the exact predecessor, schema, Definition binding, fixtures, and projections; it does not admit v2, transition v1, migrate any Definition, admit a Typed Relation, or activate a consumer or runtime."
    }
    dump(target / "artifact.json", artifact)
    invalid = copy.deepcopy(witness); invalid["voices"].pop("domain_context"); dump(target / "fixtures/invalid/missing-domain-context.json", invalid)
    invalid = copy.deepcopy(witness); invalid["unknown_field"] = True; dump(target / "fixtures/invalid/additional-property.json", invalid)
    invalid = copy.deepcopy(witness); invalid["typed_relations"] = [{"relation_kind_ref": "relation.not-declared", "from_ref": "definition:a", "to_ref": "source:b", "owner_ref": "role:definition-owner"}]; dump(target / "fixtures/invalid/undeclared-relation-kind.json", invalid)
    invalid = copy.deepcopy(witness); invalid["authority_effect"] = "admit"; dump(target / "fixtures/invalid/authority-field.json", invalid)
    shutil.copyfile(ROOT / "templates/definition-v2-validate.py", target / "validate.py")
    generator_spec = importlib.util.spec_from_file_location("definition_v2_generator", target / "generator.py")
    generator = importlib.util.module_from_spec(generator_spec); assert generator_spec and generator_spec.loader; generator_spec.loader.exec_module(generator)
    (target / "fixtures/valid/DEFINITION.md").write_text(generator.render(witness), encoding="utf-8")
    module = successor_projection_module(); (target / "ARTIFACT.md").write_text(module.render_artifact(artifact), encoding="utf-8")
    return {"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((target / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(target / "artifact.json"), "schema_sha256": sha(target / "schema.json"), "predecessor_ref": predecessor["artifact_type_ref"], "definition_ref": binding["definition_ref"]}


def main() -> None:
    registry = load(REGISTRY_PATH); definitions = load(DEFINITIONS_PATH); relations = load(RELATIONS_PATH)
    entries = [materialize_artifact_type_v3(registry, definitions, relations), materialize_definition_v2(registry, definitions, relations)]
    dump(ROOT / "metamodel-successor-postimages.json", {"schema_version": "cyberalchemy-lab-step5-metamodel-successor-postimages/v1", "status": "candidate-materialized", "authority_effect": "none", "count": 2, "entries": entries, "claim_ceiling": "This manifest identifies two candidate metamodel successors. It does not admit them, transition their predecessors, migrate instances, or activate consumers."})


if __name__ == "__main__": main()
