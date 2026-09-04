#!/usr/bin/env python3
"""Validate exact CTX01 candidate closure and cross-type orthogonality."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT / "artifact-type-pack.json"
OUTPUT = ROOT / "ARTIFACT-TYPE-PACK.md"
RECEIPT = ROOT / "receipts/validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main() -> int:
    pack = load(SOURCE)
    checks = []
    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("pack-identity", pack.get("pack_id") == "CAL-ARTIFACT-TYPE-PACK-CTX01-0001", pack.get("pack_id"))
    check("candidate-no-authority", pack.get("authority_effect") == "none" and pack.get("status", "").startswith("candidate-"), {"status": pack.get("status"), "authority_effect": pack.get("authority_effect")})
    items = pack["artifact_types"]
    check("seven-type-closure", len(items) == 7, [item["artifact_type_ref"] for item in items])
    for field in ("slug", "artifact_type_ref", "definition_id", "identity_field", "artifact_path", "schema_path", "receipt_path"):
        values = [item[field] for item in items]
        check(f"unique-{field.replace('_', '-')}", len(values) == len(set(values)), values)
    check("wave-cardinality", {wave: sum(item["wave"] == wave for item in items) for wave in {item["wave"] for item in items}} == {"identity": 3, "relationships": 2, "migration-evidence": 2}, [item["wave"] for item in items])

    material_results = []
    artifacts = {}
    receipts = {}
    for item in items:
        expected_path = f"authority/artifact-types/{item['slug']}/v1/artifact.json"
        artifact_path = LAB / item["artifact_path"]
        schema_path = LAB / item["schema_path"]
        human_path = LAB / item["human_path"]
        receipt_path = LAB / item["receipt_path"]
        artifacts[item["slug"]] = load(artifact_path)
        receipts[item["slug"]] = load(receipt_path)
        material_results.append({
            "slug": item["slug"],
            "direct_path": item["artifact_path"] == expected_path,
            "artifact_current": sha256(artifact_path) == item["artifact_sha256"],
            "schema_current": sha256(schema_path) == item["schema_sha256"],
            "human_current": sha256(human_path) == item["human_sha256"],
            "receipt_current": sha256(receipt_path) == item["receipt_sha256"],
            "receipt_pass": receipts[item["slug"]].get("result") == "PASS" and receipts[item["slug"]].get("summary", {}).get("failed") == 0,
        })
    check("all-materials-current", all(all(value for key, value in item.items() if key != "slug") for item in material_results), material_results)
    check("all-candidates-no-authority", all(value.get("status") == "candidate-unadmitted" and value.get("authority_effect") == "none" for value in artifacts.values()), {slug: {"status": value.get("status"), "authority_effect": value.get("authority_effect")} for slug, value in artifacts.items()})

    shared_results = []
    for field in ("schema", "generator", "validator"):
        path = LAB / pack["shared_mechanics"][f"{field}_path"]
        shared_results.append({"field": field, "expected": pack["shared_mechanics"][f"{field}_sha256"], "actual": sha256(path), "current": sha256(path) == pack["shared_mechanics"][f"{field}_sha256"]})
    check("shared-mechanics-current", all(item["current"] for item in shared_results), shared_results)
    prerequisite_results = []
    for name, item in pack["admitted_prerequisites"].items():
        actual = sha256(LAB / item["path"])
        prerequisite_results.append({"name": name, "expected": item["sha256"], "actual": actual, "current": actual == item["sha256"]})
    check("admitted-prerequisites-current", all(item["current"] for item in prerequisite_results), prerequisite_results)

    bounded_fields = set(artifacts["bounded-context"]["instance_contract"]["required_semantic_fields"])
    coordination_fields = set(artifacts["coordination-context"]["instance_contract"]["required_semantic_fields"])
    check("bounded-coordination-non-collapse", {"domain_model_ref", "ubiquitous_language_ref"}.issubset(bounded_fields) and not {"domain_model_ref", "ubiquitous_language_ref"}.intersection(coordination_fields) and "product_ref" in coordination_fields and "product_ref" not in bounded_fields, {"bounded": sorted(bounded_fields), "coordination": sorted(coordination_fields)})
    check("context-map-owns-relations", "relationships" in artifacts["context-map"]["instance_contract"]["required_semantic_fields"] and "relationships" not in bounded_fields, artifacts["context-map"]["instance_contract"]["required_semantic_fields"])
    check("capability-instance-separate-authority", {"parent_authority_claim_ref", "instance_authority_claim_ref"}.issubset(set(artifacts["capability-instance"]["instance_contract"]["required_semantic_fields"])), artifacts["capability-instance"]["instance_contract"]["required_semantic_fields"])
    manifest_fields = set(artifacts["context-migration-manifest"]["instance_contract"]["required_semantic_fields"])
    lineage_fields = set(artifacts["context-lineage-record"]["instance_contract"]["required_semantic_fields"])
    check("manifest-lineage-non-collapse", "execution_authority" in manifest_fields and "lineage_kind" not in manifest_fields and "lineage_kind" in lineage_fields and "execution_authority" not in lineage_fields and {"equivalence_inferred", "admission_inferred"}.issubset(lineage_fields), {"manifest": sorted(manifest_fields), "lineage": sorted(lineage_fields)})
    check("cross-type-invariants-complete", [item["invariant_id"] for item in pack["cross_type_invariants"]] == ["CTX01-X01", "CTX01-X02", "CTX01-X03", "CTX01-X04", "CTX01-X05"], pack["cross_type_invariants"])
    check("promotion-remains-gated", pack["promotion_gate"]["required_role"] == "artifact-type-owner" and pack["promotion_gate"]["current_state"].startswith("not_evaluable"), pack["promotion_gate"])
    check("no-context-instance-materials", all(not item["artifact_path"].startswith("contexts/") for item in items), [item["artifact_path"] for item in items])
    renderer = module("ctx01_pack_renderer", ROOT / "render.py")
    check("pack-projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == renderer.render(pack), str(OUTPUT.relative_to(LAB)))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-pack-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "evidence-only-does-not-admit-artifact-types",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "promotion_eligibility": "eligible-for-exact-artifact-type-owner-review" if result == "PASS" else "blocked",
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_ARTIFACT_TYPE_PACK_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
