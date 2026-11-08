#!/usr/bin/env python3
"""Cold T10 member-28 W09 case→audit→review route; no model admission."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT = Path(__file__).resolve().parents[4]
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}
DOMAINS = ("engineering", "research", "learning")
RESULTS = ("FLAG", "FLAG", "PASS")


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
            before_parent = os.fstat(child)
            attached_parent = os.stat(part, dir_fd=parent, follow_symlinks=False)
            need(stat.S_ISDIR(before_parent.st_mode) and
                 (before_parent.st_dev, before_parent.st_ino, before_parent.st_mode) ==
                 (attached_parent.st_dev, attached_parent.st_ino, attached_parent.st_mode), "unsafe parent")
            links.append((parent, part, child, before_parent.st_dev, before_parent.st_ino, before_parent.st_mode))
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


def link_cases(receipt, audit, review, cases):
    selected = review["selected_case_bindings"]
    need(len(selected) == len(cases) == 3 and selected == audit["case_bindings"] and
         all(binding in receipt["files"] for binding in selected), "case selection or producer files differ")
    need(receipt["audit_binding"] in receipt["files"] and
         receipt["review_selection_binding"] in receipt["files"] and
         receipt["result"] == audit["result"] == "PASS" and
         receipt["authority_effect"] == audit["authority_effect"] == review["authority_effect"] == "none" and
         receipt["actual_owner_outcome"] is audit["actual_owner_outcome"] is review["actual_owner_outcome"] is None and
         receipt["canonical_effects_applied"] == audit["canonical_effects_applied"] == 0 and
         receipt["fresh_domain_cases"] == 3 and receipt["cold_contexts"] == 3 and
         audit["all_Sessions_closed"] is True and review["final_assembly_obligations"],
         "W09 audit/review posture differs")
    need(len(audit["cases"]) == 3 and len({case["case_id"] for case in cases}) == 3,
         "three distinct cases required")
    rows = []
    for domain, status, original, examined, binding in zip(DOMAINS, RESULTS, cases, audit["cases"], selected):
        need(original["domain"] == examined["domain"] == domain and
             original["case_id"] == examined["case_id"] and
             original["facts"] == examined["facts"] and original["status_axes"] == examined["status_axes"] and
             original["authority_effect"] == "none" and original["actual_owner_outcome"] is None and
             original["canonical_effects_applied"] == 0 and examined["result"] == status,
             "case→audit domain, facts, axes, or counterevidence differs")
        rows.append({"domain": domain, "case_id": original["case_id"], "audit_result": status,
                     "case_binding": binding})
    need(review["scope"].startswith("Three source-bound candidate cases only") and
         "future use requires" in review["new_scoped_Lesson_use"].lower() and
         len(review["historical_only"]) == 2 and
         len({binding["path"] for binding in review["historical_only"]}) == 2 and
         all(binding in receipt["files"] for binding in review["historical_only"]),
         "later W09 review ceiling differs")
    return rows


def route(root=ROOT):
    matrix = body(root, MATRIX)
    need(len(matrix["rows"]) == 29 and [r["index"] for r in matrix["rows"]] == list(range(29)) and
         matrix["semantically_grounded_selected_representations"] == 0 and matrix["T10_complete"] is False,
         "T10 matrix claim differs")
    row = matrix["rows"][28]
    need(row["index"] == 28 and row["member_ref"] == "protocol:O06:W09-bounded-work-evidence" and
         row["original_class"] == "operational-evidence-selection" and
         row["selected_representation"] is None and row["exact_grounded_relation_selected"] is None and
         row["actual_owner_outcome"] is None and row["original_governed_model_disposition"] == "REFUSED-empty-relation_refs",
         "wrong original member or selected meaning")
    original = body(root, row["original_body_binding"])
    disposition = body(root, row["original_disposition_binding"])
    choice = body(root, row["review_choice_binding"])
    need(original["kind"] == "governed-model" and original["relation_refs"] == [] and
         disposition["original_index"] == choice["original_index"] == 28 and
         disposition["member_ref"] == choice["member_ref"] == row["member_ref"] and
         disposition["original_body_binding"] == row["original_body_binding"] and
         choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"] and
         choice["admission_or_runtime_use_allowed"] is False, "original refusal differs")
    for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
        exact(root, binding)
    receipt_binding, review_binding = row["original_target_bindings"]
    receipt = body(root, receipt_binding)
    need(receipt["review_selection_binding"] == review_binding, "later review binding differs")
    audit = body(root, receipt["audit_binding"])
    review = body(root, review_binding)
    cases = [body(root, binding) for binding in review["selected_case_bindings"]]
    rows = link_cases(receipt, audit, review, cases)
    for binding in review["historical_only"]:
        exact(root, binding)
    return {"index": 28, "member_ref": row["member_ref"], "case_audit_review_rows": rows,
            "receipt_binding": receipt_binding, "audit_binding": receipt["audit_binding"],
            "review_binding": review_binding, "historical_only_bindings": review["historical_only"],
            "selected_governed_model": None,
            "runtime_replayed": False, "authority_effect": "none"}


def receipt(root=ROOT):
    return {"schema_version": "lab-T10-local-W09-evidence-route/v1",
            "route_code_sha256": sha(Path(__file__).read_bytes()), "matrix_binding": MATRIX,
            "route": route(root), "bounded_route_count": 1,
            "selected_governed_model_representations": 0, "T10_complete": False, "authority_effect": "none",
            "claim_ceiling": "One retained W09 three-case producer→audit→later-review chain is cold linked. Engineering and Research FLAG counterevidence remains; no W09 replay, Lesson permission, original GovernedModel selection, owner outcome, or T10 completion follows."}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
