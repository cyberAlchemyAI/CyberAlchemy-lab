#!/usr/bin/env python3
"""Validate and query the non-authoritative cohesive Lab ontology candidate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
MODEL_PATH = HERE / "ontology-system.json"
CANDIDATE_PATH = HERE / "candidate.json"
SCHEMA_PATH = HERE / "schema.json"
RECEIPT_PATH = HERE / "receipts" / "validation.json"
ROOT_COMPONENT = "CAL-LAB-ONTOLOGY-SYSTEM"
ALLOWED_RELATIONS = {
    "realized_by",
    "depends_on",
    "constrained_by",
    "observed_by",
    "tested_by",
    "drifts_from",
    "traced_to",
}
REQUIRED_BRANCHES = {"business", "system", "bridge", "governance", "context"}
EXPECTED_DECISIONS = {
    "SRC-ONTOLOGY-PRODUCT-APPROVAL": ("selected", "product-approval-only"),
    "SRC-D65-PRODUCT-ADMISSION": ("selected", "admit-exact-d65-s2-product-ontology-only"),
    "SRC-D65-BUSINESS-ADMISSION": ("selected", "admit-exact-d65-s3-business-ontology-only"),
    "SRC-D65-DOMAINSPEC-ADMISSION": ("selected", "admit-exact-d65-s4-domainspec-source-only"),
    "SRC-D65-SYSTEM-ADMISSION": ("selected", "admit-exact-d65-s5-system-ontology-only"),
    "SRC-D65-BINDING-ACCEPTANCE": ("selected", "accept-exact-d65-s6-implementation-binding-only"),
    "SRC-D65-INTEGRATION-ADMISSION": (
        "selected",
        "admit-exact-d65-s8-epoch-and-authorize-reviewed-cutover-candidate-preparation-only",
    ),
    "SRC-CONTEXT-ADMISSION": ("owner-admitted", "four-exact-context-language-artifacts-admitted"),
    "SRC-CONTEXT-MAP-ADMISSION": (
        "owner-admitted",
        "one-exact-context-map-and-map-local-relationship-pattern-admitted",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _unique(values: list[str], label: str, errors: list[str]) -> None:
    if len(values) != len(set(values)):
        errors.append(f"{label}: duplicate identities")


def validate_model(
    model: dict[str, Any], candidate: dict[str, Any], *, check_files: bool = True
) -> list[str]:
    errors: list[str] = []
    if model.get("schema_version") != "cyberalchemy-lab-cohesive-ontology-system/v1":
        errors.append("schema-version: unsupported")
    if model.get("system_id") != "cal.ontology-system.lab-cohesion":
        errors.append("system-id: mismatch")
    if model.get("ontology_type") != "business-system-bridge":
        errors.append("ontology-type: business-system-bridge required")
    if model.get("status") != "testable-product-candidate":
        errors.append("status: testable-product-candidate required")
    if model.get("authority_effect") != "none":
        errors.append("authority-effect: candidate must remain none")

    sources = model.get("sources", [])
    source_ids = [item.get("source_id", "") for item in sources]
    _unique(source_ids, "sources", errors)
    source_map = {item.get("source_id"): item for item in sources}
    for item in sources:
        rel = Path(item.get("path", ""))
        if not rel.parts or rel.is_absolute() or ".." in rel.parts:
            errors.append(f"source-path: unsafe path for {item.get('source_id')}")
            continue
        digest = item.get("sha256", "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append(f"source-digest: malformed for {item.get('source_id')}")
        if check_files:
            path = REPO / rel
            if not path.is_file():
                errors.append(f"source-currentness: missing {rel}")
            elif sha256(path) != digest:
                errors.append(f"source-currentness: digest drift {rel}")

    components = model.get("components", [])
    component_ids = [item.get("component_id", "") for item in components]
    _unique(component_ids, "components", errors)
    component_map = {item.get("component_id"): item for item in components}
    if ROOT_COMPONENT not in component_map:
        errors.append("root-component: missing")
    branches = {item.get("branch") for item in components}
    if not REQUIRED_BRANCHES.issubset(branches):
        errors.append("branch-coverage: business/system/bridge/governance/context required")
    for item in components:
        refs = item.get("source_refs", [])
        if not refs:
            errors.append(f"component-sources: missing for {item.get('component_id')}")
        for ref in refs:
            if ref not in source_map:
                errors.append(f"component-sources: unknown {ref}")

    relations = model.get("relations", [])
    relation_ids = [item.get("relation_id", "") for item in relations]
    _unique(relation_ids, "relations", errors)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for item in relations:
        relation_type = item.get("type")
        source = item.get("source")
        target = item.get("target")
        if relation_type not in ALLOWED_RELATIONS:
            errors.append(f"relation-type: unsupported {relation_type}")
        if source not in component_map:
            errors.append(f"relation-endpoint: unknown source {source}")
        if target not in component_map:
            errors.append(f"relation-endpoint: unknown target {target}")
        if source in component_map and target in component_map:
            adjacency[source].add(target)
            adjacency[target].add(source)
        refs = item.get("source_refs", [])
        if not refs:
            errors.append(f"relation-sources: missing for {item.get('relation_id')}")
        for ref in refs:
            if ref not in source_map:
                errors.append(f"relation-sources: unknown {ref}")

    if ROOT_COMPONENT in component_map:
        seen = {ROOT_COMPONENT}
        queue = deque([ROOT_COMPONENT])
        while queue:
            for neighbor in adjacency[queue.popleft()]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        missing = sorted(set(component_map) - seen)
        if missing:
            errors.append(f"graph-connectivity: disconnected {','.join(missing)}")

    cross_branch_evidence = False
    for item in relations:
        if item.get("type") != "realized_by":
            continue
        source = component_map.get(item.get("source"), {})
        target = component_map.get(item.get("target"), {})
        refs = set(item.get("source_refs", []))
        if (
            source.get("branch") == "business"
            and target.get("branch") == "system"
            and "SRC-D65-BUSINESS-ADMISSION" in refs
            and "SRC-D65-SYSTEM-ADMISSION" in refs
        ):
            cross_branch_evidence = True
    if not cross_branch_evidence:
        errors.append("bridge-evidence: evidenced business-to-system realized_by relation required")

    catalog = model.get("catalog_projection", {})
    if catalog.get("expected_package_count") != 20:
        errors.append("catalog-count: expected 20 packages")
    if catalog.get("expected_review_group_count") != 10:
        errors.append("review-count: expected 10 groups")
    collision = catalog.get("identity_collision", {})
    if collision.get("ontology_id") != "domainspec-product-ontology@1" or collision.get("profile_count") != 11:
        errors.append("identity-collision: 11 qualified DomainSpec profiles must remain explicit")
    if collision.get("admission_effect") != "none":
        errors.append("identity-collision: collision handling cannot admit a profile")
    if model.get("query_contract", {}).get("duplicate_ontology_identity_behavior") != "return-all-profile-qualified-results":
        errors.append("query-contract: duplicate identities must return all qualified results")

    if check_files and "SRC-LEGACY-ONTOLOGY-INVENTORY" in source_map:
        inventory = load_json(REPO / source_map["SRC-LEGACY-ONTOLOGY-INVENTORY"]["path"])
        packages = inventory.get("packages", [])
        if len(packages) != 20 or inventory.get("package_count") != 20:
            errors.append("catalog-currentness: inventory package count mismatch")
        profiles = [
            item.get("profile_path")
            for item in packages
            if item.get("ontology_id") == "domainspec-product-ontology@1"
        ]
        if len(profiles) != 11 or len(set(profiles)) != 11:
            errors.append("catalog-currentness: DomainSpec profile collision shape changed")
        allowed_catalog_effects = {"none", "project-local-canonical-product-read-model"}
        unexpected_effects = sorted(
            {
                item.get("authority_effect")
                for item in packages
                if item.get("authority_effect") not in allowed_catalog_effects
            }
        )
        if unexpected_effects:
            errors.append(f"catalog-authority: unexpected effects {unexpected_effects}")

    if check_files and "SRC-LEGACY-ONTOLOGY-REVIEWS" in source_map:
        reviews = load_json(REPO / source_map["SRC-LEGACY-ONTOLOGY-REVIEWS"]["path"])
        entries = reviews.get("entries", [])
        if len(entries) != 10 or reviews.get("entry_count") != 10:
            errors.append("review-currentness: review group count mismatch")
        if any(item.get("blocker_count", 0) < 1 for item in entries):
            errors.append("review-vacuity: every recorded review must preserve its blockers")

    if check_files:
        for source_id, (status, effect) in EXPECTED_DECISIONS.items():
            item = source_map.get(source_id)
            if not item:
                errors.append(f"decision-source: missing {source_id}")
                continue
            decision = load_json(REPO / item["path"])
            if decision.get("status") != status or decision.get("authority_effect") != effect:
                errors.append(f"decision-authority: mismatch {source_id}")
        approval = load_json(REPO / source_map["SRC-ONTOLOGY-PRODUCT-APPROVAL"]["path"])
        subject = approval.get("subject", {})
        if subject.get("product_candidate_sha256") != source_map["SRC-ONTOLOGY-PRODUCT-CANDIDATE"]["sha256"]:
            errors.append("product-approval: candidate digest binding mismatch")
        artifact_type = load_json(REPO / source_map["SRC-ONTOLOGY-PACKAGE-TYPE"]["path"])
        if artifact_type.get("status") != "candidate-unadmitted":
            errors.append("artifact-type-boundary: expected candidate-unadmitted")

    admission = model.get("admission_model", {})
    classified = set()
    for key in (
        "already_admitted_components",
        "approved_not_admitted_components",
        "accepted_not_admitted_components",
        "candidate_only_components",
    ):
        values = admission.get(key, [])
        overlap = classified.intersection(values)
        if overlap:
            errors.append(f"authority-classification: overlap {','.join(sorted(overlap))}")
        classified.update(values)
    if classified != set(component_map):
        errors.append("authority-classification: every component must appear exactly once")
    if "must not admit" not in admission.get("forbidden_inference", ""):
        errors.append("authority-non-collapse: forbidden inference missing")

    truth = model.get("canonical_truth_contract", {})
    runtime_truth = truth.get("runtime_truth", "").lower()
    if "canonical" not in runtime_truth or "event" not in runtime_truth or "calculate" not in runtime_truth:
        errors.append("canonical-truth: canonical events must calculate state")
    required_derived = {"snapshots", "context projections", "compiled graphs", "system ontologies", "read models"}
    if not required_derived.issubset(set(truth.get("derived_only", []))):
        errors.append("canonical-truth: all derived views must remain noncanonical")
    if "not a replay source" not in truth.get("composition_rule", ""):
        errors.append("canonical-truth: root must not become replay source")

    if candidate.get("authority_effect") != "none":
        errors.append("candidate-authority: must remain none")
    if candidate.get("status") != "ready-for-product-approval":
        errors.append("candidate-status: ready-for-product-approval required")
    product_test = candidate.get("product_test", {})
    if (
        product_test.get("result") != "PASS"
        or product_test.get("structural_validation") != "PASS"
        or product_test.get("test_cases") != 9
        or product_test.get("hostile_probes") != 8
        or product_test.get("deterministic_validation_runs") != 2
        or product_test.get("product_approval_eligible") is not True
        or product_test.get("product_approval_granted") is not False
    ):
        errors.append("candidate-product-test: frozen test posture mismatch")
    expected_model_digest = candidate.get("product_increment", {}).get("ontology_system_sha256")
    if check_files and expected_model_digest != sha256(MODEL_PATH):
        errors.append("candidate-binding: ontology-system digest mismatch")
    if candidate.get("predecessor", {}).get("sha256") != source_map.get("SRC-ONTOLOGY-PRODUCT-CANDIDATE", {}).get("sha256"):
        errors.append("candidate-lineage: predecessor digest mismatch")
    return errors


def validation_summary(model: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    errors = validate_model(model, candidate)
    return {
        "schema_version": "cyberalchemy-lab-cohesive-ontology-validation/v1",
        "candidate_id": candidate.get("candidate_id"),
        "system_id": model.get("system_id"),
        "result": "PASS" if not errors else "BLOCK",
        "authority_effect": "none",
        "checks": {
            "source_count": len(model.get("sources", [])),
            "component_count": len(model.get("components", [])),
            "relation_count": len(model.get("relations", [])),
            "residue_count": len(model.get("residue", [])),
            "catalog_package_count": model.get("catalog_projection", {}).get("expected_package_count"),
            "review_group_count": model.get("catalog_projection", {}).get("expected_review_group_count"),
        },
        "errors": errors,
        "product_approval_eligible": not errors,
        "admission_authorized": False,
        "claim_ceiling": "PASS proves only structural, source-current, status-preserving cohesion for this exact Product candidate. It does not approve the Product or admit, adopt, activate, migrate, cut over, publish, release, deploy, or transfer authority for any ontology.",
    }


def write_receipt(summary: dict[str, Any]) -> None:
    if summary["result"] != "PASS":
        raise SystemExit("refusing to write a BLOCK receipt")
    inputs = []
    for path in (CANDIDATE_PATH, MODEL_PATH, SCHEMA_PATH, HERE / "validate.py", HERE / "test_validate.py", HERE / "README.md"):
        inputs.append({"path": str(path.relative_to(REPO)), "sha256": sha256(path)})
    receipt = copy.deepcopy(summary)
    receipt["inputs"] = inputs
    receipt["hostile_probe_ids"] = [
        "source-digest-drift",
        "duplicate-component",
        "dangling-relation",
        "authority-inflation",
        "duplicate-identity-collapse",
        "bridge-evidence-removal",
        "canonical-truth-collapse",
        "disconnected-component",
    ]
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_bytes(json.dumps(receipt, indent=2, sort_keys=True).encode() + b"\n")


def inventory(model: dict[str, Any]) -> dict[str, Any]:
    source = next(item for item in model["sources"] if item["source_id"] == "SRC-LEGACY-ONTOLOGY-INVENTORY")
    return load_json(REPO / source["path"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation",
        nargs="?",
        default="check",
        choices=["check", "summary", "list-components", "get-component", "list-source-ontologies", "get-source-ontology", "admission-status"],
    )
    parser.add_argument("identity", nargs="?")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    model = load_json(MODEL_PATH)
    candidate = load_json(CANDIDATE_PATH)
    summary = validation_summary(model, candidate)
    if args.write_receipt:
        write_receipt(summary)
    if args.operation in {"check", "summary"}:
        output: Any = summary
    elif args.operation == "list-components":
        output = model["components"]
    elif args.operation == "get-component":
        matches = [item for item in model["components"] if item["component_id"] == args.identity]
        if not matches:
            print(json.dumps({"result": "BLOCK", "error": "unknown component identity"}, sort_keys=True))
            return 2
        output = matches[0]
    elif args.operation == "list-source-ontologies":
        output = inventory(model)["packages"]
    elif args.operation == "get-source-ontology":
        matches = [
            item
            for item in inventory(model)["packages"]
            if item.get("ontology_id") == args.identity or item.get("profile_path") == args.identity
        ]
        if not matches:
            print(json.dumps({"result": "BLOCK", "error": "unknown source ontology identity"}, sort_keys=True))
            return 2
        output = matches
    else:
        output = model["admission_model"] | {"residue": model["residue"]}
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
