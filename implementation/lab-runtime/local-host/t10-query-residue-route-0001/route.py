#!/usr/bin/env python3
"""Cold T10 21/27 producer-to-consumer route; no GovernedModel selection."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
MATRIX = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json"
MATRIX_SHA = "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"
O03_SELECTION = {"path": "implementation/lab-ontology/candidates/v1/queries/successors/0009/packages/0001/selection.json",
                 "sha256": "5dce634a00ac7ff99f4319332d36ca77ee2c5850244d016b4bf778b705db9cf3"}
GROUPS = {
    "native-O05": ("O05-source-interpretation", "candidate:O05", "current", ("native-source-lineage",)),
    "current-D75": ("d75-selected-source", "decision:0075", "current", ("lifecycle-D75",)),
    "historical-D73": ("historical-d73-slice", "decision:0073", "historical", ("authority", "lifecycle", "provenance")),
}
QUERY_IDS = {"native-source-lineage": "capability-provenance",
             "lifecycle-D75": "lifecycle-slice", "authority": "authority-explanation",
             "lifecycle": "lifecycle-slice", "provenance": "capability-provenance"}
SNAPSHOT_FIELDS = ("admission_epoch", "histories", "manifest_digest", "source_cut_digest")


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
    root = Path(root).resolve(strict=True)
    handles = []
    links = []
    leaf = None
    try:
        parent = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in pure.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child)
            before_parent = os.fstat(child)
            attached_parent = os.stat(part, dir_fd=parent, follow_symlinks=False)
            need(stat.S_ISDIR(before_parent.st_mode) and
                 (before_parent.st_dev, before_parent.st_ino, before_parent.st_mode) ==
                 (attached_parent.st_dev, attached_parent.st_ino, attached_parent.st_mode),
                 "unsafe parent: " + rel)
            links.append((parent, part, child, before_parent.st_dev, before_parent.st_ino, before_parent.st_mode))
            parent = child
        leaf = os.open(pure.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(leaf)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024 * 1024, "unbounded file: " + rel)
        chunks = []
        size = 0
        while size <= before.st_size:
            part = os.read(leaf, min(1024 * 1024, before.st_size + 1 - size))
            if not part:
                break
            chunks.append(part)
            size += len(part)
        raw = b"".join(chunks)
        after = os.fstat(leaf)
        attached = os.stat(pure.name, dir_fd=parent, follow_symlinks=False)
        key = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(len(raw) == before.st_size and key(before) == key(after) == key(attached), "changed file: " + rel)
        for ancestor, name, held, dev, ino, mode in reversed(links):
            current = os.stat(name, dir_fd=ancestor, follow_symlinks=False)
            value = os.fstat(held)
            need((current.st_dev, current.st_ino, current.st_mode) ==
                 (value.st_dev, value.st_ino, value.st_mode) == (dev, ino, mode),
                 "changed parent: " + rel)
    except OSError as error:
        raise ValueError("unsafe path or changed attachment: " + rel) from error
    finally:
        if leaf is not None:
            os.close(leaf)
        for handle in reversed(handles):
            os.close(handle)
    need(sha(raw) == binding["sha256"], "changed bytes: " + rel)
    if "size_bytes" in binding:
        need(len(raw) == binding["size_bytes"], "changed size: " + rel)
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
         disposition["actual_owner_outcome"] is choice["actual_owner_outcome"] is None and
         choice["admission_or_runtime_use_allowed"] is False, "original refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        exact(root, binding)


def semantic_link(group, question, proposal, result, response, contract, response_binding):
    scope, epoch, freshness, names = GROUPS[group]
    need(question in names and proposal["response_binding"] == response_binding and
         result["response_binding"] == response_binding, "producer/consumer response binding differs")
    need(proposal["authority_effect"] == response["authority_effect"] == "none" and
         proposal["result_status"] == result["status"] == response["result_status"] and
         proposal["coverage"] == response["coverage"] and proposal["gaps"] == response["gaps"],
         "producer/consumer query projection differs")
    need(proposal["source_snapshot"] == {name: response["source_snapshot"][name] for name in SNAPSHOT_FIELDS} and
         response["coverage"]["scope_ref"] == response["query"]["scope_ref"] == scope and
         response["query"]["admission_as_of"] == response["source_snapshot"]["admission_epoch"] == epoch and
         response["freshness"]["state"] == freshness and contract["scopes"][scope] == epoch and
         response["query"]["query_id"] == QUERY_IDS[question] and
         response["query"]["query_id"] in contract["query_ids"] and
         response["coverage"]["partition"] == result["counts"] and len(response["gaps"]) == result["gaps"],
         "query scope, currentness, or partition differs")
    canonical = json.dumps(response, sort_keys=True, separators=(",", ":")).encode()
    need(sha(canonical) == result["response_digest"], "producer semantic response digest differs")
    need(len(response["gaps"]) > 0 and type(response["source_snapshot"]["source_cut_digest"]) is str,
         "query gap or source cut absent")
    return {"question": question, "scope_ref": scope, "source_cut_digest": response["source_snapshot"]["source_cut_digest"],
            "freshness": freshness, "result_status": result["status"], "gap_count": len(response["gaps"]),
            "response_binding": response_binding}


def producer_bindings(receipt, selection, required):
    need(receipt["result"] == "PASS" and receipt["task"] == "O03" and
         receipt["authority_effect"] == "none" and receipt["actual_owner_outcome"] is None and
         receipt["selection_binding"] == O03_SELECTION and selection["authority_effect"] == "none" and
         selection["task"] == "O03" and selection["canonical_admission"] is False,
         "O03 producer selection or posture differs")
    for title, value in (("producer", receipt), ("selection", selection)):
        files = value["files"]
        need(len({row["path"] for row in files}) == len(files), "duplicate " + title + " file row")
        actual = {row["path"]: row for row in files}
        for binding in required if title == "producer" else required[:3]:
            need(actual.get(binding["path"]) == binding, title + " does not pin consumed bytes")


def producer_result(result, scope, names):
    need(result["result"] == "PASS" and result["authority_effect"] == "none" and
         result["actual_owner_outcome"] is None and result["closed_scope"] is True and
         result["owned_query_stores_removed"] is True and result["scope_ref"] == scope and
         result["selection_binding"] == O03_SELECTION and set(result["questions"]) == set(names),
         "producer result posture differs")


def routes(root=ROOT):
    matrix = body(root, {"path": MATRIX, "sha256": MATRIX_SHA})
    need(len(matrix["rows"]) == 29 and [r["index"] for r in matrix["rows"]] == list(range(29)) and
         matrix["semantically_grounded_selected_representations"] == 0 and matrix["T10_complete"] is False,
         "matrix claim changed")
    query = matrix["rows"][21]
    residue = matrix["rows"][27]
    need(query["member_ref"] == "protocol:O06:three-lens-query-contract" and
         residue["member_ref"] == "protocol:O06:query-coverage-residue" and
         query["original_class"] == "query-contract-selection" and
         residue["original_class"] == "query-evidence-selection", "wrong original member kind")
    original_row(root, query, 21)
    original_row(root, residue, 27)
    contract = body(root, query["original_target_bindings"][1])
    request_schema = body(root, query["original_target_bindings"][2])
    response_schema = body(root, query["original_target_bindings"][3])
    need(contract["request_schema_binding"] == query["original_target_bindings"][2] and
         contract["response_schema_binding"] == query["original_target_bindings"][3] and
         contract["authority_effect"] == "none" and contract["replay_source"] is False and
         set(contract["scopes"]) == {value[0] for value in GROUPS.values()}, "query contract selection differs")
    proposal = body(root, residue["original_target_bindings"][0])
    need(set(proposal) == set(GROUPS), "query scope selection differs")
    o03_binding = next(binding for binding in query["original_evidence_bindings"]
                       if binding["path"] == "implementation/lab-ontology/candidates/v1/receipts/query-coverage.json")
    need(o03_binding in residue["original_evidence_bindings"], "O03 evidence selections differ")
    o03_receipt = body(root, o03_binding)
    o03_selection = body(root, O03_SELECTION)
    required = query["original_target_bindings"][1:4]
    for group in GROUPS:
        required.append(proposal[group]["result_binding"])
        required.extend(value["response_binding"] for value in proposal[group]["questions"].values())
    producer_bindings(o03_receipt, o03_selection, required)
    rows = []
    cuts = set()
    for group, (scope, epoch, freshness, names) in GROUPS.items():
        selected = proposal[group]
        need(set(selected["questions"]) == set(names), "query list differs")
        result = body(root, selected["result_binding"])
        producer_result(result, scope, names)
        for name in names:
            summary = result["questions"][name]
            binding = selected["questions"][name]["response_binding"]
            response = body(root, binding)
            need(not list(Draft202012Validator(request_schema).iter_errors(response["query"])) and
                 not list(Draft202012Validator(response_schema).iter_errors(response)),
                 "query request or response schema differs")
            row = semantic_link(group, name, selected["questions"][name], summary, response, contract, binding)
            rows.append(row)
            cuts.add(row["source_cut_digest"])
    need(len(rows) == 5 and len(cuts) == 3 and
         {r["result_status"] for r in rows if r["scope_ref"] == "historical-d73-slice"} == {"complete", "partial"},
         "distinct three-scope query residue differs")
    return {"members": [21, 27], "original_refs": [query["member_ref"], residue["member_ref"]],
            "contract_binding": query["original_target_bindings"][1],
            "proposal_binding": residue["original_target_bindings"][0],
            "producer_receipt_binding": o03_binding, "producer_selection_binding": O03_SELECTION,
            "producer_consumer_questions": rows,
            "source_cuts": {group: proposal[group]["questions"][names[0]]["source_snapshot"]["source_cut_digest"]
                            for group, (_, _, _, names) in GROUPS.items()},
            "selected_governed_models": 0, "runtime_query_replayed": False, "authority_effect": "none"}


def receipt(root=ROOT):
    return {"schema_version": "lab-T10-local-query-residue-route/v1",
            "route_code_sha256": sha(Path(__file__).read_bytes()),
            "matrix_binding": {"path": MATRIX, "sha256": MATRIX_SHA},
            "route": routes(root), "bounded_route_count": 2, "selected_governed_model_representations": 0,
            "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "Exact retained O03 three-scope query results and schema-valid responses are cold linked to later O06 residue projection. The query producer is not rerun; no original GovernedModel meaning, relation, owner outcome, admission, or runtime use is selected."}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
