"""Read-only comparison of bound finite graph schema versions and regression witnesses."""
import json
import subprocess
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

def graph_check(schema,graph):
    result=subprocess.run([sys.executable,str(PREVIOUS/'check.py'),str(schema),str(graph)],capture_output=True,text=True)
    need(result.returncode in (0,1),'Graph check invalid: '+result.stdout+result.stderr)
    return json.loads(result.stdout)

def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Carrier contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']+load(PREVIOUS/'manifest.json')['materials']:
        resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    pre,post=resolve(record['preimage']),resolve(record['postimage'])
    need(pre.read_bytes()!=post.read_bytes(),'No schema change')
    a,b=read_input(pre),read_input(post)
    for key in ['schema_id','scope_ref','relative_level','profile']:
        need(a[key]==b[key],'Schema identity, scope, profile or relative level changed: '+key)
    need(a['scope_ref']==record['scope_ref'],'Amendment scope mismatch')
    need(resolve(record['validator_ref'])==PREVIOUS/'check.py','Unsupported validator')
    for ref in record['source_evidence']: resolve(ref)
    ids=set(); results=[]
    for witness in record['witnesses']:
        need(witness['witness_id'] not in ids,'Duplicate witness'); ids.add(witness['witness_id'])
        before,after=resolve(witness['before']),resolve(witness['after'])
        checks={'before':graph_check(pre,before),'after_on_original':graph_check(post,before),'after_on_migrated':graph_check(post,after)}
        for key,result in checks.items():
            need(result['conforms']==witness['expected_'+key],'Regression expectation mismatch: '+key)
        results.append({'witness_id':witness['witness_id'],'checks':checks})
    compatibility='breaking-on-witnesses' if any(not x['checks']['after_on_original']['conforms'] for x in results) else 'compatible-on-witnesses'
    need(compatibility==record['compatibility_claim'],'Compatibility claim differs from witnesses')
    return {'change_id':record['change_id'],'compatibility':compatibility,'changed_top_level_fields':sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k)),'witnesses':results,'obligations_recorded':True,'obligations_executed':False,'universal_compatibility_proven':False,'authority_effect':'none','rollout_authorized':False,'preimage':record['preimage'],'postimage':record['postimage']}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py schema-change-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
