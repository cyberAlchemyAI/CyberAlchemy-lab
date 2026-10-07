#!/usr/bin/env python3
"""Materialize the missing governance interaction and admission transaction carriers."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
MODEL = LAB / "authority/relation-kinds/candidates/0007-governance-transaction-extension/model.json"
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
REGISTRY = LAB / "authority/definitions/registry.json"
TRANSACTION_DEF = LAB / "authority/definitions/candidates/0016-admission-transaction/definitions/admission-transaction/v1/definition.json"
GENERATOR = LAB / "tooling/generators/endpoint_carrier.py"
VALIDATOR = ROOT / "validate_carrier.py"
AUDIT = LAB / "authority/governance/candidates/0002-approval-admission-boundary-audit/audit.json"
PENDING_TRANSITION = LAB / "authority/project-state-transitions/candidates/0002-decision-0073-successor/transition.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_object(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def s(min_length: int = 1) -> dict:
    return {"type": "string", "minLength": min_length}


def strings(min_items: int = 0) -> dict:
    value = {"type": "array", "items": s(), "uniqueItems": True}
    if min_items:
        value["minItems"] = min_items
    return value


def closed_object(properties: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "additionalProperties": False, "properties": properties, "required": required or list(properties)}


DECISION_ITEM = closed_object({
    "decision_ref": s(),
    "decision_core_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "owner_ref": s(),
    "scope_ref": s(),
    "effect_kind": s(),
    "target_refs": strings(1),
    "target_digests": {"type": "array", "minItems": 1, "items": closed_object({"target_ref": s(), "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}})},
    "selected_outcome": {"type": ["string", "null"], "minLength": 1},
})


PAYLOAD_SCHEMAS = {
    "authority-boundary": closed_object({
        "owner_role_ref": s(), "accountable_principal_ref": s(), "authority_scope_ref": s(),
        "allowed_effect_kinds": strings(1), "excluded_effect_kinds": strings(), "challenge_route_ref": s(),
        "effective_period": s(), "revocation_state": {"enum": ["not-revoked", "revoked", "expired"]},
    }),
    "decision-bundle": closed_object({
        "checkpoint_ref": s(),
        "ordered_decisions": {"type": "array", "minItems": 1, "items": DECISION_ITEM},
        "all_targets_materialized": {"const": True},
        "bundle_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "atomicity_requirement": {"const": "all-or-nothing"},
        "invalidation_conditions": strings(1),
    }),
    "decision-checkpoint": closed_object({
        "workflow_instance_ref": s(), "workflow_profile_ref": s(),
        "checkpoint_kind": {"enum": ["before-application", "final-review"]},
        "decision_bundle_ref": s(), "presentation_state": {"enum": ["pending", "resolved", "invalidated"]},
        "resolved_preference_ref": {"type": ["string", "null"], "minLength": 1},
        "opened_at": s(), "closed_at": {"type": ["string", "null"], "minLength": 1},
    }),
    "user-decision-preference": closed_object({
        "user_ref": s(), "scope_kind": {"enum": ["workflow-type", "workflow-instance"]}, "scope_ref": s(),
        "preferred_checkpoint_kind": {"enum": ["before-application", "final-review"]},
        "profile_ref": s(), "status": {"enum": ["active", "superseded", "withdrawn"]},
        "invalidation_conditions": strings(1),
    }),
    "workflow-decision-profile": closed_object({
        "workflow_type_ref": s(), "decision_mode": {"enum": ["none", "single"]},
        "allowed_checkpoint_kinds": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"enum": ["before-application", "final-review"]}},
        "default_checkpoint_kind": {"type": ["string", "null"], "enum": ["before-application", "final-review", None]},
        "exact_target_required": {"const": True}, "none_mode_authority_basis_refs": strings(),
        "invalidation_conditions": strings(1), "post_decision_continuation_limit": {"type": "integer", "minimum": 0},
    }),
    "admission-transaction": closed_object({
        "project_ref": s(), "decision_bundle_ref": s(),
        "decision_core_refs": {"type": "array", "minItems": 1, "items": closed_object({"decision_ref": s(), "decision_core_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "selected_outcome": {"type": ["string", "null"], "minLength": 1}})},
        "review_bundle_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "resolved_bundle_digest": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"},
        "authorization_evidence_ref": {"type": ["string", "null"], "minLength": 1}, "authorization_evidence_sha256": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"},
        "input_state_ref": s(), "input_state_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "admission_targets": {"type": "array", "minItems": 1, "items": closed_object({"target_ref": s(), "target_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}, "effect_kind": s()})},
        "deterministic_consequences": {"type": "array", "minItems": 1, "items": closed_object({"consequence_ref": s(), "consequence_kind": s(), "declared_input_ref": s(), "output_sha256": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"}})},
        "atomicity": {"const": "all-or-nothing"}, "application_state": {"enum": ["planned", "applied", "rolled-back", "failed"]},
        "application_receipt_ref": {"type": ["string", "null"], "minLength": 1}, "rollback_ref": s(), "runtime_activations": {"const": 0},
        "external_effect_refs": {"type": "array", "maxItems": 0},
        "decision_core_hash_policy": {"const": "stable-core-excludes-generated-consequence-digests"},
        "output_binding_policy": {"const": "application-receipt-binds-final-output-digests"},
    }),
}


ZERO = "0" * 64
ONE = "1" * 64
TWO = "2" * 64
THREE = "3" * 64
FOUR = "4" * 64
FIVE = "5" * 64

PAYLOADS = {
    "authority-boundary": {
        "owner_role_ref": "role:lab-owner", "accountable_principal_ref": "principal:lab-owner",
        "authority_scope_ref": "decision-scope:governance-transaction-surface", "allowed_effect_kinds": ["definition-admission", "artifact-type-admission", "relation-kind-successor-admission"],
        "excluded_effect_kinds": ["runtime-activation", "external-publication", "deployment"], "challenge_route_ref": "route:lab-governance-challenge",
        "effective_period": "until-revoked-or-superseded", "revocation_state": "not-revoked",
    },
    "decision-bundle": {
        "checkpoint_ref": "decision-checkpoint:governance-transaction-review-001",
        "ordered_decisions": [
            {"decision_ref": "decision:admit-governance-carriers", "decision_core_sha256": ONE, "owner_ref": "role:artifact-type-owner", "scope_ref": "decision-scope:carrier-admission", "effect_kind": "artifact-type-admission", "target_refs": ["artifact-type-set:governance-transaction-thirteen"], "target_digests": [{"target_ref": "artifact-type-set:governance-transaction-thirteen", "sha256": TWO}], "selected_outcome": None},
            {"decision_ref": "decision:admit-transaction-definition", "decision_core_sha256": THREE, "owner_ref": "role:definition-owner", "scope_ref": "decision-scope:admission-transaction-definition", "effect_kind": "definition-admission", "target_refs": ["cal.definition.admission-transaction@1.0.0-candidate.1"], "target_digests": [{"target_ref": "cal.definition.admission-transaction@1.0.0-candidate.1", "sha256": FOUR}], "selected_outcome": None},
            {"decision_ref": "decision:admit-relation-extension", "decision_core_sha256": FIVE, "owner_ref": "role:relation-owner", "scope_ref": "decision-scope:governance-transaction-relations", "effect_kind": "relation-kind-successor-admission", "target_refs": ["relation-kind-set:governance-transaction-0007"], "target_digests": [{"target_ref": "relation-kind-set:governance-transaction-0007", "sha256": ZERO}], "selected_outcome": None},
        ],
        "all_targets_materialized": True, "bundle_digest": ZERO, "atomicity_requirement": "all-or-nothing",
        "invalidation_conditions": ["any-target-digest-change", "authority-scope-change", "new-runtime-or-external-effect", "failed-precondition"],
    },
    "decision-checkpoint": {
        "workflow_instance_ref": "workflow:governance-transaction-surface-001", "workflow_profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint",
        "checkpoint_kind": "final-review", "decision_bundle_ref": "decision-bundle:governance-transaction-surface-001",
        "presentation_state": "pending", "resolved_preference_ref": "user-decision-preference:lab-owner-final-review", "opened_at": "2026-10-06T00:00:00-03:00", "closed_at": None,
    },
    "user-decision-preference": {
        "user_ref": "principal:lab-owner", "scope_kind": "workflow-type", "scope_ref": "workflow-type:governed-repository-change",
        "preferred_checkpoint_kind": "final-review", "profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint",
        "status": "active", "invalidation_conditions": ["profile-no-longer-allows-final-review", "owner-withdrawal"],
    },
    "workflow-decision-profile": {
        "workflow_type_ref": "workflow-type:governed-repository-change", "decision_mode": "single",
        "allowed_checkpoint_kinds": ["final-review"], "default_checkpoint_kind": "final-review", "exact_target_required": True,
        "none_mode_authority_basis_refs": [], "invalidation_conditions": ["unmaterialized-target", "authority-owner-change", "new-external-effect"],
        "post_decision_continuation_limit": 1,
    },
    "admission-transaction": {
        "project_ref": "project:cyberalchemy-lab", "decision_bundle_ref": "decision-bundle:governance-transaction-surface-001",
        "decision_core_refs": [
            {"decision_ref": "decision:admit-governance-carriers", "decision_core_sha256": ONE, "selected_outcome": None},
            {"decision_ref": "decision:admit-transaction-definition", "decision_core_sha256": THREE, "selected_outcome": None},
            {"decision_ref": "decision:admit-relation-extension", "decision_core_sha256": FIVE, "selected_outcome": None},
        ],
        "review_bundle_digest": ZERO, "resolved_bundle_digest": None,
        "authorization_evidence_ref": None, "authorization_evidence_sha256": None,
        "input_state_ref": "project-state:D72", "input_state_sha256": ONE,
        "admission_targets": [
            {"target_ref": "artifact-type-set:governance-transaction-thirteen", "target_sha256": TWO, "effect_kind": "artifact-type-admission"},
            {"target_ref": "cal.definition.admission-transaction@1.0.0-candidate.1", "target_sha256": FOUR, "effect_kind": "definition-admission"},
            {"target_ref": "relation-kind-set:governance-transaction-0007", "target_sha256": ZERO, "effect_kind": "relation-kind-successor-admission"},
        ],
        "deterministic_consequences": [
            {"consequence_ref": "project-state-transition:decision-0073-successor", "consequence_kind": "project-state", "declared_input_ref": "decision:0073", "output_sha256": sha(PENDING_TRANSITION)},
            {"consequence_ref": "project-semantic-event-history:next", "consequence_kind": "project-semantic-event-history", "declared_input_ref": "decision-bundle:governance-transaction-surface-001", "output_sha256": None},
            {"consequence_ref": "project-governance-event-history:next", "consequence_kind": "project-governance-event-history", "declared_input_ref": "authorization-evidence:owner-response", "output_sha256": None},
            {"consequence_ref": "generated-output:registry-index-projections", "consequence_kind": "generated-output", "declared_input_ref": "admission-targets:exact", "output_sha256": None},
        ],
        "atomicity": "all-or-nothing", "application_state": "planned", "application_receipt_ref": None,
        "rollback_ref": "rollback:restore-input-state-D72", "runtime_activations": 0, "external_effect_refs": [],
        "decision_core_hash_policy": "stable-core-excludes-generated-consequence-digests", "output_binding_policy": "application-receipt-binds-final-output-digests",
    },
}

NEIGHBORS = {
    "authority-boundary": ["authority-claim", "decision-scope"],
    "decision-bundle": ["decision", "decision-checkpoint"],
    "decision-checkpoint": ["decision-bundle", "workflow-decision-profile"],
    "user-decision-preference": ["communication-preference", "decision"],
    "workflow-decision-profile": ["policy", "user-decision-preference"],
    "admission-transaction": ["decision", "agent-action", "project-state"],
}

PREFERRED = {
    "authority-boundary": "relation.scopes-authority-over",
    "decision-bundle": "relation.member-of",
    "decision-checkpoint": "relation.governed-by",
    "user-decision-preference": "relation.governed-by",
    "workflow-decision-profile": "relation.governed-by",
    "admission-transaction": "relation.materializes-consequence",
}


def roles_for(kind: str, model: dict) -> list[dict]:
    roles = []
    for entry in model["entries"]:
        targets = sorted({pair["target_kind"] for pair in entry["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        sources = sorted({pair["source_kind"] for pair in entry["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if targets:
            roles.append({"relation_kind_ref": entry["relation_kind_id"], "direction": "source", "counterpart_kinds": targets})
        if sources:
            roles.append({"relation_kind_ref": entry["relation_kind_id"], "direction": "target", "counterpart_kinds": sources})
    return sorted(roles, key=lambda item: (item["relation_kind_ref"], item["direction"]))


def main() -> None:
    model = load(MODEL)
    registry = load(REGISTRY)
    definition_map = {entry["definition_id"]: entry for entry in registry["entries"]}
    transaction_definition = load(TRANSACTION_DEF)
    definition_map[transaction_definition["definition_id"]] = {
        "definition_id": transaction_definition["definition_id"], "version": transaction_definition["version"], "term": transaction_definition["term"],
        "path": str(TRANSACTION_DEF.relative_to(LAB)), "sha256": sha(TRANSACTION_DEF), "lifecycle_state": "candidate-unadmitted",
    }
    spec = importlib.util.spec_from_file_location("carrier_generator", GENERATOR)
    generator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(generator)
    manifest = []
    for kind, payload in PAYLOADS.items():
        package = LAB / f"authority/artifact-types/{kind}/v1"
        shutil.rmtree(package, ignore_errors=True)
        package.mkdir(parents=True)
        roles = roles_for(kind, model)
        relation_kinds = sorted({role["relation_kind_ref"] for role in roles})
        directions = sorted({role["direction"] for role in roles})
        counterparts = sorted({counterpart for role in roles for counterpart in role["counterpart_kinds"]})
        relation_schema = closed_object({
            "relation_kind_ref": {"enum": relation_kinds}, "direction": {"enum": directions},
            "counterpart_kind": {"enum": counterparts}, "counterpart_ref": s(),
        })
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"https://cyberalchemy.local/schemas/{kind}/v1",
            "type": "object", "additionalProperties": False,
            "properties": {
                "schema_version": {"const": f"cyberalchemy-lab-{kind}/v1"}, "node_id": s(), "kind": {"const": kind}, "name": s(),
                "lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]}, "authority_effect": {"const": "none"},
                "owner_ref": s(), "scope_ref": s(), "evidence_refs": strings(), "challenge_route": s(), "successor_refs": strings(),
                "relation_refs": {"type": "array", "minItems": 1, "items": relation_schema}, "payload": PAYLOAD_SCHEMAS[kind], "claim_ceiling": s(),
            },
            "required": ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect", "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs", "relation_refs", "payload", "claim_ceiling"],
        }
        dump(package / "schema.json", schema)
        definition = definition_map[f"cal.definition.{kind}"]
        definition_ref = f"{definition['definition_id']}@{definition['version']}"
        admitted = definition["lifecycle_state"] == "admitted"
        artifact = {
            "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2", "artifact_type_id": f"cal.artifact-type.{kind}", "artifact_type_ref": f"cal.artifact-type.{kind}/v1",
            "version": "1.0.0-candidate.1", "name": definition["term"], "status": "candidate-unadmitted", "authority_effect": "none",
            "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v2", "semantic_kind": kind, "authority_kind": "none", "lifecycle_posture_ref": "candidate:governance-transaction-surface/v1"},
            "artifact_type_root_binding": {"path": str(ROOT_TYPE.relative_to(LAB)), "sha256": sha(ROOT_TYPE), "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"},
            "semantic_owner_ref": "role:artifact-type-owner", "semantic_definition_refs": [definition_ref],
            "semantic_definition_bindings": [{"definition_ref": definition_ref, "path": definition["path"], "sha256": definition["sha256"], "admission_posture": "admitted" if admitted else "candidate-unadmitted", "admission_decision_ref": definition.get("admission_decision_ref")}],
            "relation_model_binding": {"path": str(MODEL.relative_to(LAB)), "sha256": sha(MODEL), "status": "candidate-unadmitted"},
            "schema_ref": f"cal.schema.{kind}/v1", "schema_digest": sha(package / "schema.json"),
            "instance_contract": {"canonical_filename": "record.json", "human_filename": "RECORD.md", "identity_field": "node_id", "instance_discriminator": {"path": "/schema_version", "value": f"cyberalchemy-lab-{kind}/v1"}, "closed_representation": True, "required_semantic_fields": schema["required"], "forbidden_canonical_fields": ["implicit_admission", "implicit_relation", "derived_authority", "runtime_activation"]},
            "distinct_validation_purpose": load(LAB / definition["path"])["voices"]["plain_language"]["explanation"],
            "allowed_relation_kinds": relation_kinds, "relation_roles": roles, "hostile_non_collapse": NEIGHBORS[kind],
            "orthogonality_rules": [
                {"rule_id": f"{kind.upper()}-IDENTITY", "statement": f"A {definition['term']} retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor."},
                {"rule_id": f"{kind.upper()}-RELATIONS", "statement": "Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields."},
                {"rule_id": f"{kind.upper()}-AUTHORITY", "statement": "Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect."},
                {"rule_id": f"{kind.upper()}-NON-COLLAPSE", "statement": f"{definition['term']} remains distinct from {', '.join(NEIGHBORS[kind])}."},
            ],
            "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": str(GENERATOR.relative_to(LAB)), "shared_generator_sha256": sha(GENERATOR)},
            "four_facets": {"classification": f"Candidate {definition['term']} carrier under Artifact Type/v2.", "schema": "schema.json is a closed kind-specific instance contract.", "human_continuation": "ARTIFACT.md and fixture RECORD.md are generated projections.", "machine_checkable": "Definition binding, relation closure, hostile cases, fixtures, digest acyclicity, and projection parity are executable."},
            "validation_contract": {"validator_path": f"authority/artifact-types/{kind}/v1/validate.py", "shared_validator_path": str(VALIDATOR.relative_to(LAB)), "shared_validator_sha256": sha(VALIDATOR), "positive_witness": "fixtures/valid/record.json", "positive_projection": "fixtures/valid/RECORD.md", "negative_witnesses": ["fixtures/invalid/authority.json", "fixtures/invalid/extra-field.json", "fixtures/invalid/missing-payload-field.json", "fixtures/invalid/undeclared-relation.json", "fixtures/invalid/collapsed-neighbor.json"], "assessment_scope": "candidate-schema-definition-relation-surface-and-projection", "admission_effect": "none", "required_checks": ["Artifact Type/v2 root", "exact Definition binding", "closed governance transaction relation model", "closed schema", "five hostile rejections", "deterministic projections"]},
            "typed_residue": [{"residue_id": f"{kind.upper()}-R1", "missing": f"Owner admission for exact {definition['term']}/v1 bytes.", "owner_ref": "role:artifact-type-owner", "consequence": "Carrier remains candidate-only."}, {"residue_id": f"{kind.upper()}-R2", "missing": "Separate instance, Typed Relation, transaction application, and runtime decisions where applicable.", "owner_ref": "role:migration-consumer-owner", "consequence": "No operational state changes."}],
            "claim_ceiling": f"This candidate {definition['term']}/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.",
        }
        dump(package / "artifact.json", artifact)
        role = next(item for item in roles if item["relation_kind_ref"] == PREFERRED[kind])
        counterpart = role["counterpart_kinds"][0]
        relation_refs = [{"relation_kind_ref": role["relation_kind_ref"], "direction": role["direction"], "counterpart_kind": counterpart, "counterpart_ref": f"{counterpart}:example-001"}]
        if kind == "admission-transaction":
            relation_refs = [
                {"relation_kind_ref": "relation.governed-by", "direction": "source", "counterpart_kind": "policy", "counterpart_ref": "policy:atomic-admission"},
                {"relation_kind_ref": "relation.materializes-consequence", "direction": "source", "counterpart_kind": "project-state", "counterpart_ref": "project-state:D73"},
            ]
        witness = {"schema_version": f"cyberalchemy-lab-{kind}/v1", "node_id": f"{kind}:example-001", "kind": kind, "name": f"Example {definition['term']}", "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:artifact-type-owner", "scope_ref": "scope:governance-transaction-model", "evidence_refs": ["evidence:approval-admission-boundary-audit"], "challenge_route": "route:artifact-type-challenge", "successor_refs": [], "relation_refs": relation_refs, "payload": payload, "claim_ceiling": f"Realistic {definition['term']} example for candidate review only."}
        dump(package / "fixtures/valid/record.json", witness)
        invalid = copy.deepcopy(witness); invalid["authority_effect"] = "admit"; dump(package / "fixtures/invalid/authority.json", invalid)
        invalid = copy.deepcopy(witness); invalid["implicit_authority"] = True; dump(package / "fixtures/invalid/extra-field.json", invalid)
        invalid = copy.deepcopy(witness); invalid["payload"].pop(next(iter(payload))); dump(package / "fixtures/invalid/missing-payload-field.json", invalid)
        invalid = copy.deepcopy(witness); invalid["relation_refs"][0]["relation_kind_ref"] = "relation.not-declared"; dump(package / "fixtures/invalid/undeclared-relation.json", invalid)
        invalid = copy.deepcopy(witness); invalid["kind"] = NEIGHBORS[kind][0]; dump(package / "fixtures/invalid/collapsed-neighbor.json", invalid)
        (package / "validate.py").write_text("#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util\nR=Path(__file__).resolve().parent;S=R.parents[3]/'authority/artifact-types/candidates/0013-governance-transaction-surface/validate_carrier.py'\ns=importlib.util.spec_from_file_location('v',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nraise SystemExit(m.validate_package(R))\n", encoding="utf-8")
        (package / "generator.py").write_text("#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util,json\nR=Path(__file__).resolve().parent;S=R.parents[3]/'tooling/generators/endpoint_carrier.py'\ns=importlib.util.spec_from_file_location('g',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\na=json.loads((R/'artifact.json').read_text());w=json.loads((R/a['validation_contract']['positive_witness']).read_text());(R/'ARTIFACT.md').write_text(m.render_artifact(a));(R/a['validation_contract']['positive_projection']).write_text(m.render_instance(a,w))\n", encoding="utf-8")
        (package / "ARTIFACT.md").write_text(generator.render_artifact(artifact), encoding="utf-8")
        (package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(artifact, witness), encoding="utf-8")
        manifest.append({"artifact_type_ref": artifact["artifact_type_ref"], "artifact_path": str((package / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(package / "artifact.json"), "schema_path": str((package / "schema.json").relative_to(LAB)), "schema_sha256": sha(package / "schema.json"), "fixture_path": str((package / "fixtures/valid/record.json").relative_to(LAB)), "fixture_sha256": sha(package / "fixtures/valid/record.json"), "definition_ref": definition_ref, "definition_posture": "admitted" if admitted else "candidate-unadmitted", "relation_role_count": len(roles)})

    impacted_kinds = ["decision", "decision-scope", "generated-output", "policy", "project-state", "project-governance-event-history", "project-semantic-event-history"]
    impacted_manifest = []
    for kind in impacted_kinds:
        source = LAB / f"authority/artifact-types/{kind}/v1"
        package = ROOT / "impacted-carrier-successors" / kind / "v2"
        shutil.rmtree(package, ignore_errors=True)
        package.mkdir(parents=True)
        artifact = copy.deepcopy(load(source / "artifact.json"))
        schema = copy.deepcopy(load(source / "schema.json"))
        witness = copy.deepcopy(load(source / artifact["validation_contract"]["positive_witness"]))
        roles = roles_for(kind, model)
        relation_kinds = sorted({role["relation_kind_ref"] for role in roles})
        directions = sorted({role["direction"] for role in roles})
        counterparts = sorted({counterpart for role in roles for counterpart in role["counterpart_kinds"]})
        artifact["artifact_type_ref"] = f"cal.artifact-type.{kind}/v2"
        artifact["version"] = "2.0.0-candidate.1"
        artifact["status"] = "candidate-unadmitted"
        artifact["classification"]["lifecycle_posture_ref"] = "candidate:governance-transaction-endpoint-successor/v2"
        artifact["relation_model_binding"] = {"path": str(MODEL.relative_to(LAB)), "sha256": sha(MODEL), "status": "candidate-unadmitted"}
        artifact["allowed_relation_kinds"] = relation_kinds
        artifact["relation_roles"] = roles
        artifact["schema_ref"] = f"cal.schema.{kind}/v2"
        artifact["instance_contract"]["instance_discriminator"]["value"] = f"cyberalchemy-lab-{kind}/v2"
        artifact["validation_contract"] = {
            "validator_path": str((package / "validate.py").relative_to(LAB)), "shared_validator_path": str(VALIDATOR.relative_to(LAB)), "shared_validator_sha256": sha(VALIDATOR),
            "positive_witness": "fixtures/valid/record.json", "positive_projection": "fixtures/valid/RECORD.md",
            "negative_witnesses": ["fixtures/invalid/authority.json", "fixtures/invalid/extra-field.json", "fixtures/invalid/missing-payload-field.json", "fixtures/invalid/undeclared-relation.json", "fixtures/invalid/collapsed-neighbor.json"],
            "assessment_scope": "candidate-relation-endpoint-successor", "admission_effect": "none",
            "required_checks": ["predecessor preserved", "closed successor schema", "exact relation roles", "five hostile rejections", "deterministic projections"],
        }
        artifact["typed_residue"] = [{"residue_id": f"{kind.upper()}-V2-R1", "missing": "Owner admission for this exact endpoint-role successor.", "owner_ref": "role:artifact-type-owner", "consequence": "The admitted v1 carrier remains current."}]
        artifact["claim_ceiling"] = f"This candidate {artifact['name']}/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing."
        schema["$id"] = f"https://cyberalchemy.local/schemas/{kind}/v2"
        schema["properties"]["schema_version"] = {"const": f"cyberalchemy-lab-{kind}/v2"}
        relation_item = schema["properties"]["relation_refs"]["items"]
        relation_item["properties"]["relation_kind_ref"] = {"enum": relation_kinds}
        relation_item["properties"]["direction"] = {"enum": directions}
        relation_item["properties"]["counterpart_kind"] = {"enum": counterparts}
        schema["properties"]["relation_refs"]["minItems"] = 1
        dump(package / "schema.json", schema)
        artifact["schema_digest"] = sha(package / "schema.json")
        dump(package / "artifact.json", artifact)
        witness["schema_version"] = f"cyberalchemy-lab-{kind}/v2"
        new_role = None
        for role in roles:
            if role["relation_kind_ref"] == "relation.materializes-consequence" or (kind == "decision" and role["relation_kind_ref"] == "relation.member-of") or (kind == "decision-scope" and role["relation_kind_ref"] == "relation.scopes-authority-over") or (kind == "policy" and role["relation_kind_ref"] == "relation.governed-by"):
                new_role = role
                break
        assert new_role is not None
        witness["relation_refs"] = [{"relation_kind_ref": new_role["relation_kind_ref"], "direction": new_role["direction"], "counterpart_kind": new_role["counterpart_kinds"][0], "counterpart_ref": f"{new_role['counterpart_kinds'][0]}:governance-transaction-example"}]
        dump(package / "fixtures/valid/record.json", witness)
        invalid = copy.deepcopy(witness); invalid["authority_effect"] = "admit"; dump(package / "fixtures/invalid/authority.json", invalid)
        invalid = copy.deepcopy(witness); invalid["implicit_authority"] = True; dump(package / "fixtures/invalid/extra-field.json", invalid)
        invalid = copy.deepcopy(witness); invalid["payload"].pop(next(iter(witness["payload"]))); dump(package / "fixtures/invalid/missing-payload-field.json", invalid)
        invalid = copy.deepcopy(witness); invalid["relation_refs"][0]["relation_kind_ref"] = "relation.not-declared"; dump(package / "fixtures/invalid/undeclared-relation.json", invalid)
        invalid = copy.deepcopy(witness); invalid["kind"] = artifact["hostile_non_collapse"][0]; dump(package / "fixtures/invalid/collapsed-neighbor.json", invalid)
        (package / "ARTIFACT.md").write_text(generator.render_artifact(artifact), encoding="utf-8")
        (package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(artifact, witness), encoding="utf-8")
        impacted_manifest.append({
            "artifact_type_ref": artifact["artifact_type_ref"], "kind": kind,
            "predecessor_artifact_path": str((source / "artifact.json").relative_to(LAB)), "predecessor_artifact_sha256": sha(source / "artifact.json"),
            "artifact_path": str((package / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(package / "artifact.json"),
            "schema_path": str((package / "schema.json").relative_to(LAB)), "schema_sha256": sha(package / "schema.json"),
            "fixture_path": str((package / "fixtures/valid/record.json").relative_to(LAB)), "fixture_sha256": sha(package / "fixtures/valid/record.json"),
        })

    # Representation closure repair discovered during admission preflight.  The
    # new Relation Kind is executable only if the Typed Relation carrier can
    # represent its exact endpoints and qualifiers.  This successor adds no
    # semantic axis; it closes the representation of the already reviewed one.
    typed_source = LAB / "authority/artifact-types/typed-relation/v2"
    typed_package = ROOT / "impacted-carrier-successors/typed-relation/v3"
    shutil.rmtree(typed_package, ignore_errors=True)
    shutil.copytree(typed_source, typed_package)
    typed_artifact = load(typed_package / "artifact.json")
    typed_schema = load(typed_package / "schema.json")
    typed_artifact["artifact_type_ref"] = "cal.artifact-type.typed-relation/v3"
    typed_artifact["version"] = "3.0.0-candidate.1"
    typed_artifact["status"] = "candidate-unadmitted"
    typed_artifact["schema_ref"] = "cal.schema.typed-relation/v3"
    typed_artifact["classification"]["lifecycle_posture_ref"] = "candidate:governance-transaction-representation-closure/v3"
    typed_artifact["instance_contract"]["instance_discriminator"]["value"] = "cyberalchemy-lab-typed-relation/v3"
    typed_artifact.pop("candidate_predecessor_contract", None)
    typed_artifact["admitted_predecessor_contract"] = {
        "admission_posture": "admitted-current-before-successor",
        "admission_decision_ref": "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION",
        "artifact_type_ref": "cal.artifact-type.typed-relation/v2",
        "path": str((typed_source / "artifact.json").relative_to(LAB)),
        "sha256": sha(typed_source / "artifact.json"),
    }
    typed_artifact["representation_closure_repair"] = {
        "kind": "required-endpoint-schema-closure",
        "relation_kind_ref": "relation.materializes-consequence",
        "semantic_scope_changed": False,
        "new_relation_kinds": 0,
        "new_runtime_effects": 0,
        "new_external_effects": 0,
    }
    typed_artifact["validation_contract"] = {
        "validator_path": str((typed_package / "validate.py").relative_to(LAB)),
        "positive_witness": "fixtures/valid/record.json",
        "negative_witnesses": [
            "fixtures/invalid/missing-qualifier.json",
            "fixtures/invalid/extra-qualifier.json",
            "fixtures/invalid/undeclared-pair.json",
            "fixtures/invalid/authority.json",
        ],
        "assessment_scope": "candidate-typed-relation-representation-closure",
        "admission_effect": "none",
        "required_checks": ["predecessor preserved", "41 relation conditions", "exact materializes-consequence endpoints", "closed qualifiers", "hostile rejection"],
    }
    typed_artifact["typed_residue"] = [{
        "residue_id": "TYPED-RELATION-V3-R1",
        "missing": "Owner admission for this exact representation-closure successor.",
        "owner_ref": "role:artifact-type-owner",
        "consequence": "Typed Relation/v2 remains current until the atomic transaction is applied.",
    }]
    typed_artifact["claim_ceiling"] = "This candidate Typed Relation/v3 successor adds only the closed representation of the already reviewed materializes-consequence axis. It creates no new semantic relation, instance, authority, admission, inference, runtime, or external effect."
    typed_schema["$id"] = "https://cyberalchemy.local/schemas/typed-relation/v3"
    typed_schema["properties"]["schema_version"] = {"const": "cyberalchemy-lab-typed-relation/v3"}
    relation_enum = typed_schema["properties"]["payload"]["properties"]["relation_kind_ref"]["enum"]
    if "relation.materializes-consequence" not in relation_enum:
        relation_enum.append("relation.materializes-consequence")
        relation_enum.sort()
    materializes_condition = {
        "if": {"properties": {"payload": {"properties": {"relation_kind_ref": {"const": "relation.materializes-consequence"}}}}},
        "then": {"properties": {"payload": {
            "oneOf": [
                {"properties": {"source": {"properties": {"kind": {"const": "admission-transaction"}}}, "target": {"properties": {"kind": {"const": target}}}}}
                for target in ["generated-output", "project-governance-event-history", "project-semantic-event-history", "project-state"]
            ],
            "properties": {"qualifiers": {
                "type": "object", "additionalProperties": False,
                "properties": {key: s() for key in ["application_receipt_ref", "consequence_role", "output_digest"]},
                "required": ["application_receipt_ref", "consequence_role", "output_digest"],
            }},
        }}},
    }
    typed_schema["allOf"].append(materializes_condition)
    typed_schema["allOf"].sort(key=lambda item: item["if"]["properties"]["payload"]["properties"]["relation_kind_ref"]["const"])
    dump(typed_package / "schema.json", typed_schema)
    typed_artifact["schema_digest"] = sha(typed_package / "schema.json")
    dump(typed_package / "artifact.json", typed_artifact)
    typed_witness = {
        "schema_version": "cyberalchemy-lab-typed-relation/v3",
        "node_id": "typed-relation:admission-transaction-materializes-project-state-example",
        "kind": "typed-relation", "name": "Admission Transaction materializes Project State example",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:relation-owner",
        "scope_ref": "scope:governance-transaction-representation-closure", "evidence_refs": ["evidence:approval-admission-boundary-audit"],
        "challenge_route": "route:relation-governance-challenge", "successor_refs": [], "relation_refs": [],
        "payload": {
            "relation_kind_ref": "relation.materializes-consequence",
            "source": {"kind": "admission-transaction", "ref": "admission-transaction:example", "version_ref": "admission-transaction:example@applied"},
            "target": {"kind": "project-state", "ref": "project-state:example", "version_ref": "project-state:example@decision-0074"},
            "qualifiers": {"application_receipt_ref": "receipt:example", "consequence_role": "current-project-state", "output_digest": "sha256:" + ZERO},
            "relation_lifecycle_state": "candidate", "relation_evidence_refs": ["evidence:approval-admission-boundary-audit"],
        },
        "claim_ceiling": "Candidate schema witness only; it creates no relation, admission, authority, inference, runtime, or external effect.",
    }
    dump(typed_package / "fixtures/valid/record.json", typed_witness)
    invalid = copy.deepcopy(typed_witness); invalid["payload"]["qualifiers"].pop("output_digest"); dump(typed_package / "fixtures/invalid/missing-qualifier.json", invalid)
    invalid = copy.deepcopy(typed_witness); invalid["payload"]["qualifiers"]["implicit_authority"] = "forbidden"; dump(typed_package / "fixtures/invalid/extra-qualifier.json", invalid)
    invalid = copy.deepcopy(typed_witness); invalid["payload"]["target"]["kind"] = "decision"; dump(typed_package / "fixtures/invalid/undeclared-pair.json", invalid)
    invalid = copy.deepcopy(typed_witness); invalid["authority_effect"] = "admit"; dump(typed_package / "fixtures/invalid/authority.json", invalid)
    (typed_package / "ARTIFACT.md").write_text(generator.render_artifact(typed_artifact), encoding="utf-8")
    (typed_package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(typed_artifact, typed_witness), encoding="utf-8")
    (typed_package / "validate.py").write_text(
        "#!/usr/bin/env python3\nfrom pathlib import Path\nimport hashlib,json,jsonschema,sys\nR=Path(__file__).resolve().parent\nL=lambda p:json.loads(p.read_text())\nS=L(R/'schema.json');A=L(R/'artifact.json');V=jsonschema.Draft202012Validator(S)\nchecks=[]\ndef add(i,p,d):checks.append({'check_id':i,'result':'PASS' if p else 'BLOCK','detail':d})\nw=L(R/'fixtures/valid/record.json');errs=[e.message for e in V.iter_errors(w)];add('positive-witness',not errs,errs)\nneg=[]\nfor rel in A['validation_contract']['negative_witnesses']:\n e=[x.message for x in V.iter_errors(L(R/rel))];neg.append({'path':rel,'rejected':bool(e),'errors':e})\nadd('hostile-rejections',len(neg)==4 and all(x['rejected'] for x in neg),neg)\nrels=S['properties']['payload']['properties']['relation_kind_ref']['enum'];add('41-relation-conditions',len(rels)==41 and len(S['allOf'])==41 and 'relation.materializes-consequence' in rels,{'enum':len(rels),'conditions':len(S['allOf'])})\nadd('schema-current',A['schema_digest']==hashlib.sha256((R/'schema.json').read_bytes()).hexdigest(),A['schema_digest'])\nresult='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';out={'schema_version':'cyberalchemy-lab-typed-relation-v3-validation/v1','subject':A['artifact_type_ref'],'result':result,'authority_effect':'none','checks':checks};(R/'receipts').mkdir(exist_ok=True);(R/'receipts/validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\\n');print(json.dumps({'subject':A['artifact_type_ref'],'result':result,'checks':len(checks)},sort_keys=True));sys.exit(0 if result=='PASS' else 1)\n",
        encoding="utf-8",
    )
    impacted_manifest.append({
        "artifact_type_ref": typed_artifact["artifact_type_ref"], "kind": "typed-relation",
        "predecessor_artifact_path": str((typed_source / "artifact.json").relative_to(LAB)), "predecessor_artifact_sha256": sha(typed_source / "artifact.json"),
        "artifact_path": str((typed_package / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(typed_package / "artifact.json"),
        "schema_path": str((typed_package / "schema.json").relative_to(LAB)), "schema_sha256": sha(typed_package / "schema.json"),
        "fixture_path": str((typed_package / "fixtures/valid/record.json").relative_to(LAB)), "fixture_sha256": sha(typed_package / "fixtures/valid/record.json"),
    })
    dump(ROOT / "impacted-carrier-successors.json", {
        "schema_version": "cyberalchemy-lab-governance-transaction-impacted-carrier-successors/v1", "status": "candidate-awaiting-owner-review", "authority_effect": "none",
        "count": len(impacted_manifest), "entries": impacted_manifest,
        "claim_ceiling": "Seven endpoint-role successors and one Typed Relation representation-closure successor cover the exact governance transaction extension. Their admitted predecessors remain byte-immutable.",
    })

    target_entries = []
    for item in [*manifest, *impacted_manifest]:
        target_entries.append({
            "artifact_type_ref": item["artifact_type_ref"],
            "artifact_path": item["artifact_path"],
            "artifact_sha256": item["artifact_sha256"],
            "schema_path": item["schema_path"],
            "schema_sha256": item["schema_sha256"],
        })
    target_set = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-target-set/v1",
        "target_set_id": "artifact-type-set:governance-transaction-fourteen",
        "status": "candidate-exact-target-set",
        "authority_effect": "none",
        "count": len(target_entries),
        "entries": sorted(target_entries, key=lambda item: item["artifact_type_ref"]),
        "claim_ceiling": "This exact target set identifies fourteen candidate Artifact Type packages and admits none of them.",
    }
    dump(ROOT / "admission-target-set.json", target_set)
    artifact_target_digest = sha(ROOT / "admission-target-set.json")
    relation_target_path = LAB / "authority/relation-kinds/candidates/0007-governance-transaction-extension/relation-kind-successor-manifest.json"
    relation_target_digest = sha(relation_target_path)
    definition_target_digest = sha(TRANSACTION_DEF)

    bundle_package = LAB / "authority/artifact-types/decision-bundle/v1"
    bundle = load(bundle_package / "fixtures/valid/record.json")
    decision_target_digests = [artifact_target_digest, definition_target_digest, relation_target_digest]
    for decision, target_digest in zip(bundle["payload"]["ordered_decisions"], decision_target_digests):
        if decision["effect_kind"] == "artifact-type-admission":
            decision["target_refs"] = ["artifact-type-set:governance-transaction-fourteen"]
            decision["target_digests"][0]["target_ref"] = "artifact-type-set:governance-transaction-fourteen"
        decision["target_digests"][0]["sha256"] = target_digest
        core = {key: value for key, value in decision.items() if key not in {"decision_core_sha256", "selected_outcome"}}
        decision["decision_core_sha256"] = digest_object(core)
        decision["selected_outcome"] = None
    bundle_core = {key: value for key, value in bundle["payload"].items() if key != "bundle_digest"}
    bundle["payload"]["bundle_digest"] = digest_object(bundle_core)
    dump(bundle_package / "fixtures/valid/record.json", bundle)
    invalid = copy.deepcopy(bundle); invalid["authority_effect"] = "admit"; dump(bundle_package / "fixtures/invalid/authority.json", invalid)
    invalid = copy.deepcopy(bundle); invalid["implicit_authority"] = True; dump(bundle_package / "fixtures/invalid/extra-field.json", invalid)
    invalid = copy.deepcopy(bundle); invalid["payload"].pop(next(iter(bundle["payload"]))); dump(bundle_package / "fixtures/invalid/missing-payload-field.json", invalid)
    invalid = copy.deepcopy(bundle); invalid["relation_refs"][0]["relation_kind_ref"] = "relation.not-declared"; dump(bundle_package / "fixtures/invalid/undeclared-relation.json", invalid)
    invalid = copy.deepcopy(bundle); invalid["kind"] = NEIGHBORS["decision-bundle"][0]; dump(bundle_package / "fixtures/invalid/collapsed-neighbor.json", invalid)
    bundle_artifact = load(bundle_package / "artifact.json")
    (bundle_package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(bundle_artifact, bundle), encoding="utf-8")

    transition = load(PENDING_TRANSITION)
    transition_outputs = {item["semantic_kind"]: item["sha256"] for item in transition["artifact_instances"]}
    transaction_package = LAB / "authority/artifact-types/admission-transaction/v1"
    transaction = load(transaction_package / "fixtures/valid/record.json")
    transaction["payload"]["admission_targets"][0]["target_ref"] = "artifact-type-set:governance-transaction-fourteen"
    transaction["payload"]["decision_core_refs"] = [
        {"decision_ref": item["decision_ref"], "decision_core_sha256": item["decision_core_sha256"], "selected_outcome": None}
        for item in bundle["payload"]["ordered_decisions"]
    ]
    transaction["payload"]["review_bundle_digest"] = bundle["payload"]["bundle_digest"]
    transaction["payload"]["resolved_bundle_digest"] = None
    transaction["payload"]["authorization_evidence_ref"] = None
    transaction["payload"]["authorization_evidence_sha256"] = None
    transaction["payload"]["input_state_ref"] = transition["predecessor_state_ref"]
    transaction["payload"]["input_state_sha256"] = transition["inputs"]["predecessor_project_state"]["sha256"]
    for target, target_digest in zip(transaction["payload"]["admission_targets"], decision_target_digests):
        target["target_sha256"] = target_digest
    for consequence in transaction["payload"]["deterministic_consequences"]:
        if consequence["consequence_kind"] in transition_outputs:
            consequence["output_sha256"] = transition_outputs[consequence["consequence_kind"]]
        else:
            consequence["output_sha256"] = None
    transaction["payload"]["application_receipt_ref"] = None
    dump(transaction_package / "fixtures/valid/record.json", transaction)
    invalid = copy.deepcopy(transaction); invalid["authority_effect"] = "admit"; dump(transaction_package / "fixtures/invalid/authority.json", invalid)
    invalid = copy.deepcopy(transaction); invalid["implicit_authority"] = True; dump(transaction_package / "fixtures/invalid/extra-field.json", invalid)
    invalid = copy.deepcopy(transaction); invalid["payload"].pop(next(iter(transaction["payload"]))); dump(transaction_package / "fixtures/invalid/missing-payload-field.json", invalid)
    invalid = copy.deepcopy(transaction); invalid["relation_refs"][0]["relation_kind_ref"] = "relation.not-declared"; dump(transaction_package / "fixtures/invalid/undeclared-relation.json", invalid)
    invalid = copy.deepcopy(transaction); invalid["kind"] = NEIGHBORS["admission-transaction"][0]; dump(transaction_package / "fixtures/invalid/collapsed-neighbor.json", invalid)
    transaction_artifact = load(transaction_package / "artifact.json")
    (transaction_package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(transaction_artifact, transaction), encoding="utf-8")
    for item in manifest:
        if item["artifact_type_ref"] == "cal.artifact-type.decision-bundle/v1":
            item["fixture_sha256"] = sha(bundle_package / "fixtures/valid/record.json")
        if item["artifact_type_ref"] == "cal.artifact-type.admission-transaction/v1":
            item["fixture_sha256"] = sha(transaction_package / "fixtures/valid/record.json")

    package_manifest = {
        "schema_version": "cyberalchemy-lab-governance-transaction-carrier-package/v1", "status": "candidate-awaiting-owner-review", "authority_effect": "none", "count": len(manifest), "entries": manifest,
        "relation_model": {"path": str(MODEL.relative_to(LAB)), "sha256": sha(MODEL)},
        "admission_transaction_definition": {"path": str(TRANSACTION_DEF.relative_to(LAB)), "sha256": sha(TRANSACTION_DEF)},
        "source_audit": {"path": str(AUDIT.relative_to(LAB)), "sha256": sha(AUDIT)},
        "impacted_carrier_successors": {"path": str((ROOT / "impacted-carrier-successors.json").relative_to(LAB)), "sha256": sha(ROOT / "impacted-carrier-successors.json"), "count": len(impacted_manifest)},
        "admission_target_set": {"path": str((ROOT / "admission-target-set.json").relative_to(LAB)), "sha256": artifact_target_digest, "count": len(target_entries)},
        "claim_ceiling": "This package materializes six candidate carrier contracts and one integrated example. It admits no Definition, Artifact Type, Relation Kind, instance, Typed Relation, or transaction.",
    }
    correction = {
        "schema_version": "cyberalchemy-lab-admission-target-representation-closure-repair/v1",
        "kind": "required-endpoint-schema-closure",
        "reviewed_target_set_id": "artifact-type-set:governance-transaction-thirteen",
        "reviewed_target_set_sha256": "9324030cacd0e1078129f8cbd3181a9af4b4046032bbd1d54413c97869c7f613",
        "admission_target_set_id": target_set["target_set_id"],
        "admission_target_set_sha256": artifact_target_digest,
        "added_target_ref": typed_artifact["artifact_type_ref"],
        "repair_reason": "The already reviewed materializes-consequence Relation Kind requires a closed Typed Relation carrier condition before instances can be validly represented.",
        "semantic_scope_changed": False,
        "new_relation_kinds": 0,
        "new_runtime_effects": 0,
        "new_external_effects": 0,
    }
    dump(ROOT / "representation-closure-repair.json", correction)
    package_manifest["representation_closure_repair"] = {"path": str((ROOT / "representation-closure-repair.json").relative_to(LAB)), "sha256": sha(ROOT / "representation-closure-repair.json")}
    dump(ROOT / "carrier-manifest.json", package_manifest)
    integrated = {
        "schema_version": "cyberalchemy-lab-single-checkpoint-admission-example/v1", "status": "candidate-example", "authority_effect": "none",
        "workflow_profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint", "preference_ref": "user-decision-preference:lab-owner-final-review",
        "checkpoint_ref": "decision-checkpoint:governance-transaction-review-001", "bundle_ref": "decision-bundle:governance-transaction-surface-001",
        "review_bundle_digest": bundle["payload"]["bundle_digest"], "admission_target_set_sha256": artifact_target_digest,
        "decision_count": 3, "human_response_count": 1, "transaction_ref": "admission-transaction:governance-transaction-surface-001",
        "deterministic_successor_ref": "project-state-transition:decision-0073-successor", "new_checkpoint_for_successor": False,
        "runtime_activations": 0, "external_effect_refs": [],
        "flow": ["prepare exact targets and digests", "present one closed Decision Bundle at one final-review checkpoint", "record each Decision.selected_outcome from one owner response", "apply one all-or-nothing Admission Transaction", "append events, refresh derived surfaces, bind receipt, and advance Project State inside the transaction"],
        "claim_ceiling": "This example demonstrates the revised interaction and application boundary. It is not an approval, admission, or applied transaction.",
    }
    dump(ROOT / "integrated-example.json", integrated)
    lines = ["<!-- GENERATED FILE: canonical data is carrier-manifest.json and integrated-example.json. -->", "", "# Governance transaction surface review", "", "- New candidate Artifact Types: `6`", "- Required endpoint-role successors: `7`", "- Required Typed Relation representation successor: `1`", "- New candidate Definition: `Admission Transaction`", "- Relation surface: `41` kinds", "- Relation Kind successors: `3`", "- New Relation Kind: `1`", "- Human checkpoints in the example: `1`", "- Independent Decisions in the bundle: `3`", "- Admission Transactions: `1`", "- Runtime activations: `0`", "- Authority effect: `none`", "", "## Candidate carriers", "", "| Artifact Type | Definition posture | Relation roles | Fixture |", "| --- | --- | ---: | --- |"]
    for item in manifest:
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['definition_posture']}` | {item['relation_role_count']} | `{item['fixture_path']}` |")
    lines += ["", "## Required endpoint carrier successors", "", "| Successor | Preserved predecessor |", "| --- | --- |"]
    for item in impacted_manifest:
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['predecessor_artifact_path']}` |")
    lines += ["", "## Admission preflight closure repair", "", f"- Reviewed thirteen-carrier target set digest: `{correction['reviewed_target_set_sha256']}`", f"- Corrected fourteen-carrier target set digest: `{integrated['admission_target_set_sha256']}`", "- Added carrier: `cal.artifact-type.typed-relation/v3`", "- Semantic scope changed: `false`", "", "## Exact review bindings", "", f"- Review bundle digest: `{integrated['review_bundle_digest']}`", f"- Fourteen-carrier target set digest: `{integrated['admission_target_set_sha256']}`", "- Selected outcomes: `null` until the owner decides", "- Authorization evidence and application receipt: `null` while the transaction is planned", ""]
    lines += ["## Revised operational flow", ""] + [f"{index}. {step}" for index, step in enumerate(integrated["flow"], 1)]
    lines += ["", "## Boundary conclusions", "", "- Approval or rejection is the `selected_outcome` of each Decision; there is no Approval artifact type.", "- A Decision is a member of a Decision Bundle. The bundle's checkpoint and the profile's allowed checkpoint remain closed contract references.", "- One owner response may resolve all exact Decision members while preserving their identities, owners, scopes, effects, targets, and digests.", "- The Admission Transaction applies the resolved bundle atomically and creates the declared state, event, receipt, registry, index, and projection consequences.", "- The already materialized Decision 0073 Project State successor is a deterministic consequence and does not receive a separate Decision.", "- A new checkpoint is required when a target or digest changes materially, authority changes, a new effect appears, or a challenge invalidates the bundle.", "", "## Claim ceiling", "", package_manifest["claim_ceiling"], ""]
    (ROOT / "REVIEW.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
