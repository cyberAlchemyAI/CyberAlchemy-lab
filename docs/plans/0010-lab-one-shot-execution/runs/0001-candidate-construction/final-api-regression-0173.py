"""Explicit immutable-plan final API workers/aggregation; real unchanged tests."""
import argparse
from datetime import datetime,timezone
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import traceback
import unittest

sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'

RUN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_final_api_methods_0173',RUN/'final-api-regression-map-0173.py');M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)

def load_plan(a):
 api=M.path(a.api_directory);plan_path=M.path(a.plan)
 M.require(M.binding(plan_path)['sha256']==a.plan_sha256,'exact frozen worker plan hash required')
 plan=json.loads(plan_path.read_bytes())
 M.require(plan['schema_version']=='lab-final-api-regression-plan/v1-candidate' and plan['api_directory']==api.relative_to(M.ROOT).as_posix() and plan['source_sha256']==a.source and plan['profile_sha256']==a.profile,'CLI/plan API directory or independent pins differ')
 for row in plan['tools_bindings']:M.require(M.binding(M.ROOT/row['path'])==row,'frozen actual regression caller changed')
 M.require(M.discover(api)==plan['method_inventory'],'actual final API method/class/fixture AST inventory changed')
 original=M.path(plan['original_api_directory'])
 M.require(M.binding(original/'source-manifest.json')['sha256']==plan['original_source_sha256'] and M.binding(original/'contract-profile.json')['sha256']==plan['original_profile_sha256'],'original baseline pins changed')
 M.require(M.binding(M.ROOT/plan['original_plan_binding']['path'])==plan['original_plan_binding'],'original323 worker plan changed')
 old=M.discover(original);M.require(old==plan['original_method_inventory'] and M.compare(old,plan['method_inventory'])==plan['method_ast_comparison'],'exact inherited AST comparison changed')
 M.require(len(plan['original_declared_methods'])==323 and plan['method_ast_comparison']['acceptable'],'original323 retention/fixture revision proof unavailable')
 M.require(M.binding(api/'source-manifest.json')['sha256']==a.source and M.binding(api/'contract-profile.json')['sha256']==a.profile,'actual final producer pins differ')
 M.require(re.fullmatch(r'final-api-regression-0173-[A-Za-z0-9_-]{1,80}',a.output_prefix) is not None,'owned explicit output prefix required')
 return api,plan_path,plan

def guard_for(api):
 spec=importlib.util.spec_from_file_location('_cal_final_regression_guard_0173',api/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g

def buckets(plan):return {**{'sequential:'+k:v for k,v in plan['sequential_classes'].items()},**{'worker:'+k:v for k,v in plan['workers'].items()}}
def label(bucket):return bucket.replace(':','-') if bucket.startswith('worker:') else 'sequential-'+M.sha(bucket.encode())[:16]
def output(a,bucket):return RUN/(a.output_prefix+'.'+label(bucket)+'.json')

def run_worker(a,api,plan_path,plan):
 choices=buckets(plan);M.require(a.worker in choices,'exact declared whole-class bucket required');chosen=choices[a.worker]
 report=output(a,a.worker);events=report.with_suffix('.events.jsonl');M.require(not report.exists() and not events.exists(),'new exclusive report/event paths required')
 def event(value):
  with events.open('a') as stream:stream.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**value},sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
 event({'phase':'starting','pid':os.getpid(),'bucket':a.worker,'source_pin':a.source,'profile_pin':a.profile,'worker_plan_binding':M.binding(plan_path)})
 # Shared worker locks exclude source-corrupting sequential classes. Fixtures
 # start after obtaining this actual lock; no clock/deadline is extended.
 lock_path=RUN/(a.output_prefix+'.execution.lock');fd=os.open(lock_path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
 cases=[];fixture_errors=[];subtests=[];pins=[];selected=[];failure=None;exit_error=None;entry=False;actual=0
 g=guard_for(api)
 try:
  event({'phase':'waiting-execution-lock','exclusive':a.worker.startswith('sequential:')});fcntl.flock(fd,fcntl.LOCK_EX if a.worker.startswith('sequential:') else fcntl.LOCK_SH)
  g.verify(a.source);entry=True;M.require(load_plan(a)[2]==plan,'frozen plan/input changed while waiting for the actual execution lock');event({'phase':'full-history-entry-guard-passed'})
  name='_cal_final_api_0173_'+label(a.worker).replace('-','_');spec=importlib.util.spec_from_file_location(name,api/'__init__.py',submodule_search_locations=[str(api)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
  suite=unittest.TestSuite();loaded={};identities={}
  for ident in chosen:
   row=plan['method_inventory']['methods'][ident];stem=Path(row['file']).stem
   if stem not in loaded:loaded[stem]=__import__(name+'.'+stem,fromlist=['*'])
   cls=getattr(loaded[stem],row['class']);M.require(issubclass(cls,unittest.TestCase),'declared original test class required')
   test=cls(row['method']);suite.addTest(test);identities[test.id()]=ident;selected.append(ident)
  # SOURCE/PROFILE are injected only into selected test modules and the
  # original export fixture helper. No method, callback, clock or production
  # module global is replaced.
  helper=__import__(name+'.export_test_base',fromlist=['*']);fixtures=list(loaded.values())+[helper]
  for fixture in fixtures:
   fixture.SOURCE=a.source;fixture.PROFILE=a.profile;pins.append({'module':fixture.__name__,'source':a.source,'profile':a.profile})
  M.require(suite.countTestCases()==len(chosen)==len(identities) and set(selected)==set(chosen),'exact selected test accounting required')
  class Result(unittest.TextTestResult):
   active={}
   def startTest(self,test):
    super().startTest(test);ident=identities[test.id()];self.active[test.id()]={'test':test.id(),'declared_method':ident,'result':'PASS'};event({'phase':'running','declared_method':ident,'test':test.id()})
   def failed(self,test,error,status):
    row=self.active.get(test.id());detail=self._exc_info_to_string(error,test)
    if row is None:fixture_errors.append({'fixture':test.id(),'result':status,'detail':detail})
    else:row.update(result=status,detail=detail)
   def addFailure(self,test,error):super().addFailure(test,error);self.failed(test,error,'FAIL')
   def addError(self,test,error):super().addError(test,error);self.failed(test,error,'ERROR')
   def addSkip(self,test,reason):
    super().addSkip(test,reason);self.active[test.id()].update(result='SKIP',detail=reason)
   def addExpectedFailure(self,test,error):
    super().addExpectedFailure(test,error);self.failed(test,error,'EXPECTED-FAILURE')
   def addUnexpectedSuccess(self,test):
    super().addUnexpectedSuccess(test);self.active[test.id()].update(result='UNEXPECTED-SUCCESS')
   def addSubTest(self,test,subtest,error):
    super().addSubTest(test,subtest,error)
    if error is not None:
     self.failed(test,error,'FAIL' if issubclass(error[0],test.failureException) else 'ERROR');subtests.append({'test':test.id(),'subtest':str(subtest),'detail':self._exc_info_to_string(error,subtest)})
   def stopTest(self,test):
    row=self.active.pop(test.id());cases.append(row);event({'phase':'case-completed',**row});super().stopTest(test)
  result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);actual=result.testsRun
 except BaseException:failure=traceback.format_exc();event({'phase':'execution-exception','detail':failure})
 finally:
  try:g.verify(a.source);M.require(load_plan(a)[2]==plan,'final frozen plan/input drift')
  except BaseException:exit_error=traceback.format_exc()
  actual_rows=[row['declared_method'] for row in cases]
  exact=len(actual_rows)==len(set(actual_rows))==actual==len(chosen) and set(actual_rows)==set(chosen)
  passed=entry and failure is None and exit_error is None and exact and not fixture_errors and all(row['result']=='PASS' for row in cases)
  event({'phase':'terminal','result':'PASS' if passed else 'FAIL','actual_methods':actual,'exact_method_accounting':exact,'full_history_exit_guard_passed':exit_error is None})
  value={'schema_version':'lab-final-api-worker-qualification/v1-candidate','result':'PASS' if passed else 'FAIL','bucket':a.worker,'selected_methods':chosen,'actual_methods':actual,'cases':cases,'fixture_errors':fixture_errors,'subtest_failures':subtests,'exact_method_accounting':exact,'fixture_pins':pins,'worker_plan_binding':M.binding(plan_path),'events_binding':M.binding(events),'files':[M.binding(api/'source-manifest.json'),M.binding(api/'contract-profile.json'),M.binding(Path(__file__).resolve())],'source_guarded_entry_completed':entry,'source_guarded_exit_completed':exit_error is None,'execution_error':failure,'exit_guard_error':exit_error,'inherited_ast_comparison':plan['method_ast_comparison'],'original_clocks_or_callbacks_changed':False,'method_or_fixture_monkeypatches':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'goal_complete':False,'claim_ceiling':'Actual exact declared final API bucket methods only. No human pilot, canonical admission, release approval or whole Lab completion inferred.'}
  with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
  fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':value['result'],'actual_methods':actual,'report_binding':M.binding(report)}),flush=True)
 return 0 if passed else 1

def aggregate(a,api,plan_path,plan):
 groups=buckets(plan);missing=[output(a,bucket).name for bucket in groups if not output(a,bucket).exists()]
 if missing:print(json.dumps({'result':'PENDING','missing_reports':missing,'goal_complete':False}));return 2
 g=guard_for(api);g.verify(a.source);cases=[];reports=[];problems=[]
 for bucket,expected in groups.items():
  p=output(a,bucket);r=json.loads(p.read_bytes());reports.append(M.binding(p))
  M.require(r['bucket']==bucket and r['selected_methods']==expected and r['worker_plan_binding']==M.binding(plan_path),'worker exact selection or plan binding differs')
  for row in [*r['files'],r['events_binding']]:M.require(M.binding(M.ROOT/row['path'])==row,'completed worker evidence/source changed')
  log=[json.loads(line) for line in (M.ROOT/r['events_binding']['path']).read_text().splitlines()]
  M.require(log and log[-1]['phase']=='terminal','complete terminal event required')
  observations=[x for x in log if x['phase']=='case-completed'];M.require([{k:v for k,v in x.items() if k not in ('at','phase')} for x in observations]==r['cases'],'exact event/case accounting differs')
  ids=[x['declared_method'] for x in r['cases']]
  M.require(len(ids)==len(set(ids)) and set(ids)<=set(expected),'duplicate or undeclared actual case')
  if not (r['result']=='PASS' and r['exact_method_accounting'] and r['source_guarded_entry_completed'] and r['source_guarded_exit_completed'] and r['actual_methods']==len(expected) and set(ids)==set(expected) and all(x['result']=='PASS' for x in r['cases'])):problems.append(bucket)
  cases.extend([{**x,'worker_report_binding':M.binding(p)} for x in r['cases']])
 all_ids=[x['declared_method'] for x in cases];exact=len(all_ids)==len(set(all_ids))==len(plan['all_declared_methods']) and set(all_ids)==set(plan['all_declared_methods'])
 g.verify(a.source);M.require(load_plan(a)[2]==plan,'aggregate final plan drift')
 value={'schema_version':'lab-final-api-regression-aggregate/v1-candidate','result':'PASS' if exact and not problems else 'FAIL','actual_methods':len(cases),'original_methods':323,'added_installation_release_methods':plan['added_installation_release_methods'],'cases':cases,'failed_buckets':problems,'exact_method_accounting':exact,'worker_plan_binding':M.binding(plan_path),'worker_report_bindings':reports,'full_history_entry_exit_guards':True,'files':[M.binding(api/'source-manifest.json'),M.binding(api/'contract-profile.json'),M.binding(Path(__file__).resolve())],'original_clocks_or_callbacks_changed':False,'method_or_fixture_monkeypatches':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'goal_complete':False,'claim_ceiling':'All exact declared final API regression methods only. Common branches, machine transport, human pilot, actual owner decision and whole Lab acceptance require their own evidence.'}
 out=RUN/(a.output_prefix+'.aggregate.json')
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'result':value['result'],'actual_methods':len(cases),'report_binding':M.binding(out)}));return 0 if value['result']=='PASS' else 1

def main():
 p=argparse.ArgumentParser();p.add_argument('--api-directory',required=True);p.add_argument('--source',required=True);p.add_argument('--profile',required=True);p.add_argument('--plan',required=True);p.add_argument('--plan-sha256',required=True);p.add_argument('--output-prefix',required=True);p.add_argument('--worker');p.add_argument('--aggregate',action='store_true');a=p.parse_args()
 M.require(a.aggregate != (a.worker is not None),'select exactly one worker or aggregate mode')
 api,plan_path,plan=load_plan(a);return aggregate(a,api,plan_path,plan) if a.aggregate else run_worker(a,api,plan_path,plan)
if __name__=='__main__':raise SystemExit(main())
