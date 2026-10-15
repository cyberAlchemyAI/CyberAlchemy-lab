"""Continue the retained suite after a real stage refusal, without reissuing saved events."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from v3.p09.api import Client,describe
from v3.p08.metadata import Store

progress=C.decode((HERE/('layout-continuation-progress.json' if '--report-only' in sys.argv else 'layout-progress.json')).read_bytes());run_id=progress['run_id']
controls=progress['controls'];events=progress['events'];fixture=C.decode((HERE/'layout-request.json').read_bytes())
for event in events:check(event['value'])
def raw(r):return json.dumps(r,ensure_ascii=False,allow_nan=False).encode()
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def save(name,value):
    p=HERE/'layout-evidence'/run_id/(name+'.json')
    if p.exists():
        require(C.decode(p.read_bytes())==value,'existing evidence differs');return binding(p)
    p.write_text(json.dumps(value,indent=2)+'\n');return binding(p)
def record(name,value):
    events.append({'name':name,'value':value});(HERE/'layout-continuation-progress.json').write_text(json.dumps({'run_id':run_id,'controls':controls,'events':events},indent=2)+'\n')
def read_event(name):return C.decode(check(next(e['value'] for e in events if e['name']==name)).read_bytes())
def successor(r):
    r=copy.deepcopy(r);before=copy.deepcopy(r['proposal']['after']);after=copy.deepcopy(before)
    after['inference']['predicates'].append({'id':'EpochMarker','version':'v3-regression','sorts':['epoch'],'role':'ordinary'})
    after['producers'].append({'predicate':'EpochMarker','class':'derived-information','meaning':'derived-positive-horn'})
    after['inference']['rules'].append({'id':'observed-epoch-marker','version':'v3-regression','head':{'predicate':'EpochMarker','terms':[{'constant':{'kind':'epoch','value':0}}]},'body':[{'predicate':'FreshReady','terms':[{'variable':'x'}]}]})
    r['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':'P09-'+r['layout']+'-second-extension','baseline_identity':C.identity(before),'before':before,'after':after};C.validate('request',r);return r
def semantics(q):
    p=C.decode(check(q['payload']).read_bytes());return {k:p[k] for k in ['normal_form','closure','certificates','supports','observations','model_class','closure_scope']}

if '--report-only' not in sys.argv:
    failure=read_event('staged-application-1');require(failure['status']=='unknown-resource','unexpected retry cause')
    store=Store(BASE/'p08/stores'/('P09-staged-'+run_id));head0=store.head()
    test('staged-stage-refusal-retained-and-head-unchanged',head0['generation']==0 and not failure['application_authorized'])
    request=copy.deepcopy(fixture);request['layout']='staged'
    client=Client(request['resource_policy'],BASE/'p07/consumer-runs'/('P09-layout-staged-retry-'+run_id))
    review1=store.review(request,raw(request));applied1=client.apply(review1,raw(request),store)
    record('staged-application-1-retry',save('staged-application-1-retry',applied1))
    test('staged-first-real-extension',applied1['status']=='applied-candidate-shadow' and applied1['after']['generation']==1)
    request2=successor(request);review2=store.review(request2,raw(request2));applied2=client.apply(review2,raw(request2),store)
    record('staged-application-2',save('staged-application-2',applied2))
    test('staged-second-real-extension',applied2['status']=='applied-candidate-shadow' and applied2['after']['generation']==2)
    test('staged-two-exact-separate-registrations',head0['registration']!=applied1['after']['registration']!=applied2['after']['registration'])
    test('staged-immutable-three-snapshots',len(list((store.root/'snapshots').glob('*.json')))==3)
    q=C.decode(check(applied2['transaction']['proposal_qualification']).read_bytes());p=C.decode(check(q['payload']).read_bytes())
    atom=next(a for a in p['closure'] if a['predicate']['id']=='EpochMarker');numeric=copy.deepcopy(atom);numeric['values'][0]['value']=0.0
    answer=describe(request2,q,numeric);record('staged-numeric-query',save('staged-numeric-query',answer))
    test('staged-integer-valued-float-canonical-trace',answer['outcome']=='present' and answer['trace']['nodes'][0]['atom']['values'][0]['value']==0)
    boolean=copy.deepcopy(atom);boolean['values'][0]['value']=False;answer=describe(request2,q,boolean);record('staged-boolean-query',save('staged-boolean-query',answer))
    test('staged-boolean-not-normalized-as-natural',answer['outcome']=='invalid-query')
    stale=client.apply(review1,raw(request),store);record('staged-stale-review',save('staged-stale-review',stale))
    test('staged-stale-review-cannot-publish',stale['status']=='stale-head' and store.head()['generation']==2)
cases=[]
if not any(c['name']=='staged-stale-review-cannot-publish' for c in controls):
    stale=read_event('staged-stale-review')
    test('staged-stale-review-cannot-publish',stale['status']=='stale-head' and Store(BASE/'p08/stores'/('P09-staged-'+run_id)).head()['generation']==2)
for layout in ['combined','staged']:
    r=copy.deepcopy(fixture);r['layout']=layout;r2=successor(r)
    a1=read_event(layout+'-application-1'+('-retry' if layout=='staged' else ''));a2=read_event(layout+'-application-2');public=read_event(layout+'-qualification')
    q2=C.decode(check(a2['transaction']['proposal_qualification']).read_bytes());require(q2['request_identity']==C.identity(r2),'actual successor request correspondence')
    cases.append({'layout':layout,'request':save(layout+'-request',r),'qualification':next(e['value'] for e in events if e['name']==layout+'-qualification'),
        'store':str((BASE/'p08/stores'/('P09-'+layout+'-'+run_id)).relative_to(ROOT)),'applications':[a1,a2],
        'second_request':save(layout+'-request-2',r2),'semantic':semantics(public['qualification']['qualified_result']),'second_semantic':semantics(q2)})
test('combined-staged-exact-semantic-agreement',cases[0]['semantic']==cases[1]['semantic'])
test('combined-staged-second-extension-semantic-agreement',cases[0]['second_semantic']==cases[1]['second_semantic'])
report={'result':'pass','run_id':run_id,'controls':controls,'cases':cases,'events':events,'actual_fresh_horn_qualifications':12,
    'actual_applications':4,'additional_failed_qualification_attempts':1,'retained_failure':next(e['value'] for e in events if e['name']=='staged-application-1'),'authority_effect':'none'}
(HERE/'layout-suite.json').write_text(json.dumps(report,indent=2)+'\n');print('Full two-layout suite passed:',len(controls),flush=True)
