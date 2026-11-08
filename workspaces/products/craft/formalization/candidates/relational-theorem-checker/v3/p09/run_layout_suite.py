"""Actual full public qualification, inspection, explanations and two applications per layout."""
from pathlib import Path
import copy
import json
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from v3.p09.api import Client
from v3.p08.metadata import Store

fixture=C.decode((HERE/'layout-request.json').read_bytes());controls=[];cases=[];events=[]
run_id=uuid.uuid4().hex
def raw(req):return json.dumps(req,ensure_ascii=False,allow_nan=False).encode()
def record(name,value):
    events.append({'name':name,'value':value})
    (HERE/'layout-progress.json').write_text(json.dumps({'status':'in-progress','run_id':run_id,'controls':controls,'events':events,'authority_effect':'none'},indent=2)+'\n')
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def save(name,value):
    p=HERE/'layout-evidence'/run_id/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2)+'\n');return binding(p)
def semantic(answer):
    q=answer['qualification']['qualified_result'];p=C.decode(check(q['payload']).read_bytes())
    return {k:p[k] for k in ['normal_form','closure','certificates','supports','observations','model_class','closure_scope']}

for layout in ['combined','staged']:
    request=copy.deepcopy(fixture);request['layout']=layout
    client=Client(request['resource_policy'],BASE/'p07/consumer-runs'/('P09-layout-'+layout+'-'+run_id))
    answer=client.qualify(raw(request));answer_ref=save(layout+'-qualification',answer);record(layout+'-qualification',answer_ref)
    test(layout+'-fresh-full-qualified',answer['status']=='qualified-candidate' and client.live_event(answer))
    q=answer['qualification']['qualified_result'];payload=C.decode(check(q['payload']).read_bytes())
    test(layout+'-all-20-fixed-obligations',q['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')])
    expected=['combined'] if layout=='combined' else ['data','typed','closure','expansion']
    test(layout+'-exact-module-roles',[m['role'] for m in q['manifest']['witness']['modules']]==expected)
    inspected=client.inspect(request,answer);record(layout+'-inspection',save(layout+'-inspection',inspected))
    test(layout+'-saved-inspection-is-recorded-only',inspected['status']=='recorded-current' and not inspected['application_authorized'])
    positive=next(a for a in payload['closure'] if a['predicate']['id']=='FreshReady')
    explanation=client.describe(request,answer,positive);record(layout+'-positive',save(layout+'-positive',explanation))
    test(layout+'-positive-source-trace',explanation['outcome']=='present' and explanation['trace'] and explanation['supports'])
    absent=copy.deepcopy(positive);absent['values'][0]={'kind':'reference','id':'contract:review','version':'v1'}
    absence=client.describe(request,answer,absent);record(layout+'-absence',save(layout+'-absence',absence))
    test(layout+'-typed-complete-profile-absence',absence['outcome']=='absent-in-complete-profile')
    copied=Client(request['resource_policy'])
    test(layout+'-saved-result-no-new-live-event',not copied.live_event(answer))
    initial=copy.deepcopy(request);initial['proposal']['proposal_id']='P09-'+layout+'-initial-registration'
    initial['proposal']['after']=copy.deepcopy(initial['proposal']['before'])
    root=BASE/'p08/stores'/('P09-'+layout+'-'+run_id)
    initialized=client.bootstrap(root,raw(initial));record(layout+'-bootstrap',save(layout+'-bootstrap',initialized))
    test(layout+'-fresh-independent-genesis',initialized['status']=='initialized-candidate-shadow')
    store=Store(root);head0=store.head();review1=store.review(request,raw(request))
    applied1=client.apply(review1,raw(request),store);record(layout+'-application-1',save(layout+'-application-1',applied1))
    test(layout+'-first-real-extension',applied1['status']=='applied-candidate-shadow' and applied1['after']['generation']==1)
    request2=copy.deepcopy(request);before2=copy.deepcopy(request['proposal']['after']);after2=copy.deepcopy(before2)
    after2['inference']['predicates'].append({'id':'EpochMarker','version':'v3-regression','sorts':['epoch'],'role':'ordinary'})
    after2['producers'].append({'predicate':'EpochMarker','class':'derived-information','meaning':'derived-positive-horn'})
    after2['inference']['rules'].append({'id':'observed-epoch-marker','version':'v3-regression',
        'head':{'predicate':'EpochMarker','terms':[{'constant':{'kind':'epoch','value':0}}]},
        'body':[{'predicate':'FreshReady','terms':[{'variable':'x'}]}]})
    request2['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':'P09-'+layout+'-second-extension',
        'baseline_identity':C.identity(before2),'before':before2,'after':after2}
    C.validate('request',request2);review2=store.review(request2,raw(request2))
    applied2=client.apply(review2,raw(request2),store);record(layout+'-application-2',save(layout+'-application-2',applied2))
    test(layout+'-second-real-extension',applied2['status']=='applied-candidate-shadow' and applied2['after']['generation']==2)
    test(layout+'-two-exact-separate-registrations',head0['registration']!=applied1['after']['registration']!=applied2['after']['registration'])
    test(layout+'-immutable-three-snapshots',len(list((store.root/'snapshots').glob('*.json')))==3)
    # The second application's actual fresh proposal remains in this context.
    # Its source-bound stored qualification is inspected for numeric queries.
    tx=applied2['transaction'];proposal_q=C.decode(check(tx['proposal_qualification']).read_bytes())
    p2=C.decode(check(proposal_q['payload']).read_bytes());epoch_atom=next(a for a in p2['closure'] if a['predicate']['id']=='EpochMarker')
    from v3.p09.api import describe
    numeric=copy.deepcopy(epoch_atom);numeric['values'][0]['value']=0.0
    numeric_answer=describe(request2,proposal_q,numeric);record(layout+'-numeric-query',save(layout+'-numeric-query',numeric_answer))
    test(layout+'-integer-valued-float-canonical-trace',numeric_answer['outcome']=='present' and numeric_answer['trace']['nodes'][0]['atom']['values'][0]['value']==0)
    boolean=copy.deepcopy(epoch_atom);boolean['values'][0]['value']=False
    boolean_answer=describe(request2,proposal_q,boolean);record(layout+'-boolean-query',save(layout+'-boolean-query',boolean_answer))
    test(layout+'-boolean-not-normalized-as-natural',boolean_answer['outcome']=='invalid-query')
    stale=client.apply(review1,raw(request),store)
    test(layout+'-stale-review-cannot-publish',stale['status']=='stale-head' and store.head()['generation']==2)
    cases.append({'layout':layout,'request':save(layout+'-request',request),'qualification':answer_ref,
                  'store':str(root.relative_to(ROOT)),'applications':[applied1,applied2],'second_request':save(layout+'-request-2',request2),
                  'semantic':semantic(answer),'second_semantic':{k:p2[k] for k in ['normal_form','closure','certificates','supports','observations','model_class','closure_scope']}})

test('combined-staged-exact-semantic-agreement',cases[0]['semantic']==cases[1]['semantic'])
test('combined-staged-second-extension-semantic-agreement',cases[0]['second_semantic']==cases[1]['second_semantic'])
report={'result':'pass','run_id':run_id,'controls':controls,'cases':cases,'events':events,
        'actual_fresh_horn_qualifications':12,'actual_applications':4,'authority_effect':'none'}
(HERE/'layout-suite.json').write_text(json.dumps(report,indent=2)+'\n')
print('Full two-layout suite passed:',len(controls),flush=True)
