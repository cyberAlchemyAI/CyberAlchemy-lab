#!/usr/bin/env python3
"""Strict local JSON transport to the candidate Lean stress-profile functions."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parent
FORMAL = BASE.parents[2] / "formal"
ROOT = next(p for p in BASE.parents if (p / "authority/admissions/governance-transaction-surface").is_dir())
CORE_MODULES = ["StressTypes", "DelegationSemantics", "ObligationSemantics", "StressCheckers", "StressRuntime"]
spec = importlib.util.spec_from_file_location("stress_f0_helpers", FORMAL / "validate_f0.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def schema(name):
    return json.loads((BASE / "schemas" / (name + ".schema.json")).read_text())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def decode(text):
    if len(text.encode("utf-8")) > 32 * 1024 * 1024:
        raise ValueError("request exceeds 32 MiB transport limit")
    def reject_constant(value):
        raise ValueError("non-finite JSON number: " + value)
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)


def validate_request(request):
    # Python's JSON decoder accepts isolated surrogate escapes. They cannot be
    # encoded as UTF-8 Lean source and are rejected before the compiler boundary.
    def strings(value):
        if isinstance(value, str):
            value.encode("utf-8", errors="strict")
        elif isinstance(value, list):
            for item in value:
                strings(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                strings(key)
                strings(item)
    strings(request)
    validator = Draft202012Validator(schema("request"))
    errors = list(validator.iter_errors(request))
    if errors:
        # The top-level oneOf diagnostic is bounded and does not echo input.
        raise ValueError("request does not match the strict profile schema")


def lean_string(value):
    # JSON and Lean share these two escapes for strings without control chars.
    # Unicode is kept literal. No input can terminate the quoted Lean string.
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("control character in Lean string transport")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def encode(value, kind):
    fields = {
        "ref": [("id", "string"), ("version", "string")],
        "period": [("start", "nat"), ("stop", "nat")],
        "assessment": [("ref", "ref"), ("accepted", "bool")],
        "snapshot": [("ref", "ref"), ("epoch", "nat"), ("policies", "list:assessment"), ("gates", "list:assessment")],
        "delegation": [("ref", "ref"), ("agent", "ref"), ("principal", "ref"), ("scopes", "list:string"), ("actions", "list:string"), ("period", "period"), ("revokedAt", "option:nat"), ("policies", "list:ref"), ("gates", "list:ref"), ("redelegationAllowed", "bool")],
        "actsEdge": [("id", "string"), ("agent", "ref"), ("principal", "ref"), ("delegation", "ref"), ("scope", "string"), ("period", "period"), ("revokedAt", "option:nat")],
        "norm": [("mode", "mode"), ("action", "string")],
        "contract": [("ref", "ref"), ("scope", "string"), ("condition", "string"), ("interpreted", "bool"), ("norms", "list:norm")],
        "binding": [("ref", "ref"), ("subject", "ref"), ("contracts", "list:ref"), ("scope", "string"), ("active", "bool"), ("overrides", "list:ref")],
        "inheritance": [("id", "string"), ("subject", "ref"), ("contract", "ref"), ("binding", "ref"), ("scope", "string"), ("condition", "string")],
        "conformance": [("subject", "ref"), ("contract", "ref"), ("scope", "string"), ("accepted", "bool")],
        "graph": [("inheritances", "list:inheritance"), ("bindings", "list:binding"), ("contracts", "list:contract"), ("conformance", "list:conformance")],
        "fact": [("edge", "inheritance"), ("norm", "norm")],
        "step": [("rule", "rule"), ("fact", "fact"), ("parent", "option:nat")],
    }
    if kind == "string":
        return lean_string(value)
    if kind == "nat":
        return str(int(value))
    if kind == "bool":
        return "true" if value else "false"
    if kind in {"mode", "rule"}:
        return "." + value  # Closed enum validated before this function.
    if kind.startswith("list:"):
        return "[" + ", ".join(encode(v, kind[5:]) for v in value) + "]"
    if kind.startswith("option:"):
        return "none" if value is None else "(some " + encode(value, kind[7:]) + ")"
    return "{ " + ", ".join(k + " := " + encode(value[k], t) for k, t in fields[kind]) + " }"


def pinned_lean():
    lean = FORMAL / ".toolcache/lean-4.33.1-linux/bin/lean"
    lock = json.loads((FORMAL / "toolchain-lock.json").read_text())
    helpers.require(subprocess.check_output([str(lean), "--version"], text=True).strip() == lock["version_output"], "toolchain version drift")
    helpers.require(helpers.digest(lean) == lock["lean_binary_sha256"], "compiler binary drift")
    helpers.require(helpers.digest(lean.parent.parent / "lib/lean/libleanshared.so") == lock["lean_shared_library_sha256"], "kernel/runtime drift")
    return lean


def compile_into(build, lean, modules=CORE_MODULES):
    env = {**os.environ, "LEAN_PATH": str(build)}
    logs = []
    for name in modules:
        src = BASE / (name + ".lean")
        target = build / src.name
        shutil.copyfile(src, target)
        result = subprocess.run([str(lean), "-o", str(target.with_suffix(".olean")), str(target)],
                                cwd=build, env=env, text=True, capture_output=True, timeout=60)
        output = result.stdout + result.stderr
        helpers.require(result.returncode == 0 and "warning:" not in output, "Lean build failed: " + name + "\n" + output)
        logs.append({"module": name, "output": output, "source_sha256": helpers.digest(src),
                     "olean_sha256": helpers.digest(target.with_suffix(".olean"))})
    return logs


def query_source(request):
    op = request["operation"]
    if op == "evaluate-acts-for":
        expression = "actsResult (" + encode(request["delegations"], "list:delegation") + ") (" + encode(request["snapshot"], "snapshot") + ") (" + encode(request["edge"], "actsEdge") + ") " + encode(request["action"], "string") + " " + encode(request["redelegated"], "bool")
    else:
        expression = ("inheritanceResult" if op == "close-inherits-contract" else "certificateResult") + " (" + encode(request["graph"], "graph") + ") " + encode(request["budget"], "nat")
        if op == "replay-certificate":
            expression += " (" + encode(request["steps"], "list:step") + ")"
    return "import StressRuntime\nopen Stress Stress.Runtime\ndef main : IO Unit := IO.println ((" + expression + ").compress)\n"


def timeout_response(request):
    op = request["operation"]
    result = {"operation": op, "status": "unknown", "reason": "runtime-budget-exceeded"}
    if op == "evaluate-acts-for":
        result.update(snapshot=request["snapshot"]["ref"], epoch=request["snapshot"]["epoch"], assertionId=request["edge"]["id"])
    elif op == "close-inherits-contract":
        result.update(complete=False, facts=[], conflicts=[], certificate=[])
    else:
        result.update(accepted=False, stepCount=len(request["steps"]))
    return result


def evaluate(request, build, lean, timeout=30):
    validate_request(request)
    query = build / "TransportQuery.lean"
    query.write_text(query_source(request))
    try:
        result = subprocess.run([str(lean), "--run", str(query)], cwd=build,
                                env={**os.environ, "LEAN_PATH": str(build)},
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return timeout_response(request)
    helpers.require(result.returncode == 0, "Lean request failed: " + result.stdout + result.stderr)
    response = decode(result.stdout)
    helpers.require(not list(Draft202012Validator(schema("response")).iter_errors(response)),
                    "runtime response violates the transport contract")
    return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="Read a JSON request file; otherwise use stdin")
    args = parser.parse_args()
    try:
        text = args.request.read_text() if args.request else sys.stdin.read(32 * 1024 * 1024 + 1)
        request = decode(text)
        validate_request(request)
    except (ValueError, UnicodeError, OSError) as error:
        message = str(error).encode("unicode_escape").decode("ascii")[:2048]
        response = {"operation": "decode-error", "status": "invalid", "reason": "invalid-transport", "errors": [message]}
        print(json.dumps(response, ensure_ascii=True))
        return 2
    try:
        lean = pinned_lean()
        with tempfile.TemporaryDirectory(prefix="relation-stress-cli-") as folder:
            build = Path(folder)
            compile_into(build, lean)
            response = evaluate(request, build, lean)
        print(json.dumps(response, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("stress CLI unavailable: " + str(error), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
