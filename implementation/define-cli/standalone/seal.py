#!/usr/bin/env python3
"""Explicit maintainer packaging. Never regenerate integrity pins on API use."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()


def main():
    sys.path.insert(0,str(ROOT))
    from define_core.contracts import SCHEMAS
    package=ROOT/"define_core"
    (package/"schemas").mkdir(exist_ok=True)
    for name,schema in SCHEMAS.items():
        (package/"schemas"/(name+".schema.json")).write_bytes(encode({"$schema":"https://json-schema.org/draft/2020-12/schema",**schema}))
    selected=sorted(p for p in package.rglob("*") if p.is_file() and p.name!="runtime-manifest.json" and "__pycache__" not in p.parts)
    rows=[{"path":p.relative_to(package).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in selected]
    value={"schema_version":"define.portable-runtime-manifest/v1","version":"0.3.0rc2","files":rows,
           "inventory_sha256":hashlib.sha256(encode(rows)).hexdigest(),"claim_ceiling":"Local package consistency; not release authenticity or approval.","authority_effect":"none"}
    (package/"runtime-manifest.json").write_bytes(encode(value))
    print(json.dumps({"sealed_files":len(rows),"inventory_sha256":value["inventory_sha256"],"authority_effect":"none"}))


if __name__=="__main__":main()
