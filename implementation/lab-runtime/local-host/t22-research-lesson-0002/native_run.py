"""Actual final-73 Session consuming a privately reviewed research candidate.

The new caller computes on public historical W04 evidence. It does not replace
Lab callbacks, assert Source-current candidate Lesson admission or dispatch a
Tool. Original Source-controlled Lesson selection/preflight is diagnosed apart.
"""
import copy,hashlib,importlib,importlib.util,json,os,shutil,sys,tempfile,time,traceback,uuid
from contextlib import ExitStack
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
INSTALL=Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001');sys.path.insert(0,str(INSTALL/'deps'));sys.path.insert(0,str(HERE))
import consumer as C
import margin_inputs as MI
import diagnose_controlled_preflight as DIAG
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
SOURCE='5127caa2d6a829303f12af398912eeb98bb2b52580af40614e4925080224f4e7'
PROFILE='131fdcaafdf59c082546fdf94567fc7f39cc09d302466866f83b2d06eeccb6c5'
REVIEW_SHA='e925d93d681d12ebd404f03773076cc2b6e4f4fb4c2c1862dc80f3dd10efd03a'
T03=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001'
EVENTS=HERE/'native-events-0001.jsonl'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(value,reason):
 if not value:raise ValueError(reason)
def event(value):
 with EVENTS.open('a') as f:f.write(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),**value},sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def write(path,value):
 raw=C.encoded(value);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def load_path(path,name):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
 require(not EVENTS.exists(),'retain prior native attempt')
 provenance=json.loads((HERE/'provenance.json').read_bytes());lesson_raw=(HERE/'candidate-lesson.json').read_bytes();review_raw=(HERE/'private-review-0001.json').read_bytes()
 require(sha(review_raw)==REVIEW_SHA and sha(lesson_raw)==provenance['candidate_lesson_sha256'],'independently reviewed candidate changed')
 review_header=json.loads(review_raw)
 bindings=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in [Path(__file__).resolve(),HERE/'consumer.py',HERE/'diagnose_controlled_preflight.py',HERE/'margin_inputs.py',HERE/'provenance.json',HERE/'candidate-lesson.json',HERE/'private-review-0001.json',T03/'lesson_v53_provider.py']]
 bindings.extend(provenance['source_inputs'])
 bindings.extend(review_header['review_evidence_bindings'])
 require(all(sha((ROOT/b['path']).read_bytes())==b['sha256'] for b in bindings),'selected caller/public evidence bytes differ')
 name='_t22_research_native_'+uuid.uuid4().hex
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
 load=lambda leaf:importlib.import_module(name+'.'+leaf)
 P,F,S,H,A,MT=[load(x) for x in ('protocol','fixtures','service','handlers','auth','machine_transport')]
 load('guard').verify(SOURCE);schemas=P.Schemas(PROFILE);schemas.guard()
 require(sha((API/'source-manifest.json').read_bytes())==SOURCE and sha((API/'contract-profile.json').read_bytes())==PROFILE,'exact final API selection differs')
 D=load('current_legacy_context_sessions').D;R=D.records
 provider=load_path(T03/'lesson_v53_provider.py','_t22_provider_'+uuid.uuid4().hex);M=provider.modules(name)
 def stage(label,work):
  event({'phase':label,'state':'starting'});at=time.monotonic()
  try:value=work()
  except BaseException as error:event({'phase':label,'state':'failed','exception_class':type(error).__name__,'message':str(error)[:500],'seconds':round(time.monotonic()-at,3)});raise
  event({'phase':label,'state':'passed','seconds':round(time.monotonic()-at,3)});return value
 started=time.monotonic()
 with ExitStack() as stack:
  view=stage('source-replay',lambda:stack.enter_context(P.source.replay_source(P.source.CURRENT_LEGACY_NAME)));selected=view.custody_signed_sources
  require(selected is view.legacy_signed_sources and selected.source_cut==H.cut(view),'selected final native Source differs')
  materials,plan=stage('Source-controlled-one-Lesson-plan',lambda:provider.lesson_materials(M,D,selected))
  private={}
  for leaf in ('candidate-lesson.json','private-review-0001.json','provenance.json'):private['private:T22:'+leaf]=(HERE/leaf).read_bytes()
  for index,b in enumerate(provenance['source_inputs']):private['private:T22:public-evidence:'+str(index)]=(ROOT/b['path']).read_bytes()
  materials.update(private)
  root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-T22-research-native-')));root.chmod(0o700)
  key,path,pin=stage('private-scoped-reader-provision',lambda:provider.provision(M,root,D,selected,P.source.CURRENT_LEGACY_NAME,materials))
  channel=stage('reader-channel',lambda:A.ReaderChannel(path,pin,schemas));stack.callback(channel.close)
  stage('reader-authentication',lambda:channel.authenticate(F.proof(key,channel.challenge)));key=None
  host=stage('reader-Service',lambda:S.Service(view,channel,schemas));stack.callback(host.close)
  control=stage('diagnostic-margin-inputs',lambda:MI.prepare(name,SOURCE,PROFILE,D.reader.HERE/'packages/0001/period.json'));stack.callback(lambda:shutil.rmtree(control['root']))
  def call(service,operation,message,key=None):
   request=provider.call(M,service,operation,message,key=key);raw=P.compact(request);reply=service.call(raw)
   event({'phase':'api-call','operation':operation,'kind':reply.get('kind'),'request_sha256':sha(raw),'reply_sha256':sha(P.compact(reply)),'code':reply.get('message',{}).get('code') if isinstance(reply.get('message'),dict) else None})
   require(schemas.valid('api-reply',reply) and reply.get('kind')=='result',operation+' refused: '+str(reply.get('message',{}).get('code')));return reply['message']
  query=D.query(selected,host.sessions.bridge);delivery=stage('context.get',lambda:call(host,'context.get',query))
  ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+R.VERSION)[0].artifact)
  budget=copy.deepcopy(query['budget']);budget.update(max_actions=1,deadline=(A.now()+timedelta(seconds=900)).isoformat())
  runtime=load('current_legacy_context_sessions')
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T22-research-open:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(R.ASSIGNMENT),'profile':ref(R.PROFILE),'implementation':ref(R.IMPLEMENTATION),'capabilities':[ref(R.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),'authority_envelope_binding':runtime.stable_policy(channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  opened=stage('session.open',lambda:call(host,'session.open',opening,'T22:research:open:'+uuid.uuid4().hex));resource=host.sessions.live[opened['session_ref']]
  event({'phase':'session-opened','session_expires_at':resource.expires.isoformat(),'session_ref_sha256':sha(opened['session_ref'].encode())})
  consumed={}
  for refid,raw in private.items():
   channel.termination_guard();selected_row=host.vault.inputs[refid];actual=host.vault.material({'ref':refid,'sha256':selected_row['sha256']});require(actual==raw,'private input changed');consumed[refid]=actual
  channel.guard();resource.guard()
  lesson=P.frame_parse(consumed['private:T22:candidate-lesson.json']);review=P.frame_parse(consumed['private:T22:private-review-0001.json'])
  require(review['result']=='eligible-private-candidate' and lesson['scope_ref']==selected.sources.scope_ref,'candidate private eligibility/project differs')
  def candidate_guard():
   channel.termination_guard();resource.guard()
   require(A.now()<min(A.instant(lesson['payload']['expires_at']),A.instant(review['expires_at'])),
           'candidate or independent private review actually expired')
   for leaf,expected in (('candidate-lesson.json',lesson_raw),('private-review-0001.json',review_raw)):
    refid='private:T22:'+leaf;row=host.vault.inputs[refid]
    require(host.vault.material({'ref':refid,'sha256':row['sha256']})==expected,'candidate private input changed')
  def apply_current(observed):
   candidate_guard();result=C.analyze(observed,lesson,review);candidate_guard();return result
  reports=[]
  for index,b in enumerate(provenance['source_inputs']):
   if not b['path'].endswith('/observed.json'):continue
   observed=P.frame_parse(consumed['private:T22:public-evidence:'+str(index)])
   before=stage('research-ablation-'+str(index),lambda:C.analyze(observed))
   after=stage('research-Lesson-use-'+str(index),lambda:apply_current(observed))
   reports.append({'source_binding':b,'ablation_is_new_counterfactual_not_historical_omission':True,'ablation':before,'with_Lesson':after})
  report={'schema_version':'lab-T22-genuine-private-Lesson-use/v1-candidate','task_question':'Does a completed-pair subset preserve all declared historical W04 evidence, and what does each separate cohort support?','source_cut':selected.source_cut,'scope_ref':selected.sources.scope_ref,'candidate_lesson_sha256':sha(lesson_raw),'review_sha256':REVIEW_SHA,'cohorts':reports,'pooling_performed':False,'historical_study_rerun':False,'actual_new_work':'Independent current reanalysis of fixed real historical evidence through a Lesson-selected analysis population.','claim_ceiling':'Procedure inclusion and exact finite calculations only; the historical assessment already retained the timeout. No performance, Source-current Lesson, admission or human-learning claim.','authority_effect':'none'}
  channel.guard();resource.guard()
  for raw in (lesson_raw,review_raw,C.encoded(report)):
   before=len(resource.memory)
   for i in range(0,len(raw),4096):
    candidate_guard();resource.note(raw[i:i+4096]);candidate_guard()
   require(b''.join(bytes(x) for x in resource.memory[before:])==raw,'actual native Session consumed bytes differ')
  write(HERE/'native-research-report-0001.json',report)
  event({'phase':'genuine-research-Lesson-work','candidate_current_in_Source':False,'actual_private_input_reads':len(private),'native_exact_report_consumption':True,'cohort_count':len(reports)})
  machine=stage('Machine-select',lambda:MT.select(host,opened['session_ref'],{'path':str((API/'source-manifest.json').relative_to(ROOT)),'sha256':SOURCE}));stack.callback(machine.close)
  proof=stage('Machine-proof',machine.proof);stage('Machine-authentication',lambda:machine.authenticate(proof));proof=None
  lesson_query=D.query(selected,machine.service.sessions.bridge);lesson_query['budget']['max_actions']=0
  selection=stage('Source-controlled-Lesson.select',lambda:call(machine.service,'lesson.select',lesson_query))
  item=next(i for i in selection['items'] if i['posture']=='selected');require(len(selection['items'])==len(plan['lessons'])==1,'one Source-controlled Lesson required')
  diagnostic=stage('Source-controlled-original-pure-preflight-diagnostic',lambda:DIAG.execute(stack,M,D,H,selected,host,selection,provider,MI,control,stage,call))
  write(HERE/'controlled-preflight-result-0001.json',diagnostic)
  inspect={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:T22-inspect:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'session_ref':opened['session_ref'],'budget':{**budget,'max_actions':0},'authority_effect':'none'}
  inspected=stage('session.inspect',lambda:call(host,'session.inspect',inspect))
  closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:T22-close:'+uuid.uuid4().hex,'session_ref':opened['session_ref'],'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':inspected['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'}
  closed=stage('session.close',lambda:call(host,'session.close',closing,'T22:research:close:'+uuid.uuid4().hex))
  require(resource.closed and resource.memory==[] and resource.lesson_selections=={} and closed['discarded_memory'] is True,'actual native private memory/registry survives close')
  stale=False
  try:resource.note(b'closed-must-refuse')
  except ValueError as error:stale='Session is closed' in str(error)
  require(stale,'closed native resource accepted bytes')
  first={'result':'PASS-local-current-one-Lesson-selection-and-close','source_manifest_sha256':SOURCE,'profile_sha256':PROFILE,'session_ref_sha256':sha(opened['session_ref'].encode()),'lesson_version_ref_sha256':sha(item['lesson']['version_ref'].encode()),'selection_registry_erased':True,'closed_at':A.now().isoformat(),'source_cut':selected.source_cut,'source_controlled_diagnostic':diagnostic,'fixture_only':True,'authority_effect':'none'}
  write(HERE/'CONTROLLED-LESSON-FIRST-SESSION.json',first)
 require(all(sha((ROOT/b['path']).read_bytes())==b['sha256'] for b in bindings),'caller/input byte changed during execution')
 return {'result':'PASS-real-historical-research-private-Lesson-native73-consumption-and-close','source_manifest_sha256':SOURCE,'profile_sha256':PROFILE,'driver_input_bindings':bindings,'report_sha256':sha((HERE/'native-research-report-0001.json').read_bytes()),'independent_assessment_completed':False,'candidate_Source_current':False,'closed_resource_refused':True,'memory_erased':True,'selection_registry_erased':True,'controlled_original_preflight':diagnostic,'elapsed_seconds':round(time.monotonic()-started,3),'authority_effect':'none'}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True),flush=True)
