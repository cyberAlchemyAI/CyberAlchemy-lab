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


CLOSURE = "return-await-cancel-close-dispose-finalizer-quiescence"


class PythonOperationObserverError(Exception):
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


def freeze_json(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({
            key: freeze_json(child) for key, child in value.items()
        })
    if type(value) is list:
        return tuple(freeze_json(child) for child in value)
    return value


def inspect_source(source: str) -> dict[str, Any]:
    try:
        module = ast.parse(source, filename="operation_v1.py")
    except SyntaxError as error:
        raise PythonOperationObserverError(
            "PY_OP_SOURCE_SYNTAX_INVALID",
        ) from error
    if len(module.body) != 1 or type(module.body[0]) is not ast.FunctionDef:
        raise PythonOperationObserverError(
            "PY_OP_EXACT_ONE_SYNC_FUNCTION_REQUIRED",
        )
    function = module.body[0]
    if (
        function.name != "complete_settlement_operation"
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
        != ["input_data", "ports"]
        or any(argument.annotation is not None for argument in function.args.args)
    ):
        raise PythonOperationObserverError("PY_OP_FUNCTION_SHAPE_INVALID")
    forbidden_nodes = (
        ast.Import,
        ast.ImportFrom,
        ast.AsyncFunctionDef,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Global,
        ast.Nonlocal,
        ast.ClassDef,
        ast.Lambda,
        ast.With,
        ast.AsyncWith,
    )
    if any(isinstance(node, forbidden_nodes) for node in ast.walk(function)):
        raise PythonOperationObserverError("PY_OP_SOURCE_SURFACE_UNSUPPORTED")
    forbidden_names = {
        "open",
        "eval",
        "exec",
        "compile",
        "__import__",
        "globals",
        "locals",
        "getattr",
        "setattr",
        "input",
        "breakpoint",
    }
    if any(
        isinstance(node, ast.Name) and node.id in forbidden_names
        for node in ast.walk(function)
    ):
        raise PythonOperationObserverError("PY_OP_AMBIENT_NAME_FORBIDDEN")
    allowed_ports = {
        "ports": {"guard", "read", "begin_atomic", "external_effect", "close"},
        "transaction": {"write", "commit", "rollback"},
    }
    for call in (
        node for node in ast.walk(function) if isinstance(node, ast.Call)
    ):
        if (
            not isinstance(call.func, ast.Subscript)
            or not isinstance(call.func.value, ast.Name)
            or call.func.value.id not in allowed_ports
            or not isinstance(call.func.slice, ast.Constant)
            or type(call.func.slice.value) is not str
            or call.func.slice.value not in allowed_ports[call.func.value.id]
        ):
            raise PythonOperationObserverError("PY_OP_CALL_SURFACE_UNSUPPORTED")
    namespace: dict[str, Any] = {}
    exec(compile(module, "operation_v1.py", "exec"), namespace)
    target = namespace.get("complete_settlement_operation")
    if not callable(target):
        raise PythonOperationObserverError("PY_OP_TARGET_MISSING")
    instructions = tuple(dis.get_instructions(target.__code__))
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
        instruction.opname.startswith(prefix)
        for instruction in instructions
        for prefix in forbidden_prefixes
    ):
        raise PythonOperationObserverError("PY_OP_BYTECODE_EFFECT_INVALID")
    return {
        "schema_version": "PythonOperationClosedSubsetProof/v1",
        "source_sha256": sha256_bytes(source.encode("utf8")),
        "symbol_name": "complete_settlement_operation",
        "lifecycle_basis": "synchronous-return-plus-injected-port-quiescence",
        "proof_mechanism": "ast-bytecode-audit-plus-injected-port-trace",
        "bytecode_opnames": sorted({
            instruction.opname for instruction in instructions
        }),
        "authority_effect": "none",
    }


def decode_payload(encoded: str) -> dict[str, Any]:
    try:
        value = json.loads(base64.b64decode(
            encoded,
            validate=True,
        ).decode("utf8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonOperationObserverError("PY_OP_PAYLOAD_INVALID") from error
    if type(value) is not dict or set(value) != {
        "case_id",
        "input",
        "current_state_version",
        "fixtures",
    }:
        raise PythonOperationObserverError("PY_OP_PAYLOAD_INVALID")
    if (
        value["case_id"] not in {"committed-success", "guard-rejected"}
        or type(value["input"]) is not dict
        or set(value["input"]) != {
            "settlement_id",
            "expected_state_version",
        }
        or type(value["input"]["settlement_id"]) is not str
        or type(value["input"]["expected_state_version"]) is not int
        or type(value["current_state_version"]) is not int
        or type(value["fixtures"]) is not dict
        or set(value["fixtures"]) != {
            "settlement.read.settlement-by-id",
            "settlement.read.payout-account",
        }
        or any(type(item) is not dict for item in value["fixtures"].values())
    ):
        raise PythonOperationObserverError("PY_OP_PAYLOAD_INVALID")
    return value


def execute_case(source_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf8")
    source_proof = inspect_source(source)
    namespace: dict[str, Any] = {}
    exec(compile(source, str(source_path), "exec"), namespace)
    target = namespace["complete_settlement_operation"]
    input_data = freeze_json(json.loads(canonical_json(payload["input"])))
    fixtures = freeze_json(json.loads(canonical_json(payload["fixtures"])))
    trace: list[str] = []
    reads: list[str] = []
    writes: list[str] = []
    effects: list[str] = []
    events: list[dict[str, Any]] = []
    guards: list[dict[str, Any]] = []
    audit_events: list[str] = []
    active = False
    commit_mode = "all-or-nothing"
    commit_count = 0
    rollback_count = 0
    begin_count = 0
    close_count = 0
    continuation_closure: str | None = None

    def audit(event: str, _arguments: tuple[Any, ...]) -> None:
        if active:
            audit_events.append(event)

    def guard(guard_id: Any, guard_input: Any) -> dict[str, bool]:
        trace.append(f"guard:{guard_id}")
        try:
            supplied = dict(guard_input)
        except (TypeError, ValueError):
            supplied = {}
        current_version_observed = (
            guard_id == "rule.can-settle-payout"
            and set(supplied) == {
                "settlement_id",
                "expected_state_version",
            }
            and supplied["settlement_id"] == input_data["settlement_id"]
            and supplied["expected_state_version"]
            == input_data["expected_state_version"]
        )
        allowed = (
            current_version_observed
            and supplied["expected_state_version"]
            == payload["current_state_version"]
        )
        guards.append({
            "guard_id": str(guard_id),
            "invoked": True,
            "decision": "pass" if allowed else "fail",
            "current_state_version_observed": current_version_observed,
        })
        return {"allowed": allowed}

    def read(target_id: Any, settlement_id: Any) -> Any:
        target_name = str(target_id)
        reads.append(target_name)
        trace.append(f"read:{target_name}")
        if (
            target_name in fixtures
            and settlement_id == input_data["settlement_id"]
        ):
            return fixtures[target_name]
        return MappingProxyType({})

    def begin_atomic() -> MappingProxyType:
        nonlocal begin_count, commit_count, commit_mode, rollback_count
        begin_count += 1
        trace.append("atomic:begin")

        def write(target_id: Any, _value: Any) -> None:
            target_name = str(target_id)
            writes.append(target_name)
            trace.append(f"write:{target_name}")

        def commit(mode: Any) -> None:
            nonlocal commit_count, commit_mode
            commit_mode = str(mode)
            commit_count += 1
            trace.append("atomic:commit")

        def rollback() -> None:
            nonlocal rollback_count
            rollback_count += 1
            trace.append("atomic:rollback")

        return MappingProxyType({
            "write": write,
            "commit": commit,
            "rollback": rollback,
        })

    def external_effect(target_id: Any, event: Any) -> None:
        target_name = str(target_id)
        effects.append(target_name)
        trace.append(f"effect:{target_name}")
        event_type = (
            event.get("event_type")
            if hasattr(event, "get")
            else "Unknown"
        )
        trace.append(f"event:{event_type}")
        events.append({
            "event_type": str(event_type),
            "tense": "past-tense",
            "trace_ordinal": len(trace) - 1,
        })

    def close(closure: Any, failure_code: Any) -> None:
        nonlocal close_count, continuation_closure
        continuation_closure = str(closure)
        if failure_code is not None:
            trace.append("outcome:failure")
        trace.append("continuation:close")
        close_count += 1

    ports = MappingProxyType({
        "guard": guard,
        "read": read,
        "begin_atomic": begin_atomic,
        "external_effect": external_effect,
        "close": close,
    })
    sys.addaudithook(audit)
    active = True
    try:
        result = target(input_data, ports)
    finally:
        active = False
    if audit_events:
        raise PythonOperationObserverError(
            "PY_OP_RUNTIME_AUDIT_EFFECT",
            ",".join(sorted(set(audit_events))),
        )
    if type(result) is not dict or set(result) != {
        "kind",
        "value",
        "failure_code",
        "exactly_once_distributed_delivery_claimed",
    }:
        raise PythonOperationObserverError("PY_OP_RESULT_SHAPE_INVALID")
    if result["kind"] == "success":
        trace.append("outcome:success")
    return {
        "pid": os.getpid(),
        "case_id": payload["case_id"],
        "input": payload["input"],
        "result": result,
        "trace": trace,
        "reads": reads,
        "writes": writes,
        "effects": effects,
        "events": events,
        "guards": guards,
        "commit_mode": commit_mode,
        "commit_count": commit_count,
        "rollback_count": rollback_count,
        "begin_count": begin_count,
        "close_count": close_count,
        "continuation_closure": continuation_closure,
        "source_proof": source_proof,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--payload-base64", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        payload = decode_payload(arguments.payload_base64)
        result = execute_case(arguments.source, payload)
        sys.stdout.write(canonical_json(result))
        return 0
    except PythonOperationObserverError as error:
        sys.stderr.write(str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
