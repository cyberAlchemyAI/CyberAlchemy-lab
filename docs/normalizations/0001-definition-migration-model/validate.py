#!/usr/bin/env python3
"""Fail-closed validator for the NORMALIZE-01 draft and projection."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "receipts" / "validation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check("draft-has-no-authority-effect", data.get("authority_effect") == "none",
          f"authority_effect={data.get('authority_effect')!r}")
    check("candidate-artifact-type-unadmitted",
          data.get("artifact_type", {}).get("artifact_type_status") == "candidate-unadmitted",
          f"artifact_type_status={data.get('artifact_type', {}).get('artifact_type_status')!r}")
    direction = data.get("source_direction", {})
    check("machine-canonical-human-generated",
          direction.get("canonical") == SOURCE.name
          and direction.get("human_projection") == OUTPUT.name
          and direction.get("projection_policy") == "generated-only",
          json.dumps(direction, sort_keys=True))

    decisions = data.get("migration_decisions", [])
    expected_active = [f"CAV2-D{i}" for i in range(1, 70)]
    actual_active = [x.get("legacy_id") for x in decisions]
    check("active-decision-coverage", actual_active == expected_active,
          f"expected ordered CAV2-D1..CAV2-D69; found {len(actual_active)} records")
    expected_counts = {"revise": 17, "reclassify": 19, "split": 23, "collapse": 6, "drop": 4}
    actual_counts = Counter(str(x.get("decision", "")).lower() for x in decisions)
    declared_counts = data.get("accepted_outcome_counts", {})
    check("decision-counts",
          all(actual_counts[k] == v and declared_counts.get(k) == v for k, v in expected_counts.items())
          and declared_counts.get("active_total") == 69,
          f"actual={dict(actual_counts)} declared={declared_counts}")

    withdrawn = data.get("withdrawn_ids", [])
    expected_withdrawn = [(f"CAV2-D{i}", f"KEP-D{i - 69}") for i in range(70, 82)]
    actual_withdrawn = [(x.get("legacy_id"), x.get("successor_id")) for x in withdrawn]
    check("withdrawn-identity-preservation", actual_withdrawn == expected_withdrawn,
          f"expected CAV2-D70..D81 -> KEP-D1..D12; found {actual_withdrawn}")

    registries = {
        "artifact_types": ("artifact_type_id", data.get("artifact_types", [])),
        "profiles": ("profile_id", data.get("profiles", [])),
        "relation_kinds": ("relation_kind_id", data.get("relation_kinds", [])),
        "semantic_concepts": ("concept_id", data.get("semantic_concepts", [])),
        "derived_surfaces": ("derived_surface_id", data.get("derived_surfaces", [])),
    }
    all_ids: list[str] = []
    for key, (id_key, records) in registries.items():
        ids = [x.get(id_key) for x in records]
        check(f"unique-{key}", len(ids) == len(set(ids)) and all(isinstance(x, str) and x for x in ids),
              f"records={len(ids)} unique={len(set(ids))}")
        all_ids.extend(ids)
    check("global-registry-id-uniqueness", len(all_ids) == len(set(all_ids)),
          f"ids={len(all_ids)} unique={len(set(all_ids))}")
    known = set(all_ids)

    target_refs = [target for item in decisions for target in item.get("targets", [])]
    missing_targets = sorted(set(target_refs) - known)
    check("migration-target-closure", not missing_targets, f"missing={missing_targets}")

    type_ids = {x["artifact_type_id"] for x in data.get("artifact_types", [])}
    missing_profile_types = sorted({x.get("artifact_type_ref") for x in data.get("profiles", [])} - type_ids)
    check("profile-artifact-type-closure", not missing_profile_types, f"missing={missing_profile_types}")

    owner_ids = {x["owner_scope_id"] for x in data.get("owner_scopes", [])}
    concept_carriers = {x.get("carrier_ref") for x in data.get("semantic_concepts", [])}
    concept_owners = {x.get("owner_scope") for x in data.get("semantic_concepts", [])}
    check("semantic-carrier-closure", not (concept_carriers - known),
          f"missing={sorted(concept_carriers - known)}")
    check("semantic-owner-scope-closure", not (concept_owners - owner_ids),
          f"missing={sorted(concept_owners - owner_ids)}")

    admitted_context_statuses = {"admitted", "selected", "canonical", "bounded-context"}
    scope_statuses = {x.get("ddd_bounded_context_status") for x in data.get("owner_scopes", [])}
    check("no-inferred-bounded-contexts", not (scope_statuses & admitted_context_statuses),
          f"statuses={sorted(scope_statuses)}")
    check("product-and-governance-not-auto-contexts",
          all(x.get("ddd_bounded_context_status") != "admitted"
              for x in data.get("owner_scopes", [])
              if x.get("name") in {"Product", "Governance"}),
          "Product and Governance remain owner scopes pending explicit context selection")

    purposes = [x.get("distinct_validation_purpose", "").strip() for x in data.get("artifact_types", [])]
    check("artifact-types-have-validation-purpose", all(purposes),
          f"empty={sum(not x for x in purposes)}")
    required_bindings = {
        "type.construction-binding", "type.implementation-binding",
        "type.model-instance-binding", "type.capability-realization-binding",
    }
    check("specialized-bindings-preserved", required_bindings <= type_ids,
          f"missing={sorted(required_bindings - type_ids)}")

    stale_sources = []
    for source in data.get("source_refs", []):
        path = Path(source["path"])
        if not path.is_file() or digest(path) != source.get("sha256"):
            stale_sources.append(source.get("source_id"))
    check("selected-source-currentness", not stale_sources, f"stale_or_missing={stale_sources}")

    rendered_a = render(data)
    rendered_b = render(data)
    check("two-run-render-determinism", rendered_a == rendered_b,
          f"sha256={hashlib.sha256(rendered_a.encode()).hexdigest()}")
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a,
          "NORMALIZATION.md must exactly equal render(normalization.json)")

    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-normalization-validation/v0",
        "normalization_id": data.get("normalization_id"),
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "normalization_json_sha256": digest(SOURCE),
            "normalization_md_sha256": digest(OUTPUT) if OUTPUT.is_file() else None,
            "renderer_sha256": digest(ROOT / "render.py"),
            "validator_sha256": digest(ROOT / "validate.py"),
        },
        "claim_ceiling": data.get("claim_ceiling"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(x['result'] == 'PASS' for x in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
