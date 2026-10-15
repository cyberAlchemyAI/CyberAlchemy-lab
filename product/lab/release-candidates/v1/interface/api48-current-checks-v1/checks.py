"""All original146 cases or all original11 controls, with exact count successors."""
import argparse,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];API=HERE.parent/'api-v48'
SOURCE='a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
PROFILE='080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9'
def main():
 p=argparse.ArgumentParser();p.add_argument('--check-source-sha256',required=True);p.add_argument('--suite',choices=['full','controls'],required=True);a=p.parse_args()
 manifest=HERE/'source-manifest.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==a.check_source_sha256
 selected=json.loads(manifest.read_bytes())
 def source_guard():
  for row in selected['files']:
   path=ROOT/row['path'];assert path.is_file() and not path.is_symlink() and not any(parent.is_symlink() for parent in path.parents)
   assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 source_guard();name='_cal_API48_strict_current_'+a.suite
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(SOURCE)
 def versioned(filename):
  module_name=name+'.versioned_'+filename.removesuffix('.py');spec=importlib.util.spec_from_file_location(module_name,HERE/filename)
  module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module;spec.loader.exec_module(module);module.PROFILE=PROFILE;return module
 if a.suite=='controls':
  suite=unittest.defaultTestLoader.loadTestsFromTestCase(versioned('test_current_controls.py').CurrentControls);expected=11
 else:
  modules=[__import__(name+'.'+n,fromlist=['*']) for n in ['test_preparation','test_preparation_corrected','test_custody_api','test_guarded_reads']]
  for module in modules:module.PROFILE=PROFILE
  sessions=[versioned('run_session_checks.py'),versioned('test_custody_sessions.py')]
  suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(modules[3]),unittest.defaultTestLoader.loadTestsFromModule(modules[2]),unittest.defaultTestLoader.loadTestsFromTestCase(modules[1].CorrectedPreparation),unittest.defaultTestLoader.loadTestsFromModule(sessions[0]),unittest.defaultTestLoader.loadTestsFromModule(sessions[1])]);expected=146
 assert suite.countTestCases()==expected;cases=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
  def addFailure(self,test,error):
   super().addFailure(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'FAIL','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
  def addError(self,test,error):
   super().addError(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'ERROR','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
 result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);source_guard();guard.verify(SOURCE)
 report={'schema_version':'lab-current-strict-full-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==expected else 'FAIL','actual_cases':result.testsRun,'expected_cases':expected,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),'source_sha256':SOURCE,'profile_sha256':PROFILE,'exact_handler_count':17,'all_original_cases_retained':True,'only_test_AST_revision':'Exact len(SUPPORTED)15 -> 17 in three separately versioned methods.','whole_API_qualified':False,'task_complete':False,'authority_effect':'none','actual_owner_outcome':None}
 receipts=HERE/'receipts';receipts.mkdir(exist_ok=True)
 with (receipts/(a.suite+'-0001.json')).open('x') as stream:json.dump(report,stream,sort_keys=True,indent=2);stream.write('\n')
 print(json.dumps({'result':report['result'],'actual_cases':result.testsRun,'suite':a.suite}),flush=True)
 raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
