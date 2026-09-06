from __future__ import annotations

import argparse
import ast
import base64
import dis
import hashlib
import json
import os
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Any


READ_TARGETS = (
    "settlement.read.settlement-by-id",
    "settlement.read.payout-by-settlement",
)
RESULT_FIELDS = (
    "settlement_id",
    "settlement_status",
    "gross_amount_minor",
    "payout_id",
    "payout_status",
)


class PythonQueryObserverError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def expect_subscript(
    node: ast.expr,
    owner: str,
    key: str,
    code: str,
) -> None:
    if (
        not isinstance(node, ast.Subscript)
        or not isinstance(node.value, ast.Name)
        or node.value.id != owner
        or not isinstance(node.slice, ast.Constant)
        or node.slice.value != key
    ):
        raise PythonQueryObserverError(code)


def expect_read_assignment(
    statement: ast.stmt,
    variable: str,
    target_id: str,
) -> None:
    if (
        not isinstance(statement, ast.Assign)
        or len(statement.targets) != 1
        or not isinstance(statement.targets[0], ast.Name)
        or statement.targets[0].id != variable
        or not isinstance(statement.value, ast.Call)
        or not isinstance(statement.value.func, ast.Name)
        or statement.value.func.id != "read"
        or statement.value.keywords
        or len(statement.value.args) != 2
        or not isinstance(statement.value.args[0], ast.Constant)
        or statement.value.args[0].value != target_id
    ):
        raise PythonQueryObserverError("PY_QUERY_READ_SHAPE_INVALID", variable)
    expect_subscript(
        statement.value.args[1],
        "input_data",
        "settlement_id",
        "PY_QUERY_READ_KEY_INVALID",
    )


def inspect_source(source: str) -> dict[str, Any]:
    try:
        module = ast.parse(source, filename="query_v1.py")
    except SyntaxError as error:
        raise PythonQueryObserverError("PY_QUERY_SOURCE_SYNTAX_INVALID") from error
    if len(module.body) != 1 or type(module.body[0]) is not ast.FunctionDef:
        raise PythonQueryObserverError("PY_QUERY_EXACT_ONE_SYNC_FUNCTION_REQUIRED")
    function = module.body[0]
    if (
        function.name != "read_complete_settlement"
        or function.decorator_list
        or function.returns is not None
        or function.type_comment is not None
        or function.args.posonlyargs
        or function.args.kwonlyargs
        or function.args.vararg is not None
        or function.args.kwarg is not None
        or function.args.defaults
        or function.args.kw_defaults
        or [argument.arg for argument in function.args.args]
        != ["input_data", "read"]
        or any(argument.annotation is not None for argument in function.args.args)
        or len(function.body) != 3
    ):
        raise PythonQueryObserverError("PY_QUERY_FUNCTION_SHAPE_INVALID")
    expect_read_assignment(function.body[0], "settlement", READ_TARGETS[0])
    expect_read_assignment(function.body[1], "payout", READ_TARGETS[1])
    returned = function.body[2]
    if (
        not isinstance(returned, ast.Return)
        or not isinstance(returned.value, ast.Dict)
        or len(returned.value.keys) != len(RESULT_FIELDS)
        or len(returned.value.values) != len(RESULT_FIELDS)
    ):
        raise PythonQueryObserverError("PY_QUERY_RESULT_SHAPE_INVALID")
    keys = tuple(
        key.value if isinstance(key, ast.Constant) else None
        for key in returned.value.keys
    )
    if keys != RESULT_FIELDS:
        raise PythonQueryObserverError("PY_QUERY_RESULT_FIELDS_INVALID")
    expected_values = (
        ("input_data", "settlement_id"),
        ("settlement", "settlement_status"),
        ("settlement", "gross_amount_minor"),
        ("payout", "payout_id"),
        ("payout", "payout_status"),
    )
    for value, (owner, key) in zip(returned.value.values, expected_values):
        expect_subscript(value, owner, key, "PY_QUERY_RESULT_BINDING_INVALID")
    allowed_nodes = (
        ast.Module,
        ast.FunctionDef,
        ast.arguments,
        ast.arg,
        ast.Assign,
        ast.Name,
        ast.Store,
        ast.Load,
        ast.Call,
        ast.Constant,
        ast.Subscript,
        ast.Return,
        ast.Dict,
    )
    if any(not isinstance(node, allowed_nodes) for node in ast.walk(module)):
        raise PythonQueryObserverError("PY_QUERY_SOURCE_SURFACE_UNSUPPORTED")
    namespace: dict[str, Any] = {}
    exec(compile(module, "query_v1.py", "exec"), namespace)
    target = namespace.get("read_complete_settlement")
    if not callable(target):
        raise PythonQueryObserverError("PY_QUERY_TARGET_MISSING")
    instructions = tuple(dis.get_instructions(target.__code__))
    opnames = tuple(instruction.opname for instruction in instructions)
    if sum(opname == "CALL" for opname in opnames) != 2:
        raise PythonQueryObserverError("PY_QUERY_BYTECODE_CALL_COUNT_INVALID")
    forbidden_prefixes = (
        "IMPORT",
        "STORE_GLOBAL",
        "DELETE_GLOBAL",
        "STORE_ATTR",
        "DELETE_ATTR",
        "YIELD",
        "GET_AWAITABLE",
    )
    if any(
        opname.startswith(prefix)
        for opname in opnames
        for prefix in forbidden_prefixes
    ):
        raise PythonQueryObserverError("PY_QUERY_BYTECODE_EFFECT_INVALID")
    return {
        "schema_version": "PythonQueryClosedSubsetProof/v1",
        "source_sha256": sha256_bytes(source.encode("utf8")),
        "symbol_name": "read_complete_settlement",
        "declared_read_targets": list(READ_TARGETS),
        "result_fields": list(RESULT_FIELDS),
        "call_opcode_count": 2,
        "bytecode_opnames": sorted(set(opnames)),
        "lifecycle_basis": (
            "synchronous-return-plus-closed-plain-data-static-exclusion"
        ),
        "proof_mechanism": (
            "exact-ast-and-bytecode-rejection-plus-harness-read-trace"
        ),
        "authority_effect": "none",
    }


def freeze_json(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({
            key: freeze_json(child) for key, child in value.items()
        })
    if type(value) is list:
        return tuple(freeze_json(child) for child in value)
    return value


def decode_payload(encoded: str) -> dict[str, Any]:
    try:
        value = json.loads(base64.b64decode(encoded, validate=True).decode("utf8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonQueryObserverError("PY_QUERY_PAYLOAD_INVALID") from error
    if type(value) is not dict or set(value) != {
        "case_id",
        "input",
        "fixtures",
    }:
        raise PythonQueryObserverError("PY_QUERY_PAYLOAD_INVALID")
    if (
        type(value["case_id"]) is not str
        or type(value["input"]) is not dict
        or set(value["input"]) != {"settlement_id"}
        or type(value["input"]["settlement_id"]) is not str
        or type(value["fixtures"]) is not dict
        or set(value["fixtures"]) != set(READ_TARGETS)
        or any(type(item) is not dict for item in value["fixtures"].values())
    ):
        raise PythonQueryObserverError("PY_QUERY_PAYLOAD_INVALID")
    return value


def execute_case(source_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf8")
    closed_subset = inspect_source(source)
    namespace: dict[str, Any] = {}
    exec(compile(source, str(source_path), "exec"), namespace)
    target = namespace["read_complete_settlement"]
    input_data = freeze_json(json.loads(canonical_json(payload["input"])))
    fixtures = freeze_json(json.loads(canonical_json(payload["fixtures"])))
    trace: list[dict[str, str]] = []
    active = False
    audit_events: list[str] = []

    def audit(event: str, _arguments: tuple[Any, ...]) -> None:
        if active:
            audit_events.append(event)

    def read(target_id: str, settlement_id: str) -> Any:
        if (
            type(target_id) is not str
            or target_id not in READ_TARGETS
            or settlement_id != input_data["settlement_id"]
        ):
            raise PythonQueryObserverError("PY_QUERY_UNDECLARED_READ")
        trace.append({
            "target_id": target_id,
            "channel": "filesystem",
            "outcome": "success",
        })
        return fixtures[target_id]

    sys.addaudithook(audit)
    active = True
    try:
        result = target(input_data, read)
    finally:
        active = False
    if audit_events:
        raise PythonQueryObserverError(
            "PY_QUERY_RUNTIME_AUDIT_EFFECT",
            ",".join(sorted(set(audit_events))),
        )
    if tuple(entry["target_id"] for entry in trace) != READ_TARGETS:
        raise PythonQueryObserverError("PY_QUERY_READ_TRACE_INVALID")
    if type(result) is not dict or tuple(result.keys()) != RESULT_FIELDS:
        raise PythonQueryObserverError("PY_QUERY_RESULT_SHAPE_INVALID")
    if (
        any(type(result[field]) is not str for field in RESULT_FIELDS if field !=
            "gross_amount_minor")
        or type(result["gross_amount_minor"]) is not int
    ):
        raise PythonQueryObserverError("PY_QUERY_RESULT_VALUE_INVALID")
    materialized = json.loads(canonical_json(result))
    if materialized != result:
        raise PythonQueryObserverError("PY_QUERY_RESULT_NOT_INERT")
    return {
        "schema_version": "PythonQueryCaseObservation/v1",
        "case_id": payload["case_id"],
        "pid": os.getpid(),
        "trace": trace,
        "result": materialized,
        "source_proof": closed_subset,
        "runtime_audit_events": [],
        "result_consumption": "complete-json-materialization",
        "mutable_alias_observed": False,
        "quiescence": {
            "observed": True,
            "pending_count": 0,
            "basis": "exact-sync-subset-and-successful-child-exit",
        },
        "authority_effect": "none",
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--payload-base64", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        if not arguments.source.is_file() or arguments.source.is_symlink():
            raise PythonQueryObserverError("PY_QUERY_SOURCE_MISSING")
        payload = decode_payload(arguments.payload_base64)
        result = execute_case(arguments.source, payload)
        sys.stdout.write(canonical_json(result))
        return 0
    except PythonQueryObserverError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
