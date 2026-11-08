#!/usr/bin/env python3
"""One local C10 Product mapping model over a pinned candidate producer/consumer join."""
from __future__ import annotations

import base64
from copy import deepcopy
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
CONSUMER = ("implementation/lab-runtime/local-host/t10-product-mapping-model-selection-0002/consumer.py",
            "cfda0e733fc36ef82c0cb0339adeea2b5a43ec37737c70184453a4cc08f5a6b9")
PREFIX = "authority/instance-packs/candidates/0001-cyberalchemy-lab-reference-slice/"
PACK = (PREFIX + "pack.json", "2bf03927d8467bda5518c4eead02afcc1f0d76187e882aff96e726484036b3f0")
PRODUCT = (PREFIX + "instances/artifacts/product.json", "c25e4cf258e3ce23ae8ba56536194b39810b41662d89fe3af5f10900659125f1")
VALIDATION = (PREFIX + "receipts/validation.json", "f3464c6704b2cdaed371fe6c6a1bd8ad283ecc48e328c1ff1aeca435389c2bbf")
BUILDER = (PREFIX + "build.py", "6782816a249e7217cf9fb0b62d6674fc56751483af0fc666e76a150ca574c504")
VALIDATOR = (PREFIX + "validate.py", "8bac1ccc41b6ea651a7c9d9f70516ceb2c8d3f856cdb7c452c41bb94e03a6da8")
MODEL = "governed-model:lab-local:C10-product-identity-endpoint"
IMPLEMENTATION = "implementation:lab-local:C10-product-endpoint-consumer"
RELATION = "typed-relation:lab-local:C10-product-consumer-instance"
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
    module = types.ModuleType("t10_pinned_product_reader")
    module.__file__ = str(source)
    exec(compile(raw, str(source), "exec", dont_inherit=True), module.__dict__)
    module.read_pinned(root, SHARED, SHARED_SHA)
    return module


def run_consumer(root, selected_reader, proposal, schema, pack, product, validation, schema_binding):
    raw = selected_reader.read_pinned(root, *CONSUMER)
    payload = {"proposal": proposal, "schema": schema, "pack": pack, "product": product,
               "receipt": validation, "product_binding": {"path": PRODUCT[0], "sha256": PRODUCT[1]},
               "schema_binding": schema_binding, "pack_sha256": PACK[1]}
    child = ("import base64,json,sys;v=json.load(sys.stdin);"
             "p=sys.argv[1];n={'__name__':'t10_product_consumer','__file__':p};"
             "exec(compile(base64.b64decode(v['code']),p,'exec',dont_inherit=True),n);"
             "print(json.dumps(n['consume'](v['payload']),sort_keys=True,indent=2))")
    process = subprocess.run([sys.executable, "-I", "-B", "-c", child, str(root / CONSUMER[0])],
                             input=json.dumps({"code": base64.b64encode(raw).decode(), "payload": payload}).encode(),
                             cwd=root, capture_output=True, timeout=30, check=False)
    need(process.returncode == 0,
         "selected Product consumer refused: " + process.stderr.decode(errors="replace")[-500:])
    observed = json.loads(process.stdout)
    need(observed["candidate_endpoint_ref"] == "product:cyberalchemy-lab" and
         observed["candidate_endpoint_version_ref"] == "product:cyberalchemy-lab@candidate.1" and
         observed["project_identity_distinct"] is True and
         observed["general_alias_admitted"] is False and observed["instance_admitted"] is False and
         observed["authority_effect"] == "none", "Product consumer result differs")
    selected_reader.read_pinned(root, *CONSUMER)
    return observed


def selected_inputs(root=ROOT):
    selected_reader = reader(root)
    matrix = json.loads(selected_reader.read_pinned(root, *MATRIX))
    need(len(matrix["rows"]) == 29 and matrix["T10_complete"] is False, "T10 matrix changed")
    row = matrix["rows"][1]
    need(row["index"] == 1 and row["member_ref"] == "protocol:C10:mapping-product" and
         row["original_class"] == "semantic-mappings" and
         row["selected_representation"] is None and row["actual_owner_outcome"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs",
         "wrong original Product member or selection changed")
    original = json.loads(selected_reader.read_pinned(root, **row["original_body_binding"]))
    disposition = json.loads(selected_reader.read_pinned(root, **row["original_disposition_binding"]))
    choice = json.loads(selected_reader.read_pinned(root, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and disposition["original_index"] == choice["original_index"] == 1 and
         disposition["original_body_binding"] == row["original_body_binding"] and
         disposition["admission_or_runtime_use_allowed"] is False and
         choice["admission_or_runtime_use_allowed"] is False and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"],
         "original Product member refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        selected_reader.read_pinned(root, **binding)
    need(original["evidence_refs"] == [b["path"] for b in row["original_target_bindings"]] +
         ["implementation/lab-review/candidates/v1/packages/0001/preparation.json"],
         "original Product target evidence differs")
    impact = json.loads(selected_reader.read_pinned(root, **row["original_target_bindings"][0]))
    schema_binding = row["original_target_bindings"][2]
    schema = json.loads(selected_reader.read_pinned(root, **schema_binding))
    proposal = impact["endpoint_proposals"][1]
    need(proposal["schema_binding"] == schema_binding and impact["authority_effect"] == "none",
         "Product proposal/schema binding differs")
    pack = json.loads(selected_reader.read_pinned(root, *PACK))
    product = json.loads(selected_reader.read_pinned(root, *PRODUCT))
    validation = json.loads(selected_reader.read_pinned(root, *VALIDATION))
    for binding in (BUILDER, VALIDATOR):
        selected_reader.read_pinned(root, *binding)
    observed = run_consumer(root, selected_reader, proposal, schema, pack, product, validation, schema_binding)
    for binding in (PACK, PRODUCT, VALIDATION, BUILDER, VALIDATOR):
        selected_reader.read_pinned(root, *binding)
    return selected_reader, row, original, schema_binding, observed


def documents(original, schema_binding):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local C10 Product identity mapping model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Exact candidate reference-slice Product Identity/v2 selector and one Product endpoint join; no general alias or admission."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local Product endpoint mapping consumer",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": original["owner_ref"],
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER[0], PACK[0], PRODUCT[0], VALIDATION[0]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-C10-Product-endpoint-consumer",
                    "conforms_to_schema_refs": [schema_binding["path"]],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": CONSUMER[0],
                    "environment_contract_ref": original["payload"]["contract_ref"]},
        "claim_ceiling": "One isolated, captured-byte consumer joins a schema-valid candidate Product carrier to one candidate pack endpoint; no global mapping."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "Product consumer instance of local mapping model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": original["owner_ref"],
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER[0], PACK[0], VALIDATION[0]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER[0] + "#sha256=" + CONSUMER[1]},
                    "relation_evidence_refs": [CONSUMER[0], PACK[0], VALIDATION[0]]},
        "claim_ceiling": "Local classification of this exact consumer only; no original member admission."
    }
    return model, implementation, relation


def verify_documents(root, selected_reader, original, schema_binding, observed, model, implementation, relation):
    for path, body in ((selected_reader.MODEL_SCHEMA, model),
                       (selected_reader.IMPLEMENTATION_SCHEMA, implementation),
                       (selected_reader.RELATION_SCHEMA, relation)):
        schema = json.loads(selected_reader.read_pinned(root, path, selected_reader.SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(selected_reader.read_pinned(root, selected_reader.KIND,
                                                   selected_reader.SCHEMA_PINS[selected_reader.KIND]))
    expected_model_link = {"relation_kind_ref": "relation.instance-of", "direction": "target",
                           "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}
    expected_implementation_link = {"relation_kind_ref": "relation.instance-of", "direction": "source",
                                    "counterpart_kind": "governed-model", "counterpart_ref": MODEL}
    expected_relation_evidence = [CONSUMER[0], PACK[0], VALIDATION[0]]
    need(kind["node_id"] == "relation.instance-of" and
         {"source_kind": "implementation", "target_kind": "governed-model"} in
         kind["payload"]["allowed_endpoint_pairs"] and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == original["payload"]["contract_ref"] and
         model["payload"]["model_kind"] == original["payload"]["model_kind"] and
         model["payload"]["rule_refs"] == original["payload"]["rule_refs"] and
         model["evidence_refs"] == original["evidence_refs"] and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["implementation_kind"] == "local-C10-Product-endpoint-consumer" and
         implementation["payload"]["execution_entrypoint_ref"] == CONSUMER[0] and
         implementation["payload"]["conforms_to_schema_refs"] == [schema_binding["path"]] and
         implementation["payload"]["environment_contract_ref"] == original["payload"]["contract_ref"] and
         implementation["evidence_refs"] == [CONSUMER[0], PACK[0], PRODUCT[0], VALIDATION[0]] and
         relation["node_id"] == RELATION and relation["relation_refs"] == [] and
         relation["payload"]["relation_kind_ref"] == kind["node_id"] and
         relation["payload"]["relation_lifecycle_state"] == "candidate" and
         relation["payload"]["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                                           "version_ref": IMPLEMENTATION_VERSION} and
         relation["payload"]["target"] == {"kind": "governed-model", "ref": MODEL,
                                           "version_ref": MODEL_VERSION} and
         relation["payload"]["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                               "binding_ref": CONSUMER[0] + "#sha256=" + CONSUMER[1]} and
         relation["evidence_refs"] == expected_relation_evidence and
         relation["payload"]["relation_evidence_refs"] == expected_relation_evidence and
         model["relation_refs"] == [expected_model_link] and
         implementation["relation_refs"] == [expected_implementation_link] and
         observed["general_alias_admitted"] is False and
         all(body["authority_effect"] == "none" and body["lifecycle_state"] == "candidate" and
             body["owner_ref"] == original["owner_ref"] and body["scope_ref"] == original["scope_ref"]
             for body in (model, implementation, relation)), "Product mapping model classification differs")


def build(root=ROOT):
    selected_reader, row, original, schema_binding, observed = selected_inputs(root)
    model, implementation, relation = documents(original, schema_binding)
    verify_documents(root, selected_reader, original, schema_binding, observed, model, implementation, relation)
    return {"schema_version": "lab-T10-local-Product-mapping-model-selection/v2",
            "member_index": 1, "member_ref": row["member_ref"],
            "selected_governed_model_representations": 1,
            "producer_pack_binding": {"path": PACK[0], "sha256": PACK[1]},
            "producer_validation_binding": {"path": VALIDATION[0], "sha256": VALIDATION[1]},
            "consumer_binding": {"path": CONSUMER[0], "sha256": CONSUMER[1]},
            "observed": observed,
            "documents": {"model": model, "implementation": implementation, "typed_relation": relation},
            "code_sha256": sha(Path(__file__).read_bytes()),
            "original_member_admitted": False, "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "One local Product Identity/v2 mapping model over a retained candidate reference-slice producer and an isolated captured-byte consumer. Exact Product candidate identity/version only; no general alias, owner outcome, original admission or T10 completion."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
