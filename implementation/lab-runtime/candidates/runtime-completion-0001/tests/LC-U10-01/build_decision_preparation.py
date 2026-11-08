#!/usr/bin/env python3
"""Freeze an inert, per-member T10 decision worksheet from public pinned evidence.

This program deliberately never writes the selected semantics/representations.json.
"""

import hashlib
import json
import os
import pathlib
import stat
import sys


ROOT = pathlib.Path(__file__).resolve().parents[6]
SOURCE = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/COVERAGE-29.json"
SOURCE_SHA = "e3d7543a6415afdfad280d7d0869eee42e12dc30db5112ddda8a1287d5340209"
QUALIFICATION = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/initial-qualification-0001.json"
QUALIFICATION_SHA = "4bb91275ee5015b3638330d3855e5b9200b00fca3ac9085027a4d08fbe85e7b7"
MANIFEST = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/acceleration-audit-20261018/t35-scope-amendment-0002/effective-manifest-0002.json"
MANIFEST_SHA = "b03dc7d202d084dbbbeffa632d5aa5f6a9c71a3265daaf0535594746177f5a77"
OUTPUT = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U10-01/decision-preparation-0001.json"


def read_binding(binding):
    rel = binding["path"]
    path = pathlib.PurePosixPath(rel)
    if path.is_absolute() or any(c in ("", ".", "..") for c in rel.split("/")):
        raise ValueError(f"unsafe binding path: {rel}")
    file = ROOT / rel
    st = file.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        raise ValueError(f"not an exclusive regular file: {rel}")
    data = file.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != binding["sha256"] or ("size_bytes" in binding and len(data) != binding["size_bytes"]):
        raise ValueError(f"binding drift: {rel}")
    return data


def fixed_json(rel, sha=None):
    data = (ROOT / rel).read_bytes()
    if sha and hashlib.sha256(data).hexdigest() != sha:
        raise ValueError(f"source drift: {rel}")
    return json.loads(data)


def question(member):
    ref = member["member_ref"]
    category = member["category"]
    if category == "prospective-endpoint":
        return f"For {ref}, approve the exact endpoint carrier and identity-selector meaning under an authorized prospective type, prove an eligible directed GovernedModel/v1 counterpart, or keep the original refusal?"
    if category == "grounded-source-profile":
        return f"For {ref}, does the exact unchanged Implementation counterpart still support the original relation at the currently selected source/profile cut, with owner authority and fresh code/schema evidence, or must the refusal remain?"
    if category == "prospective-workflow":
        return f"For {ref}, approve a prospective model of this exact transition contract, identify a real permitted directional v1 counterpart, or retain its original refusal?"
    if category == "prospective-profile":
        return f"For {ref}, approve this exact prospective profile meaning and carrier, identify a real permitted directional v1 counterpart, or retain its original refusal?"
    if category == "distinct-unassessed-confidence-axes":
        return f"For {ref}, approve the separate evidence and commitment not-assessed vocabulary with source-local Axis and admitted Definition proof, select another supported carrier, or retain refusal?"
    if category == "new-protocol-review-alternatives":
        return f"For {ref}, choose A prospective model with explicit type/Definition approval, B bound control with an explicit category/carrier disposition, or C original refusal; what exact original scope and exclusions bind the choice?"
    raise ValueError(category)


def make_packet():
    manifest = fixed_json(MANIFEST, MANIFEST_SHA)
    unit = next(u for u in manifest["units"] if u["id"] == "LC-U10-01")
    if unit["external_gates"] != ["G04"] or unit["oracle"] != "All29 members individually accounted; schema validity alone never selects meaning":
        raise ValueError("unit contract drift")
    coverage = fixed_json(SOURCE, SOURCE_SHA)
    qualification = fixed_json(QUALIFICATION, QUALIFICATION_SHA)
    originals = qualification["original_refusals"]
    members = coverage["members"]
    if len(members) != 29 or len(originals) != 29:
        raise ValueError("wrong member count")
    rows = []
    for index, (m, q) in enumerate(zip(members, originals)):
        if m["original_index"] != index or m["member_ref"] != q["member_ref"]:
            raise ValueError(f"original order/identity mismatch: {index}")
        wrapper = json.loads(read_binding(m["original_wrapper_binding"]))
        disposition = json.loads(read_binding(m["original_disposition_binding"]))
        source_body = disposition["original_body_binding"]
        read_binding(source_body)
        if q["original_binding"] != source_body or q["original_schema_status"] != "REFUSED":
            raise ValueError(f"original qualification mismatch: {index}")
        if wrapper["relation_refs"] != [] or disposition["member_ref"] != m["member_ref"]:
            raise ValueError(f"original refusal mismatch: {index}")
        if "minItems" not in disposition["original_axes"]["blockers"][0]:
            raise ValueError(f"different refusal: {index}")
        evidence = json.loads(read_binding(m["evidence"]))
        for b in m["postimages"]:
            read_binding(b)
        if m["actual_owner_outcome"] is not None or m["selected_representation"] is not None or m["runtime_use_allowed"]:
            raise ValueError(f"prior selection changed: {index}")
        semantics = disposition["original_member_semantics"]
        row = {
            "index": index,
            "member_ref": m["member_ref"],
            "category": m["category"],
            "original_wrapper_binding": m["original_wrapper_binding"],
            "original_disposition_binding": m["original_disposition_binding"],
            "original_body_binding": source_body,
            "original_carrier_ref": disposition["original_axes"]["carrier_ref"],
            "original_refusal": "GovernedModel/v1 relation_refs.minItems=1; original relation_refs=[]",
            "member_class": semantics["member_class"],
            "requested_effect": semantics["requested_effect"],
            "proposed_owner_roles": semantics["proposed_owner_roles"],
            "scope": semantics["scope"],
            "exclusions": semantics["exclusions"],
            "option_evidence_binding": m["evidence"],
            "candidate_postimage_bindings": m["postimages"],
            "decision_question": question(m),
            "selected_option": None,
            "actual_answering_principal_ref": None,
            "accountable_disposition_binding": None,
            "runtime_use_allowed": False,
        }
        if m["category"] == "new-protocol-review-alternatives":
            if evidence["member_ref"] != m["member_ref"] or evidence["original_index"] != index:
                raise ValueError(f"new option mismatch: {index}")
            row["review_choices"] = [
                {"choice_id": choice["choice_id"], "postimage_binding": choice["postimage_binding"],
                 "benefit": choice["benefit"], "tradeoff": choice["tradeoff"]}
                for choice in evidence["choices"]
            ]
            row["exact_option_meaning"] = evidence["exact_meaning"]
            row["meaning_difference_from_original"] = evidence["meaning_difference_from_original"]
            row["counterpart_assessment"] = evidence["counterpart_assessment"]
            row["dependency_gates"] = evidence["dependency_gates"]
        else:
            row["review_choices"] = [
                {"choice_id": "supported-candidate-or-exact-v1-relation", "postimage_bindings": m["postimages"],
                 "condition": "Individually review source meaning, exact carrier/Definition and permitted relation direction/counterpart before selection."},
                {"choice_id": "retain-original-refusal", "postimage_binding": m["original_wrapper_binding"],
                 "condition": "Preserve original bytes and refusal without runtime use."},
            ]
        rows.append(row)
    return {
        "schema_version": "lab-LC-U10-01-decision-preparation/v1",
        "unit": "LC-U10-01",
        "status": "INERT-DECISION-PREPARATION-ONLY",
        "effective_manifest_binding": {"path": MANIFEST, "sha256": MANIFEST_SHA},
        "coverage_binding": {"path": SOURCE, "sha256": SOURCE_SHA},
        "qualification_binding": {"path": QUALIFICATION, "sha256": QUALIFICATION_SHA},
        "original_members": 29,
        "prepared_members": len(rows),
        "accountably_selected_members": 0,
        "authority_effect": "none",
        "materialization_allowed": False,
        "decision_required_before_effect": [
            "For each member, name the authorized principal, role assignment, scope and currentness evidence.",
            "Choose exact meaning and carrier/Definition or preserve original refusal; schema validity is insufficient.",
            "For a GovernedModel/v1 relation, prove actual eligible counterpart, declared kind and direction; never invent one.",
            "Bind exact source/body/code/schema/private evidence where applicable, independent per-member review, and preserved exclusions.",
            "Only then create a new selected disposition and eligible candidate postimage under the unit contract.",
        ],
        "members": rows,
    }


def main():
    out = ROOT / OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    packet = make_packet()
    data = (json.dumps(packet, indent=2, ensure_ascii=False) + "\n").encode()
    with os.fdopen(os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644), "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    print(f"{OUTPUT} sha256={hashlib.sha256(data).hexdigest()} rows={len(packet['members'])}")


if __name__ == "__main__":
    main()
