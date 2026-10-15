from pathlib import Path
import sys,json,copy,uuid,threading,concurrent.futures,multiprocessing,sqlite3
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.p03.context import C,write,require,binding,check
from v3.execution.extension_runtime import Client,schema_validate
from v3.e04 import lifecycle_adapter as m
from v3.e04.store import Store,Conflict
policy=C.decode((B/'p01/request-fixture.json').read_bytes())['resource_policy'];runid=uuid.uuid4().hex;out=H/'evidence'/runid;out.mkdir(parents=True);owned=H/'store-controls'/runid;owned.mkdir(parents=True);controls=[];cases=[]
def test(n,v):require(v,n);controls.append({'name':n,'result':'pass'});print(n,'PASS',flush=True)
def ref(n):return {'id':n,'version':'v1'}
store=Store.create(owned/'main',ref('initial'),ref('ctx'),5);initial=store.snapshot()
def request(successor='successor-B',state=initial,value='yes'):
 d={'ref':ref('declaration-'+successor),'predecessor':state['head'],'successor':ref(successor),'declared':True}
 r={'schema':'relational.lifecycle-request/v1','profile':'candidate-lifecycle-v1','before':state,'declaration':d,'eligibility':{'ref':ref('eligibility-'+successor),'declaration':d['ref'],'predecessor':d['predecessor'],'successor':d['successor'],'context':state['context'],'epoch':state['epoch'],'value':value},'review':{'ref':ref('review-'+successor),'head':state['head'],'successor':d['successor'],'generation':state['generation'],'context':state['context'],'epoch':state['epoch'],'accepted':True},'source_identity':''};r['source_identity']=C.identity(m.payload(r));return r
def stamp(r):r['source_identity']=C.identity(m.payload(r));return r
def local(n,r,v=None,error=None):
 try:schema_validate(m.SCHEMA,r);p=m.normalize(r,None)
 except Exception as e:test(n,error is not None and error in str(e));return
 test(n,error is None and p['eligible']==v)
r=request();local('exact-transition-eligible',r,True)
r=request(value='unknown');local('declaration-only-no-eligibility',r,False)
r=request();r['review']['accepted']=False;local('missing-current-head-review',stamp(r),False)
r=request();r['review']['generation']=1;local('stale-reviewed-generation',stamp(r),False)
r=request();r['eligibility']['context']=ref('foreign');local('foreign-eligibility-context',stamp(r),error='key mismatch')
r=request();r['declaration']['successor']=initial['head'];r['eligibility']['successor']=initial['head'];r['review']['successor']=initial['head'];local('history-cycle-rejected',stamp(r),False)
r=request();r['before']=copy.deepcopy(initial);r['before']['generation']=1;local('malformed-history-generation',stamp(r),error='malformed')
client=Client('E04',policy);answers=[]
for name,r,v in [('eligible-B',request(),True),('eligible-C',request('successor-C'),True),('declaration-only',request('ineligible',value='unknown'),False)]:
 ri=write(out/(name+'-request.json'),r);a=client.qualify(json.dumps(r).encode());ra=write(out/(name+'-result.json'),a);cases.append({'name':name,'input':ri,'answer':ra});print(name,a['status'],a.get('reason',''),flush=True)
 test(name+'-actual-kernel',a['status']=='fresh-extension-candidate');test(name+'-eligibility',a['value']['value']['eligible']==v);test(name+'-qualification-no-commit',store.snapshot()==initial);answers.append(a)
# Real process crashes test the isolated private storage primitive, not event minting.
for stage,code,gen in [('before-commit',91,0),('after-commit',92,1)]:
 path=owned/stage;path.mkdir();clone=Store(path)
 with store._connection() as src,clone._connection() as dst:src.backup(dst)
 a=answers[0];r=C.decode(check(a['value']['request']).read_bytes());p=m.normalize(r,None)
 process=multiprocessing.get_context('fork').Process(target=clone._transaction,args=(r,p,a['completion'],stage));process.start();process.join(30)
 if process.is_alive():process.terminate();process.join();raise ValueError('crash test child did not exit')
 test(stage+'-real-exit',process.exitcode==code);rec=clone.recover();test(stage+'-durable-generation',rec['state']['generation']==gen);test(stage+'-recovery-no-freshness',rec['fresh_event'] is False)
 write(out/(stage+'-recovery.json'),rec)
# Saved, altered and rule-only proofs cannot enter the public commit gate.
def refused(n,cl,a,part):
 try:store.commit(cl,a)
 except Exception as e:test(n,part in str(e));return
 raise ValueError(n+' unexpectedly committed')
refused('saved-new-client-no-write',Client('E04',policy),answers[0],'fresh owned')
forged=copy.deepcopy(answers[0]);forged['value']['value']['after']['head']=ref('forged');refused('changed-receipt-no-write',client,forged,'mismatch')
refused('rule-only-receipt-no-write',Client('E00',policy),answers[0],'exact lifecycle')
refused('declaration-only-no-write',client,answers[2],'eligibility')
test('all-refusals-preserve-initial-head',store.snapshot()==initial)
barrier=threading.Barrier(2)
def competing(a):
 barrier.wait()
 try:return Store(store.path).commit(client,a)
 except Conflict as e:return {'status':'conflict','reason':str(e)}
with concurrent.futures.ThreadPoolExecutor(2) as pool:results=list(pool.map(competing,answers[:2]))
test('two-real-competing-writers-one-commit',sorted(a['status'] for a in results)==['candidate-lifecycle-committed','conflict'])
rec=store.recover();test('one-exact-current-head',rec['state']['generation']==1 and len(rec['records'])==1);test('history-evidence-retained',rec['state']['history'][0]==initial['head'] and len(rec['state']['evidence'])==1);test('recovery-does-not-issue-event',not rec['fresh_event']);write(out/'competing-results.json',results);write(out/'main-recovery.json',rec)
refused('old-predecessor-after-winner-conflict',client,answers[0],'head/generation conflict')
write(H/'controls.json',{'result':'pass','controls':controls,'cases':cases,'full_witnesses_required':3,'crash_scope':'Real child crashes exercise isolated private SQLite storage after already checked proof; public live-event gate tested separately. No recovery issues freshness.','authority_effect':'none'})
