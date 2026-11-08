#!/usr/bin/env python3
"""Read-only T10 member-18 validation on two actual O05 native events."""

import base64
import hashlib
import json
from urllib.parse import quote

from jsonschema import Draft202012Validator

from consume import ROOT, pointer, read_pinned


CONTROL = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/18-closed-native-property-schemas.json"
CONTROL_SHA256 = "9a63a0199e2d632f05ffc6a089803579508722d5e3cb86de70371abe58d79916"
BASE = "implementation/lab-ontology/candidates/v1/migration/candidate/0001/"
MANIFEST_SHA256 = "d4228ac71001acc4061431882dfa8c0155edf87d859bbf84527307580cb81214"
SOURCE_SELECTION = "implementation/lab-ontology/candidates/v1/migration/source-selection.json"
SOURCE_SELECTION_SHA256 = "0efe0f6a59c8339211feb919757f3ec7541e044cb9ce0fd7c4a4f6ea154c7aa7"
NODE_EVENT = "semantic/00000001-ontology-semantic:O05:1.json"
RELATION_EVENT = "semantic/00000039-ontology-semantic:O05:39.json"
EXPECTED = (
    ("implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/node-properties.schema.json", "84161abdd2553b99c8cfc222aee53204fd8106b3b36abc7a4728b846628ad9bb"),
    ("implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/relation-properties.schema.json", "029199807dc5204e3a9028ddb48d361a3707ab4afd1fffd80a0f69301e2f5e34"),
)


def selected_schemas(control):
    if (control["option_id"] != "T10:control-option:18"
            or control["member_ref"] != "protocol:O06:closed-native-property-schemas"
            or control["control_kind"] != "property-schema-selection"
            or control["selected_choice"] is not None
            or control["native_or_runtime_use_allowed"] is not False
            or control["authority_effect"] != "none"):
        raise ValueError("wrong member-18 control posture")
    read_pinned(control["original_wrapper_binding"])
    read_pinned(control["original_disposition_binding"])
    if tuple((b["path"], b["sha256"]) for b in control["control_bindings"]) != EXPECTED:
        raise ValueError("wrong member-18 schema pair")
    schemas = [read_pinned(binding) for binding in control["control_bindings"]]
    for fact in control["source_facts"]:
        if pointer(read_pinned(fact["binding"]), fact["selector"]) != fact["exact_value"]:
            raise ValueError("changed member-18 source clause")
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    return schemas


def event_state(snapshot, name):
    row = snapshot["files"][name]
    raw = base64.b64decode(row["base64_original_bytes"], validate=True)
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError("changed native event bytes")
    body = json.loads(raw)
    return body["complete_resulting_semantic_state"]


def event(snapshot, name):
    return event_state(snapshot, name)["typed_properties"]["values"]


def verify_witnesses(node, relation, core, selection, snapshot):
    mapping = core["profile_binding"]
    profile = read_pinned(mapping)
    if node["mapping_sha256"] != mapping["sha256"] or relation["mapping_sha256"] != mapping["sha256"]:
        raise ValueError("mapping witness mismatch")
    node_rows = [r for r in core["record_index"] if r["version_ref"] == node["version_ref"]]
    if len(node_rows) != 1 or node_rows[0]["sha256"] != node["record_sha256"]:
        raise ValueError("node source witness mismatch")
    node_row = node_rows[0]
    if (node_row["schema_binding"]["sha256"] != node["schema_sha256"]
            or node_row["carrier_ref"] != node["carrier_ref"]
            or node_row["kind"] != node["represented_kind"]
            or node_row["node_id"] != node["identity_ref"]):
        raise ValueError("node schema or identity witness mismatch")
    read_pinned(node_row["schema_binding"])
    source_items = [item for item in selection["items"]
                    if item.get("record_structure_sha256") == relation["record_sha256"]]
    if len(source_items) != 1 or not relation["relation_version_ref"].startswith(source_items[0]["source_qualified_identity"] + "@"):
        raise ValueError("relation source witness mismatch")
    if source_items[0]["source_binding"]["sha256"] != relation["relation_version_ref"].rsplit("@", 1)[1]:
        raise ValueError("relation selected source digest mismatch")
    source_item = source_items[0]
    if (source_item["source_relation_type"] not in profile["predicates"]
            or relation["relation_kind_ref"] != profile["local_predicate_prefix"] + source_item["source_relation_type"] + "/v1-candidate"):
        raise ValueError("relation kind witness mismatch")
    relation_state = event_state(snapshot, RELATION_EVENT)
    if (relation_state["identity"]["type_ref"] != relation["relation_kind_ref"]
            or relation_state["identity"]["subject_kind"] != "relation"
            or relation_state["direction"] != "directed"):
        raise ValueError("relation native state identity mismatch")
    for side in ("source", "target"):
        endpoint_id = source_item[side + "_endpoint_id"]
        selected_nodes = [item for item in selection["items"] if item.get("legacy_identity") == endpoint_id]
        if len(selected_nodes) != 1:
            raise ValueError("relation selected endpoint unresolved")
        selected_node = selected_nodes[0]
        rows = []
        for row in core["record_index"]:
            if row["kind"] != "source":
                continue
            raw = (ROOT / BASE / row["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("candidate source record changed")
            body = json.loads(raw)
            if (body["name"] == "Observed legacy node:" + endpoint_id
                    and body["payload"]["content_digest"] == "json-structure-sha256:" + selected_node["record_structure_sha256"]
                    and body["payload"]["provenance_refs"] == [SOURCE_SELECTION + "#sha256="
                         + SOURCE_SELECTION_SHA256 + "&item=" + quote(selected_node["item_id"], safe="")]
                    and ("?sha256=" + selected_node["source_binding"]["sha256"]
                         + "&selector=" + quote(selected_node["source_binding"]["selector"], safe="")) in body["payload"]["locator"]):
                rows.append(row)
        if len(rows) != 1 or relation[side + "_version_ref"] != rows[0]["version_ref"]:
            raise ValueError("relation endpoint version unresolved")
        native_states = []
        for name in snapshot["files"]:
            if not name.startswith("semantic/"):
                continue
            state = event_state(snapshot, name)
            if state.get("typed_properties", {}).get("values", {}).get("version_ref") == rows[0]["version_ref"]:
                native_states.append(state)
        if len(native_states) != 1 or relation_state[side + "_node_id"] != native_states[0]["identity"]["subject_id"]:
            raise ValueError("relation native endpoint identity mismatch")


def consume():
    control = read_pinned({"path": CONTROL, "sha256": CONTROL_SHA256})
    node_schema, relation_schema = selected_schemas(control)
    manifest = read_pinned({"path": BASE + "manifest.json", "sha256": MANIFEST_SHA256})
    files = {row["path"]: row["sha256"] for row in manifest["files"]}
    core = read_pinned({"path": BASE + "core.json", "sha256": manifest["core_sha256"]})
    snapshot = read_pinned({"path": BASE + "native.snapshot", "sha256": files["native.snapshot"]})
    selection = read_pinned({"path": SOURCE_SELECTION, "sha256": SOURCE_SELECTION_SHA256})
    if core["selection_binding"] != {"path": SOURCE_SELECTION, "sha256": SOURCE_SELECTION_SHA256}:
        raise ValueError("migration source selection changed")
    node = event(snapshot, NODE_EVENT)
    relation = event(snapshot, RELATION_EVENT)
    for schema, value in ((node_schema, node), (relation_schema, relation)):
        errors = list(Draft202012Validator(schema).iter_errors(value))
        if errors:
            raise ValueError("actual native properties violate selected schema")
    verify_witnesses(node, relation, core, selection, snapshot)
    if core["global_typed_relations_created"] != 0:
        raise ValueError("unexpected global relation claim")
    return {"schema_version": "lab-t10-control-consumer/v1", "member_ref": control["member_ref"],
            "result": "PASS", "control_sha256": CONTROL_SHA256, "migration_manifest_sha256": MANIFEST_SHA256,
            "native_snapshot_sha256": files["native.snapshot"], "source_selection_sha256": SOURCE_SELECTION_SHA256,
            "event_sha256": {NODE_EVENT: snapshot["files"][NODE_EVENT]["sha256"],
                              RELATION_EVENT: snapshot["files"][RELATION_EVENT]["sha256"]},
            "effect": "read-only validation of one historical native node and relation; no selected T10 representation"}


if __name__ == "__main__":
    print(json.dumps(consume(), indent=2, sort_keys=True))
