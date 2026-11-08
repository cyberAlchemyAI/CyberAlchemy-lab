#!/usr/bin/env python3
"""Three local models for an exact, read-only O05→O06 source-retention route."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import types

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[4]
ROUTE = ("implementation/lab-runtime/local-host/t10-source-retention-route-0001/route.py",
         "c3fdfd95f26c8f4108d39c0fef38be9596f540793772804235c134938771bb31")
ROUTE_RESULT = ("implementation/lab-runtime/local-host/t10-source-retention-route-0001/RESULT.json",
                "0e5a5143e6d40338a8a0bc399ce261874729cf148e855d084119b6eddea39e0c")
READER = ("implementation/lab-runtime/local-host/t10-d75-model-selection-0001/select_model.py",
          "4d51b75926060a2b64ac193d8b218ebf6d150ec4352b7e387964db8e887396d8")
ROUTE_SCHEMA = ("implementation/lab-runtime/local-host/t10-source-retention-models-0002/source-route.schema.json",
                "5fe5331230d56601fcd57691c3b0cf470db255e6251dbeeee2841e14404c4d6f")
NAMES = {
    24: "source-dispositions",
    25: "private-metadata-use",
    26: "original-native-archive-retention",
}
CEILINGS = {
    24: "Exact 140-item O05 disposition projection into O06; no applied source effect or retirement.",
    25: "Private metadata validation only; owner and access authority remain unverified, with body import and public export denied.",
    26: "Pinned original core, manifest and native archive digest only; no archive replay or access effect.",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(binding, name):
    path, expected = binding
    raw = (ROOT / path).read_bytes()
    need(sha(raw) == expected, "selected executable source changed")
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / path)
    exec(compile(raw, result.__file__, "exec", dont_inherit=True), result.__dict__)
    return result


def validate_route(route, saved, rows, schema):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(route)
    need(route == saved["routes"] and saved["bounded_route_count"] == 3 and
         saved["selected_governed_model_representations"] == 0 and
         saved["T10_complete"] is False and saved["authority_effect"] == "none" and
         route["o06_disposition_binding"] == rows[0]["original_target_bindings"][0] and
         route["o06_private_use_binding"] == rows[1]["original_target_bindings"][0] and
         route["source_projection"]["archive_sha256"] ==
         rows[2]["original_target_bindings"][2]["sha256"] and
         route["o05_receipt_binding"] in rows[0]["original_evidence_bindings"] and
         all(route["o05_receipt_binding"] in row["original_evidence_bindings"] for row in rows) and
         route["selected_governed_models"] == 0 and
         route["source_import_or_archive_replay_executed"] is False and
         route["source_projection"]["public_body_export_allowed"] is False and
         route["source_projection"]["selected_source_effects"] == 0,
         "selected source-retention route or private-use ceiling differs")


def validate_original_member(index, row, original, disposition, choice):
    need(row["index"] == index and row["member_ref"] == "protocol:O06:" + NAMES[index] and
         row["selected_representation"] is None and
         row["actual_owner_outcome"] is None and
         row["exact_grounded_relation_selected"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
         original["relation_refs"] == [] and original["authority_effect"] == "none" and
         original["payload"]["contract_ref"] == row["original_target_bindings"][0]["path"] and
         disposition["original_index"] == choice["original_index"] == index and
         disposition["admission_or_runtime_use_allowed"] is False and
         choice["admission_or_runtime_use_allowed"] is False and
         disposition["actual_owner_outcome"] is choice["actual_owner_outcome"] is None,
         "original source member refusal differs")


def selected_inputs():
    source = module(ROUTE, "_t10_source_retention_route")
    reader = module(READER, "_t10_model_schema_reader")
    saved = json.loads(source.exact(ROOT, {"path": ROUTE_RESULT[0], "sha256": ROUTE_RESULT[1]}))
    route = source.routes(ROOT)
    schema = json.loads(source.exact(ROOT, {"path": ROUTE_SCHEMA[0], "sha256": ROUTE_SCHEMA[1]}))
    matrix = source.body(ROOT, source.MATRIX)
    rows = matrix["rows"][24:27]
    need(len(rows) == 3 and [row["index"] for row in rows] == [24, 25, 26] and
         [row["member_ref"] for row in rows] == route["original_refs"] and
         route["members"] == [24, 25, 26], "wrong original source-retention members")
    validate_route(route, saved, rows, schema)
    originals = []
    for index, row in zip(NAMES, rows):
        source.original_row(ROOT, row, index)
        original = source.body(ROOT, row["original_body_binding"])
        disposition = source.body(ROOT, row["original_disposition_binding"])
        choice = source.body(ROOT, row["review_choice_binding"])
        validate_original_member(index, row, original, disposition, choice)
        originals.append(original)
    for binding in (ROUTE_RESULT, ROUTE_SCHEMA):
        source.exact(ROOT, {"path": binding[0], "sha256": binding[1]})
    return source, reader, route, rows, originals


def documents(index, row, original):
    name = NAMES[index]
    model_id = "governed-model:lab-local:O05-" + name
    implementation_id = "implementation:lab-local:O05-" + name + "-retention-reader"
    relation_id = "typed-relation:lab-local:O05-" + name + "-reader-instance"
    model_version = model_id + "@local.2"
    implementation_version = implementation_id + "@local.2"
    target = row["original_target_bindings"][0]
    evidence = [ROUTE[0], ROUTE_RESULT[0]] + [binding["path"] for binding in row["original_target_bindings"]]
    model = deepcopy(original)
    model["node_id"] = model_id
    model["name"] = "Local O05 " + name + " retention model"
    model["payload"]["version_ref"] = model_version
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": implementation_id}]
    model["claim_ceiling"] = CEILINGS[index]
    common = {"lifecycle_state": "candidate", "authority_effect": "none",
              "owner_ref": original["owner_ref"], "scope_ref": original["scope_ref"],
              "evidence_refs": evidence, "challenge_route": original["challenge_route"],
              "successor_refs": []}
    implementation = {**common, "schema_version": "cyberalchemy-lab-implementation/v1",
        "node_id": implementation_id, "kind": "implementation",
        "name": "Local O05 " + name + " retention reader",
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": model_id}],
        "payload": {"implementation_kind": "local-O05-source-retention-reader",
                    "conforms_to_schema_refs": [ROUTE_SCHEMA[0]],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": ROUTE[0],
                    "environment_contract_ref": target["path"]},
        "claim_ceiling": CEILINGS[index] + " Exact cold route only; no archive access or effect."}
    relation = {**common, "schema_version": "cyberalchemy-lab-typed-relation/v2",
        "node_id": relation_id, "kind": "typed-relation",
        "name": "O05 " + name + " reader instance of local model", "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": implementation_id,
                               "version_ref": implementation_version},
                    "target": {"kind": "governed-model", "ref": model_id,
                               "version_ref": model_version},
                    "qualifiers": {"parent_version_ref": model_version,
                                   "binding_ref": target["path"] + "#sha256=" + target["sha256"]},
                    "relation_evidence_refs": evidence},
        "claim_ceiling": "One exact source-retention route classification; no original model admission."}
    return model, implementation, relation


def verify(reader, route, index, row, original, model, implementation, relation):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    target = row["original_target_bindings"][0]
    expected_evidence = [ROUTE[0], ROUTE_RESULT[0]] + [binding["path"] for binding in row["original_target_bindings"]]
    need(kind["node_id"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == "governed-model:lab-local:O05-" + NAMES[index] and
         model["payload"]["version_ref"] == model["node_id"] + "@local.2" and
         model["payload"]["contract_ref"] == original["payload"]["contract_ref"] == target["path"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         model["claim_ceiling"] == CEILINGS[index] and
         implementation["node_id"] == "implementation:lab-local:O05-" + NAMES[index] + "-retention-reader" and
         implementation["evidence_refs"] == expected_evidence and
         implementation["payload"]["implementation_kind"] == "local-O05-source-retention-reader" and
         implementation["payload"]["execution_entrypoint_ref"] == ROUTE[0] and
         implementation["payload"]["conforms_to_schema_refs"] == [ROUTE_SCHEMA[0]] and
         implementation["payload"]["realizes_capability_refs"] ==
         ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"] and
         implementation["payload"]["environment_contract_ref"] == target["path"] and
         implementation["claim_ceiling"] == CEILINGS[index] +
         " Exact cold route only; no archive access or effect." and
         relation["node_id"] == "typed-relation:lab-local:O05-" + NAMES[index] + "-reader-instance" and
         relation["evidence_refs"] == expected_evidence and
         relation["relation_refs"] == [] and
         relation["payload"]["relation_kind_ref"] == "relation.instance-of" and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         relation["payload"]["source"] == {"kind": "implementation", "ref": implementation["node_id"],
                                           "version_ref": implementation["node_id"] + "@local.2"} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": model["node_id"],
                                           "version_ref": model["node_id"] + "@local.2"} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": model["node_id"] + "@local.2",
                                               "binding_ref": target["path"] + "#sha256=" + target["sha256"]} and
         relation["payload"]["relation_evidence_refs"] == expected_evidence and
         relation["claim_ceiling"] == "One exact source-retention route classification; no original model admission." and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": implementation["node_id"]}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": model["node_id"]}] and
         route["source_projection"]["public_body_export_allowed"] is False and
         route["source_import_or_archive_replay_executed"] is False and
         all(body["owner_ref"] == original["owner_ref"] and
             body["scope_ref"] == original["scope_ref"] and
             body["lifecycle_state"] == "candidate" and
             body["authority_effect"] == "none" for body in (model, implementation, relation)),
         "source-retention model relation or private-use ceiling differs")


def build():
    source, reader, route, rows, originals = selected_inputs()
    entries = []
    for index, row, original in zip(NAMES, rows, originals):
        model, implementation, relation = documents(index, row, original)
        verify(reader, route, index, row, original, model, implementation, relation)
        entries.append({"member_index": index, "member_ref": row["member_ref"],
                        "original_target_bindings": row["original_target_bindings"],
                        "original_member_admitted": False,
                        "documents": {"model": model, "implementation": implementation,
                                      "typed_relation": relation}})
    return {"schema_version": "lab-T10-local-source-retention-model-selections/v2",
            "selected_governed_model_representations": 3, "entries": entries,
            "route_code_binding": {"path": ROUTE[0], "sha256": ROUTE[1]},
            "route_result_binding": {"path": ROUTE_RESULT[0], "sha256": ROUTE_RESULT[1]},
            "source_projection": route["source_projection"],
            "source_import_or_archive_replay_executed": False,
            "public_body_export_allowed": False, "owner_access_authority_verified": False,
            "selected_source_effects": 0, "original_members_admitted": 0,
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Three local relation-backed classifications of exact retained O05/O06 source disposition, private-use and archive history. The archive is only hashed; no archive replay, owner/access authority, body import/export, source retirement, original admission or T10 completion."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
