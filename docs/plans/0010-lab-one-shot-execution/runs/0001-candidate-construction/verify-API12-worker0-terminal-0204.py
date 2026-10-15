"""Independent saved-evidence verifier; no tests, fixture effects or exit rewriting."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
def require(value,message):
 if not value:raise ValueError(message)
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_bytes())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def main():
 p=argparse.ArgumentParser()
 for key in ('source','profile','plan-sha256','report-sha256','caller-sha256'):p.add_argument('--'+key,required=True)
 p.add_argument('--original-command-exit',type=int,required=True);p.add_argument('--original-tool-session',type=int,required=True)
 a=p.parse_args();api=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12';plan_path=RUN/'final-api-regression-plan-0177.json';report=RUN/'final-api-regression-0173-0183.worker-0.json';log=RUN/'final-api-regression-0173-0183-worker-0.log';out=RUN/'API12-worker0-terminal-verification-0204.json';are=RUN/'ARE-worker0-terminal-boundary-0195.json'
 require(not out.exists(),'new exclusive independent verification required')
 require(bind(Path(__file__))['sha256']==a.caller_sha256,'independent actual verifier pin required')
 require(a.original_command_exit==143 and a.original_tool_session==28927,'retain exact parent-observed original tool terminal; never substitute verifier exit')
 receipt=read(are);require(receipt['ok'] and receipt['authority_effect']=='none','bounded non-authorizing verification receipt required')
 require(bind(report)['sha256']==a.report_sha256 and bind(plan_path)['sha256']==a.plan_sha256,'exact saved report and original plan pins required')
 inputs=[bind(report),bind(log),bind(plan_path),bind(are),bind(Path(__file__))]
 R=load('_cal_terminal0204_original_runner',RUN/'final-api-regression-0173.py')
 original_args=argparse.Namespace(api_directory=str(api),source=a.source,profile=a.profile,plan=str(plan_path),plan_sha256=a.plan_sha256,output_prefix='final-api-regression-0173-0183')
 checked_api,checked_plan,plan=R.load_plan(original_args);require(checked_api==api and checked_plan==plan_path,'exact original selection required')
 G=R.guard_for(api);G.verify(a.source);started=datetime.now(timezone.utc).isoformat()
 r=read(report);expected=plan['workers']['0'];require(len(expected)==48 and r['bucket']=='worker:0' and r['selected_methods']==expected and r['worker_plan_binding']==bind(plan_path),'exact original48 bucket/plan required')
 require(r['files']==[bind(api/'source-manifest.json'),bind(api/'contract-profile.json'),bind(RUN/'final-api-regression-0173.py')],'actual saved original producer/caller differs')
 for row in [*r['files'],r['events_binding']]:require(bind(ROOT/row['path'])==row,'saved original source or event bytes differ')
 inputs.extend(r['files']);inputs.append(r['events_binding'])
 events=[json.loads(x) for x in (ROOT/r['events_binding']['path']).read_text().splitlines()]
 require(len(events)==100 and events[0]['phase']=='starting' and events[-1]['phase']=='terminal','complete exact original100-event lifecycle required')
 require(sum(x['phase']=='starting' for x in events)==sum(x['phase']=='terminal' for x in events)==1,'unique original lifecycle required')
 first,last=events[0],events[-1]
 require(first['bucket']=='worker:0' and first['source_pin']==a.source and first['profile_pin']==a.profile and first['worker_plan_binding']==bind(plan_path),'actual original start binding differs')
 times=[datetime.fromisoformat(x['at']) for x in events];require(all(t.tzinfo is not None for t in times) and all(x<=y for x,y in zip(times,times[1:])),'actual real event chronology required')
 running=[x['declared_method'] for x in events if x['phase']=='running'];cases=[{k:v for k,v in x.items() if k not in ('at','phase')} for x in events if x['phase']=='case-completed'];ids=[x['declared_method'] for x in cases]
 require(cases==r['cases'] and running==ids and len(ids)==len(set(ids))==48 and set(ids)==set(expected),'exact48 actual running/completion/report accounting required')
 require(r['result']==last['result']=='PASS' and r['actual_methods']==last['actual_methods']==48 and r['exact_method_accounting'] and last['exact_method_accounting'] and all(x['result']=='PASS' for x in cases),'saved actual48 outcomes must pass')
 require(r['source_guarded_entry_completed'] and r['source_guarded_exit_completed'] and last['full_history_exit_guard_passed'] and r['execution_error'] is None and r['exit_guard_error'] is None and not r['fixture_errors'] and not r['subtest_failures'],'original complete guards/fixtures required')
 require(r['inherited_ast_comparison']==plan['method_ast_comparison'] and r['original_clocks_or_callbacks_changed'] is False and r['method_or_fixture_monkeypatches'] is False and r['authority_effect']=='none' and r['actual_owner_outcome'] is None,'original method/clocks/authority proof differs')
 require(r['fixture_pins'] and all(x['source']==a.source and x['profile']==a.profile for x in r['fixture_pins']),'actual original fixture pins required')
 text=log.read_text();require('Ran 48 tests in ' in text and '\nOK\n' in text,'original unittest successful post-cleanup summary required')
 printed=[json.loads(line) for line in text.splitlines() if line.startswith('{"result":')];require(printed and printed[-1]=={'result':'PASS','actual_methods':48,'report_binding':bind(report)},'actual original final summary after report close/lock release required')
 cleanup_files=[api/'test_preparation.py',api/'test_generated_candidate.py',api/'test_challenge_api.py',api/'challenge_fixture.py']
 cleanup_bindings=[bind(x) for x in cleanup_files];inputs.extend(cleanup_bindings)
 require({plan['method_inventory']['methods'][m]['class'] for m in expected}=={'Preparation','GeneratedWorkflow'},'bounded original cleanup classes differ')
 # Original TextTestRunner.run returned, with zero fixture errors. unittest
 # completes per-test and class cleanup before this summary. Physical root
 # names were not saved: do not infer independently enumerated absence.
 G.verify(a.source);require(R.load_plan(original_args)[2]==plan,'full original final AST/plan drift')
 for row in inputs:require(bind(ROOT/row['path'])==row,'original evidence changed during independent verification')
 value={'schema_version':'lab-independent-worker-terminal-verification/v1-candidate','result':'PASS','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'api_directory':api.relative_to(ROOT).as_posix(),'source_sha256':a.source,'profile_sha256':a.profile,'original_report_binding':bind(report),'original_events_binding':r['events_binding'],'original_log_binding':bind(log),'original_plan_binding':bind(plan_path),'verifier_binding':bind(Path(__file__)),'are_boundary_binding':bind(are),'files':inputs,'actual_saved_cases_verified':48,'cases':cases,'exact_original_method_accounting':True,'original_started_at':first['at'],'original_terminal_at':last['at'],'original_pid':first['pid'],'full_history_entry_exit_guards':True,'original_unittest_cleanup_hooks_completed_without_fixture_error':True,'cleanup_source_bindings':cleanup_bindings,'individual_original_temporary_root_absence_independently_verified':None,'cleanup_limit':'Individual owned root paths were not retained in original worker evidence. Original successful unittest cleanup hooks and class teardown are verified; independent physical enumeration is unavailable.','actual_original_runner_final_print_observed':True,'original_runner_reached_post_report_close_and_lock_release':True,'original_command_terminal':{'tool_session':a.original_tool_session,'observed_exit_code':a.original_command_exit,'provenance':'Parent actual tool28927 polling observation supplied in delegated terminal audit; no independent saved tool receipt.','parent_termination_reported':False,'termination_cause':None,'original_exit_zero_verified':False},'verifier_does_not_replace_original_command_exit':True,'original_cases_rerun':0,'original_report_or_events_rewritten':False,'qualification_transferred_to_successor':False,'original_clocks_or_callbacks_changed':False,'method_or_fixture_monkeypatches':False,'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Independent verification of exact existing48 checks, complete original evidence and successful original cleanup-hook/guard closure only. Original command exit143 is retained with unknown cause; no original exit0, physical per-root absence, full34-operation acceptance, human pilot or R08 completion inferred.'}
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'result':'PASS','saved_cases_verified':48,'original_command_exit':143,'original_exit_zero_verified':False,'report_binding':bind(out)}),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
