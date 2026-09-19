"""Inspect declared pattern context and append-only ledger snapshots."""
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
    forces={x['force_id'] for x in record['forces']}
    need(len(forces)==len(record['forces']),'Duplicate force')
    need(len({x['consequence_id'] for x in record['consequences']})==len(record['consequences']),'Duplicate consequence')
    covered=set()
    for item in record['consequences']:
        need(set(item['force_refs'])<=forces,'Unknown force'); covered.update(item['force_refs'])
    need(covered==forces,'Force lacks consequence')
    before=read_input(resolve(record['witness']['before'])); after=read_input(resolve(record['witness']['after']))
    schema=Draft202012Validator(load(PACKAGE/'ledger.schema.json'))
    for ledger in [before,after]: schema.validate(ledger)
    expected=record['applicability']['required_context']; observed=record['witness']['context']
    mismatched=sorted(k for k,v in expected.items() if k in observed and observed[k]!=v)
    missing=sorted(set(expected)-set(observed))
    applicability='not-applicable' if mismatched else 'indeterminate' if missing else 'applicable'
    errors=[]
    for label,ledger in [('before',before),('after',after)]:
        if ledger['scope_ref']!=record['scope_ref']: errors.append(label+':scope-mismatch')
        ids=[x['event_id'] for x in ledger['events']]
        if len(ids)!=len(set(ids)): errors.append(label+':duplicate-event')
        if any(type(x['sequence']) is not int or x['sequence']!=i for i,x in enumerate(ledger['events'],1)): errors.append(label+':sequence-gap-or-order')
    # Canonical JSON comparison retains JSON type distinctions (true is not 1).
    canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
    if len(after['events'])<len(before['events']): errors.append('history-truncated')
    elif any(canonical(a)!=canonical(b) for a,b in zip(before['events'],after['events'])): errors.append('history-rewritten')
    return {'pattern_id':record['pattern_id'],'applicability':applicability,'missing_context':missing,'mismatched_context':mismatched,'conforms':not errors if applicability=='applicable' else None,'snapshot_errors':errors,'appended_events':max(0,len(after['events'])-len(before['events'])),'authority_effect':'none','runtime_enforcement_proven':False,'promotion_authorized':False,'claim_ceiling':'Supplied snapshots and declared context only; no runtime, durability, concurrency or promotion proof.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py architecture-pattern-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0 if result['conforms'] is True else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
