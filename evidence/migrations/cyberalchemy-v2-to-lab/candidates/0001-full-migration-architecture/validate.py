#!/usr/bin/env python3
"""Collect-all validation for the repository migration product candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"
SURFACE_VALIDATOR = LAB / "tooling/validators/artifact_surface_candidate_2.py"
REQUEST_SCHEMA = LAB / "authority/artifact-types/artifact-type-request/v1/candidates/0002-executable-surface/schema.json"
SURFACE_REGISTRY = LAB / "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=LAB, text=True, capture_output=True)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checks: list[dict[str, Any]] = []
    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    check("candidate-no-authority-effect", candidate["authority_effect"] == "none" and candidate["status"] == "test-candidate-built", {"status": candidate["status"], "authority_effect": candidate["authority_effect"]})
    foundation = candidate["artifact_surface_foundation"]
    foundation_root = LAB / "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision"
    foundation_actual = {"manifest_sha256": sha(foundation_root / "manifest.json"), "receipt_sha256": sha(foundation_root / "receipts/validation.json")}
    check("artifact-surface-dependency-current", foundation_actual == {"manifest_sha256": foundation["manifest_sha256"], "receipt_sha256": foundation["receipt_sha256"]} and load(foundation_root / "receipts/validation.json")["result"] == "PASS", foundation_actual)

    definition_result = run([sys.executable, str(DEFINITION_ROOT / "validate.py")])
    check("repository-migration-definition-valid", definition_result["returncode"] == 0, definition_result)
    type_result = run([sys.executable, str(TYPE_ROOT / "validate.py")])
    check("repository-migration-artifact-type-valid", type_result["returncode"] == 0, type_result)

    request = load(ROOT / "request.json")
    request_errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(REQUEST_SCHEMA)).iter_errors(request))
    resolver = import_path("artifact_surface_candidate_2", SURFACE_VALIDATOR)
    request_semantics = resolver.request_semantic_failures(request, load(SURFACE_REGISTRY))
    check("artifact-type-request-zero-match-valid", not request_errors and not request_semantics and request["consumed_as_subject"] is False, {"schema": request_errors, "semantic": request_semantics})

    migration = load(ROOT / "migration.json")
    migration_errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(TYPE_ROOT / "schema.json")).iter_errors(migration))
    check("migration-instance-schema-valid", not migration_errors, migration_errors)
    referenced = [migration[key] for key in ["architecture", "mapping_rules", "exclusion_inventory", "copy_allowlist", "expected_postimage", "rollback_ref"]]
    referenced += [migration["source_repository"]["inventory"], migration["target_repository"]["baseline"]]
    reference_results = [{"path": item["path"], "current": (ROOT / item["path"]).is_file() and sha(ROOT / item["path"]) == item["sha256"]} for item in referenced]
    check("migration-reference-digests-current", all(item["current"] for item in reference_results), reference_results)

    build_module = import_path("migration_candidate_build", ROOT / "build.py")
    declared_baseline = load(ROOT / "target-baseline.json")
    current_baseline = build_module.target_baseline()
    check("target-baseline-current", current_baseline["entry_count"] == declared_baseline["entry_count"] and current_baseline["root_sha256"] == declared_baseline["root_sha256"] and current_baseline["entries"] == declared_baseline["entries"], {"declared_entries": declared_baseline["entry_count"], "current_entries": current_baseline["entry_count"], "declared_root_sha256": declared_baseline["root_sha256"], "current_root_sha256": current_baseline["root_sha256"]})

    inventory = load(ROOT / "source-inventory.json")
    exclusions = load(ROOT / "exclusion-inventory.json")
    entries = inventory["entries"]
    counts = inventory["counts"]
    computed_accounted = len(entries) + sum(group["entry_count"] for group in exclusions["directory_groups"])
    selected = [item for item in entries if item["disposition"] == "copy-selected"]
    unmapped = [item["path"] for item in entries if item["disposition"] == "blocked-unmapped"]
    check("complete-source-accounting", computed_accounted == counts["accounted_entries"] and len(selected) == counts["selected_regular_files"] and not unmapped, {"computed": computed_accounted, "declared": counts["accounted_entries"], "selected": len(selected), "unmapped": unmapped})

    current_results = []
    source_root = Path(inventory["source_root"])
    for item in selected:
        path = source_root / item["path"]
        current_results.append({"path": item["path"], "current": path.is_file() and sha(path) == item["sha256"]})
    check("selected-source-digests-current", all(item["current"] for item in current_results), {"checked": len(current_results), "drift": [item["path"] for item in current_results if not item["current"]]})

    allowlist = load(ROOT / "copy-allowlist.json")
    allow = allowlist["entries"]
    destinations = [item["target_path"] for item in allow]
    relative_safe = all(not Path(path).is_absolute() and ".." not in Path(path).parts for path in destinations)
    source_match = {item["source_path"] for item in allow} == {item["path"] for item in selected}
    check("mapping-total-unique-safe", source_match and len(destinations) == len(set(destinations)) and relative_safe and not allowlist["duplicate_destinations"], {"source_set_match": source_match, "destinations": len(destinations), "unique": len(set(destinations)), "relative_safe": relative_safe, "duplicates": allowlist["duplicate_destinations"]})
    check("no-divergent-target-collisions", not allowlist["divergent_collisions"] and all(item["action"] in {"create", "preserve-existing"} for item in allow), {"collisions": allowlist["divergent_collisions"], "actions": dict(Counter(item["action"] for item in allow))})

    dry = run([sys.executable, str(ROOT / "execute.py"), "--dry-run"])
    rehearsal = run([sys.executable, str(ROOT / "execute.py"), "--rehearse-sample"])
    check("dry-run-no-effect", dry["returncode"] == 0 and json.loads(dry["stdout"])["target_mutated"] is False, dry)
    rehearsal_data = json.loads(rehearsal["stdout"]) if rehearsal["stdout"] else {}
    expected_rules = {item["mapping_rule_id"] for item in allow}
    check("isolated-rehearsal", rehearsal["returncode"] == 0 and rehearsal_data.get("temporary_tree_removed") is True and rehearsal_data.get("sample_count") == len(expected_rules), rehearsal)

    expected = load(ROOT / "expected-postimage.json")
    post_entries = [{"path": item["target_path"], "sha256": item["source_sha256"], "size": item["size"]} for item in allow]
    digest = hashlib.sha256()
    for item in sorted(post_entries, key=lambda value: value["path"]):
        digest.update(item["path"].encode()); digest.update(b"\0"); digest.update(item["sha256"].encode()); digest.update(b"\0"); digest.update(str(item["size"]).encode()); digest.update(b"\n")
    check("expected-postimage-closed", expected["imported_entry_count"] == len(allow) and expected["imported_root_sha256"] == digest.hexdigest() and expected["collision_count"] == 0, {"entries": len(allow), "digest": digest.hexdigest(), "declared": expected["imported_root_sha256"]})
    rollback = load(ROOT / "rollback.json")
    create_set = {item["target_path"] for item in allow if item["action"] == "create"}
    check("rollback-create-set-closed", set(rollback["created_file_paths"]) == create_set and rollback["created_file_count"] == len(create_set) and not rollback["source_paths"] and not rollback["overwrite_restoration_paths"], {"create": len(create_set), "rollback": rollback["created_file_count"], "source_paths": rollback["source_paths"]})

    architecture_files = ["architecture/architecture.json", "architecture/concepts.json", "architecture/relations.json", "architecture/ARCHITECTURE.md", "architecture/ARCHITECTURE-PATTERN-LIBRARY.md", "architecture/pattern-library/README.md", "ARCHITECTURE-FOUNDATIONS.md", "DEPENDENCY-RULES.md", "TESTING-ALIGNMENT.md", "OBSERVABILITY-ALIGNMENT.md"]
    check("architecture-package-complete", all((ROOT / path).is_file() for path in architecture_files), {"files": architecture_files, "missing": [path for path in architecture_files if not (ROOT / path).is_file()]})

    manifest = load(ROOT / "manifest.json")
    stale = [item["path"] for item in manifest["materials"] if not (LAB / item["path"]).is_file() or sha(LAB / item["path"]) != item["sha256"]]
    check("candidate-byte-manifest-closed", not stale and len(manifest["materials"]) >= 35, {"materials": len(manifest["materials"]), "stale": stale})

    effect_guards = migration["execution_authority"] is False and migration["copy_semantics"] == {"additive_only": True, "overwrite": False, "source_mutation": False, "import_grants_authority": False}
    check("authority-and-effect-separation", effect_guards, {"execution_authority": migration["execution_authority"], "copy_semantics": migration["copy_semantics"]})

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-repository-migration-product-validation/v1", "subject": candidate["candidate_id"], "result": "PASS" if not blocked else "BLOCK", "authority_effect": "none",
        "assessment": {"product_candidate": "TESTED" if not blocked else "NOT_ESTABLISHED", "product_approval": "not_granted", "definition_admission": "not_granted", "artifact_type_admission": "not_granted", "migration_execution": "not_authorized", "source_deletion": "not_authorized", "overwrite": "forbidden", "commit": "not_authorized", "push": "not_authorized", "publication": "not_authorized", "release": "not_authorized", "deployment": "not_authorized"},
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)}, "checks": checks,
        "materials": {"candidate_sha256": sha(ROOT / "candidate.json"), "migration_sha256": sha(ROOT / "migration.json"), "manifest_sha256": sha(ROOT / "manifest.json"), "definition_receipt_sha256": sha(DEFINITION_ROOT / "receipts/validation.json"), "artifact_type_receipt_sha256": sha(TYPE_ROOT / "receipts/validation.json"), "source_inventory_sha256": sha(ROOT / "source-inventory.json"), "target_baseline_sha256": sha(ROOT / "target-baseline.json"), "copy_allowlist_sha256": sha(ROOT / "copy-allowlist.json"), "expected_postimage_sha256": sha(ROOT / "expected-postimage.json"), "rollback_sha256": sha(ROOT / "rollback.json")},
        "approval_boundary": {"required_command_shape": "APPROVE-CYBERALCHEMY-V2-TO-LAB-MIGRATION-V1 candidate=<manifest_sha256> receipt=<this-receipt-sha256>", "single_interaction": True, "note": "A later approval must bind this exact immutable manifest and receipt. Any acceptance-bound byte change requires a new test epoch."},
        "claim_ceiling": "PASS proves the exact unapproved migration product candidate, current source accounting, collision-free additive plan, isolated rehearsal, and rollback closure only. It does not approve or execute migration, admit or activate artifacts, delete sources, overwrite Lab bytes, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"REPOSITORY_MIGRATION_PRODUCT={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    if blocked:
        print("BLOCKED=" + ",".join(item["check_id"] for item in blocked))
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
