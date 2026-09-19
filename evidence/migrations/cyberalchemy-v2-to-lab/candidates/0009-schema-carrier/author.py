#!/usr/bin/env python3
import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module

TEXT = {"type": "string", "pattern": "\\S"}


def obj(properties):
    return {"type": "object", "additionalProperties": False, "required": sorted(properties), "properties": properties}


def array(item, minimum=0, maximum=100):
    return {"type": "array", "minItems": minimum, "maxItems": maximum, "items": item}


def build():
    strings = {**array(TEXT), "uniqueItems": True}
    bound = {"type": "integer", "minimum": 0}
    maximum = {"anyOf": [bound, {"type": "null"}]}
    contract = obj({"schema_version": {"const": "cyberalchemy-lab-schema-carrier/v1"},
        "artifact_type_ref": {"const": "cal.artifact-type.schema/v1"}, "schema_id": TEXT,
        "status": {"const": "candidate-unadmitted"}, "authority_effect": {"const": "none"},
        "owner_ref": TEXT, "scope_ref": TEXT,
        "relative_level": obj({"schema_level_ref": TEXT, "occupant_level_ref": TEXT}),
        "profile": {"const": "candidate:finite-typed-graph/v1"}, "kinds": {**strings, "minItems": 1},
        "constraints": array(obj({"kind_ref": TEXT, "closed_fields": {"type": "boolean"},
            "fields": array(obj({"name": TEXT, "value_type": {"enum": ["string", "integer", "boolean"]}, "required": {"type": "boolean"}}))})),
        "relations": strings,
        "connection_rules": array(obj({"relation_ref": TEXT, "source_kind": TEXT, "target_kind": TEXT,
            "min_per_source": bound, "max_per_source": maximum, "min_per_target": bound, "max_per_target": maximum})),
        "path_equations": {"const": []},
        "source_direction": obj({"canonical": {"const": "schema-record.json"}, "human_projection": {"const": "SCHEMA.md"}, "projection_policy": {"const": "generated-only"}}),
        "claim_ceiling": TEXT})
    contract.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Schema carrier with a bounded finite typed graph profile"})
    graph_contract = obj({"scope_ref": TEXT, "level_ref": TEXT,
        "nodes": array(obj({"id": TEXT, "kind": TEXT, "fields": {"type": "object"}}), maximum=10000),
        "relations": array(obj({"id": TEXT, "kind": TEXT, "source": TEXT, "target": TEXT}), maximum=20000)})
    dump(PACKAGE / "schema.json", contract); dump(PACKAGE / "graph.schema.json", graph_contract)
    dump(ROOT / "contracts.json", {"authority_effect": "none", "schemas": [binding(PACKAGE / name) for name in ["schema.json", "graph.schema.json"]]})
    definition = L1 / "definitions/schema/v1/definition.json"
    data = load(definition)
    artifact = load(PREVIOUS / "artifact-types/decision/v1/artifact.json")
    artifact.update(artifact_type_id="cal.artifact-type.schema", artifact_type_ref="cal.artifact-type.schema/v1", name="Schema",
        schema_ref="cal.schema.schema-carrier/v1", schema_digest=sha(PACKAGE / "schema.json"),
        semantic_definition_refs=[data["definition_id"] + "@" + data["version"]],
        semantic_definition_bindings=[{**binding(definition), "definition_ref": data["definition_id"] + "@" + data["version"], "admission_posture": "candidate-unadmitted"}],
        distinct_validation_purpose="Defines admissible representation and static constraints only.")
    artifact["classification"].update(semantic_kind="schema", lifecycle_posture_ref="candidate:schema-reconstruction/v1")
    artifact["instance_contract"].update(canonical_filename="schema-record.json", human_filename="SCHEMA.md", identity_field="schema_id",
        required_semantic_fields=sorted(set(contract["required"]) - {"schema_version", "status", "authority_effect", "source_direction", "claim_ceiling"}))
    artifact["orthogonality_rules"] = [{"rule_id": "SCHEMA-01", "statement": "Kinds, occupant constraints, relations and connection rules remain separate declared parts."},
        {"rule_id": "SCHEMA-02", "statement": "Field constraints do not replace endpoint typing or multiplicity; either family may be empty."},
        {"rule_id": "SCHEMA-03", "statement": "Shape conformance is not truth, authority, promotion or execution proof. Schema and occupant levels remain explicit."}]
    artifact["four_facets"] = {"classification": "Candidate Schema carrier bound to the source-qualified Schema Definition.",
        "schema": "Closed K/C/R/N representation with an explicit relative level and bounded profile.", "machine_checkable": "Static field types, endpoint kinds, per-source/per-target multiplicity and reference closure.",
        "human_continuation": "Generated SCHEMA.md explains the exact example schema."}
    artifact["typed_residue"] = [{"residue_id": "SCHEMA-R1", "owner_ref": "role:schema-owner", "missing": "Path-equation evaluation and richer nested field constraints.", "consequence": "Nonempty path equations and unsupported field types are rejected by this profile."},
        {"residue_id": "SCHEMA-R2", "owner_ref": "role:domain-owner", "missing": "Meaning, truth, ownership and behavioral validation.", "consequence": "A conforming graph proves only its declared shape."}]
    artifact["claim_ceiling"] = "Candidate finite-graph shape checks only. No execution, semantic correctness, authority, ownership proof or admission."
    example = {"schema_version": "cyberalchemy-lab-schema-carrier/v1", "artifact_type_ref": "cal.artifact-type.schema/v1", "schema_id": "CAL-ARTIFACT-OWNER-GRAPH-001",
        "status": "candidate-unadmitted", "authority_effect": "none", "owner_ref": "role:schema-owner", "scope_ref": "scope:artifact-owner-structure",
        "relative_level": {"schema_level_ref": "level:artifact-owner-schema", "occupant_level_ref": "level:artifact-owner-records"}, "profile": "candidate:finite-typed-graph/v1",
        "kinds": ["artifact", "owner"], "constraints": [
            {"kind_ref": "artifact", "closed_fields": True, "fields": [{"name": "title", "value_type": "string", "required": True}]},
            {"kind_ref": "owner", "closed_fields": True, "fields": [{"name": "name", "value_type": "string", "required": True}]}],
        "relations": ["owned-by"], "connection_rules": [{"relation_ref": "owned-by", "source_kind": "artifact", "target_kind": "owner", "min_per_source": 1, "max_per_source": 1, "min_per_target": 0, "max_per_target": None}],
        "path_equations": [], "source_direction": {"canonical": "schema-record.json", "human_projection": "SCHEMA.md", "projection_policy": "generated-only"},
        "claim_ceiling": "Structural example only. An owned-by edge is not proof that the named person or role has authority."}
    invalid = {}
    for name, key, value in [("authority", "authority_effect", "admit"), ("empty-kinds", "kinds", []), ("unknown-profile", "profile", "execute-code"), ("path-equations", "path_equations", ["a;b=c"]), ("extra-field", "proven_true", True), ("blank-scope", "scope_ref", " ")]:
        bad = copy.deepcopy(example); bad[key] = value; invalid[name] = bad
    bad = copy.deepcopy(example); bad["constraints"][0]["fields"][0]["value_type"] = "executable"; invalid["unknown-value-type"] = bad
    bad = copy.deepcopy(example); bad["connection_rules"][0]["min_per_source"] = -1; invalid["negative-multiplicity"] = bad
    artifact["validation_contract"].update(positive_witness="fixtures/valid/schema-record.json", positive_projection="fixtures/valid/SCHEMA.md",
        negative_witnesses=["fixtures/invalid/" + name + ".json" for name in sorted(invalid)], validator_path=str((ROOT / "validate.py").relative_to(LAB)))
    dump(PACKAGE / "artifact.json", artifact); dump(PACKAGE / "fixtures/valid/schema-record.json", example)
    for name, bad in invalid.items():
        dump(PACKAGE / ("fixtures/invalid/" + name + ".json"), bad)
    renderer = module(LAB / "tooling/generators/artifact_surface.py", "schema_renderer")
    artifact = load(PACKAGE / "artifact.json")
    (PACKAGE / "ARTIFACT.md").write_text(renderer.render_artifact(artifact))
    (PACKAGE / "fixtures/valid/SCHEMA.md").write_text(renderer.render_instance(artifact, load(PACKAGE / "fixtures/valid/schema-record.json")))
    graph = {"scope_ref": example["scope_ref"], "level_ref": example["relative_level"]["occupant_level_ref"],
        "nodes": [{"id": "candidate-1", "kind": "artifact", "fields": {"title": "Example candidate"}}, {"id": "owner-1", "kind": "owner", "fields": {"name": "Example owner"}}],
        "relations": [{"id": "ownership-1", "kind": "owned-by", "source": "candidate-1", "target": "owner-1"}]}
    dump(ROOT / "examples/conforming.json", graph)
    missing = copy.deepcopy(graph); missing["relations"] = []; dump(ROOT / "examples/missing-connection.json", missing)
    wrong = copy.deepcopy(graph); wrong["nodes"][0]["fields"]["title"] = 42; dump(ROOT / "examples/wrong-field.json", wrong)
    dump(ROOT / "registry.json", {"authority_effect": "none", "entries": [{"target_id": "type.schema", "family": "artifact-type", "status": "candidate-unadmitted", **binding(PACKAGE / "artifact.json")} ]})
    edges = load(L1 / "batches.json")["edges"]; selected = {"semantic.schema"}
    while True:
        expanded = selected | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in selected}
        if expanded == selected:
            break
        selected = expanded
    registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
    scaffold = ROOT.parent / "0003-review-led-reconstruction/target-candidates/artifact-type/type-schema/v1/artifact.json"
    dump(ROOT / "dependencies.json", {"authority_effect": "none", "seed_targets": ["semantic.schema"], "inputs": [binding(PREVIOUS / "manifest.json"), binding(L1 / "batches.json"), binding(scaffold)],
        "definitions": [{"target_id": target, **binding(LAB / registry[target]["path"])} for target in sorted(selected)], "selected_source_sections": load(scaffold)["source_refs"],
        "source_lineage_residue": [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in selected]})


if __name__ == "__main__":
    build()
