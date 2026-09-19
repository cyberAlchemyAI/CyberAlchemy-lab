#!/usr/bin/env python3
"""Construct three source-bound proposition carrier contracts and examples."""
import copy
from common import ROOT, LAB, L0, L1, PREVIOUS, KINDS, binding, dump, load, sha, module

GENERATOR = LAB / "tooling/generators/artifact_surface.py"
VALIDATOR = LAB / "tooling/validators/artifact_surface.py"
TEXT = {"type": "string", "pattern": "\\S"}
STRINGS = {"type": "array", "items": TEXT, "uniqueItems": True}


def make_schema(kind):
    properties = {
        "schema_version": {"const": f"cyberalchemy-lab-{kind}/v1"},
        "proposition_id": TEXT, "artifact_type_ref": {"const": f"cal.artifact-type.{kind}/v1"},
        "status": {"const": "candidate-unadmitted"}, "authority_effect": {"const": "none"},
        "owner_ref": TEXT, "scope_ref": TEXT, "proposition": TEXT,
        "evidence_refs": STRINGS,
        "source_direction": {"type": "object", "additionalProperties": False,
            "properties": {"canonical": {"const": "proposition.json"},
                "human_projection": {"const": "PROPOSITION.md"}, "projection_policy": {"const": "generated-only"}},
            "required": ["canonical", "human_projection", "projection_policy"]},
        "claim_ceiling": TEXT,
    }
    extra = {
        "axiom": {"truth_posture": {"const": "taken-as-given-within-scope"},
            "subject": {"const": "world-or-domain"}, "derived_within_scope": {"const": False},
            "commitment": {"const": "high"}, "revision_impact": TEXT,
            "downstream_refs": {**STRINGS, "minItems": 2}},
        "premise": {"truth_posture": {"const": "unestablished"}, "adopted_to_proceed": {"const": True},
            "defeasible": {"const": True}, "conviction": {"enum": ["low", "medium", "high"]},
            "adoption_basis": TEXT, "revision_route": TEXT, "retirement_condition": TEXT},
        "hypothesis": {"truth_posture": {"const": "unestablished"}, "adopted_to_proceed": {"const": False},
            "test_method": TEXT, "support_condition": TEXT, "falsification_condition": TEXT},
    }[kind]
    properties.update(extra)
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": kind.title() + " candidate instance", "type": "object", "additionalProperties": False,
            "required": sorted(properties), "properties": properties}


def example(kind):
    common = {"schema_version": f"cyberalchemy-lab-{kind}/v1", "proposition_id": f"CAL-MIGRATION-{kind.upper()}-001",
        "artifact_type_ref": f"cal.artifact-type.{kind}/v1", "status": "candidate-unadmitted", "authority_effect": "none",
        "owner_ref": "role:repository-migration-owner", "scope_ref": "scope:cyberalchemy-lab-migration",
        "evidence_refs": [], "source_direction": {"canonical": "proposition.json", "human_projection": "PROPOSITION.md", "projection_policy": "generated-only"},
        "claim_ceiling": "Demonstration record only. Validation checks representation and declared posture; it does not prove the proposition or grant authority."}
    common.update({
        "axiom": {"proposition": "A statement's meaning depends on the context in which its terms are defined.",
            "truth_posture": "taken-as-given-within-scope", "subject": "world-or-domain", "derived_within_scope": False,
            "commitment": "high", "revision_impact": "Reconsider source-qualified identity and source-to-target interpretation if this starting proposition changes.",
            "downstream_refs": ["semantic.typed-coupling-invariant", "semantic.classification-orthogonality-invariant"]},
        "premise": {"proposition": "The selected source files will remain unchanged during this import batch.",
            "truth_posture": "unestablished", "adopted_to_proceed": True, "defeasible": True, "conviction": "high",
            "adoption_basis": "The batch may proceed provisionally with before-and-after hash checks.",
            "revision_route": "Stop the affected batch and rebind its source manifest when any source hash changes.",
            "retirement_condition": "Retire this working assumption when the exact batch completes or its source selection changes."},
        "hypothesis": {"proposition": "Two imports of the exact manifest produce byte-identical event histories.",
            "truth_posture": "unestablished", "adopted_to_proceed": False,
            "test_method": "Import into two new temporary directories and compare relative paths and file hashes.",
            "support_condition": "Every relative path and hash agrees for the declared corpus.",
            "falsification_condition": "At least one relative path or file hash differs."},
    }[kind])
    return common


def build():
    renderer = module(GENERATOR, "proposition_renderer")
    template = load(L0 / "artifact-types/construction-profile/v1/artifact.json")
    entries = []
    for kind in KINDS:
        package = ROOT / "artifact-types" / kind / "v1"
        schema = make_schema(kind)
        dump(package / "schema.json", schema)
        definition_path = L1 / "definitions" / kind / "v1/definition.json"
        definition = load(definition_path)
        artifact = copy.deepcopy(template)
        artifact.update({"artifact_type_id": f"cal.artifact-type.{kind}", "artifact_type_ref": f"cal.artifact-type.{kind}/v1",
            "name": kind.title(), "schema_ref": f"cal.schema.{kind}/v1", "schema_digest": sha(package / "schema.json"),
            "semantic_definition_refs": [definition["index_entry"]["entry_id"]],
            "semantic_definition_bindings": [{**binding(definition_path), "definition_ref": definition["index_entry"]["entry_id"], "admission_posture": "candidate-unadmitted"}]})
        scaffold = load(PREVIOUS / f"target-candidates/artifact-type/type-{kind}/v1/artifact.json")
        artifact["distinct_validation_purpose"] = scaffold["normalized_contract"]["distinct_validation_purpose"]
        artifact["classification"].update(semantic_kind=kind, lifecycle_posture_ref="candidate:proposition-reconstruction/v1")
        artifact["instance_contract"].update(canonical_filename="proposition.json", human_filename="PROPOSITION.md", identity_field="proposition_id",
            required_semantic_fields=sorted(set(schema["required"]) - {"schema_version", "source_direction", "claim_ceiling", "status", "authority_effect"}))
        artifact["orthogonality_rules"] = [
            {"rule_id": f"{kind.upper()}-01", "statement": artifact["distinct_validation_purpose"]},
            {"rule_id": f"{kind.upper()}-02", "statement": "Truth posture, commitment, evidence, lifecycle and authority remain distinct. Validation never promotes a proposition to another kind."}]
        artifact["four_facets"] = {"classification": f"Candidate {kind} carrier bound to its exact Definition and Artifact Type/v2.",
            "schema": "Closed schema requires the declared proposition posture and rejects mixed kinds.",
            "machine_checkable": "Source digests, structural constraints, cross-kind rejection and generated projection parity.",
            "human_continuation": "Generated PROPOSITION.md explains each complete example."}
        artifact["source_direction"]["shared_generator_sha256"] = sha(GENERATOR)
        artifact["validation_contract"].update(positive_witness="fixtures/valid/proposition.json", positive_projection="fixtures/valid/PROPOSITION.md",
            shared_validator_sha256=sha(VALIDATOR), validator_path=str((ROOT / "validate.py").relative_to(LAB)))
        artifact["typed_residue"] = [{"residue_id": f"{kind.upper()}-R1", "owner_ref": "role:artifact-type-owner",
            "missing": "Exact type admission and domain-specific truth assessment remain outside this candidate.",
            "consequence": "Records may be structurally validated in this prototype; they are not admitted authority or evidence of truth."}]
        artifact["claim_ceiling"] = f"Candidate {kind.title()} representation and validation only. No truth proof, automatic promotion, admission, enforcement or external effect."
        good = example(kind)
        invalid = {}
        for name, key, value in [("authority-effect", "authority_effect", "admitted"), ("additional-property", "automatic_promotion", True),
                                  ("blank-scope", "scope_ref", "   "), ("wrong-truth-posture", "truth_posture", "proven")]:
            bad = copy.deepcopy(good); bad[key] = value; invalid[name] = bad
        for other in KINDS:
            if other != kind:
                bad = example(other)
                bad["schema_version"] = good["schema_version"]
                bad["artifact_type_ref"] = good["artifact_type_ref"]
                invalid["disguised-" + other] = bad
        bad = copy.deepcopy(good)
        if kind == "axiom":
            bad["downstream_refs"] = ["semantic.typed-coupling-invariant"]
        elif kind == "premise":
            bad["adopted_to_proceed"] = False
        else:
            bad["adopted_to_proceed"] = True
        invalid["wrong-defining-posture"] = bad
        artifact["validation_contract"]["negative_witnesses"] = [f"fixtures/invalid/{key}.json" for key in sorted(invalid)]
        dump(package / "artifact.json", artifact)
        dump(package / "fixtures/valid/proposition.json", good)
        for name, bad in invalid.items():
            dump(package / f"fixtures/invalid/{name}.json", bad)
        artifact = load(package / "artifact.json")
        good = load(package / "fixtures/valid/proposition.json")
        (package / "ARTIFACT.md").write_text(renderer.render_artifact(artifact))
        (package / "fixtures/valid/PROPOSITION.md").write_text(renderer.render_instance(artifact, good))
        entries.append({"target_id": "type." + kind, "family": "artifact-type", "status": "candidate-unadmitted",
                        "authority_effect": "none", **binding(package / "artifact.json")})
    dump(ROOT / "registry.json", {"schema_version": "cal-proposition-candidate-registry/v1", "authority_effect": "none", "entries": entries})
    edges = load(L1 / "batches.json")["edges"]
    selected = {"semantic." + kind for kind in KINDS}
    while True:
        expanded = selected | {x["dependency_target_id"] for x in edges if x["consumer_target_id"] in selected}
        if expanded == selected:
            break
        selected = expanded
    registry = {x["target_id"]: x for x in load(L1 / "registry.json")["entries"]}
    definitions = [{"target_id": target, **binding(LAB / registry[target]["path"])} for target in sorted(selected)]
    residue = [x for x in load(L1 / "drift-audit.json")["legacy_reference_residue"] if x["consumer_target_id"] in selected]
    dump(ROOT / "dependencies.json", {"schema_version": "cal-proposition-construction-dependencies/v1", "authority_effect": "none",
        "inputs": [binding(L1 / name) for name in ["registry.json", "batches.json", "manifest.json", "drift-audit.json"]],
        "definitions": definitions, "source_lineage_residue": residue,
        "scope": "Transitive closure of the recorded L1 semantic dependency graph. Unmapped legacy references remain explicit source-lineage residue, not executable dependencies or admitted meanings."})
    return entries


if __name__ == "__main__":
    build()
