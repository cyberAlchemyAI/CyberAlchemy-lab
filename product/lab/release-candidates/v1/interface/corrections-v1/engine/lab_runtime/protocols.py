"""Candidate runtime interface schemas, independent of canonical Artifact Types."""
from .operations import CATEGORIES, OPERATIONS, PROPOSAL_SCHEMA

STRING = {"type": "string", "minLength": 1}
SHA = {"type": "string", "pattern": "^[a-f0-9]{64}$"}


def closed(properties):
    return {"type": "object", "additionalProperties": False, "required": list(properties), "properties": properties}


APPROVAL_SCHEMA = closed({"schema_version": {"const": "lab-runtime-approval/v1"},
    **{k: STRING for k in ["store_id", "owner_ref", "scope_ref", "policy_ref", "challenge_route", "expected_head"]},
    "source_snapshot_digest": SHA, "proposal_digest": SHA, "decision_core_digests": {"type": "array", "minItems": 1, "items": SHA},
    "approved_at": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"},
    "outcome": {"const": "authorize-exact-local-effects"}, "signature": {"type": "string", "pattern": "^[a-f0-9]{128}$"}})

LEGACY_CONFIG_SCHEMA = closed({"schema_version": {"const": "lab-runtime-store-config/v1"},
    **{k: STRING for k in ["store_id", "owner_ref", "scope_ref", "policy_ref", "challenge_route"]},
    "source_snapshot_digest": SHA, "public_key": SHA,
    "allowed_categories": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"enum": CATEGORIES}},
    "allowed_effects": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"enum": OPERATIONS}},
    "authority_boundary": {"const": "operator-provisioned-local-store"}, "repository_admission_effect": {"const": "none"}})

COUPLED_CONFIG_SCHEMA = closed({**LEGACY_CONFIG_SCHEMA['properties'],
    'schema_version': {'const': 'lab-runtime-store-config/v2-candidate'},
    'endpoint_engine_id': {'const': 'lab-operator-signed-coupling/v1-candidate'},
    'endpoint_mapping_binding': closed({'path': STRING, 'sha256': SHA}),
    'endpoint_mapping_authority': {'const': 'isolated-candidate-local-interpretation'}})
CORRECTION_CONFIG_SCHEMA=closed({**COUPLED_CONFIG_SCHEMA['properties'],
    'schema_version':{'const':'lab-runtime-store-config/v3-candidate'},
    'correction_engine_id':{'const':'lab-operator-reference-correction/v1-candidate'},
    'correction_profile_binding':closed({'path':STRING,'sha256':SHA}),
    'authorized_domain_scope_refs':{'type':'array','minItems':1,'uniqueItems':True,'items':STRING}})
CONFIG_SCHEMA={'oneOf':[LEGACY_CONFIG_SCHEMA,COUPLED_CONFIG_SCHEMA,CORRECTION_CONFIG_SCHEMA]}
LEGACY_APPROVAL_SCHEMA=APPROVAL_SCHEMA
CORRECTION_APPROVAL_SCHEMA=closed({**LEGACY_APPROVAL_SCHEMA['properties'],
    'schema_version':{'const':'lab-runtime-approval/v2-candidate'},'configuration_digest':SHA,
    'correction_profile_binding':closed({'path':STRING,'sha256':SHA}),
    'authorized_domain_scope_refs':{'type':'array','minItems':1,'uniqueItems':True,'items':STRING}})
APPROVAL_SCHEMA={'oneOf':[LEGACY_APPROVAL_SCHEMA,CORRECTION_APPROVAL_SCHEMA]}

HEAD_SCHEMA = closed({"sequence": {"type": "integer", "minimum": 0, "maximum": 100000},
    "transaction_digest": SHA, "config_digest": SHA, "baseline_digest": SHA, "digest": SHA})

CONTRACT_BINDING_SCHEMA = closed({"semantic_kind": STRING, "schema_path": STRING, "schema_sha256": SHA,
    "schema_selector": {"type": ["string", "null"]}, "identity_field": STRING,
    "instance_discriminator": closed({"path": STRING, "value": STRING}),
    "allowed_relation_kinds": {"type": "array", "uniqueItems": True, "items": {"type": "string", "pattern": "^relation\\.[a-z0-9-]+$"}},
    "relation_roles": {"type": "array", "items": closed({"direction": {"enum": ["source", "target"]},
        "relation_kind_ref": STRING, "counterpart_kinds": {"type": "array", "minItems": 1, "items": STRING}})}})

TRANSACTION_COMMON = {"schema_version": {"const": "lab-runtime-transaction/v1"}, "sequence": {"type": "integer", "minimum": 0},
    "previous_digest": {"type": ["string", "null"]}, "config_digest": SHA, "baseline_digest": SHA,
    "projection_digest": SHA, "digest": SHA}
TRANSACTION_SCHEMA = {"oneOf": [closed({**TRANSACTION_COMMON, "kind": {"const": "genesis"}}),
    closed({**TRANSACTION_COMMON, "kind": {"const": "admission"}, "proposal": PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,
        "decision_cores": {"type": "array", "minItems": 1}, "consequences": {"type": "object"}})]}

SCHEMAS = {"proposal": PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA, "store-config": CONFIG_SCHEMA,
           "head": HEAD_SCHEMA, "contract-binding": CONTRACT_BINDING_SCHEMA, "transaction": TRANSACTION_SCHEMA}
