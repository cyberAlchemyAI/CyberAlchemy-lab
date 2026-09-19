"""Inspect bound Authority Claim records without granting authority."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, PACKAGE, load, sha, need, dump

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


import subprocess
import tempfile
def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']+load(PREVIOUS/'manifest.json')['materials']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    surface=resolve(record['authority_surface']); model=read_input(surface)
    target_path=resolve(record['governed_object']['binding']); target=read_input(target_path)
    need(target_path!=surface,'Object and authority surface must be distinct')
    schema_path=LAB/'authority/artifact-types/definition/v1/schema.json'
    need(target['schema_digest']==sha(schema_path),'Definition contract drift')
    Draft202012Validator(load(schema_path)).validate(target)
    need(target['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1','Object is not a Definition')
    subject=target['definition_id']+'@'+target['version']
    need(subject==record['governed_object']['object_ref'],'Object identity mismatch')
    need(record['claim_id'] not in [subject,model['model_id']],'Claim identity collapses into object or model')
    paths=set()
    for basis in record['basis']:
        path=resolve(basis['binding']); need(path not in paths,'Duplicate basis'); paths.add(path)
    query={'model_ref':model['model_id'],'scope_ref':record['scope_ref'],'claim_ref':record['claim_id'],'subject_ref':subject,'kind_ref':record['kind_ref'],'posture_ref':record['posture_ref'],'operation_ref':record['operation_ref'],'intended_effect':record['intended_effect']}
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'claim.json'; dump(path,query)
        result=subprocess.run([sys.executable,str(PREVIOUS/'check.py'),str(surface),str(path)],capture_output=True,text=True)
    need(result.returncode in [0,1],'Model input invalid: '+result.stdout+result.stderr)
    routing=json.loads(result.stdout)
    if routing['outcome']=='requires-owner-gate':
        need(record['owner_route']==routing['owner_route'],'Claim owner route differs from model')
    return {'claim_id':record['claim_id'],'object_ref':subject,'bindings_verified':True,'routing':routing,'owner_ref':record['owner_ref'],'challenge_route':record['challenge_route'],'authority_effect':'none','claim_authenticated':False,'basis_sufficient':False,'gate_verdict_present':False,'action_authorized':False,'claim_ceiling':'Exact bound assertion and candidate model routing only; no verified grant or execution authority.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py authority-claim-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0 if result['routing']['outcome']=='requires-owner-gate' else 1
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
