#!/usr/bin/env python3
"""Local relation-backed classification of the exact retained W09 audit consumer."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import types

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
ROUTE = "implementation/lab-runtime/local-host/t10-w09-evidence-route-0001/route.py"
ROUTE_SHA = "82fd7f74c7f9caf46ecc4357439b6329ccf2b38b0a446fd03d2250ae3eb181aa"
READER = "implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py"
READER_SHA = "8dd18391b9e9bd7cd14bb05228635452a285b81b609393601e0376679a9f8dac"
OUTPUT_SCHEMA = "implementation/lab-runtime/local-host/t10-w09-model-selection-0003/w09-route-result.schema.json"
OUTPUT_SCHEMA_SHA = "d1f83ba99e6b1ce0d15bf31dab5d61c02c44c652749096690fb8a68d2861091f"
MODEL = "governed-model:lab-local:O06-W09-bounded-evidence"
IMPLEMENTATION = "implementation:lab-local:O06-W09-evidence-consumer"
RELATION = "typed-relation:lab-local:O06-W09-evidence-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_module(path, expected, name):
    raw = (ROOT / path).read_bytes()
    need(sha(raw) == expected, "selected source bytes changed: " + path)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def selected_inputs():
    route = pinned_module(ROUTE, ROUTE_SHA, "_t10_w09_route")
    reader_module = pinned_module(READER, READER_SHA, "_t10_w09_schema_reader")
    reader = reader_module.reader(ROOT)
    matrix = json.loads(reader.read_pinned(ROOT, **route.MATRIX))
    row = matrix["rows"][28]
    need(row["index"] == 28 and row["member_ref"] == "protocol:O06:W09-bounded-work-evidence" and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
         row["selected_representation"] is None and row["actual_owner_outcome"] is None,
         "original W09 member changed")
    original = json.loads(reader.read_pinned(ROOT, **row["original_body_binding"]))
    need(original["relation_refs"] == [] and original["payload"]["contract_ref"] ==
         row["original_target_bindings"][0]["path"], "original W09 model changed")
    observed = route.route(ROOT)
    output_schema = json.loads(reader.read_pinned(ROOT, OUTPUT_SCHEMA, OUTPUT_SCHEMA_SHA))
    Draft202012Validator.check_schema(output_schema)
    Draft202012Validator(output_schema).validate(observed)
    need(observed["index"] == 28 and len(observed["case_audit_review_rows"]) == 3 and
         [x["audit_result"] for x in observed["case_audit_review_rows"]] == ["FLAG", "FLAG", "PASS"] and
         observed["selected_governed_model"] is None and observed["authority_effect"] == "none",
         "W09 consumer or counterevidence changed")
    return reader, row, original, observed


def documents(original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local W09 bounded evidence model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Exact retained W09 three-case audit/review join; two FLAG results remain counterevidence."
    common = {"lifecycle_state": "candidate", "authority_effect": "none",
              "owner_ref": original["owner_ref"], "scope_ref": original["scope_ref"],
              "evidence_refs": [ROUTE, original["payload"]["contract_ref"]],
              "challenge_route": original["challenge_route"], "successor_refs": []}
    implementation = {**common, "schema_version": "cyberalchemy-lab-implementation/v1",
        "node_id": IMPLEMENTATION, "kind": "implementation", "name": "Local W09 retained-evidence consumer",
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-W09-retained-case-audit-review-consumer",
                    "conforms_to_schema_refs": [OUTPUT_SCHEMA],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": ROUTE,
                    "environment_contract_ref": original["payload"]["contract_ref"]},
        "claim_ceiling": "Cold retained evidence route only; W09 not rerun and no Lesson permission."}
    relation = {**common, "schema_version": "cyberalchemy-lab-typed-relation/v2",
        "node_id": RELATION, "kind": "typed-relation", "name": "W09 evidence consumer instance of local model",
        "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": ROUTE + "#sha256=" + ROUTE_SHA},
                    "relation_evidence_refs": [ROUTE, original["payload"]["contract_ref"]]},
        "claim_ceiling": "One local W09 retained-evidence consumer classification only."}
    return model, implementation, relation


def verify(reader, original, observed, model, implementation, relation):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    expected_model_link = {"relation_kind_ref": "relation.instance-of", "direction": "target",
                           "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}
    expected_implementation_link = {"relation_kind_ref": "relation.instance-of", "direction": "source",
                                    "counterpart_kind": "governed-model", "counterpart_ref": MODEL}
    expected_source = {"kind": "implementation", "ref": IMPLEMENTATION,
                       "version_ref": IMPLEMENTATION_VERSION}
    expected_target = {"kind": "governed-model", "ref": MODEL,
                       "version_ref": MODEL_VERSION}
    need({"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         kind["node_id"] == "relation.instance-of" and
         relation["payload"]["relation_kind_ref"] == kind["node_id"] and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["implementation_kind"] == "local-W09-retained-case-audit-review-consumer" and
         relation["node_id"] == RELATION and
         model["relation_refs"] == [expected_model_link] and
         implementation["relation_refs"] == [expected_implementation_link] and
         relation["relation_refs"] == [] and
         model["payload"]["contract_ref"] == original["payload"]["contract_ref"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         implementation["evidence_refs"] == [ROUTE, original["payload"]["contract_ref"]] and
         implementation["payload"]["execution_entrypoint_ref"] == ROUTE and
         implementation["payload"]["conforms_to_schema_refs"] == [OUTPUT_SCHEMA] and
         implementation["payload"]["environment_contract_ref"] == original["payload"]["contract_ref"] and
         relation["payload"]["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                               "binding_ref": ROUTE + "#sha256=" + ROUTE_SHA} and
         relation["payload"]["source"] == expected_source and
         relation["payload"]["target"] == expected_target and
         relation["payload"]["relation_evidence_refs"] == implementation["evidence_refs"] and
         relation["evidence_refs"] == implementation["evidence_refs"] and
         all(body["owner_ref"] == original["owner_ref"] and
             body["scope_ref"] == original["scope_ref"] and
             body["lifecycle_state"] == "candidate"
             for body in (model, implementation, relation)) and
         [x["audit_result"] for x in observed["case_audit_review_rows"]] == ["FLAG", "FLAG", "PASS"] and
         all(x["authority_effect"] == "none" for x in (model, implementation, relation)),
         "W09 local model join changed")


def build():
    reader, row, original, observed = selected_inputs()
    model, implementation, relation = documents(original)
    verify(reader, original, observed, model, implementation, relation)
    return {"schema_version": "lab-T10-local-W09-model-selection/v3", "member_index": 28,
            "member_ref": row["member_ref"], "selected_governed_model_representations": 1,
            "case_audit_review_rows": observed["case_audit_review_rows"],
            "consumer_route_binding": {"path": ROUTE, "sha256": ROUTE_SHA},
            "documents": {"model": model, "implementation": implementation,
                          "typed_relation": relation}, "runner_sha256": sha(Path(__file__).read_bytes()),
            "original_member_admitted": False, "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "One local W09 evidence model over retained Engineering FLAG, Research FLAG and Learning PASS. No W09 replay, original admission, Lesson permission or complete T10 coverage."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
