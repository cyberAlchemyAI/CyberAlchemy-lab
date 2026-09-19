"""Inspect preserved withdrawal reservations without retiring or allocating identifiers."""
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

def assess(record_path,allocation):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in load(ROOT/'contracts.json')['schemas']+load(ROOT/'dependencies.json')['inputs']: resolve(ref)
    record=read_input(record_path)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    Draft202012Validator(load(PACKAGE/'allocation.schema.json')).validate(allocation)
    need(resolve(allocation['withdrawal_record'])==record_path.resolve(),'Allocation binds another withdrawal record')
    normalization_path=resolve(record['normalization'])
    need(normalization_path==LAB/'docs/normalizations/0001-definition-migration-model/normalization.json','Unsupported normalization')
    expected={x['legacy_id']:x['successor_id'] for x in read_input(normalization_path)['withdrawn_ids']}
    actual={x['retired_id']:x['successor_id'] for x in record['reservations']}
    need(len(actual)==len(record['reservations']),'Duplicate retired identifier')
    need(actual==expected,'Reservations or successors differ from accepted normalization')
    need(not set(actual)&set(actual.values()),'Successor is also retired')
    # Keep identity matching exact; reject spelling padding instead of silently normalizing it.
    need(all(x==x.strip() for x in allocation['proposed_ids']),'Identifier contains surrounding whitespace')
    collisions=sorted(set(allocation['proposed_ids'])&set(actual))
    outcome='not-applicable' if allocation['scope_ref']!=record['scope_ref'] else 'blocked-reuse' if collisions else 'no-listed-collision'
    return {'record_id':record['record_id'],'outcome':outcome,'reserved_count':len(actual),'collisions':[{'retired_id':x,'successor_id':actual[x]} for x in collisions],'authority_effect':'none','allocation_authorized':False,'new_withdrawal_performed':False,'successor_authority_verified':False,'claim_ceiling':'Recorded identifier reservations only; no global name availability, new withdrawal or successor authority.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py withdrawal-record.json allocation.json')
        result=assess(Path(sys.argv[1]),read_input(Path(sys.argv[2]))); code=0 if result['outcome']=='no-listed-collision' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
