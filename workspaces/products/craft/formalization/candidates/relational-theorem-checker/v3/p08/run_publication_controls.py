"""Full fresh API applications, competing publishers and separately registered successors."""
from pathlib import Path
import copy
import json
import sys
import threading
import uuid
import argparse
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import ROOT,C,V2,binding,require
from v3.p08.shadow import ShadowContext
from v3.p08.metadata import Store,validate
request=C.decode((BASE/'p01/request-fixture.json').read_bytes());policy=request['resource_policy']
context=ShadowContext(policy,BASE/'p07/consumer-runs'/('P08-publication-'+uuid.uuid4().hex))
args=argparse.ArgumentParser();args.add_argument('--initialization-evidence',type=Path);args=args.parse_args()
store_path=HERE/'stores'/('fresh-publication-'+uuid.uuid4().hex)
controls=[];evidence={};events=[]
def check(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def record(stage,value):
    validate('application',value);events.append({'stage':stage,'result':value})
    (HERE/'publication-in-progress.json').write_text(json.dumps({'status':'in-progress','controls':controls,'events':events,'authority_effect':'none'},indent=2)+'\n')
def raw(req):return json.dumps(req,ensure_ascii=False,allow_nan=False).encode()
initial=copy.deepcopy(request);initial['proposal']['after']=copy.deepcopy(initial['proposal']['before']);initial['proposal']['proposal_id']='P08-genesis-registration'
check('unowned-bootstrap-refuses-before-check',context.bootstrap(BASE/'p08/outside-store',initial)['status']=='invalid')
if args.initialization_evidence:
    old=C.decode(args.initialization_evidence.read_bytes());boot=next(e['result'] for e in old['events'] if e['stage']=='bootstrap')
    store_path=ROOT/boot['store'];existing=Store(store_path).head()
    require(existing==boot['head'] and existing['generation']==0,'resumption cannot reset or replace a published fixture')
    record('earlier-fresh-initialization-inspected',boot)
else:
    boot=context.bootstrap(store_path,initial);record('bootstrap',boot)
check('fresh-independent-genesis-registration',boot['status']=='initialized-candidate-shadow')
store=Store(store_path);original=store.head();evidence['genesis']=boot
check('genesis-exact-baseline',original['baseline_identity']==C.identity(request['proposal']['before']) and original['generation']==0 and original['registration'] is not None)
check('saved-preflight-cannot-authorize',context.commit('0'*32,store)['status']=='invalid')
cancel=threading.Event();cancel.set();review_empty=store.review(request,raw(request))
check('explicit-cancel-retains-head',context.prepare(review_empty,raw(request),store,cancel=cancel)['status']=='cancelled' and store.head()==original)
mapped=[C.decode((V2/'s13/active-origin.json').read_bytes())['request']]
delegation=C.decode((V2/'s13/expired-delegation.json').read_bytes())['request']
delegation['baseline']['context']['epoch']=5;delegation['typed']['snapshot']['epoch']=5
delegation['baseline']['inference']['snapshot_epoch']=5
delegation['interpretation']['context_identity']=C.identity(delegation['baseline']['context'])
delegation['interpretation']['typed_identity']=C.identity(delegation['typed'])
delegation['interpretation']['record_identity']=C.identity({k:v for k,v in delegation['interpretation'].items() if k!='record_identity'})
mapped.append(delegation)
review=store.review(request,raw(request),mappings=mapped)
changed=copy.deepcopy(mapped);changed[0]['evaluations'][0]['key']['epoch']+=1
check('changed-condition-review-refuses',context.prepare(review,raw(request),store,mappings=changed)['status']=='invalid' and store.head()==original)
changed_request=copy.deepcopy(request);changed_request['proposal']['before']['context']['epoch']+=1
check('changed-context-raw-refuses',context.prepare(review,raw(changed_request),store,mappings=mapped)['status']=='invalid')
first=context.prepare(review,raw(request),store,mappings=mapped);record('first-prepared',first)
check('first-proposal-and-successor-freshly-checked',first['status']=='prepared-candidate-shadow')
permit=context._permits[first['handle']]
check('fresh-mapped-contexts-remain-individual',first['contexts']['horn']!=first['contexts']['mapped'][0] and len(first['mapped_checks'])==2)
check('both-positive-mapped-gates-fresh',all(context.mapped.live_event(a) and a['value']['inspection']['verdict']=='yes' for a in permit['mapped_checks']))
other_context=ShadowContext(policy)
check('saved-preparation-new-context-refuses',other_context.commit(first['handle'],store)['status']=='invalid')
bad=copy.deepcopy(permit['proposal']);bad['qualified_result']['manifest']['obligations'].pop()
check('saved-shrunken-qualification-no-live-event',not context.api.live_event(bad['qualified_result']))
# Both competitors undergo actual fresh proposal and registration checks.
# Their commits then contend for the same recorded generation.
competitor=context.prepare(review,raw(request),store,mappings=mapped);record('competitor-prepared',competitor)
check('second-publisher-also-freshly-checked',competitor['status']=='prepared-candidate-shadow')
barrier=threading.Barrier(2);answers=[]
def commit(handle):barrier.wait();answers.append(context.commit(handle,store))
threads=[threading.Thread(target=commit,args=(a['handle'],)) for a in [first,competitor]]
for t in threads:t.start()
for t in threads:t.join()
for i,a in enumerate(answers):record('competing-commit-'+str(i),a)
check('one-fresh-competing-generation-commits',sorted(a['status'] for a in answers)==['applied-candidate-shadow','stale-head'])
winner=next(a for a in answers if a['status']=='applied-candidate-shadow');head1=store.head()
check('first-successor-exact-and-registered',head1==winner['after'] and head1['generation']==1 and head1['baseline_identity']==C.identity(request['proposal']['after']))
check('live-handles-consumed-once',all(context.commit(a['handle'],store)['status']=='invalid' for a in [first,competitor]))
check('old-reviewed-generation-rejects',context.prepare(review,raw(request),store,mappings=mapped)['status']=='stale-head')
next_request=copy.deepcopy(request);after=copy.deepcopy(request['proposal']['after'])
after['inference']['predicates'].append({'id':'NextReview','version':'v3-candidate','sorts':['reference'],'role':'ordinary'})
after['producers'].append({'predicate':'NextReview','class':'derived-information','meaning':'derived-positive-horn'})
after['inference']['rules'].append({'id':'next-review','version':'v3-candidate','head':{'predicate':'NextReview','terms':[{'variable':'x'}]},'body':[{'predicate':'ContractReady','terms':[{'variable':'x'}]}]})
next_request['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':'P08-second-real-extension','baseline_identity':C.identity(request['proposal']['after']),'before':copy.deepcopy(request['proposal']['after']),'after':after}
review2=store.review(next_request,raw(next_request),mappings=mapped)
second=context.prepare(review2,raw(next_request),store,mappings=mapped);record('second-prepared',second)
check('second-real-extension-freshly-checked',second['status']=='prepared-candidate-shadow')
# A concrete postcommit exception, not a fabricated qualification, exercises
# the public result path after the authoritative transaction is durable.
old_mirror=store._mirror;raised=[False]
def fail_first_mirror(head):
    if not raised[0]:raised[0]=True;raise OSError('Injected owned fixture mirror-write interruption after durable commit')
    return old_mirror(head)
store._mirror=fail_first_mirror
second_applied=context.commit(second['handle'],store);store._mirror=old_mirror;record('second-committed',second_applied)
check('postcommit-exception-reports-durable-application',raised[0] and second_applied['status']=='applied-candidate-shadow' and 'Recovered' in second_applied['reason'])
head2=store.head()
check('second-new-successor-exact',head2['generation']==2 and head2['baseline_identity']==C.identity(after))
check('two-successors-separately-registered',original['registration']!=head1['registration']!=head2['registration'])
check('three-exact-immutable-snapshots',len(list((store.root/'snapshots').glob('*.json')))==3)
recovery=store.recover();validate('recovery',recovery)
check('recovery-never-issues-fresh-capability',recovery['status']=='head-current' and not recovery['fresh_qualification'])
check('candidate-only-authority',all(a['result']['authority_effect']=='none' and not a['result']['application_authorized'] for a in events))
report={'result':'pass','controls':controls,'events':events,'store':str(store.root.relative_to(ROOT)),
        'initialization_evidence':binding(args.initialization_evidence) if args.initialization_evidence else None,
        'actual_fresh_horn_qualifications':7,'actual_fresh_mapped_checks':6,
        'applications':[winner,second_applied],'heads':[original,head1,head2],
        'composition_policy':'individually qualified contexts; no truth merging across different contexts/epochs',
        'scope':'Full public API applications; all stores and deliberate faults are owned candidate fixtures. Metadata crash probes are separately labeled unqualified.',
        'authority_effect':'none'}
(HERE/'publication-controls.json').write_text(json.dumps(report,indent=2)+'\n')
print('Full publication controls passed:',len(controls),flush=True)
