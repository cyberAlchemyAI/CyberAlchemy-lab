#!/usr/bin/env python3
"""Cold proof that the API40 successor retains API38's inherited test methods."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
BASE = "product/lab/release-candidates/v1/interface/"
PINS = {
    "api38": {
        "directory": BASE + "api-integration-v38-current-t06-0001",
        "source": "71f5ba4008ce1955265e949bb5250a5af6d9cc5da046d40c8fa7c6a765f774a7",
        "profile": "32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869",
    },
    "api40": {
        "directory": BASE + "api-integration-v40-current-t06-0001",
        "source": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
        "profile": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
    },
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def regular(root: Path, relative: str) -> Path:
    if relative.startswith("/") or "\\" in relative or Path(relative).as_posix() != relative:
        raise ValueError("unsafe source path")
    parts = Path(relative).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ValueError("unsafe source path")
    parent = root
    for part in parts[:-1]:
        parent /= part
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("source parent changed")
    path = parent / parts[-1]
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("source file changed")
    return path


def methods(raw: bytes, file: str) -> dict[str, str]:
    tree = ast.parse(raw.decode("utf-8"), filename=file)
    found = {}
    for cls in tree.body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for method in cls.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) or not method.name.startswith("test_"):
                continue
            identity = f"{Path(file).name}:{cls.name}.{method.name}"
            if identity in found:
                raise ValueError("duplicate test method")
            found[identity] = sha(ast.dump(method, annotate_fields=True, include_attributes=False).encode())
    return found


def scan(pin: dict) -> dict:
    directory = pin["directory"]
    source_path = directory + "/source-manifest.json"
    source_raw = regular(ROOT, source_path).read_bytes()
    if sha(source_raw) != pin["source"]:
        raise ValueError("source manifest changed")
    source = json.loads(source_raw)
    profile_binding = {"path": directory + "/contract-profile.json", "sha256": pin["profile"]}
    if source["profile_binding"] != profile_binding or sha(regular(ROOT, profile_binding["path"]).read_bytes()) != pin["profile"]:
        raise ValueError("profile binding changed")
    rows = source["files"]
    if len(rows) != 207 or len({row["path"] for row in rows}) != 207:
        raise ValueError("source row inventory changed")
    selected = {}
    for row in rows:
        raw = regular(ROOT, row["path"]).read_bytes()
        if sha(raw) != row["sha256"]:
            raise ValueError("source row bytes changed")
        if row["path"].startswith(directory + "/") and row["path"].endswith(".py"):
            for identity, digest in methods(raw, row["path"]).items():
                if identity in selected:
                    raise ValueError("duplicate selected method")
                selected[identity] = digest
    directory_path = ROOT / directory
    if {path.relative_to(ROOT).as_posix() for path in directory_path.glob("*.py")} != {
        row["path"] for row in rows if row["path"].startswith(directory + "/") and row["path"].endswith(".py")
    }:
        raise ValueError("unlisted Python source")
    if len(selected) != 345:
        raise ValueError("inherited method count changed")
    return {"source_rows_rehashed": len(rows), "methods": selected}


def verify() -> dict:
    old, new = scan(PINS["api38"]), scan(PINS["api40"])
    missing = sorted(old["methods"].keys() - new["methods"].keys())
    added = sorted(new["methods"].keys() - old["methods"].keys())
    changed = sorted(name for name in old["methods"].keys() & new["methods"].keys()
                     if old["methods"][name] != new["methods"][name])
    if missing or added or changed:
        raise ValueError("API40 inherited methods differ")
    return {"schema": "lab-t15-api40-method-equivalence/v1", "pins": PINS,
            "api38_source_rows_rehashed": old["source_rows_rehashed"],
            "api40_source_rows_rehashed": new["source_rows_rehashed"],
            "method_count_each": 345, "missing": missing, "added": added, "changed": changed,
            "inherited_methods_executed": False, "t15_complete": False}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
