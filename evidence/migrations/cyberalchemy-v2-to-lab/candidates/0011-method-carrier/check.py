"""Validate a Method declaration without running its instructions or gates."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PACKAGE, load, sha, need
from author import FIELDS

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

def index(items,key):
    result={x[key]:x for x in items}; need(len(result)==len(items),'Duplicate '+key); return result

def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    inputs=index(record['inputs'],'slot_id'); outputs=index(record['outputs'],'slot_id')
    need(not set(inputs)&set(outputs),'Inputs and outputs must have distinct slot identities')
    index(record['actions'],'action_id'); gates=index(record['gates'],'gate_id'); roles=set(record['roles'])
    required=set(record['validation_rule']['required_gate_refs'])
    need(required==set(gates),'Completion must require all declared gates')
    available=set(inputs); produced=set(); checked=set(); coverage=set(); plan=[]
    for action in record['actions']:
        need(action['role_ref'] in roles,'Unknown action role')
        need(set(action['reads'])<=available,'Action reads unavailable slot')
        writes=set(action['writes'])
        need(writes<=set(outputs),'Action writes undeclared output')
        need(not writes&produced,'Output produced more than once')
        available|=writes; produced|=writes
        for gate_id in action['gate_refs']:
            need(gate_id in gates,'Unknown gate')
            need(gate_id not in checked,'Gate assigned more than once')
            gate=gates[gate_id]
            need(gate['role_ref'] in roles,'Unknown gate role')
            need(set(gate['subject_refs'])<=available,'Gate checks unavailable slot')
            checked.add(gate_id); coverage.update(gate['subject_refs'])
        plan.append({'action_id':action['action_id'],'reads':action['reads'],'writes':action['writes'],'required_checks':action['gate_refs']})
    need(produced==set(outputs),'Unproduced output')
    need(checked==set(gates),'Unassigned gate')
    need(set(outputs)<=coverage,'Output lacks a gate')
    need(record['residue_rule']['owner_ref'] in roles,'Unknown residue owner')
    fixed=set(record['reuse']['fixed_fields']); special=set(record['reuse']['specializable_fields'])
    need(not fixed&special and fixed|special==set(FIELDS),'Reuse fields must partition all minimum Method fields')
    for ref in record['evidence']: resolve(ref)
    return {'method_id':record['method_id'],'declaration_coherent':True,'ordered_plan':plan,'outputs_covered':sorted(outputs),'authority_effect':'none','instructions_executed':False,'gates_evaluated':False,'outcome_proven':False,'execution_authorized':False,'claim_ceiling':'Static reference and ordering checks only; declared instructions and gate conditions remain unevaluated.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py method-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
