"""Deterministic, read-only AST inventory of inherited API regression methods."""

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / "product/lab/release-candidates/v1/interface/api-v96"
CURRENT = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v36-current-t06-0001"
PLAN = ROOT / "docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-plan-0274.json"
PLAN_SHA256 = "b04c3f6a9953765b807adf4f8ef72b480c6c51985a1b1c563535395f86b8ac40"
CURRENT_SOURCE_SHA256 = "5990d980ae1df2fe59c90eabfc9de806ea8ab7abbf90bb123063f5ad83ff592f"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def method_ast_sha(node):
    return sha(ast.dump(node, annotate_fields=True, include_attributes=False).encode())


def scan(directory):
    rows = {}
    files = {}
    for path in sorted(directory.glob("*.py")):
        raw = path.read_bytes()
        tree = ast.parse(raw.decode("utf-8"), filename=str(path))
        found = False
        for cls in tree.body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for method in cls.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) or not method.name.startswith("test_"):
                    continue
                ident = f"{path.name}:{cls.name}.{method.name}"
                if ident in rows:
                    raise ValueError("duplicate regression method: " + ident)
                rows[ident] = {"file": path.relative_to(ROOT).as_posix(), "method_ast_sha256": method_ast_sha(method)}
                found = True
        if found:
            files[path.relative_to(ROOT).as_posix()] = sha(raw)
    return rows, files


def build():
    plan_raw = PLAN.read_bytes()
    plan = json.loads(plan_raw)
    if sha(plan_raw) != PLAN_SHA256 or plan["original_api_directory"] != OLD.relative_to(ROOT).as_posix():
        raise ValueError("frozen original regression selection changed")
    source_raw = (CURRENT / "source-manifest.json").read_bytes()
    if sha(source_raw) != CURRENT_SOURCE_SHA256:
        raise ValueError("selected API36 source changed")
    source = json.loads(source_raw)
    if len(source["files"]) != 207 or len({r["path"] for r in source["files"]}) != 207:
        raise ValueError("selected API36 source rows changed")
    for row in source["files"]:
        path = ROOT / row["path"]
        if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError("selected API36 source file changed")
    old, old_files = scan(OLD)
    selected_old = plan["original_method_inventory"]
    if set(old) != set(selected_old["methods"]) or any(
        row["method_ast_sha256"] != selected_old["methods"][ident]["method_ast_sha256"]
        for ident, row in old.items()
    ):
        raise ValueError("frozen original method AST changed")
    if set(old_files) != {r["file_binding"]["path"] for r in selected_old["modules"].values()} or any(
        old_files[row["file_binding"]["path"]] != row["file_binding"]["sha256"]
        for row in selected_old["modules"].values()
    ):
        raise ValueError("frozen original method files changed")
    new, new_files = scan(CURRENT)
    if len(old) != 323 or len(new) != 345:
        raise ValueError("inherited method count changed")
    missing = sorted(old.keys() - new.keys())
    added = sorted(new.keys() - old.keys())
    if missing or len(added) != 22 or any(not x.startswith("test_installation_release.py:") for x in added):
        raise ValueError("inherited method identity changed")
    changed = sorted(k for k in old.keys() & new.keys() if old[k]["method_ast_sha256"] != new[k]["method_ast_sha256"])
    return {"schema_version": "lab-t15-inherited-method-inventory/v1", "original_directory": OLD.relative_to(ROOT).as_posix(),
            "current_directory": CURRENT.relative_to(ROOT).as_posix(), "original_count": 323, "current_count": 345,
            "frozen_original_plan_sha256": PLAN_SHA256, "current_source_manifest_sha256": CURRENT_SOURCE_SHA256,
            "current_source_rows_rehashed": 207,
            "missing_original_methods": missing, "added_method_ids": added, "changed_method_ids": changed,
            "original_file_sha256": dict(sorted(old_files.items())), "current_file_sha256": dict(sorted(new_files.items())),
            "original_methods": dict(sorted(old.items())), "current_methods": dict(sorted(new.items())),
            "tests_executed": False, "integrated_candidate_frozen": False}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
