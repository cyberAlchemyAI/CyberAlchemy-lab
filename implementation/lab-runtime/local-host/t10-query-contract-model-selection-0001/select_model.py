#!/usr/bin/env python3
"""One local, relation-backed T10 query-contract model on selected consumer bytes."""
from __future__ import annotations

from copy import deepcopy
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
SHARED = "implementation/lab-runtime/local-host/t10-d75-model-selection-0001/select_model.py"
SHARED_SHA = "4d51b75926060a2b64ac193d8b218ebf6d150ec4352b7e387964db8e887396d8"
MATRIX = ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c")
ROUTE = ("implementation/lab-runtime/local-host/t10-query-residue-route-0001/route.py",
         "9c84e73e6faf3a7a8691a922fe2d1a14c0196e00c5f85da88867dd329fc6da76")
ROUTE_RESULT = ("implementation/lab-runtime/local-host/t10-query-residue-route-0001/RESULT.json",
                "714494791c7c499388dd406c28dcdcaf7db37dc6142ff933c93eb83a0598b6f2")
O03_VERIFY = ("implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004/verify.py",
              "7719082957a292cbb4807447dfaa1f0041e85f35e4105ba5e1e7ecb45bc85e13")
O03_RUNNER = ("implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004/secure_query.py",
              "13f889f60430ebf53818bd9e4648e184dcbb23a2f3456ed01f0af014efa21676")
O03_RESULT = ("implementation/lab-runtime/local-host/t10-o03-query-origin-successor-0004/VERIFIED-JOIN.json",
              "b82da29abae49daf9aff9cf03a97fc0b0235a2f4d09d2822e7f42a876d6af10b")
PREPARATION = ("implementation/lab-ontology/candidates/v1/review/O06/packages/0001/preparation.json",
               "55f56db53ff17fa935342048f145862db67908f8cc97324438d93237de6e1762")
MODEL = "governed-model:lab-local:O06-three-lens-query-contract"
IMPLEMENTATION = "implementation:lab-local:O06-three-lens-query-consumer"
RELATION = "typed-relation:lab-local:O06-query-consumer-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def reader(root):
    source = root / SHARED
    for item in (source, *source.parents):
        need(not stat.S_ISLNK(item.lstat().st_mode), "linked reader origin")
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size < 1024 * 1024, "reader origin not regular")
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        need(before == after and len(raw) == before.st_size and sha(raw) == SHARED_SHA,
             "reader source changed")
    finally:
        os.close(fd)
    module = types.ModuleType("t10_pinned_query_reader")
    module.__file__ = str(source)
    exec(compile(raw, str(source), "exec", dont_inherit=True), module.__dict__)
    module.read_pinned(root, SHARED, SHARED_SHA)
    return module


def run_consumers(root, selected_reader):
    route_raw = selected_reader.read_pinned(root, *ROUTE)
    verifier_raw = selected_reader.read_pinned(root, *O03_VERIFY)
    runner_raw = selected_reader.read_pinned(root, *O03_RUNNER)
    for binding in (ROUTE_RESULT, O03_RESULT):
        selected_reader.read_pinned(root, *binding)
    # The executable is compiled from the same pinned bytes supplied on stdin;
    # the path is only its diagnostic origin, never the execution source.
    route_child = ("import json,sys;from pathlib import Path;"
                   "raw=sys.stdin.buffer.read();p=sys.argv[1];n={'__name__':'t10_route','__file__':p};"
                   "exec(compile(raw,p,'exec',dont_inherit=True),n);"
                   "print(json.dumps(n['routes'](Path(sys.argv[2])),sort_keys=True,indent=2))")
    route = subprocess.run([sys.executable, "-I", "-B", "-c", route_child,
                            str(root / ROUTE[0]), str(root)], input=route_raw,
                           cwd=root, capture_output=True, timeout=90, check=False)
    need(route.returncode == 0, "three-lens route refused: " + route.stderr.decode(errors="replace")[-500:])
    observed_route = json.loads(route.stdout)
    retained = json.loads(selected_reader.read_pinned(root, *ROUTE_RESULT))
    need(observed_route == retained["route"] and
         observed_route["members"] == [21, 27] and
         len(observed_route["producer_consumer_questions"]) == 5 and
         set(observed_route["source_cuts"]) == {"native-O05", "current-D75", "historical-D73"},
         "selected three-lens route differs")
    query_child = ("import base64,json,sys,types;"
                   "x=json.load(sys.stdin);"
                   "p=x['runner_path'];m=types.ModuleType('secure_query');m.__file__=p;"
                   "sys.modules['secure_query']=m;"
                   "exec(compile(base64.b64decode(x['runner']),p,'exec',dont_inherit=True),m.__dict__);"
                   "p=x['verify_path'];n={'__name__':'t10_verify','__file__':p};"
                   "exec(compile(base64.b64decode(x['verify']),p,'exec',dont_inherit=True),n);"
                   "print(json.dumps(n['verify'](),sort_keys=True,indent=2))")
    payload = {"runner_path": str(root / O03_RUNNER[0]),
               "runner": base64.b64encode(runner_raw).decode(),
               "verify_path": str(root / O03_VERIFY[0]),
               "verify": base64.b64encode(verifier_raw).decode()}
    query = subprocess.run([sys.executable, "-I", "-B", "-c", query_child],
                           input=json.dumps(payload).encode(), cwd=root,
                           capture_output=True, timeout=90, check=False)
    need(query.returncode == 0, "byte-backed O03 verifier refused: " + query.stderr.decode(errors="replace")[-500:])
    observed_query = json.loads(query.stdout)
    need(observed_query == json.loads(selected_reader.read_pinned(root, *O03_RESULT)) and
         set(observed_query["scopes"]) == {"current-specialist-owner", "historical-d73-slice"} and
         observed_query["selected_governed_models"] == 0 and observed_query["authority_effect"] == "none",
         "selected O03 cold answer validation differs")
    for binding in (ROUTE, ROUTE_RESULT, O03_VERIFY, O03_RUNNER, O03_RESULT):
        selected_reader.read_pinned(root, *binding)
    return observed_route, observed_query


def selected_inputs(root=ROOT):
    selected_reader = reader(root)
    matrix = json.loads(selected_reader.read_pinned(root, *MATRIX))
    need(len(matrix["rows"]) == 29 and matrix["T10_complete"] is False, "T10 matrix changed")
    row = matrix["rows"][21]
    need(row["index"] == 21 and row["member_ref"] == "protocol:O06:three-lens-query-contract" and
         row["original_class"] == "query-contract-selection" and
         row["selected_representation"] is None and row["actual_owner_outcome"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs",
         "wrong original member or original selection changed")
    original = json.loads(selected_reader.read_pinned(root, **row["original_body_binding"]))
    disposition = json.loads(selected_reader.read_pinned(root, **row["original_disposition_binding"]))
    choice = json.loads(selected_reader.read_pinned(root, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and disposition["admission_or_runtime_use_allowed"] is False and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"],
         "original query model refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        selected_reader.read_pinned(root, **binding)
    selected_reader.read_pinned(root, *PREPARATION)
    need(original["evidence_refs"] == [b["path"] for b in row["original_target_bindings"]] + [PREPARATION[0]],
         "query model source evidence differs")
    route, query = run_consumers(root, selected_reader)
    return selected_reader, row, original, route, query


def documents(original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local three-lens query contract model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Exact local query-contract consumer; historical D73, current D75 and source-native cuts remain distinct."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local O06 three-lens query consumer",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"],
        "evidence_refs": [ROUTE[0], O03_VERIFY[0]], "challenge_route": original["challenge_route"],
        "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-O06-three-lens-query-consumer",
                    "conforms_to_schema_refs": [r.removesuffix("#") for r in original["payload"]["rule_refs"][1:]],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": ROUTE[0],
                    "environment_contract_ref": original["payload"]["contract_ref"]},
        "claim_ceiling": "Five cold producer/consumer query links and two cold-validated O03 answer scopes; no complete repository coverage."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "Three-lens consumer instance of local query model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [ROUTE[0], O03_VERIFY[0]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": ROUTE[0] + "#sha256=" + ROUTE[1]},
                    "relation_evidence_refs": [ROUTE[0], O03_VERIFY[0]]},
        "claim_ceiling": "Local classification of this exact consumer only; no original member admission."
    }
    return model, implementation, relation


def verify_documents(root, selected_reader, original, model, implementation, relation, route, query):
    for path, body in ((selected_reader.MODEL_SCHEMA, model),
                       (selected_reader.IMPLEMENTATION_SCHEMA, implementation),
                       (selected_reader.RELATION_SCHEMA, relation)):
        schema = json.loads(selected_reader.read_pinned(root, path, selected_reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(selected_reader.read_pinned(root, selected_reader.KIND,
                                                   selected_reader.SCHEMA_PINS[selected_reader.KIND]))
    need(kind["node_id"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == original["payload"]["contract_ref"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["execution_entrypoint_ref"] == ROUTE[0] and
         implementation["payload"]["environment_contract_ref"] == original["payload"]["contract_ref"] and
         implementation["payload"]["conforms_to_schema_refs"] ==
         [r.removesuffix("#") for r in original["payload"]["rule_refs"][1:]] and
         implementation["evidence_refs"] == [ROUTE[0], O03_VERIFY[0]] and
         relation["payload"]["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                                           "version_ref": IMPLEMENTATION_VERSION} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": MODEL,
                                           "version_ref": MODEL_VERSION} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                               "binding_ref": ROUTE[0] + "#sha256=" + ROUTE[1]} and
         relation["payload"]["relation_evidence_refs"] == [ROUTE[0], O03_VERIFY[0]] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": MODEL}] and
         route["source_cuts"]["current-D75"] != route["source_cuts"]["historical-D73"] and
         query["selected_governed_models"] == 0 and
         all(body["authority_effect"] == "none" and body["lifecycle_state"] == "candidate"
             for body in (model, implementation, relation)), "query model classification differs")


def build(root=ROOT):
    selected_reader, row, original, route, query = selected_inputs(root)
    model, implementation, relation = documents(original)
    verify_documents(root, selected_reader, original, model, implementation, relation, route, query)
    return {"schema_version": "lab-T10-local-three-lens-query-model-selection/v2",
            "member_index": 21, "member_ref": row["member_ref"],
            "selected_governed_model_representations": 1,
            "route_result_sha256": ROUTE_RESULT[1], "o03_verified_join_sha256": O03_RESULT[1],
            "source_cuts": route["source_cuts"],
            "route_question_count": len(route["producer_consumer_questions"]),
            "o03_cold_validated_scopes": sorted(query["scopes"]),
            "documents": {"model": model, "implementation": implementation, "typed_relation": relation},
            "code_sha256": sha(Path(__file__).read_bytes()), "original_member_admitted": False,
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "One local relation-backed query-contract model. Five three-cut producer/consumer links and two byte-backed O03 cold answer/receipt validations. No original admission, authority, full coverage or current D75 query rerun."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
