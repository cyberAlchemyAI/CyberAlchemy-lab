"""Later selected-Lesson inspection/application and independent assessment."""
import argparse,copy,importlib.util,json,sys,uuid
from contextlib import ExitStack
from datetime import timedelta
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_t03_first_runtime',HERE/'runtime_common.py');C=importlib.util.module_from_spec(spec);sys.modules[spec.name]=C;spec.loader.exec_module(C)

def run(evidence,first_receipt):
 r=C.Runtime(evidence);P,D,A=r.P,r.D,r.A;helpers=r.helpers
 first_path=Path(first_receipt);first_raw=first_path.read_bytes();first=json.loads(first_raw)
 C.need(first['result']=='PASS-local-current-one-Lesson-selection-and-close' and first['selection_registry_erased'] is True and first['explicitly_closed'] is True and first['family_source_binding']==r.provider.binding('family.source'),'exact current family earlier closed Lesson Session required')
 margin=C.load_file(HERE/'margin_inputs.py');actions=C.load_file(HERE/'actions.py')
 control=r.stage('diagnostic-margin-configuration',lambda:margin.prepare(r))
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
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T03-later:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),'authority_envelope_binding':r.load('current_legacy_context_sessions').stable_policy(channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  open_key='T03:later-open:'+uuid.uuid4().hex
  try:opened=r.stage('session.open',lambda:r.call(host,'session.open',opening,open_key))
  except BaseException:
   r.inspect_operation(host,'session.open',open_key,'failed-session-open')
   raise
  sid=opened['session_ref'];resource=host.sessions.live[sid]
  formal=r.capture_formal_session(host,sid)
  machine=r.stage('Machine-select',lambda:r.MT.select(host,sid,r.api_binding));stack.callback(machine.close)
  proof=r.stage('Machine-proof',machine.proof);r.stage('Machine-authenticate',lambda:machine.authenticate(proof));proof=None
  query=D.query(selected,machine.service.sessions.bridge);query['budget']['max_actions']=0
  selection=r.stage('lesson.select',lambda:r.call(machine.service,'lesson.select',query))
  items=[i for i in selection['items'] if i['posture']=='selected'];C.need(len(items)==len(selection['items'])==len(plan['lessons'])==1,'exactly one selected Lesson required')
  item=items[0]
  C.need(C.sha(item['lesson']['version_ref'].encode())==first['lesson_version_ref_sha256'] and C.sha(sid.encode())!=first['session_ref_sha256'],'later Session must select exact Lesson with a fresh identity')
  def terminal_cleanup():
   host.close()
   C.need(resource.closed and resource.memory==[] and resource.lesson_selections=={} and sid not in host.sessions.live,'owned laterSession disposal incomplete')
   r.event({'phase':'terminal-owned-resource-cleanup','closed':True,'memory_erased':True,'selection_registry_erased':True,'custodian_live_entry_removed':True})
  stack.callback(terminal_cleanup)
  result=r.stage('actual-later-use-application-independent-assessment',lambda:actions.execute(stack,r.M,D,r.H,selected,host,selection,helpers,margin,control,r.stage,r.call,runtime=r,first_receipt=first_path))
  C.need(result['parent_session_closed'] is True and resource.closed and resource.memory==[] and resource.lesson_selections=={},'later parent must be explicitly closed before assessment')
  permission_negatives=r.stage('closed-parent-permission-negatives',lambda:r.closed_permission_negatives(host))
  C.need(first_path.read_bytes()==first_raw,'earlier firstSession receipt changed')
  output={'result':'PASS-local-current-Lesson-later-application-independent-assessment','api_source_binding':r.api_binding,'profile_binding':r.profile_binding,'family_source_binding':r.provider.binding('family.source'),'source_cut':selected.source_cut,'actual_selected_subject_count':r.actual_subject_count,'first_session_receipt':{'path':str(first_path),'sha256':C.sha(first_raw)},'session_ref_sha256':C.sha(sid.encode()),'lesson_version_ref_sha256':C.sha(item['lesson']['version_ref'].encode()),'formal_session_binding':formal,'actual_later_work':result,'permission_negatives':permission_negatives,'common_dispatch_operation_pairs':r.pairs,'actual_fixture_budget_seconds':3600,'assessed_result_later_consumed':False,'fixture_only':True,'authority_effect':'none'}
  r.guard_caller()
  C.write(r.evidence/'LATER-SESSION.json',output);return output
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--first-receipt',required=True);a=p.parse_args();print(json.dumps(run(a.evidence,a.first_receipt),sort_keys=True),flush=True)
