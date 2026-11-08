#!/usr/bin/env python3
"""Select one local O06 property-schema model through an actual O05 consumer."""
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
HERE = Path(__file__).resolve().parent
SHARED = Path("implementation/lab-runtime/local-host/t10-d75-model-selection-0001/select_model.py")
SHARED_SHA = "4d51b75926060a2b64ac193d8b218ebf6d150ec4352b7e387964db8e887396d8"
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
CONSUMER = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/consume_18.py",
            "sha256": "c57f738dedfc6d297ce53d992d3fe17caee70a32610bba7f66537648612ec6a2"}
DEPENDENCY = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/consume.py",
              "sha256": "28938e7417284aeb94ca0b14eee1d4276fc4289d5181d372bc05985ffd36870e"}
CONSUMER_RESULT = {"path": "implementation/lab-runtime/local-host/t10-control-consumer-0001/RESULT-18.json",
                   "sha256": "ee99a639d070075abc80fdf6a6bff58e95f9cb6943f46673d5d1c91957f10c20"}
CONTROL = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/18-closed-native-property-schemas.json",
           "sha256": "9a63a0199e2d632f05ffc6a089803579508722d5e3cb86de70371abe58d79916"}
PREPARATION = {"path": "implementation/lab-ontology/candidates/v1/review/O06/packages/0001/preparation.json",
               "sha256": "55f56db53ff17fa935342048f145862db67908f8cc97324438d93237de6e1762"}
MIGRATION_MANIFEST = {"path": "implementation/lab-ontology/candidates/v1/migration/candidate/0001/manifest.json",
                      "sha256": "d4228ac71001acc4061431882dfa8c0155edf87d859bbf84527307580cb81214"}
SOURCE_SELECTION = {"path": "implementation/lab-ontology/candidates/v1/migration/source-selection.json",
                    "sha256": "0efe0f6a59c8339211feb919757f3ec7541e044cb9ce0fd7c4a4f6ea154c7aa7"}
WORKER = {"path": "implementation/lab-runtime/local-host/t10-native-property-model-selection-0001/consumer_worker.py",
          "sha256": "a7bce14a292fe19c0aa75b65741bd866531ef64ea35713da498fe4ed37427121"}
SCHEMAS = (
    {"path": "implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/node-properties.schema.json",
     "sha256": "84161abdd2553b99c8cfc222aee53204fd8106b3b36abc7a4728b846628ad9bb"},
    {"path": "implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/relation-properties.schema.json",
     "sha256": "029199807dc5204e3a9028ddb48d361a3707ab4afd1fffd80a0f69301e2f5e34"},
)
MODEL = "governed-model:lab-local:O06-native-property-schemas"
IMPLEMENTATION = "implementation:lab-local:O06-property-consumer"
RELATION = "typed-relation:lab-local:O06-property-consumer-instance"
MODEL_VERSION = MODEL + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION + "@local.1"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def import_source_bytes(path, expected):
    path = path.absolute()
    for item in (path, *path.parents):
        mode = item.lstat().st_mode
        need(not stat.S_ISLNK(mode) and (item != path or stat.S_ISREG(mode)),
             "linked or nonregular import origin")
    raw = path.read_bytes()
    need(digest(raw) == expected, "changed import source")
    return raw


def shared(root=ROOT):
    source = root / SHARED
    import_source_bytes(source, SHARED_SHA)
    spec = importlib.util.spec_from_file_location("t10_local_pin_reader", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.read_pinned(root, SHARED, SHARED_SHA)
    return module


def selected_inputs(root=ROOT):
    reader = shared(root)
    matrix = json.loads(reader.read_pinned(root, **MATRIX))
    need(len(matrix["rows"]) == 29 and matrix["semantically_grounded_selected_representations"] == 0,
         "original T10 matrix changed")
    row = matrix["rows"][18]
    need(row["index"] == 18 and row["member_ref"] == "protocol:O06:closed-native-property-schemas" and
         row["selected_representation"] is None and tuple(row["original_target_bindings"]) == SCHEMAS,
         "wrong original property-schema member")
    original = json.loads(reader.read_pinned(root, **row["original_body_binding"]))
    disposition = json.loads(reader.read_pinned(root, **row["original_disposition_binding"]))
    choice = json.loads(reader.read_pinned(root, **row["review_choice_binding"]))
    need(original["relation_refs"] == [] and disposition["admission_or_runtime_use_allowed"] is False and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"],
         "original property-schema refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        reader.read_pinned(root, **binding)
    reader.read_pinned(root, **PREPARATION)
    need(original["evidence_refs"] == [b["path"] for b in SCHEMAS] + [PREPARATION["path"]],
         "original model evidence differs")
    control = json.loads(reader.read_pinned(root, **CONTROL))
    need(control["member_ref"] == row["member_ref"] and
         control["control_kind"] == "property-schema-selection" and
         control["control_bindings"] == row["original_target_bindings"] and
         control["selected_choice"] is None and control["native_or_runtime_use_allowed"] is False,
         "selected O06 control differs")
    for binding in (CONSUMER, DEPENDENCY, CONSUMER_RESULT, MIGRATION_MANIFEST, SOURCE_SELECTION, WORKER):
        reader.read_pinned(root, **binding)
    retained = json.loads(reader.read_pinned(root, **CONSUMER_RESULT))
    process = subprocess.run([sys.executable, "-I", "-B", str(root / WORKER["path"]),
                              str(root), CONSUMER["sha256"], DEPENDENCY["sha256"]],
                             cwd=root, capture_output=True, check=False, timeout=90)
    need(process.returncode == 0,
         "actual O05 property consumer refused: " + process.stderr.decode(errors="replace")[:250])
    actual = json.loads(process.stdout)
    need(actual == retained and actual["result"] == "PASS" and
         actual["member_ref"] == row["member_ref"] and
         actual["migration_manifest_sha256"] == MIGRATION_MANIFEST["sha256"] and
         actual["source_selection_sha256"] == SOURCE_SELECTION["sha256"] and
         len(actual["event_sha256"]) == 2,
         "O05 native consumer result differs")
    for binding in (CONSUMER, DEPENDENCY, CONSUMER_RESULT, MIGRATION_MANIFEST, SOURCE_SELECTION, WORKER):
        reader.read_pinned(root, **binding)
    reader.read_pinned(root, SHARED, SHARED_SHA)
    return reader, row, original, actual


def documents(original):
    model = deepcopy(original)
    model["node_id"] = MODEL
    model["name"] = "Local O06 native property-schema model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}]
    model["claim_ceiling"] = "Local model of exact O06 node/relation property schemas; no native or original admission."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION,
        "kind": "implementation", "name": "Local historical O05 property validator",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"],
        "evidence_refs": [CONSUMER["path"], MIGRATION_MANIFEST["path"], SOURCE_SELECTION["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL}],
        "payload": {"implementation_kind": "local-O05-native-property-validator",
                    "conforms_to_schema_refs": [binding["path"] for binding in SCHEMAS],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": CONSUMER["path"],
                    "environment_contract_ref": CONTROL["path"]},
        "claim_ceiling": "Exact consumer of one historical O05 native node/relation pair and source witnesses; no current runtime qualification."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION,
        "kind": "typed-relation", "name": "O05 validator instance of local O06 property model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [CONSUMER["path"], SOURCE_SELECTION["path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]},
                    "relation_evidence_refs": [CONSUMER["path"], SOURCE_SELECTION["path"]]},
        "claim_ceiling": "Local classification of the historical O05 property consumer only; no admission or global edge."
    }
    return model, implementation, relation


def verify_documents(root, reader, model, implementation, relation, actual):
    for path, body in ((reader.MODEL_SCHEMA, model), (reader.IMPLEMENTATION_SCHEMA, implementation),
                       (reader.RELATION_SCHEMA, relation)):
        Draft202012Validator(json.loads(reader.read_pinned(root, path, reader.SCHEMA_PINS[path]))).validate(body)
    kind = json.loads(reader.read_pinned(root, reader.KIND, reader.SCHEMA_PINS[reader.KIND]))
    payload = relation["payload"]
    need(actual["result"] == "PASS" and actual["migration_manifest_sha256"] == MIGRATION_MANIFEST["sha256"] and
         actual["source_selection_sha256"] == SOURCE_SELECTION["sha256"] and len(actual["event_sha256"]) == 2 and
         kind["node_id"] == payload["relation_kind_ref"] == "relation.instance-of" and
         {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]} in
         kind["payload"]["allowed_endpoint_pairs"] and
         payload["source"] == {"kind": "implementation", "ref": IMPLEMENTATION,
                               "version_ref": IMPLEMENTATION_VERSION} and
         payload["target"] == {"kind": "governed-model", "ref": MODEL, "version_ref": MODEL_VERSION} and
         payload["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": CONSUMER["path"] + "#sha256=" + CONSUMER["sha256"]} and
         model["node_id"] == MODEL and model["payload"]["version_ref"] == MODEL_VERSION and
         model["payload"]["contract_ref"] == SCHEMAS[0]["path"] and
         model["payload"]["model_kind"] == "exact-original-control-rules:O06:closed-native-property-schemas" and
         model["payload"]["rule_refs"] == [b["path"] + "#" for b in SCHEMAS] and
         model["evidence_refs"] == [b["path"] for b in SCHEMAS] + [PREPARATION["path"]] and
         implementation["node_id"] == IMPLEMENTATION and
         implementation["payload"]["execution_entrypoint_ref"] == CONSUMER["path"] and
         implementation["payload"]["conforms_to_schema_refs"] == [b["path"] for b in SCHEMAS] and
         implementation["evidence_refs"] == [CONSUMER["path"], MIGRATION_MANIFEST["path"], SOURCE_SELECTION["path"]] and
         relation["evidence_refs"] == [CONSUMER["path"], SOURCE_SELECTION["path"]] and
         payload["relation_evidence_refs"] == [CONSUMER["path"], SOURCE_SELECTION["path"]] and
         model["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                     "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION}] and
         implementation["relation_refs"] == [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                                              "counterpart_kind": "governed-model", "counterpart_ref": MODEL}] and
         all(body["lifecycle_state"] == "candidate" and body["authority_effect"] == "none"
             for body in (model, implementation, relation)),
         "O05 property model classification or consumer binding differs")


def build(root=ROOT):
    reader, row, original, actual = selected_inputs(root)
    model, implementation, relation = documents(original)
    verify_documents(root, reader, model, implementation, relation, actual)
    return {"schema_version": "lab-T10-local-O05-property-model-selection/v1", "member_index": 18,
            "member_ref": row["member_ref"], "selected_governed_model_representations": 1,
            "consumer_result": actual,
            "documents": {"model": model, "implementation": implementation, "typed_relation": relation},
            "code_sha256": digest(Path(__file__).read_bytes()), "authority_effect": "none",
            "original_member_admitted": False, "T10_complete": False,
            "claim_ceiling": "One local relation-backed O06 property model on historical O05 native node/relation evidence. No current native run, global relation, original admission or general qualification."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
