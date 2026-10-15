"""Run the original incomplete-core and failed-schema cases without altered clocks.

This scoped successor check does not replace the full original runtime suites.
The prior CPU diagnostic must terminate before starting these owned fixtures.
"""
import ast,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v46'
PARENT=API.parent/'api-v45'
SOURCE='db77ca7aa91fe4d8b5e25f2f23b4b32610a40f83dfd20ab6bcf50fcd06326118'
PROFILE='251d06f0bd757a392b33508d82b70a15bd0b8d61b1694bb1617f1d3532f11872'
METHODS=['test_14_uncertain_core_failure_stays_pending','test_15_invalid_schema_is_never_assessed']
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def method_asts(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name in METHODS}
def main():
 terminal=RUN/'API45-failure12-cpu-measurement-terminal-0001.json'
 assert terminal.is_file(),'existing CPU measurement must be terminal before original-case fixtures'
 assert json.loads(terminal.read_bytes())['actual_exit_code']==0,'inspect failed diagnostic before successor fixtures'
 assert json.loads((RUN/'API45-failure12-cpu-measurement-0001.json').read_bytes())['result']=='MEASURED'
 selection=json.loads((RUN/'API46-core-schema-selection-0001.json').read_bytes())
 assert selection['runner_binding']==bind(Path(__file__).resolve())
 assert selection['source_binding']==bind(API/'source-manifest.json') and selection['profile_binding']==bind(API/'contract-profile.json')
 assert selection['ordered_original_methods']==METHODS
 original=method_asts(PARENT/'test_failure_api.py');actual=method_asts(API/'test_failure_api.py')
 assert original==actual and len(actual)==2
 name='_cal_api46_original_core_schema_checks'
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
 package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 guard=__import__(name+'.guard',fromlist=['verify']);manifest=guard.verify(SOURCE)
 assert manifest['freeze_precedes_new_owned_fixture_effects'] and bind(API/'contract-profile.json')['sha256']==PROFILE
 module=__import__(name+'.test_failure_api',fromlist=['FailureAPI']);module.SOURCE=SOURCE;module.PROFILE=PROFILE
 cases=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):
   super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
  def addFailure(self,test,error):
   super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
  def addError(self,test,error):
   super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
 result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.TestSuite([module.FailureAPI(method) for method in METHODS]))
 guard.verify(SOURCE);assert bind(API/'contract-profile.json')['sha256']==PROFILE
 assert original==method_asts(PARENT/'test_failure_api.py')==method_asts(API/'test_failure_api.py')
 observations=[]
 for p in sorted((API/'receipts/per-call-observations').glob('*.json')):
  v=json.loads(p.read_bytes())
  if v['test_ref'].rsplit('.',1)[-1] in METHODS:observations.append(bind(p))
 value={'schema_version':'lab-original-successor-core-schema-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==2 and len(cases)==2 else 'FAIL','actual_tests':result.testsRun,'expected_tests':2,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'runner_binding':bind(Path(__file__).resolve()),'selection_binding':bind(RUN/'API46-core-schema-selection-0001.json'),'preceding_CPU_diagnostic_terminal_binding':bind(terminal),'original_test_source_binding':bind(PARENT/'test_failure_api.py'),'successor_test_source_binding':bind(API/'test_failure_api.py'),'original_method_AST_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in original.items()},'original_method_bodies_unchanged':True,'actual_public_observation_bindings':observations,'registered_owned_fixture_cleanup_paths_completed':result.testsRun==2 and len(cases)==2 and not result.errors,'original_reader_entry_exit_and_source_guards_completed':True,'original_real_clocks_and_900_second_bound_unchanged':True,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'claim_ceiling':'Only two unchanged original public cases over owned isolated candidate fixtures. Full original runtime suites, deadline delivery, current Actor/source integration and admission remain outstanding.'}
 with (RUN/'API46-core-schema-focused-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':value['result'],'actual_tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'whole_API_qualified':False}),flush=True)
 raise SystemExit(0 if value['result']=='PASS' else 1)
if __name__=='__main__':main()
