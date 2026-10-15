"""Real stage timing and exception origins; instrumented, not qualification."""
import fcntl,hashlib,importlib,importlib.util,json,os,sys,tempfile,time
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v14';RUNTIME=BASE/'source8-session-runtime-v1-action-0148'
SOURCE='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
PROFILE='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
def main():
 report=OUT/'report.json';event_path=OUT/'events.jsonl';assert not report.exists() and not event_path.exists()
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 start=time.monotonic();stages=[];exceptions=[];seen=set();roots=[];exit_guard=False;current=None
 def emit(row):
  with event_path.open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
 def trace(frame,event,arg):
  if event=='exception':
   p=Path(frame.f_code.co_filename)
   if p.is_absolute() and p.is_relative_to(ROOT) and p.suffix=='.py':
    typ=arg[0];row={'event':'exception','stage':current,'file':str(p.relative_to(ROOT)),'function':frame.f_code.co_name,'line':frame.f_lineno,'exception_class':typ.__module__+'.'+typ.__qualname__}
    key=tuple(row.values())
    if key not in seen and len(exceptions)<3000:seen.add(key);exceptions.append(row);emit(row)
  return trace
 def stage(name,call):
  nonlocal current
  current=name;at=time.monotonic();row={'event':'stage','stage':name,'phase':'started','UTC':datetime.now(timezone.utc).isoformat(),'monotonic_seconds':at-start};emit(row)
  try:return call()
  finally:
   end=time.monotonic();row={'event':'stage','stage':name,'phase':'finished','UTC':datetime.now(timezone.utc).isoformat(),'monotonic_seconds':end-start,'duration_seconds':end-at};stages.append(row);emit(row)
 try:
  assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
  package='_cal_Source8_stage_diagnostic_0250';load(package,API)
  G=importlib.import_module(package+'.guard');stage('full-source-entry',lambda:G.verify(SOURCE))
  pn='_cal_Source8_stage_provider_0250';load(pn,RUNTIME);H=importlib.import_module(pn+'.provider');M=H.modules(package);P=M['protocol']
  schemas=stage('Schemas',lambda:P.Schemas(PROFILE));D=stage('Source8-delivery-selection',lambda:P.source.source8_delivery_for('source8-session-participation'))
  cn='_cal_Source8_stage_original_caller_0250';file=RUN/'source8-common-0244/qualify.py';spec=importlib.util.spec_from_file_location(cn,file);Q=importlib.util.module_from_spec(spec);sys.modules[cn]=Q;spec.loader.exec_module(Q);Q.EVENT_PATH=OUT/'public-calls.jsonl'
  with ExitStack() as stack:
   selected=stage('real-reader.open_signed',lambda:stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE)));view=selected.view
   view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
   materials,_=stage('independent-Lesson-materials',lambda:H.lesson_materials(M,D,selected))
   root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-source8-stage-diagnostic-0250-')));root.chmod(0o700);roots.append(str(root))
   key,policy,pin=stage('fresh-private-provision',lambda:H.provision(M,root,D,selected,'source8-session-participation',materials))
   channel=stage('ReaderChannel-constructor',lambda:M['auth'].ReaderChannel(policy,pin,schemas));stage('reader-authenticate',lambda:channel.authenticate(M['fixtures'].proof(key,channel.challenge)))
   service=stage('Service-constructor',lambda:M['service'].Service(view,channel,schemas));stack.callback(service.close)
   dispatcher=importlib.import_module(package+'.integration_dispatch').IntegrationService(service);public=[]
   delivery,opened,raw=stage('actual-Context+Session-opening',lambda:Q.opening(H,M,service,D,dispatcher,'source8-session-participation',public))
   sid=opened['message']['session_ref'];emit({'event':'actual-lease','started_at':opened['message']['started_at'],'expires_at':opened['message']['expires_at'],'UTC':datetime.now(timezone.utc).isoformat()})
   parent=bind(API/'source-manifest.json');sys.settrace(trace)
   peer=stage('Machine.select',lambda:M['machine_transport'].select(service,sid,parent));stack.callback(peer.close)
   proof=stage('Machine.proof',peer.proof)
   stage('Machine.authenticate',lambda:peer.authenticate(proof))
   machine=stage('Machine-common-dispatcher',lambda:importlib.import_module(package+'.integration_dispatch').IntegrationService(peer.service))
   query=stage('Machine-query',lambda:D.query(selected,peer.service.sessions.bridge))
   wire=stage('Machine-call-envelope',lambda:P.compact(H.call(M,peer.service,'lesson.select',query)))
   reply=stage('lesson.select',lambda:Q.invoke(machine,wire,public));sys.settrace(None)
   status='actual-machine-result' if reply.get('kind')=='result' else 'actual-machine-refusal';key=None
 except BaseException as error:
  sys.settrace(None);status='diagnostic-exception';failure_class=type(error).__module__+'.'+type(error).__qualname__
 finally:
  sys.settrace(None)
  try:
   if 'G' in locals():stage('full-source-exit',lambda:G.verify(SOURCE));exit_guard=True
  finally:
   result={'schema_version':'lab-Source8-stage-diagnostic/v1-candidate','status':locals().get('status'),'qualification':False,
    'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'caller_binding':bind(Path(__file__).resolve()),
    'stages':stages,'exception_origins':exceptions,'exception_trace_truncated':len(exceptions)>=3000,'failure_class':locals().get('failure_class'),
    'full_exit_guard':exit_guard,'owned_roots_absent':all(not Path(p).exists() for p in roots),'duration_seconds':time.monotonic()-start,
    'instrumentation':'monotonic/UTC stages and exception classes/files/functions/lines only; no locals, private policy values or keys',
    'authority_effect':'none','actual_owner_outcome':None}
   with report.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'status':result['status'],'report_binding':bind(report)}),flush=True)
 return 0 if exit_guard and result['owned_roots_absent'] else 1
if __name__=='__main__':raise SystemExit(main())
