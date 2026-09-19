"""Preview contestability policy routing without resolving or executing a challenge."""
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

def assess(record,challenge):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    Draft202012Validator(load(PACKAGE/'challenge.schema.json')).validate(challenge)
    questions={x['question_id'] for x in record['blocking_questions']}
    need(len(questions)==len(record['blocking_questions']),'Duplicate question')
    need(not set(record['contradiction_edges'])&set(record['validation_edges']),'Link has contradictory roles')
    need(set(challenge['answers'])<=questions,'Unknown answer question')
    mismatches=[key for key,expected in [('policy_ref',record['policy_id']),('scope_ref',record['scope_ref']),('subject_ref',record['subject_ref'])] if challenge[key]!=expected]
    missing=sorted(questions-set(challenge['answers']))
    blocked=sorted(k for k,v in challenge['answers'].items() if v is False)
    if mismatches: outcome='not-applicable'
    elif challenge['challenge_mode'] not in record['valid_challenge_modes']: outcome='unsupported-mode'
    elif blocked: outcome='blocked'
    elif missing: outcome='indeterminate'
    else: outcome='ready-for-owner-review'
    route=record['owner_route'] if outcome=='ready-for-owner-review' else record['challenge_residue_route'] if outcome in ['blocked','indeterminate'] else None
    return {'policy_id':record['policy_id'],'outcome':outcome,'mismatches':mismatches,'missing_answers':missing,'blocking_answers':blocked,'suggested_route':route,'resolution_gate':record['resolution_gate'],'authority_effect':'none','gate_completed':False,'challenge_resolved':False,'confidence_changed':False,'route_executed':False,'action_authorized':False,'claim_ceiling':'Routing preview from supplied answers only; no verified evidence, verdict, confidence change or authority grant.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py policy-record.json challenge.json')
        result=assess(read_input(Path(sys.argv[1])),read_input(Path(sys.argv[2]))); code=0 if result['outcome']=='ready-for-owner-review' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
