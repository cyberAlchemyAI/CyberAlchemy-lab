"""Actual public malformed/profile/resource requests and mapped active conflicts."""
from pathlib import Path
import copy
import json
import sys
import uuid
import threading
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,V2,ROOT,binding,check,require
from v3.p09.api import Client
from v3.p08.metadata import Store

template=C.decode((HERE/'layout-request.json').read_bytes());policy=template['resource_policy']
run_id=uuid.uuid4().hex;evidence_root=HERE/'hostile-evidence'/run_id;evidence_root.mkdir(parents=True)
client=Client(policy,BASE/'p07/consumer-runs'/('P09-hostile-'+run_id))
controls=[];cases=[]
def raw(r):return json.dumps(r,allow_nan=False).encode()
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def run(name,data,expected,api=client,cancel=None):
    input_path=evidence_root/(name+'.raw');input_path.write_bytes(data)
    answer=api.qualify(data,cancel=cancel);test(name,answer['status'] in expected and not api.live_event(answer))
    source=answer['qualification'];test(name+'-no-claims-or-closure',not source['claims'] and not source['complete_closure'] and source['qualified_result'] is None)
    explanation=api.describe(C.decode(data) if source.get('failure_result') else template,answer);test(name+'-no-absence-or-readiness',explanation['outcome']=='incomplete' and not explanation['application_authorized'])
    path=evidence_root/(name+'.json');path.write_text(json.dumps(answer,indent=2)+'\n')
    cases.append({'name':name,'input':binding(input_path),'input_bytes_sha256':__import__('hashlib').sha256(data).hexdigest(),'answer':binding(path),'observed':answer['status'],'expected':expected,'entry_point':'Client.qualify'})
    (HERE/('hostile-progress-'+run_id+'.json')).write_text(json.dumps({'status':'in-progress','controls':controls,'cases':cases,'authority_effect':'none'},indent=2)+'\n')

run('missing-fields',b'{}',['invalid'])
run('duplicate-operation',b'{"operation":"qualify",'+raw(template)[1:],['invalid'])
run('nonfinite-number',b'{"x":NaN}',['invalid'])
run('over-depth',('['*65+'0'+']'*65).encode(),['invalid'])
run('over-byte-ceiling',b' '* (policy['work_limits']['input_bytes']+1),['unknown-resource'])
def derived_root(r):
    r['proposal']['after']['inference']['rules'].append({'id':'forged-protected-head','version':'v3-hostile','head':{'predicate':'Conforms','terms':[{'variable':'x'}]},'body':[{'predicate':'BaselineSignal','terms':[{'variable':'x'}]}]})
def caller_root(r):r['proposal']['after']['inference']['facts'].append({'predicate':'Conforms','terms':[{'kind':'reference','id':'capability:reviewer','version':'v1'}]})
def domain_change(r):r['proposal']['after']['inference']['domain'].append({'kind':'reference','id':'undeclared-extra','version':'v1'})
def negative_body(r):r['proposal']['after']['inference']['rules'][-1]['body'][0]['negative']=True
def chain_field(r):r['redelegation_chain']=[]
for name,modify,expected in [('derived-protected-root',derived_root,['invalid','unsupported']),('caller-protected-root',caller_root,['invalid','unsupported']),('changed-domain',domain_change,['unsupported']),('negative-body',negative_body,['invalid']),('unsupported-chain-field',chain_field,['invalid'])]:
    r=copy.deepcopy(template);modify(r);run(name,raw(r),expected)
required=copy.deepcopy(policy);required['memory_mode']='required'
r=copy.deepcopy(template);r['resource_policy']=required
required_client=Client(required,BASE/'p07/consumer-runs/P09-required-refusal')
run('required-backend-unavailable',raw(r),['unsupported-policy'],required_client)
tiny=copy.deepcopy(policy);tiny['stage_seconds']=0.000001
r=copy.deepcopy(template);r['resource_policy']=tiny
run('atomic-stage-budget',raw(r),['unknown-resource'],Client(tiny,BASE/'p07/consumer-runs/P09-atomic-refusal'))
cancel=threading.Event();cancel.set();run('actual-user-cancellation',raw(template),['cancelled'],cancel=cancel)

# Valid reviewed requests still have to pass semantic qualification before any
# publication. Use only the new P09 store, never accepted predecessor stores.
layout=C.decode((HERE/'layout-suite.json').read_bytes());store=Store(ROOT/layout['cases'][1]['store']);head=store.head()
baseline=C.decode(check(head['snapshot']).read_bytes())['baseline']
for name,modify in [('failed-application-derived-root',derived_root),('failed-application-caller-root',caller_root)]:
    r=copy.deepcopy(template);r['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':name,'baseline_identity':C.identity(baseline),'before':copy.deepcopy(baseline),'after':copy.deepcopy(baseline)};modify(r)
    C.validate('request',r);data=raw(r);review=store.review(r,data);answer=client.apply(review,data,store)
    test(name,answer['status'] in ['invalid','unsupported'] and not answer['application_authorized'] and store.head()==head)
    p=evidence_root/(name+'.raw');p.write_bytes(data);out=p.with_suffix('.json');out.write_text(json.dumps(answer,indent=2)+'\n')
    cases.append({'name':name,'input':binding(p),'answer':binding(out),'expected':['invalid','unsupported'],'observed':answer['status'],'entry_point':'Client.apply'})

mapped=C.decode((V2/'s13/active-origin.json').read_bytes())['request']
norms=mapped['typed']['graph']['contracts'][0]['norms'];forbid=copy.deepcopy(norms[0]);forbid['mode']='forbid';norms.append(forbid)
mapped['interpretation']['typed_identity']=C.identity(mapped['typed'])
mapped['interpretation']['record_identity']=C.identity({k:v for k,v in mapped['interpretation'].items() if k!='record_identity'})
checked=client.shadow.mapped.qualify(mapped)
test('actual-active-conflict-freshly-checked',checked['status']=='fresh-mapped-candidate' and client.shadow.mapped.live_event(checked))
inspection=checked['value']['inspection']
test('active-conflict-pair-retains-both-origins',inspection['condition_status']=='yes' and len(inspection['active_norms'])==2 and len(inspection['active_conflicts'])==1 and all(n['edge']['id']=='inherits-1' for n in inspection['active_conflicts'][0]))
test('conflict-is-not-fulfillment-or-admission',inspection['fulfilled']=='not-established' and inspection['admission']=='not-derived')
(HERE/'active-conflict-request.json').write_text(json.dumps(mapped,indent=2)+'\n')
(HERE/'active-conflict-result.json').write_text(json.dumps(checked,indent=2)+'\n')
report={'result':'pass','run_id':run_id,'runtime_root':str(client.owned.supervisor.run_root.relative_to(ROOT)),'controls':controls,'cases':cases,'actual_fresh_mapped_checks':1,'fresh_conflict':binding(HERE/'active-conflict-result.json'),
        'scope':'Actual public failures under fixed profile/catalog; one actual mapped conflict witness. No failed qualification creates application capability.','authority_effect':'none'}
(HERE/'public-hostile-controls.json').write_text(json.dumps(report,indent=2)+'\n')
print('Public hostile controls passed:',len(controls),flush=True)
