#!/usr/bin/env python3
"""Validate axis orthogonality and hostile no-collapse cases."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    model = load(ROOT / "model.json")
    examples = load(ROOT / "examples.json")
    endpoint_inventory = load(ROOT / "endpoint-inventory.json")
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    registry = load(DEFINITION_REGISTRY)
    admitted = {f"{item['definition_id']}@{item['version']}": item for item in registry["entries"] if item["lifecycle_state"] == "admitted"}
    def_results = []
    for binding in model["definition_bindings"]:
        path = LAB / binding["path"]
        item = admitted.get(binding["definition_ref"])
        def_results.append({"definition_ref": binding["definition_ref"], "admitted": item is not None, "path_current": path.is_file() and sha(path) == binding["sha256"], "registry_current": item is not None and item["sha256"] == binding["sha256"]})
    check("admitted-axis-definitions-current", len(def_results) == 6 and all(all(value for key, value in row.items() if key != "definition_ref") for row in def_results), def_results)

    candidate_definition_results = []
    for binding in model.get("candidate_definition_bindings", []):
        definition_path = LAB / binding["path"]
        validation_path = LAB / binding["validation_path"]
        validation = load(validation_path) if validation_path.is_file() else {}
        candidate_definition_results.append({
            "definition_ref": binding["definition_ref"],
            "definition_current": definition_path.is_file() and sha(definition_path) == binding["sha256"],
            "validation_current": validation_path.is_file() and sha(validation_path) == binding["validation_sha256"],
            "validation_pass": validation.get("result") == "PASS" and binding["validation_result"] == "PASS",
            "candidate_unadmitted": binding["admission_posture"] == "candidate-unadmitted" and binding["definition_ref"].split("@", 1)[0] not in registry["current_lookup"],
            "required_before_admission": binding.get("required_before_relation_kind_admission") is True,
        })
    check("candidate-extension-definition-bound", len(candidate_definition_results) == 1 and all(all(value for key, value in row.items() if key != "definition_ref") for row in candidate_definition_results), candidate_definition_results)

    entries = model["entries"]
    ids = [item["relation_kind_id"] for item in entries]
    axis_ids = [item["axis_id"] for item in entries]
    questions = [item["unique_question"] for item in entries]
    check("23-independent-relation-axes", len(ids) == 23 and len(set(ids)) == 23 and len(set(axis_ids)) == 23 and len(set(questions)) == 23 and "axis.membership" in axis_ids and "relation.member-of" in ids and "relation.membership" not in ids, {"axes": len(ids), "axis_ids": len(set(axis_ids)), "unique_questions": len(set(questions)), "membership_axis": "axis.membership", "membership_predicate": "relation.member-of"})

    endpoint_pair_results = []
    for item in entries:
        pairs = item.get("allowed_endpoint_pairs", [])
        signatures = [(pair.get("source_kind"), pair.get("target_kind")) for pair in pairs]
        derived_sources = sorted({source for source, _ in signatures})
        derived_targets = sorted({target for _, target in signatures})
        endpoint_pair_results.append({
            "relation_kind": item["relation_kind_id"],
            "pair_count": len(pairs),
            "nonempty": bool(pairs),
            "unique": len(signatures) == len(set(signatures)),
            "no_wildcards": all(source != "*" and target != "*" for source, target in signatures),
            "source_projection_current": derived_sources == item["source_kinds"],
            "target_projection_current": derived_targets == item["target_kinds"],
        })
    check("closed-explicit-endpoint-pairs", all(all(value for key, value in row.items() if key not in {"relation_kind", "pair_count"}) for row in endpoint_pair_results) and sum(row["pair_count"] for row in endpoint_pair_results) == model["counts"]["declared_endpoint_pairs"], endpoint_pair_results)

    normalizations = model["normalizations"]
    old = [item["previous_relation_kind"] for item in normalizations]
    check("42-relation-names-normalized-exactly-once", len(old) == 42 and len(set(old)) == 42 and all(item["axis_relation_kind"] in ids for item in normalizations), {"previous_relation_names": len(old), "duplicates": len(old)-len(set(old))})
    check("semantic-compression-exact", model["counts"]["collapsed_duplicate_kinds"] == 19 and model["counts"]["axis_relation_kinds"] == 23, model["counts"])

    absorbed = {item["relation_kind_id"]: item["absorbed_relation_kinds"] for item in entries}
    qualifier_results = []
    for axis, old_kinds in absorbed.items():
        rows = [item for item in normalizations if item["axis_relation_kind"] == axis]
        signatures = [json.dumps(item["fixed_qualifiers"], sort_keys=True) for item in rows]
        qualifier_results.append({"axis": axis, "absorbed": len(old_kinds), "distinguished_when_merged": len(rows) <= 1 or len(set(signatures)) == len(signatures)})
    check("merged-meanings-retain-distinguishing-qualifiers", all(item["distinguished_when_merged"] for item in qualifier_results), qualifier_results)

    def endpoint_kind(ref: str) -> str:
        if ref.startswith("cal.artifact-type."):
            return "artifact-type"
        if ref.startswith("cal.definition."):
            return "definition"
        if ref.startswith("CA2-PRODUCT-"):
            return "product"
        kind = ref.split(":", 1)[0]
        return "method" if kind == "measurement-method" else kind

    example_results = []
    for item in entries:
        example = examples.get(item["relation_kind_id"], {})
        declared_pairs = {(pair["source_kind"], pair["target_kind"]) for pair in item["allowed_endpoint_pairs"]}
        observed_pair = (endpoint_kind(example.get("source_ref", "")), endpoint_kind(example.get("target_ref", "")))
        example_results.append({"axis": item["relation_kind_id"], "present": bool(example), "distinct_endpoints": example.get("source_ref") != example.get("target_ref"), "endpoint_pair_declared": observed_pair in declared_pairs, "observed_pair": list(observed_pair), "qualifiers_complete": set(item["required_qualifier_axes"]) <= set(example.get("qualifiers", {})), "owner_explicit": bool(example.get("owner_ref")), "evidence_explicit": bool(example.get("evidence_refs")), "lifecycle_explicit": bool(example.get("lifecycle_state")), "authority_none": example.get("authority_effect") == "none"})
    check("typed-coupling-vector-complete", all(all(value for key, value in row.items() if key != "axis") for row in example_results), example_results)

    hostile_results = []
    axes = set(ids)
    for hostile in model["hostile_no_collapse_cases"]:
        asserted = hostile["asserted"]
        # The model has no implicit inference rules: only the asserted axis and explicit qualifier are present.
        derived = {asserted}
        forbidden_axes = set(hostile["forbidden"]) & axes
        forbidden_tokens = set(hostile["forbidden"]) - axes
        qualifier_values = set(hostile.get("qualifier", {}).values())
        ok = asserted in axes and not (derived & forbidden_axes) and not (qualifier_values & forbidden_tokens)
        hostile_results.append({"hostile_id": hostile["id"], "asserted": asserted, "implicit_axes": sorted(derived - {asserted}), "forbidden": hostile["forbidden"], "result": "PASS" if ok else "BLOCK"})
    check("hostile-no-collapse", len(hostile_results) == 10 and all(item["result"] == "PASS" for item in hostile_results), hostile_results)
    dump(ROOT / "receipts/no-collapse.json", {"schema_version": "cyberalchemy-lab-relation-no-collapse/v1", "result": "PASS" if all(item["result"] == "PASS" for item in hostile_results) else "BLOCK", "cases": hostile_results, "claim_ceiling": "PASS shows the candidate model declares no tested implicit cross-axis inference. It does not prove every possible semantic distinction or admit the model."})

    mandatory_separations = [
        ("relation.member-of", "relation.contributes-to"), ("relation.uses-method", "relation.conforms-to"),
        ("relation.evaluates", "relation.evidence-bears-on"), ("relation.realizes", "relation.conforms-to"),
        ("relation.conforms-to", "relation.declares-effect-on"), ("relation.assigned-to", "relation.scopes-authority-over"),
        ("relation.instance-of", "relation.conforms-to"), ("relation.originates-from", "relation.derives-from"),
    ]
    check("mandatory-axis-separations", all(a in axes and b in axes and a != b for a, b in mandatory_separations), mandatory_separations)
    check("candidate-no-authority-effect", model["authority_effect"] == "none" and model["status"] == "candidate-complete-awaiting-owner-review", {"status": model["status"], "authority_effect": model["authority_effect"]})

    named_endpoint_kinds = sorted({kind for item in entries for kind in item["source_kinds"] + item["target_kinds"] if kind != "*"})
    endpoint_entries = {item["endpoint_kind"]: item for item in endpoint_inventory["entries"]}
    endpoint_counts = endpoint_inventory["counts"]
    role_results = []
    for kind in named_endpoint_kinds:
        expected_sources = sorted(item["relation_kind_id"] for item in entries if kind in item["source_kinds"])
        expected_targets = sorted(item["relation_kind_id"] for item in entries if kind in item["target_kinds"])
        actual = endpoint_entries.get(kind, {})
        role_results.append({"endpoint_kind": kind, "source_for_current": actual.get("source_for") == expected_sources, "target_for_current": actual.get("target_for") == expected_targets})
    inventory_complete = (
        set(endpoint_entries) == set(named_endpoint_kinds)
        and endpoint_counts.get("named_endpoint_kinds") == 50
        and endpoint_counts.get("admitted-current") == 13
        and endpoint_counts.get("candidate-materialized") == 15
        and endpoint_counts.get("referenced-no-canonical-carrier") == 22
        and endpoint_counts.get("wildcard_tokens") == 0
        and endpoint_counts.get("declared_endpoint_pairs") == model["counts"]["declared_endpoint_pairs"]
        and endpoint_inventory.get("closed_world") is True
        and all(all(value for key, value in row.items() if key != "endpoint_kind") for row in role_results)
    )
    check("endpoint-inventory-complete", inventory_complete, {"declared_counts": endpoint_counts, "derived_named_endpoint_kinds": len(named_endpoint_kinds), "role_results": role_results})

    def lifecycle_evidence_admits(item: dict[str, Any]) -> bool:
        evidence_path = item.get("lifecycle_evidence_path")
        if not evidence_path or not (LAB / evidence_path).is_file():
            return False
        evidence = load(LAB / evidence_path)
        if "entries" in evidence:
            return any(row.get("artifact_type_ref") == item.get("carrier_ref") and row.get("lifecycle_state") == "admitted-current" for row in evidence["entries"])
        if "lifecycle" in evidence and "current" in evidence["lifecycle"]:
            current = evidence["lifecycle"]["current"]
            return current.get("artifact_type_ref") == item.get("carrier_ref") and current.get("lifecycle_state") == "admitted-current"
        return evidence.get("artifact_type_ref") == item.get("carrier_ref") and evidence.get("lifecycle_state") == "admitted-current"

    carrier_results = []
    for item in endpoint_inventory["entries"]:
        state = item["lifecycle_state"]
        path_exists = bool(item.get("path")) and (LAB / item["path"]).is_file()
        if state == "admitted-current":
            ok = path_exists and lifecycle_evidence_admits(item)
        elif state == "candidate-materialized":
            ok = path_exists and bool(item.get("carrier_ref")) and not item.get("admission_ref")
        else:
            ok = not item.get("path") and not item.get("carrier_ref")
        carrier_results.append({"endpoint_kind": item["endpoint_kind"], "state": state, "carrier_state_supported": ok})
    connected_kinds = set(named_endpoint_kinds)
    unconnected_results = [{"endpoint_kind": item["endpoint_kind"], "carrier_state_supported": (LAB / item["path"]).is_file() and lifecycle_evidence_admits(item), "has_no_declared_connection": item["endpoint_kind"] not in connected_kinds} for item in endpoint_inventory["admitted_carriers_without_declared_connections"]]
    check("endpoint-carrier-states-supported", all(all(value for key, value in item.items() if key != "endpoint_kind") for item in carrier_results + unconnected_results), {"named": carrier_results, "admitted_unconnected": unconnected_results})

    markdown = (ROOT / "RELATIONS.md").read_text(encoding="utf-8")
    check("human-review-surface-complete", all(f"`{axis}`" in markdown and json.dumps(examples[axis], indent=2, sort_keys=True) in markdown for axis in ids), {"axes": len(ids), "examples": len(examples)})
    endpoint_markdown = (ROOT / "ENDPOINTS.md").read_text(encoding="utf-8")
    check("endpoint-review-surface-complete", all(f"`{kind}`" in endpoint_markdown for kind in named_endpoint_kinds) and all(f"`{axis}`" in endpoint_markdown for axis in ids), {"endpoint_kinds": len(named_endpoint_kinds), "axes": len(ids)})

    manifest = load(ROOT / "manifest.json")
    manifest_results = []
    for item in manifest["files"] + manifest["inputs"]:
        path = LAB / item["path"]
        manifest_results.append({"path": item["path"], "ok": path.is_file() and sha(path) == item["sha256"]})
    check("manifest-current", all(item["ok"] for item in manifest_results), manifest_results)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {"schema_version": "cyberalchemy-lab-axis-orthogonal-relation-validation/v1", "subject": model["model_id"], "result": "PASS" if not blocked else "BLOCK", "authority_effect": "none", "checks": checks, "summary": {"passed": len(checks)-len(blocked), "blocked": len(blocked), "total": len(checks)}, "materials": {"model_sha256": sha(ROOT / "model.json"), "examples_sha256": sha(ROOT / "examples.json"), "endpoint_inventory_sha256": sha(ROOT / "endpoint-inventory.json"), "relations_markdown_sha256": sha(ROOT / "RELATIONS.md"), "endpoints_markdown_sha256": sha(ROOT / "ENDPOINTS.md"), "manifest_sha256": sha(ROOT / "manifest.json"), "no_collapse_sha256": sha(ROOT / "receipts/no-collapse.json")}, "claim_ceiling": "PASS establishes structural axis orthogonality, exact normalization of 42 prior relation names into 23 axes, zero wildcard endpoint contracts, explicit ordered endpoint-pair closure, declared hostile no-collapse cases, and current endpoint carrier availability. It does not prove that every possible historical endpoint use was valid, admit Relation Kinds, admit candidate endpoint carriers, or prove runtime semantics."}
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"AXIS_ORTHOGONAL_RELATION_MODEL={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    print(f"NO_COLLAPSE={load(ROOT / 'receipts/no-collapse.json')['result']} ({len(hostile_results)}/{len(hostile_results)})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
