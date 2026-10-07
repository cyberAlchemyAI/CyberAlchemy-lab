#!/usr/bin/env python3
"""Materialize the 22 distinct endpoint carrier candidates required by Step 5."""

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
PLAN = ROOT / "plan.json"
DEFINITIONS = LAB / "authority/definitions/registry.json"
RELATION_MODEL = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
ROOT_TYPE = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
GENERATOR = LAB / "tooling/generators/endpoint_carrier.py"
VALIDATOR = LAB / "tooling/validators/endpoint_carrier.py"


PAYLOADS: dict[str, dict[str, Any]] = {
    "authority-claim": {"claimant_ref": "role:artifact-type-owner", "authority_basis_refs": ["decision:0068"], "decision_scope_ref": "decision-scope:artifact-type-registry", "claimed_permissions": ["admit-exact-reviewed-artifact-type"], "limitations": ["no consumer activation"]},
    "constitution": {"governed_scope_ref": "scope:lab-semantic-governance", "rule_refs": ["rule:typed-coupling"], "invariant_refs": ["invariant:no-implicit-authority"], "amendment_policy_ref": "policy:constitution-amendment"},
    "contract": {"party_refs": ["role:artifact-type-owner"], "subject_refs": ["artifact-type:registry/v2"], "obligation_refs": ["obligation:preserve-exact-bytes"], "permission_refs": ["permission:validate-candidate"], "prohibition_refs": ["prohibition:implicit-admission"], "breach_route": "route:contract-challenge"},
    "decision": {"decision_maker_ref": "person-reference:owner", "subject_refs": ["artifact-type:registry/v2"], "selected_outcome": "admit exact reviewed bytes", "evidence_basis_refs": ["receipt:registry-v2-validation"], "declared_effect_refs": ["effect:registry-v2-admitted-current"]},
    "decision-scope": {"subject_kind_refs": ["artifact-type"], "subject_refs": ["artifact-type:registry/v2"], "permitted_effects": ["admit"], "excluded_effects": ["activate-consumer", "admit-instance"]},
    "effect": {"effect_kind": "lifecycle-transition", "subject_ref": "artifact-type:registry/v2", "intended_state": "admitted-current", "effective_when": "decision postimage is valid", "verification_refs": ["registry:snapshot-0002"]},
    "evaluation": {"profile_ref": "evaluation-profile:artifact-type-candidate", "subject_ref": "artifact-type:implementation/v1", "input_state_ref": "digest:candidate-postimage", "outcomes": [{"check_id": "schema-conformance", "result": "PASS", "evidence_refs": ["receipt:implementation-v1"], "blocker_ref": "none"}]},
    "evidence-set": {"source_refs": ["source:validator-run"], "item_refs": ["receipt:carrier-validation"], "coverage_statement": "Exact candidate schema and hostile cases", "limitations": ["No runtime behavior evaluated"]},
    "generated-output": {"generator_ref": "generator:endpoint-carrier/v1", "input_refs": ["artifact:implementation/v1"], "output_digest": "sha256:0123456789abcdef", "reproducibility_receipt_ref": "receipt:projection-parity"},
    "governed-model": {"model_kind": "artifact-type-registry", "contract_ref": "contract:registry-v2", "version_ref": "model:registry@2", "rule_refs": ["rule:exact-overlay-resolution"], "extension_policy_ref": "policy:typed-extension"},
    "hypothesis": {"proposition": "Registry generation is deterministic for identical inputs", "falsification_conditions": ["Two builds from identical bytes produce different digests"], "observation_targets": ["measurement-result:registry-digest"], "disposition": "open"},
    "implementation": {"implementation_kind": "validator", "conforms_to_schema_refs": ["schema:artifact-type-registry/v2"], "realizes_capability_refs": ["product-capability:effective-state-resolution"], "execution_entrypoint_ref": "python:validate.py", "environment_contract_ref": "contract:python-runtime"},
    "ontology-node": {"ontology_ref": "ontology:lab-integrated-model", "node_type_ref": "definition", "label": "Implementation", "proposition": "Implementation is an executable realization", "provenance_refs": ["definition:implementation"], "confidence": "admitted-definition"},
    "person": {"stable_identity_ref": "person:local-owner", "display_name": "Repository owner", "identity_evidence_refs": ["identity-claim:local-owner"], "identity_boundary": "Human identity remains separate from references, roles, sessions, and Agents", "privacy_classification": "restricted"},
    "policy": {"issuer_ref": "role:governance-owner", "governed_scope_ref": "scope:artifact-type-admission", "rule_refs": ["rule:exact-byte-admission"], "exception_route": "route:policy-exception", "effective_period": "until superseded"},
    "relation-kind": {"axis_id": "axis.membership", "predicate": "member-of", "inverse_ref": "none", "qualifier_schema_ref": "schema:membership-qualifiers/v1", "allowed_endpoint_pairs": [{"source_kind": "work", "target_kind": "project"}]},
    "responsibility": {"responsibility_statement": "Review and admit exact Artifact Type postimages", "scope_ref": "scope:artifact-type-governance", "accountable_role_refs": ["role:artifact-type-owner"], "completion_evidence_refs": ["decision:artifact-type-admission"]},
    "review": {"subject_ref": "artifact-type:implementation/v1", "review_profile_ref": "review-profile:artifact-type", "reviewer_refs": ["person-reference:owner"], "finding_refs": ["finding:no-collapse-pass"], "disposition": "ready-for-decision"},
    "schema": {"schema_ref": "schema:implementation/v1", "dialect": "https://json-schema.org/draft/2020-12/schema", "subject_kind_ref": "implementation", "content_digest": "sha256:fedcba9876543210", "conformance_profile_ref": "evaluation-profile:json-schema"},
    "source": {"source_kind": "repository-file", "locator": "authority/definitions/registry.json", "content_digest": "sha256:750b19ddb675c44f1", "captured_at": "2026-10-06T00:00:00-03:00", "provenance_refs": ["repository:CyberAlchemy-lab"]},
    "typed-relation": {"relation_kind_ref": "relation.realizes", "source_ref": "implementation:registry-validator", "target_ref": "product-capability:effective-state-resolution", "qualifiers": [{"axis": "realization-role", "value": "validator"}], "relation_lifecycle_state": "candidate", "relation_evidence_refs": ["receipt:validator-pass"]},
    "work": {"project_ref": "project:lab-semantic-governance", "goal_refs": ["goal:complete-integrated-lab-model"], "work_statement": "Materialize missing endpoint carriers", "input_refs": ["plan:step5-carrier-closure"], "output_refs": ["artifact-type:implementation/v1"], "completion_state": "candidate-complete"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema_for(value: Any) -> dict:
    if isinstance(value, str):
        return {"type": "string", "minLength": 1}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, list):
        item_schema = schema_for(value[0]) if value else {"type": "string", "minLength": 1}
        result = {"type": "array", "items": item_schema, "minItems": 1}
        if value and all(isinstance(item, (str, int, bool)) for item in value):
            result["uniqueItems"] = True
        return result
    if isinstance(value, dict):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {key: schema_for(item) for key, item in value.items()},
            "required": list(value),
        }
    raise TypeError(type(value))


def relation_roles(kind: str, model: dict) -> list[dict]:
    roles = []
    for relation in model["entries"]:
        outgoing = sorted({pair["target_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        incoming = sorted({pair["source_kind"] for pair in relation["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        if outgoing:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "source", "counterpart_kinds": outgoing})
        if incoming:
            roles.append({"relation_kind_ref": relation["relation_kind_id"], "direction": "target", "counterpart_kinds": incoming})
    return sorted(roles, key=lambda item: (item["relation_kind_ref"], item["direction"]))


def instance_schema(kind: str, roles: list[dict], payload: dict) -> dict:
    relation_kinds = sorted({role["relation_kind_ref"] for role in roles})
    directions = sorted({role["direction"] for role in roles})
    counterparts = sorted({item for role in roles for item in role["counterpart_kinds"]})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://cyberalchemy.local/schemas/{kind}/v1",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": f"cyberalchemy-lab-{kind}/v1"},
            "node_id": {"type": "string", "minLength": 1},
            "kind": {"const": kind},
            "name": {"type": "string", "minLength": 1},
            "lifecycle_state": {"enum": ["candidate", "active", "historical", "retired"]},
            "authority_effect": {"const": "none"},
            "owner_ref": {"type": "string", "minLength": 1},
            "scope_ref": {"type": "string", "minLength": 1},
            "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
            "challenge_route": {"type": "string", "minLength": 1},
            "successor_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
            "relation_refs": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "relation_kind_ref": {"enum": relation_kinds},
                        "direction": {"enum": directions},
                        "counterpart_kind": {"enum": counterparts},
                        "counterpart_ref": {"type": "string", "minLength": 1},
                    },
                    "required": ["relation_kind_ref", "direction", "counterpart_kind", "counterpart_ref"],
                },
            },
            "payload": schema_for(payload),
            "claim_ceiling": {"type": "string", "minLength": 1},
        },
        "required": ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect", "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs", "relation_refs", "payload", "claim_ceiling"],
    }


def write_wrappers(package: Path) -> None:
    (package / "generator.py").write_text(
        "#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util, json\nROOT=Path(__file__).resolve().parent\nSHARED=ROOT.parents[3]/'tooling/generators/endpoint_carrier.py'\nspec=importlib.util.spec_from_file_location('endpoint_carrier_generator',SHARED); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)\nif __name__=='__main__':\n a=json.loads((ROOT/'artifact.json').read_text()); w=ROOT/a['validation_contract']['positive_witness']; d=json.loads(w.read_text()); (ROOT/'ARTIFACT.md').write_text(mod.render_artifact(a)); (ROOT/a['validation_contract']['positive_projection']).write_text(mod.render_instance(a,d))\n",
        encoding="utf-8",
    )
    (package / "validate.py").write_text(
        "#!/usr/bin/env python3\nfrom pathlib import Path\nimport importlib.util\nROOT=Path(__file__).resolve().parent\nSHARED=ROOT.parents[3]/'tooling/validators/endpoint_carrier.py'\nspec=importlib.util.spec_from_file_location('endpoint_carrier_validator',SHARED); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)\nif __name__=='__main__': raise SystemExit(mod.validate_package(ROOT))\n",
        encoding="utf-8",
    )


def main() -> None:
    plan = load(PLAN)
    definitions = load(DEFINITIONS)
    model = load(RELATION_MODEL)
    spec = importlib.util.spec_from_file_location("endpoint_carrier_generator", GENERATOR)
    generator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(generator)
    results = []
    for planned in plan["new_endpoint_carriers"]:
        kind = planned["endpoint_kind"]
        package = LAB / f"authority/artifact-types/{kind}/v1"
        if package.exists():
            shutil.rmtree(package)
        package.mkdir(parents=True)
        roles = relation_roles(kind, model)
        payload = PAYLOADS[kind]
        schema = instance_schema(kind, roles, payload)
        dump(package / "schema.json", schema)
        binding = planned["semantic_definition_binding"]
        definition = load(LAB / binding["path"])
        explanation = definition["voices"]["plain_language"]["explanation"]
        term = definition["term"]
        allowed = sorted({role["relation_kind_ref"] for role in roles})
        artifact = {
            "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2",
            "artifact_type_id": f"cal.artifact-type.{kind}",
            "artifact_type_ref": f"cal.artifact-type.{kind}/v1",
            "version": "1.0.0-candidate.1",
            "name": term,
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "classification": {"artifact_type_ref": "cal.artifact-type.artifact-type/v2", "semantic_kind": kind, "authority_kind": "none", "lifecycle_posture_ref": "candidate:step5-carrier-closure/v1"},
            "artifact_type_root_binding": {"path": "authority/artifact-types/artifact-type/v2/artifact.json", "sha256": sha(ROOT_TYPE), "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"},
            "semantic_owner_ref": "role:artifact-type-owner",
            "semantic_definition_refs": [binding["definition_ref"]],
            "semantic_definition_bindings": [{**binding, "admission_posture": "admitted", "admission_decision_ref": next(item["admission_decision_ref"] for item in definitions["entries"] if f"{item['definition_id']}@{item['version']}" == binding["definition_ref"])}],
            "schema_ref": f"cal.schema.{kind}/v1",
            "schema_digest": sha(package / "schema.json"),
            "instance_contract": {"canonical_filename": "record.json", "human_filename": "RECORD.md", "identity_field": "node_id", "instance_discriminator": {"path": "/schema_version", "value": f"cyberalchemy-lab-{kind}/v1"}, "closed_representation": True, "required_semantic_fields": schema["required"], "forbidden_canonical_fields": ["implicit_admission", "implicit_relation", "derived_authority", "runtime_activation"]},
            "distinct_validation_purpose": explanation,
            "allowed_relation_kinds": allowed,
            "relation_roles": roles,
            "hostile_non_collapse": planned["must_remain_distinct_from"],
            "orthogonality_rules": [
                {"rule_id": f"{kind.upper()}-IDENTITY", "statement": f"A {term} instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier."},
                {"rule_id": f"{kind.upper()}-RELATIONS", "statement": "Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact."},
                {"rule_id": f"{kind.upper()}-AUTHORITY", "statement": "Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect."},
                {"rule_id": f"{kind.upper()}-NON-COLLAPSE", "statement": f"{term} remains distinct from {', '.join(planned['must_remain_distinct_from'])}."},
            ],
            "source_direction": {"canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only", "shared_generator_path": "tooling/generators/endpoint_carrier.py", "shared_generator_sha256": sha(GENERATOR)},
            "four_facets": {"classification": f"Candidate {term} carrier under Artifact Type/v2.", "schema": "schema.json is a closed kind-specific instance contract.", "human_continuation": "ARTIFACT.md and the fixture RECORD.md are deterministic generated projections.", "machine_checkable": "Definition binding, schema closure, relation roles, hostile non-collapse, fixtures, and projection parity are executable."},
            "validation_contract": {"validator_path": f"authority/artifact-types/{kind}/v1/validate.py", "shared_validator_path": "tooling/validators/endpoint_carrier.py", "shared_validator_sha256": sha(VALIDATOR), "positive_witness": "fixtures/valid/record.json", "positive_projection": "fixtures/valid/RECORD.md", "negative_witnesses": ["fixtures/invalid/authority.json", "fixtures/invalid/extra-field.json", "fixtures/invalid/missing-payload-field.json", "fixtures/invalid/undeclared-relation.json", "fixtures/invalid/collapsed-neighbor.json"], "assessment_scope": "candidate-schema-definition-relation-surface-and-projection", "admission_effect": "none", "required_checks": ["modern carrier contract", "Artifact Type/v2 root", "current admitted Definition", "closed kind-specific schema", "exact relation roles", "five hostile rejections", "neighbor non-collapse", "deterministic projections"]},
            "typed_residue": [
                {"residue_id": f"{kind.upper()}-R1", "missing": f"Artifact Type owner admission for this exact {term}/v1 candidate.", "owner_ref": "role:artifact-type-owner", "consequence": "The carrier remains candidate-only."},
                {"residue_id": f"{kind.upper()}-R2", "missing": "A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision.", "owner_ref": "role:migration-consumer-owner", "consequence": "No relation, instance, consumer, or runtime becomes active."},
            ],
            "claim_ceiling": f"This is a candidate {term}/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.",
        }
        dump(package / "artifact.json", artifact)
        first_role = roles[0]
        first_counterpart = first_role["counterpart_kinds"][0]
        witness = {
            "schema_version": f"cyberalchemy-lab-{kind}/v1",
            "node_id": f"{kind}:example-001",
            "kind": kind,
            "name": f"Example {term}",
            "lifecycle_state": "candidate",
            "authority_effect": "none",
            "owner_ref": "role:artifact-type-owner",
            "scope_ref": "scope:lab-integrated-model",
            "evidence_refs": [f"evidence:{kind}-example"],
            "challenge_route": "route:artifact-type-challenge",
            "successor_refs": [],
            "relation_refs": [{"relation_kind_ref": first_role["relation_kind_ref"], "direction": first_role["direction"], "counterpart_kind": first_counterpart, "counterpart_ref": f"{first_counterpart}:example-001"}],
            "payload": payload,
            "claim_ceiling": f"Example {term} fixture for schema and relation-role validation only.",
        }
        dump(package / "fixtures/valid/record.json", witness)
        authority = copy.deepcopy(witness); authority["authority_effect"] = "admit"; dump(package / "fixtures/invalid/authority.json", authority)
        extra = copy.deepcopy(witness); extra["implicit_authority"] = True; dump(package / "fixtures/invalid/extra-field.json", extra)
        missing = copy.deepcopy(witness); missing["payload"].pop(next(iter(payload))); dump(package / "fixtures/invalid/missing-payload-field.json", missing)
        undeclared = copy.deepcopy(witness); undeclared["relation_refs"][0]["relation_kind_ref"] = "relation.not-declared"; dump(package / "fixtures/invalid/undeclared-relation.json", undeclared)
        collapsed = copy.deepcopy(witness); collapsed["kind"] = planned["must_remain_distinct_from"][0]; dump(package / "fixtures/invalid/collapsed-neighbor.json", collapsed)
        write_wrappers(package)
        (package / "ARTIFACT.md").write_text(generator.render_artifact(artifact), encoding="utf-8")
        (package / "fixtures/valid/RECORD.md").write_text(generator.render_instance(artifact, witness), encoding="utf-8")
        results.append({"artifact_type_ref": artifact["artifact_type_ref"], "kind": kind, "artifact_path": str((package / "artifact.json").relative_to(LAB)), "artifact_sha256": sha(package / "artifact.json"), "schema_path": str((package / "schema.json").relative_to(LAB)), "schema_sha256": sha(package / "schema.json"), "definition_ref": binding["definition_ref"], "relation_role_count": len(roles), "hostile_case_count": 5})
    dump(ROOT / "endpoint-carrier-postimages.json", {"schema_version": "cyberalchemy-lab-step5-endpoint-carrier-postimages/v1", "status": "candidate-materialized", "authority_effect": "none", "count": len(results), "entries": results, "claim_ceiling": "This manifest binds 22 candidate carrier postimages. It does not admit a type, instance, relation, consumer, or runtime."})


if __name__ == "__main__":
    main()
