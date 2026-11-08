#!/usr/bin/env python3
"""Cold T10 16/17/19/20 O02 native representation→O06 confidence route."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT = Path(__file__).resolve().parents[4]
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
O02 = "implementation/lab-ontology/candidates/v1/receipts/O02/0004.json"
EPISODE = "implementation/lab-ontology/candidates/v1/receipts/O02/lifecycle-episodes/0004/"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(root, binding):
    rel = binding["path"]
    need(type(rel) is str and rel and not rel.startswith("/") and "\\" not in rel, "unsafe path")
    pure = PurePosixPath(rel)
    need(pure.as_posix() == rel and all(part not in ("", ".", "..") for part in pure.parts), "unsafe path")
    handles = []
    links = []
    leaf = None
    try:
        parent = os.open(Path(root).resolve(strict=True), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in pure.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child)
            previous = os.fstat(child)
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            need(stat.S_ISDIR(previous.st_mode) and
                 (previous.st_dev, previous.st_ino, previous.st_mode) ==
                 (attached.st_dev, attached.st_ino, attached.st_mode), "unsafe parent")
            links.append((parent, part, child, previous.st_dev, previous.st_ino, previous.st_mode))
            parent = child
        leaf = os.open(pure.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(leaf)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024 * 1024, "unbounded file")
        chunks = []
        total = 0
        while total <= before.st_size:
            part = os.read(leaf, min(1024 * 1024, before.st_size + 1 - total))
            if not part:
                break
            chunks.append(part)
            total += len(part)
        raw = b"".join(chunks)
        after = os.fstat(leaf)
        attached = os.stat(pure.name, dir_fd=parent, follow_symlinks=False)
        key = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        need(len(raw) == before.st_size and key(before) == key(after) == key(attached), "changed file")
        for ancestor, name, held, dev, ino, mode in reversed(links):
            current = os.stat(name, dir_fd=ancestor, follow_symlinks=False)
            value = os.fstat(held)
            need((current.st_dev, current.st_ino, current.st_mode) ==
                 (value.st_dev, value.st_ino, value.st_mode) == (dev, ino, mode), "changed parent")
    except OSError as error:
        raise ValueError("unsafe path or changed attachment") from error
    finally:
        if leaf is not None:
            os.close(leaf)
        for handle in reversed(handles):
            os.close(handle)
    need(sha(raw) == binding["sha256"], "changed bytes")
    if "size_bytes" in binding:
        need(len(raw) == binding["size_bytes"], "changed size")
    return raw


def body(root, binding):
    return json.loads(exact(root, binding))


def original_row(root, row, index):
    need(row["index"] == index and row["selected_representation"] is None and
         row["exact_grounded_relation_selected"] is None and row["actual_owner_outcome"] is None and
         row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs", "selected model claim changed")
    original = body(root, row["original_body_binding"])
    disposition = body(root, row["original_disposition_binding"])
    choice = body(root, row["review_choice_binding"])
    need(original["kind"] == "governed-model" and original["relation_refs"] == [] and
         disposition["original_index"] == choice["original_index"] == index and
         disposition["member_ref"] == choice["member_ref"] == row["member_ref"] and
         disposition["original_body_binding"] == row["original_body_binding"] and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"] and
         choice["admission_or_runtime_use_allowed"] is False, "original refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        exact(root, binding)


def link_native(o02, profile, translation, sentinel, episode, witness, view,
                profile_binding, translation_binding, episode_binding, witness_binding, view_binding):
    files = o02["files"]
    need(len({row["path"] for row in files}) == len(files) and
         all(binding in files for binding in (profile_binding, translation_binding, episode_binding,
                                               witness_binding, view_binding)) and
         o02["rich_lifecycle_episode"] == episode_binding and
         witness["profile_binding"] == translation_binding,
         "O02 producer source/output bindings differ")
    need(o02["result"] == episode["result"] == view["result"] == "PASS" and
         o02["authority_effect"] == episode["authority_effect"] == view["authority_effect"] == "none" and
         o02["actual_owner_outcome"] is episode["actual_owner_outcome"] is None and
         o02["cold_rich_lifecycle"]["result"] == "PASS" and
         o02["cold_rich_lifecycle"]["rich_nodes_verified"] == episode["rich_nodes"] == 3 and
         o02["cold_rich_lifecycle"]["typed_relations_verified"] == episode["typed_relations"] == 1 and
         o02["cold_rich_lifecycle"]["native_checkpoint_parity"] == episode["native_checkpoint_parity"] ==
         view["checkpoint_parity"] == "PASS" and
         o02["cold_rich_lifecycle"]["source_effects_applied"] == episode["source_effects_applied"] == 0 and
         episode["canonical_ontology_admissions_applied"] == 0,
         "O02 retained native lifecycle result differs")
    need(profile["authority_effect"] == translation["authority_effect"] == "none" and
         profile["replay_source"] is False and
         profile["namespaces"]["governed_subject"] == translation["namespace"] and
         translation["confidence"] == sentinel and
         sentinel["allowed_levels"] == ["not-assessed"] and
         sentinel["evidence_level"] == sentinel["commitment_level"] == "not-assessed" and
         len(view["governed_nodes"]) == 3,
         "representation profile or confidence projection differs")
    identities = []
    by_id = {node["identity"]["subject_id"]: node for node in view["governed_nodes"]}
    need(len(by_id) == 3, "native represented subjects differ")
    for node in view["governed_nodes"]:
        identity = node["identity"]
        governance = node["governance_state"]
        need(identity["subject_kind"] == "node" and identity["type_ref"] == translation["node_type_ref"] and
             governance["evidence_confidence"] == governance["commitment_confidence"] ==
             {"level": sentinel["evidence_level"], "scheme_ref": sentinel["scheme_ref"]} and
             governance["candidate_or_maturity_status"] == "candidate-unadmitted" and
             governance["authority_kind_and_posture"]["posture"] == "no-source-admission-authority",
             "native view confidence, type, or admission posture differs")
        identities.append(identity["subject_id"])
    witness_ids = []
    for name in ("capability", "work", "implementation"):
        selected = witness[name]
        record = selected["rich_record"]
        need(record["node_id"] in by_id and
             selected["translation_profile_binding"] == translation_binding and
             selected["source_view"]["carrier"]["source_binding"] in files and
             selected["source_view"]["confirmed_global_edge_eligible"] is False,
             "native witness source or node identity differs")
        native = by_id[record["node_id"]]
        properties = native["semantic_state"]["typed_properties"]
        values = properties["values"]
        source = selected["source_view"]["represented_subject"]
        represented = record["payload"]["represented_subject"]
        need(native["semantic_state"]["identity"] == native["identity"] and
             native["semantic_state"]["profile_ref"] == properties["profile_ref"] ==
             translation["node_profile_ref"] and
             record["payload"]["node_type_ref"] == translation["node_type_ref"] and
             values["identity_ref"] == source["identity"] == represented["ref"] and
             values["version_ref"] == source["version_ref"] == represented["version_ref"] and
             values["record_sha256"] == source["carrier_bytes_sha256"] == represented["digest"] ==
             selected["source_view"]["carrier"]["source_binding"]["sha256"] and
             values["represented_kind"] == values["carrier_kind"] == source["kind"] == represented["kind"] and
             values["carrier_ref"] == selected["source_view"]["carrier"]["ref"] and
             values["schema_sha256"] == selected["source_view"]["carrier"]["schema_binding"]["sha256"],
             "native witness represented source differs")
        witness_ids.append(record["node_id"])
    need(set(witness_ids) == set(identities), "native witness node set differs")
    relation = witness["relation"]
    source_relation = relation["source_typed_relation"]
    selected_event = relation["native_semantic_ref"]
    matches = [event for event in view["semantic_events"] if event["event_id"] == selected_event["semantic_event_id"]]
    need(len(matches) == 1 and source_relation["carrier"]["source_binding"] in files and
         relation["confirmed_global_edge_eligible"] is False, "native relation source or event differs")
    event = matches[0]
    state = event["complete_resulting_semantic_state"]
    properties = state["typed_properties"]
    values = properties["values"]
    source_record = source_relation["record"]
    source_payload = source_record["payload"]
    need(event["semantic_cursor"] == selected_event["semantic_cursor"] == 4 and
         event["event_digest"] == selected_event["semantic_event_digest"] and
         event["subject_identity"] == state["identity"] and
         event["subject_identity"]["subject_kind"] == "relation" and
         state["source_node_id"] == witness["implementation"]["rich_record"]["node_id"] and
         state["target_node_id"] == witness["capability"]["rich_record"]["node_id"] and
         properties["profile_ref"] == translation["relation_profile_ref"] and
         values["record_sha256"] == source_relation["carrier"]["source_binding"]["sha256"] ==
         source_relation["represented_subject"]["carrier_bytes_sha256"] and
         values["qualifiers_sha256"] == sha(json.dumps(relation["qualifiers"], sort_keys=True,
                                               separators=(",", ":")).encode()) and
         values["source_version_ref"] == relation["exact_source_revision"] and
         values["target_version_ref"] == relation["exact_target_revision"] and
         values["relation_version_ref"] == source_relation["represented_subject"]["version_ref"] and
         values["relation_kind_ref"] == event["subject_identity"]["type_ref"] ==
         source_payload["relation_kind_ref"] and
         source_record["node_id"] == source_relation["represented_subject"]["identity"] and
         source_payload["source"]["version_ref"] == relation["exact_source_revision"] and
         source_payload["target"]["version_ref"] == relation["exact_target_revision"] and
         source_payload["qualifiers"] == relation["qualifiers"],
         "native relation event/source/endpoint join differs")
    return {"rich_nodes": 3, "typed_relations": 1,
            "confidence_level": "not-assessed", "candidate_node_ids": identities,
            "native_checkpoint_parity": "PASS", "global_edge_selected": False,
            "actual_native_replay_this_run": False}


def routes(root=ROOT):
    matrix = body(root, MATRIX)
    need(len(matrix["rows"]) == 29 and [row["index"] for row in matrix["rows"]] == list(range(29)) and
         matrix["semantically_grounded_selected_representations"] == 0 and matrix["T10_complete"] is False,
         "matrix claim changed")
    indexes = (16, 17, 19, 20)
    rows = [matrix["rows"][index] for index in indexes]
    need([row["member_ref"] for row in rows] ==
         ["protocol:O06:governed-subject-representation-profile",
          "protocol:O06:native-lifecycle-extension", "protocol:O06:rich-domain-translation",
          "protocol:O06:unknown-confidence"], "wrong original member identities")
    for index, row in zip(indexes, rows):
        original_row(root, row, index)
    profile_binding = rows[0]["original_target_bindings"][0]
    translation_binding = next(binding for binding in rows[2]["original_target_bindings"]
                               if binding["path"].endswith("/profiles/translation-profile.json"))
    need(translation_binding == rows[3]["original_target_bindings"][1], "confidence profile target differs")
    o02_binding = next(binding for binding in rows[0]["original_evidence_bindings"] if binding["path"] == O02)
    need(all(o02_binding in row["original_evidence_bindings"] for row in rows[1:]),
         "O02 producer evidence selection differs")
    o02 = body(root, o02_binding)
    need(all(binding in o02["files"] for row in rows[:3] for binding in row["original_target_bindings"]),
         "O02 receipt does not pin native/translation implementation")
    profile = body(root, profile_binding)
    translation = body(root, translation_binding)
    sentinel = body(root, rows[3]["original_target_bindings"][0])
    episode_binding = o02["rich_lifecycle_episode"]
    witness_binding = next(binding for binding in o02["files"] if binding["path"] == EPISODE + "mapping-witnesses.json")
    view_binding = next(binding for binding in o02["files"] if binding["path"] == EPISODE + "initial-native-view.json")
    episode = body(root, episode_binding)
    witness = body(root, witness_binding)
    view = body(root, view_binding)
    for name in ("capability", "work", "implementation"):
        exact(root, witness[name]["source_view"]["carrier"]["source_binding"])
    exact(root, witness["relation"]["source_typed_relation"]["carrier"]["source_binding"])
    observed = link_native(o02, profile, translation, sentinel, episode, witness, view,
                           profile_binding, translation_binding, episode_binding, witness_binding, view_binding)
    return {"members": list(indexes), "original_refs": [row["member_ref"] for row in rows],
            "representation_profile_binding": profile_binding, "translation_profile_binding": translation_binding,
            "unknown_confidence_proposal_binding": rows[3]["original_target_bindings"][0],
            "o02_receipt_binding": o02_binding, "episode_binding": episode_binding,
            "mapping_witness_binding": witness_binding, "native_view_binding": view_binding,
            "observed": observed, "selected_governed_models": 0, "authority_effect": "none"}


def receipt(root=ROOT):
    return {"schema_version": "lab-T10-local-representation-native-route/v1",
            "route_code_sha256": sha(Path(__file__).read_bytes()), "matrix_binding": MATRIX,
            "routes": routes(root), "bounded_route_count": 4,
            "selected_governed_model_representations": 0, "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Retained O02 native lifecycle receipt/view and exact implementation/profile bytes are cold linked to later O06 unassessed-confidence proposal. No native process is rerun, no global relation, original GovernedModel meaning, owner outcome, admission, or T10 completion is selected."}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
