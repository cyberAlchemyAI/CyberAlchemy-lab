"""Inspect candidate Discipline recurrence evidence without promoting maturity."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PACKAGE, load, sha, need

def read_input(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'Duplicate JSON key: '+key); result[key]=value
        return result
    def invalid(value): raise ValueError('Invalid JSON constant: '+value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=invalid)

def resolve(ref):
    path=(LAB/ref['path']).resolve()
    need(path.is_relative_to(LAB.resolve()),'Binding escapes Lab')
    need(sha(path)==ref['sha256'],'Bound bytes changed: '+ref['path'])
    return path

def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    capabilities={x['capability_ref']:x for x in record['capabilities']}
    need(len(capabilities)==len(record['capabilities']),'Duplicate capability')
    paths=set(); identities=set()
    for capability in capabilities.values():
        path=resolve(capability['artifact']); data=read_input(path)
        need(path not in paths and data['artifact_type_id'] not in identities,'Capabilities alias the same artifact or type')
        need(data['authority_effect']=='none','Unexpected capability authority')
        paths.add(path); identities.add(data['artifact_type_id'])
    ids=set(); receipts=set(); digests=set(); covered=set(); occurrences=[]
    for occurrence in record['recurrence_evidence']:
        ident=occurrence['occurrence_id']; cap=occurrence['capability_ref']
        need(ident not in ids,'Duplicate occurrence'); ids.add(ident)
        need(cap in capabilities,'Unknown capability')
        receipt_path=resolve(occurrence['receipt']); digest=occurrence['receipt']['sha256']
        need(receipt_path not in receipts and digest not in digests,'Reused receipt is not distinct recurrence')
        receipts.add(receipt_path); digests.add(digest)
        receipt=read_input(receipt_path)
        need(receipt['schema_version'] in ['cal-schema-carrier-validation/v1','cal-method-carrier-validation/v1'],'Unsupported receipt profile')
        need(receipt['result']=='PASS' and receipt['authority_effect']=='none','Receipt did not pass without authority effects')
        checks=receipt['checks']
        need(isinstance(checks,list) and checks and all(x['result']=='PASS' for x in checks),'Receipt has missing or failed checks')
        need(len({x['check'] for x in checks})==len(checks),'Duplicate receipt check')
        materials=receipt['materials']; need(isinstance(materials,dict) and materials,'Missing receipt materials')
        base=receipt_path.parent.parent; target=resolve(capabilities[cap]['artifact']); matched=False
        for name,value in materials.items():
            local=Path(name); need(not local.is_absolute() and '..' not in local.parts,'Unsafe receipt material path')
            path=(base/local).resolve(); need(path.is_relative_to(base),'Receipt material escapes batch')
            need(sha(path)==value,'Receipt material drift: '+name)
            if path==target: matched=True
        need(matched,'Receipt does not bind capability artifact')
        covered.add(cap); occurrences.append({'occurrence_id':ident,'capability_ref':cap,'receipt':occurrence['receipt']})
    need(covered==set(capabilities),'Capability lacks recurrence evidence')
    return {'discipline_id':record['discipline_id'],'recurrence_supported':True,'evidence_scope':'Distinct local validation records and their exact materials only','capabilities_checked':len(covered),'occurrences':occurrences,'maturity_status':'candidate','promotion_authorized':False,'hardening_completed':False,'authority_effect':'none','claim_ceiling':'Recorded recurrence supports a candidate practice only; no authentication, sustained-practice proof, promotion or execution.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py discipline-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
