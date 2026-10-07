#!/usr/bin/env python3
"""Read-only governance posture projection for Decisions 0071 and 0072."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path: str, sha256: str) -> dict:
    actual = digest(ROOT / path)
    if actual != sha256:
        raise ValueError(f"source digest mismatch: {path}: {actual} != {sha256}")
    return read_json(ROOT / path)


def inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict, dict]:
    sources = read_json(HERE / "sources.json")
    for item in sources["bindings"]:
        checked(item["path"], item["sha256"])
    by_id = {item["id"]: item for item in sources["bindings"]}
    module = read_json(HERE / "module.json")
    bundle = checked(**{k: by_id["foundation-bundle"][k] for k in ("path", "sha256")})
    artifact_overlay = checked(**{k: by_id["artifact-admission"][k] for k in ("path", "sha256")})
    relation_overlay = checked(**{k: by_id["relation-admission"][k] for k in ("path", "sha256")})
    type_registry = checked(**{k: by_id["artifact-type-registry"][k] for k in ("path", "sha256")})
    bootstrap_bundle = checked(**{k: by_id["bootstrap-bundle"][k] for k in ("path", "sha256")})
    bootstrap_artifacts = checked(**{k: by_id["bootstrap-artifact-admission"][k] for k in ("path", "sha256")})
    bootstrap_relations = checked(**{k: by_id["bootstrap-relation-admission"][k] for k in ("path", "sha256")})
    return sources, module, bundle, artifact_overlay, relation_overlay, type_registry, bootstrap_bundle, bootstrap_artifacts, bootstrap_relations


def normalize(entry: dict) -> dict:
    """D72 overlays use path/sha256; expose the same keys as D71 overlays."""
    if "source_path" in entry:
        return entry
    return {**entry, "source_path": entry["path"], "source_sha256": entry["sha256"],
            "admitted_instance_sha256": entry["sha256"]}


def project_one(entry: dict, sources: dict, module: dict, bundle: dict,
                relations: list[dict], types: dict, bootstrap: dict,
                bootstrap_artifacts: dict) -> dict:
    entry = normalize(entry)
    source = checked(entry["source_path"], entry["source_sha256"])
    copy = checked(entry["admitted_instance_path"], entry["admitted_instance_sha256"])
    if source != copy or entry["source_sha256"] != entry["admitted_instance_sha256"]:
        raise ValueError(f"admitted copy differs from source: {entry['identity_ref']}")
    identity = source.get("node_id", source.get("product_id", source.get("project_id")))
    if identity != entry["identity_ref"]:
        raise ValueError(f"identity mismatch: {entry['identity_ref']}")
    type_entry = next((item for item in types["admitted_contracts"]
                       if item["artifact_type_ref"] == entry["carrier_type_ref"]), None)
    if type_entry is None or type_entry["lifecycle_state"] != "admitted-current":
        raise ValueError(f"no admitted current carrier: {entry['carrier_type_ref']}")
    checked(type_entry["artifact_path"], type_entry["artifact_sha256"])
    checked(type_entry["schema_path"], type_entry["schema_sha256"])
    posture = source.get("lifecycle_posture", {})
    owner = None
    owner_field = None
    for field, value in (("lifecycle_posture.owner_ref", posture.get("owner_ref")),
                         ("owner_ref", source.get("owner_ref")),
                         ("semantic_owner_ref", source.get("semantic_owner_ref")),
                         ("accountable_owner_ref", source.get("accountable_owner_ref"))):
        if value is not None:
            owner, owner_field = value, field
            break
    domain_status = posture.get("status")
    lineage = []
    for raw_rel in relations:
        rel = normalize(raw_rel)
        if rel["source_ref"] != entry["identity_ref"]:
            continue
        if rel["relation_kind_ref"] not in ("relation.originates-from", "relation.derives-from"):
            continue
        rel_record = checked(rel["admitted_instance_path"], rel["admitted_instance_sha256"])
        checked(rel["source_path"], rel["source_sha256"])
        if rel_record["payload"]["source"]["ref"] != entry["identity_ref"]:
            raise ValueError(f"relation endpoint mismatch: {rel['relation_id']}")
        lineage.append({"relation_id": rel["relation_id"],
                        "relation_kind_ref": rel["relation_kind_ref"],
                        "target_ref": rel["target_ref"],
                        "qualifiers": rel_record["payload"].get("qualifiers", {})})
    lineage.sort(key=lambda item: item["relation_id"])
    successor_of = []
    superseded_by = []
    for raw_rel in relations:
        rel = normalize(raw_rel)
        if rel["relation_kind_ref"] != "relation.successor-of":
            continue
        if rel["source_ref"] == entry["identity_ref"]:
            successor_of.append(rel["target_ref"])
        if rel["target_ref"] == entry["identity_ref"]:
            superseded_by.append(rel["source_ref"])
    successor_of.sort()
    superseded_by.sort()
    evidence_refs = sorted(set(source.get("evidence_refs", []) + posture.get("evidence_refs", [])))
    semantic_history = next(x for x in bootstrap_artifacts["entries"] if x["semantic_kind"] == "project-semantic-event-history")
    governance_history = next(x for x in bootstrap_artifacts["entries"] if x["semantic_kind"] == "project-governance-event-history")
    semantic = checked(semantic_history["admitted_instance_path"], semantic_history["sha256"])["payload"]
    governance = checked(governance_history["admitted_instance_path"], governance_history["sha256"])["payload"]
    effective_state = entry["lifecycle_state"]
    predecessor = bootstrap_artifacts["predecessor_transition"]
    if entry["identity_ref"] == predecessor["identity_ref"]:
        effective_state = predecessor["to"]
    bundle_binding_id = "foundation-bundle" if bundle["bundle_id"] == module["current_integration"]["operational_foundation_bundle_ref"] else "bootstrap-bundle"
    return {
        "schema_version": "cyberalchemy-lab-governance-posture-view/v1",
        "view_kind": "governance-posture-view",
        "module_ref": module["module_id"],
        "subject_ref": entry["identity_ref"],
        "subject_version_ref": entry["version_ref"],
        "source_bundle_ref": bundle["bundle_id"],
        "source_bundle_sha256": next(item["sha256"] for item in sources["bindings"] if item["id"] == bundle_binding_id),
        "authority_effect": "none",
        "replay_source": False,
        "authority": {
            "effective_instance_state": effective_state,
            "admission_decision_ref": entry["admission_decision_ref"],
            "admission_effect": "foundation-artifact-instance-admission-only" if bundle_binding_id == "foundation-bundle" else "project-state-bootstrap-instance-admission-only",
            "declared_owner_ref": owner,
            "declared_owner_source_field": owner_field,
            "action_authorization": "not-evaluated",
            "authority_grant": "not-inferred"
        },
        "provenance": {
            "source_path": entry["source_path"],
            "source_sha256": entry["source_sha256"],
            "admitted_copy_path": entry["admitted_instance_path"],
            "admitted_copy_sha256": entry["admitted_instance_sha256"],
            "source_copy_integrity": "exact-match",
            "declared_provenance_refs": posture.get("provenance_refs", []),
            "lineage_relations": lineage,
            "declared_evidence_refs": evidence_refs,
            "evidence_sufficiency": "not-assessed"
        },
        "lifecycle": {
            "artifact_type_contract_state": type_entry["lifecycle_state"],
            "artifact_instance_state": effective_state,
            "embedded_source_status": source.get("status", "unknown"),
            "embedded_source_lifecycle_state": source.get("lifecycle_state", "unknown"),
            "domain_status": domain_status if domain_status is not None else "unknown",
            "domain_status_vocabulary_ref": posture.get("status_vocabulary_ref"),
            "realization_binding_refs": source.get("realization_binding_refs", []),
            "successor_of_refs": successor_of,
            "superseded_by_refs": superseded_by,
            "runtime_effect_of_admission_decision": "none",
            "runtime_current_state": "not-evaluated"
        },
        "independent_facets": {
            "kind": entry["semantic_kind"],
            "status": domain_status if domain_status is not None else "unknown",
            "evidence_confidence": "not-assessed",
            "commitment": posture.get("commitment_ref") or "not-declared",
            "provenance": "digest-bound-source-and-admission-copy",
            "owner": owner if owner is not None else "unknown",
            "residue": posture.get("residue_refs", [])
        },
        "project_history_at_foundation_bundle": {
            "semantic": "declared-empty-at-cursor-0",
            "governance": "declared-empty-at-cursor-0",
            "event_instances_in_this_bundle": 0
        },
        "project_history_at_bootstrap_bundle": {
            "bundle_ref": bootstrap["bundle_id"],
            "semantic_cursor": semantic["latest_cursor"],
            "semantic_event_ids": [x["event_id"] for x in semantic["events"]],
            "governance_cursor": governance["latest_governance_cursor"],
            "governance_event_ids": [x["event_id"] for x in governance["events"]],
            "latest_admitted_project_state_ref": module["current_integration"]["current_admitted_project_state_ref"],
            "next_successor_obligation": module["current_integration"]["next_successor_obligation"]
        },
        "claim_ceiling": "Read-only, source-bound projection of admitted records through Decision 0072. No permission, proof, activation, live runtime, or later Project State is established."
    }


def project_all() -> list[dict]:
    sources, module, bundle, artifacts, relations, types, bootstrap, bootstrap_artifacts, bootstrap_relations = inputs()
    if bundle["counts"]["artifact_instances_admitted"] != len(artifacts["entries"]):
        raise ValueError("artifact admission count mismatch")
    if bundle["counts"]["typed_relation_instances_admitted"] != len(relations["entries"]):
        raise ValueError("relation admission count mismatch")
    if bundle["counts"]["runtime_activations"] != 0:
        raise ValueError("runtime activation claim changed")
    if bootstrap["counts"]["artifact_instances_admitted"] != len(bootstrap_artifacts["entries"]):
        raise ValueError("bootstrap artifact count mismatch")
    if bootstrap["counts"]["typed_relation_instances_admitted"] != len(bootstrap_relations["entries"]):
        raise ValueError("bootstrap relation count mismatch")
    if bootstrap["counts"]["runtime_activations"] != 0:
        raise ValueError("bootstrap runtime activation claim changed")
    all_relations = relations["entries"] + bootstrap_relations["entries"]
    return ([project_one(entry, sources, module, bundle, all_relations, types, bootstrap, bootstrap_artifacts)
             for entry in artifacts["entries"]] +
            [project_one(entry, sources, module, bootstrap, all_relations, types, bootstrap, bootstrap_artifacts)
             for entry in bootstrap_artifacts["entries"]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", help="exact admitted artifact identity; omit for all twelve")
    parser.add_argument("--summary", action="store_true", help="compact inventory of the twelve admitted artifact postures")
    args = parser.parse_args()
    views = project_all()
    if args.subject:
        matches = [view for view in views if view["subject_ref"] == args.subject]
        if not matches:
            parser.error(f"unknown admitted artifact: {args.subject}")
        result = matches[0]
    else:
        result = views
    if args.summary:
        selected = result if isinstance(result, list) else [result]
        result = [{
            "subject_ref": view["subject_ref"],
            "kind": view["independent_facets"]["kind"],
            "effective_instance_state": view["authority"]["effective_instance_state"],
            "domain_status": view["lifecycle"]["domain_status"],
            "source_bundle_ref": view["source_bundle_ref"],
            "declared_owner_ref": view["authority"]["declared_owner_ref"],
            "evidence_confidence": view["independent_facets"]["evidence_confidence"]
        } for view in selected]
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
