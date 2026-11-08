from __future__ import annotations

import argparse
import ast
import base64
from dataclasses import FrozenInstanceError, asdict
import dis
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


class PythonValueObjectObserverError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def inspect_source(source: str) -> dict[str, Any]:
    try:
        module = ast.parse(source, filename="value_object_v1.py")
    except SyntaxError as error:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_SOURCE_INVALID") from error
    forbidden_nodes = (
        ast.AsyncFunctionDef,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Global,
        ast.Nonlocal,
        ast.With,
        ast.AsyncWith,
    )
    if any(isinstance(node, forbidden_nodes) for node in ast.walk(module)):
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_SOURCE_SURFACE_UNSUPPORTED")
    allowed_imports = {"__future__", "dataclasses", "hashlib", "typing"}
    for node in module.body:
        if isinstance(node, ast.Import):
            if any(alias.name not in allowed_imports for alias in node.names):
                raise PythonValueObjectObserverError("PY_VALUE_OBJECT_IMPORT_UNSUPPORTED")
        if isinstance(node, ast.ImportFrom) and node.module not in allowed_imports:
            raise PythonValueObjectObserverError("PY_VALUE_OBJECT_IMPORT_UNSUPPORTED")
    forbidden_names = {
        "open", "exec", "eval", "compile", "__import__", "globals", "locals",
        "getattr", "setattr", "delattr", "input", "breakpoint",
    }
    for node in ast.walk(module):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_names:
                raise PythonValueObjectObserverError("PY_VALUE_OBJECT_CALL_UNSUPPORTED")
    required = (
        "@dataclass(frozen=True, slots=True)\nclass SettlementAccountValue:",
        "@dataclass(frozen=True, slots=True)\nclass SettlementValue:",
        "self.minor_units_sha256 == other.minor_units_sha256",
        "self.settlement_account == other.settlement_account",
        "return _stable_hash((\n"
        "            self.currency_sha256,\n"
        "            self.minor_units_sha256,\n"
        "            self.settlement_account.protocol_id,\n"
        "            self.settlement_account.protocol_sha256,\n"
        "            self.settlement_account.normalized_value_sha256,\n"
        "        ))",
        "input_data.settlement_account.account_ref,",
        "observed.protocol_sha256 == expected.protocol_sha256",
        "for validator in self.validators:",
        "return ValidationFailure(\n                False,\n                None,",
        "def extend_with_account_active(self) -> SettlementValueFactory | None:",
        "return SettlementValueFactory(\"with-account-active\")",
        '"extension_policy": "additive-validation-only"',
        '"equality_mode": "complete-normalized-tuple"',
        '"hash_mode": "same-normalized-complete-tuple"',
    )
    if any(token not in source for token in required):
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_REQUIRED_SEMANTIC")
    namespace: dict[str, Any] = {}
    exec(compile(module, "value_object_v1.py", "exec"), namespace)
    factory_type = namespace.get("SettlementValueFactory")
    value_type = namespace.get("SettlementValue")
    account_type = namespace.get("SettlementAccountValue")
    if not all(isinstance(item, type) for item in (factory_type, value_type, account_type)):
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_SYMBOL_MISSING")
    methods = (
        factory_type.create,
        factory_type.extend_with_account_active,
        value_type.__eq__,
        value_type.__hash__,
        account_type.__eq__,
        account_type.__hash__,
    )
    instructions = [instruction for method in methods for instruction in dis.get_instructions(method)]
    forbidden_prefixes = (
        "IMPORT", "STORE_GLOBAL", "DELETE_GLOBAL", "STORE_ATTR", "DELETE_ATTR",
        "YIELD", "GET_AWAITABLE",
    )
    if any(
        instruction.opname.startswith(prefix)
        for instruction in instructions
        for prefix in forbidden_prefixes
    ):
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_BYTECODE_EFFECT_INVALID")
    return {
        "schema_version": "PythonValueObjectClosedSubsetProof/v1",
        "source_sha256": sha256_bytes(source.encode("utf8")),
        "mechanism": "exact-source-ast-bytecode-and-runtime-observation",
        "bytecode_opnames": sorted({item.opname for item in instructions}),
        "authority_effect": "none",
    }


def decode_payload(encoded: str) -> dict[str, Any]:
    try:
        value = json.loads(base64.b64decode(encoded, validate=True).decode("utf8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_PAYLOAD_INVALID") from error
    if type(value) is not dict or set(value) != {"cases", "probes", "nested_probe"}:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_PAYLOAD_INVALID")
    if type(value["cases"]) is not list or type(value["probes"]) is not list:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_PAYLOAD_INVALID")
    if type(value["nested_probe"]) is not dict:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_PAYLOAD_INVALID")
    return value


def execute(source_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf8")
    source_proof = inspect_source(source)
    namespace: dict[str, Any] = {}
    exec(compile(source, str(source_path), "exec"), namespace)
    component_input = namespace["ComponentInput"]
    account_input = namespace["SettlementAccountInput"]
    value_input = namespace["SettlementValueInput"]
    base_factory = namespace["create_settlement_value_factory"]()
    factory = base_factory.extend_with_account_active()
    if factory is None or factory.extend_with_account_active() is not None:
        raise PythonValueObjectObserverError("PY_VALUE_OBJECT_EXTENSION_GRAPH_INVALID")

    def validator_refs(owner: Any) -> list[dict[str, str]]:
        return [asdict(item) for item in owner.validators]

    formed: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for entry in payload["cases"]:
        components = entry["components"]
        account_source = account_input(
            components["settlement_account"]["protocol_id"],
            components["settlement_account"]["protocol_sha256"],
            components["settlement_account"]["normalized_value_sha256"],
            entry["case_id"],
            True,
        )
        input_data = value_input(
            component_input(**components["currency"]),
            component_input(**components["minor_units"]),
            account_source,
        )
        base_result = base_factory.create(input_data)
        result = factory.create(input_data)
        object.__setattr__(account_source, "account_ref", "mutated-after-formation")
        formed_mutation = False
        nested_mutation = False
        if result.ok:
            outer_before = result.value.currency_sha256
            try:
                setattr(result.value, "currency_sha256", "0" * 64)
            except FrozenInstanceError:
                pass
            formed_mutation = result.value.currency_sha256 != outer_before
            before = result.value.settlement_account.account_ref
            try:
                setattr(result.value.settlement_account, "account_ref", "direct-mutation")
            except FrozenInstanceError:
                pass
            nested_mutation = result.value.settlement_account.account_ref != before
            formed[entry["case_id"]] = result.value
        rows.append({
            "case_id": entry["case_id"],
            "input_class": entry["input_class"],
            "ok": result.ok,
            "object_created": result.value is not None,
            "failure_codes": list(result.failure_codes),
            "validator_trace": list(result.validator_trace),
            "formation_ordinal": len(result.validator_trace) if result.ok else None,
            "component_bindings": [asdict(item) for item in result.value.component_bindings]
                if result.ok else [
                    {"component_name": name, **components[name],
                     "nested_value_object": name == "settlement_account"}
                    for name in ("currency", "minor_units", "settlement_account")
                ],
            "tuple": list(result.value.normalized_tuple) if result.ok else None,
            "hash": str(hash(result.value)) if result.ok else None,
            "frozen": result.ok and not formed_mutation,
            "nested_frozen": result.ok and not nested_mutation,
            "nested_alias": result.ok
                and result.value.settlement_account.account_ref != entry["case_id"],
            "nested_mutation": nested_mutation,
            "base_ok": base_result.ok,
            "base_tuple": list(base_result.value.normalized_tuple) if base_result.ok else None,
            "base_hash": str(hash(base_result.value)) if base_result.ok else None,
            "base_component_bindings": [asdict(item) for item in base_result.value.component_bindings]
                if base_result.ok else None,
            "base_equals_extended": base_result.ok and result.ok
                and base_result.value == result.value,
            "extended_equals_base": base_result.ok and result.ok
                and result.value == base_result.value,
        })
    equality_probes: list[dict[str, Any]] = []
    for probe in payload["probes"]:
        left = formed[probe["left_case_id"]]
        right = formed[probe["right_case_id"]]
        equality_probes.append({
            **probe,
            "references_distinct": left is not right,
            "observed_equal": left == right,
            "left_hash": str(hash(left)),
            "right_hash": str(hash(right)),
        })
    nested_definition = payload["nested_probe"]
    nested_left = formed[nested_definition["left_case_id"]].settlement_account
    nested_right = formed[nested_definition["right_case_id"]].settlement_account
    nested_variant = formed[nested_definition["variant_case_id"]].settlement_account
    nested_probe = {
        "component_name": nested_definition["component_name"],
        "protocol_id": nested_left.protocol_id,
        "protocol_sha256": nested_left.protocol_sha256,
        "equal_observed": nested_left == nested_right,
        "equal_hash_congruent": hash(nested_left) == hash(nested_right),
        "variant_unequal_observed": nested_left != nested_variant,
    }
    successful = [row for row in rows if row["ok"]]
    extension_input = payload["cases"][0]
    extension_components = extension_input["components"]
    inactive = value_input(
        component_input(**extension_components["currency"]),
        component_input(**extension_components["minor_units"]),
        account_input(
            extension_components["settlement_account"]["protocol_id"],
            extension_components["settlement_account"]["protocol_sha256"],
            extension_components["settlement_account"]["normalized_value_sha256"],
            extension_input["case_id"],
            False,
        ),
    )
    base_probe = base_factory.create(inactive)
    extension_probe = factory.create(inactive)
    extension = {
        "base_factory_ref": base_factory.factory_ref,
        "extension_factory_ref": factory.factory_ref,
        "base_validators": validator_refs(base_factory),
        "extension_validators": validator_refs(factory),
        "added_validators": validator_refs(factory)[len(validator_refs(base_factory)):],
        "base_preserved": validator_refs(factory)[:len(validator_refs(base_factory))]
            == validator_refs(base_factory),
        "tuple_and_hash_preserved": all(
            row["tuple"] == row["base_tuple"] and row["hash"] == row["base_hash"]
            for row in successful
        ),
        "component_bindings_and_normalization_preserved": all(
            row["component_bindings"] == row["base_component_bindings"]
            for row in successful
        ),
        "equality_preserved": all(
            row["base_equals_extended"] and row["extended_equals_base"]
            for row in successful
        ),
        "recursive_immutability_preserved": all(
            row["frozen"] and row["nested_frozen"]
            and not row["nested_alias"] and not row["nested_mutation"]
            for row in successful
        ),
        "concept_binding_preserved": (
            base_factory.factory_ref["concept_id"] == factory.factory_ref["concept_id"]
        ),
        "extension_is_terminal": factory.extend_with_account_active() is None,
        "validation_probe": {
            "base_ok": base_probe.ok,
            "extended_ok": extension_probe.ok,
            "extended_object_created": extension_probe.value is not None,
            "extended_failure_codes": list(extension_probe.failure_codes),
            "extended_validator_trace": list(extension_probe.validator_trace),
        },
    }
    executable = Path(os.path.realpath(sys.executable))
    return {
        "schema_version": "PythonValueObjectRuntimeObservation/v1",
        "pid": os.getpid(),
        "source_proof": source_proof,
        "results": rows,
        "equality_probes": equality_probes,
        "nested_probe": nested_probe,
        "extension": extension,
        "toolchain": {
            "python_version": sys.version.split()[0],
            "executable_path": str(executable),
            "executable_sha256": sha256_bytes(executable.read_bytes()),
        },
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--payload-base64", required=True)
    arguments = parser.parse_args()
    try:
        if not arguments.source.is_file() or arguments.source.is_symlink():
            raise PythonValueObjectObserverError("PY_VALUE_OBJECT_SOURCE_MISSING")
        result = execute(arguments.source, decode_payload(arguments.payload_base64))
        sys.stdout.write(canonical_json(result))
        return 0
    except PythonValueObjectObserverError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
