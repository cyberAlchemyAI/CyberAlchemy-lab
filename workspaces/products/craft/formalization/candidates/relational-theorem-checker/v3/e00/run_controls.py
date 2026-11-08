"""Independent tables, exact-key challenges and actual supervised proof witnesses."""
from pathlib import Path
import copy
import json
import sys
import threading
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,binding,check,require,write
from v3.execution.extension_runtime import Client,schema_validate
from v3.e00.evaluator import prepare,evaluate
from v3.e00.adapter import prevalidate

policy=C.decode((BASE/'p01/request-fixture.json').read_bytes())['resource_policy']
run_id=uuid.uuid4().hex;out=HERE/'evidence'/run_id;out.mkdir(parents=True)
frame={'profile':'expression-fixture','context':{'id':'context','version':'v1'},'subject':{'id':'reviewer','version':'v1'},
    'target':{'id':'contract','version':'v1'},'scope':'static','epoch':0}
left={'op':'atom','condition':{'id':'left','version':'v1'}};right={'op':'atom','condition':{'id':'right','version':'v1'}}
def request(expr=left,entries=None,f=frame,mapped=None):return {'schema':'relational.condition-expression-request/v1','profile':'condition-expression-v1',
    'frame':copy.deepcopy(f),'condition':{'id':'expression','version':'v1'},'expression':copy.deepcopy(expr),'evaluations':copy.deepcopy(entries or []),'mapped':mapped}
def entry(atom,value,f=frame):return {'key':{**copy.deepcopy(f),'condition':copy.deepcopy(atom['condition'])},'value':value,'assessment':{'id':atom['condition']['id']+'-assessment','version':'v1'}}
controls=[];cases=[];client=Client('E00',policy)
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def pure(r):
    prevalidate(r);schema_validate(HERE/'expression.schema.json',r);_,values,_=prepare(r['expression'],r['frame'],r['evaluations']);return evaluate(r['expression'],r['frame'],values)
table=[('yes','yes','yes','yes'),('yes','no','no','yes'),('yes','unknown','unknown','yes'),
    ('no','yes','no','yes'),('no','no','no','no'),('no','unknown','no','unknown'),
    ('unknown','yes','unknown','yes'),('unknown','no','no','unknown'),('unknown','unknown','unknown','unknown')]
for a,b,and_expected,or_expected in table:
    for op,expected in [('and',and_expected),('or',or_expected)]:
        r=request({'op':op,'left':left,'right':right},[entry(left,a),entry(right,b)])
        test('independent-'+op+'-'+a+'-'+b,pure(r)==expected)
for a,expected in [('yes','no'),('no','yes'),('unknown','unknown')]:test('independent-not-'+a,pure(request({'op':'not','operand':left},[entry(left,a)]))==expected)
test('missing-leaf-is-unknown',pure(request())=='unknown')

def actual(name,r,expected_status,verdict=None,raw=None,cancel=None):
    raw=raw if raw is not None else json.dumps(r,ensure_ascii=False,allow_nan=False).encode()
    inp=out/(name+'.raw');inp.write_bytes(raw)
    answer=client.qualify(raw,cancel=cancel);answer_ref=write(out/(name+'.json'),answer)
    print(name,answer['status'],answer.get('reason',''),flush=True)
    cases.append({'name':name,'input':binding(inp),'answer':answer_ref,'observed':answer['status']})
    (HERE/'control-progress.json').write_text(json.dumps({'cases':cases,'controls':controls},indent=2)+'\n')
    test(name+'-actual-status',answer['status']==expected_status)
    if verdict is not None:
        value=answer['value']['value'];test(name+'-actual-verdict',value['verdict']==verdict)
        test(name+'-fresh-event',client.live_event(answer))
        test(name+'-no-core-application',not answer['application_authorized'] and value['admission']=='not-derived')
        changed=copy.deepcopy(answer);changed['value']['value']['verdict']='unknown' if verdict!='unknown' else 'yes'
        test(name+'-changed-result-refused',not client.live_event(changed))
        test(name+'-new-client-no-rehydration',not Client('E00',policy).live_event(answer))
    else:test(name+'-no-qualification-event',not client.live_event(answer))
    return answer

actual('nested-positive',request({'op':'and','left':left,'right':{'op':'not','operand':right}},[entry(left,'yes'),entry(right,'no')]),'fresh-extension-candidate','yes')
actual('missing-unknown',request({'op':'not','operand':left}),'fresh-extension-candidate','unknown')
actual('negative-conjunction',request({'op':'and','left':left,'right':right},[entry(left,'no')]),'fresh-extension-candidate','no')

prior=C.decode((BASE/'p11/worked-examples.json').read_bytes())
for name,source_name,truth in [('mapped-active','unknown-potential-norm','yes'),('mapped-unknown','unknown-potential-norm','unknown'),('mapped-opposing-origins','active-conflicting-norms','yes')]:
    source=next(c for c in prior['cases'] if c['name']==source_name)
    original=C.decode(check(source['source_result']).read_bytes());key=original['condition_key'];f={k:v for k,v in key.items() if k!='condition'}
    atom={'op':'atom','condition':key['condition']};r=request(atom,[entry(atom,truth,f)],f,{'request':source['input'],'result':source['source_result']});r['condition']=key['condition']
    answer=actual(name,r,'fresh-extension-candidate',truth);value=answer['value']['value']
    test(name+'-potential-origin-retained',len(value['potential_origins'])==len(original['potential_norms']) and bool(value['potential_origins']))
    test(name+'-activation-count',len(value['active_origins'])==(len(original['potential_norms']) if truth=='yes' else 0))
    test(name+'-recorded-mapping-explicit',value['mapped_proof_mode']=='recorded-current-source-witness')
    if name=='mapped-active':mapped_positive=r
    if name=='mapped-opposing-origins':test('require-and-forbid-origins-retained',{json.loads(o)['norm']['mode'] for o in value['active_origins']}=={'require','forbid'})

bad=request({'op':'or','left':left,'right':right},[entry(left,'yes'),entry(right,'yes'),entry(right,'no')])
actual('conflict-in-nonessential-branch',bad,'invalid')
for field,replacement in [('epoch',1),('scope','other-scope'),('context',{'id':'context','version':'v2'}),('subject',{'id':'other','version':'v1'}),('target',{'id':'contract','version':'v2'}),('profile','different-profile')]:
    bad=request(entries=[entry(left,'yes')]);bad['evaluations'][0]['key'][field]=replacement
    actual('changed-key-'+field,bad,'invalid')
bad=request(entries=[entry(left,'yes')]);bad['evaluations'][0]['key']['condition']['version']='v2';actual('changed-condition-revision',bad,'invalid')
bad=request(entries=[entry(left,'yes'),entry(left,'yes')]);actual('duplicate-same-evidence',bad,'invalid')
bad=request();bad['frame']['epoch']=False;actual('boolean-epoch',bad,'invalid')
bad=copy.deepcopy(mapped_positive);bad['condition']['version']='wrong-root';actual('mapped-root-revision-mismatch',bad,'invalid')
bad=request({'op':'execute','code':'print(1)'});actual('unsupported-execution-operator',bad,'unsupported')
deep=left
for _ in range(16):deep={'op':'not','operand':deep}
actual('depth-exhaustion',request(deep),'unknown-resource')
actual('duplicate-json-key',None,'invalid',raw=b'{"schema":"x","schema":"y"}')
actual('nonfinite-json',None,'invalid',raw=b'{"n":NaN}')
cancel=threading.Event();cancel.set();actual('explicit-cancellation',request(),'cancelled',cancel=cancel)
required=copy.deepcopy(policy);required['memory_mode']='required';answer=Client('E00',required).qualify(json.dumps(request()).encode())
from v3.p06.supervisor import capabilities
if not capabilities()['required_memory_available']:test('unavailable-required-backend-refuses',answer['status']=='unsupported-policy' and not answer.get('value'))

write(HERE/'controls.json',{'result':'pass','run_id':run_id,'controls':controls,'cases':cases,'new_complete_expression_witnesses':6,
    'independent_tables':table,'formal_proof':binding(HERE/'formal-kernel-evidence.json'),'legacy_atomic':'unchanged accepted profile; selected mapped source witness inspected under its original meanings',
    'authority_effect':'none'})
print('E00 controls complete:',len(controls),flush=True)
