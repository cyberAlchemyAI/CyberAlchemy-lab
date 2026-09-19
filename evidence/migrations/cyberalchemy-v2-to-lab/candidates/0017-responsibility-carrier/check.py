"""Inspect Responsibility evidence without accepting completion or granting authority."""
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
    need(resolve(observation['responsibility'])==record_path.resolve(),'Observation binds another responsibility')
    subject=resolve(record['subject'])
    need(resolve(observation['subject'])==subject,'Observation binds another subject')
    criteria={x['criterion_id']:x for x in record['criteria']}
    need(len(criteria)==len(record['criteria']),'Duplicate criterion')
    need(all(type(x['expected']) in [str,int,bool] for x in criteria.values()),'Expected value must be string, integer or boolean')
    evidence={x['criterion_ref']:x for x in observation['evidence']}
    need(len(evidence)==len(observation['evidence']),'Duplicate criterion evidence')
    need(set(evidence)<=set(criteria),'Unknown criterion evidence')
    results=[]
    for ident,criterion in criteria.items():
        state='indeterminate'; detail='missing-evidence'
        if ident in evidence:
            data=read_input(resolve(evidence[ident]['binding'])); need(isinstance(data,dict),'Evidence must be a JSON object')
            field=criterion['field']
            if field not in data: detail='missing-field'
            else:
                actual=data[field]; expected=criterion['expected']
                matches=type(actual) is type(expected) and actual==expected
                state='supported' if matches else 'unmet'; detail='field-matches' if matches else 'field-mismatch'
        results.append({'criterion_ref':ident,'state':state,'detail':detail})
    states={x['state'] for x in results}
    if observation['scope_ref']!=record['scope_ref']: outcome='not-applicable'; route=None
    else:
        outcome='unmet' if 'unmet' in states else 'indeterminate' if 'indeterminate' in states else 'supported-for-owner-review'
        route=record['review_route'] if outcome=='supported-for-owner-review' else record['escalation_route']
    return {'responsibility_id':record['responsibility_id'],'outcome':outcome,'criteria':results,'suggested_route':route,'owner_ref':record['owner_ref'],'authority_effect':'none','completion_accepted':False,'owner_authenticated':False,'action_authorized':False,'route_executed':False,'claim_ceiling':'Exact supplied evidence-field matches only; no evidence truth, completion acceptance or authority grant.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py responsibility-record.json observation.json')
        result=assess(Path(sys.argv[1]),read_input(Path(sys.argv[2]))); code=0 if result['outcome']=='supported-for-owner-review' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
