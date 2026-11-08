#!/usr/bin/env python3
"""Bounded local routes for T10 members 00–03; no semantic admission."""

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
EXAMPLES = (
    ("authority/artifact-types/project-identity/v1/fixtures/valid/project.json", "6cd111461c42cf7eb20362c6bbb100a609a17e87228e824718ddb45b4835a72a", "project_id", "project"),
    ("authority/artifact-types/product-identity/v2/fixtures/valid/product.json", "3f4a554a5752f43cb03ea8032f954f9f22af037cf618849d19ebfd7aa5f11f27", "product_id", "product"),
    ("implementation/lab-runtime/candidates/repeatable-operation/semantic-proposals/method/v1/example.json", "c82e32a904a0c0265225df47e1738266480e1688f3ad874951f109a366190ea4", "method_id", "method"),
)
PROFILES_CODE = {"path": "implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/profiles.py",
                 "sha256": "93237149ba9da94c96561e3beaf8418471fe5385964a6197dd2ee8ddd31a5dd4"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(root, binding):
    rel = binding["path"]
    need(type(rel) is str and rel and not rel.startswith("/") and "\\" not in rel, "unsafe path")
    pure = PurePosixPath(rel)
    need(pure.as_posix() == rel and all(p not in ("", ".", "..") for p in pure.parts), "unsafe path")
    root = root.resolve(strict=True)
    path = root
    for part in pure.parts[:-1]:
        path /= part
        need(stat.S_ISDIR(path.lstat().st_mode), "unsafe parent: " + rel)
    path /= pure.parts[-1]
    need(stat.S_ISREG(path.lstat().st_mode), "unsafe file: " + rel)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        need(stat.S_ISREG(os.fstat(fd).st_mode), "unsafe file: " + rel)
        raw = os.read(fd, os.fstat(fd).st_size + 1)
    finally:
        os.close(fd)
    need(sha(raw) == binding["sha256"], "changed bytes: " + rel)
    if "size_bytes" in binding:
        need(len(raw) == binding["size_bytes"], "changed size: " + rel)
    return raw


def body(root, binding):
    return json.loads(exact(root, binding))


def proposed_identity(artifact, schema, proposal, *, expected_field, expected_kind):
    need(proposal["endpoint_kind"] == expected_kind and
         proposal["identity_selector"] == "/" + expected_field and
         proposal["status"] in ("candidate-semantic-mapping-not-an-admitted-alias", "candidate-carrier-required"),
         "wrong endpoint proposal or selector")
    errors = list(Draft202012Validator(schema).iter_errors(artifact))
    need(not errors, "invalid carrier example")
    identity = artifact.get(expected_field)
    need(type(identity) is str and identity, "missing declared identity field")
    return identity


def endpoint(root, row, impact, index):
    path, digest, field, kind = EXAMPLES[index]
    need(row["index"] == index and row["member_ref"] == "protocol:C10:mapping-" + kind and
         row["original_class"] == "semantic-mappings" and row["candidate_route"] == "endpoint-interpretation" and
         row["original_target_bindings"][0]["path"].endswith("/contract-impact.json") and
         {k: row["original_target_bindings"][2][k] for k in ("path", "sha256")} ==
         {k: impact["endpoint_proposals"][index]["schema_binding"][k] for k in ("path", "sha256")},
         "wrong endpoint member or target")
    schema = body(root, row["original_target_bindings"][2])
    example = body(root, {"path": path, "sha256": digest})
    identity = proposed_identity(example, schema, impact["endpoint_proposals"][index],
                                 expected_field=field, expected_kind=kind)
    prospective = body(root, row["prepared_postimage_bindings"][0])
    need(prospective["kind"] == "governed-model" and prospective["relation_refs"] == [] and
         prospective["node_id"] != identity and prospective["lifecycle_state"] == "candidate",
         "prospective model would collapse carrier/endpoint")
    return {"index": index, "member_ref": row["member_ref"], "route_kind": "schema-validated-selector-example",
            "carrier_schema_binding": row["original_target_bindings"][2],
            "example_binding": {"path": path, "sha256": digest},
            "identity_selector": "/" + field, "observed_example_identity": identity,
            "endpoint_meaning_selected": False, "selected_governed_model": None,
            "admission_or_runtime_use_allowed": False}


def source_profile(root, row):
    need(row["index"] == 3 and row["member_ref"] == "protocol:C10:source-profile" and
         row["candidate_route"] == "source-selection-contract" and
         row["original_class"] == "source-selection", "wrong source-profile member")
    selections, profile, policy, review, content = [body(root, b) for b in row["original_target_bindings"]]
    d75 = [x for x in selections["selections"] if x["name"] == "d75"]
    need(len(d75) == 1 and
         all(d75[0][field] == row["original_target_bindings"][position]["path"]
             for field, position in (("profile_path", 1), ("policy_path", 2), ("review_path", 3))) and
         d75[0]["profile_sha256"] == row["original_target_bindings"][1]["sha256"] and
         d75[0]["review_sha256"] == row["original_target_bindings"][3]["sha256"] and
         profile["policy_core_sha256"] == row["original_target_bindings"][2]["sha256"] and
         profile["content_manifest"]["sha256"] == row["original_target_bindings"][4]["sha256"] and
         review["profile_sha256"] == d75[0]["profile_sha256"] and
         review["policy_sha256"] == profile["policy_core_sha256"] and
         review["content_manifest_sha256"] == profile["content_manifest"]["sha256"] and
         content["source_cut"] == profile["expected_cut"] and
         d75[0]["source_materials"] == len(content["materials"]) and
         policy["authority_effect"] == profile["authority_effect"] == review["authority_effect"] == "none",
         "D75 profile/policy/review/content selection differs")
    exact(root, PROFILES_CODE)
    candidate = body(root, row["prepared_postimage_bindings"][0])
    need(candidate["relation_refs"] == [row["proposed_model_relation"]] and
         candidate["lifecycle_state"] == "candidate" and
         candidate["authority_effect"] == "none", "source-profile candidate relation differs")
    return {"index": 3, "member_ref": row["member_ref"], "route_kind": "cold-D75-control-binding",
            "source_profile_bindings": row["original_target_bindings"], "selector_code_binding": PROFILES_CODE,
            "observed_source_cut": content["source_cut"], "selected_governed_model": None,
            "candidate_relation_classification_proven": False, "actual_selection_executed": False,
            "admission_or_runtime_use_allowed": False}


def routes(root=ROOT):
    matrix = body(root, {"path": MATRIX, "sha256": MATRIX_SHA})
    rows = matrix["rows"]
    need(len(rows) == 29 and [x["index"] for x in rows] == list(range(29)) and
         matrix["semantically_grounded_selected_representations"] == 0 and matrix["T10_complete"] is False,
         "matrix claim changed")
    impact = body(root, rows[0]["original_target_bindings"][0])
    need(len(impact["endpoint_proposals"]) >= 3 and impact["authority_effect"] == "none", "endpoint impact changed")
    result = []
    for i, row in enumerate(rows[:4]):
        original = body(root, row["original_body_binding"])
        disposition = body(root, row["original_disposition_binding"])
        choice = body(root, row["review_choice_binding"])
        for binding in row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]:
            exact(root, binding)
        need(original["kind"] == "governed-model" and original["relation_refs"] == [] and
             disposition["original_index"] == choice["original_index"] == i and
             disposition["member_ref"] == choice["member_ref"] == row["member_ref"] and
             disposition["original_body_binding"] == row["original_body_binding"] and
             choice["original_disposition_binding"]["sha256"] == row["original_disposition_binding"]["sha256"] and
             disposition["actual_owner_outcome"] is choice["actual_owner_outcome"] is None and
             choice["admission_or_runtime_use_allowed"] is False and
             row["selected_representation"] is None and row["exact_grounded_relation_selected"] is None,
             "original refusal or unselected meaning changed")
        result.append(endpoint(root, row, impact, i) if i < 3 else source_profile(root, row))
    return result


def receipt(root=ROOT):
    return {"schema_version": "lab-T10-local-endpoint-control-routes/v1",
            "route_code_sha256": sha(Path(__file__).read_bytes()),
            "matrix_binding": {"path": MATRIX, "sha256": MATRIX_SHA},
            "routes": routes(root), "bounded_route_count": 4,
            "schema_validated_identity_examples": 3, "selected_governed_model_representations": 0,
            "authority_effect": "none", "T10_complete": False,
            "claim_ceiling": "Three candidate carrier identity selectors and one D75 cold control binding are locally checked. No endpoint alias, Method admission, D75 current selection, relation classification, original GovernedModel selection, or T10 completion is established."}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
