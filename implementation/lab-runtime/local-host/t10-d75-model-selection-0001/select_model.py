#!/usr/bin/env python3
"""Select one local D75-bound GovernedModel through the actual profile selector."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import stat
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
LOCAL = Path(__file__).resolve().parent
MATRIX = ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/"
          "all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c")
PACKAGE = Path("implementation/lab-runtime/candidates/repeatable-operation")
MODEL_SCHEMA = Path("authority/artifact-types/governed-model/v1/schema.json")
IMPLEMENTATION_SCHEMA = Path("authority/artifact-types/implementation/v1/schema.json")
RELATION_SCHEMA = Path("authority/artifact-types/typed-relation/v2/schema.json")
KIND = Path("authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/instance-of.json")
SOURCE_PROFILE_SCHEMA = PACKAGE / "schemas/source-profile.schema.json"
SOURCE_PROFILE_SCHEMA_SHA = "6cdecddf688bdffbb5cadf727c825e8b833ae85c5c64380792bf4edac45deb67"
SCHEMA_PINS = {
    MODEL_SCHEMA: "ad0ca3493af89804d190b769cbf123f71b31c228228736f839873f97ce300e61",
    IMPLEMENTATION_SCHEMA: "a6f08cb8ec97afcb11a41501b15af92fa10c75cc1f0b771d547a8b158891d172",
    RELATION_SCHEMA: "837e8ac2fb92dddd2ec894ac7238cf0415698371ac4b8e72087df0d459346a1f",
    KIND: "02af44a7bb4693b04148dc168cd336749b711da4001dbaf2ea4bcc6047747cf4",
}
IMPLEMENTATION_ID = "implementation:lab-local:C10-source-profile-d75-selector"
MODEL_ID = "governed-model:lab-local:C10-source-profile-d75"
RELATION_ID = "typed-relation:lab-local:C10-source-profile-d75-instance"
MODEL_VERSION = MODEL_ID + "@local.1"
IMPLEMENTATION_VERSION = IMPLEMENTATION_ID + "@local.1"
WORKER_SHA = "192ad7fe7b8fb849f328232f6539faf68369024f05e0a51335c7bf5d19f0aef5"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pinned(root, path, sha256, **_):
    require(type(path) is str or isinstance(path, Path), "unsafe path")
    name = path.as_posix() if isinstance(path, Path) else path
    pure = PurePosixPath(name)
    require(name == pure.as_posix() and not pure.is_absolute() and
            all(part not in ("", ".", "..") for part in pure.parts), "unsafe path")
    handles = []
    try:
        parent = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        ancestors = []
        for part in pure.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child)
            current = os.fstat(child)
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(current.st_mode) and
                    (current.st_dev, current.st_ino, current.st_mode) ==
                    (attached.st_dev, attached.st_ino, attached.st_mode), "linked or changed ancestor")
            ancestors.append((parent, part, child))
            parent = child
        leaf = os.open(pure.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        handles.append(leaf)
        before = os.fstat(leaf)
        require(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024 * 1024,
                "non-regular or unbounded input")
        parts = []
        remaining = before.st_size + 1
        while remaining:
            chunk = os.read(leaf, min(1024 * 1024, remaining))
            if not chunk:
                break
            parts.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(parts)
        after = os.fstat(leaf)
        attached = os.stat(pure.name, dir_fd=parent, follow_symlinks=False)
        key = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        require(len(raw) == before.st_size and key(before) == key(after) == key(attached),
                "changed selected file")
        for ancestor, part, held in reversed(ancestors):
            attached = os.stat(part, dir_fd=ancestor, follow_symlinks=False)
            current = os.fstat(held)
            require((attached.st_dev, attached.st_ino, attached.st_mode) ==
                    (current.st_dev, current.st_ino, current.st_mode), "changed ancestor")
    except OSError as error:
        raise ValueError("missing, linked, or changed selected input") from error
    finally:
        for handle in reversed(handles):
            os.close(handle)
    require(digest(raw) == sha256, "changed selected bytes: " + name)
    return raw


def original_context(root=ROOT):
    matrix = json.loads(read_pinned(root, *MATRIX))
    require(len(matrix["rows"]) == 29, "wrong T10 matrix")
    row = matrix["rows"][3]
    require(row["index"] == 3 and row["member_ref"] == "protocol:C10:source-profile" and
            row["selected_representation"] is None and row["exact_grounded_relation_selected"] is None and
            row["specific_missing_proof"].startswith("Whole shared D74/D75 Implementation"),
            "original semantic state changed")
    original = json.loads(read_pinned(root, **row["original_body_binding"]))
    require(original["relation_refs"] == [], "original refusal changed")
    disposition = json.loads(read_pinned(root, **row["original_disposition_binding"]))
    require(disposition["admission_or_runtime_use_allowed"] is False, "original disposition changed")
    for binding in disposition["code_bindings"]:
        read_pinned(root, **binding)
    for binding in row["original_target_bindings"]:
        read_pinned(root, **binding)
    return row, original, disposition, read_pinned(root, **row["original_target_bindings"][0])


def actual_selections(root=ROOT, source_schema_sha256=SOURCE_PROFILE_SCHEMA_SHA):
    row, original, disposition, choices_raw = original_context(root)
    expected_source = next(b["sha256"] for b in disposition["code_bindings"]
                           if b["path"] == (PACKAGE / "lab_runtime/profiles.py").as_posix())
    read_pinned(root, SOURCE_PROFILE_SCHEMA, source_schema_sha256)
    read_pinned(root, (LOCAL / "selector_worker.py").relative_to(root), WORKER_SHA)
    command = [sys.executable, "-I", "-B", str(LOCAL / "selector_worker.py"),
               str(root), expected_source]
    process = subprocess.run(command, input=choices_raw, capture_output=True, timeout=180, check=False)
    require(process.returncode == 0, "isolated original selector refused: " +
            process.stderr.decode(errors="replace")[:250])
    read_pinned(root, SOURCE_PROFILE_SCHEMA, source_schema_sha256)
    read_pinned(root, (LOCAL / "selector_worker.py").relative_to(root), WORKER_SHA)
    observed = json.loads(process.stdout)
    require(set(observed) == {"d74", "d75"} and
            observed["d74"]["executable_manifest_sha256"] == observed["d75"]["executable_manifest_sha256"] and
            observed["d74"]["profile_sha256"] != observed["d75"]["profile_sha256"],
            "D74 shared-executable counterexample missing")
    return row, original, disposition, observed


def make_documents(original, selected):
    require(selected["profile_id"] == "source-profile:lab-read:d75" and
            selected["expected_cut"] == "decision:0075" and
            selected["profile_sha256"] == "bb8ab4538a524031924d8fa5c3352c2f9bc1cd66893c39222615160d0c9fd302",
            "D75 selector binding required")
    model = deepcopy(original)
    model["node_id"] = MODEL_ID
    model["name"] = "Local D75 source-profile control model"
    model["payload"]["version_ref"] = MODEL_VERSION
    model["relation_refs"] = [{"relation_kind_ref": "relation.instance-of", "direction": "target",
                                "counterpart_kind": "implementation", "counterpart_ref": IMPLEMENTATION_ID}]
    model["claim_ceiling"] = "Local D75 selector model with tested exact source selection only; no admission or original owner outcome."
    implementation = {
        "schema_version": "cyberalchemy-lab-implementation/v1", "node_id": IMPLEMENTATION_ID,
        "kind": "implementation", "name": "Local D75-bound profile selector", "lifecycle_state": "candidate",
        "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"],
        "evidence_refs": [str(PACKAGE / "lab_runtime/profiles.py"), selected["profile_path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [],
        "relation_refs": [{"relation_kind_ref": "relation.instance-of", "direction": "source",
                           "counterpart_kind": "governed-model", "counterpart_ref": MODEL_ID}],
        "payload": {"implementation_kind": "local-d75-exact-profile-selector",
                    "conforms_to_schema_refs": [str(PACKAGE / "schemas/source-profile.schema.json")],
                    "realizes_capability_refs": ["product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"],
                    "execution_entrypoint_ref": str(PACKAGE / "lab_runtime/profiles.py") + "#select",
                    "environment_contract_ref": str(PACKAGE / "profiles/selections.json")},
        "claim_ceiling": "The local selector is limited to the D75 profile/cut; no generic Implementation classification or authority effect."
    }
    relation = {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": RELATION_ID,
        "kind": "typed-relation", "name": "D75 selector instance of local D75 control model",
        "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": "role:repository-owner",
        "scope_ref": original["scope_ref"], "evidence_refs": [selected["profile_path"]],
        "challenge_route": original["challenge_route"], "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": "relation.instance-of", "relation_lifecycle_state": "candidate",
                    "source": {"kind": "implementation", "ref": IMPLEMENTATION_ID,
                               "version_ref": IMPLEMENTATION_VERSION},
                    "target": {"kind": "governed-model", "ref": MODEL_ID, "version_ref": MODEL_VERSION},
                    "qualifiers": {"parent_version_ref": MODEL_VERSION,
                                   "binding_ref": selected["profile_path"] +
                                                  "#sha256=" + selected["profile_sha256"]},
                    "relation_evidence_refs": [selected["profile_path"]]},
        "claim_ceiling": "Local D75-only classification; no conformance, admission, original owner outcome or global edge."
    }
    return model, implementation, relation


def verify_documents(root, model, implementation, relation, selected):
    schemas = [(MODEL_SCHEMA, model), (IMPLEMENTATION_SCHEMA, implementation), (RELATION_SCHEMA, relation)]
    for path, body in schemas:
        schema = json.loads(read_pinned(root, path, SCHEMA_PINS[path]))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(body)
    kind = json.loads(read_pinned(root, KIND, SCHEMA_PINS[KIND]))
    pairs = kind["payload"]["allowed_endpoint_pairs"]
    source = relation["payload"]["source"]
    target = relation["payload"]["target"]
    expected_ref = selected["profile_path"] + "#sha256=" + selected["profile_sha256"]
    require(kind["node_id"] == relation["payload"]["relation_kind_ref"] == "relation.instance-of" and
            {"source_kind": source["kind"], "target_kind": target["kind"]} in pairs and
            source == {"kind": "implementation", "ref": IMPLEMENTATION_ID,
                       "version_ref": IMPLEMENTATION_VERSION} and
            target == {"kind": "governed-model", "ref": MODEL_ID, "version_ref": MODEL_VERSION} and
            model["node_id"] == target["ref"] and implementation["node_id"] == source["ref"] and
            model["payload"]["version_ref"] == target["version_ref"] and
            model["relation_refs"] == [{"relation_kind_ref": kind["node_id"], "direction": "target",
                                        "counterpart_kind": source["kind"], "counterpart_ref": source["ref"]}] and
            implementation["relation_refs"] == [{"relation_kind_ref": kind["node_id"], "direction": "source",
                                                 "counterpart_kind": target["kind"], "counterpart_ref": target["ref"]}] and
            relation["payload"]["qualifiers"] == {"parent_version_ref": MODEL_VERSION,
                                                    "binding_ref": expected_ref} and
            relation["payload"]["relation_evidence_refs"] == [selected["profile_path"]] and
            all(body["authority_effect"] == "none" and body["lifecycle_state"] == "candidate"
                for body in (model, implementation, relation)),
            "D75 relation classification or reciprocal binding differs")


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def build(root=ROOT):
    row, original, _, selections = actual_selections(root)
    model, implementation, relation = make_documents(original, selections["d75"])
    verify_documents(root, model, implementation, relation, selections["d75"])
    return {"schema_version": "lab-T10-local-d75-model-selection/v1", "member_index": row["index"],
            "member_ref": row["member_ref"], "selected_governed_model_representations": 1,
            "selection_scope": "local-D75-only", "D74_counterexample": {
                "profile_sha256": selections["d74"]["profile_sha256"],
                "expected_cut": selections["d74"]["expected_cut"]},
            "D75_selection": {"profile_sha256": selections["d75"]["profile_sha256"],
                               "expected_cut": selections["d75"]["expected_cut"],
                               "profile_id": selections["d75"]["profile_id"]},
            "documents": {"model": model, "implementation": implementation, "typed_relation": relation},
            "code_sha256": digest(Path(__file__).read_bytes()), "authority_effect": "none",
            "original_member_admitted": False, "source_material_capture_current": "NOT_PROVEN",
            "T10_complete": False,
            "claim_ceiling": "One locally selected relation-backed D75 profile-control model, checked by actual D74/D75 selector runs and native schemas. Physical source-material capture and original admission are not proven; other 28 members remain open."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
