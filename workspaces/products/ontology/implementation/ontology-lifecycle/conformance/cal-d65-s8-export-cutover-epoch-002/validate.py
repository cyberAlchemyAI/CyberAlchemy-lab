#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; LAB=HERE.parents[2]; MANIFEST=HERE/"manifest.json"; EVIDENCE=HERE/"product-test-evidence.json"; CANDIDATE=LAB/"ontology-lifecycle/runtime-candidates/cal-ontology-context-adapters-v2/v1"; RUNTIME=LAB/"ontology-lifecycle/runtime"; COMPILER=LAB/"ontology-lifecycle/system-ontology/cal-ontology-runtime-export-cutover-epoch-002/compiler.py"; SOURCE=LAB/"ontology-lifecycle/domainspec-source/cal-ontology-runtime-export-cutover-epoch-002/authored-source.json"; GENERATED=LAB/"ontology-lifecycle/system-ontology/cal-ontology-runtime-export-cutover-epoch-002/generated"
TEST_RE=re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(output): return sorted((m.group(1),m.group(2)) for line in output.splitlines() if (m:=TEST_RE.match(line.strip())))
def cargo(crate,target,test=None):
    cmd=["cargo","test","--locked"]+(["--test",test] if test else [])+["--","--test-threads=1"]
    return subprocess.run(cmd,cwd=crate,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={**os.environ,"CARGO_TARGET_DIR":str(target)})
def compile_to(out): return subprocess.run([sys.executable,str(COMPILER),"--source",str(SOURCE),"--output-dir",str(out)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
def main():
    manifest=load(MANIFEST); checks=[]
    def add(i,ok,d): checks.append({"check_id":i,"result":"PASS" if ok else "FAIL","detail":d})
    refs=manifest["selected_artifacts"]+manifest["protected_admitted_runtime"]; before={r["path"]:(digest(LAB/r["path"]) if (LAB/r["path"]).is_file() else None) for r in refs}; drift=[{"path":r["path"],"expected":r["sha256"],"actual":before[r["path"]]} for r in refs if before[r["path"]]!=r["sha256"]]; add("frozen-selected-bytes-current",not drift,drift)
    stage_receipts=[r for r in manifest["selected_artifacts"] if "validation" in r["role"] or r["role"]=="v2-context-map-conformance"]
    bad=[]
    for r in stage_receipts:
        value=load(LAB/r["path"])
        if value.get("result")!="PASS": bad.append({"path":r["path"],"result":value.get("result")})
        if value.get("product_approval") not in (None,"not-requested"): bad.append({"path":r["path"],"approval":value.get("product_approval")})
    add("all-stage-tests-pass",not bad,{"receipt_count":len(stage_receipts),"failures":bad})
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); ca=root/"compile-a"; cb=root/"compile-b"; ra=compile_to(ca); rb=compile_to(cb); outputs=["graph.json","system-ontology.json","source-manifest.json","compile-receipt.json"]
        add("deterministic-compile-twice",ra.returncode==0 and rb.returncode==0 and all((ca/n).read_bytes()==(cb/n).read_bytes()==(GENERATED/n).read_bytes() for n in outputs),{"a":ra.stdout.strip(),"b":rb.stdout.strip(),"outputs":outputs})
        a=cargo(CANDIDATE,root/"cargo-target","public_contract"); b=cargo(CANDIDATE,root/"cargo-target","public_contract"); an=normalized(a.stdout); bn=normalized(b.stdout); add("candidate-product-tests-twice",a.returncode==0 and b.returncode==0 and an==bn and len(an)==4 and all(x[1]=="ok" for x in an),{"run_a":an,"run_b":bn})
        p=cargo(RUNTIME,root/"cargo-target-predecessor"); pn=normalized(p.stdout); add("frozen-predecessor-compatible",p.returncode==0 and len(pn)==22 and all(x[1]=="ok" for x in pn),{"tests":len(pn),"exit":p.returncode})
        probes=[]
        cases=[("v1-map-substitution","cal.context-map.governance-ontology-lifecycle/v2","cal.context-map.governance-ontology-lifecycle/v1"),("reverse-direction","source-to-target","target-to-source"),("projection-source-escalation","canonical_replay_source: false","canonical_replay_source: true"),("public-module-removal","pub mod governance_v2","mod governance_v2")]
        for pid,old,new in cases:
            crate=root/pid; shutil.copytree(CANDIDATE,crate,ignore=shutil.ignore_patterns("target","receipts","validate.py")); cargo_file=crate/"Cargo.toml"; cargo_file.write_text(cargo_file.read_text().replace('path = "../../../runtime"',f'path = "{RUNTIME}"'),encoding="utf-8"); source=crate/"src/lib.rs"; body=source.read_text();
            if body.count(old)<1: probes.append({"probe_id":pid,"result":"FAIL","detail":"anchor-missing"}); continue
            source.write_text(body.replace(old,new,1),encoding="utf-8"); rr=cargo(crate,root/"mutation-target","public_contract"); probes.append({"probe_id":pid,"result":"PASS" if rr.returncode!=0 else "FAIL","normalized_tests":normalized(rr.stdout)})
    after={r["path"]:(digest(LAB/r["path"]) if (LAB/r["path"]).is_file() else None) for r in refs}; changed=[p for p in before if before[p]!=after[p]]; add("selected-source-immutability",not changed,changed)
    add("approval-and-authority-boundary",manifest.get("product_approval")=="not-requested" and manifest.get("cutover_authorized") is False and manifest.get("cutover_performed") is False and manifest.get("authority_effect")=="none",{"approval":manifest.get("product_approval"),"cutover":manifest.get("cutover_authorized"),"authority":manifest.get("authority_effect")})
    passed=all(x["result"]=="PASS" for x in checks+probes); manifest_digest=digest(MANIFEST)
    evidence={"schema_version":"cal.product-test-evidence/v2","product_candidate_id":manifest["product_candidate_id"],"stage_id":"D65-S8","manifest_path":str(MANIFEST.relative_to(LAB)),"manifest_sha256":manifest_digest,"result":"PASS" if passed else "FAIL","checks":checks,"mutation_tournament":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"mutation_probes_passed":sum(x["result"]=="PASS" for x in probes),"mutation_probes_total":len(probes),"stage_state":"TESTED_PRODUCT" if passed else "PRODUCT_TEST_FAILED","product_candidate_frozen":passed,"product_approval_eligible":passed,"product_approval":"not-requested","next_owner_gate":"G-D65-EPOCH-002-PRODUCT-APPROVAL" if passed else None,"implementation_admitted":False,"cutover_authorized":False,"cutover_performed":False,"authority_effect":"none","claim_ceiling":manifest["claim_ceiling"]}
    EVIDENCE.write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:evidence[k] for k in ("stage_id","result","checks_passed","checks_total","mutation_probes_passed","mutation_probes_total","stage_state","product_candidate_frozen","product_approval_eligible","product_approval","next_owner_gate","cutover_authorized","authority_effect")},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
