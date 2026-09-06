from __future__ import annotations

import argparse
import ast
import dis
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


SOURCE_PATH = Path(
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/policy_v1.py"
)
DEFINITION_PATH = Path(
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "strategy-selection/fixtures/settlement-routing/selector-definition.json"
)
REQUIRED_FACTS = (
    "amount_minor",
    "expedite_limit_minor",
    "expedite_requested",
    "manual_review_required",
)
REQUIRED_IDENTITIES = (
    "settlement.route.standard",
    "settlement.route.expedited",
    "settlement.route.manual-review",
)
FORBIDDEN_OP_PREFIXES = (
    "CALL",
    "IMPORT",
    "STORE_GLOBAL",
    "DELETE_GLOBAL",
    "STORE_ATTR",
    "DELETE_ATTR",
    "YIELD",
    "GET_AWAITABLE",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def inspect_source(source: str) -> dict[str, Any]:
    module = ast.parse(source, filename="policy_v1.py")
    functions = [
        node for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(functions) != 1 or type(functions[0]) is not ast.FunctionDef:
        raise RuntimeError("PY_POLICY_EXACT_ONE_SYNC_FUNCTION_REQUIRED")
    selector = functions[0]
    if selector.name != "select_settlement_route" or len(selector.args.args) != 1:
        raise RuntimeError("PY_POLICY_FUNCTION_SHAPE_INVALID")
    if selector.decorator_list or selector.args.vararg or selector.args.kwarg:
        raise RuntimeError("PY_POLICY_FUNCTION_SHAPE_INVALID")
    if len(selector.body) != 1 or not isinstance(selector.body[0], ast.Return):
        raise RuntimeError("PY_POLICY_RETURN_SHAPE_INVALID")
    forbidden = (
        ast.Call,
        ast.Attribute,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Global,
        ast.Nonlocal,
        ast.NamedExpr,
        ast.Lambda,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )
    if any(isinstance(node, forbidden) for node in ast.walk(selector)):
        raise RuntimeError("PY_POLICY_EFFECT_OR_EXECUTION_SYNTAX_FORBIDDEN")
    facts = sorted({
        node.slice.value
        for node in ast.walk(selector)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "input_data"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, str)
    })
    identities = sorted({
        node.value
        for node in ast.walk(selector)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("settlement.route.")
    })
    conditional_count = sum(
        isinstance(node, ast.IfExp) for node in ast.walk(selector)
    )
    if facts != sorted(REQUIRED_FACTS):
        raise RuntimeError("PY_POLICY_EXPLICIT_INPUT_COVERAGE_INVALID")
    if identities != sorted(REQUIRED_IDENTITIES):
        raise RuntimeError("PY_POLICY_STRATEGY_IDENTITY_SET_INVALID")
    if conditional_count != 2:
        raise RuntimeError("PY_POLICY_BRANCH_SHAPE_INVALID")
    namespace: dict[str, Any] = {}
    exec(compile(module, "policy_v1.py", "exec"), namespace)
    selector_code = namespace["select_settlement_route"].__code__
    opnames = tuple(instruction.opname for instruction in dis.get_instructions(selector_code))
    if any(
        opname.startswith(prefix)
        for opname in opnames
        for prefix in FORBIDDEN_OP_PREFIXES
    ):
        raise RuntimeError("PY_POLICY_BYTECODE_EFFECT_OR_CALL_FORBIDDEN")
    return {
        "schema_version": "PythonPolicyClosedSubsetProof/v1",
        "source_sha256": sha256_bytes(source.encode("utf8")),
        "symbol_name": "select_settlement_route",
        "explicit_input_facts": facts,
        "strategy_identities": identities,
        "conditional_branches": conditional_count,
        "target_call_opcodes": 0,
        "bytecode_opnames": sorted(set(opnames)),
        "proof_mechanism": (
            "closed-selector-ast-and-bytecode-rejection-plus-two-fresh-processes"
        ),
        "authority_effect": "none",
    }


def load_selector(source_path: Path):
    spec = importlib.util.spec_from_file_location("domainspec_policy_target", source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PY_POLICY_TARGET_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.select_settlement_route


def execute_child(source_path: Path, case_json: str) -> int:
    selector = load_selector(source_path)
    inputs = json.loads(case_json)
    nested_calls = 0
    active = False

    def profile(frame, event, arg):
        nonlocal active, nested_calls
        if frame.f_code is selector.__code__:
            if event == "call":
                active = True
            elif event == "return":
                active = False
            return profile
        if active and event in ("call", "c_call"):
            nested_calls += 1
        return profile

    sys.setprofile(profile)
    try:
        selected = selector(inputs)
    finally:
        sys.setprofile(None)
    if type(selected) is not str or not selected.startswith("settlement.route."):
        return 23
    sys.stdout.write(canonical_json({
        "pid": os.getpid(),
        "selected": selected,
        "nested_call_count": nested_calls,
    }))
    return 0


def run_fresh_case(
    supervisor: Path,
    source_path: Path,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(supervisor),
            "--child-source",
            str(source_path),
            "--case-json",
            canonical_json(inputs),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if completed.stderr:
        raise RuntimeError("PY_POLICY_CHILD_STDERR")
    value = json.loads(completed.stdout)
    if (
        type(value.get("pid")) is not int
        or type(value.get("selected")) is not str
        or type(value.get("nested_call_count")) is not int
    ):
        raise RuntimeError("PY_POLICY_CHILD_OUTPUT_INVALID")
    return value


def build_proof(repository_root: Path) -> dict[str, Any]:
    source_path = repository_root / SOURCE_PATH
    definition_path = repository_root / DEFINITION_PATH
    source = source_path.read_text(encoding="utf8")
    definition = json.loads(definition_path.read_text(encoding="utf8"))
    closed_subset = inspect_source(source)
    observed_cases: list[dict[str, Any]] = []
    pids: list[int] = []
    nested_calls = 0
    for case in definition["cases"]:
        first = run_fresh_case(Path(__file__), source_path, case["inputs"])
        second = run_fresh_case(Path(__file__), source_path, case["inputs"])
        if first["pid"] == second["pid"]:
            raise RuntimeError("PY_POLICY_PROCESS_ISOLATION_FAILED")
        if first["selected"] != second["selected"]:
            raise RuntimeError("PY_POLICY_NONDETERMINISTIC")
        pids.extend((first["pid"], second["pid"]))
        nested_calls += first["nested_call_count"] + second["nested_call_count"]
        selected = first["selected"]
        observed_cases.append({
            "case_id": case["case_id"],
            "input_sha256": sha256_bytes(
                canonical_json(case["inputs"]).encode("utf8")
            ),
            "selected_strategy_id": selected,
            "selected_sha256": sha256_bytes(canonical_json(selected).encode("utf8")),
            "nested_call_count": (
                first["nested_call_count"] + second["nested_call_count"]
            ),
        })
    return {
        "schema_version": "PythonPolicyNativeProof/v1",
        "result": "pass",
        "closed_subset": closed_subset,
        "observed_cases": observed_cases,
        "fresh_processes_executed": len(pids),
        "distinct_processes": len(set(pids)),
        "strategy_execution_attempts": nested_calls,
        "quiescence_basis": "closed-subset-plus-successful-child-exit",
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--child-source", type=Path)
    parser.add_argument("--case-json")
    args = parser.parse_args()
    if args.child_source is not None and args.case_json is not None:
        return execute_child(args.child_source, args.case_json)
    if args.repository_root is None or args.output is None:
        raise RuntimeError("PY_POLICY_ARGUMENTS_INVALID")
    proof = build_proof(args.repository_root.resolve())
    args.output.write_text(
        json.dumps(proof, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
