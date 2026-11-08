from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


OWNER_PATH = (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/"
    "owner-member-wire-catalogue.json"
)
DENOMINATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "finite-vocabulary/fixtures/shipment-priority/denominator.json"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/"
    "python/nominal-enum-v1/python-binding.json"
)
EXPECTED_ERROR_CODE = "DOMAINSPEC_ENUM_UNKNOWN_WIRE"


class PythonEnumProofError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def document_digest(value: dict[str, Any], field: str) -> str:
    return sha256_bytes(canonical_json({
        key: child for key, child in value.items() if key != field
    }).encode("utf8"))


def read_bytes(root: Path, relative: str) -> bytes:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise PythonEnumProofError("PY_ENUM_INPUT_MISSING", relative)
    return path.read_bytes()


def load_module(source_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("domainspec_enum_candidate", source_path)
    if spec is None or spec.loader is None:
        raise PythonEnumProofError("PY_ENUM_SOURCE_IMPORT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise PythonEnumProofError("PY_ENUM_SOURCE_IMPORT_FAILED", type(error).__name__) from error
    return module


def _expect_ref(value: Any, code: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise PythonEnumProofError(code)
    if not isinstance(value["path"], str) or not isinstance(value["sha256"], str):
        raise PythonEnumProofError(code)
    return value


def _native_members(
    enum_class: Any,
    owner_members: list[dict[str, str]],
    emit: Any,
    parse: Any,
    member_id: Any,
) -> list[dict[str, Any]]:
    owner_by_key = {item["member_key"]: item for item in owner_members}
    grouped: dict[int, tuple[Any, list[str]]] = {}
    for key, member in enum_class.__members__.items():
        identity = id(member)
        if identity not in grouped:
            grouped[identity] = (member, [])
        grouped[identity][1].append(key)

    observed: list[dict[str, Any]] = []
    for member, native_keys in grouped.values():
        matched = [owner_by_key[key] for key in native_keys if key in owner_by_key]
        observed_member_id = matched[0]["member_id"] if matched else (
            f"implementation-unexpected:{native_keys[0]}"
        )
        emitted = emit(member)
        parsed = parse(emitted)
        observed.append({
            "member_id": observed_member_id,
            "native_keys": sorted(native_keys),
            "emitted_wire": emitted,
            "parsed_member_id": member_id(parsed),
        })
    return sorted(observed, key=lambda item: item["member_id"])


def build_proof(repository_root: Path) -> dict[str, Any]:
    binding_bytes = read_bytes(repository_root, BINDING_PATH)
    try:
        binding = json.loads(binding_bytes)
    except json.JSONDecodeError as error:
        raise PythonEnumProofError("PY_ENUM_BINDING_JSON_INVALID") from error
    if not isinstance(binding, dict) or document_digest(binding, "binding_sha256") != binding.get("binding_sha256"):
        raise PythonEnumProofError("PY_ENUM_BINDING_STALE")

    owner_ref = _expect_ref(binding.get("owner_catalogue_ref"), "PY_ENUM_OWNER_REF_INVALID")
    if owner_ref["path"] != OWNER_PATH:
        raise PythonEnumProofError("PY_ENUM_OWNER_REF_INVALID")
    owner_bytes = read_bytes(repository_root, OWNER_PATH)
    if sha256_bytes(owner_bytes) != owner_ref["sha256"]:
        raise PythonEnumProofError("PY_ENUM_OWNER_CATALOGUE_STALE")
    try:
        owner = json.loads(owner_bytes)
    except json.JSONDecodeError as error:
        raise PythonEnumProofError("PY_ENUM_OWNER_CATALOGUE_JSON_INVALID") from error
    if owner.get("authorship") != "owner-authored-admission-input" or owner.get(
        "derivation_policy"
    ) != "runtime-and-generated-members-forbidden-as-authority":
        raise PythonEnumProofError("PY_ENUM_OWNER_CATALOGUE_POLICY_INVALID")
    owner_members = owner.get("members")
    if not isinstance(owner_members, list) or not owner_members:
        raise PythonEnumProofError("PY_ENUM_OWNER_CATALOGUE_MEMBERS_INVALID")

    denominator_ref = _expect_ref(
        binding.get("denominator_ref"), "PY_ENUM_DENOMINATOR_REF_INVALID"
    )
    if denominator_ref["path"] != DENOMINATOR_PATH:
        raise PythonEnumProofError("PY_ENUM_DENOMINATOR_REF_INVALID")
    denominator_bytes = read_bytes(repository_root, DENOMINATOR_PATH)
    if sha256_bytes(denominator_bytes) != denominator_ref["sha256"]:
        raise PythonEnumProofError("PY_ENUM_DENOMINATOR_INPUT_STALE")
    try:
        denominator = json.loads(denominator_bytes)
    except json.JSONDecodeError as error:
        raise PythonEnumProofError("PY_ENUM_DENOMINATOR_JSON_INVALID") from error
    denominator_body = {
        key: child for key, child in denominator.items()
        if key != "denominator_sha256"
    }
    if isinstance(denominator_body.get("positive_decisions"), list):
        denominator_body["positive_decisions"] = sorted(
            denominator_body["positive_decisions"]
        )
    if sha256_bytes(canonical_json(denominator_body).encode("utf8")) != denominator.get(
        "denominator_sha256"
    ):
        raise PythonEnumProofError("PY_ENUM_DENOMINATOR_DIGEST_STALE")
    denominator_owner_ref = denominator.get("owner_catalogue_ref")
    if not isinstance(denominator_owner_ref, dict) or (
        denominator_owner_ref.get("path") != OWNER_PATH
        or denominator_owner_ref.get("sha256") != owner_ref["sha256"]
        or denominator_owner_ref.get("catalogue_id") != owner.get("catalogue_id")
    ):
        raise PythonEnumProofError("PY_ENUM_DENOMINATOR_OWNER_REF_STALE")

    source_ref = _expect_ref(binding.get("source_ref"), "PY_ENUM_SOURCE_REF_INVALID")
    source_bytes = read_bytes(repository_root, source_ref["path"])
    if sha256_bytes(source_bytes) != source_ref["sha256"]:
        raise PythonEnumProofError("PY_ENUM_SOURCE_STALE")
    module = load_module(repository_root / source_ref["path"])
    enum_class = getattr(module, binding.get("symbol_name", ""), None)
    emit = getattr(module, binding.get("emit_symbol", ""), None)
    parse = getattr(module, binding.get("parse_symbol", ""), None)
    member_id = getattr(module, binding.get("member_id_symbol", ""), None)
    wire_error = getattr(module, binding.get("wire_error_symbol", ""), None)
    member_error = getattr(module, binding.get("member_error_symbol", ""), None)
    if not isinstance(enum_class, type) or not all(callable(item) for item in (
        emit, parse, member_id, wire_error, member_error,
    )):
        raise PythonEnumProofError("PY_ENUM_EXPORT_MISSING")

    members = _native_members(enum_class, owner_members, emit, parse, member_id)
    probe = binding.get("unknown_wire_probe")
    if not isinstance(probe, str) or probe in {
        item["wire_value"] for item in owner_members
    }:
        raise PythonEnumProofError("PY_ENUM_UNKNOWN_PROBE_INVALID")

    constructor_rejected = False
    try:
        enum_class(probe)
    except ValueError:
        constructor_rejected = True

    structured_failure: dict[str, Any] | None = None
    parsed_unknown: str | None = None
    try:
        parsed_unknown = member_id(parse(probe))
    except wire_error as error:
        structured_failure = error.as_dict() if hasattr(error, "as_dict") else None

    extension_rejected = False
    try:
        exec(
            "class ExtendedShipmentPriority(ShipmentPriority):\n    Bulk = 'bulk'\n",
            {"ShipmentPriority": enum_class},
        )
    except TypeError:
        extension_rejected = True

    invalid_member_emit_rejected = False
    try:
        emit(object())
    except member_error as error:
        invalid_member_emit_rejected = (
            getattr(error, "code", None) == "DOMAINSPEC_ENUM_MEMBER_INVALID"
            and getattr(error, "enum_id", None) == owner.get("concept_id")
        )

    runtime_members = list(enum_class)
    native_properties = {
        "str_mixin_absent": not issubclass(enum_class, str),
        "aliases_absent": len(enum_class.__members__) == len(runtime_members),
        "raw_string_equality_false": all(
            member != emit(member) and emit(member) != member
            for member in runtime_members
        ),
        "known_emit_parse_total": len(members) == len(runtime_members) and all(
            isinstance(item["emitted_wire"], str)
            and isinstance(item["parsed_member_id"], str)
            for item in members
        ),
    }
    hostile_probes = {
        "unknown_constructor_rejected": constructor_rejected,
        "unknown_wire_structured_failure": structured_failure == {
            "code": EXPECTED_ERROR_CODE,
            "enum_id": owner.get("concept_id"),
            "wire_value": probe,
        } and parsed_unknown is None,
        "extension_rejected": extension_rejected,
        "invalid_member_emit_rejected": invalid_member_emit_rejected,
    }
    return {
        "schema_version": "PythonEnumNativeProof/v1",
        "result": "pass" if all(native_properties.values()) and all(
            hostile_probes.values()
        ) else "block",
        "target": {
            "target_id": "python.shipment-priority.nominal-enum-v1",
            "language": "python",
            "protocol_id": "python.nominal-enum-explicit-wire/v1",
        },
        "owner_catalogue_ref": {
            "catalogue_id": owner["catalogue_id"],
            "path": OWNER_PATH,
            "sha256": owner_ref["sha256"],
        },
        "denominator_ref": {
            "denominator_id": denominator["denominator_id"],
            "path": DENOMINATOR_PATH,
            "sha256": denominator_ref["sha256"],
            "denominator_sha256": denominator["denominator_sha256"],
        },
        "source_ref": source_ref,
        "catalogue_origin": "owner-authored-admission-input",
        "member_order_semantics": "none",
        "members": members,
        "unknown_wire": {
            "wire_value": probe,
            "outcome": "structured-failure" if structured_failure else "member",
            "error_code": structured_failure.get("code") if structured_failure else None,
            "parsed_member_id": parsed_unknown,
        },
        "native_identity_diagnostic": {
            "relation": "nominal",
            "claim_scope": "native-diagnostic-only",
        },
        "native_properties": native_properties,
        "hostile_probes": hostile_probes,
        "structured_failure": structured_failure,
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    try:
        proof = build_proof(Path(arguments.repository_root).resolve())
        Path(arguments.output).write_text(
            f"{json.dumps(proof, indent=2, sort_keys=True)}\n", encoding="utf8"
        )
        return 0 if proof["result"] == "pass" else 2
    except PythonEnumProofError as error:
        sys.stderr.write(f"{error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
