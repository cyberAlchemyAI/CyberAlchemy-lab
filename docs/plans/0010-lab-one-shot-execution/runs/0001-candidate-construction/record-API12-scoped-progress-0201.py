"""Record one guarded partial API12 construction cut; close no obligations."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v12'
SOURCE='5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PROFILE='2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'
CLOSED={'complete','complete-existing-evidence','complete-planning','satisfied-scoped'}
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def require(value,message):
 if not value:raise ValueError(message)
def exclusive(p,value):
 with p.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,value,original):
 require(p.read_bytes()==original,'evidence pointer changed concurrently: '+str(p))
 stage=p.with_name(p.name+'.progress-0201-staging');exclusive(stage,value);os.replace(stage,p)

def main():
 are=RUN/'ARE-scoped-progress-boundary-0185.json';a=load(are);require(a['ok'] and a['authority_effect']=='none','exact non-authorizing progress ARE required')
 dag_path=RUN/'dag.json';swu_path=RUN/'swu-manifest.json';evidence_path=RUN/'evidence.json'
 originals={p:p.read_bytes() for p in (dag_path,swu_path,evidence_path)}
 dag=json.loads(originals[dag_path]);swu=json.loads(originals[swu_path]);evidence=json.loads(originals[evidence_path]);r03=next(n for n in dag['nodes'] if n['id']=='R03')
 require(len(dag['nodes'])==46 and sum(n['status'] in CLOSED for n in dag['nodes'])==36,'preserve actual36/46 cut')
 require(r03['status']=='in-progress' and r03['progress_evidence']==[evidence['task_progress']['R03']],'exact current partial R03 pointer required')
 parent=ROOT/r03['progress_evidence'][0]['path'];require(bind(parent)['sha256']==r03['progress_evidence'][0]['sha256'],'current predecessor changed')
 require(bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE,'frozen actual API12 pins differ')
 common_path=RUN/'Common-operator-0180.json';common=load(common_path)
 require(common['result']=='PASS' and len(common['checks'])==22 and len(common['actual_calls'])==19 and common['exit_guard_error'] is None and common['failure'] is None and common['owned_fixture_removed'],'actual completed Common22/19 required')
 source_path=BASE/'source-union-v3-qualification-action-0148/qualification.json';source=load(source_path)
 require(bind(source_path)['sha256']=='00ec7c1b4b4218e5c1463b5a1932143c789cfab9f7b16b9acee44c53c113427b' and source['result']=='PASS' and source['actual_original_methods']==10 and source['actual_authenticated_public_calls']==16 and source['full_history_guards_entry_exit_passed_each_run'],'actual immutable Source3 focused10/16 required')
 action_path=BASE/'api-action-integration-v3/receipts/governance-transport-0166-0001/qualification.json';action=load(action_path);require(action['result']=='PASS' and action['actual_cases']==22 and action['actual_public_calls']==66 and action['actual_crashed_public_calls']==3 and action['source_guarded_exit_completed'],'unchanged Action3 scoped22/66/3 required')
 governance_path=RUN/'Governance-public-qualification-0148-v4.json';governance=load(governance_path);require(governance['result']=='PASS' and governance['actual_cases']==17 and governance['actual_public_calls']==30 and governance['full_history_entry_exit_guards'],'unchanged governance17/30 required')
 ir_path=RUN/'installation-release-v4-0148-bounded.json';ir=load(ir_path);require(ir['result']=='PASS-bounded-retry-and-inspection' and ir['qualified_cases']==2 and ir['actual_public_calls']==4 and all(x['result']=='PASS' and x['actual_process_exit_code']==0 for x in ir['reports']),'actual IR4 scoped2/4 required')
 plan_path=RUN/'final-api-regression-plan-0177.json';plan=load(plan_path);require(bind(plan_path)['sha256']=='8447e875378112d2fe73a158da75f40c02dc6e63fc65ad08c7e2ef7a6025f03a' and len(plan['all_declared_methods'])==345,'unchanged exact345 plan required')
 rows={}
 def add(p):
  row=bind(p);require(rows.get(row['path'],row)==row,'conflicting exact immutable input');rows[row['path']]=row
 def verified(row):require(bind(ROOT/row['path'])==row,'delivered evidence original drift');add(ROOT/row['path'])
 for p in (parent,API/'source-manifest.json',API/'contract-profile.json',common_path,source_path,action_path,governance_path,ir_path,plan_path,are,Path(__file__).resolve(),RUN/'Action3-public-delivery-0166.json',RUN/'Governance-public-delivery-0148-v4.json',RUN/'final-api-regression-execution-disposition-0183.json',RUN/'aggregate-final-api-regression-0183.py'):add(p)
 for row in common['files']:verified(row)
 for row in [*source['receipts'],*source['selected_source_bindings']]:verified(row)
 for row in action['files']:verified(row)
 for row in ir['reports']:
  for key in ('report_binding','log_binding','wire_binding'):verified(row[key])
 snapshots=[];known=[]
 event_paths=[RUN/'final-api-regression-0173-0177.sequential-fcffea20c78446ae.events.jsonl',*[RUN/('final-api-regression-0173-0183.worker-'+str(i)+'.events.jsonl') for i in range(6)]]
 for path in event_paths:
  require(path.is_file(),'expected actual live event source missing: '+path.name);raw=path.read_bytes();prefix=raw if raw.endswith(b'\n') else raw[:raw.rfind(b'\n')+1];events=[json.loads(line) for line in prefix.splitlines()]
  require(events and events[0]['source_pin']==SOURCE and events[0]['profile_pin']==PROFILE and events[0]['worker_plan_binding']==bind(plan_path),'live event names another frozen producer')
  compact_events=[{k:x[k] for k in ('at','phase','bucket','declared_method','result','actual_methods','full_history_exit_guard_passed') if k in x} for x in events]
  failures=[x for x in compact_events if x.get('phase')=='case-completed' and x.get('result') in ('FAIL','ERROR')];known.extend(failures)
  snapshots.append({'live_event_locator':path.relative_to(ROOT).as_posix(),'captured_original_prefix_sha256':hashlib.sha256(prefix).hexdigest(),'captured_original_prefix_bytes':len(prefix),'original_event_count':len(events),'bucket':events[0]['bucket'],'completed_cases_observed':sum(x.get('phase')=='case-completed' for x in events),'known_failures_observed':failures,'last_actual_event':compact_events[-1],'sanitized_original_events':compact_events,'qualification_posture':'pending; terminal and all345 exact accounting remain required'})
 observed=next((x for x in known if x['declared_method']=='test_current_controls.py:CurrentControls.test_03_exact_current_profile_and_protocol_controls'),None);require(observed is not None,'preserve actual known CurrentControls literal-count failure')
 snapshot_path=RUN/'API12-regression-pending-snapshot-0201.json';snapshot={'schema_version':'lab-actual-regression-pending-snapshot/v1-candidate','captured_at':datetime.now(timezone.utc).isoformat(),'source_sha256':SOURCE,'profile_sha256':PROFILE,'plan_binding':bind(plan_path),'snapshots':snapshots,'known_original_failures':known,'regression_qualified':False,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False,'claim_ceiling':'Immutable cut of actual original live event prefixes only. Later appends or silence do not supply a terminal result, a passed suite or a duplicate job.'};exclusive(snapshot_path,snapshot);add(snapshot_path)
 remaining=['Finish actual345-method original regression and preserve all failures. At this cut CurrentControls.test_03 has actual FAIL from obsolete24 versus declared34; custody Sessions.test_30 has the same additional stale assertion identified statically, not yet relabeled as an observed failure. Any additive correction check remains separate from original regression outcomes.','Finish complete selected common Session/Machine/inherited behavior and exact all-operation paths; Common22 and Source3focused10 do not transfer full qualification.','Establish actual value and later controlled lesson application/outcome/counterevidence through original R05 obligations; construction/repair is not causal learning evidence.','Gather genuine human engineering/research/freshSession pilot observations and actual usefulness response.','Complete exact R06 private/public release selection, R07/S02 and sole actual R08 owner outcome; retain separately scoped A01-A04 effects.']
 value={'schema_version':'lab-interface-construction-progress/v1-candidate','result':'PASS','progress_record_result':'PASS','qualification_result':'pending-with-known-original-failure','recorded_at':datetime.now(timezone.utc).isoformat(),'parent_progress_binding':bind(parent),'files':[rows[k] for k in sorted(rows)],'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'authored_operations':34,'actual_scoped_results':{'commonAPI12':{'result':'PASS','checks':22,'actual_calls':19,'binding':bind(common_path),'whole_API_qualified':False},'Source3':{'result':'PASS-focused','original_methods':10,'authenticated_calls':16,'binding':bind(source_path),'qualification_transferred_to_common34':False},'action3':{'result':'PASS','cases':22,'public_calls':66,'real_OS_child_exits':3,'binding':bind(action_path)},'governance4':{'result':'PASS','cases':17,'public_calls':30,'binding':bind(governance_path)},'installation_release4':{'result':'PASS-scoped','cases':2,'public_calls':4,'binding':bind(ir_path)}},'original_regression_plan_binding':bind(plan_path),'original_regression_declared_methods':345,'original_regression_posture':'pending; actual known failure retained','original_regression_snapshot_binding':bind(snapshot_path),'known_original_regression_failures':known,'additional_static_stale_assertion':{'method':'test_custody_sessions.py:Sessions.test_30_current_handler_profile_retains_all_original_contracts','file_line':211,'expected_old_supported_count':24,'actual_declared_supported_count':34,'observed_failure_claimed':False},'closed_tasks':36,'total_tasks':46,'remaining_obligations':remaining,'human_pilot_complete':False,'Paperclip_installed':False,'actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0,'external_effects':0,'task_complete':False,'whole_API_qualified':False,'goal_complete':False,'authority_effect':'none','claim_ceiling':'Passing bounded progress synchronization only: actual Common22/19 and focused Source3/Action3/Gov4/IR4 evidence. Original345 has a known failure and remains pending/unqualified. No genuine human approval/usefulness, causal learning result, canonical admission, actual R08/A outcome or completed Lab.'}
 output=API/'receipts/R03-0201.json';require(output.parent.is_dir(),'owned API12 receipts directory required');exclusive(output,value)
 pointer={**bind(output),'authority_effect':'none','completion_mode':'candidate-partial'}
 r03['progress_evidence']=[pointer];r03['remaining_obligations']=remaining
 for unit in swu['units']:
  if unit['parent_task']=='R03':unit['status']=r03['status'];unit['progress_evidence']=[pointer]
 evidence['task_progress']['R03']=pointer
 for p,v in ((dag_path,dag),(swu_path,swu),(evidence_path,evidence)):replace(p,v,originals[p])
 require(sum(n['status'] in CLOSED for n in dag['nodes'])==36 and r03['status']=='in-progress','no task closure permitted')
 print(json.dumps({'result':'PASS','progress_binding':bind(output),'snapshot_binding':bind(snapshot_path),'immutable_bound_files':len(rows),'closed':36,'total':46,'known_original_failures':len(known),'whole_API_qualified':False,'task_complete':False,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
