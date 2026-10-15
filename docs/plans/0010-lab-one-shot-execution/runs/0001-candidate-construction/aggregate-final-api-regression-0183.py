"""Collect exact API12 regression evidence across bounded lock namespaces.

Read-only collection of original worker reports/events; never run test methods,
replace callbacks/clocks, rewrite a worker report or transfer it to a successor.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]

def require(value,message):
 if not value:raise ValueError(message)
def path(value):
 p=Path(value)
 if not p.is_absolute():p=ROOT/p
 require(p.is_relative_to(ROOT) and p.resolve()==p,'exact repository original required')
 return p
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_bytes())
def instant(value):
 result=datetime.fromisoformat(value)
 require(result.tzinfo is not None,'actual timezone-aware event timestamp required')
 return result.astimezone(timezone.utc)
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--api-directory',required=True);parser.add_argument('--source',required=True);parser.add_argument('--profile',required=True)
 parser.add_argument('--plan',required=True);parser.add_argument('--plan-sha256',required=True);parser.add_argument('--disposition',required=True);parser.add_argument('--disposition-sha256',required=True)
 parser.add_argument('--session-report',required=True);parser.add_argument('--worker-report',required=True,action='append');parser.add_argument('--ir-report',required=True);parser.add_argument('--output',required=True);a=parser.parse_args()
 api=path(a.api_directory);plan_path=path(a.plan);disposition_path=path(a.disposition);out=path(a.output)
 require(out.parent==RUN and out.name.startswith('final-api-regression-0183') and not out.exists(),'new owned aggregate output required')
 require(binding(plan_path)['sha256']==a.plan_sha256,'exact original0177 plan pin differs')
 require(binding(disposition_path)['sha256']==a.disposition_sha256,'exact bounded execution disposition pin differs')
 plan=read(plan_path);disposition=read(disposition_path)
 require(disposition['schema_version']=='lab-final-api-execution-disposition/v1-candidate' and disposition['original_plan_binding']==binding(plan_path),'disposition does not bind this exact frozen plan')
 for selected in (plan,disposition):
  require(selected['api_directory']==api.relative_to(ROOT).as_posix() and selected['source_sha256']==a.source and selected['profile_sha256']==a.profile,'report/plan/disposition must select one exact API12 producer')
 require(disposition['exact_declared_methods']==plan['all_declared_methods'] and len(plan['all_declared_methods'])==len(set(plan['all_declared_methods']))==345,'exact345 method inventory required')
 require(disposition['method_inventory_sha256']==hashlib.sha256(compact(plan['method_inventory'])).hexdigest(),'bounded method inventory differs')
 require(disposition['original_method_count']==len(plan['original_declared_methods'])==323 and disposition['added_installation_release_count']==len(plan['added_installation_release_methods'])==22,'exact original323 plusIR22 inventory required')
 require(disposition['ordinary_worker_methods']==plan['workers'] and len(plan['workers'])==6 and sum(map(len,plan['workers'].values()))==289,'exact six ordinary class buckets required')
 require(len(a.worker_report)==6,'exact six actual ordinary worker reports required')
 inputs=[path(a.session_report),*[path(p) for p in a.worker_report],path(a.ir_report)]
 require(len(inputs)==len(set(inputs))==8,'eight distinct original report paths required')
 missing=[p.relative_to(ROOT).as_posix() for p in inputs if not p.is_file()]
 if missing:print(json.dumps({'result':'PENDING','missing_reports':missing,'goal_complete':False}));return 2
 # The actual frozen comparison helper is read under the original plan's
 # caller binding, with no fixture import or production dispatch.
 for row in plan['tools_bindings']:require(binding(ROOT/row['path'])==row,'frozen original regression caller changed')
 helper=RUN/'final-api-regression-map-0173.py';spec=importlib.util.spec_from_file_location('_cal_regression_0183_original_map',helper);M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
 require(M.discover(api)==plan['method_inventory'],'final API method/class/fixture AST differs from frozen inventory')
 original=path(plan['original_api_directory']);require(M.discover(original)==plan['original_method_inventory'],'inherited original AST changed')
 require(M.compare(plan['original_method_inventory'],plan['method_inventory'])==plan['method_ast_comparison'] and plan['method_ast_comparison']['acceptable'],'inherited exact method/fixture comparison differs')
 require(binding(ROOT/plan['original_plan_binding']['path'])==plan['original_plan_binding'],'original323 baseline worker plan changed')
 require(binding(original/'source-manifest.json')['sha256']==plan['original_source_sha256'] and binding(original/'contract-profile.json')['sha256']==plan['original_profile_sha256'],'original baseline source/profile changed')
 are=ROOT/disposition['are_boundary_binding']['path'];require(binding(are)==disposition['are_boundary_binding'],'actual scheduling ARE boundary changed');receipt=read(are);require(receipt['ok'] and receipt['authority_effect']=='none','bounded ARE evidence grants no governing authority')
 for row in [*disposition['write_path_audit']['declared_test_file_bindings'],*disposition['write_path_audit']['fixture_provenance_bindings'],*disposition['write_path_audit']['shared_original_targets']]:require(binding(ROOT/row['path'])==row,'bounded actual write-path proof original changed')
 require(disposition['write_path_audit']['shared_repository_mutating_classes']==['test_installation_release.py:InstallationReleaseAPI'],'actual exclusive repository-mutating class differs')
 require(binding(api/'source-manifest.json')['sha256']==a.source and binding(api/'contract-profile.json')['sha256']==a.profile,'actual final producer pins differ')
 spec=importlib.util.spec_from_file_location('_cal_regression_0183_full_guard',api/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 guard.verify(a.source);entry=datetime.now(timezone.utc).isoformat();cases=[];records=[];problems=[];event_bindings=[];terminals={};starts={};seen_buckets=set()
 expected={**{'worker:'+k:v for k,v in plan['workers'].items()},**{'sequential:'+k:v for k,v in plan['sequential_classes'].items()}}
 session_bucket=disposition['existing_session_bucket'];ir_bucket=disposition['exclusive_ir_bucket']
 for i,p in enumerate(inputs):
  raw=p.read_bytes();r=json.loads(raw);bucket=r['bucket'];require(bucket in expected and bucket not in seen_buckets,'unknown or duplicated actual bucket');seen_buckets.add(bucket)
  require((i==0 and bucket==session_bucket) or (i==7 and bucket==ir_bucket) or (1<=i<=6 and bucket.startswith('worker:')),'explicit Session/ordinary/IR report classification differs')
  require(r['schema_version']=='lab-final-api-worker-qualification/v1-candidate' and r['worker_plan_binding']==binding(plan_path) and r['selected_methods']==expected[bucket],'actual worker names another method selection/plan')
  require(r['files'][0]==binding(api/'source-manifest.json') and r['files'][1]==binding(api/'contract-profile.json'),'actual worker source/profile differs')
  for row in [*r['files'],r['events_binding']]:require(binding(ROOT/row['path'])==row,'actual completed worker source/events changed')
  require(all(x['source']==a.source and x['profile']==a.profile for x in r['fixture_pins']) and bool(r['fixture_pins']),'actual original fixture SOURCE/PROFILE pins differ')
  require(r['authority_effect']=='none' and r['actual_owner_outcome'] is None and r['original_clocks_or_callbacks_changed'] is False and r['method_or_fixture_monkeypatches'] is False,'worker claims changed original authority/clocks/callbacks')
  require(r['inherited_ast_comparison']==plan['method_ast_comparison'],'actual worker inherited method comparison differs')
  events_path=ROOT/r['events_binding']['path'];events=[json.loads(line) for line in events_path.read_text().splitlines()];require(events and events[0]['phase']=='starting' and events[-1]['phase']=='terminal','complete original starting/terminal events required')
  require(sum(x['phase']=='starting' for x in events)==sum(x['phase']=='terminal' for x in events)==1,'exact original event lifecycle required')
  first=events[0];terminal=events[-1];require(first['bucket']==bucket and first['source_pin']==a.source and first['profile_pin']==a.profile and first['worker_plan_binding']==binding(plan_path),'actual starting event producer/plan differs')
  timestamps=[instant(x['at']) for x in events];require(all(x<=y for x,y in zip(timestamps,timestamps[1:])),'actual event timeline moved backwards')
  expected_prefix=disposition['existing_session_prefix'] if bucket==session_bucket else disposition['ordinary_worker_prefix'] if bucket.startswith('worker:') else None
  if expected_prefix:require(p.name.startswith(expected_prefix+'.') and events_path.name.startswith(expected_prefix+'.'),'actual authorized report/lock namespace differs')
  observations=[{k:v for k,v in x.items() if k not in ('phase','at')} for x in events if x['phase']=='case-completed'];require(observations==r['cases'],'exact actual completed event/report cases differ')
  declared=[x['declared_method'] for x in r['cases']];require(len(declared)==len(set(declared)) and set(declared)<=set(expected[bucket]),'duplicate or undeclared original method result')
  running=[x['declared_method'] for x in events if x['phase']=='running'];require(len(running)==len(set(running)) and set(declared)<=set(running)<=set(expected[bucket]),'actual started method accounting differs')
  require(terminal['result']==r['result'] and terminal['actual_methods']==r['actual_methods'] and terminal['exact_method_accounting']==r['exact_method_accounting'] and terminal['full_history_exit_guard_passed']==r['source_guarded_exit_completed'],'actual terminal/report summary differs')
  good=r['result']=='PASS' and r['source_guarded_entry_completed'] and r['source_guarded_exit_completed'] and r['execution_error'] is None and r['exit_guard_error'] is None and not r['fixture_errors'] and not r['subtest_failures'] and r['exact_method_accounting'] and r['actual_methods']==len(expected[bucket]) and set(declared)==set(running)==set(expected[bucket]) and all(x['result']=='PASS' for x in r['cases'])
  if not good:problems.append(bucket)
  starts[bucket]=timestamps[0];terminals[bucket]=timestamps[-1];report_binding=binding(p)
  cases.extend([{**x,'worker_report_binding':report_binding,'worker_events_binding':r['events_binding']} for x in r['cases']]);event_bindings.append(r['events_binding']);records.append({'bucket':bucket,'report_binding':report_binding,'events_binding':r['events_binding'],'started_at':first['at'],'terminal_at':terminal['at'],'result':r['result'],'actual_methods':r['actual_methods']})
  require(p.read_bytes()==raw,'original worker report changed during collection')
 require(seen_buckets==set(expected),'all exact original buckets required')
 other_terminals=[v for k,v in terminals.items() if k!=ir_bucket];ordered=starts[ir_bucket]>=max(other_terminals)
 if not ordered:problems.append('IR-start-overlapped-live-Session-or-ordinary-worker')
 ids=[x['declared_method'] for x in cases];exact=len(ids)==len(set(ids))==345 and set(ids)==set(plan['all_declared_methods'])
 guard.verify(a.source);require(binding(plan_path)['sha256']==a.plan_sha256 and binding(disposition_path)['sha256']==a.disposition_sha256 and M.discover(api)==plan['method_inventory'],'aggregate final plan/disposition/method drift')
 for row in [*event_bindings,*[x['report_binding'] for x in records]]:require(binding(ROOT/row['path'])==row,'completed evidence changed at aggregate exit')
 value={'schema_version':'lab-final-api-cross-namespace-regression-aggregate/v1-candidate','result':'PASS' if exact and ordered and not problems else 'FAIL','started_at':entry,'ended_at':datetime.now(timezone.utc).isoformat(),'api_directory':plan['api_directory'],'source_sha256':a.source,'profile_sha256':a.profile,'original_plan_binding':binding(plan_path),'execution_disposition_binding':binding(disposition_path),'source_manifest_binding':binding(api/'source-manifest.json'),'profile_binding':binding(api/'contract-profile.json'),'collector_binding':binding(Path(__file__).resolve()),'are_boundary_binding':disposition['are_boundary_binding'],'exact_method_accounting':exact,'actual_methods':len(cases),'original_declared_methods':323,'added_installation_release_methods':22,'declared_method_inventory_sha256':disposition['method_inventory_sha256'],'cases':cases,'worker_records':records,'failed_buckets':problems,'actual_ir_started_after_all_other_terminals':ordered,'latest_other_terminal':max(other_terminals).isoformat(),'actual_ir_start':starts[ir_bucket].isoformat(),'full_history_entry_exit_guards':True,'inherited_ast_comparison':plan['method_ast_comparison'],'worker_report_or_event_bytes_rewritten':False,'qualification_transferred_to_successor':False,'original_clocks_or_callbacks_changed':False,'method_or_fixture_monkeypatches':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'human_pilot_complete':False,'goal_complete':False,'claim_ceiling':'Exact345 regression methods for this one unchanged API12 producer and original0177 method plan, using independently scoped actual Session/ordinary/IR reports and actual terminal ordering. No source renewal, human response, canonical admission, release approval or whole Lab completion.'}
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'result':value['result'],'actual_methods':len(cases),'failed_buckets':problems,'ir_ordering':ordered,'report_binding':binding(out)}),flush=True);return 0 if value['result']=='PASS' else 1
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception:traceback.print_exc();raise SystemExit(1)
