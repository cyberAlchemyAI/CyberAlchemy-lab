#!/usr/bin/env python3
"""Validate this candidate and the exact admitted sources it projects."""

import hashlib
import json
from pathlib import Path

import jsonschema

from project import HERE, ROOT, checked, inputs, normalize, project_all, read_json


def main() -> None:
    sources, module, bundle, artifacts, relations, types, bootstrap, bootstrap_artifacts, bootstrap_relations = inputs()
    jsonschema.Draft202012Validator(read_json(HERE / "module.schema.json")).validate(module)
    if [x["id"] for x in module["lenses"]] != ["authority", "provenance", "lifecycle"]:
        raise ValueError("governance lens set or order changed")
    if [x["id"] for x in module["independent_facets"]] != ["kind", "status", "evidence_confidence", "commitment", "provenance", "owner", "residue"]:
        raise ValueError("independent facet set or order changed")
    bindings = {item["id"]: item for item in sources["bindings"]}
    if len(bindings) != len(sources["bindings"]):
        raise ValueError("duplicate source binding")
    registry = checked(bindings["definition-registry"]["path"], bindings["definition-registry"]["sha256"])
    for ident in module["canonical_definition_refs"]:
        exact = registry["current_lookup"][ident]
        item = next(x for x in registry["entries"] if x["definition_id"] == ident and ident + "@" + x["version"] == exact)
        binding = bindings["definition:" + ident]
        if binding["path"] != item["path"] or binding["sha256"] != item["sha256"] or item["lifecycle_state"] != "admitted":
            raise ValueError(f"definition binding drift: {ident}")
    decision = checked(bindings["admission-decision"]["path"], bindings["admission-decision"]["sha256"])
    if decision.get("decision_id") != bundle["decision_id"]:
        raise ValueError("decision binding mismatch")
    bootstrap_decision = checked(bindings["bootstrap-decision"]["path"], bindings["bootstrap-decision"]["sha256"])
    bootstrap_receipt = checked(bindings["bootstrap-application-receipt"]["path"], bindings["bootstrap-application-receipt"]["sha256"])
    if bootstrap_decision.get("decision_id") != bootstrap["decision_id"] or bootstrap_decision.get("status") != "owner-admitted" or bootstrap_receipt.get("result") != "PASS":
        raise ValueError("bootstrap admission not established")
    if bundle["bundle_id"] != module["current_integration"]["operational_foundation_bundle_ref"]:
        raise ValueError("module points to a different foundation bundle")
    if bootstrap["bundle_id"] != module["current_integration"]["project_bootstrap_bundle_ref"]:
        raise ValueError("module points to a different bootstrap bundle")
    if bundle["counts"]["history_streams_declared"] != 2:
        raise ValueError("history count changed")
    history = checked(bindings["history-declarations"]["path"], bindings["history-declarations"]["sha256"])
    if [(x["history_class"], x["state"], x["cursor"], x["runtime_active"]) for x in history["streams"]] != [
        ("semantic", "initialized-empty", 0, False), ("governance", "initialized-empty", 0, False)
    ]:
        raise ValueError("history baseline changed")
    if history["project_state_ref"] != module["current_integration"]["initial_project_state_ref"]:
        raise ValueError("project state binding mismatch")
    bootstrap_by_kind = {item["semantic_kind"]: item for item in bootstrap_artifacts["entries"]}
    semantic = checked(bootstrap_by_kind["project-semantic-event-history"]["admitted_instance_path"], bootstrap_by_kind["project-semantic-event-history"]["sha256"])["payload"]
    governance = checked(bootstrap_by_kind["project-governance-event-history"]["admitted_instance_path"], bootstrap_by_kind["project-governance-event-history"]["sha256"])["payload"]
    successor_state = checked(bootstrap_by_kind["project-state"]["admitted_instance_path"], bootstrap_by_kind["project-state"]["sha256"])["payload"]
    if len(semantic["events"]) != 1 or len(governance["events"]) != 1:
        raise ValueError("bootstrap event count changed")
    semantic_event, governance_event = semantic["events"][0], governance["events"][0]
    if semantic_event["cursor"] != 1 or governance_event["governance_cursor"] != 1:
        raise ValueError("bootstrap event cursor changed")
    if governance_event["semantic_event_ref"]["semantic_event_digest"] != semantic_event["event_digest"] or governance_event["semantic_event_ref"]["semantic_event_id"] != semantic_event["event_id"]:
        raise ValueError("governance event is not bound to the semantic event")
    if semantic_event["predecessor_state_ref"] != module["current_integration"]["initial_project_state_ref"] or semantic_event["resulting_state_ref"] != module["current_integration"]["current_admitted_project_state_ref"]:
        raise ValueError("semantic event state transition mismatch")
    if successor_state["cursor"] != "decision:0071" or bootstrap["decision_id"] in successor_state["decision_refs"]:
        raise ValueError("successor includes its own admission decision")
    if bootstrap_receipt["materials"]["bundle_sha256"] != bindings["bootstrap-bundle"]["sha256"]:
        raise ValueError("application receipt bundle digest mismatch")
    manifests = {}
    for binding_id, admitted_bundle in (("foundation-bundle", bundle), ("bootstrap-bundle", bootstrap)):
        bundle_dir = Path(bindings[binding_id]["path"]).parent
        manifest = {x["path"]: x["sha256"] for x in admitted_bundle["files"]}
        manifests[binding_id] = (bundle_dir, manifest)
        for item in admitted_bundle["files"]:
            path = ROOT / bundle_dir / item["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError(f"bundle manifest mismatch: {path}")
    for overlay, admitted_bundle, binding_id in ((artifacts, bundle, "foundation-bundle"), (relations, bundle, "foundation-bundle"),
                                                (bootstrap_artifacts, bootstrap, "bootstrap-bundle"), (bootstrap_relations, bootstrap, "bootstrap-bundle")):
        if overlay["decision_id"] != admitted_bundle["decision_id"] or overlay["count"] != len(overlay["entries"]):
            raise ValueError("admission overlay mismatch")
        bundle_dir, manifest = manifests[binding_id]
        for raw_entry in overlay["entries"]:
            entry = normalize(raw_entry)
            for path_key, digest_key in (("source_path", "source_sha256"), ("admitted_instance_path", "admitted_instance_sha256")):
                checked(entry[path_key], entry[digest_key])
            relative = str(Path(entry["admitted_instance_path"]).relative_to(bundle_dir))
            if manifest[relative] != entry["admitted_instance_sha256"]:
                raise ValueError(f"overlay and bundle manifest differ: {relative}")
    kind_registry = checked(bindings["relation-kind-registry"]["path"], bindings["relation-kind-registry"]["sha256"])
    kinds = {item["relation_kind_ref"]: item for item in kind_registry["entries"]}
    admitted_nodes = {item["identity_ref"]: item["semantic_kind"] for item in artifacts["entries"] + bootstrap_artifacts["entries"]}
    for raw_entry in relations["entries"] + bootstrap_relations["entries"]:
        entry = normalize(raw_entry)
        kind = kinds[entry["relation_kind_ref"]]
        if kind["lifecycle_state"] != "admitted-current":
            raise ValueError(f"relation kind is not admitted-current: {entry['relation_kind_ref']}")
        kind_record = checked(kind["instance_path"], kind["instance_sha256"])
        record = checked(entry["admitted_instance_path"], entry["admitted_instance_sha256"])
        payload = record["payload"]
        pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
        if pair not in kind_record["payload"]["allowed_endpoint_pairs"]:
            raise ValueError(f"relation endpoint pair is not closed: {entry['relation_id']}")
        if admitted_nodes.get(entry["source_ref"]) != pair["source_kind"] or admitted_nodes.get(entry["target_ref"]) != pair["target_kind"]:
            raise ValueError(f"relation endpoint instance is not in the foundation: {entry['relation_id']}")
        if payload["relation_kind_ref"] != entry["relation_kind_ref"] or payload["source"]["ref"] != entry["source_ref"] or payload["target"]["ref"] != entry["target_ref"]:
            raise ValueError(f"relation overlay differs from record: {entry['relation_id']}")
        if not set(kind["required_qualifier_axes"]).issubset(payload["qualifiers"]):
            raise ValueError(f"missing relation qualifier: {entry['relation_id']}")
    views = project_all()
    if len(views) != 12 or len({v["subject_ref"] for v in views}) != 12:
        raise ValueError("expected twelve unique artifact views")
    schema = read_json(HERE / "posture.schema.json")
    for view in views:
        jsonschema.Draft202012Validator(schema).validate(view)
    capability = next(v for v in views if v["independent_facets"]["kind"] == "product-capability")
    if capability != read_json(HERE / "examples/product-capability-posture.json"):
        raise ValueError("worked example differs from live projection")
    if (capability["authority"]["effective_instance_state"], capability["lifecycle"]["domain_status"],
        capability["lifecycle"]["realization_binding_refs"], capability["lifecycle"]["runtime_effect_of_admission_decision"]) != ("admitted-current", "draft", [], "none"):
        raise ValueError("capability lifecycle layers collapsed")
    initial = next(v for v in views if v["subject_ref"] == module["current_integration"]["initial_project_state_ref"])
    successor = next(v for v in views if v["subject_ref"] == module["current_integration"]["current_admitted_project_state_ref"])
    if initial["authority"]["effective_instance_state"] != "admitted-historical" or successor["authority"]["effective_instance_state"] != "admitted-current":
        raise ValueError("Project State predecessor/current transition collapsed")
    if successor != read_json(HERE / "examples/project-state-successor-posture.json"):
        raise ValueError("successor example differs from live projection")
    if successor["project_history_at_bootstrap_bundle"]["semantic_cursor"] != 1 or successor["project_history_at_bootstrap_bundle"]["governance_cursor"] != 1:
        raise ValueError("bootstrap history cursor mismatch")
    print(f"valid candidate module; {len(bindings)} source bindings; {len(module['canonical_definition_refs'])} current definitions; 12 artifact views; 15 relation records; examples match")


if __name__ == "__main__":
    main()
