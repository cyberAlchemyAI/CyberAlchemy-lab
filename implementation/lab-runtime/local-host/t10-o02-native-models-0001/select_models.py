#!/usr/bin/env python3
"""Four local classifications of the retained O02 native-evidence route."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import types

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
ROUTE = "implementation/lab-runtime/local-host/t10-representation-native-route-0001/route.py"
ROUTE_SHA = "9e1e67ca84b3ecfd6f4149d3954bab121969824d9c7922edaa04a3e7a3ec7707"
ROUTE_RESULT = "implementation/lab-runtime/local-host/t10-representation-native-route-0001/RESULT.json"
ROUTE_RESULT_SHA = "8e456655a185761397e9aa50f84ae556b96f204f8ba22c7d85b7dfae15d70c0d"
READER = "implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py"
READER_SHA = "8dd18391b9e9bd7cd14bb05228635452a285b81b609393601e0376679a9f8dac"
OUTPUT_SCHEMA = "implementation/lab-runtime/local-host/t10-o02-native-models-0001/native-route.schema.json"
OUTPUT_SCHEMA_SHA = "2594e644cfea124317b6f2ed5d7a6c9fc1a9a1d5a9995699f62a6fdf3edfaa56"
MEMBERS = (16, 17, 19, 20)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(path, expected, name):
    raw = (ROOT / path).read_bytes()
    need(sha(raw) == expected, "selected executable bytes changed")
    selected = types.ModuleType(name)
    selected.__file__ = str(ROOT / path)
    exec(compile(raw, selected.__file__, "exec", dont_inherit=True), selected.__dict__)
    return selected


def validate_member(row, original, route, index):
    need(row["index"] == index and row["member_ref"] == route["original_refs"][MEMBERS.index(index)] and
         row["selected_representation"] is None and row["actual_owner_outcome"] is None and
         row["exact_grounded_relation_selected"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
         original["relation_refs"] == [] and original["authority_effect"] == "none" and
         original["payload"]["contract_ref"] in
         {binding["path"] for binding in row["original_target_bindings"]},
         "O02 original member selection differs")


def selected_inputs():
    source = module(ROUTE, ROUTE_SHA, "_t10_o02_route")
    reader = module(READER, READER_SHA, "_t10_o02_reader").reader(ROOT)
    saved = json.loads(reader.read_pinned(ROOT, ROUTE_RESULT, ROUTE_RESULT_SHA))
    route = source.routes(ROOT)
    need(route == saved["routes"] and saved["bounded_route_count"] == 4 and
         saved["selected_governed_model_representations"] == 0 and
         saved["T10_complete"] is False and saved["authority_effect"] == "none",
         "retained O02 route receipt differs")
    schema = json.loads(reader.read_pinned(ROOT, OUTPUT_SCHEMA, OUTPUT_SCHEMA_SHA))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(route)
    matrix = json.loads(reader.read_pinned(ROOT, **source.MATRIX))
    originals = []
    rows = []
    for index in MEMBERS:
        row = matrix["rows"][index]
        original = json.loads(reader.read_pinned(ROOT, **row["original_body_binding"]))
        validate_member(row, original, route, index)
        rows.append(row)
        originals.append(original)
    return reader, route, rows, originals


def documents(row, original):
    name = row["member_ref"].split(":")[-1]
    model_id = "governed-model:lab-local:O02-" + name
    implementation_id = "implementation:lab-local:O02-" + name + "-reader"
    relation_id = "typed-relation:lab-local:O02-" + name + "-instance"
    model_version = model_id + "@local.1"
    implementation_version = implementation_id + "@local.1"
    contract = original["payload"]["contract_ref"]
    target = next(binding for binding in row["original_target_bindings"] if binding["path"] == contract)
    evidence = [ROUTE, contract, ROUTE_RESULT]
    model = deepcopy(original)
    model["node_id"] = model_id
    model["name"] = "Local O02 " + name + " evidence model"
    model["payload"]["version_ref"] = model_version
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": implementation_id}]
    model["claim_ceiling"] = "One retained O02 native-evidence route; no new native execution or original admission."
    common = {"lifecycle_state": "candidate", "authority_effect": "none",
              "owner_ref": original["owner_ref"], "scope_ref": original["scope_ref"],
              "evidence_refs": evidence, "challenge_route": original["challenge_route"],
              "successor_refs": []}
    implementation = {**common, "schema_version": "cyberalchemy-lab-implementation/v1",
        "node_id": implementation_id, "kind": "implementation",
        "name": "Local O02 " + name + " retained-evidence reader",
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": model_id}],
        "payload": {"implementation_kind": "local-O02-retained-evidence-reader",
                    "conforms_to_schema_refs": [OUTPUT_SCHEMA],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": ROUTE, "environment_contract_ref": contract},
        "claim_ceiling": "Cold selected-source and native-view join only; no Rust rebuild or global edge."}
    relation = {**common, "schema_version": "cyberalchemy-lab-typed-relation/v2",
        "node_id": relation_id, "kind": "typed-relation",
        "name": "O02 " + name + " reader instance of local model", "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": implementation_id,
                               "version_ref": implementation_version},
                    "target": {"kind": "governed-model", "ref": model_id, "version_ref": model_version},
                    "qualifiers": {"parent_version_ref": model_version,
                                   "binding_ref": contract + "#sha256=" + target["sha256"]},
                    "relation_evidence_refs": evidence},
        "claim_ceiling": "One exact O02 local reader classification only."}
    return model, implementation, relation


def verify(reader, row, original, model, implementation, relation):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    name = row["member_ref"].split(":")[-1]
    model_id = "governed-model:lab-local:O02-" + name
    implementation_id = "implementation:lab-local:O02-" + name + "-reader"
    relation_id = "typed-relation:lab-local:O02-" + name + "-instance"
    contract = original["payload"]["contract_ref"]
    target = next(binding for binding in row["original_target_bindings"] if binding["path"] == contract)
    evidence = [ROUTE, contract, ROUTE_RESULT]
    need(kind["node_id"] == relation["payload"]["relation_kind_ref"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == model_id and model["payload"]["version_ref"] == model_id + "@local.1" and
         model["payload"]["contract_ref"] == contract and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": implementation_id}] and
         implementation["node_id"] == implementation_id and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": model_id}] and
         implementation["payload"]["implementation_kind"] == "local-O02-retained-evidence-reader" and
         implementation["payload"]["conforms_to_schema_refs"] == [OUTPUT_SCHEMA] and
         implementation["payload"]["execution_entrypoint_ref"] == ROUTE and
         implementation["payload"]["environment_contract_ref"] == contract and
         implementation["evidence_refs"] == evidence and
         relation["node_id"] == relation_id and relation["relation_refs"] == [] and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         relation["payload"]["source"] == {"kind": "implementation", "ref": implementation_id,
                                           "version_ref": implementation_id + "@local.1"} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": model_id,
                                           "version_ref": model_id + "@local.1"} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": model_id + "@local.1",
                                               "binding_ref": contract + "#sha256=" + target["sha256"]} and
         relation["evidence_refs"] == relation["payload"]["relation_evidence_refs"] == evidence and
         all(body["owner_ref"] == original["owner_ref"] and
             body["scope_ref"] == original["scope_ref"] and
             body["lifecycle_state"] == "candidate" and body["authority_effect"] == "none"
             for body in (model, implementation, relation)),
         "O02 local representation join differs")


def build():
    reader, route, rows, originals = selected_inputs()
    entries = []
    for row, original in zip(rows, originals):
        model, implementation, relation = documents(row, original)
        verify(reader, row, original, model, implementation, relation)
        entries.append({"member_index": row["index"], "member_ref": row["member_ref"],
                        "original_member_admitted": False,
                        "contract_ref": original["payload"]["contract_ref"],
                        "documents": {"model": model, "implementation": implementation,
                                      "typed_relation": relation}})
    return {"schema_version": "lab-T10-local-O02-native-model-selections/v1",
            "selected_governed_model_representations": 4, "entries": entries,
            "native_observed": route["observed"],
            "route_code_binding": {"path": ROUTE, "sha256": ROUTE_SHA},
            "route_result_binding": {"path": ROUTE_RESULT, "sha256": ROUTE_RESULT_SHA},
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "original_members_admitted": 0, "native_replayed_this_run": False,
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Four local classifications of source-pinned retained O02 profile, native implementation, translation and unknown-confidence evidence. No Rust/native rerun, global edge, original admission or full T10 coverage."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
