#!/usr/bin/env python3
"""Cold T10 24–26 O05 producer→O06 disposition/privacy/archive route."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT = Path(__file__).resolve().parents[4]
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
O05 = "implementation/lab-ontology/candidates/v1/receipts/O05/0001.json"


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


def link_source(dispositions, policy, core, manifest, archive_sha, o05, core_binding, manifest_binding, archive_binding):
    expected = {"adapt": 88, "reference": 43, "block": 9}
    need(dispositions["original_core_binding"] == core_binding and
         dispositions["items"] == core["dispositions"] and len(core["dispositions"]) == 140 and
         dict(Counter(item["disposition"] for item in core["dispositions"])) == expected and
         len({item["item_id"] for item in core["dispositions"]}) == 140 and
         dispositions["source_selection_binding"] == policy["source_selection_binding"] ==
         core["selection_binding"] == manifest["source_selection_binding"] and
         dispositions["excluded_packages"] == core["excluded_packages"] and
         dispositions["deferred_source_epoch"] == core["deferred_source_epoch"] and
         dispositions["original_residual_questions"] == core["outside_references"],
         "O05→O06 source disposition projection differs")
    need(core["native_archive_sha256"] == archive_sha == archive_binding["sha256"] and
         manifest["core_sha256"] == core_binding["sha256"] and
         manifest["counts"] == {"source": 131, "ontology-node": 38, "ontology-edge": 50, "generated-output": 1} and
         {r["path"]: r["sha256"] for r in manifest["files"]}.get("native.snapshot") == archive_sha and
         o05["manifest_binding"] == manifest_binding and
         all(binding in o05["files"] for binding in (core_binding, manifest_binding, archive_binding)) and
         o05["result"] == "PASS" and o05["items_reconciled"] == 140 and
         o05["blocked_dependency_revisions"] == 9 and
         o05["source_effects_applied"] == o05["source_bodies_copied"] ==
         o05["global_typed_relations_created"] == o05["domain_instances_conformed"] == 0,
         "O05 original archive or producer receipt differs")
    denied = ("body_import", "semantic_admission", "execution", "public_export", "service_activation",
              "source_retirement", "secrets_or_Session_memory_allowed")
    need(policy["source_owner_and_access_authority_verified"] is False and
         policy["source_validation_read_only"] is True and policy["current_operation_authority_required"] is True and
         all(policy[name] is False for name in denied) and
         dispositions["admitted_source_effects_applied"] == dispositions["source_retirements"] == 0 and
         dispositions["public_body_export_allowed"] is False and
         all(value["authority_effect"] == "none" and value["actual_owner_outcome"] is None
             for value in (dispositions, policy, core, manifest, o05)),
         "private-use or authority ceiling differs")
    return {"disposition_counts": expected, "source_manifest_counts": manifest["counts"],
            "archive_sha256": archive_sha, "source_selection_binding": core["selection_binding"],
            "public_body_export_allowed": False, "selected_source_effects": 0}


def routes(root=ROOT):
    matrix = body(root, MATRIX)
    need(len(matrix["rows"]) == 29 and [row["index"] for row in matrix["rows"]] == list(range(29)) and
         matrix["semantically_grounded_selected_representations"] == 0 and matrix["T10_complete"] is False,
         "matrix claim changed")
    rows = matrix["rows"][24:27]
    need([row["member_ref"] for row in rows] ==
         ["protocol:O06:source-dispositions", "protocol:O06:private-metadata-use",
          "protocol:O06:original-native-archive-retention"], "wrong original source members")
    for index, row in enumerate(rows, 24):
        original_row(root, row, index)
    core_binding, manifest_binding, archive_binding = rows[2]["original_target_bindings"]
    o05_binding = next(binding for binding in rows[0]["original_evidence_bindings"] if binding["path"] == O05)
    need(o05_binding in rows[1]["original_evidence_bindings"] and
         o05_binding in rows[2]["original_evidence_bindings"], "O05 producer evidence selection differs")
    dispositions = body(root, rows[0]["original_target_bindings"][0])
    policy = body(root, rows[1]["original_target_bindings"][0])
    core = body(root, core_binding)
    manifest = body(root, manifest_binding)
    archive_sha = sha(exact(root, archive_binding))
    o05 = body(root, o05_binding)
    exact(root, core["selection_binding"])
    observed = link_source(dispositions, policy, core, manifest, archive_sha, o05,
                           core_binding, manifest_binding, archive_binding)
    return {"members": [24, 25, 26], "original_refs": [row["member_ref"] for row in rows],
            "source_projection": observed, "o05_receipt_binding": o05_binding,
            "o06_disposition_binding": rows[0]["original_target_bindings"][0],
            "o06_private_use_binding": rows[1]["original_target_bindings"][0],
            "selected_governed_models": 0, "source_import_or_archive_replay_executed": False,
            "authority_effect": "none"}


def receipt(root=ROOT):
    return {"schema_version": "lab-T10-local-source-retention-route/v1",
            "route_code_sha256": sha(Path(__file__).read_bytes()), "matrix_binding": MATRIX,
            "routes": routes(root), "bounded_route_count": 3,
            "selected_governed_model_representations": 0, "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Exact retained O05 public core, manifest, and native archive bytes are cold linked to later O06 dispositions and private-use limits. No archive replay, source withdrawal, body export, actual owner authority, original GovernedModel selection, or T10 completion follows."}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
