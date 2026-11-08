"""Deterministic, read-only AST inventory of inherited API regression methods."""

import ast
import hashlib
import json
from pathlib import Path
import stat


ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / "product/lab/release-candidates/v1/interface/api-v96"
CURRENT = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v38-current-t06-0001"
PLAN = ROOT / "docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-plan-0274.json"
PLAN_SHA256 = "b04c3f6a9953765b807adf4f8ef72b480c6c51985a1b1c563535395f86b8ac40"
CURRENT_SOURCE_SHA256 = "71f5ba4008ce1955265e949bb5250a5af6d9cc5da046d40c8fa7c6a765f774a7"
CURRENT_PROFILE_SHA256 = "32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def method_ast_sha(node):
    return sha(ast.dump(node, annotate_fields=True, include_attributes=False).encode())


def regular_without_symlink_parents(root, path):
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if not relative.parts or any(part in (".", "..") for part in relative.parts):
        return False
    parent = root
    for part in relative.parts[:-1]:
        parent /= part
        if not stat.S_ISDIR(parent.lstat().st_mode):
            return False
    return stat.S_ISREG(path.lstat().st_mode)


def scan(directory):
    rows = {}
    files = {}
    for path in sorted(directory.glob("*.py")):
        if not regular_without_symlink_parents(ROOT, path):
            raise ValueError("regression test origin changed: " + str(path))
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
        raise ValueError("selected API38 source changed")
    source = json.loads(source_raw)
    profile_raw = (CURRENT / "contract-profile.json").read_bytes()
    if sha(profile_raw) != CURRENT_PROFILE_SHA256 or source["profile_binding"] != {
        "path": (CURRENT / "contract-profile.json").relative_to(ROOT).as_posix(),
        "sha256": CURRENT_PROFILE_SHA256,
    }:
        raise ValueError("selected API38 profile changed")
    if len(source["files"]) != 207 or len({r["path"] for r in source["files"]}) != 207:
        raise ValueError("selected API38 source rows changed")
    for row in source["files"]:
        path = ROOT / row["path"]
        if not regular_without_symlink_parents(ROOT, path) or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError("selected API38 source file changed")
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
            "current_profile_sha256": CURRENT_PROFILE_SHA256,
            "current_source_rows_rehashed": 207,
            "missing_original_methods": missing, "added_method_ids": added, "changed_method_ids": changed,
            "original_file_sha256": dict(sorted(old_files.items())), "current_file_sha256": dict(sorted(new_files.items())),
            "original_methods": dict(sorted(old.items())), "current_methods": dict(sorted(new.items())),
            "tests_executed": False, "integrated_candidate_frozen": False}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
