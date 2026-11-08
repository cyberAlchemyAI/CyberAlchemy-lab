#!/usr/bin/env python3
"""Select one local relation-backed W08 workflow-run validation model."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "implementation/lab-runtime/local-host/t10-d75-model-selection-0001/select_model.py"
PREDECESSOR_SHA = "4d51b75926060a2b64ac193d8b218ebf6d150ec4352b7e387964db8e887396d8"
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
CONSUMER = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/consume.py",
            "sha256": "28938e7417284aeb94ca0b14eee1d4276fc4289d5181d372bc05985ffd36870e"}
CONSUMER_RESULT = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/RESULT.json",
                   "sha256": "3efce26a0a5687a4bf17871aae4ef7cf81a88b11e835b7a253f0fe9d22cbbfd8"}
T31_RESULT = {"path": "implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/RESULT.json",
              "sha256": "c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445"}
RUN = {"path": "implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/research/workflow-run.json",
       "sha256": "bd2f746854fac130e355425bbb34a9c1e9644c650daa4649445cc1a81ed1db5e"}
CONTROL = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/14-workflow-run-schemas.json",
           "sha256": "4f95040ffb32055b6cbe24c5509ae4d8b00ab42d1b11ca0ffd4e8e0a9bf20b2c"}
PREPARATION = {"path": "implementation/lab-workflows/candidates/v1/review/W08/packages/0001/preparation.json",
               "sha256": "590bcbfb134fccddd2e38341dc94c9f67e2ac83b87c4bceb8c9cf488813d303a"}
MODEL = "governed-model:lab-local:W08-workflow-run-validation"
IMPLEMENTATION = "implementation:lab-local:W08-workflow-run-consumer"
RELATION = "typed-relation:lab-local:W08-workflow-run-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def base():
    need(digest(PREDECESSOR.read_bytes()) == PREDECESSOR_SHA, "changed shared pin reader")
    spec = importlib.util.spec_from_file_location("t10_selected_model_reader", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_inputs(root=ROOT):
    shared = base()
    matrix = json.loads(shared.read_pinned(root, **MATRIX))
    need(len(matrix["rows"]) == 29 and matrix["semantically_grounded_selected_representations"] == 0,
         "original T10 matrix changed")
    row = matrix["rows"][14]
    need(row["index"] == 14 and row["member_ref"] == "protocol:W08:workflow-run-schemas" and
         row["selected_representation"] is None and row["specific_missing_proof"].startswith("Two exact workflow-run schemas"),
         "wrong original member")
    need(tuple(row["original_target_bindings"]) == MATRIX_SCHEMA_BINDINGS,
         "original W08 schema selection differs")
    original = json.loads(shared.read_pinned(root, **row["original_body_binding"]))
    disposition = json.loads(shared.read_pinned(root, **row["original_disposition_binding"]))
    choice = json.loads(shared.read_pinned(root, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and not disposition["admission_or_runtime_use_allowed"] and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"],
         "original refusal changed")
    for binding in row["original_target_bindings"]:
        shared.read_pinned(root, **binding)
    for binding in row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        shared.read_pinned(root, **binding)
    shared.read_pinned(root, **PREPARATION)
    need(original["evidence_refs"] == [binding["path"] for binding in row["original_target_bindings"]] +
         [PREPARATION["path"]], "original model evidence differs")
    control = json.loads(shared.read_pinned(root, **CONTROL))
    need(control["member_ref"] == row["member_ref"] and
         control["control_kind"] == "validation-contract" and
         control["control_bindings"] == row["original_target_bindings"] and
         control["selected_choice"] is None and control["native_or_runtime_use_allowed"] is False,
         "workflow control differs")
    for binding in (CONSUMER, CONSUMER_RESULT, T31_RESULT, RUN):
        shared.read_pinned(root, **binding)
    retained = json.loads(shared.read_pinned(root, **CONSUMER_RESULT))
    command = [sys.executable, "-I", "-B", str(root / CONSUMER["path"])]
    process = subprocess.run(command, cwd=root, capture_output=True, timeout=60, check=False)
    need(process.returncode == 0, "actual workflow consumer refused: " +
         process.stderr.decode(errors="replace")[:250])
    actual = json.loads(process.stdout)
    need(actual == retained and actual["result"] == "PASS" and
         actual["member_ref"] == row["member_ref"] and
         actual["source_result_sha256"] == T31_RESULT["sha256"] and
         actual["source_run_sha256"] == RUN["sha256"], "workflow consumer result differs")
    for binding in (CONSUMER, CONSUMER_RESULT, T31_RESULT, RUN):
        shared.read_pinned(root, **binding)
    need(digest(PREDECESSOR.read_bytes()) == PREDECESSOR_SHA, "changed shared pin reader")
    return shared, row, original, actual


def documents(original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local W08 workflow-run validation model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Local model of the exact W08 workflow-run validation controls; no schema or original member admission."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local exact workflow-run validation consumer",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"],
        "evidence_refs": [CONSUMER["path"], RUN["path"], T31_RESULT["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-exact-W08-workflow-run-validator",
                    "conforms_to_schema_refs": [binding["path"] for binding in MATRIX_SCHEMA_BINDINGS],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": CONSUMER["path"],
                    "environment_contract_ref": CONTROL["path"]},
        "claim_ceiling": "One actual candidate WorkflowRun validated against exact W08 controls and T31 producer lineage; no general protocol admission."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "W08 workflow consumer instance of local validation model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER["path"], RUN["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]},
                    "relation_evidence_refs": [CONSUMER["path"], RUN["path"]]},
        "claim_ceiling": "Local classification of the exact validating consumer only; no conformance or authority inferred."
    }
    return model, implementation, relation


MATRIX_SCHEMA_BINDINGS = (
    {"path": "implementation/lab-workflows/candidates/v1/review/W08/packages/0001/postimages/schemas/common.schema.json",
     "sha256": "d41f2b8811d0cbea6845f13f1c586665afe03d49ddf7c0974d0632bb3ceded74"},
    {"path": "implementation/lab-workflows/candidates/v1/review/W08/packages/0001/postimages/schemas/workflow-run.schema.json",
     "sha256": "257df967d6c5dd1ac4f7f38ddd6833e803e48bfe9289fce51ee5ebc63d262a6f"},
)
MODEL_RULES = [binding["path"] + "#" for binding in MATRIX_SCHEMA_BINDINGS]
MODEL_EVIDENCE = [binding["path"] for binding in MATRIX_SCHEMA_BINDINGS] + [
    PREPARATION["path"]]


def verify_documents(root, shared, model, implementation, relation, observed):
    for path, body in ((shared.MODEL_SCHEMA, model), (shared.IMPLEMENTATION_SCHEMA, implementation),
                       (shared.RELATION_SCHEMA, relation)):
        schema = json.loads(shared.read_pinned(root, path, shared.SCHEMA_PINS[path]))
        Draft202012Validator(schema).validate(body)
    kind = json.loads(shared.read_pinned(root, shared.KIND, shared.SCHEMA_PINS[shared.KIND]))
    payload = relation["payload"]
    need(observed["result"] == "PASS" and observed["source_run_sha256"] == RUN["sha256"] and
         observed["source_result_sha256"] == T31_RESULT["sha256"] and
         kind["node_id"] == payload["relation_kind_ref"] == "relation.instance-of" and
         {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]} in
         kind["payload"]["allowed_endpoint_pairs"] and
         payload["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION} and
         payload["target"] == {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION} and
         payload["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]} and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == MATRIX_SCHEMA_BINDINGS[0]["path"] and
         model["payload"]["model_kind"] == "exact-original-control-rules:W08:workflow-run-schemas" and
         model["payload"]["rule_refs"] == MODEL_RULES and
         model["evidence_refs"] == MODEL_EVIDENCE and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["execution_entrypoint_ref"] == CONSUMER["path"] and
         implementation["payload"]["conforms_to_schema_refs"] == [b["path"] for b in MATRIX_SCHEMA_BINDINGS] and
         implementation["evidence_refs"] == [CONSUMER["path"], RUN["path"], T31_RESULT["path"]] and
         relation["evidence_refs"] == [CONSUMER["path"], RUN["path"]] and
         payload["relation_evidence_refs"] == [CONSUMER["path"], RUN["path"]] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": MODEL}] and
         all(x["authority_effect"] == "none" and x["lifecycle_state"] == "candidate"
             for x in (model, implementation, relation)),
         "workflow model classification or producer binding differs")


def build(root=ROOT):
    shared, row, original, observed = selected_inputs(root)
    model, implementation, relation = documents(original)
    verify_documents(root, shared, model, implementation, relation, observed)
    return {"schema_version": "lab-T10-local-W08-model-selection/v1", "member_index": 14,
            "member_ref": row["member_ref"], "selected_governed_model_representations": 1,
            "consumer_result": observed, "documents": {"model": model,
                                                       "implementation": implementation,
                                                       "typed_relation": relation},
            "code_sha256": digest(Path(__file__).read_bytes()), "authority_effect": "none",
            "original_member_admitted": False, "T10_complete": False,
            "claim_ceiling": "One local relation-backed model of exact W08 workflow-run validation, grounded in actual consumer and T31 output lineage. No original admission, general workflow validation, or effect."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
