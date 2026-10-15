"""Two unchanged original methods after nine guarded original terminals.

Original345 FAIL evidence stays unchanged. No qualification transfer, source
renewal, fixture/clock/callback substitution or profiler is selected.
"""
from datetime import datetime,timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HELPER=RUN/'diagnose-API12-classification-performance-action-0148.py'
HELPER_SHA='604a9e64b563b99b5ad06296a695a2f37a97e078ede6cfab19341e4975cbb6c6'
REPORT=RUN/'API12-original-deadline-replay-action-0148.json'
EVENTS=RUN/'API12-original-deadline-replay-action-0148.events.jsonl'
IR_DISPOSITION=RUN/'final-api-regression-ir-disposition-0190.json'
IR_SHA='fbc46388802bb5e10eadc437f2c21bd7e07268f6bfef42b4bce0e6a17f7fda62'
PLAN=RUN/'final-api-regression-plan-0177.json'
PLAN_SHA='8447e875378112d2fe73a158da75f40c02dc6e63fc65ad08c7e2ef7a6025f03a'
METHODS=[('test_classification_api','ClassificationAPI','test_04_same_key_different_control_inputs_conflicts'),
 ('test_failure_api','FailureAPI','test_01_exact_original_ChangeProposal_and_connections')]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def bind(p):return {'path':str(Path(p).relative_to(ROOT)),'sha256':sha(Path(p).read_bytes())}
def event(phase,**values):
 row={'phase':phase,'at':datetime.now(timezone.utc).isoformat(),**values}
 with EVENTS.open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
 print(json.dumps(row,sort_keys=True),flush=True)
def terminal_reports(H):
 require(bind(IR_DISPOSITION)['sha256']==IR_SHA and bind(PLAN)['sha256']==PLAN_SHA,'frozen original scheduling plan/disposition differs')
 d=json.loads(IR_DISPOSITION.read_bytes());p=json.loads(PLAN.read_bytes())
 label='sequential-'+sha(b'subset:installation-release:tamper')[:16]
 paths=[ROOT/n for n in d['tamper_predecessor_reports']]+[RUN/('final-api-regression-0173-0190.'+label+'.json')]
 require(len(paths)==len(set(paths))==9,'exact9 distinct original reports required')
 missing=[str(path.relative_to(ROOT)) for path in paths if not path.exists()]
 if missing:return None,missing
 records=[]
 for path in paths:
  x=json.loads(path.read_bytes())
  require(x['source_guarded_entry_completed'] and x['source_guarded_exit_completed'] and x['execution_error'] is None and x['exit_guard_error'] is None,'original worker did not reach guarded terminal')
  require(x['exact_method_accounting'] and x['actual_methods']==len(x['selected_methods']),'original exact method accounting incomplete')
  require(x['worker_plan_binding']==bind(PLAN) and x['files'][0]==bind(H.API/'source-manifest.json') and x['files'][1]==bind(H.API/'contract-profile.json'),'original worker pins/plan differ')
  ep=ROOT/x['events_binding']['path'];require(bind(ep)==x['events_binding'],'original terminal events changed')
  es=[json.loads(line) for line in ep.read_text().splitlines()];last=es[-1]
  require(last['phase']=='terminal' and last['result']==x['result'] and last['full_history_exit_guard_passed'],'actual original guarded terminal required')
  records.append({'report_binding':bind(path),'events_binding':bind(ep),'original_result':x['result'],'original_actual_methods':x['actual_methods'],'terminal_at':last['at']})
 require(sum(r['original_actual_methods'] for r in records)==345,'exact all345 original methods required')
 return records,[]

def main():
 require(not REPORT.exists() and not EVENTS.exists(),'immutable new replay output required')
 require(bind(HELPER)['sha256']==HELPER_SHA,'independently pinned diagnostic helper differs')
 spec=importlib.util.spec_from_file_location('_cal_original_replay_helper_action_0148',HELPER);H=importlib.util.module_from_spec(spec);sys.modules[spec.name]=H;spec.loader.exec_module(H)
 caller=bind(Path(__file__));started=datetime.now(timezone.utc).isoformat();cases=[];error=None;exit_error=None;guard_entry=False;guard_exit=False;g=None;predecessors=None;period=None
 event('supervisor-starting',selected_original_methods=['.'.join(m) for m in METHODS],no_test_started=True)
 try:
  while True:
   H.period_check();predecessors,missing=terminal_reports(H)
   if predecessors is not None:break
   event('waiting-nine-original-guarded-terminals',missing_reports=missing,no_test_started=True)
   time.sleep(30)
  fd=os.open(H.LOCK,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   fcntl.flock(fd,fcntl.LOCK_SH)
   try:
    predecessors,missing=terminal_reports(H);require(predecessors is not None,'original guarded terminals unavailable at locked entry')
    period=H.period_check();g,_=H.bootstrap('_cal_API12_original_deadline_replay_action_0148');guard_entry=True
    event('locked-execution-starting',original345_results_preserved=True,source_sha256=H.SOURCE,profile_sha256=H.PROFILE)
    for module,cls,method in METHODS:
     H.period_check();event('original-method-running',declared_method=module+'.py:'+cls+'.'+method)
     row=H.run_original('_cal_API12_original_deadline_replay_action_0148',module,cls,method)
     cases.append(row);event('original-method-completed',declared_method=row['declared_method'],result=row['result'])
   except Exception:error=traceback.format_exc()
   finally:
    try:
     if g is not None:g.verify(H.SOURCE);guard_exit=True
     H.period_check();require(bind(Path(__file__))==caller and bind(HELPER)['sha256']==HELPER_SHA,'replay caller/helper changed')
     for r in predecessors or []:
      require(bind(ROOT/r['report_binding']['path'])==r['report_binding'] and bind(ROOT/r['events_binding']['path'])==r['events_binding'],'original terminal evidence changed during replay')
    except Exception:exit_error=traceback.format_exc()
  finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 except Exception:error=(error or '')+traceback.format_exc()
 passed=len(cases)==2 and all(r['result']=='PASS' and r['original_cleanup_completed'] for r in cases) and guard_entry and guard_exit and error is None and exit_error is None
 value={'schema_version':'lab-unchanged-API12-original-deadline-replay/v1-candidate','result':'PASS' if passed else 'FAIL',
  'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'actual_original_methods':sum(r['actual_methods'] for r in cases),'cases':cases,
  'source_sha256':H.SOURCE,'profile_sha256':H.PROFILE,'full_source_guarded_entry':guard_entry,'full_source_guarded_exit':guard_exit,
  'execution_error':error,'exit_guard_error':exit_error,'all_nine_original_guarded_terminal_reports':predecessors,'original_Source5_period':period,
  'actual_shared_lock_held_through_original_cleanup_and_full_guards':guard_entry,'replay_caller_binding':caller,'helper_binding':bind(HELPER),
  'ARE_boundary_binding':bind(H.ARE),'original345_regression_replaced':False,'original_regression_failures_preserved':True,
  'original_test_AST_or_clock_or_fixture_or_production_or_callback_monkeypatches':False,'profiler_or_tracer_selected':False,
  'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'task_complete':False,'goal_complete':False,
  'claim_ceiling':'Two actual unchanged original methods after all345 original guarded terminals, one original class lifetime each, fresh owned fixtures and original600s request deadlines. Original failures remain counterevidence. No alloriginalPASS, wholeAPI, R03, AC01, human pilot or R08 closure.'}
 with REPORT.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
 event('terminal',result=value['result'],actual_original_methods=value['actual_original_methods'],report_binding=bind(REPORT))
 print(json.dumps({'result':value['result'],'report_binding':bind(REPORT),'whole_API_qualified':False}),flush=True)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
