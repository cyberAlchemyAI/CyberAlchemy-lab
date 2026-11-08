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
from typing import Any


EFFECT_CHANNELS = (
    "clock",
    "random",
    "environment",
    "filesystem",
    "network",
    "process",
    "global-cache",
    "delayed-lazy",
    "callback",
    "iterator-future",
    "finalizer-drop",
    "mutable-output",
)


class PythonCalculationObservationError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _name(node: ast.expr | None) -> str | None:
    return node.id if isinstance(node, ast.Name) else None


def validate_closed_subset(source: str) -> ast.FunctionDef:
    try:
        module = ast.parse(source, filename="calculation_v1.py", mode="exec")
    except SyntaxError as error:
        raise PythonCalculationObservationError(
            "PY_CALC_CLOSED_SUBSET_SYNTAX",
        ) from error
    if len(module.body) != 1:
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_MODULE")
    function = module.body[0]
    if not isinstance(function, ast.FunctionDef):
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_CALLABLE")
    if (
        function.name != "calculate_net_settlement"
        or function.decorator_list
        or function.type_comment is not None
        or function.args.posonlyargs
        or function.args.vararg is not None
        or function.args.kwonlyargs
        or function.args.kw_defaults
        or function.args.kwarg is not None
        or function.args.defaults
        or len(function.args.args) != 2
        or _name(function.returns) != "int"
    ):
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_SIGNATURE")
    expected_arguments = ("gross_amount_minor", "fee_amount_minor")
    for argument, expected in zip(function.args.args, expected_arguments, strict=True):
        if argument.arg != expected or _name(argument.annotation) != "int":
            raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_SIGNATURE")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.Return):
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_BODY")
    expression = function.body[0].value
    if not (
        isinstance(expression, ast.BinOp)
        and isinstance(expression.op, ast.Sub)
        and _name(expression.left) == "gross_amount_minor"
        and _name(expression.right) == "fee_amount_minor"
    ):
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_EXPRESSION")
    return function


def load_closed_calculation(source: str) -> Any:
    validate_closed_subset(source)
    namespace: dict[str, Any] = {"__builtins__": {"int": int}}
    try:
        exec(compile(source, "calculation_v1.py", "exec"), namespace)
    except Exception as error:
        raise PythonCalculationObservationError(
            "PY_CALC_CLOSED_SUBSET_LOAD",
            type(error).__name__,
        ) from error
    calculation = namespace.get("calculate_net_settlement")
    if not callable(calculation):
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_EXPORT")
    instructions = tuple(
        (instruction.opname, instruction.argrepr)
        for instruction in dis.get_instructions(calculation)
    )
    expected = (
        ("RESUME", ""),
        ("LOAD_FAST", "gross_amount_minor"),
        ("LOAD_FAST", "fee_amount_minor"),
        ("BINARY_OP", "-"),
        ("RETURN_VALUE", ""),
    )
    if instructions != expected:
        raise PythonCalculationObservationError("PY_CALC_CLOSED_SUBSET_BYTECODE")
    return calculation


def decode_case(encoded: str) -> dict[str, Any]:
    try:
        value = json.loads(base64.b64decode(encoded, validate=True).decode("utf8"))
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise PythonCalculationObservationError("PY_CALC_CASE_INVALID") from error
    if not isinstance(value, dict) or set(value) != {
        "case_id",
        "gross_amount_minor",
        "fee_amount_minor",
    }:
        raise PythonCalculationObservationError("PY_CALC_CASE_INVALID")
    if not isinstance(value["case_id"], str) or not value["case_id"]:
        raise PythonCalculationObservationError("PY_CALC_CASE_INVALID")
    for field in ("gross_amount_minor", "fee_amount_minor"):
        if type(value[field]) is not int:
            raise PythonCalculationObservationError("PY_CALC_INPUT_NOT_EXACT_INT", field)
    return value


def observe(source_path: Path, case: dict[str, Any]) -> dict[str, Any]:
    if not source_path.is_file() or source_path.is_symlink():
        raise PythonCalculationObservationError("PY_CALC_SOURCE_MISSING")
    source_bytes = source_path.read_bytes()
    try:
        source = source_bytes.decode("utf8", errors="strict")
    except UnicodeDecodeError as error:
        raise PythonCalculationObservationError("PY_CALC_SOURCE_UTF8") from error
    calculation = load_closed_calculation(source)
    audit_events: list[str] = []

    def reject_audit_event(event: str, _arguments: tuple[Any, ...]) -> None:
        audit_events.append(event)
        raise PythonCalculationObservationError("PY_CALC_AUDIT_EVENT", event)

    sys.addaudithook(reject_audit_event)
    result = calculation(
        case["gross_amount_minor"],
        case["fee_amount_minor"],
    )
    if type(result) is not int:
        raise PythonCalculationObservationError("PY_CALC_RESULT_NOT_EXACT_INT")
    if audit_events:
        raise PythonCalculationObservationError("PY_CALC_AUDIT_EVENT")
    result_bytes = json.dumps(
        result,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf8")
    return {
        "schema_version": "PythonCalculationCaseObservation/v1",
        "case_id": case["case_id"],
        "pid": os.getpid(),
        "source_sha256": sha256_bytes(source_bytes),
        "result_kind": "number",
        "result_value": result,
        "result_sha256": sha256_bytes(result_bytes),
        "audit_events": audit_events,
        "effect_channels": [
            {
                "channel": channel,
                "coverage": "supported",
                "read_count": 0,
                "write_count": 0,
                "escape_count": 0,
                "deferred_count": 0,
            }
            for channel in EFFECT_CHANNELS
        ],
        "result_consumption": "complete",
        "mutable_alias_observed": False,
        "quiescence_observed": True,
        "pending_count": 0,
        "mechanism": "exact-ast-bytecode-subset-plus-python-audit-hook",
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--case-base64", required=True)
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    try:
        case = decode_case(arguments.case_base64)
        result = observe(Path(arguments.source).resolve(), case)
        sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except PythonCalculationObservationError as error:
        sys.stderr.write(f"{error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
