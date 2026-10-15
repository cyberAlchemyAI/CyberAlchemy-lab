"""Actual selected stdio Session interruption, historical retry and cold metadata proof."""
import argparse,base64,copy,hashlib,importlib.util,json,os,selectors,signal,subprocess,sys,tempfile,time
from pathlib import Path
from contextlib import ExitStack
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
checks=[];children=[];bindings=[];frames={}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def require(v,name):
 checks.append({'name':name,'result':'PASS' if v else 'FAIL'})
 if not v:raise AssertionError(name)
def emit(p,v,raw=None):
 p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(encoded(v) if raw is None else raw)
 bindings.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p)})
def load_api(base):
 name='_cal_'+base.name.replace('-','_');spec=importlib.util.spec_from_file_location(name,base/'__init__.py',submodule_search_locations=[str(base)])
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 return __import__(name+'.run_session_checks',fromlist=['Sessions'])
class Child:
 def __init__(self,name,key,policy,pin,api,profile,out):
  self.name=name;self.policy=policy;self.frames=[];self.api=api;self.out=out
  self.err=open(out/(name+'.stderr'),'xb');os.chmod(out/(name+'.stderr'),0o600)
  self.p=subprocess.Popen([sys.executable,str(api/'serve.py'),'--policy',str(policy),'--policy-sha256',pin,'--protocol-profile-sha256',profile],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err)
  self.sel=selectors.DefaultSelector();self.sel.register(self.p.stdout,selectors.EVENT_READ);self.stopped=False
  challenge=self.receive();self.send(K.proof(key,challenge));self.auth=self.receive()
  require(self.auth['schema_version']=='lab-local-reader-authenticated/v1-candidate',name+': nonce signature authenticated actual process')
  self.context=self.auth['context']
 def send(self,raw):
  self.frames.append({'direction':'request','sha256':K.source.sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()});self.p.stdin.write(raw+b'\n');self.p.stdin.flush()
 def receive(self):
  # Bounded observation inside the producer; the parent tool is polled separately.
  if not self.sel.select(timeout=180):raise TimeoutError(self.name+': response observation exceeded 180 seconds')
  raw=self.p.stdout.readline().removesuffix(b'\n')
  if not raw:raise RuntimeError(self.name+': child closed before complete response')
  self.frames.append({'direction':'response','sha256':K.source.sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()});return K.frame_parse(raw)
 def invoke(self,c):
  raw=K.compact(c);self.send(raw);r=self.receive();require(SCHEMAS.valid('api-reply',r),self.name+': actual reply original schema')
  require(r['request_binding']['sha256']==K.source.sha(raw),self.name+': exact outer wire binding')
  require(r['contract_profile_binding']==SCHEMAS.profile_binding,self.name+': selected profile binding');return r
 def result(self,c):
  r=self.invoke(c);require(r['kind']=='result',self.name+': requested result '+c['operation']);return r['message']
 def stop(self,kill=False):
  if self.stopped:return
  if kill:self.p.kill()
  else:self.p.stdin.close()
  code=self.p.wait(timeout=60);self.stopped=True;self.err.close();self.sel.close();self.p.stdout.close()
  if kill:self.p.stdin.close()
  children.append({'name':self.name,'pid':self.p.pid,'exit_code':code,'terminal_observed':True,'intentional_interruption':kill})
  emit(self.out/(self.name+'.json'),{'schema_version':'lab-original-wire-transcript/v1-candidate','frames':self.frames,'authority_effect':'none'})
  require(code==(-signal.SIGKILL if kill else 0),self.name+': expected terminal process code')
  policy=K.source.parse(self.policy.read_bytes());workspace=Path(policy['workspace']['root'])
  for p in sorted(workspace.rglob('*.json')):
   raw=p.read_bytes();K.privacy(K.source.parse(raw));emit(self.out/(self.name+'-evidence')/p.relative_to(workspace),None,raw)
def outer(child,operation,message=None,**changes):
 c=K.call(child.context,'lab.status',CUT);c['operation']=operation
 if message is not None:c['message']=message
 c.update(changes);return c
def get_delivery(child,view):
 actor={**{k:child.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')},'role_assignment_refs':child.context['role_assignment_bindings']}
 q=K.D.query(view.fresh_signed_sources,SimpleNamespace(actor=lambda:actor));q['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
 return child.result(outer(child,'context.get',q))
def opening(child,view,delivery,key):
 selected=view.fresh_signed_sources;ref=lambda identity:selected.sources.resolve(identity+'@'+K.R.VERSION)[0].artifact
 c=outer(child,'session.open');actor=c['message']['actor'];budget=c['message']['budget'];budget['max_actions']=1
 c.update(idempotency_key=key,message={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:process-open:'+K.uuid.uuid4().hex,'actor':actor,
  'assignment':ref(K.R.ASSIGNMENT),'profile':ref(K.R.PROFILE),'implementation':ref(K.R.IMPLEMENTATION),'capabilities':[ref(K.R.CAPABILITY)],
  'context_delivery_binding':K.binding('context-delivery:'+delivery['context_view']['version_ref'],K.compact(delivery)),
  'authority_envelope_binding':K.binding('host-policy-sha256:'+POLICY_PIN,POLICY.read_bytes()),'source_cut':copy.deepcopy(CUT),'budget':budget,
  'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'})
 return c
def inspect(child,sid):
 c=outer(child,'session.inspect');c['message'].update(schema_version='lab-session-inspect-request/v1-candidate',session_ref=sid);c['message'].pop('scope_refs');c['message'].pop('source_cut');return c
def closing(child,opened,state):
 return outer(child,'session.close',{'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:process-close:'+K.uuid.uuid4().hex,
  'session_ref':opened['session_ref'],'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':state['last_receipt_binding'],
  'requested_at':K.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'},idempotency_key='close:'+K.uuid.uuid4().hex)
def retry(child,request):
 c=copy.deepcopy(request);c['call_id']='call:cold:'+K.uuid.uuid4().hex;c['caller_context_ref']=child.context['context_ref'];return c
def event_count(workspace):return len(list((workspace/'journal').glob('session-*.json')))
def main():
 global K,SCHEMAS,CUT,POLICY,POLICY_PIN
 p=argparse.ArgumentParser();p.add_argument('--api-directory',required=True);p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);p.add_argument('--producer-sha256',required=True);a=p.parse_args()
 require(digest(HERE/'source-manifest.json')==a.producer_sha256,'independent process producer source pin')
 source_manifest=json.loads((HERE/'source-manifest.json').read_bytes())
 for row in source_manifest['files']:require(digest(ROOT/row['path'])==row['sha256'],'process source file '+row['path'])
 api=(ROOT/a.api_directory).resolve();require(api.parent==HERE.parent,'selected candidate API directory boundary');require(digest(api/'source-manifest.json')==a.source_sha256,'selected API source pin')
 for row in json.loads((api/'source-manifest.json').read_bytes())['files']:require(digest(ROOT/row['path'])==row['sha256'],'selected original source '+row['path'])
 K=load_api(api);SCHEMAS=K.Schemas(a.profile_sha256);out=HERE/'receipts/0001';out.mkdir(parents=True,exist_ok=False,mode=0o700)
 outcome={'result':'FAIL','task_complete':False,'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'private_keys_exported':False,'short_memory_exported':False,'claim_ceiling':'Actual owned source-reader Session process and candidate metadata proof only; no complete Product or plan.'};live=[];owned=[]
 try:
  with ExitStack() as stack:
   view=stack.enter_context(K.source.replay_source('fresh-participation'));CUT=K.cut(view);materials,metadata,_=K.materials_for(view)
   root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-Session-process-')));root.chmod(0o700);owned.append(str(root))
   key,POLICY,POLICY_PIN=K.provision(root,'fresh-participation',materials,metadata,principal=K.R.PRINCIPAL);workspace=root/'workspace'
   warm=Child('interrupted-active',key,POLICY,POLICY_PIN,api,a.profile_sha256,out);live.append(warm);stack.callback(lambda: warm.stop(kill=True))
   delivery=get_delivery(warm,view);request=opening(warm,view,delivery,'process:interrupted-active');opened=warm.result(request)
   state=warm.result(inspect(warm,opened['session_ref']));require(state['posture']=='active','actual live Session observed before interruption')
   warm.stop(kill=True);live.remove(warm)
   cold=Child('cold-observer',key,POLICY,POLICY_PIN,api,a.profile_sha256,out);live.append(cold);stack.callback(lambda: cold.stop(kill=True))
   lost=cold.result(inspect(cold,opened['session_ref']));require(lost['posture']=='indeterminate' and lost['ended_at'] is None and not lost['short_memory_in_response'],'cold lost process does not infer disposal or rehydrate memory')
   count=event_count(workspace);same=cold.result(retry(cold,request));require(same==opened and event_count(workspace)==count,'cold same key retains historical outcome with no resource creation')
   unchanged=cold.result(inspect(cold,opened['session_ref']));require(unchanged['posture']=='indeterminate','historical retry does not restore live Session')
   changed=retry(cold,request);changed['message']['request_ref']='request:changed-original-opening';conflict=cold.invoke(changed);require(conflict['kind']=='error' and conflict['message']['code']=='idempotency-conflict','cold changed input same key refuses')
   denied=cold.invoke(closing(cold,opened,lost));require(denied['kind']=='error' and denied['message']['code']=='recovery-required','lost Session cannot fabricate close/disposal receipt')
   fresh_delivery=get_delivery(cold,view);new_request=opening(cold,view,fresh_delivery,'process:new-after-loss');new=cold.result(new_request)
   require(new['session_ref']!=opened['session_ref'] and new['agent_instance_ref']!=opened['agent_instance_ref'],'new Session has fresh Machine and Session identities')
   new_state=cold.result(inspect(cold,new['session_ref']));closed=cold.result(closing(cold,new,new_state));require(closed['discarded_memory'] and closed['agent_identity_reuse_allowed'] is False,'actual explicit close observes disposal and forbids identity reuse')
   eof_request=opening(cold,view,get_delivery(cold,view),'process:EOF-owned');eof=cold.result(eof_request);require(cold.result(inspect(cold,eof['session_ref']))['posture']=='active','actual Session held before EOF')
   cold.stop();live.remove(cold)
   observer=Child('cold-after-EOF',key,POLICY,POLICY_PIN,api,a.profile_sha256,out);live.append(observer);stack.callback(lambda: observer.stop(kill=True))
   for result in (new,eof):
    observed=observer.result(inspect(observer,result['session_ref']));require(observed['posture']=='closed' and observed['ended_at'] is not None and not observed['short_memory_in_response'],'cold retains verified terminal metadata without memory')
   require(observer.result(inspect(observer,opened['session_ref']))['posture']=='indeterminate','unobserved interrupted disposal remains explicit after later work')
   observer.stop();live.remove(observer);view.fresh_signed_sources.guard()
  require(all(not Path(p).exists() for p in owned),'all owned workspaces, policies and transport keys removed')
  outcome['result']='PASS';outcome['owned_fixture_roots_removed']=True
 except BaseException as error:
  outcome['failure']=str(error)
  for child in live:
   try:child.stop(kill=True)
   except BaseException:pass
 outcome.update(checks=checks,children=children,files=bindings,api_source_binding={'path':str((api/'source-manifest.json').relative_to(ROOT)),'sha256':a.source_sha256},profile_binding={'path':str((api/'contract-profile.json').relative_to(ROOT)),'sha256':a.profile_sha256})
 emit(out/'result.json',outcome);print(json.dumps({'result':outcome['result'],'checks':len(checks),'children':len(children),'failure':outcome.get('failure')}),flush=True)
 return 0 if outcome['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
