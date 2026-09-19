#!/usr/bin/env python3
import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module

TEXT = {"type": "string", "pattern": "\\S"}
REFS = {"type": "array", "items": TEXT, "uniqueItems": True, "minItems": 1}


def obj(properties):
    return {"type": "object", "additionalProperties": False, "required": sorted(properties), "properties": properties}


def array(item, minimum=1):
    return {"type": "array", "minItems": minimum, "maxItems": 100, "items": item}


def build():
    schema = obj({
        "schema_version": {"const": "cyberalchemy-lab-constitution/v1"},
        "artifact_type_ref": {"const": "cal.artifact-type.constitution/v1"}, "constitution_id": TEXT,
        "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(?:-[a-zA-Z0-9.-]+)?$"},
        "status": {"const": "candidate-unadmitted"}, "authority_effect": {"const": "none"},
        "scope_ref": TEXT, "owner_route": TEXT, "authority_level": {"const": "proposed-owner-scoped"},
        "subject_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"enum": ["artifact", "task_or_workflow", "repository_owned_agent_action", "system_operation_or_state_transition", "validation_surface", "authority_movement"]}},
        "selectors": array(obj({"selector_id": TEXT, "attribute": TEXT, "equals": TEXT})),
        "rules": array(obj({"rule_id": TEXT, "statement": TEXT, "selector_ids": REFS,
            "validation_mode": {"enum": ["deterministic", "review", "hybrid", "none-yet"]},
            "validation_binding_id": {"anyOf": [TEXT, {"type": "null"}]}, "grounding_refs": REFS})),
        "policies": array(obj({"policy_id": TEXT, "statement": TEXT, "rule_ids": REFS}), 0),
        "precedence": REFS, "composition": {"const": "all-matching-rules-no-implicit-override"},
        "conflict_route": TEXT, "challenge_route": TEXT, "retirement_or_split_conditions": REFS,
        "downstream_effect": {"const": "preview-only"},
        "validation_bindings": array(obj({"binding_id": TEXT, "path": TEXT,
            "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "invariant_id": TEXT,
            "evaluation_profile": {"const": "candidate:integer-observation-comparison/v1"}}), 0),
        "source_direction": obj({"canonical": {"const": "constitution.json"}, "human_projection": {"const": "CONSTITUTION.md"}, "projection_policy": {"const": "generated-only"}}),
        "claim_ceiling": TEXT,
    })
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Candidate Constitution with exact selector preview"})
    dump(PACKAGE / "schema.json", schema)
    definition = L1 / "definitions/constitution/v1/definition.json"
    artifact = load(PREVIOUS / "artifact-types/invariant/v1/artifact.json")
    artifact.update(artifact_type_id="cal.artifact-type.constitution", artifact_type_ref="cal.artifact-type.constitution/v1",
        name="Constitution", schema_ref="cal.schema.constitution/v1", schema_digest=sha(PACKAGE / "schema.json"),
        semantic_definition_refs=[load(definition)["index_entry"]["entry_id"]],
        semantic_definition_bindings=[{**binding(definition), "definition_ref": load(definition)["index_entry"]["entry_id"], "admission_posture": "candidate-unadmitted"}],
        distinct_validation_purpose="Carries selector-bound normative authority after exact adoption.")
    artifact["classification"].update(semantic_kind="constitution", lifecycle_posture_ref="candidate:constitution-reconstruction/v1")
    artifact["instance_contract"].update(canonical_filename="constitution.json", human_filename="CONSTITUTION.md", identity_field="constitution_id",
        required_semantic_fields=sorted(set(schema["required"]) - {"schema_version", "status", "authority_effect", "source_direction", "claim_ceiling"}))
    artifact["orthogonality_rules"] = [{"rule_id": "CONSTITUTION-01", "statement": "Candidate, selected or context-loaded rulebooks do not govern merely because their selectors match."},
        {"rule_id": "CONSTITUTION-02", "statement": "Exact owner adoption, scope, selectors, validation and enforcement remain separate questions."},
        {"rule_id": "CONSTITUTION-03", "statement": "All matched rules remain visible in declared order; this profile grants no implicit override or inferred conflict resolution."}]
    artifact["four_facets"] = {"classification": "Candidate Constitution carrier bound to the existing source-qualified Definition.",
        "schema": "Closed scope, selector, rule, policy, ownership and composition record.", "machine_checkable": "Shared carrier validation, reference closure, exact local invariant binding and read-only selector preview.",
        "human_continuation": "Generated CONSTITUTION.md explains the candidate rulebook."}
    artifact["typed_residue"] = [{"residue_id": "CONSTITUTION-R1", "owner_ref": "role:constitution-owner", "missing": "Exact owner adoption and conflict interpretation.", "consequence": "This candidate never reports that it governs or resolves semantic conflicts."},
        {"residue_id": "CONSTITUTION-R2", "owner_ref": "role:validation-owner", "missing": "General binding types and automatic execution of rules.", "consequence": "This profile resolves existing integer-invariant bindings but only previews selectors."}]
    artifact["claim_ceiling"] = "Candidate rulebook and selector preview only. No owner authentication, adoption, rule execution, enforcement or cross-constitution conflict resolution."
    invariant_path = PREVIOUS / "artifact-types/invariant/v1/fixtures/valid/invariant.json"
    invariant = load(invariant_path)
    example = {"schema_version": "cyberalchemy-lab-constitution/v1", "artifact_type_ref": "cal.artifact-type.constitution/v1", "constitution_id": "CAL-IMPORT-RULEBOOK-001", "version": "1.0.0-candidate.1",
        "status": "candidate-unadmitted", "authority_effect": "none", "scope_ref": invariant["scope_ref"],
        "owner_route": "role:repository-migration-owner", "authority_level": "proposed-owner-scoped", "subject_kinds": ["artifact"],
        "selectors": [{"selector_id": "selected-runtime", "attribute": "runtime_ref", "equals": invariant["subject_ref"]}],
        "rules": [{"rule_id": "preserve-counts", "statement": invariant["must_hold"], "selector_ids": ["selected-runtime"], "validation_mode": "deterministic", "validation_binding_id": "import-counts", "grounding_refs": ["semantic.invariant"]},
            {"rule_id": "preserve-meaning", "statement": "Review source-qualified identities and explicit lineage residue before claiming semantic equivalence.", "selector_ids": ["selected-runtime"], "validation_mode": "review", "validation_binding_id": None, "grounding_refs": ["semantic.typed-coupling-invariant"]}],
        "policies": [{"policy_id": "no-counts-only-completion", "statement": "Matching counts alone cannot establish a complete semantic migration.", "rule_ids": ["preserve-counts", "preserve-meaning"]}],
        "precedence": ["preserve-counts", "preserve-meaning"], "composition": "all-matching-rules-no-implicit-override",
        "conflict_route": "role:repository-migration-owner", "challenge_route": "role:definition-owner",
        "retirement_or_split_conditions": ["Split the rulebook if new consumers require different scopes or owners.", "Retire this version after an explicit successor decision for a different source corpus."],
        "downstream_effect": "preview-only", "validation_bindings": [{"binding_id": "import-counts", **binding(invariant_path), "invariant_id": invariant["invariant_id"], "evaluation_profile": invariant["evaluation_profile"]}],
        "source_direction": {"canonical": "constitution.json", "human_projection": "CONSTITUTION.md", "projection_policy": "generated-only"},
        "claim_ceiling": "Candidate demonstration. Matching a subject does not adopt this rulebook or activate its rules."}
    invalid = {}
    for name, key, value in [("self-adoption", "status", "adopted"), ("authority-effect", "authority_effect", "govern"), ("empty-rules", "rules", []), ("empty-scope", "scope_ref", " "), ("implicit-override", "composition", "last-wins"), ("effect-execution", "downstream_effect", "enforce"), ("extra-adoption-field", "adoption_verified", True)]:
        bad = copy.deepcopy(example); bad[key] = value; invalid[name] = bad
    bad = copy.deepcopy(example); bad["rules"][0]["validation_mode"] = "execute-shell"; invalid["unknown-validation-mode"] = bad
    artifact["validation_contract"].update(positive_witness="fixtures/valid/constitution.json", positive_projection="fixtures/valid/CONSTITUTION.md",
        negative_witnesses=["fixtures/invalid/" + name + ".json" for name in sorted(invalid)], validator_path=str((ROOT / "validate.py").relative_to(LAB)))
    dump(PACKAGE / "artifact.json", artifact); dump(PACKAGE / "fixtures/valid/constitution.json", example)
    for name, bad in invalid.items():
        dump(PACKAGE / ("fixtures/invalid/" + name + ".json"), bad)
    renderer = module(LAB / "tooling/generators/artifact_surface.py", "constitution_renderer")
    artifact = load(PACKAGE / "artifact.json")
    (PACKAGE / "ARTIFACT.md").write_text(renderer.render_artifact(artifact))
    (PACKAGE / "fixtures/valid/CONSTITUTION.md").write_text(renderer.render_instance(artifact, load(PACKAGE / "fixtures/valid/constitution.json")))
    subject = {"scope_ref": invariant["scope_ref"], "subject_kind": "artifact", "attributes": {"runtime_ref": invariant["subject_ref"]}}
    dump(ROOT / "examples/matching.json", subject)
    missing = copy.deepcopy(subject); missing["attributes"] = {}; dump(ROOT / "examples/missing.json", missing)
    other = copy.deepcopy(subject); other["scope_ref"] = "scope:other-import"; dump(ROOT / "examples/outside-scope.json", other)
    dump(ROOT / "registry.json", {"authority_effect": "none", "entries": [{"target_id": "type.constitution", "family": "artifact-type", "status": "candidate-unadmitted", **binding(PACKAGE / "artifact.json")} ]})
    edges = load(L1 / "batches.json")["edges"]; selected = {"semantic.constitution"}
    while True:
        expanded = selected | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in selected}
        if selected == expanded:
            break
        selected = expanded
    registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
    dump(ROOT / "dependencies.json", {"authority_effect": "none", "inputs": [binding(PREVIOUS / "manifest.json"), binding(L1 / "batches.json"), binding(invariant_path)],
        "definitions": [{"target_id": target, **binding(LAB / registry[target]["path"])} for target in sorted(selected)],
        "source_lineage_residue": [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in selected]})


if __name__ == "__main__":
    build()
