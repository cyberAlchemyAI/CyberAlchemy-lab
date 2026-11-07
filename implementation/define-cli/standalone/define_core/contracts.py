"""Closed executable formats for the standalone preparation kernel."""
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from .exact import Refusal, require, tree

TEXT = {"type": "string", "minLength": 1, "maxLength": 262144}
SHA = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
NONE = {"const": "none"}
REV = {"type": "integer", "minimum": 1, "maximum": 9007199254740991}


def obj(fields, optional=()):
    return {"type": "object", "additionalProperties": False, "properties": fields,
            "required": [k for k in fields if k not in optional]}


def array(items, maximum=256, minimum=0):
    return {"type": "array", "items": items, "maxItems": maximum, "minItems": minimum}


BINDING = obj({"path": TEXT, "sha256": SHA, "bytes": {"type": "integer", "minimum": 0, "maximum": 16777216},
               "digest_kind": {"const": "original-file-sha256"}})
GAP = obj({"gap_id": TEXT, "reason": TEXT, "affected_use": TEXT, "continuation": TEXT})
EXTERNAL = obj({"kind": {"const": "external"}, "input_id": TEXT, "identity": TEXT, "revision": TEXT,
                "carrier_ref": TEXT, "selector": {"type": "string"}, "sha256": SHA})
EMBEDDED = obj({"kind": {"const": "embedded"}, "pack_id": TEXT, "pack_revision": REV,
                "entry_kind": {"enum": ["working-meaning", "application", "assessment"]},
                "entry_id": TEXT, "revision": REV, "selector": TEXT, "sha256": SHA})
REFERENCE = {"oneOf": [EXTERNAL, EMBEDDED]}
LINEAGE = array(BINDING)
PARAMETER = obj({"name": TEXT, "value_schema": {"type": "object"}, "required": {"type": "boolean"},
                 "interpretation": TEXT})
MEANING = obj({"meaning_id": TEXT, "revision": REV, "statement": TEXT, "scope": TEXT,
               "boundaries": array(TEXT, minimum=1), "parameters": array(PARAMETER, 24),
               "ownership_posture": TEXT, "lineage": LINEAGE, "status": {"const": "local-proposed"}, "authority_effect": NONE})
CONCEPT = obj({"concept_id": TEXT, "question": TEXT, "scope": TEXT})


def handling(disposition, payload):
    return obj({"concept_id": TEXT, "disposition": {"const": disposition}, "payload": payload})


HANDLING = {"oneOf": [
    handling("reuse", obj({"meaning_ref": EXTERNAL, "applicability": TEXT})),
    handling("propose", obj({"working_meaning": MEANING, "applicability": TEXT})),
    handling("open", obj({"question": TEXT, "reason": TEXT, "affected_use": TEXT,
                           "owner_route": {"type": ["string", "null"]}, "continuation": TEXT})),
    handling("specialize", {"oneOf": [
        obj({"mode": {"const": "application"}, "parent_ref": REFERENCE, "application_id": TEXT, "applicability": TEXT}),
        obj({"mode": {"const": "meaning-change"}, "parent_ref": REFERENCE, "working_meaning": MEANING,
             "delta": TEXT, "identity_intention": {"enum": ["new-identity", "successor"]}, "applicability": TEXT})]})]}
VALUE_ORIGIN = obj({"parameter": TEXT, "input_id": TEXT, "selector": {"type": "string"}, "sha256": SHA})
APPLICATION = obj({"application_id": TEXT, "revision": REV, "meaning_ref": REFERENCE,
                   "parameter_contract_ref": TEXT, "context_ref": TEXT, "consumer": TEXT, "intended_use": TEXT,
                   "bindings": {"type": "object"}, "value_provenance": array(VALUE_ORIGIN, 256),
                   "applicability": {"enum": ["established-for-candidate-examination", "unestablished"]},
                   "binding_gaps": array(GAP), "lineage": LINEAGE, "authority_effect": NONE})
ASSESSMENT = obj({"assessment_id": TEXT, "revision": REV, "application_ref": EMBEDDED,
                  "input_bindings": array(BINDING), "evidence_bindings": array(BINDING),
                  "method_profile_refs": array(REFERENCE), "method_gaps": array(GAP),
                  "producer": obj({"identity": TEXT, "execution_posture": {"enum": ["synthetic", "reported", "verified-external"]},
                                   "execution_receipt": {"oneOf": [BINDING, {"type": "null"}]}}),
                  "reported_result": {"enum": ["PASS", "FAIL", "NOT_EVALUABLE"]},
                  "unevaluable_reason": {"type": ["string", "null"]},
                  "validation_posture": {"enum": ["binding-verified-within-scope", "unverified-reported", "not-evaluable"]},
                  "applicability_limits": array(TEXT, minimum=1), "lineage": LINEAGE})
MATERIALIZATION = obj({"meaning_ref": EMBEDDED, "purpose": TEXT, "authority_scope": TEXT,
                       "owner_route": {"type": ["string", "null"]}, "identity_intention": {"enum": ["new-identity", "successor"]},
                       "parent_ref": {"oneOf": [EXTERNAL, {"type": "null"}]},
                       "definition_binding": BINDING, "field_lineage_binding": BINDING})
VALIDATION = obj({"required_checks": array(TEXT), "evidence_scope": TEXT, "claim_ceiling": TEXT})
REQUEST = obj({"schema_version": {"const": "cal.define.prepare-request/v3"}, "request_id": TEXT, "request_revision": REV,
               **{k: TEXT for k in ["goal", "originating_intent", "context", "consumer", "intended_use"]},
               "adapter_selection_binding": {"type": "null"},
               "required_concepts": array(CONCEPT, 24, 1), "handling": array(HANDLING, 24, 1),
               "source_bindings": array(BINDING), "evidence_bindings": array(BINDING),
               "applications": array(APPLICATION, 64), "assessments": array(ASSESSMENT, 64),
               "materialization_selection": array(MATERIALIZATION, 24), "validation_scope": VALIDATION,
               "authority_effect": NONE, "predecessor_package_binding": BINDING,
               "field_supplement_binding": BINDING, "language_evidence_binding": BINDING},
              optional=("predecessor_package_binding", "field_supplement_binding", "language_evidence_binding"))
INPUT_ROW = obj({"input_id": TEXT, "population": {"enum": ["local-supplement", "external-evidence"]},
                 "binding": BINDING, "encoding_contract_binding": BINDING, "selector": {"type": "string"},
                 "standing_observation": obj({"status": {"const": "local-reference"}, "basis_bindings": array(BINDING), "limitations": array(TEXT)}),
                 "provenance_bindings": array(BINDING), "permitted_uses": array(TEXT, minimum=1),
                 "retention_posture": {"enum": ["permitted", "forbidden", "unresolved"]}})
CAPTURE = obj({"schema_version": {"const": "cal.define.capture-bundle/v2"}, "capture_id": TEXT, "revision": REV,
               "mode": {"const": "local-snapshot"},
               "adapter_selection_binding": {"type": "null"}, "intended_use": TEXT,
               "source_cut": obj({"kind": {"const": "local-files"}, "binding": BINDING}),
               "source_profile_binding": BINDING, "context_bindings": array(BINDING), "ontology_view_bindings": array(BINDING),
               "captured_at": TEXT, "permission_observation_binding": {"type": "null"},
               "input_rows": array(INPUT_ROW), "capture_limits": obj({"max_bytes": REV, "max_items": REV}),
               "gaps": array(GAP), "authority_effect": NONE})
NAMED_USES = ("inspect-preparation", "apply-parameters", "consume-assessment", "materialize-definition", "prepare-owner-review", "governing-application")
READINESS = obj({u: obj({"outcome": {"enum": ["ready", "blocked", "not-evaluable"]},
                        "obligations": array(TEXT, 1024), "claim_ceiling": TEXT}) for u in NAMED_USES})
PARAM_CONTRACT = obj({"contract_id": TEXT, "meaning_ref": REFERENCE, "parameters": array(PARAMETER, 24),
                      "lineage": LINEAGE, "authority_effect": NONE})
PACK = obj({"schema_version": {"const": "cal.define.pack/v3"}, "pack_id": TEXT, "revision": REV,
            "status": {"const": "candidate"}, "authority_effect": NONE,
            "scope": obj({**{k: TEXT for k in ["goal", "originating_intent", "context", "consumer", "intended_use"]}, "authority_boundary": TEXT}),
            "capture_binding": BINDING, "required_concepts": array(CONCEPT, 24, 1), "handling": array(HANDLING, 24, 1),
            "working_meanings": array(MEANING, 24), "parameter_contracts": array(PARAM_CONTRACT, 88),
            "applications": array(APPLICATION, 64), "assessments": array(ASSESSMENT, 64),
            "source_bindings": array(BINDING), "evidence_bindings": array(BINDING),
            "relationship_records": array(REFERENCE), "owner_routes": array(TEXT), "gaps": array(GAP, 1024),
            "materialization_selection": array(MATERIALIZATION, 24), "validation_scope": VALIDATION,
            "readiness": READINESS, "lineage": obj({"request_binding": BINDING, "predecessor_package_binding": {"oneOf": [BINDING, {"type": "null"}]}}),
            "claim_ceiling": TEXT})
CATALOG = obj({"schema_version": {"const": "define.source-catalog/v1"},
               "entries": array(obj({"input_id": TEXT, "binding": BINDING,
                                     "reported_standing": {"type": ["string", "null"], "maxLength": 4096}})),
               "authority_effect": NONE})
SCHEMAS = {"request": REQUEST, "capture": CAPTURE, "pack": PACK, "catalog": CATALOG}


REPORT = obj({"schema_version": {"const": "cal.define.preparation-report/v3"}, "authority_effect": NONE,
              "structural_validity": {"const": "valid"}, "capture_mode": {"const": "local-snapshot"},
              "application_checks": array(obj({"application_id": TEXT, "fully_bound": {"type": "boolean"},
                   "meaning_standing": {"enum": ["local-proposed", "local-reference"]}, "domain_assessment_executed": {"const": False}})),
              "readiness": READINESS, "assessment_execution_count": {"const": 0}, "actual_owner_outcome": {"type": "null"}, "claim_ceiling": TEXT})
MEMBERS = {"type": "object", "maxProperties": 256, "additionalProperties": {"type": "string", "maxLength": 22369624}}
UTF8_RECORD = {"type": "string", "maxLength": 1048576}
API_PARAMS = {
    "capabilities": obj({}),
    "schema": obj({"kind": TEXT}),
    "capture": obj({"request_utf8": UTF8_RECORD, "inputs": MEMBERS, "catalog_utf8": UTF8_RECORD,
                    "permit_retention": {"type": "boolean"}, "captured_at": TEXT}, optional=("catalog_utf8", "permit_retention", "captured_at")),
    "prepare": obj({"request_utf8": UTF8_RECORD, "capture_utf8": UTF8_RECORD, "inputs": MEMBERS}),
    **{op: obj({"package_members": MEMBERS}) for op in ("inspect", "reconstruct", "materialize")},
    "observe-use": obj({"package_members": MEMBERS, "requested_use": TEXT, "consumer": TEXT,
                        "current_source_base64": {"type": "string", "maxLength": 22369624}}, optional=("current_source_base64",))}
API_REQUEST = {"oneOf": [obj({"api_version": {"const": "define.api/v1"},
                 "id": {"type": "string", "minLength": 1, "maxLength": 128}, "operation": {"const": op}, "params": params}) for op, params in API_PARAMS.items()]}
API_RESULT = obj({"api_version": {"const": "define.api/v1"}, "id": {"type": ["string", "null"]},
                  "operation": {"type": ["string", "null"]},
                  "outcome": {"enum": ["prepared", "prepared-with-gaps", "ready", "not-evaluable", "invalid-input", "blocked", "unsupported", "interrupted", "outcome-unknown"]},
                  "diagnostics": array(obj({"code": TEXT, "message": TEXT})), "data": {"type": ["object", "null"]}, "authority_effect": NONE})
SCHEMAS.update({"report": REPORT, "api-request": API_REQUEST, "api-result": API_RESULT})


def check(value, which):
    tree(value)
    errors = list(Draft202012Validator(SCHEMAS[which]).iter_errors(value))
    if errors:
        error = errors[0]
        raise Refusal("schema-invalid", f"{which}: {'/'.join(map(str, error.absolute_path))}: failed {error.validator}; input values withheld")


def value_schema(schema):
    """No reference resolution, custom code, regex backtracking or implicit formats."""
    allowed = {"type", "properties", "required", "additionalProperties", "items", "minItems", "maxItems", "enum", "const", "minimum", "maximum", "minLength", "maxLength"}
    require(isinstance(schema, dict) and schema.keys() <= allowed and "type" in schema, "unsupported-parameter-schema", exit_code=4)
    require(schema["type"] in ("string", "integer", "boolean", "object", "array", "null"), "unsupported-parameter-schema", exit_code=4)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError:
        raise Refusal("invalid-parameter-schema", "Invalid declared parameter schema; values withheld") from None
    if schema["type"] == "object":
        require(schema.get("additionalProperties") is False and "properties" in schema, "ambiguous-object-parameter", "Object parameters need explicit property semantics")
        for nested in schema["properties"].values():
            value_schema(nested)
    if schema["type"] == "array":
        require("maxItems" in schema and schema["maxItems"] <= 256 and "items" in schema, "unbounded-parameter")
        value_schema(schema["items"])
