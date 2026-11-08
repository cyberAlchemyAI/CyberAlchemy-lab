from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


def sha256(value: bytes | str) -> str:
    raw = value.encode("utf8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def document_digest(value: dict[str, Any], field: str) -> str:
    return sha256(canonical_json({key: child for key, child in value.items() if key != field}))


class RuleProofError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def inspect_source(source: str, symbol_name: str) -> dict[str, Any]:
    diagnostics: list[str] = []
    try:
        module = ast.parse(source, filename="candidate.py", mode="exec")
    except SyntaxError:
        return {"supported": False, "diagnostics": ["PY_RULE_PARSE_DIAGNOSTIC"]}
    if any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(module)):
        diagnostics.append("PY_RULE_IMPORT_UNSUPPORTED")
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if len(module.body) != 1 or len(functions) != 1 or functions[0].name != symbol_name:
        diagnostics.append("PY_RULE_MODULE_SHAPE_UNSUPPORTED")
        return {"supported": False, "diagnostics": diagnostics, "tree": module}
    function = functions[0]
    if function.decorator_list or len(function.args.args) != 1 or function.args.vararg or \
            function.args.kwarg or len(function.body) != 1 or not isinstance(function.body[0], ast.Return) or \
            not isinstance(function.returns, ast.Name) or function.returns.id != "bool":
        diagnostics.append("PY_RULE_FUNCTION_SHAPE_UNSUPPORTED")
        return {"supported": False, "diagnostics": diagnostics, "tree": module}
    parameter = function.args.args[0].arg

    def pure(node: ast.AST) -> bool:
        if isinstance(node, ast.BoolOp):
            return isinstance(node.op, (ast.And, ast.Or)) and all(pure(value) for value in node.values)
        if isinstance(node, ast.Compare):
            return pure(node.left) and all(
                isinstance(operator, (ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Is, ast.IsNot))
                for operator in node.ops
            ) and all(pure(child) for child in node.comparators)
        if isinstance(node, ast.Subscript):
            return isinstance(node.value, ast.Name) and node.value.id == parameter and \
                isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)
        if isinstance(node, ast.UnaryOp):
            return isinstance(node.op, ast.Not) and pure(node.operand)
        return isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool, type(None)))

    returned = function.body[0].value
    if returned is None or not pure(returned):
        diagnostics.append("PY_RULE_EXPRESSION_UNSUPPORTED")
    return {"supported": not diagnostics, "diagnostics": diagnostics, "tree": module}


class RuleMutator(ast.NodeTransformer):
    def __init__(self, defect: str):
        self.defect = defect
        self.applied = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if self.applied or len(node.body) != 1 or not isinstance(node.body[0], ast.Return):
            return node
        returned = node.body[0]
        expression = returned.value
        if not isinstance(expression, ast.BoolOp) or not isinstance(expression.op, ast.And) or \
                len(expression.values) < 2:
            return node
        if self.defect == "wrong-result":
            expression.values[0] = ast.Constant(value=False)
        elif self.defect == "bypass-check":
            returned.value = expression.values[0]
        else:
            effect_name = "__domainspec_rule_effect_count"
            update = ast.Assign(
                targets=[ast.Name(id=effect_name, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Call(
                        func=ast.Attribute(value=ast.Call(func=ast.Name(id="globals", ctx=ast.Load()), args=[], keywords=[]), attr="get", ctx=ast.Load()),
                        args=[ast.Constant(value=effect_name), ast.Constant(value=0)],
                        keywords=[],
                    ),
                    op=ast.Add(),
                    right=ast.Constant(value=1),
                ),
            )
            node.body = [
                ast.Global(names=[effect_name]),
                ast.If(test=expression, body=[update], orelse=[]),
                returned,
            ]
        self.applied = True
        return node


def mutate_source(source: str, symbol_name: str, defect: str) -> str:
    inspection = inspect_source(source, symbol_name)
    if not inspection["supported"]:
        raise RuleProofError("PY_RULE_MUTATION_BASE_UNSUPPORTED")
    mutator = RuleMutator(defect)
    tree = mutator.visit(inspection["tree"])
    if not mutator.applied:
        raise RuleProofError("PY_RULE_MUTATION_NOT_APPLICABLE")
    ast.fix_missing_locations(tree)
    return f"{ast.unparse(tree)}\n"


HARNESS = r'''import json, sys
payload = json.loads(sys.stdin.read())
namespace = {"__name__": "__domainspec_rule_candidate__"}
exec(compile(payload["source"], "candidate.py", "exec"), namespace)
rule = namespace.get(payload["symbol"])
if not callable(rule):
    raise RuntimeError("PY_RULE_RUNTIME_EXPORT_MISSING")
observations = []
for case in payload["cases"]:
    namespace["__domainspec_rule_effect_count"] = 0
    try:
        outcome = rule(case["input"])
    except Exception:
        outcome = None
    observations.append({
        "case_id": case["case_id"],
        "outcome": outcome if type(outcome) in (bool, str, int, float) or outcome is None else None,
        "observed_effect_count": namespace.get("__domainspec_rule_effect_count", 0),
    })
sys.stdout.write(json.dumps(observations, separators=(",", ":")))
'''


def execute_source(source: str, symbol_name: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        compile(source, "candidate.py", "exec", dont_inherit=True, optimize=0)
    except SyntaxError as error:
        return {"exit_status": 1, "diagnostics": [f"PY{error.lineno}:syntax"], "observations": []}
    with tempfile.TemporaryDirectory(prefix="domainspec-rule-python-") as workspace:
        completed = subprocess.run(
            [sys.executable, "-I", "-c", HARNESS],
            input=json.dumps({"source": source, "symbol": symbol_name, "cases": cases}),
            text=True,
            capture_output=True,
            cwd=workspace,
            env={"PATH": os.environ.get("PATH", "")},
            timeout=30,
            check=False,
        )
    if completed.returncode != 0:
        return {"exit_status": completed.returncode, "diagnostics": ["PY_RULE_RUNTIME_FAILED"], "observations": []}
    return {
        "exit_status": 0,
        "diagnostics": [],
        "observations": json.loads(completed.stdout),
        "workspace": {"isolated": True, "cleaned": True, "symlinks": False},
    }


def evaluate(obligations: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_case = {item["case_id"]: item for item in observations}
    findings: list[dict[str, Any]] = []
    for obligation in obligations["obligations"]:
        case_id = obligation["case_id"]
        if obligation["kind"] == "binding-current":
            continue
        observed = by_case.get(case_id)
        if observed is None:
            findings.append({"code": "RULE_OUTCOME_MISSING", "case_id": case_id})
        elif obligation["kind"] == "case-outcome-exact" and \
                (type(observed["outcome"]) is not bool or observed["outcome"] != obligation["expected_outcome"]):
            findings.append({"code": "RULE_OUTCOME_MISMATCH", "case_id": case_id})
        elif obligation["kind"] == "effect-free" and observed["observed_effect_count"] != 0:
            findings.append({"code": "RULE_EFFECT_OBSERVED", "case_id": case_id})
    unique = {(item["code"], item["case_id"]): item for item in findings}
    return [unique[key] for key in sorted(unique)]


def build_proof(root: Path) -> dict[str, Any]:
    common = root / "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout"
    target = root / "projects/domainspec-v2/impl/architecture-conformance/targets/python/fixtures"
    definition = json.loads((common / "rule-definition.json").read_text(encoding="utf8"))
    cases = json.loads((common / "cases.json").read_text(encoding="utf8"))
    obligations = json.loads((common / "obligations.json").read_text(encoding="utf8"))
    mutants = json.loads((common / "mutants.json").read_text(encoding="utf8"))
    binding_bytes = (target / "python-binding.json").read_text(encoding="utf8")
    binding = json.loads(binding_bytes)
    source_bytes = (root / binding["source_ref"]["path"]).read_bytes()
    source = source_bytes.decode("utf8")
    if document_digest(definition, "definition_sha256") != definition["definition_sha256"] or \
            document_digest(cases, "catalogue_sha256") != cases["catalogue_sha256"] or \
            document_digest(obligations, "catalogue_sha256") != obligations["catalogue_sha256"] or \
            document_digest(mutants, "catalogue_sha256") != mutants["catalogue_sha256"]:
        raise RuleProofError("PY_RULE_SEMANTIC_INPUT_STALE")
    exact_rule_ref = {
        "rule_id": definition["rule_id"],
        "definition_sha256": definition["definition_sha256"],
    }
    if cases["rule_ref"] != exact_rule_ref or obligations["rule_ref"] != exact_rule_ref or \
            mutants["rule_ref"] != exact_rule_ref or binding["rule_ref"] != exact_rule_ref or \
            obligations["case_catalogue_sha256"] != cases["catalogue_sha256"] or \
            binding["target_id"] != "python" or binding["current"] is not True or \
            sha256(source_bytes) != binding["source_ref"]["sha256"] or \
            document_digest(binding, "binding_sha256") != binding["binding_sha256"]:
        raise RuleProofError("PY_RULE_BINDING_STALE")
    inspection = inspect_source(source, binding["symbol_name"])
    if not inspection["supported"]:
        raise RuleProofError(inspection["diagnostics"][0])
    positive = execute_source(source, binding["symbol_name"], cases["cases"])
    positive_findings = evaluate(obligations, positive["observations"])
    positive_results = [
        {"case_id": case["case_id"], "status": "passed" if not positive_findings else "failed"}
        for case in sorted(cases["cases"], key=lambda item: item["case_id"])
    ]
    mutation_results = []
    for mutant in mutants["mutations"]:
        mutated = mutate_source(source, binding["symbol_name"], mutant["defect"])
        executed = execute_source(mutated, binding["symbol_name"], cases["cases"])
        findings = evaluate(obligations, executed["observations"])
        exact = findings == [{"code": mutant["expected_finding_code"], "case_id": mutant["case_id"]}]
        mutation_results.append({
            "mutation_id": mutant["mutation_id"],
            "case_id": mutant["case_id"],
            "finding_code": findings[0]["code"] if len(findings) == 1 else None,
            "status": "killed" if exact else "survived",
            "source_sha256": sha256(mutated),
        })
    summary = {
        "schema_version": "RuleProofSummary/v1",
        "rule_id": definition["rule_id"],
        "target_id": "python",
        "realization_id": binding["realization_id"],
        "positive": positive_results,
        "mutations": [{key: item[key] for key in ("mutation_id", "case_id", "finding_code", "status")} for item in mutation_results],
        "accounting": {
            "result": "pass" if all(item["status"] == "passed" for item in positive_results) and all(item["status"] == "killed" for item in mutation_results) else "block",
            "positive": {"declared": len(positive_results), "passed": sum(item["status"] == "passed" for item in positive_results), "failed": sum(item["status"] == "failed" for item in positive_results), "unaccounted": 0},
            "mutations": {"declared": len(mutation_results), "killed": sum(item["status"] == "killed" for item in mutation_results), "survived": sum(item["status"] == "survived" for item in mutation_results), "unaccounted": 0},
        },
        "claim_ceiling": "one candidate-local handwritten Python Rule in the admitted pure-function subset",
        "authority_effect": "none",
    }
    if positive["exit_status"] != 0 or summary["accounting"]["result"] != "pass":
        raise RuleProofError("PY_RULE_PROOF_ACCOUNTING_BLOCKED")
    return {
        "summary": summary,
        "summary_sha256": sha256(canonical_json(summary)),
        "static": {"ast": "stdlib", "supported": True, "source_sha256": sha256(source_bytes)},
        "runtime": positive,
        "mutations": mutation_results,
        "toolchain": {"python": sys.version.split()[0], "executable": sys.executable, "executable_sha256": sha256(Path(sys.executable).read_bytes())},
        "authority_effect": "none",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    proof = build_proof(arguments.repository_root.resolve())
    rendered = json.dumps(proof, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf8", newline="\n")
    sys.stdout.write(json.dumps({"status": "pass", "summary_sha256": proof["summary_sha256"], "output": str(arguments.output) if arguments.output else None, "authority_effect": "none"}) + "\n")


if __name__ == "__main__":
    main()
