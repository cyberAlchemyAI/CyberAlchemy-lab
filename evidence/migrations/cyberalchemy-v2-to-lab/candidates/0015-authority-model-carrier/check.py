"""Preview closed authority routing without issuing a grant or gate verdict."""
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

def assess(record,claim):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    Draft202012Validator(load(PACKAGE/'claim.schema.json')).validate(claim)
    kinds=set(record['authority_kinds']); postures=set(record['postures']); effects=set(record['effects'])
    operations={x['operation_id']:x['effect_ref'] for x in record['operations']}
    need(len(operations)==len(record['operations']),'Duplicate operation')
    need(set(operations.values())==effects,'Operation effects must cover exactly the declared effects')
    rules={}; ids=set()
    for rule in record['rules']:
        need(rule['rule_id'] not in ids,'Duplicate rule'); ids.add(rule['rule_id'])
        need(rule['kind_ref'] in kinds and rule['posture_ref'] in postures,'Unknown rule kind or posture')
        key=(rule['kind_ref'],rule['posture_ref']); need(key not in rules,'Conflicting kind-posture rules'); rules[key]=rule
        allowed=set(rule['allowed_effects']); blocked=set(rule['blocked_effects'])
        need(not allowed&blocked and allowed|blocked==effects,'Allowed and blocked effects must partition declared effects')
    need({k for k,p in rules}==kinds,'Kind lacks an owner rule')
    outcome='blocked'; reason=None; route=None; gate=None; surface=None; boundaries=[]
    if claim['model_ref']!=record['model_id'] or claim['scope_ref']!=record['scope_ref']: outcome='not-applicable'; reason='model-or-scope-mismatch'
    elif claim['kind_ref'] not in kinds: reason='unknown-kind'; route=record['amendment_route']
    elif claim['posture_ref'] not in postures: reason='unknown-posture'
    elif claim['operation_ref'] not in operations: reason='unknown-operation'
    elif operations[claim['operation_ref']]!=claim['intended_effect']: reason='operation-effect-mismatch'
    else:
        rule=rules.get((claim['kind_ref'],claim['posture_ref']))
        if rule is None: reason='no-routing-rule'
        else:
            boundaries=rule['non_collapse_rules']
            if claim['intended_effect'] in rule['blocked_effects']: reason='effect-blocked'
            else:
                outcome='requires-owner-gate'; reason='modeled-use-only'; route=rule['owner_route']; gate=rule['gate_ref']; surface=rule['validation_surface_ref']
    return {'model_id':record['model_id'],'claim_ref':claim['claim_ref'],'subject_ref':claim['subject_ref'],'outcome':outcome,'reason':reason,'owner_route':route,'required_gate':gate,'validation_surface':surface,'non_collapse_rules':boundaries,'authority_effect':'none','claim_authenticated':False,'gate_verdict_present':False,'action_authorized':False,'claim_ceiling':'Static routing from supplied claim assertions only; no authority grant, gate verdict or execution.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py authority-model-record.json claim.json')
        result=assess(read_input(Path(sys.argv[1])),read_input(Path(sys.argv[2]))); code=0 if result['outcome']=='requires-owner-gate' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
