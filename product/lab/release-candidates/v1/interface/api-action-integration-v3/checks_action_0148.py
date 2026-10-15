"""Bounded focused Action qualification with original exit guards and receipts."""
import argparse,hashlib,importlib.util,json,sys,time,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True);parser.add_argument('--scope',choices=['smoke','upgrade','full'],required=True);parser.add_argument('--run',required=True)
 args=parser.parse_args();n='_cal_action_0148_checks';spec=importlib.util.spec_from_file_location(n,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);module=importlib.util.module_from_spec(spec);sys.modules[n]=module;spec.loader.exec_module(module)
 d=__import__(n+'.dependencies',fromlist=['*']);tests=__import__(n+'.test_action_api',fromlist=['*']);tests.SOURCE=args.source_sha256;tests.PROFILE=args.profile_sha256
 d.guard(args.source_sha256,history=True)
 suite=unittest.TestSuite([tests.ActionAPI('test_01_actual_evaluation_dispatch_output_and_exact_semantic_retry')]) if args.scope=='smoke' else unittest.TestSuite([tests.ActionAPI(name) for name in unittest.defaultTestLoader.getTestCaseNames(tests.ActionAPI) if name.startswith(('test_16_','test_17_','test_18_','test_19_'))]) if args.scope=='upgrade' else unittest.defaultTestLoader.loadTestsFromTestCase(tests.ActionAPI)
 expected=1 if args.scope=='smoke' else 4 if args.scope=='upgrade' else 22;assert suite.countTestCases()==expected
 directory=HERE/'receipts'/args.run;directory.mkdir(parents=True,exist_ok=False);started=time.monotonic();cases=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
  def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL'})
  def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR'})
 with (directory/'terminal.log').open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
 d.guard(args.source_sha256,history=True)
 (directory/'observed-public-wire.json').write_text(json.dumps({'observations':tests.ActionAPI.witnesses,'authority_effect':'none','actual_owner_outcome':None},indent=2,sort_keys=True)+'\n')
 def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 good=result.wasSuccessful() and result.testsRun==expected
 report={'schema_version':'lab-authenticated-public-action-qualification/v1-candidate','result':'PASS' if good else 'FAIL','expected_cases':expected,'original_cases_retained':19,'additional_transport_cases':3 if args.scope=='full' else 0,'actual_cases':result.testsRun,'cases':cases,'actual_public_calls':sum('reply' in x for x in tests.ActionAPI.witnesses),'actual_crashed_public_calls':sum('actual_child_exit_code' in x for x in tests.ActionAPI.witnesses),'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,'elapsed_seconds':time.monotonic()-started,'failures':len(result.failures),'errors':len(result.errors),'original_source_exit_completed':result.testsRun==expected,'source_guarded_exit_completed':True,'owned_fixture_cleanup_completed':result.testsRun==expected,'files':[bind(HERE/'source-manifest.json'),bind(directory/'terminal.log'),bind(directory/'observed-public-wire.json')],'canonical_admissions_applied':0,'runtime_activations':0,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Fresh successor qualification retaining original19 and adding3 original transport-schema refusals. Selected isolated authenticated public action.evaluate, action.dispatch, action.reconcile checks only. Live W02 leases and fresh separately selected Action actor; real local counter observations and real OS child exits. No owner R08 or complete common API qualification.'}
 path=directory/'qualification.json';path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':report['result'],'actual_cases':report['actual_cases'],'failures':report['failures'],'errors':report['errors'],'report':bind(path)}),flush=True)
 return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
