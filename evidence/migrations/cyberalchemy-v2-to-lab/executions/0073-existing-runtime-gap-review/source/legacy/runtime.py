#!/usr/bin/env python3
"""Read-only, registry-bound ontology management runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PACKAGE_ROOT / "registry.json"
SYSTEM_ONTOLOGY_REF = "cyberAlchemy-v2/implementation/ontology-runtime/domainspec/generated/system-ontology.json"
SYSTEM_ONTOLOGY_DIGEST = "57ea1f2977efa8be92a611d46dbadc697d165578e1accd500ed171a787f5b541"
SNAPSHOT_CLAIM = (
    "Deterministic read model of one exact local registration only; not native "
    "ontology acceptance, meaning authority, promotion, publication, release, or deployment."
)
VALIDATION_CLAIM = (
    "Faithful wrapper of one registered native validator result only; runtime execution "
    "success does not upgrade the native verdict or grant authority."
)
PREFLIGHT_INTENTS = {"inspect", "query", "validate", "mutate", "publish"}


class RuntimeContractError(ValueError):
    """A declared registry or path contract is not safe or evaluable."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeContractError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def _relative_parts(relative: str) -> tuple[str, ...]:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise RuntimeContractError(f"UNSAFE_RELATIVE_PATH:{relative!r}")
    path = Path(relative)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise RuntimeContractError(f"UNSAFE_RELATIVE_PATH:{relative!r}")
    return path.parts


def resolve_bounded(root: Path, relative: str, *, kind: str) -> Path:
    parts = _relative_parts(relative)
    root_resolved = root.resolve(strict=True)
    cursor = root_resolved
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise RuntimeContractError(f"SYMLINK_FORBIDDEN:{relative}")
    try:
        resolved = cursor.resolve(strict=True)
    except OSError as exc:
        raise RuntimeContractError(f"PATH_UNAVAILABLE:{relative}:{exc.__class__.__name__}") from exc
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise RuntimeContractError(f"PATH_ESCAPE:{relative}") from exc
    if kind == "file" and not resolved.is_file():
        raise RuntimeContractError(f"FILE_REQUIRED:{relative}")
    if kind == "directory" and not resolved.is_dir():
        raise RuntimeContractError(f"DIRECTORY_REQUIRED:{relative}")
    return resolved


def heading_section_bytes(path: Path, selector: str) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    target = selector.encode()
    start = next(
        (index for index, line in enumerate(lines) if line.rstrip(b"\r\n") == target),
        None,
    )
    if start is None:
        raise RuntimeContractError(f"SELECTOR_NOT_FOUND:{selector}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith(b"## "):
            end = index
            break
    return b"".join(lines[start:end])


def json_record_bytes(path: Path, selector: str) -> bytes:
    try:
        collection, expression = selector.split(":", 1)
        field, expected = expression.split("=", 1)
    except ValueError as exc:
        raise RuntimeContractError(f"JSON_SELECTOR_INVALID:{selector}") from exc
    document = load_json(path)
    records = document.get(collection)
    if not isinstance(records, list):
        raise RuntimeContractError(f"JSON_COLLECTION_MISSING:{collection}")
    matches = [item for item in records if isinstance(item, dict) and str(item.get(field)) == expected]
    if len(matches) != 1:
        raise RuntimeContractError(f"JSON_SELECTOR_CARDINALITY:{selector}:{len(matches)}")
    return canonical_json_bytes(matches[0])


def selected_bytes(repository_root: Path, selection: dict[str, Any]) -> bytes:
    path = resolve_bounded(repository_root, str(selection.get("path", "")), kind="file")
    scope = selection.get("scope_kind")
    selector = selection.get("selector")
    if scope == "whole-file" and selector is None:
        return path.read_bytes()
    if scope == "heading-section" and isinstance(selector, str):
        return heading_section_bytes(path, selector)
    if scope == "json-record" and isinstance(selector, str):
        return json_record_bytes(path, selector)
    raise RuntimeContractError(f"SELECTION_SHAPE_INVALID:{selection.get('selection_id')}")


def material_digest(package_root: Path, material_files: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(material_files):
        path = resolve_bounded(package_root, relative, kind="file")
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_registry(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return load_json(registry_path)


def find_registration(registry: dict[str, Any], ontology_id: str) -> dict[str, Any]:
    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise RuntimeContractError("REGISTRY_ENTRIES_REQUIRED")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("ontology_id") == ontology_id]
    if len(matches) != 1:
        raise RuntimeContractError(f"REGISTRATION_CARDINALITY:{ontology_id}:{len(matches)}")
    return matches[0]


def _registry_errors(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != "cav2-ontology-runtime-registry/v1":
        errors.append("REGISTRY_VERSION_UNSUPPORTED")
    if registry.get("authority_effect") != "none":
        errors.append("REGISTRY_AUTHORITY_EFFECT_FORBIDDEN")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("REGISTRY_ENTRIES_REQUIRED")
        return errors
    ids = [entry.get("ontology_id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or len(set(ids)) != len(ids):
        errors.append("REGISTRATION_IDS_NOT_UNIQUE")
    return errors


def _entry_shape_errors(entry: dict[str, Any]) -> list[str]:
    expected = {
        "ontology_id", "package_root", "profile_ref", "adapter", "material_files",
        "expected_material_digest", "source_selections", "record_sources",
        "native_validator", "owner_route", "authority_effect",
    }
    errors: list[str] = []
    if set(entry) != expected:
        errors.append("REGISTRATION_FIELD_SET_INVALID")
    if entry.get("adapter") != "cav2-json-ontology/v1":
        errors.append("ADAPTER_UNSUPPORTED")
    if entry.get("authority_effect") != "none":
        errors.append("REGISTRATION_AUTHORITY_EFFECT_FORBIDDEN")
    for field in ("material_files", "source_selections", "record_sources"):
        if not isinstance(entry.get(field), list) or not entry.get(field):
            errors.append(f"REGISTRATION_{field.upper()}_REQUIRED")
    return errors


def compile_snapshot(
    ontology_id: str,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry if registry is not None else load_registry()
    errors = _registry_errors(registry)
    try:
        entry = find_registration(registry, ontology_id)
    except RuntimeContractError as exc:
        errors.append(str(exc))
        return _blocked_snapshot(ontology_id, errors)
    errors.extend(_entry_shape_errors(entry))
    package_root: Path | None = None
    actual_material_digest: str | None = None
    selections: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    try:
        package_root = resolve_bounded(repository_root, str(entry.get("package_root", "")), kind="directory")
    except RuntimeContractError as exc:
        errors.append(str(exc))

    if package_root is not None:
        try:
            profile_path = resolve_bounded(package_root, str(entry.get("profile_ref", "")), kind="file")
            profile = load_json(profile_path)
            if profile.get("ontology_id") != ontology_id:
                errors.append("PROFILE_ONTOLOGY_ID_MISMATCH")
            if profile.get("authority_effect") != "none":
                errors.append("PROFILE_AUTHORITY_EFFECT_FORBIDDEN")
        except (RuntimeContractError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"PROFILE_INVALID:{exc}")
        try:
            raw_files = entry.get("material_files", [])
            if not isinstance(raw_files, list) or any(not isinstance(item, str) for item in raw_files):
                raise RuntimeContractError("MATERIAL_FILE_LIST_INVALID")
            actual_material_digest = material_digest(package_root, raw_files)
            if actual_material_digest != entry.get("expected_material_digest"):
                errors.append("PACKAGE_MATERIAL_DIGEST_DRIFT")
        except (RuntimeContractError, OSError) as exc:
            errors.append(f"PACKAGE_MATERIAL_INVALID:{exc}")

    selection_ids: list[str] = []
    for raw in entry.get("source_selections", []):
        if not isinstance(raw, dict):
            errors.append("SOURCE_SELECTION_OBJECT_REQUIRED")
            continue
        selection_id = str(raw.get("selection_id", ""))
        selection_ids.append(selection_id)
        try:
            digest = sha256_bytes(selected_bytes(repository_root, raw))
            current = digest == raw.get("expected_digest")
            selections.append({"selection_id": selection_id, "digest": digest, "current": current})
            if not current:
                errors.append(f"SOURCE_SELECTION_DIGEST_DRIFT:{selection_id}")
        except (RuntimeContractError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"SOURCE_SELECTION_INVALID:{selection_id}:{exc}")
    if len(set(selection_ids)) != len(selection_ids):
        errors.append("SOURCE_SELECTION_IDS_NOT_UNIQUE")

    record_keys: set[tuple[str, str]] = set()
    if package_root is not None:
        for source in entry.get("record_sources", []):
            if not isinstance(source, dict):
                errors.append("RECORD_SOURCE_OBJECT_REQUIRED")
                continue
            try:
                path = resolve_bounded(package_root, str(source.get("path", "")), kind="file")
                document = load_json(path)
                collection = document.get(str(source.get("collection", "")))
                if not isinstance(collection, list):
                    raise RuntimeContractError(f"RECORD_COLLECTION_REQUIRED:{source.get('collection')}")
                for item in collection:
                    if not isinstance(item, dict):
                        raise RuntimeContractError("RECORD_OBJECT_REQUIRED")
                    local_id = item.get(str(source.get("id_field", "")))
                    if not isinstance(local_id, str) or not local_id:
                        raise RuntimeContractError("RECORD_ID_REQUIRED")
                    kind = str(source.get("kind", ""))
                    key = (kind, local_id)
                    if key in record_keys:
                        raise RuntimeContractError(f"RECORD_ID_COLLISION:{kind}:{local_id}")
                    record_keys.add(key)
                    payload = canonical_json_bytes(item)
                    records.append({
                        "kind": kind,
                        "id": local_id,
                        "payload_digest": sha256_bytes(payload),
                        "payload": item,
                        "source_ref": f"{entry['package_root']}/{source['path']}",
                    })
            except (RuntimeContractError, OSError, json.JSONDecodeError) as exc:
                errors.append(f"RECORD_SOURCE_INVALID:{source.get('path')}:{exc}")

    expected_system_path = resolve_bounded(repository_root, SYSTEM_ONTOLOGY_REF, kind="file")
    if sha256_bytes(expected_system_path.read_bytes()) != SYSTEM_ONTOLOGY_DIGEST:
        errors.append("RUNTIME_SYSTEM_ONTOLOGY_BINDING_DRIFT")

    if errors:
        return _blocked_snapshot(ontology_id, errors, actual_material_digest, selections)
    records.sort(key=lambda item: (item["kind"], item["id"]))
    selections.sort(key=lambda item: item["selection_id"])
    content = {
        "schema_version": "cav2-ontology-runtime-snapshot/v1",
        "ontology_id": ontology_id,
        "package_root": entry["package_root"],
        "adapter": entry["adapter"],
        "registration_digest": sha256_bytes(canonical_json_bytes(entry)),
        "material_digest": actual_material_digest,
        "source_selections": selections,
        "records": records,
        "system_ontology_digest": SYSTEM_ONTOLOGY_DIGEST,
        "authority_effect": "none",
    }
    snapshot_id = sha256_bytes(canonical_json_bytes(content))
    return {
        "status": "PASS",
        "snapshot": {"snapshot_id": snapshot_id, **content},
        "errors": [],
        "authority_effect": "none",
        "claim_ceiling": SNAPSHOT_CLAIM,
    }


def _blocked_snapshot(
    ontology_id: str,
    errors: list[str],
    material: str | None = None,
    selections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "BLOCK",
        "ontology_id": ontology_id,
        "material_digest": material,
        "source_selections": sorted(selections or [], key=lambda item: item.get("selection_id", "")),
        "errors": sorted(set(errors)),
        "authority_effect": "none",
        "claim_ceiling": SNAPSHOT_CLAIM,
    }


def catalog(
    *, repository_root: Path = REPOSITORY_ROOT, registry: dict[str, Any] | None = None
) -> dict[str, Any]:
    registry = registry if registry is not None else load_registry()
    errors = _registry_errors(registry)
    entries: list[dict[str, Any]] = []
    for entry in registry.get("entries", []) if isinstance(registry.get("entries"), list) else []:
        if not isinstance(entry, dict) or not isinstance(entry.get("ontology_id"), str):
            continue
        result = compile_snapshot(entry["ontology_id"], repository_root=repository_root, registry=registry)
        snapshot = result.get("snapshot", {})
        entries.append({
            "ontology_id": entry["ontology_id"],
            "status": result["status"],
            "package_root": entry.get("package_root"),
            "material_digest": snapshot.get("material_digest", result.get("material_digest")),
            "snapshot_id": snapshot.get("snapshot_id"),
            "errors": result["errors"],
            "owner_route": entry.get("owner_route"),
        })
    if any(entry["status"] != "PASS" for entry in entries):
        errors.append("ONE_OR_MORE_REGISTRATIONS_BLOCKED")
    return {
        "schema_version": "cav2-ontology-runtime-catalog/v1",
        "status": "PASS" if not errors else "BLOCK",
        "runtime_id": "cav2.ontology-runtime",
        "entries": entries,
        "errors": sorted(set(errors)),
        "authority_effect": "none",
        "claim_ceiling": "Currentness catalog only; registration does not imply ontology acceptance or authority.",
    }


def get_record(
    ontology_id: str,
    kind: str,
    local_id: str,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = compile_snapshot(ontology_id, repository_root=repository_root, registry=registry)
    if result["status"] != "PASS":
        return result
    matches = [
        record for record in result["snapshot"]["records"]
        if record["kind"] == kind and record["id"] == local_id
    ]
    if len(matches) != 1:
        return {
            "status": "BLOCK",
            "ontology_id": ontology_id,
            "kind": kind,
            "id": local_id,
            "errors": [f"RECORD_CARDINALITY:{kind}:{local_id}:{len(matches)}"],
            "authority_effect": "none",
            "claim_ceiling": SNAPSHOT_CLAIM,
        }
    return {
        "status": "PASS",
        "ontology_id": ontology_id,
        "snapshot_id": result["snapshot"]["snapshot_id"],
        "record": matches[0],
        "errors": [],
        "authority_effect": "none",
        "claim_ceiling": SNAPSHOT_CLAIM,
    }


def run_native_validation(
    ontology_id: str,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry if registry is not None else load_registry()
    snapshot_result = compile_snapshot(ontology_id, repository_root=repository_root, registry=registry)
    if snapshot_result["status"] != "PASS":
        return {
            "schema_version": "cav2-ontology-runtime-validation/v1",
            "status": "BLOCK",
            "ontology_id": ontology_id,
            "runtime_status": "not_evaluable",
            "native_status": None,
            "native_exit_code": None,
            "snapshot_status": "BLOCK",
            "errors": snapshot_result["errors"],
            "authority_effect": "none",
            "claim_ceiling": VALIDATION_CLAIM,
        }
    entry = find_registration(registry, ontology_id)
    validator = entry.get("native_validator", {})
    argv = validator.get("argv")
    if (
        not isinstance(argv, list)
        or len(argv) != 2
        or argv[0] != "python3"
        or not isinstance(argv[1], str)
        or not argv[1].endswith(".py")
    ):
        return _failed_validation(ontology_id, "NATIVE_VALIDATOR_COMMAND_FORBIDDEN")
    try:
        validator_path = resolve_bounded(repository_root, argv[1], kind="file")
        safe_argv = [sys.executable, str(validator_path)]
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
        }
        completed = subprocess.run(
            safe_argv,
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=int(validator.get("timeout_seconds", 30)),
            check=False,
        )
    except (RuntimeContractError, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return _failed_validation(ontology_id, f"NATIVE_VALIDATOR_EXECUTION_FAILED:{exc}")
    try:
        payload = json.loads(completed.stdout)
        if not isinstance(payload, dict):
            raise ValueError("native payload must be an object")
    except (json.JSONDecodeError, ValueError) as exc:
        return _failed_validation(
            ontology_id,
            f"NATIVE_VALIDATOR_OUTPUT_INVALID:{exc}",
            exit_code=completed.returncode,
            stdout_digest=sha256_bytes(completed.stdout.encode()),
        )
    errors: list[str] = []
    declared_statuses = [
        payload[key]
        for key in ("status", "overall")
        if key in payload
    ]
    native_status = declared_statuses[0] if declared_statuses else None
    if len(set(declared_statuses)) > 1:
        errors.append("NATIVE_STATUS_CONFLICT")
    if native_status not in {"PASS", "BLOCK", "NOT_EVALUABLE"}:
        errors.append("NATIVE_STATUS_UNSUPPORTED")
    if payload.get("authority_effect") != validator.get("expected_authority_effect"):
        errors.append("NATIVE_AUTHORITY_EFFECT_MISMATCH")
    if (native_status == "PASS") != (completed.returncode == 0):
        errors.append("NATIVE_STATUS_EXIT_MISMATCH")
    status = "PASS" if not errors and native_status == "PASS" else "BLOCK"
    return {
        "schema_version": "cav2-ontology-runtime-validation/v1",
        "status": status,
        "ontology_id": ontology_id,
        "runtime_status": "succeeded" if not errors else "failed",
        "native_status": native_status,
        "native_exit_code": completed.returncode,
        "native_stdout_digest": sha256_bytes(completed.stdout.encode()),
        "native_stderr_digest": sha256_bytes(completed.stderr.encode()),
        "native_result": payload,
        "snapshot_status": "PASS",
        "snapshot_id": snapshot_result["snapshot"]["snapshot_id"],
        "errors": errors,
        "authority_effect": "none",
        "claim_ceiling": VALIDATION_CLAIM,
    }


def _failed_validation(
    ontology_id: str,
    error: str,
    *,
    exit_code: int | None = None,
    stdout_digest: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "cav2-ontology-runtime-validation/v1",
        "status": "BLOCK",
        "ontology_id": ontology_id,
        "runtime_status": "failed",
        "native_status": None,
        "native_exit_code": exit_code,
        "native_stdout_digest": stdout_digest,
        "snapshot_status": "PASS",
        "errors": [error],
        "authority_effect": "none",
        "claim_ceiling": VALIDATION_CLAIM,
    }


def validate_all(
    *, repository_root: Path = REPOSITORY_ROOT, registry: dict[str, Any] | None = None
) -> dict[str, Any]:
    registry = registry if registry is not None else load_registry()
    results = [
        run_native_validation(entry["ontology_id"], repository_root=repository_root, registry=registry)
        for entry in registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("ontology_id"), str)
    ]
    return {
        "schema_version": "cav2-ontology-runtime-validation-aggregate/v1",
        "status": "PASS" if results and all(item["status"] == "PASS" for item in results) else "BLOCK",
        "results": results,
        "errors": [] if results else ["NO_REGISTERED_ONTOLOGIES"],
        "authority_effect": "none",
        "claim_ceiling": "Collect-all wrapper results only; no aggregate acceptance or authority effect.",
    }


def route_preflight(
    ontology_id: str,
    intent: str,
    selected_route: str,
    *,
    repository_root: Path = REPOSITORY_ROOT,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if intent not in PREFLIGHT_INTENTS:
        errors.append(f"PREFLIGHT_INTENT_UNSUPPORTED:{intent}")
    if not isinstance(selected_route, str) or not selected_route.startswith("CA2-ROUTE-"):
        errors.append("PREFLIGHT_SELECTED_ROUTE_INVALID")
    if errors:
        return _blocked_preflight(ontology_id, intent, selected_route, errors)

    if intent == "validate":
        operation = run_native_validation(
            ontology_id,
            repository_root=repository_root,
            registry=registry,
        )
        snapshot_id = operation.get("snapshot_id")
        native_status = operation.get("native_status")
        status = operation.get("status")
        operation_errors = operation.get("errors", [])
    else:
        operation = compile_snapshot(
            ontology_id,
            repository_root=repository_root,
            registry=registry,
        )
        snapshot_id = operation.get("snapshot", {}).get("snapshot_id")
        native_status = None
        status = operation.get("status")
        operation_errors = operation.get("errors", [])

    core = {
        "schema_version": "cav2-ontology-runtime-route-preflight/v1",
        "status": status,
        "ontology_id": ontology_id,
        "intent": intent,
        "selected_route": selected_route,
        "selected_route_preserved": True,
        "runtime_operation": "validate" if intent == "validate" else "snapshot",
        "snapshot_id": snapshot_id,
        "native_status": native_status,
        "effect_authorized": False,
        "repeat_after_material_mutation": intent in {"mutate", "publish"},
        "errors": operation_errors,
        "authority_effect": "none",
    }
    return {
        "preflight_id": sha256_bytes(canonical_json_bytes(core)),
        **core,
        "claim_ceiling": (
            "Ontology-runtime currentness and native-result preflight only; the selected route remains "
            "the sole objective route and no mutation, acceptance, publication, release, deployment, or external effect is authorized."
        ),
    }


def _blocked_preflight(
    ontology_id: str,
    intent: str,
    selected_route: str,
    errors: list[str],
) -> dict[str, Any]:
    core = {
        "schema_version": "cav2-ontology-runtime-route-preflight/v1",
        "status": "BLOCK",
        "ontology_id": ontology_id,
        "intent": intent,
        "selected_route": selected_route,
        "selected_route_preserved": True,
        "runtime_operation": None,
        "snapshot_id": None,
        "native_status": None,
        "effect_authorized": False,
        "repeat_after_material_mutation": intent in {"mutate", "publish"},
        "errors": sorted(set(errors)),
        "authority_effect": "none",
    }
    return {
        "preflight_id": sha256_bytes(canonical_json_bytes(core)),
        **core,
        "claim_ceiling": "Blocked ontology preflight only; no route or effect authority is granted.",
    }


def _emit(result: dict[str, Any]) -> int:
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight_parser = subparsers.add_parser("route-preflight")
    preflight_parser.add_argument("--ontology", required=True)
    preflight_parser.add_argument("--intent", required=True, choices=sorted(PREFLIGHT_INTENTS))
    preflight_parser.add_argument("--route", required=True)
    subparsers.add_parser("catalog")
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--ontology", required=True)
    get_parser = subparsers.add_parser("get-record")
    get_parser.add_argument("--ontology", required=True)
    get_parser.add_argument("--kind", required=True)
    get_parser.add_argument("--id", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--ontology", required=True)
    subparsers.add_parser("validate-all")
    args = parser.parse_args()
    if args.command == "route-preflight":
        return _emit(route_preflight(args.ontology, args.intent, args.route))
    if args.command == "catalog":
        return _emit(catalog())
    if args.command == "snapshot":
        return _emit(compile_snapshot(args.ontology))
    if args.command == "get-record":
        return _emit(get_record(args.ontology, args.kind, args.id))
    if args.command == "validate":
        return _emit(run_native_validation(args.ontology))
    return _emit(validate_all())


if __name__ == "__main__":
    raise SystemExit(main())
