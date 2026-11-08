#!/usr/bin/env python3
"""Ten local W08 design representations; does not execute workflow transitions."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import types

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
ROUTE = "implementation/lab-runtime/local-host/t10-workflow-route-0001/route.py"
ROUTE_SHA = "3cf69b30db889d6d0a31820760e5959c6294eef8713f3606b57a3c5cec80212c"
ROUTE_RESULT = "implementation/lab-runtime/local-host/t10-workflow-route-0001/RESULT-0002.json"
ROUTE_RESULT_SHA = "4383a1187aa68ae60f22f4709d8df9d4c99d2528f8c56976b1124cf92b74c027"
READER = "implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py"
READER_SHA = "8dd18391b9e9bd7cd14bb05228635452a285b81b609393601e0376679a9f8dac"
DESIGN_SCHEMA = "implementation/lab-runtime/local-host/t10-w08-design-models-0001/design-route.schema.json"
DESIGN_SCHEMA_SHA = "afcf2c29a9a2746ed5b3936b3dee6b9fa8d14583d929e2d1f43e43f28c902b6e"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(path, expected, name):
    raw = (ROOT / path).read_bytes()
    need(sha(raw) == expected, "selected executable source changed")
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / path)
    exec(compile(raw, result.__file__, "exec", dont_inherit=True), result.__dict__)
    return result


def validate_original_selection(row, original, route):
    need(row["index"] == route["index"] and
         row["member_ref"] == route["member_ref"] and
         row["selected_representation"] is None and
         row["actual_owner_outcome"] is None and
         row["exact_grounded_relation_selected"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
         original["relation_refs"] == [] and
         original["payload"]["contract_ref"] == route["w08_design_binding"]["path"] and
         route["workflow_type_ref"] == "workflow:" + route["member_ref"].split(":")[-1] + ":v1-candidate",
         "W08 original member is not an unselected refused design")


def selected_inputs():
    source = module(ROUTE, ROUTE_SHA, "_t10_w08_route")
    reader = module(READER, READER_SHA, "_t10_w08_reader").reader(ROOT)
    saved = json.loads(reader.read_pinned(ROOT, ROUTE_RESULT, ROUTE_RESULT_SHA))
    routes = source.design_routes(ROOT)
    need(routes == saved["design_routes"] and saved["design_route_count"] == 10 and
         saved["design_transition_count"] == 28 and
         saved["selected_governed_model_representations"] == 0 and
         saved["T10_complete"] is False and saved["authority_effect"] == "none",
         "selected W08 route receipt differs")
    schema = json.loads(reader.read_pinned(ROOT, DESIGN_SCHEMA, DESIGN_SCHEMA_SHA))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    matrix = json.loads(reader.read_pinned(ROOT, source.MATRIX, source.MATRIX_SHA))
    originals = []
    for route in routes:
        validator.validate(route)
        row = matrix["rows"][route["index"]]
        original = json.loads(reader.read_pinned(ROOT, **row["original_body_binding"]))
        validate_original_selection(row, original, route)
        originals.append(original)
    need([r["index"] for r in routes] == list(range(4, 14)) and
         len({r["member_ref"] for r in routes}) == 10 and
         len({ref for route in routes for ref in route["transition_refs"]}) == 28,
         "ten exact W08 members or 28 transitions missing")
    return reader, routes, originals


def documents(original, route):
    index = route["index"]
    name = route["member_ref"].split(":")[-1]
    model_id = "governed-model:lab-local:W08-" + name + "-design"
    implementation_id = "implementation:lab-local:W08-" + name + "-design-reader"
    relation_id = "typed-relation:lab-local:W08-" + name + "-design-instance"
    model_version = model_id + "@local.1"
    implementation_version = implementation_id + "@local.1"
    evidence = [route["w08_design_binding"]["path"], route["original_definition_binding"]["path"], ROUTE]
    model = deepcopy(original)
    model["node_id"] = model_id
    model["name"] = "Local W08 " + name + " transition design model"
    model["payload"]["version_ref"] = model_version
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": implementation_id}]
    model["claim_ceiling"] = "Exact candidate W08 transition design only; not an executable workflow."
    common = {"lifecycle_state": "candidate", "authority_effect": "none",
              "owner_ref": original["owner_ref"], "scope_ref": original["scope_ref"],
              "evidence_refs": evidence, "challenge_route": original["challenge_route"],
              "successor_refs": []}
    implementation = {**common, "schema_version": "cyberalchemy-lab-implementation/v1",
        "node_id": implementation_id, "kind": "implementation", "name": "Local W08 " + name + " design reader",
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": model_id}],
        "payload": {"implementation_kind": "local-W08-transition-design-reader",
                    "conforms_to_schema_refs": [DESIGN_SCHEMA],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": ROUTE,
                    "environment_contract_ref": route["original_definition_binding"]["path"]},
        "claim_ceiling": "Reads the candidate design and selected original definition; no transition execution."}
    relation = {**common, "schema_version": "cyberalchemy-lab-typed-relation/v2",
        "node_id": relation_id, "kind": "typed-relation",
        "name": "W08 " + name + " design reader instance of local model", "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": implementation_id,
                               "version_ref": implementation_version},
                    "target": {"kind": "governed-model", "ref": model_id, "version_ref": model_version},
                    "qualifiers": {"parent_version_ref": model_version,
                                   "binding_ref": route["w08_design_binding"]["path"] +
                                   "#sha256=" + route["w08_design_binding"]["sha256"]},
                    "relation_evidence_refs": evidence},
        "claim_ceiling": "One exact W08 design reader classification; no original model admission."}
    return model, implementation, relation


def verify(reader, route, original, model, implementation, relation):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    name = route["member_ref"].split(":")[-1]
    model_id = "governed-model:lab-local:W08-" + name + "-design"
    implementation_id = "implementation:lab-local:W08-" + name + "-design-reader"
    relation_id = "typed-relation:lab-local:W08-" + name + "-design-instance"
    expected_model_link = {"relation_kind_ref": "relation.instance-of", "direction": "target",
                           "counterpart_kind": "implementation", "counterpart_ref": implementation_id}
    expected_implementation_link = {"relation_kind_ref": "relation.instance-of", "direction": "source",
                                    "counterpart_kind": "governed-model", "counterpart_ref": model_id}
    need({"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         kind["node_id"] == relation["payload"]["relation_kind_ref"] == "relation.instance-of" and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         model["node_id"] == model_id and model["payload"]["version_ref"] == model_id + "@local.1" and
         implementation["node_id"] == implementation_id and relation["node_id"] == relation_id and
         model["payload"]["contract_ref"] == route["w08_design_binding"]["path"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["evidence_refs"] == original["evidence_refs"] and
         model["relation_refs"] == [expected_model_link] and
         implementation["relation_refs"] == [expected_implementation_link] and
         relation["relation_refs"] == [] and
         implementation["payload"]["conforms_to_schema_refs"] == [DESIGN_SCHEMA] and
         implementation["payload"]["execution_entrypoint_ref"] == ROUTE and
         implementation["payload"]["environment_contract_ref"] == route["original_definition_binding"]["path"] and
         relation["payload"]["source"] == {"kind": "implementation", "ref": implementation["node_id"],
                                           "version_ref": implementation["node_id"] + "@local.1"} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": model["node_id"],
                                           "version_ref": model["node_id"] + "@local.1"} and
         relation["payload"]["qualifiers"] == {
             "parent_version_ref": model["node_id"] + "@local.1",
             "binding_ref": route["w08_design_binding"]["path"] + "#sha256=" + route["w08_design_binding"]["sha256"]} and
         relation["payload"]["relation_evidence_refs"] == implementation["evidence_refs"] and
         relation["evidence_refs"] == implementation["evidence_refs"] and
         all(body["owner_ref"] == original["owner_ref"] and
             body["scope_ref"] == original["scope_ref"] and
             body["lifecycle_state"] == "candidate"
             for body in (model, implementation, relation)) and
         not route["admitted_or_executable"] and route["selected_original_relation"] is None and
         all(body["authority_effect"] == "none" for body in (model, implementation, relation)),
         "W08 design representation join differs")


def build():
    reader, routes, originals = selected_inputs()
    entries = []
    for route, original in zip(routes, originals):
        model, implementation, relation = documents(original, route)
        verify(reader, route, original, model, implementation, relation)
        entries.append({"member_index": route["index"], "member_ref": route["member_ref"],
                        "workflow_type_ref": route["workflow_type_ref"],
                        "transition_refs": route["transition_refs"],
                        "design_binding": route["w08_design_binding"],
                        "original_member_admitted": False,
                        "documents": {"model": model, "implementation": implementation,
                                      "typed_relation": relation}})
    return {"schema_version": "lab-T10-local-W08-design-model-selections/v1",
            "selected_governed_model_representations": len(entries), "entries": entries,
            "route_code_binding": {"path": ROUTE, "sha256": ROUTE_SHA},
            "route_result_binding": {"path": ROUTE_RESULT, "sha256": ROUTE_RESULT_SHA},
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "design_transition_count": sum(len(x["transition_refs"]) for x in entries),
            "original_members_admitted": 0, "workflow_transitions_executed": 0,
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Ten local relation-backed classifications of exact W08 candidate designs and 28 transition declarations. No workflow execution, original model admission or complete T10 coverage."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
