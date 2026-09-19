"""Verify and replay one fixed local checker receipt."""
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


import subprocess
def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']+load(ROOT/'dependencies.json')['inputs']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    need(type(record['exit_code']) is int,'Exit code must be an integer')
    need(record['reported_result']=={0:'passed',2:'invalid-input'}[record['exit_code']],'Result and exit code disagree')
    need(record['python_version']==sys.version,'Python runtime differs from receipt')
    manifest=resolve(record['execution_snapshot'])
    need(manifest==PREVIOUS/'manifest.json','Unsupported execution snapshot')
    for ref in read_input(manifest)['materials']: resolve(ref)
    script=resolve(record['implementation']); input_path=resolve(record['input'])
    need(script==PREVIOUS/'check.py','Unsupported implementation')
    need(input_path==PREVIOUS/'artifact-types/evidence-set/v1/fixtures/valid/evidence-set-record.json','Unsupported replay input')
    stdout=resolve(record['stdout']); stderr=resolve(record['stderr'])
    need(len({script,input_path,stdout,stderr})==4,'Implementation, input and output streams must be distinct')
    replay=subprocess.run([sys.executable,str(script),str(input_path)],capture_output=True,timeout=30)
    need(replay.returncode==record['exit_code'],'Replay exit code mismatch')
    need(replay.stdout==stdout.read_bytes(),'Replay stdout mismatch')
    need(replay.stderr==stderr.read_bytes(),'Replay stderr mismatch')
    return {'receipt_id':record['receipt_id'],'replay_matches':True,'exit_code':replay.returncode,'reported_result':record['reported_result'],'authority_effect':'none','local_replay_performed':True,'historical_actor_authenticated':False,'external_effect_proven':False,'action_authorized':False,'claim_ceiling':'Exact fixed local replay agreement only; no historical actor authentication or external effect proof.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py receipt-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
