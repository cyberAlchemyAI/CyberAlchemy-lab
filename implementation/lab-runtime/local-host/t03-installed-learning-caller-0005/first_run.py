"""A genuine first selected-Lesson Session on the fresh installed3600 family."""
import argparse,copy,importlib.util,json,sys,uuid
from contextlib import ExitStack
from datetime import timedelta
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_t03_first_runtime',HERE/'runtime_common.py');C=importlib.util.module_from_spec(spec);sys.modules[spec.name]=C;spec.loader.exec_module(C)

def run(evidence, first_emitter_code=None, first_emitter_sha256=None):
 r=C.Runtime(evidence);P,D,A=r.P,r.D,r.A;helpers=r.helpers
 with ExitStack() as stack:
  view=r.stage('source-replay',lambda:stack.enter_context(P.source.replay_source(P.source.CURRENT_LEGACY_NAME)))
  selected=view.custody_signed_sources;r.source_count(selected);materials,plan=r.stage('one-Lesson-plan',lambda:helpers.lesson_materials(r.M,D,selected))
  root=r.workspace('reader');key,path,pin=r.stage('current-private-reader-provision',lambda:helpers.provision(r.M,root,D,selected,P.source.CURRENT_LEGACY_NAME,materials))
  channel=r.stage('Reader-channel',lambda:A.ReaderChannel(path,pin,r.schemas));stack.callback(channel.close)
  r.stage('Reader-authenticate',lambda:channel.authenticate(r.F.proof(key,channel.challenge)));key=None
  host=r.stage('Reader-Service',lambda:r.S.Service(view,channel,r.schemas));stack.callback(host.close)
  query=D.query(selected,host.sessions.bridge);delivery=r.stage('context.get',lambda:r.call(host,'context.get',query))
  ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact)
  budget=copy.deepcopy(query['budget']);budget.update(max_actions=1,deadline=(A.now()+timedelta(seconds=3600)).isoformat())
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T03-first:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),'authority_envelope_binding':r.load('current_legacy_context_sessions').stable_policy(channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  open_key='T03:first-open:'+uuid.uuid4().hex
  try:opened=r.stage('session.open',lambda:r.call(host,'session.open',opening,open_key))
  except BaseException:
   r.inspect_operation(host,'session.open',open_key,'failed-session-open')
   raise
  sid=opened['session_ref'];resource=host.sessions.live[sid]
  formal=r.capture_formal_session(host,sid)
  emission=None
  if first_emitter_code is not None:
   C.need(first_emitter_sha256 is not None,'pinned first-emitter SHA required')
   hook=C.load_file(HERE/'first_emitter_hook.py')
   emission=r.stage('live-native-first-emission',lambda:hook.emit(r,host,selected,opened,resource,first_emitter_code,first_emitter_sha256))
  machine=r.stage('Machine-select',lambda:r.MT.select(host,sid,r.api_binding));stack.callback(machine.close)
  proof=r.stage('Machine-proof',machine.proof);r.stage('Machine-authenticate',lambda:machine.authenticate(proof));proof=None
  query=D.query(selected,machine.service.sessions.bridge);query['budget']['max_actions']=0
  selection=r.stage('lesson.select',lambda:r.call(machine.service,'lesson.select',query))
  items=[i for i in selection['items'] if i['posture']=='selected'];C.need(len(items)==len(selection['items'])==len(plan['lessons'])==1,'exactly one selected Lesson required')
  item=items[0]
  inspect={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:T03-first-inspect:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'session_ref':sid,'budget':{**budget,'max_actions':0},'authority_effect':'none'}
  inspected=r.stage('session.inspect',lambda:r.call(host,'session.inspect',inspect))
  closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:T03-first-close:'+uuid.uuid4().hex,'session_ref':sid,'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':inspected['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'}
  closed=r.stage('session.close',lambda:r.call(host,'session.close',closing,'T03:first-close:'+uuid.uuid4().hex))
  C.need(resource.closed and resource.memory==[] and resource.lesson_selections=={} and sid not in host.sessions.live and closed['discarded_memory'] is True,'explicit Session disposal incomplete')
  refused=False
  try:resource.note(b'closed-first-refusal')
  except ValueError:refused=True
  C.need(refused,'closed resource accepted bytes')
  result={'result':'PASS-local-current-one-Lesson-selection-and-close','api_source_binding':r.api_binding,'profile_binding':r.profile_binding,'family_source_binding':r.provider.binding('family.source'),'source_cut':selected.source_cut,'actual_selected_subject_count':r.actual_subject_count,'session_ref_sha256':C.sha(sid.encode()),'lesson_version_ref_sha256':C.sha(item['lesson']['version_ref'].encode()),'selection_registry_erased':True,'explicitly_closed':True,'memory_erased':True,'closed_refused':True,'formal_session_binding':formal,'native_first_emission':emission,'common_dispatch_operation_pairs':r.pairs,'closed_at':A.now().isoformat(),'actual_fixture_budget_seconds':3600,'fixture_only':True,'authority_effect':'none'}
  r.guard_caller()
  C.write(r.evidence/'FIRST-SESSION.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--first-emitter-code');p.add_argument('--first-emitter-sha256');a=p.parse_args();print(json.dumps(run(a.evidence,a.first_emitter_code,a.first_emitter_sha256),sort_keys=True),flush=True)
