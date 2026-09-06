#!/usr/bin/env python3
"""Reusable schema and semantic checks for CML-07 identity carriers."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator


RELATION_SIGNATURES = {
    "contains_product": ("product", "product"),
    "coordinated_by": ("product", "project"),
    "embodies_method": ("product", "method"),
    "uses_method": ("project", "method"),
    "pursues_goal": ("project", "goal"),
}


def schema_errors(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    Draft202012Validator.check_schema(schema)
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema).iter_errors(instance),
            key=lambda item: list(item.absolute_path),
        )
    ]


def semantic_errors(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kind = instance.get("schema_version")
    if instance.get("status") != "candidate-unadmitted":
        errors.append("carrier status must remain candidate-unadmitted")
    if instance.get("authority_effect") != "none":
        errors.append("carrier authority_effect must remain none")

    if kind == "cyberalchemy-lab-product-identity/v1":
        if instance.get("product_id") != "CA2-PRODUCT-CRAFT":
            errors.append("Craft Product identity must be CA2-PRODUCT-CRAFT")
        if instance.get("lineage_ref") != "CAL-LINEAGE-CRAFT-PRODUCT-V1":
            errors.append("Craft Product must explicitly reference its lineage carrier")
    elif kind == "cyberalchemy-lab-project-identity/v1":
        if instance.get("project_id") != "CA2-PROJECT-CRAFT":
            errors.append("Craft Project identity must be CA2-PROJECT-CRAFT")
    elif kind == "cyberalchemy-lab-method-binding/v1":
        if instance.get("method_ref") == instance.get("subject_ref"):
            errors.append("Method and binding subject identities must remain distinct")
        if (instance.get("method_ref"), instance.get("subject_ref"), instance.get("subject_kind")) != (
            "CAV2-D20",
            "CA2-PRODUCT-CRAFT",
            "product",
        ):
            errors.append("Craft Method Binding must bind CAV2-D20 to the Craft Product")
    elif kind == "cyberalchemy-lab-goal/v1":
        if instance.get("goal_id") != "CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION":
            errors.append("Craft foundation Goal identity does not match its admitted source")
    elif kind == "cyberalchemy-lab-identity-lineage/v1":
        if instance.get("lineage_kind") != "same-product-renamed":
            errors.append("Craft lineage must retain same-product-renamed posture")
        if instance.get("subject_kind") != "product":
            errors.append("Craft rename lineage cannot be substituted with Context lineage")
        if instance.get("predecessor_ref") == instance.get("successor_ref"):
            errors.append("Lineage identity endpoints must remain explicit and non-collapsed")
        if instance.get("successor_ref") != "CA2-PRODUCT-CRAFT":
            errors.append("Craft lineage successor must resolve to CA2-PRODUCT-CRAFT")
    elif kind == "cyberalchemy-lab-identity-graph/v1":
        nodes = instance.get("nodes", [])
        relations = instance.get("relations", [])
        refs = [item.get("identity_ref") for item in nodes]
        relation_ids = [item.get("relation_id") for item in relations]
        if len(refs) != len(set(refs)):
            errors.append("identity graph node references must be unique")
        if len(relation_ids) != len(set(relation_ids)):
            errors.append("identity graph relation identities must be unique")
        kinds = {item.get("identity_ref"): item.get("identity_kind") for item in nodes}
        for relation in relations:
            source = relation.get("source_ref")
            target = relation.get("target_ref")
            relation_kind = relation.get("relation_kind")
            if source not in kinds or target not in kinds:
                errors.append(f"relation {relation.get('relation_id')} has an unresolved endpoint")
                continue
            expected = RELATION_SIGNATURES.get(relation_kind)
            observed = (kinds[source], kinds[target])
            if expected != observed:
                errors.append(
                    f"relation {relation.get('relation_id')} has signature {observed}, expected {expected}"
                )
    else:
        errors.append(f"unsupported carrier schema_version: {kind}")
    return errors


def cohort_errors(carriers: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    product = carriers["product"]
    project = carriers["project"]
    method = carriers["method-binding"]
    goal = carriers["goal"]
    graph = carriers["identity-graph"]
    lineage = carriers["identity-lineage"]

    identities = [
        product["product_id"],
        project["project_id"],
        method["binding_id"],
        goal["goal_id"],
        graph["graph_id"],
        lineage["lineage_id"],
        method["method_ref"],
    ]
    if len(identities) != len(set(identities)):
        errors.append("Product, Project, Method Binding, Goal, Graph, Lineage, and Method identities must be distinct")
    if product["lineage_ref"] != lineage["lineage_id"] or lineage["successor_ref"] != product["product_id"]:
        errors.append("Product and lineage carriers do not resolve bidirectionally")
    if method["subject_ref"] != product["product_id"]:
        errors.append("Method Binding subject does not resolve to the Product carrier")

    expected_nodes = {
        ("CA2-PRODUCT-CYBERALCHEMY", "product"),
        (product["product_id"], "product"),
        (project["project_id"], "project"),
        (method["method_ref"], "method"),
        (goal["goal_id"], "goal"),
    }
    observed_nodes = {(item["identity_ref"], item["identity_kind"]) for item in graph["nodes"]}
    if observed_nodes != expected_nodes:
        errors.append("Identity Graph node set does not match the exact CML-07 endpoint set")

    expected_relations = {
        ("contains_product", "CA2-PRODUCT-CYBERALCHEMY", product["product_id"]),
        ("coordinated_by", product["product_id"], project["project_id"]),
        ("embodies_method", product["product_id"], method["method_ref"]),
        ("uses_method", project["project_id"], method["method_ref"]),
        ("pursues_goal", project["project_id"], goal["goal_id"]),
    }
    observed_relations = {
        (item["relation_kind"], item["source_ref"], item["target_ref"])
        for item in graph["relations"]
    }
    if observed_relations != expected_relations:
        errors.append("Identity Graph relation set does not match the five required CML-07 relations")

    forbidden = {"context_id", "bounded_context_ref", "craft_context_ref", "owner_inference"}
    for name, carrier in carriers.items():
        overlap = forbidden.intersection(carrier)
        if overlap:
            errors.append(f"{name} contains forbidden inferred labels: {sorted(overlap)}")
    return errors
