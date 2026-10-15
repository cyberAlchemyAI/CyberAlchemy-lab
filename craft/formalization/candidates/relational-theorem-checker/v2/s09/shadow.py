"""Immutable candidate snapshots and cooperative local shadow application; no authority transition."""
from pathlib import Path
import sys,copy,json,time,tempfile,os,fcntl
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'s06'));import runtime as r
sys.path.insert(0,str(BASE/'s07'));import stress_adapter as stress
s=r.s

def runtime_bindings():return [s.binding(p) for _,p in r.module_list()]+[s.binding(r.HERE/'runtime.py'),s.binding(HERE/'shadow.py'),s.binding(BASE/'s05/adapter.py'),s.binding(BASE/'s07/stress_adapter.py'),s.binding(BASE/'s07/interpretation.schema.json')]
def immutable(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
 try:
  with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 except FileExistsError:s.require(path.read_bytes()==raw,'immutable snapshot collision/drift')
 return s.binding(path)
def head(store):
 p=Path(store)/'HEAD.json';s.require(p.is_file(),'shadow baseline uninitialized');h=s.read(p);s.check(h['snapshot']);s.check(h['registration']);s.require(h['identity']==s.identity(s.read(s.check(h['snapshot']))),'pointer/snapshot mismatch');return h

def register(snapshot,store,build=None):
 store=Path(store).resolve();s.require(store.is_relative_to(HERE/'runs'),'shadow store must stay in the local v2 candidate runs directory');store.mkdir(parents=True,exist_ok=True);id=s.identity(snapshot)
 checked=r.qualify(r.proposal(snapshot,snapshot,'register-'+id[:16]),build)
 s.require(checked['status']=='qualified-candidate','baseline not qualified')
 src=immutable(store/'snapshots'/(id+'.json'),snapshot)
 receipt={'schema':'relational.baseline-registration/v2','baseline_identity':id,'snapshot':src,'required_inventory':[o['id'] for o in r.ext.c.obligations('register')],'qualified_by':'stronger exact 20-obligation identity-extension replay including complete selected closure','qualification':checked,'human_review':'pending','authority_effect':'none'}
 # Registration proof evidence is immutable and bound to this exact snapshot.
 dest=store/'registrations'/(id+'-'+s.identity(checked)[:16]+'.json');ref=immutable(dest,receipt)
 return {'identity':id,'snapshot':src,'registration':ref}
def initialize(snapshot,store,build=None):
 store=Path(store);record=register(snapshot,store,build)
 with (store/'LOCK').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);immutable(store/'HEAD.json',record)
 return record

def review(proposal,store,mappings=(),label='candidate-review'):
 current=head(store);s.require(proposal['baseline_identity']==current['identity'],'proposal not based on current registered snapshot')
 before=s.read(s.check(current['snapshot']));s.require(proposal['before']==before,'before-state snapshot substitution')
 r.ext.classify(before,proposal['after']);r.resource.preflight(proposal['after']);r.ext.c.reference_stability(before['graph'],proposal['after']['graph'])
 envelope={'schema':'relational.shadow-review/v2','label':label,'before':current,'proposal_identity':s.identity(proposal),'mappings_identity':s.identity(list(mappings)),'runtime_bindings':runtime_bindings(),'human_review':'pending','authority_effect':'none'}
 envelope['review_identity']=s.identity(envelope);return envelope

def validate_review(record,proposal,store,mappings):
 s.require(record['review_identity']==s.identity({k:v for k,v in record.items() if k!='review_identity'}),'review envelope drift')
 s.require(record['before']==head(store),'old baseline/review receipt; current snapshot differs')
 s.require(record['proposal_identity']==s.identity(proposal) and record['mappings_identity']==s.identity(list(mappings)),'proposal/condition/interpretation/context drift')
 s.require(record['runtime_bindings']==runtime_bindings(),'verifier/profile/transport policy drift')
 for b in record['runtime_bindings']:s.check(b)
 r.ext.c.reference_stability(proposal['before']['graph'],proposal['after']['graph'])
 r.ext.classify(proposal['before'],proposal['after'])

def apply(record,proposal,store,mappings=(),build=None):
 store=Path(store);validate_review(record,proposal,store,mappings)
 start=time.monotonic();qualified=r.qualify(proposal,build);mapping_results=[stress.evaluate(q,store/'stress-build') for q in mappings]
 for q,out in zip(mappings,mapping_results):
  s.require(out['status']=='yes','required composed mapping not yes')
  if q['operation']=='inheritance':s.require(out['condition_status']=='yes','required active norm context unknown/false/conflicting')
 # Replay registration on the successor as an independent before-state. The previous
 # proposal result cannot serve as its registration receipt.
 registered=register(proposal['after'],store,build)
 with (store/'LOCK').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);validate_review(record,proposal,store,mappings)
  for q,out in zip(mappings,mapping_results):
   s.require(out['request_identity']==s.identity(q),'mapped request changed during replay')
   for m in out['kernel_evidence']:s.check(m['source']);s.check(m['olean'])
  r.validate_receipt(proposal,qualified)
  pending=store/('HEAD.'+registered['identity']+'.tmp');s.write(pending,registered)
  with pending.open('rb') as f:os.fsync(f.fileno())
  os.replace(pending,store/'HEAD.json')
  s.require(head(store)==registered,'indeterminate: noncooperating writer changed pointer after publish; retain snapshots and reconcile')
 out={'schema':'relational.shadow-application/v2','status':'applied-candidate-shadow','review_identity':record['review_identity'],'before':record['before'],'after':registered,'qualification':qualified,'mapped_results':mapping_results,'contexts':{'horn':s.identity(proposal['before']['context']),'mapped':[o['context_identity'] for o in mapping_results]},'composition_policy':'individually qualified contexts; no truth merging across different contexts/epochs','seconds':time.monotonic()-start,'human_review':'pending','authority_effect':'none','locking_limits':'advisory local cooperating writers only; a noncooperating writer can race final check/rename; postcheck reports indeterminate and retains immutable snapshots'}
 immutable(store/'applications'/(s.identity(out)+'.json'),out);return out

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['initialize','review','apply']);p.add_argument('input',type=Path);p.add_argument('--store',type=Path,required=True);args=p.parse_args()
 try:
  obj=s.read(args.input)
  if args.operation=='initialize':out=initialize(obj,args.store)
  elif args.operation=='review':out=review(obj,args.store)
  else:out=apply(obj['review'],obj['proposal'],args.store,obj.get('mappings',[]))
  print(json.dumps(out,indent=2));return 0
 except (r.resource.Exhausted,__import__('subprocess').TimeoutExpired) as ex:print(json.dumps({'status':'unknown-resource','reason':str(ex),'authority_effect':'none'}));return 3
 except Exception as ex:print(json.dumps({'status':'blocked','reason':str(ex).splitlines()[0],'authority_effect':'none'}));return 5
if __name__=='__main__':sys.exit(main())
