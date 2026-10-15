"""Instrumented diagnosis only; never a qualification or authority grant."""
import copy,fcntl,hashlib,importlib,importlib.util,json,os,sys,tempfile,time,uuid
from contextlib import ExitStack
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v13'
RUNTIME=BASE/'source8-session-runtime-v1-action-0148'
SOURCE='213ebd20742b8f7c8af0aa6614b71f735d574e89d22c92c094c3657c0d189322'
PROFILE='73d832dcec7776f6a8a3064ac9c11a60ba086c6802bb81c159058dcea9d692b2'
REPORT=RUN/'Source8-session-open-api13-diagnostic-action-0148.json'
EVENTS=RUN/'Source8-session-open-api13-diagnostic-action-0148.events.jsonl'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def bootstrap(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
def main():
 assert not REPORT.exists() and not EVENTS.exists(),'immutable prior diagnostic retained'
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 fcntl.flock(fd,fcntl.LOCK_SH);started=time.monotonic();trace_rows=[];seen=set();public=[];roots=[];exit_guard=False
 def tracing(frame,event,arg):
  if event=='exception':
   p=Path(frame.f_code.co_filename)
   if p.is_absolute() and p.is_relative_to(ROOT) and p.suffix=='.py':
    typ=arg[0];row={'file':str(p.relative_to(ROOT)),'function':frame.f_code.co_name,'line':frame.f_lineno,'exception_class':typ.__module__+'.'+typ.__qualname__}
    key=tuple(row.values())
    if key not in seen and len(trace_rows)<2000:seen.add(key);trace_rows.append(row)
  return tracing
 try:
  assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
  package='_cal_Source8_session_diagnostic_0239';bootstrap(package,API)
  G=importlib.import_module(package+'.guard');G.verify(SOURCE)
  provider='_cal_Source8_session_diagnostic_provider_0239';bootstrap(provider,RUNTIME)
  H=importlib.import_module(provider+'.provider');M=H.modules(package);P=M['protocol'];schemas=P.Schemas(PROFILE)
  D=P.source.source8_delivery_for('source8-session-participation')
  with ExitStack() as stack:
   selected=stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE));view=selected.view
   view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
   materials,_=H.lesson_materials(M,D,selected)
   root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-source8-session-diagnostic-0239-')));root.chmod(0o700);roots.append(str(root))
   key,policy,pin=H.provision(M,root,D,selected,'source8-session-participation',materials)
   channel=M['auth'].ReaderChannel(policy,pin,schemas);channel.authenticate(M['fixtures'].proof(key,channel.challenge))
   service=M['service'].Service(view,channel,schemas);stack.callback(service.close)
   dispatcher=importlib.import_module(package+'.integration_dispatch').IntegrationService(service)
   sys.settrace(tracing)
   message=D.query(selected,service.sessions.bridge)
   raw=P.compact(H.call(M,service,'context.get',message));response=dispatcher.call(raw)
   public.append({'operation':'context.get','raw_request':P.frame_parse(raw),'raw_request_sha256':P.source.sha(raw),'reply':response})
   with EVENTS.open('x') as stream:stream.write(json.dumps(public[-1],sort_keys=True)+'\n')
   assert response.get('kind')=='result','actual context.get refused'
   delivery=response['message'];ref=lambda i:copy.deepcopy(selected.sources.resolve(i+'@'+D.records.VERSION)[0].artifact)
   budget=copy.deepcopy(message['budget']);budget['max_actions']=1
   runtime=importlib.import_module(type(service.sessions).__module__)
   message={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:Source8-diagnostic-open:'+uuid.uuid4().hex,
    'actor':service.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),
    'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],
    'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),
    'authority_envelope_binding':runtime.stable_policy(service.channel),'source_cut':selected.source_cut,'budget':budget,
    'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
   raw=P.compact(H.call(M,service,'session.open',message,key='Source8:diagnostic-open:'+uuid.uuid4().hex));opened=dispatcher.call(raw)
   public.append({'operation':'session.open','raw_request':P.frame_parse(raw),'raw_request_sha256':P.source.sha(raw),'reply':opened})
   with EVENTS.open('a') as stream:stream.write(json.dumps(public[-1],sort_keys=True)+'\n')
   sys.settrace(None);key=None
   status='actual-session-result' if opened.get('kind')=='result' else 'actual-session-refusal'
 except BaseException as error:
  sys.settrace(None);status='diagnostic-error';diagnostic_error={'exception_class':type(error).__module__+'.'+type(error).__qualname__}
 finally:
  sys.settrace(None)
  try:
   if 'G' in locals():G.verify(SOURCE);exit_guard=True
  finally:
   result={'schema_version':'lab-instrumented-Source8-session-diagnostic/v1-candidate','status':locals().get('status','diagnostic-error'),
    'qualification':False,'instrumentation':'exception class/file/function/line only; no locals, values, private grants or keys',
    'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
    'caller_binding':bind(Path(__file__).resolve()),'provider_binding':bind(RUNTIME/'source-manifest.json'),
    'public_calls_recorded':len(public),'exception_origins':trace_rows,'trace_truncated':len(trace_rows)>=2000,
    'full_exit_guard':exit_guard,'owned_roots_absent':all(not Path(r).exists() for r in roots),
    'duration_seconds':time.monotonic()-started,'diagnostic_error':locals().get('diagnostic_error'),
    'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
   with REPORT.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'status':result['status'],'report_binding':bind(REPORT)}),flush=True)
 return 0 if exit_guard and result['owned_roots_absent'] and public else 1
if __name__=='__main__':raise SystemExit(main())
