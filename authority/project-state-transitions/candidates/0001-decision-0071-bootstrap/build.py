#!/usr/bin/env python3
"""Build the first real Project State event histories and Decision 0071 successor."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
DECISION = "CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
OLD_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0070"
NEW_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0071"
SEMANTIC_HISTORY = "project-semantic-event-history:cyberalchemy-v2-to-lab-migration"
GOVERNANCE_HISTORY = "project-governance-event-history:cyberalchemy-v2-to-lab-migration"
OWNER = "role:repository-owner"
SCOPE = "scope:cyberalchemy-lab-operational-foundation"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
POLICY = "policy:cyberalchemy-lab-operational-foundation"
FOUNDATION = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"
MODEL = LAB / "authority/admissions/definition-complete-lab-model/v1"
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0015-project-state-event-histories"
SEMANTIC_TYPE = LAB / "authority/artifact-types/project-semantic-event-history/v1"
GOVERNANCE_TYPE = LAB / "authority/artifact-types/project-governance-event-history/v1"
INSTANCES = ROOT / "instances" / "artifacts"
RELATIONS = ROOT / "instances" / "typed-relations"


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


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def merge(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target


def definition_renderer():
    path = LAB / "authority/artifact-types/definition/v1/generator.py"
    spec = importlib.util.spec_from_file_location("definition_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def endpoint_renderer():
    path = LAB / "tooling/generators/endpoint_carrier.py"
    spec = importlib.util.spec_from_file_location("endpoint_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def build_definitions() -> list[dict[str, Any]]:
    base = load(LAB / "authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/governance-event-history/v1/definition.json")
    schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
    specs = [
        {
            "slug": "project-semantic-event-history",
            "definition_id": "cal.definition.project-semantic-event-history",
            "term": "Project Semantic Event History",
            "statement": "A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests.",
            "boundary": "It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.",
            "example": "The first event records that the Decision 0071 operational foundation entered the durable migration Project State.",
        },
        {
            "slug": "project-governance-event-history",
            "definition_id": "cal.definition.project-governance-event-history",
            "term": "Project Governance Event History",
            "statement": "A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.",
            "boundary": "It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.",
            "example": "The first governance event binds the Decision 0071 owner authorization and immutable admission bundle to semantic event 1.",
        },
    ]
    renderer = definition_renderer()
    entries = []
    for spec in specs:
        version = "1.0.0-candidate.1"
        ref = f"{spec['definition_id']}@{version}"
        record = copy.deepcopy(base)
        record.update(
            {
                "definition_id": spec["definition_id"],
                "term": spec["term"],
                "version": version,
                "aliases": [],
                "boundaries": [spec["boundary"], "The term supplies meaning only; carrier shape, admission, relation availability, runtime behavior, and authority effect require separate admitted contracts."],
                "claim_ceiling": f"This candidate defines {spec['term']} for the Decision 0071 bootstrap only. It creates no admission, Project State transition, relation, runtime, or external effect.",
                "evidence_refs": ["docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json", "authority/admissions/cyberalchemy-lab-operational-foundation/v1/bundle.json"],
                "index_entry": {"entry_id": ref, "index_ref": "authority/definitions/DEFINITIONS-INDEX.md"},
                "primary_consumer_refs": ["cal.artifact-type.project-state/v1"],
                "residue_refs": ["Definition and carrier admission are atomic in Decision 0072.", "Runtime consumption and later state transitions remain separate."],
                "schema_digest": sha(schema_path),
                "schema_ref": "cal.schema.definition/v1",
                "scope": {"applicability": spec["statement"], "authority_scope_ref": f"scope:{spec['slug']}-definition", "exclusions": [spec["boundary"], "This Definition does not create an Artifact Type, instance, Typed Relation, runtime, authority grant, or external effect."]},
                "semantic_owner_ref": "role:definition-owner",
                "source_refs": [{"admission_posture": "admitted", "content_sha256": sha(FOUNDATION / "bundle.json"), "selector": "whole-file", "source_admission_ref": "CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION", "source_ref": "cal.source.decision-0071-operational-foundation"}],
                "typed_relations": [],
                "voices": {
                    "domain_context": {"examples": [spec["example"]], "explanation": f"In the Lab, {spec['term']} supplies the replay surface needed by immutable Project State successors.", "normative": False, "workspace_ref": str(LAB)},
                    "plain_language": {"explanation": f"{spec['statement']} {spec['boundary']}", "normative": False},
                    "scientific_formal": {"boundary_conditions": [spec["statement"], spec["boundary"], "Identity, evidence, authority, and lifecycle effects remain separately governed."], "formal_expression": f"{spec['term'].replace(' ', '')}(x) => append_only(x) and digest_bound(x); {spec['term'].replace(' ', '')}(x) =/=> authority_effect(x).", "normative_statement": f"{spec['statement']} {spec['boundary']}", "notation": [{"symbol": "x", "meaning": f"One history evaluated under the {spec['term']} Definition."}], "testable_conditions": ["Every event has one cursor, predecessor digest, event digest, and exact record reference.", "Every use resolves this admitted Definition version or a later admitted successor.", "No consumer infers authority, runtime activation, or ontology truth from the term alone."]},
                },
            }
        )
        path = DEFINITION_ROOT / "definitions" / spec["slug"] / "v1" / "definition.json"
        dump(path, record)
        write(path.with_name("DEFINITION.md"), renderer.render(record))
        entries.append({"definition_id": spec["definition_id"], "version": version, "term": spec["term"], "path": str(path.relative_to(LAB)), "sha256": sha(path), "ref": ref})
    return entries


def semantic_schema() -> dict[str, Any]:
    binding = {"type": "object", "additionalProperties": False, "required": ["path", "sha256"], "properties": {"path": {"type": "string", "minLength": 1}, "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}}}
    relation = {"type": "object", "additionalProperties": False, "required": ["relation_kind_ref", "direction", "counterpart_kind", "counterpart_ref"], "properties": {"relation_kind_ref": {"type": "string", "minLength": 1}, "direction": {"enum": ["source", "target"]}, "counterpart_kind": {"type": "string", "minLength": 1}, "counterpart_ref": {"type": "string", "minLength": 1}}}
    event = {"type": "object", "additionalProperties": False, "required": ["event_id", "event_digest", "cursor", "previous_event_digest", "change_kind", "predecessor_state_ref", "predecessor_state_digest", "resulting_state_ref", "resulting_state_digest", "material_refs", "record_ref", "semantic_summary"], "properties": {"event_id": {"type": "string", "minLength": 1}, "event_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "cursor": {"type": "integer", "minimum": 1}, "previous_event_digest": {"oneOf": [{"type": "null"}, {"type": "string", "pattern": "^[a-f0-9]{64}$"}]}, "change_kind": {"type": "string", "minLength": 1}, "predecessor_state_ref": {"type": "string", "minLength": 1}, "predecessor_state_digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"}, "resulting_state_ref": {"type": "string", "minLength": 1}, "resulting_state_digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"}, "material_refs": {"type": "array", "minItems": 1, "uniqueItems": True, "items": binding}, "record_ref": {"type": "string", "minLength": 1}, "semantic_summary": {"type": "string", "minLength": 1}}}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/project-semantic-event-history/v1", "type": "object", "additionalProperties": False, "required": ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect", "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs", "relation_refs", "payload", "claim_ceiling"], "properties": {"schema_version": {"const": "cyberalchemy-lab-project-semantic-event-history/v1"}, "node_id": {"type": "string", "minLength": 1}, "kind": {"const": "project-semantic-event-history"}, "name": {"type": "string", "minLength": 1}, "lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]}, "authority_effect": {"const": "none"}, "owner_ref": {"type": "string", "minLength": 1}, "scope_ref": {"type": "string", "minLength": 1}, "evidence_refs": {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}, "challenge_route": {"type": "string", "minLength": 1}, "successor_refs": {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}, "relation_refs": {"type": "array", "items": relation}, "payload": {"type": "object", "additionalProperties": False, "required": ["history_id", "project_ref", "subject_ref", "stream_id", "events", "latest_cursor", "chain_digest", "append_only", "event_records_are_replay_source", "history_manifest_is_event_index"], "properties": {"history_id": {"type": "string", "minLength": 1}, "project_ref": {"type": "string", "minLength": 1}, "subject_ref": {"type": "string", "minLength": 1}, "stream_id": {"type": "string", "minLength": 1}, "events": {"type": "array", "minItems": 1, "items": event}, "latest_cursor": {"type": "integer", "minimum": 1}, "chain_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "append_only": {"const": True}, "event_records_are_replay_source": {"const": True}, "history_manifest_is_event_index": {"const": True}}}, "claim_ceiling": {"type": "string", "minLength": 1}}}


def governance_schema() -> dict[str, Any]:
    relation = {"type": "object", "additionalProperties": False, "required": ["relation_kind_ref", "direction", "counterpart_kind", "counterpart_ref"], "properties": {"relation_kind_ref": {"type": "string", "minLength": 1}, "direction": {"enum": ["source", "target"]}, "counterpart_kind": {"type": "string", "minLength": 1}, "counterpart_ref": {"type": "string", "minLength": 1}}}
    event = {"type": "object", "additionalProperties": False, "required": ["event_id", "event_digest", "governance_cursor", "previous_event_digest", "semantic_event_ref", "decision_ref", "authorization_ref", "authorization_sha256", "policy_ref", "challenge_contract_ref", "upstream_governance_evidence_refs", "record_ref", "governance_summary"], "properties": {"event_id": {"type": "string", "minLength": 1}, "event_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "governance_cursor": {"type": "integer", "minimum": 1}, "previous_event_digest": {"oneOf": [{"type": "null"}, {"type": "string", "pattern": "^[a-f0-9]{64}$"}]}, "semantic_event_ref": {"type": "object", "additionalProperties": False, "required": ["semantic_event_id", "semantic_event_digest", "semantic_cursor"], "properties": {"semantic_event_id": {"type": "string", "minLength": 1}, "semantic_event_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "semantic_cursor": {"type": "integer", "minimum": 1}}}, "decision_ref": {"type": "string", "minLength": 1}, "authorization_ref": {"type": "string", "minLength": 1}, "authorization_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "policy_ref": {"type": "string", "minLength": 1}, "challenge_contract_ref": {"type": "string", "minLength": 1}, "upstream_governance_evidence_refs": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "minLength": 1}}, "record_ref": {"type": "string", "minLength": 1}, "governance_summary": {"type": "string", "minLength": 1}}}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/project-governance-event-history/v1", "type": "object", "additionalProperties": False, "required": ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect", "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs", "relation_refs", "payload", "claim_ceiling"], "properties": {"schema_version": {"const": "cyberalchemy-lab-project-governance-event-history/v1"}, "node_id": {"type": "string", "minLength": 1}, "kind": {"const": "project-governance-event-history"}, "name": {"type": "string", "minLength": 1}, "lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]}, "authority_effect": {"const": "none"}, "owner_ref": {"type": "string", "minLength": 1}, "scope_ref": {"type": "string", "minLength": 1}, "evidence_refs": {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}, "challenge_route": {"type": "string", "minLength": 1}, "successor_refs": {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}, "relation_refs": {"type": "array", "items": relation}, "payload": {"type": "object", "additionalProperties": False, "required": ["history_id", "project_ref", "subject_ref", "stream_id", "events", "latest_governance_cursor", "chain_digest", "append_only", "semantic_patch_forbidden", "event_records_are_replay_source", "history_manifest_is_event_index"], "properties": {"history_id": {"type": "string", "minLength": 1}, "project_ref": {"type": "string", "minLength": 1}, "subject_ref": {"type": "string", "minLength": 1}, "stream_id": {"type": "string", "minLength": 1}, "events": {"type": "array", "minItems": 1, "items": event}, "latest_governance_cursor": {"type": "integer", "minimum": 1}, "chain_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "append_only": {"const": True}, "semantic_patch_forbidden": {"const": True}, "event_records_are_replay_source": {"const": True}, "history_manifest_is_event_index": {"const": True}}}, "claim_ceiling": {"type": "string", "minLength": 1}}}


def build_artifact_type(root: Path, kind: str, name: str, definition: dict[str, Any], schema: dict[str, Any], purpose: str, neighbors: list[str]) -> dict[str, Any]:
    dump(root / "schema.json", schema)
    root_type = MODEL / "artifact-type-registry.json"
    current_registry = load(root_type)
    root_contract = next(item for item in current_registry["admitted_contracts"] if item["artifact_type_ref"] == "cal.artifact-type.artifact-type/v3")
    artifact_type_id = f"cal.artifact-type.{kind}"
    artifact_type_ref = f"{artifact_type_id}/v1"
    descriptor = {
        "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2",
        "artifact_type_id": artifact_type_id,
        "artifact_type_ref": artifact_type_ref,
        "version": "1.0.0-candidate.1",
        "name": name,
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v3", "semantic_kind": kind, "authority_kind": "none", "lifecycle_posture_ref": "candidate:project-state-bootstrap/v1"},
        "semantic_owner_ref": "role:artifact-type-owner",
        "semantic_definition_refs": [definition["ref"]],
        "semantic_definition_bindings": [{"definition_ref": definition["ref"], "path": definition["path"], "sha256": definition["sha256"], "admission_posture": "proposed-atomic-admission", "admission_decision_ref": DECISION}],
        "artifact_type_root_binding": {"path": root_contract["artifact_path"], "sha256": root_contract["artifact_sha256"], "admission_decision_ref": root_contract["admission_decision_ref"]},
        "schema_ref": f"cal.schema.{kind}/v1",
        "schema_digest": sha(root / "schema.json"),
        "instance_contract": {"canonical_filename": "record.json", "human_filename": "RECORD.md", "identity_field": "node_id", "instance_discriminator": {"path": "/schema_version", "value": f"cyberalchemy-lab-{kind}/v1"}, "closed_representation": True, "required_semantic_fields": ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect", "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs", "relation_refs", "payload", "claim_ceiling"], "forbidden_canonical_fields": ["implicit_admission", "implicit_relation", "derived_authority", "runtime_activation"]},
        "distinct_validation_purpose": purpose,
        "allowed_relation_kinds": [],
        "relation_roles": [],
        "hostile_non_collapse": neighbors,
        "orthogonality_rules": [{"rule_id": f"{kind.upper()}-IDENTITY", "statement": f"{name} retains its own identity and is not Project State, an ontology history, or a derived view."}, {"rule_id": f"{kind.upper()}-REPLAY", "statement": "Only ordered digest-bound event records are replay sources; projections and indexes are not competing sources."}, {"rule_id": f"{kind.upper()}-AUTHORITY", "statement": "Schema validity and event presence create no admission, authority, truth, or runtime effect."}, {"rule_id": f"{kind.upper()}-NON-COLLAPSE", "statement": f"{name} remains distinct from {', '.join(neighbors)}."}],
        "relation_model_binding": {"path": "authority/relation-kinds/candidates/0005-definition-complete-extension/model.json", "sha256": sha(LAB / "authority/relation-kinds/candidates/0005-definition-complete-extension/model.json"), "status": "admitted-by-CAL-DECISION-0070"},
        "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": "tooling/generators/endpoint_carrier.py", "shared_generator_sha256": sha(LAB / "tooling/generators/endpoint_carrier.py")},
        "four_facets": {"classification": f"Candidate {name} carrier.", "schema": "schema.json is a closed kind-specific contract.", "human_continuation": "ARTIFACT.md and fixture RECORD.md are generated projections.", "machine_checkable": "Definition binding, closed schema, event digests, fixtures, hostile cases, and projections are executable."},
        "validation_contract": {"admission_effect": "none", "assessment_scope": "project-state-bootstrap-event-history", "positive_witness": "fixtures/valid/record.json", "positive_projection": "fixtures/valid/RECORD.md", "negative_witnesses": ["fixtures/invalid/authority.json", "fixtures/invalid/extra-field.json"], "required_checks": ["atomic Definition binding", "current Artifact Type root", "closed schema", "event chain integrity", "hostile rejection", "deterministic projections"], "validator_path": str((root / "validate.py").relative_to(LAB))},
        "typed_residue": [{"residue_id": f"{kind.upper()}-R1", "owner_ref": "role:artifact-type-owner", "missing": "Exact Decision 0072 atomic admission.", "consequence": "Carrier and instances remain candidate-only."}],
        "claim_ceiling": f"Candidate {name}/v1 carrier. PASS proves only the exact schema, Definition binding, fixtures, event integrity, and projections; it does not admit the type or any instance.",
    }
    dump(root / "artifact.json", descriptor)
    return descriptor


def build_instances(definitions: list[dict[str, Any]], semantic_descriptor: dict[str, Any], governance_descriptor: dict[str, Any]) -> dict[str, Any]:
    old_state_path = FOUNDATION / "instances/artifacts/project-state.json"
    old_state = load(old_state_path)
    old_state_digest = old_state["payload"]["state_digest"]
    material_paths = [LAB / path for path in old_state["payload"]["artifact_refs"]] + [LAB / "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json", FOUNDATION / "bundle.json"]
    materials = [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in material_paths]
    state_digest = f"sha256:{digest(materials)}"
    semantic_core = {"event_id": "project-semantic-event:cyberalchemy-v2-to-lab-migration:1", "cursor": 1, "previous_event_digest": None, "change_kind": "operational-foundation-admitted", "predecessor_state_ref": OLD_STATE, "predecessor_state_digest": old_state_digest, "resulting_state_ref": NEW_STATE, "resulting_state_digest": state_digest, "material_refs": [{"path": str((LAB / "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json").relative_to(LAB)), "sha256": sha(LAB / "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json")}, {"path": str((FOUNDATION / "bundle.json").relative_to(LAB)), "sha256": sha(FOUNDATION / "bundle.json")}], "record_ref": str((FOUNDATION / "bundle.json").relative_to(LAB)), "semantic_summary": "Decision 0071 admitted the minimum durable CyberAlchemy Lab operational foundation."}
    semantic_event = {**semantic_core, "event_digest": digest(semantic_core)}
    semantic_record = {"schema_version": "cyberalchemy-lab-project-semantic-event-history/v1", "node_id": SEMANTIC_HISTORY, "kind": "project-semantic-event-history", "name": "CyberAlchemy v2 migration Project semantic history", "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": OWNER, "scope_ref": SCOPE, "evidence_refs": [semantic_core["record_ref"]], "challenge_route": CHALLENGE, "successor_refs": [], "relation_refs": [], "payload": {"history_id": SEMANTIC_HISTORY, "project_ref": PROJECT, "subject_ref": PROJECT, "stream_id": "project-semantic:cyberalchemy-v2-to-lab-migration", "events": [semantic_event], "latest_cursor": 1, "chain_digest": digest([semantic_event["event_digest"]]), "append_only": True, "event_records_are_replay_source": True, "history_manifest_is_event_index": True}, "claim_ceiling": "First canonical Project semantic event history through Decision 0071. It records one durable state change and no governance authority."}
    dump(INSTANCES / "project-semantic-event-history.json", semantic_record)

    auth_path = LAB / "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/authorization.json"
    governance_core = {"event_id": "project-governance-event:cyberalchemy-v2-to-lab-migration:1", "governance_cursor": 1, "previous_event_digest": None, "semantic_event_ref": {"semantic_event_id": semantic_event["event_id"], "semantic_event_digest": semantic_event["event_digest"], "semantic_cursor": 1}, "decision_ref": "CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION", "authorization_ref": str(auth_path.relative_to(LAB)), "authorization_sha256": sha(auth_path), "policy_ref": POLICY, "challenge_contract_ref": CHALLENGE, "upstream_governance_evidence_refs": [str(auth_path.relative_to(LAB)), "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json", str((FOUNDATION / "bundle.json").relative_to(LAB))], "record_ref": "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json", "governance_summary": "Repository owner authorization admitted the exact Decision 0071 operational foundation under the foundation Policy and Challenge Contract."}
    governance_event = {**governance_core, "event_digest": digest(governance_core)}
    governance_record = {"schema_version": "cyberalchemy-lab-project-governance-event-history/v1", "node_id": GOVERNANCE_HISTORY, "kind": "project-governance-event-history", "name": "CyberAlchemy v2 migration Project governance history", "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": OWNER, "scope_ref": SCOPE, "evidence_refs": governance_core["upstream_governance_evidence_refs"], "challenge_route": CHALLENGE, "successor_refs": [], "relation_refs": [], "payload": {"history_id": GOVERNANCE_HISTORY, "project_ref": PROJECT, "subject_ref": PROJECT, "stream_id": "project-governance:cyberalchemy-v2-to-lab-migration", "events": [governance_event], "latest_governance_cursor": 1, "chain_digest": digest([governance_event["event_digest"]]), "append_only": True, "semantic_patch_forbidden": True, "event_records_are_replay_source": True, "history_manifest_is_event_index": True}, "claim_ceiling": "First canonical Project governance event history through Decision 0071. It observes exact authority evidence and cannot alter semantic state."}
    dump(INSTANCES / "project-governance-event-history.json", governance_record)

    state = copy.deepcopy(old_state)
    state.update({"node_id": NEW_STATE, "name": "CyberAlchemy v2 migration operational state after Decision 0071", "lifecycle_state": "candidate", "evidence_refs": [item["path"] for item in materials], "successor_refs": [], "relation_refs": [{"relation_kind_ref": "relation.member-of", "direction": "source", "counterpart_kind": "project", "counterpart_ref": PROJECT}, {"relation_kind_ref": "relation.successor-of", "direction": "source", "counterpart_kind": "project-state", "counterpart_ref": OLD_STATE}], "payload": {"project_ref": PROJECT, "cursor": "decision:0071", "artifact_refs": [item["path"] for item in materials], "decision_refs": old_state["payload"]["decision_refs"] + ["CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"], "semantic_history_ref": SEMANTIC_HISTORY, "governance_history_ref": GOVERNANCE_HISTORY, "state_digest": state_digest}, "claim_ceiling": "Immutable successor Project State through Decision 0071. Decision 0072 and later work belong in another governed successor."})
    dump(INSTANCES / "project-state.json", state)

    typed_fixture = load(LAB / "authority/artifact-types/typed-relation/v2/fixtures/valid/record.json")
    relations = []
    specs = [("successor-state-successor-of-initial", "relation.successor-of", "project-state", NEW_STATE, "project-state", OLD_STATE, {"succession_effect": "continues-and-supersedes-current-state"}), ("successor-state-member-of-project", "relation.member-of", "project-state", NEW_STATE, "project", PROJECT, {"membership_role": "durable-project-state"})]
    for slug, kind, sk, sr, tk, tr, qualifiers in specs:
        record = merge(copy.deepcopy(typed_fixture), {"node_id": f"typed-relation:project-state-bootstrap:{slug}", "name": f"Project State bootstrap {kind}", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": ["CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"], "claim_ceiling": "Exact Project State bootstrap relation; it implies only the admitted relation axis and qualifier.", "payload": {"relation_kind_ref": kind, "relation_lifecycle_state": "candidate", "source": {"kind": sk, "ref": sr, "version_ref": f"{sr}@bootstrap.1"}, "target": {"kind": tk, "ref": tr, "version_ref": f"{tr}@{'foundation.1' if tr == OLD_STATE or tr == PROJECT else 'bootstrap.1'}"}, "qualifiers": qualifiers, "relation_evidence_refs": ["CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"]}, "relation_refs": []})
        record["payload"]["qualifiers"] = qualifiers
        path = RELATIONS / f"{slug}.json"
        dump(path, record)
        relations.append({"relation_id": record["node_id"], "path": str(path.relative_to(LAB)), "sha256": sha(path), "relation_kind_ref": kind, "source_ref": sr, "target_ref": tr})
    return {"semantic": semantic_record, "governance": governance_record, "state": state, "materials": materials, "relations": relations}


def build_type_packages(definitions: list[dict[str, Any]], instance_data: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {item["definition_id"]: item for item in definitions}
    specs = [(SEMANTIC_TYPE, "project-semantic-event-history", "Project Semantic Event History", by_id["cal.definition.project-semantic-event-history"], semantic_schema(), "Canonical append-only replay history for complete Project State semantic transitions.", ["project-state", "semantic-event-history", "project-governance-event-history", "ontology-view"], instance_data["semantic"]), (GOVERNANCE_TYPE, "project-governance-event-history", "Project Governance Event History", by_id["cal.definition.project-governance-event-history"], governance_schema(), "Canonical append-only governance history joined to exact Project semantic events and owner authority evidence.", ["project-state", "governance-event-history", "project-semantic-event-history", "policy"], instance_data["governance"])]
    renderer = endpoint_renderer()
    entries = []
    for root, kind, name, definition, schema, purpose, neighbors, fixture in specs:
        descriptor = build_artifact_type(root, kind, name, definition, schema, purpose, neighbors)
        dump(root / "fixtures/valid/record.json", fixture)
        write(root / "ARTIFACT.md", renderer.render_artifact(descriptor))
        write(root / "fixtures/valid/RECORD.md", renderer.render_instance(descriptor, fixture))
        invalid_authority = copy.deepcopy(fixture); invalid_authority["authority_effect"] = "admitted"
        invalid_extra = copy.deepcopy(fixture); invalid_extra["implicit_admission"] = True
        dump(root / "fixtures/invalid/authority.json", invalid_authority)
        dump(root / "fixtures/invalid/extra-field.json", invalid_extra)
        write(root / "validate.py", "#!/usr/bin/env python3\nfrom pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).parents[3] / 'project-state-transitions/candidates/0001-decision-0071-bootstrap/validate.py'), run_name='__main__')\n")
        entries.append({"artifact_type_id": descriptor["artifact_type_id"], "artifact_type_ref": descriptor["artifact_type_ref"], "semantic_kind": kind, "artifact_path": str((root / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(root / "artifact.json"), "schema_path": str((root / "schema.json").relative_to(LAB)), "schema_sha256": sha(root / "schema.json"), "fixture_path": str((root / "fixtures/valid/record.json").relative_to(LAB)), "fixture_sha256": sha(root / "fixtures/valid/record.json"), "definition_ref": definition["ref"]})
    return entries


def build_registry_postimages(definitions: list[dict[str, Any]], types: list[dict[str, Any]]) -> None:
    live = load(LAB / "authority/definitions/registry.json")
    dpost = copy.deepcopy(live)
    dpost["predecessor"] = {"path": "authority/definitions/registry.json", "sha256": sha(LAB / "authority/definitions/registry.json"), "admission_decision_ref": live["admission_decision_ref"], "entry_count": len(live["entries"]), "current_count": len(live["current_lookup"])}
    for item in definitions:
        dpost["entries"].append({"admission_decision_ref": DECISION, "definition_id": item["definition_id"], "version": item["version"], "term": item["term"], "path": item["path"], "sha256": item["sha256"], "lifecycle_state": "admitted"})
        dpost["current_lookup"][item["definition_id"]] = item["ref"]
    dpost["entries"] = sorted(dpost["entries"], key=lambda item: (item["definition_id"], item["version"]))
    dpost["current_lookup"] = dict(sorted(dpost["current_lookup"].items()))
    dpost.update({"admission_decision_ref": DECISION, "authority_effect": "one-hundred-eighty-eight-exact-definition-versions-canonical", "claim_ceiling": "This registry contains 188 admitted Definition versions and selects 182 current identities. Decision 0072 adds only the two Project event history Definitions; it does not activate a runtime."})
    dump(ROOT / "definition-registry-postimage.json", dpost)
    lines = ["<!-- GENERATED FILE: canonical data is definition-registry-postimage.json. -->", "", "# CyberAlchemy Lab Definition Index", "", f"- Status: `owner-admitted-postimage`", f"- Admission decision: `{DECISION}`", "", "| ID | Version | Term | Lifecycle | Path |", "| --- | --- | --- | --- | --- |"]
    lines.extend(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |" for item in dpost["entries"])
    lines.extend(["", "## Current lookup", ""] + [f"- `{k}` -> `{v}`" for k, v in dpost["current_lookup"].items()] + ["", "## Claim ceiling", "", dpost["claim_ceiling"], ""])
    write(ROOT / "DEFINITIONS-INDEX-postimage.md", "\n".join(lines))

    areg = load(MODEL / "artifact-type-registry.json")
    apost = copy.deepcopy(areg)
    for item in types:
        apost["admitted_contracts"].append({"admission_decision_ref": DECISION, "artifact_path": item["artifact_path"], "artifact_sha256": item["artifact_sha256"], "artifact_type_ref": item["artifact_type_ref"], "instance_discriminator": {"path": "/schema_version", "value": f"cyberalchemy-lab-{item['semantic_kind']}/v1"}, "lifecycle_state": "admitted-current", "schema_path": item["schema_path"], "schema_selector": None, "schema_sha256": item["schema_sha256"], "semantic_definition_refs": [item["definition_ref"]], "semantic_kind": item["semantic_kind"]})
        apost["current_by_identity"][item["artifact_type_id"]] = item["artifact_type_ref"]
        apost["descriptors"].append({"activation_state": "not-activated", "artifact_type_id": item["artifact_type_id"], "artifact_type_ref": item["artifact_type_ref"], "descriptor_path": item["artifact_path"], "descriptor_sha256": item["artifact_sha256"], "descriptor_version": "1.0.0-candidate.1", "effective_decision_refs": [DECISION], "effective_state": "admitted-current", "embedded_status": "candidate-unadmitted", "instance_discriminator": {"path": "/schema_version", "value": f"cyberalchemy-lab-{item['semantic_kind']}/v1"}, "proposed_primary_definition_ref": None, "resolution_target_ref": None, "schema_path": item["schema_path"], "schema_sha256": item["schema_sha256"], "semantic_binding_posture": "current-as-declared", "semantic_definition_refs": [item["definition_ref"]]})
    apost["admitted_contracts"] = sorted(apost["admitted_contracts"], key=lambda item: (item["artifact_type_ref"], item["artifact_path"]))
    apost["descriptors"] = sorted(apost["descriptors"], key=lambda item: (item["artifact_type_id"], item["artifact_type_ref"], item["descriptor_path"]))
    apost["current_by_identity"] = dict(sorted(apost["current_by_identity"].items()))
    apost["registry_id"] = "CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0006"
    apost["version"] = "2.0.0-candidate.6"
    apost["status"] = "owner-admitted-postimage"
    apost["authority_effect"] = "two-project-event-history-artifact-types-admitted"
    apost["inventory"]["admitted_contract_count"] = len(apost["admitted_contracts"])
    apost["inventory"]["admitted_current_count"] = sum(item["lifecycle_state"] == "admitted-current" for item in apost["admitted_contracts"])
    apost["inventory"]["admitted_historical_count"] = sum(item["lifecycle_state"] == "admitted-historical" for item in apost["admitted_contracts"])
    apost["inventory"]["descriptor_count"] = len(apost["descriptors"])
    apost["inventory"]["descriptor_identity_count"] = len({item["artifact_type_id"] for item in apost["descriptors"]})
    apost["inventory"]["descriptor_declared_ref_count"] = len({item["artifact_type_ref"] for item in apost["descriptors"]})
    apost["inventory"]["descriptor_resolved_ref_count"] = sum(item["effective_state"] != "resolved-duplicate" for item in apost["descriptors"])
    apost["inventory"]["state_counts"] = dict(Counter(item["effective_state"] for item in apost["descriptors"]))
    apost["inventory"]["semantic_binding_counts"] = dict(Counter(item["semantic_binding_posture"] for item in apost["descriptors"]))
    apost["claim_ceiling"] = "Decision 0072 postimage adding two exact Project event history Artifact Types. It activates no runtime and changes no Relation Kind or endpoint pair."
    dump(ROOT / "artifact-type-registry-postimage.json", apost)


def build_manifest(definitions: list[dict[str, Any]], types: list[dict[str, Any]], data: dict[str, Any]) -> None:
    artifacts = []
    for name, type_ref, kind, identity in [("project-semantic-event-history.json", types[0]["artifact_type_ref"], types[0]["semantic_kind"], SEMANTIC_HISTORY), ("project-governance-event-history.json", types[1]["artifact_type_ref"], types[1]["semantic_kind"], GOVERNANCE_HISTORY), ("project-state.json", "cal.artifact-type.project-state/v1", "project-state", NEW_STATE)]:
        path = INSTANCES / name
        artifacts.append({"identity_ref": identity, "carrier_type_ref": type_ref, "semantic_kind": kind, "path": str(path.relative_to(LAB)), "sha256": sha(path), "version_ref": f"{identity}@bootstrap.1"})
    manifest = {"schema_version": "cyberalchemy-lab-project-state-bootstrap/v1", "transition_id": "CAL-PROJECT-STATE-BOOTSTRAP-0001", "decision_id": DECISION, "status": "candidate-awaiting-admission", "authority_effect": "none", "project_ref": PROJECT, "predecessor_state_ref": OLD_STATE, "successor_state_ref": NEW_STATE, "inputs": {"foundation_bundle": {"path": str((FOUNDATION / "bundle.json").relative_to(LAB)), "sha256": sha(FOUNDATION / "bundle.json")}, "foundation_decision": {"path": "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json", "sha256": sha(LAB / "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json")}, "artifact_type_registry": {"path": str((MODEL / "artifact-type-registry.json").relative_to(LAB)), "sha256": sha(MODEL / "artifact-type-registry.json")}, "definition_registry": {"path": "authority/definitions/registry.json", "sha256": sha(LAB / "authority/definitions/registry.json")}}, "counts": {"definitions": 2, "artifact_types": 2, "artifact_instances": 3, "typed_relation_instances": 2, "semantic_events": 1, "governance_events": 1, "runtime_activations": 0}, "definitions": definitions, "artifact_types": types, "artifact_instances": artifacts, "typed_relations": data["relations"], "registry_postimages": {"definitions": {"path": str((ROOT / "definition-registry-postimage.json").relative_to(LAB)), "sha256": sha(ROOT / "definition-registry-postimage.json")}, "definition_index": {"path": str((ROOT / "DEFINITIONS-INDEX-postimage.md").relative_to(LAB)), "sha256": sha(ROOT / "DEFINITIONS-INDEX-postimage.md")}, "artifact_types": {"path": str((ROOT / "artifact-type-registry-postimage.json").relative_to(LAB)), "sha256": sha(ROOT / "artifact-type-registry-postimage.json")}}, "integrity": {"predecessor_state_digest": data["semantic"]["payload"]["events"][0]["predecessor_state_digest"], "successor_state_digest": data["state"]["payload"]["state_digest"], "semantic_event_digest": data["semantic"]["payload"]["events"][0]["event_digest"], "semantic_chain_digest": data["semantic"]["payload"]["chain_digest"], "governance_event_digest": data["governance"]["payload"]["events"][0]["event_digest"], "governance_chain_digest": data["governance"]["payload"]["chain_digest"]}, "excluded_effects": ["No Agent, Session, Context View, Evidence Set, Finding, Ontology Node, Edge, Cut, or View is created", "No implementation, capability realization, consumer, service, or runtime is activated", "Decision 0072 is not self-included in the Decision 0071 successor state", "No migration, cutover, deployment, publication, or external effect occurs"], "claim_ceiling": "Candidate closes only the Decision 0071 Project State bootstrap with two new event history contracts, one semantic event, one governance event, one successor state, and two Typed Relations. It has no effect before Decision 0072 application."}
    dump(ROOT / "transition.json", manifest)
    write(ROOT / "TRANSITION.md", "\n".join(["# Decision 0071 Project State bootstrap", "", "- Definitions: `2`", "- Artifact Types: `2`", "- Artifact instances: `3`", "- Typed Relations: `2`", "- Semantic events: `1`", "- Governance events: `1`", "- Runtime activations: `0`", "", f"`{NEW_STATE}` succeeds `{OLD_STATE}` and binds Decision 0071 through separate semantic and governance replay histories.", "", "## Claim ceiling", "", manifest["claim_ceiling"], ""]))


def main() -> None:
    for path in (INSTANCES, RELATIONS, DEFINITION_ROOT, SEMANTIC_TYPE, GOVERNANCE_TYPE):
        if path.exists(): shutil.rmtree(path)
    definitions = build_definitions()
    data = build_instances(definitions, {}, {})
    types = build_type_packages(definitions, data)
    build_registry_postimages(definitions, types)
    build_manifest(definitions, types, data)
    print(json.dumps(load(ROOT / "transition.json")["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
