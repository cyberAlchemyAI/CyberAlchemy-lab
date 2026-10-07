#!/usr/bin/env python3
"""Materialize six modern successors for admitted legacy Artifact Type contracts."""

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
REGISTRY = LAB / "authority/artifact-types/candidates/0008-registry-snapshot-0002/registry.json"
DEFINITIONS = LAB / "authority/definitions/registry.json"
RELATIONS = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
GENERATOR = LAB / "tooling/generators/artifact_type_successor.py"
VALIDATOR = LAB / "tooling/validators/artifact_type_successor.py"


CONFIG = [
    {"kind": "bounded-context", "source": "bounded-context/v2", "target": "bounded-context/v3", "version": "3.0.0-candidate.1", "positive": "fixtures/valid/context.json"},
    {"kind": "capability-instance", "source": "capability-instance/v1", "target": "capability-instance/v2", "version": "2.0.0-candidate.1", "positive": "fixtures/valid/instance.json"},
    {"kind": "context-lineage-record", "source": "context-lineage-record/v1", "target": "context-lineage-record/v2", "version": "2.0.0-candidate.1", "positive": "fixtures/valid/lineage.json"},
    {"kind": "context-map", "source": "context-map/v2", "target": "context-map/v3", "version": "3.0.0-candidate.1", "positive": "fixtures/valid/map.json"},
    {"kind": "context-migration-manifest", "source": "context-migration-manifest/v1", "target": "context-migration-manifest/v2", "version": "2.0.0-candidate.1", "positive": "fixtures/valid/migration.json"},
    {"kind": "ubiquitous-language", "source": "ubiquitous-language/v1", "target": "ubiquitous-language/v2", "version": "2.0.0-candidate.1", "positive": "fixtures/valid/language.json"},
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_strings(item, replacements) for key, item in value.items()}
    return value


def self_contained_schema(source_path: Path, replacements: dict[str, str], target_id: str) -> dict:
    source = load(source_path)
    external_ref = source.get("$ref")
    if external_ref and not external_ref.startswith("#"):
        file_part, _, fragment = external_ref.partition("#")
        shared = load((source_path.parent / file_part).resolve())
        value = {
            "$schema": source.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
            "$id": target_id,
            "title": source.get("title", shared.get("title", "Artifact Type successor schema")),
            "$ref": f"#{fragment}",
            "$defs": shared["$defs"],
        }
        return replace_strings(value, replacements)
    value = replace_strings(source, replacements)
    value["$id"] = target_id
    return value


def roles_for(kind: str, model: dict) -> list[dict]:
    roles = []
    for relation in model["entries"]:
        outgoing = sorted({pair["target_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        incoming = sorted({pair["source_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if outgoing: roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "source", "counterpart_kinds": outgoing})
        if incoming: roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "target", "counterpart_kinds": incoming})
    return sorted(roles, key=lambda row: (row["relation_kind_ref"], row["direction"]))


def write_wrappers(target: Path) -> None:
    (target / "generator.py").write_text("#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util,json\nROOT=Path(__file__).resolve().parent; SHARED=ROOT.parents[3]/'tooling/generators/artifact_type_successor.py'\ns=importlib.util.spec_from_file_location('g',SHARED);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m)\nif __name__=='__main__':\n a=json.loads((ROOT/'artifact.json').read_text());p=ROOT/a['validation_contract']['positive_witness'];d=json.loads(p.read_text());(ROOT/'ARTIFACT.md').write_text(m.render_artifact(a));(ROOT/a['validation_contract']['positive_projection']).write_text(m.render_instance(a,d))\n", encoding="utf-8")
    (target / "validate.py").write_text("#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util\nROOT=Path(__file__).resolve().parent;SHARED=ROOT.parents[3]/'tooling/validators/artifact_type_successor.py'\ns=importlib.util.spec_from_file_location('v',SHARED);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m)\nif __name__=='__main__':raise SystemExit(m.validate_package(ROOT))\n", encoding="utf-8")


def main() -> None:
    registry = load(REGISTRY)
    definitions = load(DEFINITIONS)
    model = load(RELATIONS)
    spec = importlib.util.spec_from_file_location("successor_generator", GENERATOR)
    generator = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(generator)
    results = []
    for config in CONFIG:
        kind = config["kind"]
        source = LAB / "authority/artifact-types" / config["source"]
        target = LAB / "authority/artifact-types" / config["target"]
        if target.exists(): shutil.rmtree(target)
        target.mkdir(parents=True)
        predecessor_ref = f"cal.artifact-type.{config['source'].replace('/', '/v' if False else '/')}"
        admitted = next(row for row in registry["admitted_contracts"] if row["artifact_path"] == str((source / "artifact.json").relative_to(LAB)))
        predecessor = load(source / "artifact.json")
        new_ref = f"cal.artifact-type.{config['target']}"
        old_discriminator = admitted["instance_discriminator"]["value"]
        new_discriminator = old_discriminator.rsplit("/v", 1)[0] + "/v" + config["target"].rsplit("/v", 1)[1]
        replacements = {old_discriminator: new_discriminator}
        target_schema_id = f"https://cyberalchemy.local/schemas/{config['target']}"
        schema = self_contained_schema(source / "schema.json", replacements, target_schema_id)
        dump(target / "schema.json", schema)
        positive_name = Path(config["positive"]).name
        witness = replace_strings(load(source / config["positive"]), replacements)
        positive_path = target / "fixtures/valid" / positive_name
        dump(positive_path, witness)
        negatives = []
        hostile = copy.deepcopy(witness)
        hostile["implicit_authority"] = "admit"
        dump(target / "fixtures/invalid/implicit-authority.json", hostile)
        negatives.append("fixtures/invalid/implicit-authority.json")
        definition_ref = admitted["semantic_definition_refs"][0]
        row = next(item for item in definitions["entries"] if f"{item['definition_id']}@{item['version']}" == definition_ref)
        binding = {"definition_ref": definition_ref, "path": row["path"], "sha256": row["sha256"], "admission_posture": "admitted", "admission_decision_ref": row["admission_decision_ref"]}
        roles = roles_for(kind, model)
        instance_contract = copy.deepcopy(predecessor.get("instance_contract", {}))
        instance_contract["instance_discriminator"] = {"path": admitted["instance_discriminator"]["path"], "value": new_discriminator}
        missing = copy.deepcopy(witness)
        missing.pop(instance_contract["identity_field"])
        dump(target / "fixtures/invalid/missing-identity.json", missing)
        negatives.append("fixtures/invalid/missing-identity.json")
        projection_name = instance_contract.get("human_filename", "RECORD.md")
        artifact = {
            "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2", "artifact_type_id": f"cal.artifact-type.{kind}", "artifact_type_ref": new_ref, "version": config["version"], "name": predecessor["name"], "status": "candidate-unadmitted", "authority_effect": "none",
            "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v2", "semantic_kind": kind, "authority_kind": "none", "lifecycle_posture_ref": "candidate:step5-carrier-closure/v1"},
            "artifact_type_root_binding": {"path": "authority/artifact-types/artifact-type/v2/artifact.json", "sha256": sha(ROOT_TYPE), "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"},
            "predecessor_contract": {"artifact_type_ref": admitted["artifact_type_ref"], "path": admitted["artifact_path"], "sha256": admitted["artifact_sha256"], "schema_path": admitted["schema_path"], "schema_sha256": admitted["schema_sha256"], "admission_decision_ref": admitted["admission_decision_ref"]},
            "semantic_owner_ref": predecessor.get("semantic_owner_ref") or "role:artifact-type-owner", "semantic_definition_refs": [definition_ref], "semantic_definition_bindings": [binding], "schema_ref": f"cal.schema.{config['target']}", "schema_digest": sha(target / "schema.json"), "instance_contract": instance_contract,
            "distinct_validation_purpose": predecessor.get("distinct_validation_purpose") or f"Carries one closed {predecessor['name']} record while preserving identity, Definition, schema, lifecycle, relation, evidence, ownership, and authority boundaries.",
            "allowed_relation_kinds": sorted({role["relation_kind_ref"] for role in roles}), "relation_roles": roles,
            "orthogonality_rules": [{"rule_id": f"{kind.upper()}-SUCCESSION", "statement": "The successor and admitted predecessor remain exact separate contracts; admission may transition lifecycle but never rewrites predecessor bytes."}, {"rule_id": f"{kind.upper()}-SEMANTICS", "statement": "The carrier binds one exact current admitted Definition without redefining it."}, {"rule_id": f"{kind.upper()}-RELATIONS", "statement": "Only the declared closed relation roles are eligible and every Typed Relation remains a separate artifact."}, {"rule_id": f"{kind.upper()}-AUTHORITY", "statement": "Schema validity, evidence, relation membership, and candidate status create no admission, authority, execution, migration, deletion, or runtime effect."}],
            "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": "tooling/generators/artifact_type_successor.py", "shared_generator_sha256": sha(GENERATOR)},
            "four_facets": {"classification": f"Candidate immutable successor for {predecessor['name']}.", "schema": "schema.json is a closed versioned instance contract derived from the admitted predecessor schema with an explicit successor discriminator.", "human_continuation": "ARTIFACT.md and the valid instance projection are deterministic generated views.", "machine_checkable": "Predecessor bytes, Definition, schema, relation surface, hostile fixtures, and projections are executable checks."},
            "validation_contract": {"validator_path": f"authority/artifact-types/{config['target']}/validate.py", "shared_validator_path": "tooling/validators/artifact_type_successor.py", "shared_validator_sha256": sha(VALIDATOR), "positive_witness": f"fixtures/valid/{positive_name}", "positive_projection": f"fixtures/valid/{projection_name}", "negative_witnesses": negatives, "assessment_scope": "candidate-successor-schema-definition-relation-and-projection", "admission_effect": "none", "required_checks": ["modern successor contract", "exact admitted predecessor", "current Definition", "closed schema", "candidate relation surface", "hostile rejection", "deterministic projections"]},
            "typed_residue": [{"residue_id": f"{kind.upper()}-SUCCESSOR-R1", "missing": "Artifact Type owner admission for this exact successor.", "owner_ref": "role:artifact-type-owner", "consequence": "The successor remains candidate-only and the predecessor remains admitted-current."}, {"residue_id": f"{kind.upper()}-SUCCESSOR-R2", "missing": "A separately admitted instance and consumer activation decision.", "owner_ref": "role:migration-consumer-owner", "consequence": "No instance, relation, migration, deletion, consumer, or runtime effect occurs."}],
            "claim_ceiling": f"This is the candidate immutable {predecessor['name']} successor. PASS proves only its exact predecessor, Definition, schema, fixture, relation surface, hostile cases, and projections; it does not admit or activate the successor, transition the predecessor, create an instance, or authorize migration, deletion, or runtime effects."
        }
        dump(target / "artifact.json", artifact)
        write_wrappers(target)
        (target / "ARTIFACT.md").write_text(generator.render_artifact(artifact), encoding="utf-8")
        (target / artifact["validation_contract"]["positive_projection"]).write_text(generator.render_instance(artifact, witness), encoding="utf-8")
        results.append({"artifact_type_ref": new_ref, "artifact_path": str((target / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(target / "artifact.json"), "schema_sha256": sha(target / "schema.json"), "predecessor_ref": admitted["artifact_type_ref"], "definition_ref": definition_ref})
    dump(ROOT / "legacy-successor-postimages.json", {"schema_version": "cyberalchemy-lab-step5-legacy-successor-postimages/v1", "status": "candidate-materialized", "authority_effect": "none", "count": len(results), "entries": results, "claim_ceiling": "This manifest identifies six candidate immutable successor postimages. It does not admit or activate them or transition their predecessors."})


if __name__ == "__main__": main()
