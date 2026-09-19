#!/usr/bin/env python3
import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module


def build():
    text = {"type": "string", "pattern": "\\S"}
    properties = {
        "schema_version": {"const": "cyberalchemy-lab-invariant/v1"},
        "artifact_type_ref": {"const": "cal.artifact-type.invariant/v1"}, "invariant_id": text,
        "status": {"const": "candidate-unadmitted"}, "authority_effect": {"const": "none"},
        "owner_ref": text, "scope_ref": text, "subject_ref": text, "subject_kind": {"const": "system-or-artifact"},
        "must_hold": text, "violation_meaning": text, "grounding_refs": {"type": "array", "items": text, "minItems": 1, "uniqueItems": True},
        "evaluation_profile": {"const": "candidate:integer-observation-comparison/v1"},
        "checks": {"type": "array", "minItems": 1, "maxItems": 100, "items": {"type": "object", "additionalProperties": False,
            "required": ["check_id", "field", "operator", "expected"], "properties": {"check_id": text, "field": text,
                "operator": {"enum": ["equals", "at-least", "at-most"]}, "expected": {"type": "integer"}}}},
        "source_direction": {"type": "object", "additionalProperties": False,
            "required": ["canonical", "human_projection", "projection_policy"], "properties": {
                "canonical": {"const": "invariant.json"}, "human_projection": {"const": "INVARIANT.md"}, "projection_policy": {"const": "generated-only"}}},
        "claim_ceiling": text,
    }
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Invariant candidate with bounded integer comparison profile",
        "type": "object", "additionalProperties": False, "required": sorted(properties), "properties": properties}
    dump(PACKAGE / "schema.json", schema)
    definition = L1 / "definitions/invariant/v1/definition.json"
    artifact = load(PREVIOUS / "artifact-types/premise/v1/artifact.json")
    artifact.update(artifact_type_id="cal.artifact-type.invariant", artifact_type_ref="cal.artifact-type.invariant/v1",
        name="Invariant", schema_ref="cal.schema.invariant/v1", schema_digest=sha(PACKAGE / "schema.json"),
        semantic_definition_refs=[load(definition)["index_entry"]["entry_id"]],
        semantic_definition_bindings=[{**binding(definition), "definition_ref": load(definition)["index_entry"]["entry_id"], "admission_posture": "candidate-unadmitted"}],
        distinct_validation_purpose="Defines a scoped must-hold predicate and violation semantics.")
    artifact["classification"].update(semantic_kind="invariant", lifecycle_posture_ref="candidate:invariant-reconstruction/v1")
    artifact["instance_contract"].update(canonical_filename="invariant.json", human_filename="INVARIANT.md", identity_field="invariant_id",
        required_semantic_fields=sorted(set(properties) - {"schema_version", "status", "authority_effect", "source_direction", "claim_ceiling"}))
    artifact["orthogonality_rules"] = [{"rule_id": "INVARIANT-01", "statement": "A system must satisfy an invariant; a scoped axiom is a proposition the system is built around."},
        {"rule_id": "INVARIANT-02", "statement": "Missing, mismatched or mistyped observations never establish satisfaction."},
        {"rule_id": "INVARIANT-03", "statement": "Checking a supplied observation grants no adoption or enforcement authority and does not prove the invariant holds continuously."}]
    artifact["four_facets"] = {"classification": "Candidate Invariant carrier bound to its exact Definition.", "schema": "Closed instance with a nonempty set of bounded integer checks.",
        "machine_checkable": "Shared Artifact Type validation plus a read-only observation evaluator.", "human_continuation": "Generated INVARIANT.md explains the exact scoped rule."}
    artifact["typed_residue"] = [{"residue_id": "INVARIANT-R1", "owner_ref": "role:artifact-type-owner", "missing": "Type admission and general domain predicate profiles.", "consequence": "Only this candidate's three integer comparison operators can execute."},
        {"residue_id": "INVARIANT-R2", "owner_ref": "role:observation-owner", "missing": "Observation authenticity, freshness and grounding-reference resolution.", "consequence": "Results apply only to the supplied observation; no continuous or authoritative conformance claim."}]
    artifact["claim_ceiling"] = "Candidate record validation and bounded observation comparison only; no admission, automatic enforcement or continuous invariant proof."
    example = {"schema_version": "cyberalchemy-lab-invariant/v1", "artifact_type_ref": "cal.artifact-type.invariant/v1", "invariant_id": "CAL-IMPORT-COUNTS-001",
        "status": "candidate-unadmitted", "authority_effect": "none", "owner_ref": "role:repository-migration-owner",
        "scope_ref": "scope:v4-sibling-import-genesis", "subject_ref": "runtime:v4-sibling-import", "subject_kind": "system-or-artifact",
        "must_hold": "The initial imported store must preserve the manifest's node, relation and supporting-document counts.",
        "violation_meaning": "A count differs from the selected import corpus; investigate possible omitted or extra records.",
        "grounding_refs": ["semantic.claim-support-compatibility-invariant"], "evaluation_profile": "candidate:integer-observation-comparison/v1",
        "checks": [{"check_id": name, "field": name, "operator": "equals", "expected": count} for name, count in [("nodes", 815), ("relations", 1210), ("documents", 422)]],
        "source_direction": {"canonical": "invariant.json", "human_projection": "INVARIANT.md", "projection_policy": "generated-only"},
        "claim_ceiling": "Initial imported-corpus counts only. Matching counts do not prove record content or authorized ongoing mutations correct."}
    invalid = {}
    for name, key, value in [("authority", "authority_effect", "enforce"), ("no-checks", "checks", []), ("axiom-subject", "subject_kind", "world-or-domain"), ("blank-scope", "scope_ref", " "), ("extra-field", "automatically_adopt", True)]:
        bad = copy.deepcopy(example); bad[key] = value; invalid[name] = bad
    for name, key, value in [("code-operator", "operator", "eval"), ("boolean-expected", "expected", True), ("fractional-expected", "expected", 1.5)]:
        bad = copy.deepcopy(example); bad["checks"][0][key] = value; invalid[name] = bad
    artifact["validation_contract"].update(positive_witness="fixtures/valid/invariant.json", positive_projection="fixtures/valid/INVARIANT.md",
        negative_witnesses=["fixtures/invalid/" + name + ".json" for name in sorted(invalid)], validator_path=str((ROOT / "validate.py").relative_to(LAB)))
    dump(PACKAGE / "artifact.json", artifact); dump(PACKAGE / "fixtures/valid/invariant.json", example)
    for name, bad in invalid.items():
        dump(PACKAGE / ("fixtures/invalid/" + name + ".json"), bad)
    renderer = module(LAB / "tooling/generators/artifact_surface.py", "invariant_renderer")
    artifact = load(PACKAGE / "artifact.json")
    (PACKAGE / "ARTIFACT.md").write_text(renderer.render_artifact(artifact))
    (PACKAGE / "fixtures/valid/INVARIANT.md").write_text(renderer.render_instance(artifact, load(PACKAGE / "fixtures/valid/invariant.json")))
    observation = {"scope_ref": example["scope_ref"], "subject_ref": example["subject_ref"], "values": {x["field"]: x["expected"] for x in example["checks"]}}
    dump(ROOT / "examples/satisfied.json", observation)
    violated = copy.deepcopy(observation); violated["values"]["nodes"] -= 1
    dump(ROOT / "examples/violated.json", violated)
    missing = copy.deepcopy(observation); del missing["values"]["documents"]
    dump(ROOT / "examples/missing.json", missing)
    dump(ROOT / "registry.json", {"authority_effect": "none", "entries": [{"target_id": "type.invariant", "family": "artifact-type", "status": "candidate-unadmitted", **binding(PACKAGE / "artifact.json")} ]})
    edges = load(L1 / "batches.json")["edges"]
    selected = {"semantic.invariant"}
    while True:
        expanded = selected | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in selected}
        if selected == expanded:
            break
        selected = expanded
    registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
    residue = [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in selected]
    dump(ROOT / "dependencies.json", {"authority_effect": "none", "inputs": [binding(PREVIOUS / "manifest.json"), binding(L1 / "batches.json"), binding(PREVIOUS / "source-rebinding.json")],
        "definitions": [{"target_id": target, **binding(LAB / registry[target]["path"])} for target in sorted(selected)],
        "source_lineage_residue": residue, "scope": "Closure of the recorded semantic dependency graph; unmapped legacy references remain source-lineage residue."})


if __name__ == "__main__":
    build()
