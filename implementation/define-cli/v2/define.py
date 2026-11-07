#!/usr/bin/env python3
"""Isolated entrypoint: Python -I ignores caller module search paths."""
from pathlib import Path
import hashlib
import json
import sys

package = Path(__file__).resolve().parent
repo = package.parents[2]
try:
    # Validate before putting local modules on the import path or importing dependencies.
    manifest = json.loads((package / "runtime-manifest.json").read_bytes())
    rows = manifest["files"]
    canonical = (json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    if hashlib.sha256(canonical).hexdigest() != manifest["inventory_sha256"]:raise ValueError("inventory")
    for row in rows:
        path = repo / row["path"]
        if path.resolve() != path or not path.is_relative_to(repo):raise ValueError("path")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["sha256"] or len(raw) != row["bytes"]:raise ValueError("drift")
    selected = {row["path"] for row in rows}
    for path in package.rglob("*"):
        if path.is_file() and path.suffix in (".py", ".so", ".pyd") and "__pycache__" not in path.parts:
            if str(path.relative_to(repo)) not in selected:raise ValueError("unselected import")
except (OSError, ValueError, KeyError, TypeError):
    print(json.dumps({"schema_version": "cal.define.result/v2", "outcome": "blocked", "diagnostics": [{"code": "runtime-source-drift", "message": "Runtime integrity refused before local imports; maintainer review required."}], "authority_effect": "none"}))
    raise SystemExit(3)

# Compile the same verified source buffers, bypassing unselected bytecode caches.
from importlib.machinery import SourceFileLoader
_original_get_code = SourceFileLoader.get_code
_selected_python = {str(repo / row["path"]): row["sha256"] for row in rows if row["path"].endswith(".py")}
def _pinned_code(loader, fullname):
    filename = str(Path(loader.path).absolute())
    if filename in _selected_python:
        raw = Path(filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != _selected_python[filename]:
            raise ImportError("Define selected source changed before import")
        return compile(raw, filename, "exec", dont_inherit=True)
    return _original_get_code(loader, fullname)
SourceFileLoader.get_code = _pinned_code

sys.path.insert(0, str(package))
from define_runtime.cli import main
raise SystemExit(main())
