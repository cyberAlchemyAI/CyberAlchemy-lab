#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent; LAB=HERE.parents[3]; RUNTIME=LAB/"ontology-lifecycle/runtime"; BINDING=LAB/"ontology-lifecycle/conformance/implementation-binding/cal-ontology-runtime-export-cutover-epoch-002/binding.json"; BINDING_RECEIPT=BINDING.parent/"receipts/validation.json"; RECEIPT=HERE/"receipts/validation.json"
TEST_RE=re.compile(r"^test ([^ ]+) \.\.\. (ok|FAILED|ignored)$")
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def env(target): return {**os.environ,"CARGO_TARGET_DIR":str(target)}
def run(crate,target,test=None):
    cmd=["cargo","test","--locked"]
    if test: cmd += ["--test",test]
    cmd += ["--","--test-threads=1"]
    return subprocess.run(cmd,cwd=crate,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env(target))
def normalized(output): return sorted((m.group(1),m.group(2)) for line in output.splitlines() if (m:=TEST_RE.match(line.strip())))
def main():
    binding=load(BINDING); checks=[]
    def add(i,ok,d): checks.append({"check_id":i,"result":"PASS" if ok else "FAIL","detail":d})
    add("binding-predecessor-current",digest(BINDING)=="2e891f1d804139014811fe7135c9b6df26269dc92699c77073c6c1421a0b4150" and digest(BINDING_RECEIPT)=="3e43bf8354cf0ac046f50214218f7b89e62d5186849a497f1b8202c3ca3992b3" and load(BINDING_RECEIPT).get("result")=="PASS",{"binding":digest(BINDING),"receipt":digest(BINDING_RECEIPT)})
    drift=[]
    for ref in binding["protected_admitted_runtime"]:
        p=LAB/ref["path"]; actual=digest(p) if p.is_file() else None
        if actual!=ref["sha256"]: drift.append({"path":ref["path"],"actual":actual})
    add("admitted-runtime-unchanged",not drift,drift)
    expected_files=set(binding["candidate_crate"]["files"]); actual_files={"Cargo.toml","Cargo.lock","src/lib.rs","tests/public_contract.rs"}; add("bound-candidate-files-present",expected_files==actual_files and all((HERE/p).is_file() for p in actual_files),sorted(expected_files))
    text=(HERE/"src/lib.rs").read_text(encoding="utf-8")
    required=["pub const V2_CONTEXT_MAP","pub mod governance_v2","pub struct GovernanceContextAdapterV2","pub fn project_governance_context_v2","pub mod ontology_lifecycle_v2","pub struct OntologyLifecycleContextAdapterV2","pub fn project_ontology_lifecycle_context_v2"]
    add("public-symbol-postimages",all(x in text for x in required),required)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); a=run(HERE,root/"target-a","public_contract"); b=run(HERE,root/"target-b","public_contract"); an=normalized(a.stdout); bn=normalized(b.stdout)
        expected_tests={"both_contexts_share_the_exact_event_cut","exact_v2_topology_is_public_and_enforced","projection_has_no_authority_effect","projection_is_not_a_replay_source"}
        add("candidate-suite-twice",a.returncode==0 and b.returncode==0 and an==bn and {x[0] for x in an}==expected_tests,{"run_a":an,"run_b":bn})
        predecessor=run(RUNTIME,root/"target-predecessor"); pn=normalized(predecessor.stdout); add("admitted-predecessor-suite",predecessor.returncode==0 and len(pn)==22 and all(x[1]=="ok" for x in pn),{"tests":len(pn),"exit":predecessor.returncode})
        probes=[]
        cases=[("v1-map-substitution","cal.context-map.governance-ontology-lifecycle/v2","cal.context-map.governance-ontology-lifecycle/v1"),("reverse-direction","source-to-target","target-to-source"),("projection-source-escalation","canonical_replay_source: false","canonical_replay_source: true")]
        for pid,old,new in cases:
            crate=root/pid; shutil.copytree(HERE,crate,ignore=shutil.ignore_patterns("target","receipts","validate.py")); cargo=crate/"Cargo.toml"; cargo.write_text(cargo.read_text().replace('path = "../../../runtime"',f'path = "{RUNTIME}"'),encoding="utf-8"); source=crate/"src/lib.rs"; body=source.read_text();
            if body.count(old)<1: probes.append({"probe_id":pid,"result":"FAIL","detail":"anchor-missing"}); continue
            source.write_text(body.replace(old,new,1),encoding="utf-8"); rr=run(crate,root/f"target-{pid}","public_contract"); probes.append({"probe_id":pid,"result":"PASS" if rr.returncode!=0 else "FAIL","tests":normalized(rr.stdout)})
    passed=all(x["result"]=="PASS" for x in checks+probes)
    artifacts={p:{"path":str((HERE/p).relative_to(LAB)),"sha256":digest(HERE/p)} for p in sorted(actual_files)}
    receipt={"schema_version":"cal.d65-s7-implementation-validation/v2","stage_id":"D65-S7","result":"PASS" if passed else "FAIL","checks":checks,"hostile_probes":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"hostile_probes_passed":sum(x["result"]=="PASS" for x in probes),"hostile_probes_total":len(probes),"artifacts":artifacts,"stage_state":"TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED","next_product_frontier":"D65-S8" if passed else "D65-S7","product_approval":"not-requested","implementation_admitted":False,"cutover_authorized":False,"authority_effect":"none","claim_ceiling":"PASS proves the isolated D65-S7 implementation prototype and its public v2 adapter tests only; it does not admit or cut over the candidate."}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("stage_id","result","checks_passed","checks_total","hostile_probes_passed","hostile_probes_total","next_product_frontier","product_approval","implementation_admitted","cutover_authorized","authority_effect")},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
