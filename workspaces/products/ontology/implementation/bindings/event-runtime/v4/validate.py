#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def need(ok,msg):
    if not ok:raise ValueError(msg)
def run(cmd):
    start=time.perf_counter()
    p=subprocess.run(cmd,cwd=LAB,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"),capture_output=True,text=True,timeout=420)
    need(p.returncode==0,p.stdout+p.stderr)
    return p.stdout,time.perf_counter()-start
def tree(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob("*") if f.is_file()}
def validate():
    c=load(ROOT/"candidate.json")
    need(c["status"]=="test-candidate" and c["authority_effect"]=="none","candidate authority mismatch")
    for r in c["acceptance_material"]:need(sha(LAB/r["path"])==r["sha256"],"acceptance drift: "+r["path"])
    old=LAB/".local/ontology-event-runtime-0049";v3=LAB/".local/ontology-source-importer-v3-prototype"
    before=(tree(old),tree(v3))
    for ref in c["preserved_material"]:need(sha(LAB/ref["path"])==ref["sha256"],"predecessor drift")
    manifest=load(ROOT/"source-manifest.json")
    # Build before measurement: benchmark the optimized CLI, not compilation or Cargo locks.
    run(["cargo","build","--release","--offline","--locked","--manifest-path",str(ROOT/"Cargo.toml")])
    prefix=[str(ROOT/"target/release/cal-ontology-source-runtime")]
    run(["cargo","fmt","--manifest-path",str(ROOT/"Cargo.toml"),"--","--check"])
    tests,_=run(["cargo","test","--offline","--locked","--manifest-path",str(ROOT/"Cargo.toml")])
    need("23 passed; 0 failed" in tests,"focused tests missing")
    expected={};docs={};counts={"nodes":0,"relations":0}
    for p in manifest["packages"]:
        for kind in ("nodes","relations"):
            registry=p[kind];s=registry["source"];path=Path(manifest["roots"][s["root"]])/s["path"]
            need(sha(path)==s["sha256"],"source digest drift")
            rows=load(path)[registry["selector"].lstrip("/")]
            counts[kind]+=len(rows)
            for i,row in enumerate(rows):expected[(p["package_key"],s["path"],registry["selector"]+"/"+str(i))]=row
        for s in p["documents"]:
            path=Path(manifest["roots"][s["root"]])/s["path"]
            need(sha(path)==s["sha256"],"document drift")
            docs[(p["package_key"],s["path"])]=path.read_bytes()
    durations={}
    with tempfile.TemporaryDirectory(prefix="cal-v4-product-") as tmp:
        a=Path(tmp)/"a";b=Path(tmp)/"b"
        x,durations["import_seconds"]=run(prefix+["import",str(ROOT/"source-manifest.json"),str(a)])
        y,durations["second_import_seconds"]=run(prefix+["import",str(ROOT/"source-manifest.json"),str(b)])
        need(json.loads(x)==json.loads(y) and tree(a)==tree(b),"determinism failed")
        initial=tree(a)
        z,durations["replay_seconds"]=run(prefix+["observe",str(a)])
        need(json.loads(z)["source_event_set_digest"]==json.loads(x)["source_event_set_digest"],"restart mismatch")
        out,_=run(prefix+["export",str(a)]);out=json.loads(out)
        actual={};documents={}
        for row in out["records"]:
            ref=row["source_binding"];record=row["source_record"]
            if row["identity"]["type_ref"]=="source-document":
                key=(ref["package_key"],ref["path"])
                need(key not in documents,"duplicate document export")
                documents[key]=record["content"].encode("utf-8")
                need(hashlib.sha256(documents[key]).hexdigest()==record["content_sha256"],"document hash mismatch")
            else:
                key=(ref["package_key"],ref["path"],ref["selector"])
                need(key not in actual,"duplicate record export")
                actual[key]=record
        need(expected==actual and docs==documents,"lossless source/document round trip failed")
        bridge=next(p for p in manifest["packages"] if p["profile"]["path"]=="define/profile.json")
        durations["scoped_query_seconds"]=[]
        for _ in range(3):
            query,t=run(prefix+["observe",str(a),bridge["package_key"]])
            durations["scoped_query_seconds"].append(t)
            q=json.loads(query)
            own=sum(k[0]==bridge["package_key"] and "/nodes/" in k[2] for k in expected)+sum(k[0]==bridge["package_key"] for k in docs)
            need(q["context_nodes"]>own,"cross-package endpoint closure absent")
        need(tree(a)==initial,"read commands mutated store")
        for operation in ("create","update"):
            run(prefix+["apply",str(a),str(ROOT/"commands"/(operation+".json"))])
        changed=tree(a)
        stale=subprocess.run(prefix+["apply",str(a),str(ROOT/"commands/update.json")],cwd=LAB,capture_output=True,text=True)
        need(stale.returncode!=0 and "expected version mismatch" in stale.stderr and tree(a)==changed,"stale write not safely rejected")
        exported=json.loads(run(prefix+["export",str(a)])[0])
        need(any(r["source_record"].get("label")=="Updated through a canonical event" for r in exported["records"]),"update not replayed")
        run(prefix+["apply",str(a),str(ROOT/"commands/retire.json")])
        # Recovery of one deliberately simulated uncommitted residue, never a committed frame.
        head=load(a/"HEAD.json")["digest"]
        with (a/"PENDING.json").open("x") as f:f.write("simulated incomplete transaction")
        recovered=json.loads(run(prefix+["recover",str(a),head])[0])
        need(recovered["removed_uncommitted_files"]==["PENDING.json"],"recovery scope mismatch")
        run(prefix+["summary",str(a)])
    need(durations["import_seconds"]<=120 and durations["second_import_seconds"]<=120,"import timing bound: "+json.dumps(durations))
    need(durations["replay_seconds"]<=30 and max(durations["scoped_query_seconds"])<=30,"query timing bound: "+json.dumps(durations))
    need(before==(tree(old),tree(v3)),"prior instances changed")
    return {"schema_version":"cal-source-runtime-product-test/v1","result":"PASS","candidate_sha256":sha(ROOT/"candidate.json"),
      "focused_tests":23,"packages":len(manifest["packages"]),"nodes":counts["nodes"],"relations":counts["relations"],
      "documents":len(docs),"lossless_records_and_documents":True,"deterministic_transactions":True,
      "restart":True,"cross_package_context":True,"create_update_retire":True,"stale_version_rejection":True,
      "recovery":True,"prior_instances_unchanged":True,"timings":durations,"benchmark_build":"release; compiled before timing",
      "authority_effect":"none","product_approval_granted":False}
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--write-receipt",action="store_true");args=ap.parse_args()
    try:
        result=validate();encoded=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.write_receipt:
            path=ROOT/"receipts/product-test.json";path.parent.mkdir(exist_ok=True)
            need(not path.exists(),"preserve previous measured receipt; run without --write-receipt")
            with path.open("x") as f:f.write(encoded)
        print(encoded,end="")
    except Exception as exc:
        print(json.dumps({"result":"BLOCK","error":str(exc),"authority_effect":"none"}));raise SystemExit(1)
