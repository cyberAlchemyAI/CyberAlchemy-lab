"""Fresh native Session consumes exact assessed report; actual Machine privacy probe."""
import argparse,copy,importlib.util,json,sys,uuid
from contextlib import ExitStack
from datetime import timedelta
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_t03_first_runtime',HERE/'runtime_common.py');C=importlib.util.module_from_spec(spec);sys.modules[spec.name]=C;spec.loader.exec_module(C)

def run(evidence,later_receipt):
 r=C.Runtime(evidence);P,D,A=r.P,r.D,r.A;helpers=r.helpers
 prior_path=Path(later_receipt);prior_raw=prior_path.read_bytes();prior=json.loads(prior_raw)
 C.need(prior['result']=='PASS-local-current-Lesson-later-application-independent-assessment' and prior['family_source_binding']==r.provider.binding('family.source') and prior['actual_later_work']['parent_session_closed'] is True and prior['actual_later_work']['independent_assessment_after_parent_close'] is True,'exact completed independent assessment required')
 leaves={'later-inspection-output.json':'inspection_output_sha256','later-assessment-candidate.json':'assessment_candidate_sha256','later-assessment-result.json':'assessment_reply_sha256','later-inspection-counterevidence.json':'counterevidence_sha256'}
 inputs={}
 for leaf,key in leaves.items():
  raw=(prior_path.parent/leaf).read_bytes();C.need(len(raw)<=16384 and C.sha(raw)==prior['actual_later_work'][key],'completed assessed-result original differs');inputs[leaf]=raw
 privacy=C.load_file(HERE/'machine_privacy.py')
 with ExitStack() as stack:
  view=r.stage('source-replay',lambda:stack.enter_context(P.source.replay_source(P.source.CURRENT_LEGACY_NAME)))
  selected=view.custody_signed_sources;r.source_count(selected);materials,plan=r.stage('one-Lesson-plan',lambda:helpers.lesson_materials(r.M,D,selected))
  materials.update({'fixture:assessed-input:'+leaf:raw for leaf,raw in inputs.items()})
  root=r.workspace('reader');key,path,pin=r.stage('current-private-reader-provision',lambda:helpers.provision(r.M,root,D,selected,P.source.CURRENT_LEGACY_NAME,materials))
  channel=r.stage('Reader-channel',lambda:A.ReaderChannel(path,pin,r.schemas));stack.callback(channel.close)
  r.stage('Reader-authenticate',lambda:channel.authenticate(r.F.proof(key,channel.challenge)));key=None
  host=r.stage('Reader-Service',lambda:r.S.Service(view,channel,r.schemas));stack.callback(host.close)
  query=D.query(selected,host.sessions.bridge);delivery=r.stage('context.get',lambda:r.call(host,'context.get',query))
  ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact)
  budget=copy.deepcopy(query['budget']);budget.update(max_actions=1,deadline=(A.now()+timedelta(seconds=3600)).isoformat())
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T03-consume:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),'authority_envelope_binding':r.load('current_legacy_context_sessions').stable_policy(channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  open_key='T03:consume-open:'+uuid.uuid4().hex
  try:opened=r.stage('session.open',lambda:r.call(host,'session.open',opening,open_key))
  except BaseException:
   r.inspect_operation(host,'session.open',open_key,'failed-session-open')
   raise
  sid=opened['session_ref'];resource=host.sessions.live[sid]
  formal=r.capture_formal_session(host,sid)
  C.need(C.sha(sid.encode())!=prior['session_ref_sha256'],'assessed-result consumer Session must be fresh')
  consumed=[]
  for leaf,expected in inputs.items():
   refid='fixture:assessed-input:'+leaf;channel.termination_guard();row=host.vault.inputs[refid];raw=host.vault.material({'ref':refid,'sha256':row['sha256']});C.need(raw==expected,'actual owned input read differs')
   before=len(resource.memory)
   for offset in range(0,len(raw),4096):resource.note(raw[offset:offset+4096])
   C.need(b''.join(bytes(value) for value in resource.memory[before:])==raw,'native assessed-result consumption differs')
   consumed.append({'name':leaf,'sha256':C.sha(raw),'size_bytes':len(raw),'actual_private_input_read_and_native_note':True})
  machine=r.stage('Machine-select',lambda:r.MT.select(host,sid,r.api_binding));stack.callback(machine.close)
  proof=r.stage('Machine-proof',machine.proof);r.stage('Machine-authenticate',lambda:machine.authenticate(proof));proof=None
  surface=r.I.IntegrationService(machine.service);r.surfaces[id(machine.service)]=surface
  witness=r.stage('actual-Machine-privacy-probe',lambda:privacy.probe(r.M,D,selected,host,machine,opened,helpers,surface))
  query=D.query(selected,machine.service.sessions.bridge);query['budget']['max_actions']=0
  selection=r.stage('lesson.select',lambda:r.call(machine.service,'lesson.select',query))
  items=[i for i in selection['items'] if i['posture']=='selected'];C.need(len(items)==len(selection['items'])==len(plan['lessons'])==1,'exactly one selected Lesson required')
  item=items[0]
  inspect={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:T03-consume-inspect:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'session_ref':sid,'budget':{**budget,'max_actions':0},'authority_effect':'none'}
  inspected=r.stage('session.inspect',lambda:r.call(host,'session.inspect',inspect))
  closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:T03-consume-close:'+uuid.uuid4().hex,'session_ref':sid,'agent_instance_ref':opened['agent_instance_ref'],'expected_session_binding':inspected['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'}
  closed=r.stage('session.close',lambda:r.call(host,'session.close',closing,'T03:consume-close:'+uuid.uuid4().hex))
  C.need(resource.closed and resource.memory==[] and resource.lesson_selections=={} and sid not in host.sessions.live and closed['discarded_memory'] is True,'explicit Session disposal incomplete')
  refused=False
  try:resource.note(b'closed-first-refusal')
  except ValueError:refused=True
  C.need(refused,'closed resource accepted bytes')
  privacy_result=r.stage('Machine-private-memory-disposal',lambda:witness.finish(lambda path:path.read_bytes()))
  r.guard_caller()
  C.write(r.evidence/'MACHINE-PRIVACY.json',privacy_result)
  C.need(prior_path.read_bytes()==prior_raw and all((prior_path.parent/leaf).read_bytes()==raw for leaf,raw in inputs.items()),'completed assessed input changed during consumption')
  result={'result':'PASS-local-assessed-result-later-Session-consumption-and-close','consumed_inputs':consumed,'earlier_learning_receipt':{'path':str(prior_path),'sha256':C.sha(prior_raw)},'assessed_result_later_consumed':True,'Machine_privacy_result':privacy_result,'api_source_binding':r.api_binding,'profile_binding':r.profile_binding,'family_source_binding':r.provider.binding('family.source'),'source_cut':selected.source_cut,'actual_selected_subject_count':r.actual_subject_count,'session_ref_sha256':C.sha(sid.encode()),'lesson_version_ref_sha256':C.sha(item['lesson']['version_ref'].encode()),'selection_registry_erased':True,'explicitly_closed':True,'memory_erased':True,'closed_refused':True,'formal_session_binding':formal,'common_dispatch_operation_pairs':r.pairs,'closed_at':A.now().isoformat(),'actual_fixture_budget_seconds':3600,'fixture_only':True,'authority_effect':'none'}
  r.guard_caller()
  C.write(r.evidence/'CONSUMER-SESSION.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--later-receipt',required=True);a=p.parse_args();print(json.dumps(run(a.evidence,a.later_receipt),sort_keys=True),flush=True)
