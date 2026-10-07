#!/usr/bin/env python3
"""Validate the complete materialized Step 5 postimage."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
def load(path:Path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path:Path,value)->None: path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def main()->int:
    subprocess.run([sys.executable,str(ROOT/"build.py")],check=True)
    candidate=load(ROOT/"candidate.json");registry=load(ROOT/"registry.json");endpoints=load(ROOT/"endpoint-inventory.json")
    base=load(LAB/candidate["inputs"]["predecessor_registry"]);schema=load(LAB/candidate["inputs"]["registry_schema"]);model=load(LAB/candidate["inputs"]["relation_model"]);definitions=load(LAB/"authority/definitions/registry.json")
    checks=[]
    def check(cid,ok,detail): checks.append({"check_id":cid,"result":"PASS" if ok else "BLOCK","detail":detail})
    errors=[error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(registry)]
    check("registry-v2-schema",not errors,errors)
    check("admitted-state-preserved",registry["admitted_contracts"]==base["admitted_contracts"] and registry["current_by_identity"]==base["current_by_identity"] and registry["overlay_sources"]==base["overlay_sources"] and registry["duplicate_resolutions"]==base["duplicate_resolutions"],{"contracts":len(registry["admitted_contracts"]),"current_mappings":len(registry["current_by_identity"])})
    expected_inventory={"admitted_contract_count":34,"admitted_current_count":29,"admitted_historical_count":5,"descriptor_count":90,"descriptor_declared_ref_count":83,"descriptor_identity_count":68,"descriptor_resolved_ref_count":85,"duplicate_resolution_count":2,"semantic_binding_counts":{"admitted-successor-required":1,"candidate-rebind-required":0,"current-as-declared":89},"state_counts":{"admitted-current":22,"admitted-historical":5,"candidate-unadmitted":61,"resolved-duplicate":2}}
    check("exact-step5-cardinality",registry["inventory"]==expected_inventory,registry["inventory"])
    descriptor_results=[]
    for row in registry["descriptors"]:
        descriptor_results.append({"ref":row["artifact_type_ref"],"descriptor":sha(LAB/row["descriptor_path"])==row["descriptor_sha256"],"schema":sha(LAB/row["schema_path"])==row["schema_sha256"]})
    check("all-descriptor-and-schema-digests-current",all(row["descriptor"] and row["schema"] for row in descriptor_results),descriptor_results)
    hard=load(LAB/candidate["inputs"]["hard_corrections"]);endpoint_manifest=load(LAB/candidate["inputs"]["endpoint_carriers"]);legacy=load(LAB/candidate["inputs"]["legacy_successors"]);meta=load(LAB/candidate["inputs"]["metamodel_successors"]);relation_hardening=load(LAB/candidate["inputs"]["relation_carrier_hardening"])
    step5_paths={row["artifact_path"] for row in hard["postimages"]}|{row["artifact_path"] for row in endpoint_manifest["entries"]}|{row["artifact_path"] for row in legacy["entries"]}|{row["artifact_path"] for row in meta["entries"]}|{row["artifact_path"] for row in relation_hardening["entries"]}
    candidate_rows=[row for row in registry["descriptors"] if row["descriptor_path"] in step5_paths]
    receipt_results=[]
    for row in candidate_rows:
        receipt=LAB/Path(row["descriptor_path"]).parent/"receipts/validation.json"
        data=load(receipt) if receipt.exists() else {}
        receipt_results.append({"ref":row["artifact_type_ref"],"exists":receipt.exists(),"pass":data.get("result")=="PASS"})
    check("all-38-reviewed-carrier-receipts-pass",len(receipt_results)==38 and all(row["exists"] and row["pass"] for row in receipt_results),receipt_results)
    binding_results=[]
    for row in candidate_rows:
        for ref in row["semantic_definition_refs"]:
            did=ref.split("@",1)[0];binding_results.append({"artifact_type_ref":row["artifact_type_ref"],"definition_ref":ref,"current":definitions["current_lookup"].get(did)==ref})
    check("all-step5-definitions-current",all(row["current"] for row in binding_results),binding_results)
    check("endpoint-carrier-closure",endpoints["counts"]=={"admitted-current":13,"candidate-materialized":37,"declared_endpoint_pairs":147,"named_endpoint_kinds":50,"referenced-no-canonical-carrier":0,"wildcard_tokens":0},endpoints["counts"])
    model_pairs=sum(len(row["allowed_endpoint_pairs"]) for row in model["entries"])
    check("relation-model-unchanged",len(model["entries"])==23 and model_pairs==147 and endpoints["counts"]["wildcard_tokens"]==0,{"axes":len(model["entries"]),"pairs":model_pairs})
    check("nine-successor-lineages",sum(row["posture"]=="candidate-successor-unadmitted" for row in registry["candidate_lineage"])==9,registry["candidate_lineage"])
    check("candidate-no-authority-effect",candidate["authority_effect"]==registry["authority_effect"]=="none" and candidate["status"]=="candidate-owner-review-open",{"candidate":candidate["status"],"registry":registry["status"]})
    before=[(ROOT/name).read_bytes() for name in ["registry.json","endpoint-inventory.json","REGISTRY.md"]];subprocess.run([sys.executable,str(ROOT/"build.py")],check=True);after=[(ROOT/name).read_bytes() for name in ["registry.json","endpoint-inventory.json","REGISTRY.md"]]
    check("deterministic-derived-surfaces",before==after,{"registry_sha256":sha(ROOT/"registry.json"),"endpoint_inventory_sha256":sha(ROOT/"endpoint-inventory.json"),"projection_sha256":sha(ROOT/"REGISTRY.md")})
    result="PASS" if all(row["result"]=="PASS" for row in checks) else "BLOCK"
    receipt={"schema_version":"cyberalchemy-lab-step5-postimage-validation/v1","candidate_id":candidate["candidate_id"],"result":result,"authority_effect":"none","checks":checks,"materials":{"registry_sha256":sha(ROOT/"registry.json"),"endpoint_inventory_sha256":sha(ROOT/"endpoint-inventory.json")},"claim_ceiling":"PASS proves the complete materialized Step 5 candidate postimage, exact preserved admitted state, current bytes, passing candidate receipts, current Definition bindings, and zero missing materialized endpoint carriers. It does not admit candidates or relations, transition predecessors, or activate consumers."}
    dump(ROOT/"receipts/validation.json",receipt)
    audit={"schema_version":"cyberalchemy-lab-step5-closure-audit/v1","audit_id":"CAL-ARTIFACT-TYPE-STEP5-CLOSURE-AUDIT-0001","result":result,"authority_effect":"none","counts":{"revised_candidates":5,"immutable_successors":9,"new_endpoint_carrier_identities":22,"pre_admission_relation_carrier_hardenings":2,"total_reviewed_postimages":38,"visible_descriptors":90,"passing_candidate_receipts":sum(row["pass"] for row in receipt_results),"named_endpoint_kinds":50,"missing_materialized_endpoint_carriers":endpoints["counts"]["referenced-no-canonical-carrier"]},"admission_readiness":"exact-postimages-ready-for-owner-review" if result=="PASS" else "blocked","required_next_effect":"One exact collective Artifact Type admission decision may admit the reviewed Step 5 postimages and transition only their named admitted predecessors.","claim_ceiling":receipt["claim_ceiling"]}
    dump(ROOT/"closure-audit.json",audit)
    print(json.dumps({"result":result,"checks":len(checks),"registry_sha256":receipt["materials"]["registry_sha256"],"endpoint_inventory_sha256":receipt["materials"]["endpoint_inventory_sha256"]},sort_keys=True));return 0 if result=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
