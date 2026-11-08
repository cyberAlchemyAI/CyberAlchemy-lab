"""One local model for the exact O06 three-cut query residue consumer."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path
import types

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[4]
QUERY_MODEL = ROOT / "implementation/lab-runtime/local-host/t10-query-contract-model-selection-0001/select_model.py"
QUERY_MODEL_SHA = "8dd18391b9e9bd7cd14bb05228635452a285b81b609393601e0376679a9f8dac"
MODEL = "governed-model:lab-local:O06-query-coverage-residue"
IMPLEMENTATION = "implementation:lab-local:O06-query-residue-consumer"
RELATION = "typed-relation:lab-local:O06-query-residue-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"
QUERY_SCHEMA_REFS = [
    "implementation/lab-ontology/candidates/v1/queries/successors/0009/contracts/request.schema.json",
    "implementation/lab-ontology/candidates/v1/queries/successors/0009/contracts/response.schema.json",
]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_query_model():
    raw = QUERY_MODEL.read_bytes()
    need(sha(raw) == QUERY_MODEL_SHA, "selected query consumer source changed")
    module = types.ModuleType("_cal_t10_selected_query_model")
    module.__file__ = str(QUERY_MODEL)
    exec(compile(raw, str(QUERY_MODEL), "exec", dont_inherit=True), module.__dict__)
    return module


def join_proposal(proposal, route):
    need(set(proposal) == {"current-D75", "historical-D73", "native-O05"} and
         route["members"] == [21, 27] and route["selected_governed_models"] == 0 and
         route["runtime_query_replayed"] is False and route["authority_effect"] == "none",
         "query residue source scope differs")
    cuts = route["source_cuts"]
    need(set(cuts) == set(proposal) and len(set(cuts.values())) == 3,
         "three query source cuts conflated")
    questions = []
    for scope in sorted(proposal):
        part = proposal[scope]
        need(set(part) == {"questions", "result_binding"} and part["questions"],
             "query residue partition differs")
        for name, value in sorted(part["questions"].items()):
            need(value["source_snapshot"]["source_cut_digest"] == cuts[scope] and
                 value["authority_effect"] == "none",
                 "query residue source cut differs")
            questions.append({
                "scope": scope,
                "question": name,
                "source_cut_digest": cuts[scope],
                "result_status": value["result_status"],
                "response_binding": value["response_binding"],
                "gap_count": len(value["gaps"]),
            })
    observed = []
    for item in route["producer_consumer_questions"]:
        matches = [q for q in questions if q["question"] == item["question"] and
                   q["source_cut_digest"] == item["source_cut_digest"]]
        need(len(matches) == 1 and
             all(matches[0][field] == item[field] for field in
                 ("result_status", "response_binding", "gap_count")),
             "retained query residue producer/consumer link differs")
        observed.append(matches[0])
    expected_keys = {(q["scope"], q["question"], q["source_cut_digest"]) for q in questions}
    observed_keys = [(q["scope"], q["question"], q["source_cut_digest"]) for q in observed]
    need(len(questions) == len(observed) == len(expected_keys) == len(set(observed_keys)) == 5 and
         set(observed_keys) == expected_keys and
         {q["scope"] for q in observed} == set(cuts),
         "complete five-question residue join required")
    return sorted(observed, key=lambda q: (q["scope"], q["question"]))


def selected_inputs():
    parent = selected_query_model()
    reader, _, _, route, query = parent.selected_inputs()
    matrix = json.loads(reader.read_pinned(ROOT, *parent.MATRIX))
    need([binding["path"] for binding in matrix["rows"][21]["original_target_bindings"][2:4]] == QUERY_SCHEMA_REFS,
         "retained query request/response schema route changed")
    row = matrix["rows"][27]
    need(row["index"] == 27 and row["member_ref"] == "protocol:O06:query-coverage-residue" and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs" and
         row["selected_representation"] is None and row["actual_owner_outcome"] is None,
         "original residue member selection changed")
    original = json.loads(reader.read_pinned(ROOT, **row["original_body_binding"]))
    disposition = json.loads(reader.read_pinned(ROOT, **row["original_disposition_binding"]))
    choice = json.loads(reader.read_pinned(ROOT, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and
         disposition["original_index"] == choice["original_index"] == 27 and
         disposition["admission_or_runtime_use_allowed"] is False and
         choice["admission_or_runtime_use_allowed"] is False,
         "original residue refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        reader.read_pinned(ROOT, **binding)
    need(len(row["original_target_bindings"]) == 1 and
         route["proposal_binding"] == row["original_target_bindings"][0] and
         original["payload"]["contract_ref"] == route["proposal_binding"]["path"],
         "original residue proposal binding differs")
    proposal = json.loads(reader.read_pinned(ROOT, **route["proposal_binding"]))
    links = join_proposal(proposal, route)
    return parent, reader, row, original, route, query, proposal, links


def documents(parent, original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local O06 three-cut query residue model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Exact retained five-question query residue join over three distinct source cuts; no query rerun or general coverage."
    route_path = parent.ROUTE[0]
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local O06 query residue consumer",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": original["owner_ref"],
        "scope_ref": original["scope_ref"], "evidence_refs": [route_path, original["payload"]["contract_ref"]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-O06-three-cut-query-residue-consumer",
                    "conforms_to_schema_refs": QUERY_SCHEMA_REFS,
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": route_path,
                    "environment_contract_ref": original["payload"]["contract_ref"]},
        "claim_ceiling": "Five source-pinned retained-response links only; no current query engine rerun or whole-repository coverage.",
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "Query residue consumer instance of local model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": original["owner_ref"],
        "scope_ref": original["scope_ref"], "evidence_refs": [route_path, original["payload"]["contract_ref"]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": route_path + "#sha256=" + parent.ROUTE[1]},
                    "relation_evidence_refs": [route_path, original["payload"]["contract_ref"]]},
        "claim_ceiling": "Local classification of the exact retained query-residue consumer only.",
    }
    return model, implementation, relation


def verify_documents(parent, reader, original, route, links, model, implementation, relation):
    for path, body in ((reader.MODEL_SCHEMA, model),
                       (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        schema = json.loads(reader.read_pinned(ROOT, path, reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(reader.read_pinned(ROOT, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    need(kind["node_id"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == original["payload"]["contract_ref"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["execution_entrypoint_ref"] == parent.ROUTE[0] and
         implementation["payload"]["conforms_to_schema_refs"] == QUERY_SCHEMA_REFS and
         implementation["payload"]["environment_contract_ref"] == original["payload"]["contract_ref"] and
         relation["payload"]["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                                           "version_ref": IMPLEMENTATION_VERSION} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": MODEL,
                                           "version_ref": MODEL_VERSION} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                               "binding_ref": parent.ROUTE[0] + "#sha256=" + parent.ROUTE[1]} and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                    "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                             "counterpart_kind": "governed-model", "counterpart_ref": MODEL}] and
         len(links) == 5 and len(set(route["source_cuts"].values())) == 3 and
         all(x["authority_effect"] == "none" and x["lifecycle_state"] == "candidate"
             for x in (model, implementation, relation)),
         "query residue model classification differs")


def build():
    parent, reader, row, original, route, query, proposal, links = selected_inputs()
    model, implementation, relation = documents(parent, original)
    verify_documents(parent, reader, original, route, links, model, implementation, relation)
    return {"schema_version": "lab-T10-local-query-residue-model-selection/v1",
            "member_index": 27, "member_ref": row["member_ref"],
            "selected_governed_model_representations": 1,
            "producer_proposal_binding": route["proposal_binding"],
            "consumer_route_binding": {"path": parent.ROUTE[0], "sha256": parent.ROUTE[1]},
            "source_cuts": route["source_cuts"], "links": links,
            "documents": {"model": model, "implementation": implementation,
                          "typed_relation": relation},
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "original_member_admitted": False, "T10_complete": False,
            "authority_effect": "none",
            "claim_ceiling": "One local relation-backed query-residue model for five retained producer/consumer links across historical D73, current D75 and native O05 cuts. No current query rerun, original admission or complete coverage."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
