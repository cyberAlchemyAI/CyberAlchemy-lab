#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent; LAB=HERE.parents[2]; SOURCE=HERE.parents[1]/"domainspec-source/cal-ontology-runtime-export-cutover-epoch-002/authored-source.json"; SOURCE_RECEIPT=SOURCE.parent/"receipts/validation.json"; GENERATED=HERE/"generated"; RECEIPT=HERE/"receipts/validation.json"; SCHEMA=HERE/"system-ontology.schema.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(source,out): return subprocess.run([sys.executable,str(HERE/"compiler.py"),"--source",str(source),"--output-dir",str(out)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
def main():
    checks=[]
    def add(i,ok,d): checks.append({"check_id":i,"result":"PASS" if ok else "FAIL","detail":d})
    source_receipt=load(SOURCE_RECEIPT); add("d65-s4-predecessor-pass",source_receipt.get("result")=="PASS" and source_receipt.get("stage_state")=="TESTED_PROTOTYPE",source_receipt.get("result"))
    expected={"authored-source":"798b6c5ff5affe6b2597010cedf1f2bfa43f068c1989cd4a599c2536298d4afe","source-receipt":"bc6a9f05062281b4d1dafea4e2e861aaae17b49d9069df699b33e31375a650e1"}; actual={"authored-source":digest(SOURCE),"source-receipt":digest(SOURCE_RECEIPT)}; add("selected-source-current",actual==expected,{"expected":expected,"actual":actual})
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); a=root/"a"; b=root/"b"; ra=run(SOURCE,a); rb=run(SOURCE,b)
        names=["graph.json","system-ontology.json","source-manifest.json","compile-receipt.json"]
        add("compile-twice-success",ra.returncode==0 and rb.returncode==0,{"a":ra.stdout,"b":rb.stdout})
        equal=all((a/n).read_bytes()==(b/n).read_bytes() for n in names); add("compile-byte-equality",equal,names)
        current=all((GENERATED/n).is_file() and (GENERATED/n).read_bytes()==(a/n).read_bytes() for n in names); add("materialized-output-current",current,names)
        system=load(a/"system-ontology.json"); errors=sorted(e.message for e in Draft202012Validator(load(SCHEMA)).iter_errors(system)); add("system-ontology-schema-valid",not errors,errors)
        graph=load(a/"graph.json"); add("compiled-graph-closed",len(graph.get("nodes",[]))==22 and len(graph.get("edges",[]))==16 and graph.get("canonical_replay_source") is False,{"nodes":len(graph.get("nodes",[])),"edges":len(graph.get("edges",[]))})
        source=load(SOURCE); probes=[]
        cases=[("reverse-direction",lambda x:x["context_map"].update(direction="target-to-source")),("missing-event",lambda x:x["events"].pop()),("projection-as-source",lambda x:x["projections"][0].update(canonical_replay_source=True))]
        for pid,mut in cases:
            h=copy.deepcopy(source); mut(h); hp=root/f"{pid}.json"; hp.write_text(json.dumps(h,sort_keys=True)+"\n",encoding="utf-8"); rr=run(hp,root/f"out-{pid}"); probes.append({"probe_id":pid,"result":"PASS" if rr.returncode!=0 else "FAIL","compiler_output":rr.stdout.strip()})
    passed=all(x["result"]=="PASS" for x in checks+probes)
    artifacts={n:{"path":str((GENERATED/n).relative_to(LAB)),"sha256":digest(GENERATED/n)} for n in ["graph.json","system-ontology.json","source-manifest.json","compile-receipt.json"]}
    receipt={"schema_version":"cal.d65-s5-compile-validation/v2","stage_id":"D65-S5","result":"PASS" if passed else "FAIL","checks":checks,"hostile_probes":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"hostile_probes_passed":sum(x["result"]=="PASS" for x in probes),"hostile_probes_total":len(probes),"artifacts":artifacts,"stage_state":"TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED","next_product_frontier":"D65-S6" if passed else "D65-S5","product_approval":"not-requested","authority_effect":"none","claim_ceiling":"PASS proves deterministic compilation and system-ontology prototype closure only; it grants no product approval or authority."}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("stage_id","result","checks_passed","checks_total","hostile_probes_passed","hostile_probes_total","next_product_frontier","product_approval","authority_effect")},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
