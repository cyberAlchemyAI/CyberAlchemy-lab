"""Actual crash/recovery and mediated writer probes, with no kernel claims."""
from pathlib import Path
import copy
import json
import os
import sqlite3
import subprocess
import sys
import threading
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p08.metadata import Store,Cancelled,encoded
sys.path.insert(0,str(BASE/'execution'));import support as s
request=s.read(BASE/'p01/request-fixture.json');before=request['proposal']['before'];after=request['proposal']['after']
controls=[];cases=[]
def check(name,ok):s.require(ok,name);controls.append({'name':name,'result':'pass'})
def new(label):return Store.initialize(HERE/'stores'/(label+'-'+uuid.uuid4().hex),before,store_kind='io-probe-unqualified')
def external_write(path,raw):
    s.require(path.resolve().is_relative_to(HERE/'stores'),'test edit outside owned fixture stores')
    # An equivalent-privilege external owner can change permissions. The
    # mediated readonly policy is not claimed to exclude that writer.
    os.chmod(path,0o600);path.write_bytes(raw)
def raw_head(store):
    db=sqlite3.connect(store.root/'metadata.db')
    try:return json.loads(db.execute('SELECT value FROM head WHERE id=1').fetchone()[0])
    finally:db.close()
for stage in ['journal','snapshot','registration','metadata-head','mirror']:
    store=new('crash-'+stage);initial=store.head()
    result=subprocess.run([sys.executable,str(HERE/'crash_probe.py'),str(store.root),stage],capture_output=True,text=True,timeout=10)
    check('actual-process-crash-'+stage,result.returncode==91)
    current=store.recover();check('explicit-recovery-'+stage,current['status']=='head-current')
    expected=1 if stage in ['metadata-head','mirror'] else 0
    check('authoritative-generation-preserved-'+stage,current['head']['generation']==expected)
    events={e['kind'] for e in current['events']}
    if expected==0:check('uncommitted-journal-aborted-'+stage,'aborted-prepared' in events)
    if stage=='metadata-head':check('recorded-mirror-window-repaired','repaired-mirror' in events)
    check('crash-probe-has-no-fresh-qualification-'+stage,not current['fresh_qualification'] and current['proof_scope']=='io-probe-unqualified')
    cases.append({'stage':stage,'exit_code':result.returncode,'store':str(store.root.relative_to(s.ROOT)),'recovery':current})
store=new('cooperating-race');head=store.head();barrier=threading.Barrier(2);results=[]
def competitor():
    barrier.wait()
    results.append(store._publish(before=head,after_baseline=after,
                   registration_evidence={'proof_mode':'io-probe-unqualified','request':None,'qualification':None,'completion':None,'owned_run':None,'required_inventory':[],'fresh_at_creation':False},
                   review=None,proposal_qualification=None,fresh_run_id='io-race-'+uuid.uuid4().hex))
threads=[threading.Thread(target=competitor) for _ in range(2)]
for t in threads:t.start()
for t in threads:t.join()
check('one-cooperating-metadata-publisher-wins',sorted(r['status'] for r in results)==['committed-io-probe','stale-head'] and store.head()['generation']==1)
store=new('postcommit-head-conflict');store.probe(after);published=raw_head(store)
external_write(store.root/'HEAD.json',b'externally changed HEAD')
recovered=store.recover()
check('external-head-conflict-reconciliation',recovered['status']=='reconciliation-required')
check('external-head-conflict-does-not-rollback',raw_head(store)==published)
store=new('completed-old-head-rollback');old=store.head();store.probe(after)
external_write(store.root/'HEAD.json',encoded(old))
check('known-old-mirror-outside-window-not-auto-repaired',store.recover()['status']=='reconciliation-required' and raw_head(store)['generation']==1)
store=new('missing-committed-registration');result=store.probe(after);path=s.ROOT/result['after']['registration']['path'];path.rename(path.with_suffix('.retained'))
check('missing-committed-artifact-reconciliation',store.recover()['status']=='reconciliation-required')
check('missing-committed-artifact-preserves-head',raw_head(store)['generation']==1)
store=new('prepared-artifact-drift')
result=subprocess.run([sys.executable,str(HERE/'crash_probe.py'),str(store.root),'snapshot'],capture_output=True,text=True,timeout=10)
snap=next(p for p in (store.root/'snapshots').glob('*.json') if p.name!='genesis.json')
external_write(snap,b'changed completed snapshot')
check('recorded-durable-prepared-artifact-conflict',result.returncode==91 and store.recover()['status']=='reconciliation-required' and raw_head(store)['generation']==0)
store=new('cancellation');cancel=threading.Event()
try:
    store.probe(after,cancel=cancel,fault=lambda at:cancel.set() if at=='registration' else None)
    raise ValueError('cancelled registration was committed')
except Cancelled:pass
check('cancel-after-registration-leaves-head-unchanged',raw_head(store)['generation']==0 and store.recover()['head']['generation']==0)
store=new('precommit-external-head')
def external(at):
    if at=='registration':
        external_write(store.root/'HEAD.json',b'external precommit conflict')
try:
    store.probe(after,fault=external)
    raise ValueError('external precommit edit was accepted')
except Exception as e:s.require('external mirror edit' in str(e),'unexpected precommit outcome '+str(e))
check('external-precommit-edit-refuses-and-preserves-head',raw_head(store)['generation']==0 and store.recover()['status']=='reconciliation-required')
store=new('wrong-store-owner');owner=s.read(store.root/'owner.json');owner['root']='outside/wrong-store'
external_write(store.root/'owner.json',encoded(owner))
try:Store(store.root);raise ValueError('wrong store owner accepted')
except Exception as e:s.require('owner/root mismatch' in str(e),'unexpected owner outcome')
check('store-owner-transplant-refused',True)
s.write(HERE/'metadata-controls.json',{'result':'pass','controls':controls,'actual_process_crashes':cases,'actual_fresh_kernel_qualifications':0,'scope':'Mediated transactional IO probes only; full fresh proposal/successor registration integration remains required.','authority_effect':'none'})
print('P08 metadata-only controls passed: '+str(len(controls)),flush=True)
