#!/usr/bin/env python3
"""Validate the admitted-root navigation projection without granting authority."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import materialize


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
PROFILE = HERE / "profile.json"
SOURCES = HERE / "sources.json"
SCHEMA = HERE / "schema.json"
NAVIGATION = HERE / "navigation.json"
RECEIPTS = HERE / "receipts"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def semantic_errors(nav: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if canonical(nav) != canonical(expected):
        errors.append("deterministic-projection-parity-mismatch")
    binding = nav.get("authority_binding", {})
    if binding.get("validation_result") != "PASS" or binding.get("stage_state") != "ROOT_ADMITTED" or binding.get("authority_effect") != "root-admission-only":
        errors.append("admitted-root-authority-binding-mismatch")
    root = nav.get("root", {})
    if root.get("component_id") != "CAL-LAB-ONTOLOGY-SYSTEM" or root.get("system_id") != "cal.ontology-system.lab-cohesion" or root.get("admission_state") != "admitted":
        errors.append("root-identity-or-state-mismatch")
    if root.get("replay_source") is not False:
        errors.append("root-replay-source-collapse")

    components = nav.get("components", [])
    component_ids = [item.get("component_id") for item in components]
    if len(components) != 14 or len(component_ids) != len(set(component_ids)):
        errors.append("component-identity-closure-mismatch")
    root_components = [item for item in components if item.get("component_id") == "CAL-LAB-ONTOLOGY-SYSTEM"]
    if len(root_components) != 1 or root_components[0].get("effective_authority_state") != "admitted-root":
        errors.append("effective-root-state-mismatch")
    for item in components:
        if item.get("component_id") != "CAL-LAB-ONTOLOGY-SYSTEM" and item.get("effective_authority_state") != item.get("source_authority_state"):
            errors.append(f"child-authority-state-changed:{item.get('component_id')}")

    relations = nav.get("relations", [])
    relation_ids = [item.get("relation_id") for item in relations]
    if len(relations) != 15 or len(relation_ids) != len(set(relation_ids)):
        errors.append("relation-overlay-closure-mismatch")
    if any(item.get("effective_status") != "admitted-composition-overlay" for item in relations):
        errors.append("relation-overlay-state-mismatch")

    residues = nav.get("residue_routes", [])
    residue_ids = {item.get("residue_id") for item in residues}
    expected_residue_ids = {item.get("residue_id") for item in expected.get("residue_routes", [])}
    if residue_ids != expected_residue_ids or len(residues) != 5:
        errors.append("residue-route-closure-mismatch")
    if any(not item.get("owner_route") or not item.get("route_id") for item in residues):
        errors.append("residue-owner-route-missing")

    reviews = nav.get("review_routes", [])
    if len(reviews) != 10 or len({item.get("group_id") for item in reviews}) != 10:
        errors.append("review-route-closure-mismatch")
    unresolved = [item for item in reviews if item.get("route_status") == "blocked-owner-unresolved"]
    if len(unresolved) != 2 or any(item.get("owner_resolution_route") != "CyberAlchemy migration review owner" for item in unresolved):
        errors.append("review-owner-gap-mismatch")
    if any(item.get("authority_effect") != "none" or item.get("blocker_count", 0) < 1 for item in reviews):
        errors.append("review-route-authority-or-blocker-mismatch")

    lane_ids = set(nav.get("work_lanes", {}).get("runnable_product_construction_route_ids", []))
    lane_ids.update(item.get("route_id") for item in nav.get("work_lanes", {}).get("operational_support", []))
    if lane_ids != {item.get("route_id") for item in residues}:
        errors.append("two-lane-work-coverage-mismatch")
    if nav.get("authority_effect") != "none" or nav.get("source_direction", {}).get("projection_is_authority_source") is not False:
        errors.append("derived-projection-authority-inflation")
    if nav.get("canonical_truth_contract", {}).get("navigation_projection_is_replay_source") is not False:
        errors.append("navigation-replay-source-collapse")
    return errors


def validate() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    profile = load(PROFILE)
    sources = load(SOURCES)
    schema = load(SCHEMA)
    nav = load(NAVIGATION)
    profile_ok = (
        profile.get("package_id") == "cal.ontology-navigation.lab-cohesion"
        and profile.get("ontology_type") == "business-system-bridge"
        and profile.get("status") == "derived-from-admitted-root"
        and profile.get("authority_effect") == "none"
    )
    add("profile-boundary", profile_ok, [])

    source_failures = []
    for item in sources.get("sources", []):
        path = REPO / item.get("path", "")
        if not path.is_file() or sha256(path) != item.get("sha256"):
            source_failures.append(item.get("source_id"))
    add("selected-source-currentness", len(sources.get("sources", [])) == 5 and not source_failures, source_failures)

    schema_errors = sorted(Draft202012Validator(schema).iter_errors(nav), key=lambda error: list(error.path))
    add("navigation-schema", not schema_errors, [error.message for error in schema_errors])

    try:
        expected = materialize.build()
        build_error = None
    except Exception as error:  # fail closed with the exact materialization cause
        expected = {}
        build_error = str(error)
    add("deterministic-materialization", build_error is None and canonical(nav) == canonical(expected), build_error or [])

    semantics = semantic_errors(nav, expected) if build_error is None else ["materialization-not-evaluable"]
    add("navigation-and-route-semantics", not semantics, semantics)

    probes = []
    mutations = {
        "root-state-substitution": ("root", "admission_state", "candidate"),
        "root-replay-source-collapse": ("root", "replay_source", True),
        "child-admission-inflation": ("components", 1, "effective_authority_state", "admitted-root"),
        "relation-removal": ("relations", "pop"),
        "residue-owner-removal": ("residue_routes", 0, "owner_route", ""),
        "projection-authority-inflation": (None, "authority_effect", "root-admission-only"),
        "runtime-adoption-inference": ("authority_binding", "authority_effect", "runtime-adoption"),
    }
    for probe_id, mutation in mutations.items():
        mutated = copy.deepcopy(nav)
        if len(mutation) == 2 and mutation[1] == "pop":
            mutated[mutation[0]].pop()
        elif len(mutation) == 4:
            section, index, key, value = mutation
            mutated[section][index][key] = value
        else:
            section, key, value = mutation
            if section is None:
                mutated[key] = value
            else:
                mutated[section][key] = value
        caught = bool(semantic_errors(mutated, expected))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    return {
        "schema_version": "cyberalchemy-lab-admitted-ontology-navigation-validation/v1",
        "package_id": profile.get("package_id"),
        "projection_id": nav.get("projection_id"),
        "result": result,
        "stage_state": "ADMITTED_ROOT_NAVIGATION_READY" if result == "PASS" else "not_evaluable",
        "failed_checks": failed,
        "checks": checks,
        "counts": {
            "components": len(nav.get("components", [])),
            "relations": len(nav.get("relations", [])),
            "residue_routes": len(nav.get("residue_routes", [])),
            "review_routes": len(nav.get("review_routes", [])),
            "unresolved_review_owners": sum(item.get("route_status") == "blocked-owner-unresolved" for item in nav.get("review_routes", [])),
        },
        "root_admission_observed": result == "PASS",
        "child_ontologies_admitted_by_projection": 0,
        "runtime_adopted": False,
        "activated": False,
        "migration_authorized": False,
        "publication_authorized": False,
        "deployment_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(path.relative_to(REPO)), "sha256": sha256(path)}
            for path in (PROFILE, SOURCES, SCHEMA, NAVIGATION, HERE / "materialize.py", HERE / "validate.py", HERE / "query.py", HERE / "test_navigation.py", HERE / "README.md")
        ] + [
            {"path": item["path"], "sha256": item["sha256"]}
            for item in sources["sources"]
        ],
        "claim_ceiling": "PASS proves that the derived navigation projection is byte-current with the admitted root, exactly preserves the 14-component and 15-relation graph, keeps every child authority state unchanged, and routes five residues plus ten review groups. It grants no new authority or operational effect.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.write_receipt:
        if result["result"] != "PASS":
            raise SystemExit("refusing to write a BLOCK receipt")
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        receipt = RECEIPTS / "validation.json"
        if receipt.exists():
            raise SystemExit("refusing to overwrite append-only validation receipt")
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result if not args.write_receipt else {
        "package_id": result["package_id"],
        "result": result["result"],
        "stage_state": result["stage_state"],
        "failed_checks": result["failed_checks"],
        "counts": result["counts"],
        "root_admission_observed": result["root_admission_observed"],
        "child_ontologies_admitted_by_projection": result["child_ontologies_admitted_by_projection"],
        "authority_effect": result["authority_effect"],
    }, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
