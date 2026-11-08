#!/usr/bin/env python3
"""Two local classifications over exact retained O05 generator and vocabulary evidence."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import types

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[4]
MATRIX = ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c")
READER = ("implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py",
          "8dd18391b9e9bd7cd14bb05228635452a285b81b609393601e0376679a9f8dac")
ROUTE = ("implementation/lab-runtime/local-host/t10-o05-local-models-0002/route.py",
         "e98e751b673580483ad193418f9f573b6b6dc47407eeb47ea97e34622d0e945e")
OUTPUT_SCHEMA = ("implementation/lab-runtime/local-host/t10-o05-local-models-0002/local-route.schema.json",
                 "920d92bcd5f1b0226fb16ea1331eded2a362d779fe6d7b2238d24c2daa344a4f")
O05 = ("implementation/lab-ontology/candidates/v1/receipts/O05/0001.json",
       "4375c986a84e1be17416517f0a55120895011728877ddee168cb1e7ded7ac562")
MEMBERS = {
    22: ("protocol:O06:source-metadata-generator",
         "implementation/lab-ontology/candidates/v1/migration/adapters/build-scope.json",
         "local-O05-source-metadata-generator-candidate"),
    23: ("protocol:O06:legacy-local-vocabulary",
         "implementation/lab-ontology/candidates/v1/migration/adapters/translation-profile.json",
         "local-O05-retained-vocabulary-evidence-reader"),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_module(binding, name):
    path, expected = binding
    raw = (ROOT / path).read_bytes()
    need(sha(raw) == expected, "selected executable bytes changed: " + path)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def selected_inputs():
    reader = selected_module(READER, "_t10_o05_local_reader").reader(ROOT)
    route = selected_module(ROUTE, "_t10_o05_local_route")
    matrix = json.loads(reader.read_pinned(ROOT, *MATRIX))
    need(len(matrix["rows"]) == 29 and
         [row["index"] for row in matrix["rows"]] == list(range(29)) and
         matrix["T10_complete"] is False and
         matrix["semantically_grounded_selected_representations"] == 0,
         "original T10 matrix differs")
    rows, originals = [], []
    for index, (member_ref, contract, _) in MEMBERS.items():
        row = matrix["rows"][index]
        original = json.loads(reader.read_pinned(ROOT, **row["original_body_binding"]))
        disposition = json.loads(reader.read_pinned(ROOT, **row["original_disposition_binding"]))
        choice = json.loads(reader.read_pinned(ROOT, **row["review_choice_binding"]))
        need(row["index"] == index and row["member_ref"] == member_ref and
             row["selected_representation"] is None and row["actual_owner_outcome"] is None and
             row["exact_grounded_relation_selected"] is None and
             row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
             original["kind"] == "governed-model" and original["relation_refs"] == [] and
             original["authority_effect"] == "none" and
             original["payload"]["contract_ref"] == contract and
             disposition["original_index"] == choice["original_index"] == index and
             disposition["member_ref"] == choice["member_ref"] == member_ref and
             disposition["original_body_binding"] == row["original_body_binding"] and
             disposition["admission_or_runtime_use_allowed"] is False and
             choice["admission_or_runtime_use_allowed"] is False and
             choice["original_disposition_binding"]["sha256"] ==
             row["original_disposition_binding"]["sha256"],
             "O05 original member or refusal differs")
        for binding in (row["original_target_bindings"] + row["original_evidence_bindings"] +
                        row["prepared_postimage_bindings"]):
            reader.read_pinned(ROOT, **binding)
        need(original["evidence_refs"] ==
             [binding["path"] for binding in row["original_target_bindings"]] +
             ["implementation/lab-ontology/candidates/v1/review/O06/packages/0001/preparation.json"],
             "O05 original target evidence differs")
        rows.append(row)
        originals.append(original)
    selected_o05 = next(binding for binding in rows[0]["original_evidence_bindings"]
                        if binding["path"] == O05[0])
    need(selected_o05 == {"path": O05[0], "sha256": O05[1]}, "O05 receipt pin differs")
    observed = route.observe(reader.read_pinned, ROOT, rows[0], rows[1], selected_o05)
    schema = json.loads(reader.read_pinned(ROOT, *OUTPUT_SCHEMA))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(observed)
    return reader, rows, originals, observed


def identities(index):
    suffix = "source-metadata-generator" if index == 22 else "legacy-local-vocabulary"
    model = "governed-model:lab-local:O05-" + suffix
    implementation = "implementation:lab-local:O05-" + suffix + ("-generator" if index == 22 else "-reader")
    relation = "typed-relation:lab-local:O05-" + suffix + "-instance"
    return model, implementation, relation


def documents(row, original, observed=None):
    index = row["index"]
    model_id, implementation_id, relation_id = identities(index)
    contract = MEMBERS[index][1]
    implementation_kind = MEMBERS[index][2]
    target = next(binding for binding in row["original_target_bindings"] if binding["path"] == contract)
    model_version, implementation_version = model_id + "@local.1", implementation_id + "@local.1"
    generator = (observed or selected_inputs()[3])["generator"] if index == 22 else None
    entrypoint = generator["code_binding"]["path"] if index == 22 else ROUTE[0]
    schema_ref = generator["output_schema_binding"]["path"] if index == 22 else OUTPUT_SCHEMA[0]
    evidence = ([entrypoint, contract, generator["profile_binding"]["path"],
                 generator["output_schema_binding"]["path"],
                 generator["output_record_binding"]["path"],
                 generator["manifest_binding"]["path"],
                 generator["reproduction_binding"]["path"], O05[0]]
                if index == 22 else [ROUTE[0], contract, O05[0]])
    model = deepcopy(original)
    model["node_id"] = model_id
    model["name"] = "Local O05 " + MEMBERS[index][0].split(":")[-1] + " model"
    model["payload"]["version_ref"] = model_version
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": implementation_id}]
    model["claim_ceiling"] = "One exact retained O05 candidate; no generator rerun or original admission."
    common = {"lifecycle_state": "candidate", "authority_effect": "none",
              "owner_ref": original["owner_ref"], "scope_ref": original["scope_ref"],
              "evidence_refs": evidence, "challenge_route": original["challenge_route"],
              "successor_refs": []}
    implementation = {**common, "schema_version": "cyberalchemy-lab-implementation/v1",
        "node_id": implementation_id, "kind": "implementation",
        "name": "Local O05 " + MEMBERS[index][0].split(":")[-1] + (" candidate generator" if index == 22 else " evidence reader"),
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": model_id}],
        "payload": {"implementation_kind": implementation_kind,
                    "conforms_to_schema_refs": [schema_ref],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": entrypoint, "environment_contract_ref": contract},
        "claim_ceiling": "Retained O05 candidate with repeated/cold receipt; no generator rerun, source effect or global relation."}
    relation = {**common, "schema_version": "cyberalchemy-lab-typed-relation/v2",
        "node_id": relation_id, "kind": "typed-relation",
        "name": "O05 local candidate implementation instance of model", "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": implementation_id,
                               "version_ref": implementation_version},
                    "target": {"kind": "governed-model", "ref": model_id, "version_ref": model_version},
                    "qualifiers": {"parent_version_ref": model_version,
                                   "binding_ref": (entrypoint + "#sha256=" + generator["code_binding"]["sha256"]
                                                   if index == 22 else contract + "#sha256=" + target["sha256"])},
                    "relation_evidence_refs": evidence},
        "claim_ceiling": "One local O05 candidate classification only."}
    return model, implementation, relation


def verify(reader, row, original, model, implementation, relation, observed=None):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    index = row["index"]
    model_id, implementation_id, relation_id = identities(index)
    contract, implementation_kind = MEMBERS[index][1:]
    target = next(binding for binding in row["original_target_bindings"] if binding["path"] == contract)
    generator = (observed or selected_inputs()[3])["generator"] if index == 22 else None
    entrypoint = generator["code_binding"]["path"] if index == 22 else ROUTE[0]
    schema_ref = generator["output_schema_binding"]["path"] if index == 22 else OUTPUT_SCHEMA[0]
    evidence = ([entrypoint, contract, generator["profile_binding"]["path"],
                 generator["output_schema_binding"]["path"],
                 generator["output_record_binding"]["path"],
                 generator["manifest_binding"]["path"],
                 generator["reproduction_binding"]["path"], O05[0]]
                if index == 22 else [ROUTE[0], contract, O05[0]])
    binding_ref = (entrypoint + "#sha256=" + generator["code_binding"]["sha256"]
                   if index == 22 else contract + "#sha256=" + target["sha256"])
    model_version, implementation_version = model_id + "@local.1", implementation_id + "@local.1"
    need(kind["node_id"] == relation["payload"]["relation_kind_ref"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == model_id and model["payload"]["version_ref"] == model_version and
         model["payload"]["contract_ref"] == contract and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": implementation_id}] and
         implementation["node_id"] == implementation_id and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": model_id}] and
         implementation["payload"]["implementation_kind"] == implementation_kind and
         implementation["payload"]["conforms_to_schema_refs"] == [schema_ref] and
         implementation["payload"]["execution_entrypoint_ref"] == entrypoint and
         implementation["payload"]["environment_contract_ref"] == contract and
         implementation["evidence_refs"] == evidence and
         relation["node_id"] == relation_id and relation["relation_refs"] == [] and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         relation["payload"]["source"] == {"kind": "implementation", "ref": implementation_id,
                                           "version_ref": implementation_version} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": model_id,
                                           "version_ref": model_version} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": model_version,
                                               "binding_ref": binding_ref} and
         relation["evidence_refs"] == relation["payload"]["relation_evidence_refs"] == evidence and
         all(body["owner_ref"] == original["owner_ref"] and body["scope_ref"] == original["scope_ref"] and
             body["lifecycle_state"] == "candidate" and body["authority_effect"] == "none"
             for body in (model, implementation, relation)),
         "O05 local representation join differs")


def build():
    reader, rows, originals, observed = selected_inputs()
    entries = []
    for row, original in zip(rows, originals):
        model, implementation, relation = documents(row, original, observed)
        verify(reader, row, original, model, implementation, relation, observed)
        entries.append({"member_index": row["index"], "member_ref": row["member_ref"],
                        "contract_ref": original["payload"]["contract_ref"],
                        "original_member_admitted": False,
                        "documents": {"model": model, "implementation": implementation,
                                      "typed_relation": relation}})
    return {"schema_version": "lab-T10-local-O05-model-selections/v2",
            "selected_governed_model_representations": 2, "entries": entries,
            "observed": observed,
            "route_binding": {"path": ROUTE[0], "sha256": ROUTE[1]},
            "output_schema_binding": {"path": OUTPUT_SCHEMA[0], "sha256": OUTPUT_SCHEMA[1]},
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "original_members_admitted": 0, "generator_rerun_this_run": False,
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "One retained candidate generator classification and one source-local vocabulary reader classification. No generator rerun, global relation, source effect, original admission or full T10 coverage."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
