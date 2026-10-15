"""Instrumented original Classification04 diagnosis; never qualification.

A new caller selects unchanged API12, real Source5 period and original class
setup/test/cleanup/teardown. cProfile captures function metadata and timings,
never frame locals, RAM notes, signing keys or policy bodies.
"""
import ast
import cProfile
from datetime import datetime,timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pstats
import sys
import time
import traceback
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12'
SOURCE='5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PROFILE='2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'
LOCK=RUN/'final-api-regression-0173-0190.execution.lock'
ARE=RUN/'ARE-performance-diagnostic-boundary-0194.json'
PERIOD=ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json'
REPORT=RUN/'API12-classification-performance-diagnostic-action-0148.json'
STATS=RUN/'API12-classification-performance-diagnostic-action-0148.pstats'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):
 p=Path(p);return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def now():return datetime.now(timezone.utc)
def require(ok,reason):
 if not ok:raise ValueError(reason)
def original_ast(module_path,class_name,method):
 tree=ast.parse(module_path.read_bytes());cls=next(c for c in tree.body if isinstance(c,ast.ClassDef) and c.name==class_name)
 selected=next(n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==method)
 return sha(ast.dump(selected,include_attributes=False).encode())
def period_check():
 manifest=json.loads((API/'source-manifest.json').read_bytes());require(sha((API/'source-manifest.json').read_bytes())==SOURCE,'API12 independent source pin changed')
 row=next(r for r in manifest['files'] if r['path']==str(PERIOD.relative_to(ROOT)))
 require(bind(PERIOD)==row,'retained Source5 period bytes changed')
 x=json.loads(PERIOD.read_bytes());current=now()
 require(datetime.fromisoformat(x['not_before'])<=current<datetime.fromisoformat(x['expires_at']),'original Source5 absolute period is not current; no renewal')
 return {'checked_at':current.isoformat(),'period_binding':bind(PERIOD),'not_before':x['not_before'],'expires_at':x['expires_at']}
def bootstrap(name):
 require(sha((API/'source-manifest.json').read_bytes())==SOURCE and sha((API/'contract-profile.json').read_bytes())==PROFILE,'independent API12 pins differ')
 m=json.loads((API/'source-manifest.json').read_bytes());rows={r['path']:r for r in m['files']}
 for n in ('__init__.py','guard.py'):require(bind(API/n)==rows[str((API/n).relative_to(ROOT))],'bootstrap outside frozen source')
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 g=__import__(name+'.guard',fromlist=['verify']);g.verify(SOURCE);period_check()
 return g,m

def run_original(name,module_name,class_name,method,profiler=None):
 module=__import__(name+'.'+module_name,fromlist=[class_name]);module.SOURCE=SOURCE;module.PROFILE=PROFILE
 cls=getattr(module,class_name);function=getattr(cls,method);identity=function
 original_binding=bind(API/(module_name+'.py'));method_ast=original_ast(API/(module_name+'.py'),class_name,method)
 cases=[];errors=[];setup=False;started=now();clock=time.monotonic()
 observer=API/'receipts/per-call-observations';before=set(observer.glob('*.json')) if observer.exists() else set()
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
  def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
  def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
 result=Result(unittest.runner._WritelnDecorator(sys.stderr),True,2)
 try:
  cls.setUpClass();setup=True
  print(json.dumps({'phase':'original-method-starting','method':module_name+':'+class_name+'.'+method,'at':now().isoformat(),'instrumented':profiler is not None}),flush=True)
  if profiler is not None:profiler.enable()
  try:cls(method).run(result)
  finally:
   if profiler is not None:profiler.disable()
 finally:
  if setup:
   try:cls.tearDownClass()
   except Exception:errors.append({'phase':'original-class-teardown','detail':traceback.format_exc()})
  else:errors.append({'phase':'original-class-setup','detail':'original setUpClass did not complete'})
 require(getattr(cls,method) is identity and bind(API/(module_name+'.py'))==original_binding and original_ast(API/(module_name+'.py'),class_name,method)==method_ast,'original method identity/bytes/AST changed')
 require(not errors,'original class fixture cleanup or source exit failed')
 after=set(observer.glob('*.json')) if observer.exists() else set();owned_observations=[]
 for p in sorted(after-before):
  x=json.loads(p.read_bytes())
  if x['test_ref']==name+'.'+module_name+'.'+class_name+'.'+method:owned_observations.append(bind(p))
 return {'declared_method':module_name+'.py:'+class_name+'.'+method,'cases':cases,'started_at':started.isoformat(),'finished_at':now().isoformat(),
  'elapsed_seconds':time.monotonic()-clock,'actual_methods':result.testsRun,'result':'PASS' if result.wasSuccessful() and result.testsRun==1 else 'FAIL',
  'failures':len(result.failures),'errors':len(result.errors),'subtest_failures':len([x for x in result.failures if isinstance(x[0],unittest.case._SubTest)]),
  'original_class_setup_teardown_completed':setup and not errors,'original_cleanup_completed':setup and not errors and not result.errors,
  'original_function_identity_retained':True,'original_method_binding':original_binding,'original_method_ast_sha256':method_ast,
  'actual_authenticated_public_calls':len(owned_observations),'public_call_observation_bindings':owned_observations}

def main():
 require(not REPORT.exists() and not STATS.exists(),'immutable new diagnostic paths required')
 started=now();clock=time.monotonic();profiler=cProfile.Profile();value={};error=None;exit_error=None;g=None;method=None
 driver=bind(Path(__file__));are=bind(ARE);source_entry=False;source_exit=False;first_period=None
 fd=os.open(LOCK,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  fcntl.flock(fd,fcntl.LOCK_SH)
  try:
   require(json.loads(ARE.read_bytes())['result']['ok'] is True,'actual non-authorizing ARE boundary required')
   first_period=period_check();g,_=bootstrap('_cal_API12_performance_diagnostic_action_0148');source_entry=True
   method=run_original('_cal_API12_performance_diagnostic_action_0148','test_classification_api','ClassificationAPI','test_04_same_key_different_control_inputs_conflicts',profiler)
  except Exception:error=traceback.format_exc()
  finally:
   profiler.disable()
   try:
    if g is not None:g.verify(SOURCE);source_exit=True
    require(bind(Path(__file__))==driver and bind(ARE)==are,'diagnostic caller/boundary changed')
    period_check()
   except Exception:exit_error=traceback.format_exc()
  profiler.dump_stats(str(STATS));stats=pstats.Stats(profiler)
  functions=[]
  for (filename,line,function),(primitive,calls,self_seconds,cumulative_seconds,callers) in stats.stats.items():
   functions.append({'path':filename,'line':line,'function':function,'primitive_calls':primitive,'calls':calls,'self_seconds':self_seconds,'cumulative_seconds':cumulative_seconds})
  functions.sort(key=lambda x:x['cumulative_seconds'],reverse=True)
  host_guards=[r for r in functions if r['path']==str(API/'guard.py') and r['function']=='verify']
  value={'schema_version':'lab-instrumented-API12-performance-diagnostic/v1-candidate','result':'DIAGNOSTIC-COMPLETE' if source_entry and source_exit and error is None and exit_error is None else 'DIAGNOSTIC-INCOMPLETE',
   'started_at':started.isoformat(),'finished_at':now().isoformat(),'elapsed_seconds':time.monotonic()-clock,
   'instrumentation':'cProfile surrounds only the original TestCase.run including its original fixture effects and cleanup; original class setup/teardown and full guards run unprofiled. Instrumentation changes timing; no qualification is inferred.',
   'diagnostic_original_method':method,'full_source_entry':source_entry,'full_source_exit':source_exit,'error':error,'exit_guard_error':exit_error,
   'initial_original_Source5_period':first_period,'actual_full_API_history_guard_calls':host_guards,'top_cumulative_functions':functions[:100],
   'all_profiled_functions':functions,'profile_binding':bind(STATS),'source_manifest_binding':bind(API/'source-manifest.json'),
   'contract_profile_binding':bind(API/'contract-profile.json'),'diagnostic_caller_binding':driver,'ARE_boundary_binding':are,
   'shared_execution_lock':str(LOCK.relative_to(ROOT)),'shared_lock_held_through_full_guard_and_original_cleanup':True,
   'clock_fixture_production_or_callback_monkeypatches':False,'frame_locals_RAM_or_private_keys_recorded':False,
   'qualification':False,'whole_API_qualified':False,'original_regression_failures_preserved':True,
   'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False}
  with REPORT.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':value['result'],'report_binding':bind(REPORT),'original_method_result':None if method is None else method['result'],'host_guard_costs':host_guards,'qualification':False}),flush=True)
 return 0 if value['result']=='DIAGNOSTIC-COMPLETE' else 1
if __name__=='__main__':raise SystemExit(main())
