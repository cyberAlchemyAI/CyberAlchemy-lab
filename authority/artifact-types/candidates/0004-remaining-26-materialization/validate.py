#!/usr/bin/env python3
"""Validate the 26-package Artifact Type materialization batch."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
MIGRATION_REGISTRY = LAB / "authority/decisions/migration-contracts/v1/registry.json"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
SHARED_VALIDATOR = LAB / "tooling/validators/artifact_surface.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(LAB))


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, result: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if result else "BLOCK", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    migration_entries = {
        entry["target_id"]: entry
        for entry in load(MIGRATION_REGISTRY)["entries"]
        if entry["family"] == "artifact-type"
    }
    candidate_entries = {entry["target_id"]: entry for entry in candidate["entries"]}
    expected_ids = set(migration_entries)
    actual_ids = set(candidate_entries)
    check("exact-26-target-closure", len(expected_ids) == 26 and actual_ids == expected_ids and len(candidate["entries"]) == 26, {
        "expected": sorted(expected_ids), "actual": sorted(actual_ids), "entry_count": len(candidate["entries"])
    })
    check("batch-has-no-authority-effect", candidate["authority_effect"] == "none" and candidate["status"] == "candidate-materialized-awaiting-artifact-type-owner-admission", {
        "status": candidate["status"], "authority_effect": candidate["authority_effect"]
    })

    live_definitions = {
        f"{entry['definition_id']}@{entry['version']}": entry
        for entry in load(DEFINITION_REGISTRY)["entries"]
        if entry["lifecycle_state"] == "admitted"
    }
    spec = importlib.util.spec_from_file_location("materialized_artifact_validator", SHARED_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)

    package_results = []
    for target_id in sorted(expected_ids):
        selected = migration_entries[target_id]
        entry = candidate_entries.get(target_id)
        if entry is None:
            package_results.append({"target_id": target_id, "ok": False, "reason": "missing candidate entry"})
            continue
        package = LAB / entry["package_path"]
        artifact_path = package / "artifact.json"
        materialization_path = package / "materialization.json"
        required = [
            artifact_path, package / "schema.json", package / "ARTIFACT.md", package / "generator.py", package / "validate.py",
            materialization_path, package / "MATERIALIZATION.md", package / "migration-contract.json",
            package / "fixtures/valid/record.json", package / "fixtures/valid/RECORD.md",
            package / "fixtures/invalid/authority.json", package / "fixtures/invalid/missing-field.json",
            package / "fixtures/invalid/extra-field.json", package / "receipts/validation.json",
        ]
        if target_id == "type.intent":
            required.append(package / "fixtures/invalid/missing-traceability.json")
        if target_id == "type.product-thesis":
            required.append(package / "fixtures/invalid/missing-thesis-structure.json")
        if target_id == "type.product-capability":
            required.append(package / "fixtures/invalid/missing-capability-contract.json")
        if target_id == "type.capability-realization-binding":
            required.append(package / "fixtures/invalid/missing-capability-version.json")
        files_present = all(path.is_file() for path in required)
        artifact = load(artifact_path) if artifact_path.is_file() else {}
        materialization = load(materialization_path) if materialization_path.is_file() else {}
        definitions_ok = True
        for binding in artifact.get("semantic_definition_bindings", []):
            live = live_definitions.get(binding["definition_ref"])
            definitions_ok = definitions_ok and live is not None and binding == {
                "admission_decision_ref": live["admission_decision_ref"],
                "admission_posture": "admitted",
                "definition_ref": binding["definition_ref"],
                "path": live["path"],
                "sha256": live["sha256"],
            }
        source_ok = (
            sha(LAB / selected["binding"]["path"]) == selected["binding"]["sha256"]
            and sha(LAB / selected["contract"]["path"]) == selected["contract"]["sha256"]
            and sha(package / "migration-contract.json") == selected["contract"]["sha256"]
        )
        metadata_ok = (
            artifact.get("artifact_type_ref") == entry["artifact_type_ref"]
            and artifact.get("status") == "candidate-unadmitted"
            and artifact.get("authority_effect") == "none"
            and materialization.get("target_id") == target_id
            and materialization.get("status") in {"candidate-materialized", "candidate-refined"}
            and materialization.get("authority_effect") == "none"
            and materialization.get("source_artifact") == selected["binding"]
            and materialization.get("source_contract") == selected["contract"]
        )
        refinement_path = ROOT / "refinements" / f"{target_id}.json"
        if refinement_path.is_file():
            metadata_ok = metadata_ok and materialization.get("status") == "candidate-refined" and materialization.get("review_refinement") == {
                "path": relative(refinement_path),
                "sha256": sha(refinement_path),
                "review_state": "revision-authorized-before-admission",
            }
        digest_ok = (
            sha(artifact_path) == entry["artifact_sha256"]
            and sha(package / "schema.json") == entry["schema_sha256"]
            and sha(materialization_path) == entry["materialization_sha256"]
        )
        validator_ok = files_present and validator.validate_package(package) == 0
        receipt_path = package / "receipts/validation.json"
        receipt_ok = (
            receipt_path.is_file()
            and load(receipt_path)["result"] == "PASS"
            and sha(receipt_path) == entry["validation_receipt"]["sha256"]
        )
        package_results.append({
            "target_id": target_id,
            "ok": files_present and definitions_ok and source_ok and metadata_ok and digest_ok and validator_ok and receipt_ok,
            "files_present": files_present,
            "admitted_definition_bindings": definitions_ok,
            "source_contract_exact": source_ok,
            "candidate_boundary": metadata_ok,
            "declared_digests_current": digest_ok,
            "package_validation": "PASS" if validator_ok else "BLOCK",
            "receipt_current": receipt_ok,
        })
    check("all-packages-complete-and-valid", len(package_results) == 26 and all(item["ok"] for item in package_results), package_results)

    catalog = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
    catalog_ok = all(f"`{target_id}`" in catalog and f"`{candidate_entries[target_id]['package_path']}`" in catalog for target_id in actual_ids)
    check("catalog-covers-all-packages", catalog_ok, {"target_count": len(actual_ids)})

    manifest = load(ROOT / "manifest.json")
    manifest_results = []
    for item in manifest["files"]:
        path = LAB / item["path"]
        actual = sha(path) if path.is_file() else "missing"
        manifest_results.append({"path": item["path"], "ok": actual == item["sha256"], "actual": actual})
    check("exact-file-manifest-current", bool(manifest_results) and all(item["ok"] for item in manifest_results), manifest_results)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-materialization-validation/v1",
        "subject": candidate["batch_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {
            "candidate_sha256": sha(ROOT / "candidate.json"),
            "catalog_sha256": sha(ROOT / "CATALOG.md"),
            "manifest_sha256": sha(ROOT / "manifest.json"),
            "package_count": len(candidate["entries"]),
        },
        "claim_ceiling": "PASS proves exact materialization, admitted Definition binding, fixture behavior, projections, and file integrity for the 26 candidate packages. It does not admit an Artifact Type or instance and does not activate a consumer.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"ARTIFACT_TYPE_MATERIALIZATION_BATCH={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
