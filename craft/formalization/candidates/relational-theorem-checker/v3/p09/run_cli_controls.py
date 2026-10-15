"""Actual new command integration over the saved qualified layout and refusals."""
from pathlib import Path
import copy
import json
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require

suite=C.decode((HERE/'layout-suite.json').read_bytes());case=suite['cases'][1]
request=C.decode(check(case['request']).read_bytes());public=C.decode(check(case['qualification']).read_bytes())
payload=C.decode(check(public['qualification']['qualified_result']['payload']).read_bytes())
policy=HERE/'cli-policy.json';policy.write_text(json.dumps(request['resource_policy'],indent=2)+'\n')
query=next(a for a in payload['closure'] if a['predicate']['id']=='FreshReady')
outdir=HERE/'cli-evidence';outdir.mkdir(exist_ok=True);cases=[];controls=[]
def run(name,operation,input_ref,extra,exit_code,expected,kind):
    output=outdir/(name+'.json');require(not output.exists(),'CLI output overwrite refused')
    args=[sys.executable,str(HERE/'cli.py'),operation,str(check(input_ref)),'--policy',str(policy),'--output',str(output),*extra]
    record=outdir/(name+'-invocation.json');record.write_text(json.dumps({'argv':args,'input':input_ref,'policy':binding(policy),'expected_exit':exit_code},indent=2)+'\n')
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    value=C.decode(output.read_bytes());observed=value.get('status',value.get('outcome'))
    require(p.returncode==exit_code and observed==expected,name+': '+p.stdout[:400]+p.stderr[:400])
    if operation=='inspect':require(not value['application_authorized'],'saved CLI inspection authorized')
    controls.append({'name':name,'result':'pass'});cases.append({'name':name,'entry_point':'cli.py '+operation,'evidence_kind':kind,
        'input':binding(record),'output':binding(output),'expected':expected+'; exit '+str(exit_code),'observed':observed+'; exit '+str(p.returncode)})
    print(name,'PASS',flush=True)
run('cli-saved-current-inspection','inspect',case['request'],['--result',str(check(case['qualification']))],0,'recorded-current','saved-inspection')
for name,q,expected in [('cli-positive-explanation',query,'present'),('cli-typed-absence',copy.deepcopy(query),'absent-in-complete-profile')]:
    if name=='cli-typed-absence':q['values'][0]={'kind':'reference','id':'contract:review','version':'v1'}
    path=outdir/(name+'-query.json');path.write_text(json.dumps(q,indent=2)+'\n')
    run(name,'describe',case['request'],['--result',str(check(case['qualification'])),'--query',str(path)],0,expected,'saved-inspection')
malformed=outdir/'malformed.raw';malformed.write_bytes(b'{}')
run('cli-malformed-public-refusal','qualify',binding(malformed),[],3,'invalid','boundary')
report={'result':'pass','controls':controls,'cases':cases,'fresh_successful_kernel_qualifications':0,'authority_effect':'none'}
(HERE/'cli-controls.json').write_text(json.dumps(report,indent=2)+'\n');print('CLI controls passed:',len(controls),flush=True)
