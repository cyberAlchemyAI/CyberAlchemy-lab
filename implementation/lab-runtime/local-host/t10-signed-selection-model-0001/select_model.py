#!/usr/bin/env python3
"""Select a local model for the executable historical W07 signature consumer."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
SHARED = Path("implementation/lab-runtime/local-host/t10-d75-model-selection-0001/select_model.py")
SHARED_SHA = "4d51b75926060a2b64ac193d8b218ebf6d150ec4352b7e387964db8e887396d8"
IMPLEMENTATION_SCHEMA = "authority/artifact-types/implementation/v1/schema.json"
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
CONSUMER = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/consume_15.py",
            "sha256": "bb186abd5a3ba1abb45ac109cd32c361161abb6f2d6031c63419f3a76a014867"}
RESULT = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/RESULT-15.json",
          "sha256": "958f590a4cd4d6628681d9c40c6d661f517e006f7e657bd0de29522abf9bc816"}
CONTROL = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/15-signed-integration-selection.json",
           "sha256": "6c8686bd72621ee8d241148bfe96f7e3235df107ca3e05617c2c00fb56d777cf"}
SELECTION = {"path": "implementation/lab-workflows/candidates/v1/tests/signed_integration/selection.json",
             "sha256": "6e5d8e24325e45c6801d64161b23539190c78befb2bf9d8f1a9d0f2819ffb1db"}
W07 = {"path": "implementation/lab-workflows/candidates/v1/receipts/integration/W07/0004.json",
       "sha256": "3e40e0cb64a479b5546a30c069dc009c950b78a8a6357e0bd58b8e92ea840203"}
PREPARATION = {"path": "implementation/lab-workflows/candidates/v1/review/W08/packages/0001/preparation.json",
               "sha256": "590bcbfb134fccddd2e38341dc94c9f67e2ac83b87c4bceb8c9cf488813d303a"}
MODEL = "governed-model:lab-local:W07-signed-selection"
IMPLEMENTATION = "implementation:lab-local:W07-signed-selection-consumer"
RELATION = "typed-relation:lab-local:W07-signed-selection-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def import_bytes(path, expected):
    path = path.absolute()
    for item in (path, *path.parents):
        mode = item.lstat().st_mode
        need(not stat.S_ISLNK(mode) and (item != path or stat.S_ISREG(mode)),
             "linked or nonregular import origin")
    raw = path.read_bytes()
    need(digest(raw) == expected, "changed import source")
    return raw


def reader(root=ROOT):
    source = root / SHARED
    import_bytes(source, SHARED_SHA)
    spec = importlib.util.spec_from_file_location("t10_local_signed_pin_reader", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.read_pinned(root, SHARED, SHARED_SHA)
    return module


def selected_inputs(root=ROOT):
    pins = reader(root)
    matrix = json.loads(pins.read_pinned(root, **MATRIX))
    need(len(matrix["rows"]) == 29 and matrix["semantically_grounded_selected_representations"] == 0,
         "original T10 matrix changed")
    row = matrix["rows"][15]
    need(row["index"] == 15 and row["member_ref"] == "review:W07:signed-integration-selection" and
         row["selected_representation"] is None and row["original_target_bindings"] == [SELECTION],
         "wrong original signed-selection member")
    original = json.loads(pins.read_pinned(root, **row["original_body_binding"]))
    disposition = json.loads(pins.read_pinned(root, **row["original_disposition_binding"]))
    choice = json.loads(pins.read_pinned(root, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and disposition["admission_or_runtime_use_allowed"] is False and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"],
         "original signed-selection refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        pins.read_pinned(root, **binding)
    pins.read_pinned(root, **PREPARATION)
    need(original["evidence_refs"] == [SELECTION["path"], PREPARATION["path"]] and
         row["original_evidence_bindings"] == [W07], "original signed evidence differs")
    control = json.loads(pins.read_pinned(root, **CONTROL))
    need(control["member_ref"] == row["member_ref"] and
         control["control_kind"] == "verification-selection" and
         control["control_bindings"] == [SELECTION] and
         control["selected_choice"] is None and control["native_or_runtime_use_allowed"] is False,
         "signed selection control differs")
    for binding in (CONSUMER, RESULT, W07):
        pins.read_pinned(root, **binding)
    retained = json.loads(pins.read_pinned(root, **RESULT))
    import_bytes(root / CONSUMER["path"], CONSUMER["sha256"])
    process = subprocess.run([sys.executable, "-I", "-B", str(root / CONSUMER["path"])],
                             cwd=root, capture_output=True, check=False, timeout=90)
    need(process.returncode == 0,
         "actual signed W07 consumer refused: " + process.stderr.decode(errors="replace")[:250])
    actual = json.loads(process.stdout)
    need(actual == retained and actual["result"] == "PASS" and actual["case_count"] == 4 and
         actual["member_ref"] == row["member_ref"] and
         actual["selection_sha256"] == SELECTION["sha256"] and
         actual["receipt_sha256"] == W07["sha256"] and
         [item["domain"] for item in actual["signature_verified_witnesses"]] == ["engineering", "research"],
         "signed W07 consumer result differs")
    for binding in (CONSUMER, RESULT, W07):
        pins.read_pinned(root, **binding)
    import_bytes(root / CONSUMER["path"], CONSUMER["sha256"])
    pins.read_pinned(root, SHARED, SHARED_SHA)
    return pins, row, original, actual


def documents(original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local W07 signed selection model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Local model of exact historical W07 signed selection; no original or current admission."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local historical W07 signed-selection verifier",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER["path"], SELECTION["path"], W07["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-historical-W07-signed-selection-verifier",
                    "conforms_to_schema_refs": [IMPLEMENTATION_SCHEMA],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": CONSUMER["path"], "environment_contract_ref": CONTROL["path"]},
        "claim_ceiling": "Four historical W07 cases and two signatures verified; no current runtime conformance or human benefit."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "W07 verifier instance of local signed selection model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER["path"], W07["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]},
                    "relation_evidence_refs": [CONSUMER["path"], W07["path"]]},
        "claim_ceiling": "Local classification of the historical signed-selection consumer only; no admission or authority."
    }
    return model, implementation, relation


def verify_documents(root, pins, model, implementation, relation, actual):
    for path, body in ((pins.MODEL_SCHEMA, model), (pins.IMPLEMENTATION_SCHEMA, implementation),
                       (pins.RELATION_SCHEMA, relation)):
        Draft202012Validator(json.loads(pins.read_pinned(root, path, pins.SCHEMA_PINS[path]))).validate(body)
    kind = json.loads(pins.read_pinned(root, pins.KIND, pins.SCHEMA_PINS[pins.KIND]))
    payload = relation["payload"]
    need(actual["result"] == "PASS" and actual["case_count"] == 4 and
         actual["receipt_sha256"] == W07["sha256"] and
         [r["domain"] for r in actual["signature_verified_witnesses"]] == ["engineering", "research"] and
         kind["node_id"] == payload["relation_kind_ref"] == "relation.instance-of" and
         {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]} in
         kind["payload"]["allowed_endpoint_pairs"] and
         payload["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION} and
         payload["target"] == {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION} and
         payload["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]} and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == SELECTION["path"] and
         model["payload"]["model_kind"] == "exact-original-control-rules:W07:signed-integration-selection" and
         model["payload"]["rule_refs"] == [SELECTION["path"] + "#"] and
         model["evidence_refs"] == [SELECTION["path"], PREPARATION["path"]] and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["execution_entrypoint_ref"] == CONSUMER["path"] and
         implementation["payload"]["conforms_to_schema_refs"] == [IMPLEMENTATION_SCHEMA] and
         implementation["evidence_refs"] == [CONSUMER["path"], SELECTION["path"], W07["path"]] and
         relation["evidence_refs"] == [CONSUMER["path"], W07["path"]] and
         payload["relation_evidence_refs"] == [CONSUMER["path"], W07["path"]] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": MODEL}] and
         all(x["lifecycle_state"] == "candidate" and x["authority_effect"] == "none"
             for x in (model, implementation, relation)),
         "signed selection model classification or consumer evidence differs")


def build(root=ROOT):
    pins, row, original, actual = selected_inputs(root)
    model, implementation, relation = documents(original)
    verify_documents(root, pins, model, implementation, relation, actual)
    return {"schema_version": "lab-T10-local-W07-signed-model-selection/v1", "member_index": 15,
            "member_ref": row["member_ref"], "selected_governed_model_representations": 1,
            "consumer_result": actual,
            "documents": {"model": model, "implementation": implementation, "typed_relation": relation},
            "code_sha256": digest(Path(__file__).read_bytes()), "authority_effect": "none",
            "original_member_admitted": False, "T10_complete": False,
            "claim_ceiling": "One local relation-backed historical W07 signed selection model. No current runtime verification, original admission or human benefit."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
