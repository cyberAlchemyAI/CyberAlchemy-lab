"""Inspect Gate evidence without accepting completion or granting authority."""
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

def assess(record_path,observation):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    record=read_input(record_path)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    Draft202012Validator(load(PACKAGE/'observation.schema.json')).validate(observation)
    need(resolve(observation['gate'])==record_path.resolve(),'Observation binds another gate')
    subject=resolve(record['subject'])
    need(resolve(observation['subject'])==subject,'Observation binds another subject')
    criteria={x['criterion_id']:x for x in record['criteria']}
    need(len(criteria)==len(record['criteria']),'Duplicate criterion')
    need(all(type(x['expected']) in [str,int,bool] for x in criteria.values()),'Expected value must be string, integer or boolean')
    need(record['effect_boundary']['from_state'] != record['effect_boundary']['to_state'], 'Effect boundary requires distinct states')
    for criterion in criteria.values():
        need((criterion['risk'] is not None) == (criterion['on_failure']=='flag'), 'Flag requires risk; other failure modes must not carry a flag risk')
    evidence={x['criterion_ref']:x for x in observation['evidence']}
    need(len(evidence)==len(observation['evidence']),'Duplicate criterion evidence')
    need(set(evidence)<=set(criteria),'Unknown criterion evidence')
    results=[]
    for ident,criterion in criteria.items():
        state='defer'; detail='missing-evidence'
        if ident in evidence:
            data=read_input(resolve(evidence[ident]['binding'])); need(isinstance(data,dict),'Evidence must be a JSON object')
            field=criterion['field']
            if field not in data: detail='missing-field'
            else:
                actual=data[field]; expected=criterion['expected']
                matches=type(actual) is type(expected) and actual==expected
                state='pass' if matches else criterion['on_failure']; detail='field-matches' if matches else 'field-mismatch'
        results.append({'criterion_ref':ident,'state':state,'detail':detail})
    states={x['state'] for x in results}
    mismatch=observation['scope_ref']!=record['scope_ref'] or observation['requested_effect']!=record['effect_boundary']['effect']
    verdict='block' if mismatch or 'block' in states else 'defer' if 'defer' in states else 'flag' if 'flag' in states else 'pass'
    risks=[{'criterion_ref':x['criterion_ref'],**criteria[x['criterion_ref']]['risk']} for x in results if x['state']=='flag']
    return {'gate_id':record['gate_id'],'proposed_verdict':verdict,'boundary_mismatch':mismatch,'criteria':results,'risks':risks,'suggested_route':record['review_route'] if verdict in ['pass','flag'] else record['escalation_route'],'record_location':record['record_location'],'declared_effect':record['effect_boundary'],'authority_effect':'none','owner_verdict_recorded':False,'effect_authorized':False,'effect_executed':False,'claim_ceiling':'Computed candidate verdict only; owner acceptance and authority for the downstream effect remain unproven.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py gate-record.json observation.json')
        result=assess(Path(sys.argv[1]),read_input(Path(sys.argv[2]))); code=0 if result['proposed_verdict']=='pass' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
