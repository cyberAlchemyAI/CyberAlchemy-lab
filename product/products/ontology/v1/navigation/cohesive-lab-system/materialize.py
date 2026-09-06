#!/usr/bin/env python3
"""Deterministically derive the admitted-root navigation projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
SOURCES = HERE / "sources.json"
OUTPUT = HERE / "navigation.json"
ROOT_COMPONENT = "CAL-LAB-ONTOLOGY-SYSTEM"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_map() -> dict[str, dict[str, Any]]:
    return {item["source_id"]: item for item in load(SOURCES)["sources"]}


def source_path(sources: dict[str, dict[str, Any]], source_id: str) -> Path:
    item = sources[source_id]
    path = REPO / item["path"]
    actual = sha256(path) if path.is_file() else "missing"
    if actual != item["sha256"]:
        raise ValueError(f"source drift: {source_id}: expected {item['sha256']}, got {actual}")
    return path


def build() -> dict[str, Any]:
    sources = source_map()
    decision = load(source_path(sources, "ROOT-ADMISSION-DECISION"))
    decision_validation = load(source_path(sources, "ROOT-ADMISSION-VALIDATION"))
    model = load(source_path(sources, "APPROVED-ONTOLOGY-SYSTEM"))
    inventory = load(source_path(sources, "LEGACY-ONTOLOGY-INVENTORY"))
    reviews = load(source_path(sources, "LEGACY-ONTOLOGY-REVIEWS"))

    inventory_by_key = {
        (item["ontology_id"], item["profile_path"]): item
        for item in inventory["packages"]
    }
    review_routes = []
    for review in reviews["entries"]:
        ontology_id = (
            "domainspec-product-ontology@1"
            if review["group_id"] == "domainspec-v2-lineage"
            else review["group_id"]
        )
        source_packages = [
            item for item in inventory["packages"]
            if item["ontology_id"] == ontology_id
        ]
        if not source_packages:
            raise ValueError(f"review group has no inventory packages: {review['group_id']}")
        owners = sorted({
            inventory_by_key[(item["ontology_id"], item["profile_path"])]["owner_route"]
            for item in source_packages
        })
        owner_route = owners[0] if len(owners) == 1 else " + ".join(owners)
        owner_resolved = owner_route != "unresolved"
        review_routes.append({
            "route_id": f"CAL-REVIEW-ROUTE-{review['group_id'].upper().replace('.', '-').replace('_', '-')}",
            "group_id": review["group_id"],
            "owner_route": owner_route,
            "owner_resolution_route": None if owner_resolved else "CyberAlchemy migration review owner",
            "route_status": "ready-for-owner-review" if owner_resolved else "blocked-owner-unresolved",
            "blocker_count": review["blocker_count"],
            "source_profiles": [item["profile_path"] for item in source_packages],
            "recommended_disposition": review["recommended_disposition"],
            "authority_effect": "none",
        })

    lane_by_residue = {
        "CAL-RES-DOMAINSPEC-SUCCESSOR-COLLISION": ("product-construction", "DomainSpec successor selection"),
        "CAL-RES-ONTOLOGY-REVIEWS-BLOCKED": ("product-construction", "review-led successor construction"),
        "CAL-RES-ONTOLOGY-PACKAGE-TYPE-UNADMITTED": ("product-construction", "Ontology Package Artifact Type product test and admission"),
        "CAL-RES-PRODUCT-RUNTIME-REALIZATION-UNPROVEN": ("product-construction", "package-to-event/runtime binding prototype and product test"),
        "CAL-RES-STALE-STATUS-PROJECTION": ("operational-support", "derived status-projection refresh"),
    }
    residue_routes = []
    for residue in model["residue"]:
        lane, affected_stage = lane_by_residue[residue["residue_id"]]
        route = {
            **residue,
            "route_id": f"CAL-ROUTE-{residue['residue_id'].removeprefix('CAL-RES-')}",
            "lane": lane,
            "affected_stage": affected_stage,
            "route_status": "ready-for-owner-action",
            "authority_effect": "none",
        }
        if residue["residue_id"] == "CAL-RES-ONTOLOGY-REVIEWS-BLOCKED":
            route["route_status"] = "partially-routable-owner-resolution-required"
            route["review_route_count"] = len(review_routes)
            route["resolved_owner_route_count"] = sum(item["route_status"] == "ready-for-owner-review" for item in review_routes)
            route["unresolved_owner_route_count"] = sum(item["route_status"] == "blocked-owner-unresolved" for item in review_routes)
        residue_routes.append(route)

    components = []
    for item in model["components"]:
        components.append({
            "component_id": item["component_id"],
            "kind": item["kind"],
            "branch": item["branch"],
            "source_authority_state": item["authority_state"],
            "effective_authority_state": "admitted-root" if item["component_id"] == ROOT_COMPONENT else item["authority_state"],
            "owner_route": item["owner_route"],
            "source_refs": item["source_refs"],
        })
    relations = [{
        "relation_id": item["relation_id"],
        "type": item["type"],
        "source": item["source"],
        "target": item["target"],
        "source_status": item["status"],
        "effective_status": "admitted-composition-overlay",
        "source_refs": item["source_refs"],
    } for item in model["relations"]]

    product_route_ids = [item["route_id"] for item in residue_routes if item["lane"] == "product-construction"]
    operational_route_ids = [item["route_id"] for item in residue_routes if item["lane"] == "operational-support"]
    return {
        "schema_version": "cyberalchemy-lab-admitted-ontology-navigation/v1",
        "projection_id": "cal.ontology-navigation.lab-cohesion",
        "version": "1.0.0",
        "status": "derived-from-admitted-root",
        "ontology_type": "business-system-bridge",
        "authority_effect": "none",
        "authority_binding": {
            "decision_id": decision["decision_id"],
            "decision_path": sources["ROOT-ADMISSION-DECISION"]["path"],
            "decision_sha256": sources["ROOT-ADMISSION-DECISION"]["sha256"],
            "validation_path": sources["ROOT-ADMISSION-VALIDATION"]["path"],
            "validation_sha256": sources["ROOT-ADMISSION-VALIDATION"]["sha256"],
            "validation_result": decision_validation["result"],
            "stage_state": decision_validation["stage_state"],
            "authority_effect": decision["authority_effect"],
        },
        "root": {
            "component_id": decision["root_admission"]["root_component_id"],
            "system_id": decision["root_admission"]["root_system_id"],
            "admission_state": decision["root_admission"]["state"],
            "navigation_authority": decision["root_admission"]["navigation_authority"],
            "composition_overlay_authority": decision["root_admission"]["composition_overlay_authority"],
            "source_model_path": sources["APPROVED-ONTOLOGY-SYSTEM"]["path"],
            "source_model_sha256": sources["APPROVED-ONTOLOGY-SYSTEM"]["sha256"],
            "replay_source": False,
        },
        "components": components,
        "relations": relations,
        "residue_routes": residue_routes,
        "review_routes": review_routes,
        "work_lanes": {
            "current_product_construction_frontier": "Resolve owner-ready ontology residues while independently prototyping and testing the package-to-event/runtime binding.",
            "runnable_product_construction_route_ids": product_route_ids,
            "operational_support": [{
                "route_id": route_id,
                "owner_route": next(item["owner_route"] for item in residue_routes if item["route_id"] == route_id),
                "affected_stage": next(item["affected_stage"] for item in residue_routes if item["route_id"] == route_id),
            } for route_id in operational_route_ids],
            "causal_construction_blockers": [{
                "blocker": "review-group-owner-unresolved",
                "affected_review_groups": [item["group_id"] for item in review_routes if item["route_status"] == "blocked-owner-unresolved"],
                "owner_route": "CyberAlchemy migration review owner",
                "does_not_block": "other owner-ready residue work or the package-to-event/runtime prototype",
            }],
            "deferred_operational_residue": [
                "commit, publication, release, deployment, migration, cutover, and source retirement remain separately authorized effects"
            ],
        },
        "canonical_truth_contract": {
            **model["canonical_truth_contract"],
            "navigation_projection_is_replay_source": False,
        },
        "query_contract": {
            "operations": [
                "summary",
                "list-components",
                "get-component",
                "list-relations",
                "get-relation",
                "list-residue",
                "route-residue",
                "list-review-routes",
                "route-review",
                "get-source-ontology"
            ],
            "unknown_identity_behavior": "BLOCK with nonzero exit",
            "duplicate_ontology_identity_behavior": "return-all-profile-qualified-results",
            "authority_behavior": "validate all selected source digests before answering",
        },
        "source_direction": {
            "canonical_runtime_truth": "per-subject ordered node and relation event histories",
            "authority_source": sources["ROOT-ADMISSION-DECISION"]["path"],
            "approved_graph_source": sources["APPROVED-ONTOLOGY-SYSTEM"]["path"],
            "derived_projection": "navigation.json",
            "projection_is_authority_source": False,
        },
        "claim_ceiling": "This derived projection makes the admitted cohesive root usable for source-current navigation and owner routing. It does not admit child ontologies, resolve residue, select a DomainSpec profile, become a replay source, adopt or activate a runtime, or authorize migration, cutover, publication, release, deployment, source retirement, credentials, destructive action, or external effects.",
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
