#!/usr/bin/env python3
"""Collect-all validation for successor migration candidate 0002."""

from __future__ import annotations

import ast
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
PREDECESSOR = ROOT.parent / "0001-full-migration-architecture"
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"


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
    check("successor-candidate-no-effect", candidate["candidate_id"].endswith("0002") and candidate["status"] == "test-candidate-built" and candidate["authority_effect"] == "none", {"candidate_id": candidate["candidate_id"], "status": candidate["status"], "authority_effect": candidate["authority_effect"]})
    predecessor = candidate["predecessor"]
    predecessor_actual = {"manifest_sha256": sha(PREDECESSOR / "manifest.json"), "receipt_sha256": sha(PREDECESSOR / "receipts/validation.json")}
    check("predecessor-0001-preserved", predecessor_actual == {"manifest_sha256": predecessor["manifest_sha256"], "receipt_sha256": predecessor["receipt_sha256"]} and load(PREDECESSOR / "receipts/validation.json")["result"] == "PASS", predecessor_actual)

    foundation = load(ROOT / "admitted-foundation-bindings.json")
    registry_path = LAB / foundation["definition_registry"]["path"]
    registry = load(registry_path)
    definition_results = []
    for item in foundation["definitions"]:
        path = LAB / item["path"]
        live_ref = registry["current_lookup"].get(item["definition_ref"].split("@")[0])
        definition_results.append({"definition_ref": item["definition_ref"], "current": live_ref == item["definition_ref"], "digest_current": path.is_file() and sha(path) == item["sha256"], "admitted": item["lifecycle_state"] == "admitted"})
    check("admitted-definition-foundation-current", sha(registry_path) == foundation["definition_registry"]["sha256"] and registry["status"] == "owner-admitted" and all(item["current"] and item["digest_current"] and item["admitted"] for item in definition_results), definition_results)

    type_results = []
    for item in foundation["artifact_types"]:
        artifact = LAB / item["artifact_path"]
        schema = LAB / item["schema_path"]
        decision = LAB / item["admission_decision_path"]
        decision_text = decision.read_text(encoding="utf-8") if decision.is_file() else ""
        type_results.append({"artifact_type_ref": item["artifact_type_ref"], "artifact_current": artifact.is_file() and sha(artifact) == item["artifact_sha256"], "schema_current": schema.is_file() and sha(schema) == item["schema_sha256"], "decision_current": decision.is_file() and sha(decision) == item["admission_decision_sha256"], "decision_binds_ref": item["artifact_type_ref"] in decision_text and item["artifact_sha256"] in decision_text})
    check("admitted-artifact-type-foundation-current", all(all(value for key, value in item.items() if key != "artifact_type_ref") for item in type_results), type_results)
    check("artifact-surface-foundation-not-a-prerequisite", "artifact_surface_foundation" not in candidate and "artifact_type_request_ref" not in candidate and not (ROOT / "request.json").exists(), {"candidate_keys": sorted(candidate), "request_exists": (ROOT / "request.json").exists()})

    definition_result = run([sys.executable, str(DEFINITION_ROOT / "validate.py")])
    type_result = run([sys.executable, str(TYPE_ROOT / "validate.py")])
    check("new-definition-candidate-valid", definition_result["returncode"] == 0, definition_result)
    check("new-artifact-type-candidate-valid", type_result["returncode"] == 0, type_result)

    migration = load(ROOT / "migration.json")
    migration_errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(TYPE_ROOT / "schema.json")).iter_errors(migration))
    check("migration-instance-schema-valid", not migration_errors and migration["migration_manifest_id"].endswith("0002") and migration["execution_authority"] is False, migration_errors)
    references = [migration[key] for key in ["architecture", "mapping_rules", "exclusion_inventory", "copy_allowlist", "expected_postimage", "rollback_ref"]] + [migration["source_repository"]["inventory"], migration["target_repository"]["baseline"]]
    reference_results = [{"path": item["path"], "current": (ROOT / item["path"]).is_file() and sha(ROOT / item["path"]) == item["sha256"]} for item in references]
    check("migration-reference-digests-current", all(item["current"] for item in reference_results), reference_results)

    declared_baseline = load(ROOT / "target-baseline.json")
    inventory = load(ROOT / "source-inventory.json")
    exclusions = load(ROOT / "exclusion-inventory.json")
    selected = [item for item in inventory["entries"] if item["disposition"] == "copy-selected"]
    unmapped = [item["path"] for item in inventory["entries"] if item["disposition"] == "blocked-unmapped"]
    accounted = len(inventory["entries"]) + sum(item["entry_count"] for item in exclusions["directory_groups"])
    check("complete-source-accounting", accounted == inventory["counts"]["accounted_entries"] and len(selected) == inventory["counts"]["selected_regular_files"] and not unmapped, {"accounted": accounted, "selected": len(selected), "unmapped": unmapped})
    source_root = Path(inventory["source_root"])
    drift = [item["path"] for item in selected if not (source_root / item["path"]).is_file() or sha(source_root / item["path"]) != item["sha256"]]
    check("selected-source-digests-current", not drift, {"checked": len(selected), "drift": drift})

    allowlist = load(ROOT / "copy-allowlist.json")
    current_baseline_entries = []
    for item in allowlist["entries"]:
        path = LAB / item["target_path"]
        if path.is_file():
            info = path.stat()
            current_baseline_entries.append({"path": item["target_path"], "kind": "regular-file", "size": info.st_size, "mode": info.st_mode & 0o7777, "sha256": sha(path)})
        elif path.exists():
            current_baseline_entries.append({"path": item["target_path"], "kind": "non-regular-collision", "size": 0, "mode": 0, "sha256": ""})
    current_baseline_entries.sort(key=lambda item: item["path"])
    build_wrapper = import_path("migration_successor_build", ROOT / "build.py")
    current_baseline_root = build_wrapper.module.root_digest(current_baseline_entries)
    check("target-baseline-current", declared_baseline.get("scope") == "allowlisted-destination-preimage-only" and current_baseline_entries == declared_baseline["entries"] and current_baseline_root == declared_baseline["root_sha256"], {"scope": declared_baseline.get("scope"), "declared_entries": declared_baseline["entry_count"], "current_entries": len(current_baseline_entries), "declared_root": declared_baseline["root_sha256"], "current_root": current_baseline_root})

    destinations = [item["target_path"] for item in allowlist["entries"]]
    mapping_ok = {item["source_path"] for item in allowlist["entries"]} == {item["path"] for item in selected} and len(destinations) == len(set(destinations)) and all(not Path(path).is_absolute() and ".." not in Path(path).parts for path in destinations)
    check("mapping-total-unique-safe", mapping_ok and not allowlist["duplicate_destinations"], {"entries": len(destinations), "unique": len(set(destinations)), "duplicates": allowlist["duplicate_destinations"]})
    check("no-divergent-target-collisions", not allowlist["divergent_collisions"] and all(item["action"] in {"create", "preserve-existing"} for item in allowlist["entries"]), {"actions": dict(Counter(item["action"] for item in allowlist["entries"])), "collisions": allowlist["divergent_collisions"]})

    dry = run([sys.executable, str(ROOT / "execute.py"), "--dry-run"])
    rehearsal = run([sys.executable, str(ROOT / "execute.py"), "--rehearse-sample"])
    check("dry-run-no-effect", dry["returncode"] == 0 and json.loads(dry["stdout"])["target_mutated"] is False, dry)
    rehearsal_data = json.loads(rehearsal["stdout"]) if rehearsal["stdout"] else {}
    check("isolated-rehearsal", rehearsal["returncode"] == 0 and rehearsal_data.get("temporary_tree_removed") is True, rehearsal)

    expected = load(ROOT / "expected-postimage.json")
    post_entries = [{"path": item["target_path"], "sha256": item["source_sha256"], "size": item["size"]} for item in allowlist["entries"]]
    digest = hashlib.sha256()
    for item in sorted(post_entries, key=lambda value: value["path"]):
        digest.update(item["path"].encode()); digest.update(b"\0"); digest.update(item["sha256"].encode()); digest.update(b"\0"); digest.update(str(item["size"]).encode()); digest.update(b"\n")
    check("expected-postimage-closed", expected["imported_entry_count"] == len(post_entries) and expected["imported_root_sha256"] == digest.hexdigest() and expected["collision_count"] == 0, {"entries": len(post_entries), "digest": digest.hexdigest()})
    rollback = load(ROOT / "rollback.json")
    create_set = {item["target_path"] for item in allowlist["entries"] if item["action"] == "create"}
    check("rollback-create-set-closed", set(rollback["created_file_paths"]) == create_set and rollback["created_file_count"] == len(create_set) and not rollback["source_paths"] and not rollback["overwrite_restoration_paths"], {"create": len(create_set), "rollback": rollback["created_file_count"]})

    schema_results = []
    for name in ["decision-request-set.schema.json", "decision-record.schema.json"]:
        schema = load(ROOT / name)
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            schema_results.append({"path": name, "valid": True})
        except Exception as error:
            schema_results.append({"path": name, "valid": False, "error": str(error)})
    check("decision-envelope-schemas-valid", all(item["valid"] for item in schema_results), schema_results)
    executor_source = (ROOT / "execute.py").read_text(encoding="utf-8")
    missing_record = run([sys.executable, str(ROOT / "execute.py"), "--execute"])
    check("separate-decision-record-required", missing_record["returncode"] != 0 and "missing-separate-decision-record" in missing_record["stdout"] and "product_approval" not in executor_source and "decision-record.schema.json" in executor_source, missing_record)
    syntax_results = []
    for path in sorted(ROOT.glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8")); syntax_results.append({"path": path.name, "valid": True})
        except SyntaxError as error:
            syntax_results.append({"path": path.name, "valid": False, "error": str(error)})
    check("python-surfaces-parse", all(item["valid"] for item in syntax_results), syntax_results)

    manifest = load(ROOT / "manifest.json")
    stale = [item["path"] for item in manifest["materials"] if not (LAB / item["path"]).is_file() or sha(LAB / item["path"]) != item["sha256"]]
    check("successor-byte-manifest-closed", not stale and manifest["manifest_id"].endswith("0002") and manifest["predecessor_manifest_sha256"] == predecessor["manifest_sha256"], {"materials": len(manifest["materials"]), "stale": stale})

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-repository-migration-product-validation/v2", "subject": candidate["candidate_id"], "result": "PASS" if not blocked else "BLOCK", "authority_effect": "none",
        "assessment": {"product_candidate": "TESTED" if not blocked else "NOT_ESTABLISHED", "product_approval": "not_granted", "definition_admission": "not_granted-for-new-definition", "artifact_type_admission": "not_granted-for-new-type", "admitted_foundation": "CURRENT" if checks[2]["result"] == "PASS" and checks[3]["result"] == "PASS" else "NOT_ESTABLISHED", "migration_execution": "not_authorized", "source_deletion": "not_authorized", "overwrite": "forbidden", "commit": "not_authorized", "push": "not_authorized", "publication": "not_authorized"},
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)}, "checks": checks,
        "materials": {"candidate_sha256": sha(ROOT / "candidate.json"), "migration_sha256": sha(ROOT / "migration.json"), "manifest_sha256": sha(ROOT / "manifest.json"), "foundation_bindings_sha256": sha(ROOT / "admitted-foundation-bindings.json"), "definition_receipt_sha256": sha(DEFINITION_ROOT / "receipts/validation.json"), "artifact_type_receipt_sha256": sha(TYPE_ROOT / "receipts/validation.json"), "source_inventory_sha256": sha(ROOT / "source-inventory.json"), "copy_allowlist_sha256": sha(ROOT / "copy-allowlist.json"), "expected_postimage_sha256": sha(ROOT / "expected-postimage.json"), "rollback_sha256": sha(ROOT / "rollback.json")},
        "decision_boundary": {"next_command": "run prepare_decision_request.py to generate one exact four-decision request set", "interaction_count": 1, "outcomes_remain_independent": True},
        "claim_ceiling": "PASS proves successor candidate 0002 uses current admitted foundations, preserves predecessor 0001, has a current collision-free additive plan, and requires a separate decision record. It does not approve, admit, execute, delete, overwrite, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"REPOSITORY_MIGRATION_SUCCESSOR={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    if blocked:
        print("BLOCKED=" + ",".join(item["check_id"] for item in blocked))
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
