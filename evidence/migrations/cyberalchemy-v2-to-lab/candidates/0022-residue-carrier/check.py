"""Inspect exact JSON preservation residue without performing its treatment."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, PACKAGE, load, sha, need

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
    source=read_input(resolve(record['source'])); result=read_input(resolve(record['result']))
    need(isinstance(source,dict) and isinstance(result,dict),'Source and result must be JSON objects')
    required=record['preservation_condition']['required_fields']
    need(set(required)<=set(source),'Preservation field absent from source')
    canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    observed=[]
    for field in sorted(required):
        if field not in result: observed.append({'field':field,'issue':'missing'})
        elif canonical(source[field])!=canonical(result[field]): observed.append({'field':field,'issue':'changed'})
    need(observed,'No residue under the declared preservation condition')
    declared=record['observed_remainder']
    need(len({x['field'] for x in declared})==len(declared),'Duplicate remainder field')
    need(sorted(declared,key=lambda x:x['field'])==observed,'Declared remainder differs from bound evidence')
    return {'residue_id':record['residue_id'],'remainder_verified':True,'observed_remainder':observed,'preserved_fields':sorted(set(required)-{x['field'] for x in observed}),'treatment':record['treatment'],'treatment_route':record['treatment_route'],'authority_effect':'none','treatment_executed':False,'closure_accepted':False,'semantic_preservation_proven':False,'promotion_authorized':False,'claim_ceiling':'Exact declared field-preservation remainder only; operation provenance, treatment and closure remain unproven.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py residue-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
