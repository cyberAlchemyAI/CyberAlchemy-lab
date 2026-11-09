#!/usr/bin/env python3
"""Reproduce the frozen successor Product tests without changing reviewed receipts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return json.loads(p.read_text())
def require(ok, message):
    if not ok:
        raise ValueError(message)
def run(argv):
    p = subprocess.run(argv, cwd=LAB, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                       capture_output=True, text=True, timeout=420)
    require(p.returncode == 0, p.stdout + p.stderr)
    return p.stdout
def tree(root):
    return {str(p.relative_to(root)):sha(p) for p in root.rglob("*") if p.is_file()}
def validate():
    candidate = load(ROOT/"candidate.json")
    require(candidate["status"]=="test-candidate" and candidate["authority_effect"]=="none", "Candidate authority mismatch")
    for ref in candidate["acceptance_material"]:
        require(sha(LAB/ref["path"])==ref["sha256"], "Acceptance drift: "+ref["path"])
    provenance=load(ROOT/"kernel-provenance.json")
    require(sha(LAB/provenance["base"]["path"])==provenance["base"]["sha256"], "Base kernel changed")
    active=LAB/".local/ontology-event-runtime-0049"
    active_before=tree(active)
    manifest=load(ROOT/"source-manifest.json")
    argv=["cargo","run","--offline","--locked","--quiet","--manifest-path",str(ROOT/"Cargo.toml"),"--"]
    run(["cargo","fmt","--manifest-path",str(ROOT/"Cargo.toml"),"--","--check"])
    tests=run(["cargo","test","--offline","--locked","--manifest-path",str(ROOT/"Cargo.toml")])
    require("16 passed; 0 failed" in tests,"Required Rust test set did not pass")
    expected={}
    counts={"nodes":0,"relations":0}
    for package in manifest["packages"]:
        for kind in ("nodes","relations"):
            registry=package[kind]
            source=registry["source"]
            path=Path(manifest["roots"][source["root"]])/source["path"]
            require(sha(path)==source["sha256"],"Source changed: "+str(path))
            rows=load(path)[registry["selector"].lstrip("/")]
            counts[kind]+=len(rows)
            for index,row in enumerate(rows):
                key=(package["package_key"],source["path"],registry["selector"]+"/"+str(index))
                require(key not in expected,"Duplicate expected source record")
                expected[key]=row
    with tempfile.TemporaryDirectory(prefix="cal-v3-product-") as temporary:
        first=Path(temporary)/"first"; second=Path(temporary)/"second"
        a=json.loads(run(argv+["import",str(ROOT/"source-manifest.json"),str(first)]))
        before=tree(first)
        b=json.loads(run(argv+["import",str(ROOT/"source-manifest.json"),str(second)]))
        require(a==b and before==tree(second),"Independent imports differ")
        require(a==json.loads(run(argv+["observe",str(first)])),"Restart differs")
        exported=json.loads(run(argv+["export",str(first)]))
        actual={}
        for row in exported["records"]:
            ref=row["source_binding"]; key=(ref["package_key"],ref["path"],ref["selector"])
            require(key not in actual,"Duplicate exported source")
            actual[key]=row["source_record"]
        require(expected==actual,"Lossless record round trip failed")
        for package in manifest["packages"]:
            subset=json.loads(run(argv+["export",str(first),package["package_key"]]))
            require(len(subset["records"])==sum(k[0]==package["package_key"] for k in expected),"Package selection lost records")
        require(tree(first)==before,"Read commands changed event files")
    require(tree(active)==active_before,"Active v2 instance changed")
    return {"schema_version":"cal-source-import-product-test/v1","result":"PASS",
            "candidate_sha256":sha(ROOT/"candidate.json"),"rust_tests":16,
            "supported_packages":len(manifest["packages"]),"unsupported_packages":manifest["unsupported"],
            "source_records":len(expected),"nodes":counts["nodes"],"relations":counts["relations"],
            "lossless_record_round_trip":True,"independent_event_trees_equal":True,
            "restart_equal":True,"read_commands_nonmutating":True,"active_v2_unchanged":True,
            "authority_effect":"none","product_approval_granted":False}
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--write-receipt",action="store_true")
    args=parser.parse_args()
    try:
        result=validate()
        encoded=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.write_receipt:
            path=ROOT/"receipts/product-test.json";path.parent.mkdir(exist_ok=True)
            if path.exists():
                require(path.read_text()==encoded,"Frozen receipt differs; create a successor")
            else:
                with path.open("x") as f:f.write(encoded)
        print(encoded,end="")
    except Exception as e:
        print(json.dumps({"result":"BLOCK","error":str(e),"authority_effect":"none"}))
        raise SystemExit(1)
