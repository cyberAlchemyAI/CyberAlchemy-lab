#!/usr/bin/env python3
"""Explicit maintainer packaging step after source review; never runs on CLI use."""
from pathlib import Path
import hashlib
import json
import sys

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main():
    sys.path.insert(0, str(PACKAGE))
    from define_runtime.contracts import SCHEMAS
    (PACKAGE / "schemas").mkdir(exist_ok=True)
    for name, schema in SCHEMAS.items():
        (PACKAGE / "schemas" / (name + ".schema.json")).write_bytes(encoded({"$schema": "https://json-schema.org/draft/2020-12/schema", **schema}))
    selected = [p for p in PACKAGE.rglob("*") if p.is_file() and p.name != "runtime-manifest.json" and "__pycache__" not in p.parts and "evidence" not in p.parts]
    selected += [REPO / "define/define-v2", REPO / "authority/artifact-types/definition/v2/schema.json", REPO / "authority/artifact-types/definition/v2/generator.py"]
    rows = [{"path": str(p.relative_to(REPO)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in sorted(selected)]
    value = {"schema_version": "cal.define.runtime-manifest/v2", "version": "0.2.0-rc.1", "files": rows,
             "inventory_sha256": hashlib.sha256(encoded(rows)).hexdigest(), "authority_effect": "none", "standing": "candidate; not runtime adoption or release approval"}
    (PACKAGE / "runtime-manifest.json").write_bytes(encoded(value))
    print(json.dumps({"sealed_files": len(rows), "inventory_sha256": value["inventory_sha256"], "authority_effect": "none"}))


if __name__ == "__main__":main()
