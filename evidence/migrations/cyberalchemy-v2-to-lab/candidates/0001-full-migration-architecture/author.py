#!/usr/bin/env python3
"""Author the semantic and architectural dependencies of migration candidate 0001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"
DEFINITION_PATH = DEFINITION_ROOT / "definitions/repository-migration-manifest/v1/definition.json"
GENERATOR = LAB / "tooling/generators/artifact_surface.py"
VALIDATOR = LAB / "tooling/validators/artifact_surface_candidate_2.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admitted_binding(definition_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = load(LAB / "authority/definitions/registry.json")
    entry = next(item for item in registry["entries"] if item["definition_id"] == definition_id and item["lifecycle_state"] == "admitted" and registry["current_lookup"][definition_id] == f"{definition_id}@{item['version']}")
    binding = {
        "source_ref": f"{definition_id}@{entry['version']}",
        "repository": "CyberAlchemy-lab",
        "path": entry["path"],
        "selector": {"kind": "whole-file"},
        "sha256": entry["sha256"],
        "admission_posture": "admitted",
    }
    source = {
        "source_ref": binding["source_ref"],
        "selector": "whole-json",
        "content_sha256": entry["sha256"],
        "admission_posture": "admitted",
        "source_admission_ref": entry["admission_decision_ref"],
    }
    return binding, source


def author_definition() -> None:
    definition_binding, definition_source = admitted_binding("cal.definition.definition")
    context_binding, context_source = admitted_binding("cal.definition.context-migration-manifest")
    validation_binding, validation_source = admitted_binding("cal.definition.validation")
    schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
    generator_path = LAB / "authority/artifact-types/definition/v1/generator.py"
    live_registry = LAB / "authority/definitions/registry.json"

    record = {
        "schema_version": "cyberalchemy-lab-definition/v1",
        "definition_id": "cal.definition.repository-migration-manifest",
        "version": "1.0.0-candidate.1",
        "term": "Repository Migration Manifest",
        "aliases": ["repository migration envelope", "source-to-target migration manifest"],
        "classification": {
            "artifact_type_ref": "cal.artifact-type.definition/v1",
            "semantic_kind": "definition",
            "authority_kind": "semantic-authority",
            "lifecycle_posture_ref": "CAL-LIFECYCLE-DEFINITION-V1:candidate-authored",
        },
        "semantic_owner_ref": "role:definition-owner",
        "scope": {
            "authority_scope_ref": "scope:repository-migration-manifest-definition",
            "applicability": "An immutable, exact-byte, source-to-target repository migration envelope that binds complete source accounting, exclusions, unique mappings, a target baseline, a copy allowlist, an expected postimage, validation obligations, and rollback boundaries.",
            "exclusions": [
                "Context-local semantic succession, which remains owned by Context Migration Manifest.",
                "Source admission, target activation, product approval, execution authorization, source deletion, overwrite, publication, release, or deployment.",
                "Installed dependencies, build products, caches, or host-specific runtime state reconstructed from profiles and locks.",
            ],
        },
        "voices": {
            "scientific_formal": {
                "normative_statement": "A Repository Migration Manifest M binds source snapshot S, target baseline T0, total accounting partition A=(C,E), injective mapping f:C->P, expected postimage T1, validation set V, and rollback set R. M is well formed only when every observed source entry occurs exactly once in C or E, every selected regular file has one digest-bound destination, f has no divergent collision with T0, execution_authority=false, and R equals the set of paths that an authorized additive execution may create.",
                "formal_expression": "M=(S,T0,C,E,f,T1,V,R); C disjoint E; C union E=entries(S); injective(f); collision(f(C),T0)=empty; authorize(M)=false; R=create_set(M).",
                "notation": [
                    {"symbol": "S", "meaning": "Exact observed source repository snapshot."},
                    {"symbol": "T0", "meaning": "Exact target repository baseline before migration."},
                    {"symbol": "f", "meaning": "Unique mapping from selected source files to target paths."},
                    {"symbol": "R", "meaning": "Exact rollback set for paths created by authorized execution."},
                ],
                "boundary_conditions": [
                    "Every source entry is accounted for without an ambient glob at execution time.",
                    "Divergent existing target bytes block rather than overwrite.",
                    "Imported bytes remain non-authoritative until separately classified and admitted.",
                    "Runtime installations are reconstructed from canonical profiles and locks.",
                ],
                "testable_conditions": [
                    "Source selection and exclusion counts close over the observed filesystem.",
                    "All selected file digests and target-baseline digests are current.",
                    "Mapping is total for selected files, unique, traversal-free, and collision-free.",
                    "Dry-run and isolated rehearsal create no declared-target effects.",
                    "Rollback identifies exactly the paths an authorized execution could create.",
                ],
            },
            "plain_language": {
                "normative": False,
                "explanation": "This is the sealed moving list for one repository migration: every source item is counted, every file to copy has one destination and digest, collisions stop the move, and the rollback list says exactly what the move could create. The list itself never performs or approves the move.",
            },
            "domain_context": {
                "normative": False,
                "workspace_ref": str(LAB),
                "explanation": "The CyberAlchemy-v2 to CyberAlchemy-lab candidate preserves the Lab architecture and copies selected v2 bytes only into plane-local imports/cyberalchemy-v2 boundaries. Imported paths are evidence, not automatic authority or activation.",
                "examples": [
                    "authority/foo.json maps to authority/imports/cyberalchemy-v2/foo.json without replacing Lab authority.",
                    "node_modules and Rust target trees are accounted as excluded reconstructible state.",
                ],
            },
        },
        "boundaries": [
            "Repository Migration Manifest and Context Migration Manifest are related but not interchangeable scopes.",
            "A manifest is a candidate artifact, not an execution authorization.",
            "Copy selection is not semantic admission; imported material requires later type- and owner-specific review.",
            "Rollback permission is separate from rollback description.",
        ],
        "source_refs": [definition_source, context_source, validation_source],
        "primary_consumer_refs": ["cal.artifact-type.repository-migration-manifest/v1", "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0001"],
        "index_entry": {"index_ref": "authority/definitions/candidates/0011-repository-migration-manifest/DEFINITIONS-INDEX.md", "entry_id": "cal.definition.repository-migration-manifest@1.0.0-candidate.1"},
        "drift_route": {"owner_ref": "role:definition-owner", "audit_ref": "authority/definitions/candidates/0011-repository-migration-manifest/drift-audit-postimage.json", "challenge_ref": "CA2-ROUTE-DEFINITIONS"},
        "source_direction": {"canonical": "definition.json", "human_projection": "DEFINITION.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.definition-markdown/v1", "generator_sha256": sha(generator_path)},
        "schema_ref": "cal.schema.definition/v1",
        "schema_digest": sha(schema_path),
        "evidence_refs": ["CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0001"],
        "residue_refs": ["CAL-MIGRATION-R1", "CAL-MIGRATION-R2"],
        "typed_relations": [{"relation_kind_ref": "relation.originates-from", "from_ref": "cal.definition.repository-migration-manifest@1.0.0-candidate.1", "to_ref": context_source["source_ref"], "owner_ref": "role:definition-owner"}],
        "claim_ceiling": "This candidate defines a repository migration manifest only. It does not approve or execute migration, admit imported bytes, delete sources, overwrite target bytes, commit, push, publish, release, or deploy.",
    }
    dump(DEFINITION_PATH, record)

    candidate = {
        "candidate_id": "CAL-DEFINITION-CANDIDATE-REPOSITORY-MIGRATION-MANIFEST-0011",
        "title": "Repository Migration Manifest Definition",
        "status": "candidate-authored-owner-review-open",
        "authority_effect": "none",
        "semantic_owner_ref": "role:definition-owner",
        "definition_contract": {"schema_sha256": sha(schema_path), "generator_sha256": sha(generator_path)},
        "definitions": [{
            "definition_id": record["definition_id"], "version": record["version"], "disposition": "new-candidate-term",
            "path": str(DEFINITION_PATH.relative_to(LAB)),
            "human_projection_path": str(DEFINITION_PATH.with_name("DEFINITION.md").relative_to(LAB)),
        }],
        "source_bindings": [definition_binding, context_binding, validation_binding],
        "predecessor_registry": {"path": "authority/definitions/registry.json", "sha256": sha(live_registry), "entry_count": len(load(live_registry)["entries"])},
        "registry_postimage_id": "cal.registry.definitions/v1-repository-migration-candidate.1",
        "registry_claim_ceiling": "Candidate postimage adds one unadmitted Definition to the admitted registry preimage without changing the live registry.",
        "ownership_boundary": "The Definition owner owns semantic admission. Migration product validation can prove use of the candidate meaning but cannot admit it.",
        "promotion_blockers": ["Exact definition-owner admission is not granted by product validation."],
        "hostile_fixture_rules": ["manifest-must-not-authorize-execution", "manifest-must-not-overwrite", "manifest-must-account-for-rollback"],
        "source_direction": {"canonical": "candidate.json", "human_projection": "CANDIDATE.md", "projection_policy": "generated-only", "generator": "render.py", "generator_ref": "candidate:cal.generator.definition-candidate-pack/v1"},
        "claim_ceiling": "Candidate Definition review only; no admission, migration, deletion, overwrite, commit, push, publication, release, or deployment authority follows.",
    }
    dump(DEFINITION_ROOT / "candidate.json", candidate)
    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1", "audit_id": "CAL-DEFINITION-DRIFT-0011", "title": "Repository Migration Manifest Definition Drift Audit", "status": "candidate-diagnostic", "authority_effect": "none",
        "summary": {"pass": 3, "warning": 0, "block": 0, "total": 3},
        "findings": [
            {"finding_id": "RMM-D1", "severity": "pass", "status": "closed", "condition": "Repository scope is distinct from context-local semantic succession.", "target": str(DEFINITION_PATH.relative_to(LAB)), "remediation": "None."},
            {"finding_id": "RMM-D2", "severity": "pass", "status": "closed", "condition": "Inventory, mapping, copy, rollback, and authority boundaries are explicit.", "target": str(DEFINITION_PATH.relative_to(LAB)), "remediation": "None."},
            {"finding_id": "RMM-D3", "severity": "pass", "status": "closed", "condition": "Machine-canonical and generated-human direction is explicit.", "target": str(DEFINITION_PATH.relative_to(LAB)), "remediation": "None."},
        ],
        "claim_ceiling": "Definition-level selected-surface drift evidence only; it is not admission or migration approval.",
    }
    dump(DEFINITION_ROOT / "drift-audit-postimage.json", drift)
    write(DEFINITION_ROOT / "render.py", """#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent
PATH=ROOT.parent/\"_candidate_pack.py\"
spec=importlib.util.spec_from_file_location(\"candidate_pack\",PATH); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
if __name__==\"__main__\": module.render(ROOT)
""")
    write(DEFINITION_ROOT / "build.py", """#!/usr/bin/env python3
from pathlib import Path
import runpy
if __name__==\"__main__\": runpy.run_path(str(Path(__file__).with_name(\"render.py\")),run_name=\"__main__\")
""")
    write(DEFINITION_ROOT / "validate.py", """#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/\"_candidate_pack.py\"
def hostile(subject):
 failures=set()
 if subject.get(\"execution_authority\") is not False: failures.add(\"manifest-must-not-authorize-execution\")
 if subject.get(\"copy_semantics\",{}).get(\"overwrite\") is not False: failures.add(\"manifest-must-not-overwrite\")
 if not subject.get(\"rollback_ref\"): failures.add(\"manifest-must-account-for-rollback\")
 return failures
if __name__==\"__main__\":
 spec=importlib.util.spec_from_file_location(\"candidate_pack\",SHARED); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); module.hostile_failures=hostile
 raise SystemExit(module.validate(ROOT,{\"cal.definition.repository-migration-manifest\"}))
""")
    invalid = DEFINITION_ROOT / "fixtures/invalid"
    dump(invalid / "execution-authority.json", {"fixture_id": "RMM-H1", "expected_rule": "manifest-must-not-authorize-execution", "subject": {"execution_authority": True, "copy_semantics": {"overwrite": False}, "rollback_ref": "rollback.json"}})
    dump(invalid / "overwrite.json", {"fixture_id": "RMM-H2", "expected_rule": "manifest-must-not-overwrite", "subject": {"execution_authority": False, "copy_semantics": {"overwrite": True}, "rollback_ref": "rollback.json"}})
    dump(invalid / "missing-rollback.json", {"fixture_id": "RMM-H3", "expected_rule": "manifest-must-account-for-rollback", "subject": {"execution_authority": False, "copy_semantics": {"overwrite": False}}})


def migration_schema() -> dict[str, Any]:
    ref = {"type": "string", "minLength": 1}
    digest_ref = {
        "type": "object", "additionalProperties": False,
        "properties": {"path": ref, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
        "required": ["path", "sha256"],
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cyberalchemy.local/schemas/repository-migration-manifest/v1",
        "type": "object", "additionalProperties": False,
        "properties": {
            "schema_version": {"const": "cyberalchemy-lab-repository-migration-manifest/v1"},
            "migration_manifest_id": ref, "version": ref, "status": {"const": "candidate-unapproved"}, "authority_effect": {"const": "none"},
            "source_repository": {"type": "object", "additionalProperties": False, "properties": {"path": ref, "inventory": digest_ref}, "required": ["path", "inventory"]},
            "target_repository": {"type": "object", "additionalProperties": False, "properties": {"path": ref, "baseline": digest_ref}, "required": ["path", "baseline"]},
            "architecture": digest_ref, "mapping_rules": digest_ref, "exclusion_inventory": digest_ref, "copy_allowlist": digest_ref, "expected_postimage": digest_ref,
            "rollback_ref": digest_ref,
            "copy_semantics": {"type": "object", "additionalProperties": False, "properties": {"additive_only": {"const": True}, "overwrite": {"const": False}, "source_mutation": {"const": False}, "import_grants_authority": {"const": False}}, "required": ["additive_only", "overwrite", "source_mutation", "import_grants_authority"]},
            "execution_authority": {"const": False},
            "validation_obligations": {"type": "array", "minItems": 1, "items": ref},
            "semantic_definition_refs": {"type": "array", "minItems": 1, "items": ref},
            "source_direction": {"type": "object", "additionalProperties": False, "properties": {"canonical": {"const": "migration.json"}, "human_projection": {"const": "MIGRATION.md"}, "projection_policy": {"const": "generated-only"}, "generator_ref": ref}, "required": ["canonical", "human_projection", "projection_policy", "generator_ref"]},
            "claim_ceiling": ref,
        },
        "required": ["schema_version", "migration_manifest_id", "version", "status", "authority_effect", "source_repository", "target_repository", "architecture", "mapping_rules", "exclusion_inventory", "copy_allowlist", "expected_postimage", "rollback_ref", "copy_semantics", "execution_authority", "validation_obligations", "semantic_definition_refs", "source_direction", "claim_ceiling"],
    }


def author_artifact_type() -> None:
    schema = migration_schema()
    dump(TYPE_ROOT / "schema.json", schema)
    artifact_binding, _ = admitted_binding("cal.definition.artifact-type")
    validation_binding, _ = admitted_binding("cal.definition.validation")
    bindings = [
        {"definition_ref": artifact_binding["source_ref"], "path": artifact_binding["path"], "sha256": artifact_binding["sha256"], "admission_posture": "admitted"},
        {"definition_ref": "cal.definition.repository-migration-manifest@1.0.0-candidate.1", "path": str(DEFINITION_PATH.relative_to(LAB)), "sha256": sha(DEFINITION_PATH), "admission_posture": "candidate-unadmitted"},
        {"definition_ref": validation_binding["source_ref"], "path": validation_binding["path"], "sha256": validation_binding["sha256"], "admission_posture": "admitted"},
    ]
    artifact = {
        "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2",
        "artifact_type_id": "cal.artifact-type.repository-migration-manifest",
        "artifact_type_ref": "cal.artifact-type.repository-migration-manifest/v1",
        "version": "1.0.0-candidate.1", "name": "Repository Migration Manifest", "status": "candidate-unadmitted", "authority_effect": "none",
        "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v2", "semantic_kind": "artifact-type", "authority_kind": "none", "lifecycle_posture_ref": "candidate:repository-migration-manifest/v1"},
        "artifact_type_root_binding": {"path": "authority/artifact-types/artifact-type/v2/artifact.json", "sha256": sha(LAB / "authority/artifact-types/artifact-type/v2/artifact.json"), "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"},
        "semantic_owner_ref": "role:artifact-type-owner",
        "schema_ref": "cal.schema.repository-migration-manifest/v1", "schema_digest": sha(TYPE_ROOT / "schema.json"),
        "semantic_definition_refs": [item["definition_ref"] for item in bindings], "semantic_definition_bindings": bindings,
        "instance_contract": {"canonical_filename": "migration.json", "human_filename": "MIGRATION.md", "identity_field": "migration_manifest_id", "closed_representation": True, "forbidden_canonical_fields": ["approval", "admission_effect", "execution_token"], "required_semantic_fields": ["source_repository", "target_repository", "mapping_rules", "exclusion_inventory", "copy_allowlist", "expected_postimage", "rollback_ref", "execution_authority"]},
        "distinct_validation_purpose": "Proves complete repository-level byte accounting and one collision-free additive copy postimage without conflating copy selection, semantic admission, or execution authority.",
        "orthogonality_rules": [
            {"rule_id": "RMM-01", "statement": "Copy selection, semantic admission, and execution authorization remain separate."},
            {"rule_id": "RMM-02", "statement": "Every observed source entry is selected or explicitly excluded exactly once."},
            {"rule_id": "RMM-03", "statement": "Divergent target collisions block; overwrite is never inferred."},
            {"rule_id": "RMM-04", "statement": "Rollback description grants no rollback authority."},
        ],
        "four_facets": {"classification": "Repository migration is a source-to-target byte-envelope artifact, not a bounded-context succession.", "schema": "Closed schema binds repositories, inventory, mapping, exclusions, allowlist, postimage, rollback, checks, and no-effect constants.", "human_continuation": "MIGRATION.md is generated from migration.json.", "machine_checkable": "Schema, digest currency, total accounting, unique mapping, dry-run, rehearsal, target baseline, and rollback closure are executable."},
        "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": str(GENERATOR.relative_to(LAB)), "shared_generator_sha256": sha(GENERATOR)},
        "validation_contract": {"assessment_scope": "schema-and-repository-migration-contract", "admission_effect": "none", "validator_path": "validate.py", "shared_validator_path": str(VALIDATOR.relative_to(LAB)), "shared_validator_sha256": sha(VALIDATOR), "positive_witness": "fixtures/valid/migration.json", "positive_projection": "fixtures/valid/MIGRATION.md", "negative_witnesses": ["fixtures/invalid/execution-authority.json", "fixtures/invalid/overwrite.json", "fixtures/invalid/missing-rollback.json"]},
        "typed_residue": [{"residue_id": "RMM-R1", "missing": "Definition and Artifact Type owner admissions.", "owner_ref": "role:definition-owner and role:artifact-type-owner", "consequence": "The migration instance remains candidate-only."}, {"residue_id": "RMM-R2", "missing": "Exact product approval and execution authorization.", "owner_ref": "role:repository-migration-owner", "consequence": "No target mutation is permitted."}],
        "claim_ceiling": "PASS proves this candidate contract and fixtures only; it does not admit the type, approve or execute a migration, delete, overwrite, commit, push, publish, release, or deploy.",
    }
    dump(TYPE_ROOT / "artifact.json", artifact)
    fixture = {
        "schema_version": "cyberalchemy-lab-repository-migration-manifest/v1", "migration_manifest_id": "fixture.repository-migration/v1", "version": "1.0.0-fixture", "status": "candidate-unapproved", "authority_effect": "none",
        "source_repository": {"path": "/source", "inventory": {"path": "source-inventory.json", "sha256": "0" * 64}},
        "target_repository": {"path": "/target", "baseline": {"path": "target-baseline.json", "sha256": "1" * 64}},
        "architecture": {"path": "architecture/architecture.json", "sha256": "2" * 64}, "mapping_rules": {"path": "mapping-rules.json", "sha256": "3" * 64}, "exclusion_inventory": {"path": "exclusion-inventory.json", "sha256": "4" * 64}, "copy_allowlist": {"path": "copy-allowlist.json", "sha256": "5" * 64}, "expected_postimage": {"path": "expected-postimage.json", "sha256": "6" * 64}, "rollback_ref": {"path": "rollback.json", "sha256": "7" * 64},
        "copy_semantics": {"additive_only": True, "overwrite": False, "source_mutation": False, "import_grants_authority": False}, "execution_authority": False,
        "validation_obligations": ["complete-accounting", "hash-currency", "collision-free", "dry-run", "isolated-rehearsal", "rollback-closure"], "semantic_definition_refs": ["cal.definition.repository-migration-manifest@1.0.0-candidate.1"],
        "source_direction": {"canonical": "migration.json", "human_projection": "MIGRATION.md", "projection_policy": "generated-only", "generator_ref": "build.py"}, "claim_ceiling": "Fixture only; no effect."
    }
    dump(TYPE_ROOT / "fixtures/valid/migration.json", fixture)
    bad = json.loads(json.dumps(fixture)); bad["execution_authority"] = True; dump(TYPE_ROOT / "fixtures/invalid/execution-authority.json", bad)
    bad = json.loads(json.dumps(fixture)); bad["copy_semantics"]["overwrite"] = True; dump(TYPE_ROOT / "fixtures/invalid/overwrite.json", bad)
    bad = json.loads(json.dumps(fixture)); del bad["rollback_ref"]; dump(TYPE_ROOT / "fixtures/invalid/missing-rollback.json", bad)
    write(TYPE_ROOT / "generator.py", """#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[5]; P=LAB/\"tooling/generators/artifact_surface.py\"
spec=importlib.util.spec_from_file_location(\"generator\",P); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
load=lambda p: json.loads(p.read_text())
if __name__==\"__main__\":
 (ROOT/\"ARTIFACT.md\").write_text(module.render_artifact(load(ROOT/\"artifact.json\")))
 (ROOT/\"fixtures/valid/MIGRATION.md\").write_text(module.render_instance(load(ROOT/\"artifact.json\"),load(ROOT/\"fixtures/valid/migration.json\")))
""")
    write(TYPE_ROOT / "validate.py", """#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[5]
if __name__==\"__main__\": raise SystemExit(subprocess.run([sys.executable,str(LAB/\"tooling/validators/artifact_surface_candidate_2.py\"),\"validate-package\",str(ROOT)]).returncode)
""")


def author_request() -> None:
    request = {
        "schema_version": "cyberalchemy-lab-artifact-type-request/v1", "request_id": "CAL-ARTIFACT-TYPE-REQUEST-REPOSITORY-MIGRATION-MANIFEST-0001", "version": "1.0.0-candidate.1", "status": "candidate-unadmitted", "authority_effect": "none", "owner_ref": "role:artifact-type-owner",
        "proposed_semantic_kind": "repository-migration-manifest", "proposed_package_home_ref": "authority/artifact-types/repository-migration-manifest/v1", "proposed_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-repository-migration-manifest/v1"},
        "resolution_evidence": {"registry_ref": "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json", "matches": []},
        "compatibility_analysis": [{"existing_type_ref": "cal.artifact-type.context-migration-manifest/v1", "rejection_reason": "Context Migration Manifest governs one bounded-context succession; it does not bind complete repository byte accounting, target baseline, copy allowlist, or repository rollback."}],
        "semantic_definition_refs": ["cal.definition.artifact-type-request@1.0.0-candidate.2", "cal.definition.artifact-type-resolution@1.0.0-candidate.2", "cal.definition.repository-migration-manifest@1.0.0-candidate.1"],
        "representation_proposal": {"canonical_filename": "migration.json", "human_filename": "MIGRATION.md", "projection_policy": "generated-only"},
        "validation_purpose": "Require complete source accounting, exact byte mappings, collision blocking, target postimage, dry-run evidence, and rollback closure at repository scope.", "consumed_as_subject": False,
        "expiry": {"condition": "Expires when an admitted Artifact Type registry entry resolves the proposed discriminator or this request is withdrawn.", "superseded_by": None},
        "source_direction": {"canonical": "request.json", "human_projection": "REQUEST.md", "projection_policy": "generated-only", "generator_ref": "author.py"},
        "claim_ceiling": "Intake candidate only; it neither registers an Artifact Type nor approves or executes migration.",
    }
    dump(ROOT / "request.json", request)
    lines = ["<!-- GENERATED FILE: canonical data is request.json. -->", "", "# Repository Migration Manifest Artifact Type Request", "", f"- Request: `{request['request_id']}`", f"- Proposed discriminator: `{request['proposed_discriminator']['value']}`", "- Current matches: `0`", "- Authority effect: `none`", "", "## Distinctness", "", request["compatibility_analysis"][0]["rejection_reason"], "", "## Claim ceiling", "", request["claim_ceiling"]]
    write(ROOT / "REQUEST.md", "\n".join(lines))


def author_architecture_projections() -> None:
    architecture = load(ROOT / "architecture/architecture.json")
    concepts = load(ROOT / "architecture/concepts.json")
    relations = load(ROOT / "architecture/relations.json")
    mapping = load(ROOT / "mapping-rules.json")
    lines = ["<!-- GENERATED FILE: canonical data is architecture/architecture.json. -->", "", "# CyberAlchemy-lab Migration Architecture", "", "## Decision", "", architecture["recommended_architecture"]["principle"], "", "## Planes", "", "| Plane | Responsibility | Import boundary |", "| --- | --- | --- |"]
    for plane in architecture["recommended_architecture"]["planes"]:
        lines.append(f"| `{plane['path']}` | {plane['owns']} | `{plane['import_root']}` |")
    lines += ["", "## Recursive bounded-context form", "", architecture["recommended_architecture"]["recursive_context_form"], "", "## Import rule", "", architecture["recommended_architecture"]["import_rule"], "", "## Runtime rule", "", architecture["recommended_architecture"]["runtime_rule"], "", "## Claim ceiling", "", architecture["claim_ceiling"]]
    write(ROOT / "architecture/ARCHITECTURE.md", "\n".join(lines))
    concept_lines = ["<!-- GENERATED FILE: canonical data is architecture/concepts.json. -->", "", "# Architecture Pattern Library", "", "| Concept | Meaning |", "| --- | --- |"]
    for item in concepts["concepts"]: concept_lines.append(f"| `{item['concept_id']}` | **{item['name']}** ({item['kind']}), evidenced by `{item['evidence']}`. |")
    write(ROOT / "architecture/ARCHITECTURE-PATTERN-LIBRARY.md", "\n".join(concept_lines))
    write(ROOT / "architecture/pattern-library/README.md", "\n".join(["<!-- GENERATED INDEX: canonical sources are ../concepts.json and ../relations.json. -->", "", "# Pattern Library", "", "The reusable pattern is **plane-local quarantined import**: preserve source bytes below the target plane that owns later interpretation, while denying authority, activation, or runtime effects by path alone."]))
    foundations = ["<!-- GENERATED FILE: canonical inputs are candidate.json and architecture/*.json. -->", "", "# Architecture Foundations", "", "- Machine-readable artifacts are canonical; Markdown is generated.", "- Definitions, Artifact Types, instances, evidence, approval, admission, activation, and execution remain separate.", "- Bounded contexts recurse using the same internal planes without repeating the context name.", "- Imported v2 bytes remain source evidence below plane-local import boundaries.", "- Runtime and dependency state is reconstructed from profiles and locks.", "", "## Candidate status", "", "This architecture is a product candidate and has no authority effect."]
    write(ROOT / "ARCHITECTURE-FOUNDATIONS.md", "\n".join(foundations))
    deps = ["<!-- GENERATED FILE: canonical inputs are mapping-rules.json and architecture/relations.json. -->", "", "# Dependency Rules", "", "1. Authority may define contracts for every plane; imported authority cannot replace Lab authority.", "2. Product meaning may depend on admitted authority, never on implementation details.", "3. Context packages expose explicit maps and bindings; directory proximity creates no relationship.", "4. Implementation depends on product/context contracts; bindings do not redefine them.", "5. Evidence observes all planes but grants no approval or activation.", "6. Platform installs runtimes from profiles/locks; imported caches and build trees are excluded.", "7. Tooling generates projections and validates contracts; generated views never become canonical axes.", "8. An unmapped source path or divergent target collision blocks the migration.", "", f"Mapping rules: `{len(mapping['rules'])}`."]
    write(ROOT / "DEPENDENCY-RULES.md", "\n".join(deps))
    testing = ["<!-- GENERATED FILE: canonical input is architecture/architecture.json. -->", "", "# Testing Alignment", "", "- Contract tests: Definition, Artifact Type Request, Artifact Type, and migration schema.", "- Inventory tests: total source accounting and exact selected-file digests.", "- Mapping tests: one rule and destination per selected file; no traversal or collision.", "- Rehearsal tests: deterministic sample copy in an isolated temporary directory.", "- Evolution tests: imported bytes cannot shadow active Lab packages.", "- Recovery tests: rollback equals the exact create-set and never includes source bytes."]
    write(ROOT / "TESTING-ALIGNMENT.md", "\n".join(testing))
    observing = ["<!-- GENERATED FILE: canonical input is architecture/architecture.json. -->", "", "# Observability Alignment", "", "- Build receipt records source, exclusions, selected bytes, mappings, target baseline, and expected postimage.", "- Validation receipt records every check including blocked or not-evaluable dependencies.", "- Execution, if later authorized, must emit a per-path journal and stop at the first collision or source-digest drift.", "- Admission, activation, publication, release, and deployment require separate owner evidence."]
    write(ROOT / "OBSERVABILITY-ALIGNMENT.md", "\n".join(observing))
    relation_lines = ["<!-- GENERATED FILE: canonical data is architecture/relations.json. -->", "", "# Architecture Relations", "", "| From | Relation | To |", "| --- | --- | --- |"]
    for item in relations["relations"]: relation_lines.append(f"| `{item['from']}` | `{item['relation']}` | `{item['to']}` |")
    write(ROOT / "architecture/RELATIONS.md", "\n".join(relation_lines))


def main() -> None:
    author_definition()
    author_artifact_type()
    author_request()
    author_architecture_projections()
    print("MIGRATION_SEMANTIC_AUTHORING=PASS")
    print(f"DEFINITION={DEFINITION_PATH.relative_to(LAB)}")
    print(f"ARTIFACT_TYPE={TYPE_ROOT.relative_to(LAB)}")


if __name__ == "__main__":
    main()
