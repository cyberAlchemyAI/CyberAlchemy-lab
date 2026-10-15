"""Actual signed-source challenge checks with original exit and cleanup guards."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    parser.add_argument('--profile-sha256',required=True);parser.add_argument('--scope',choices=['focused','full'],required=True)
    args=parser.parse_args();name='_cal_api75_carrier_reference_checks'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify']);P=__import__(name+'.protocol',fromlist=['*'])
    guard.verify(args.source_sha256)
    module=__import__(name+'.test_carrier_references',fromlist=['CarrierReferenceChecks']);module.SOURCE=args.source_sha256;module.PROFILE=args.profile_sha256
    if args.scope=='focused':suite=unittest.TestSuite([module.CarrierReferenceChecks('test_01_three_carriers_have_separate_typed_reference_evidence')]);expected=1
    else:suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.CarrierReferenceChecks);expected=3
    assert suite.countTestCases()==expected
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'FAIL','detail':detail})
            self.stream.write('\n'+detail);self.stream.flush()
        def addError(self,test,error):
            super().addError(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'ERROR','detail':detail})
            self.stream.write('\n'+detail);self.stream.flush()
    receipts=HERE/'receipts';receipts.mkdir(exist_ok=True);log=receipts/f'carrier-reference-{args.scope}-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    guard.verify(args.source_sha256)
    def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':P.source.sha(p.read_bytes())}
    good=result.wasSuccessful() and result.testsRun==expected
    # A source-class setup/exit failure is not a completed isolated fixture run.
    complete=result.testsRun==expected and not any('setUpClass' in c['test'] or 'tearDownClass' in c['test'] for c in cases)
    wire=receipts/f'carrier-reference-{args.scope}-wire-0001.json'
    observations=getattr(module.CarrierReferenceChecks,'witnesses',[])
    with wire.open('x') as stream:json.dump({'observations':observations,'actual_owner_outcome':None,'authority_effect':'none'},stream,indent=2,sort_keys=True);stream.write('\n')
    report={'schema_version':'lab-actual-carrier-reference-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'scope':args.scope,'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,
        'actual_cases':result.testsRun,'expected_cases':expected,'cases':cases,'actual_public_calls':len(observations),
        'failures':len(result.failures),'errors':len(result.errors),'full_selected_suite_completed':complete,
        'original_source_exit_completed':complete,'source_guarded_exit_completed':True,
        'owned_fixture_cleanup_completed':complete and not result.errors,'whole_API_qualified':False,'actual_owner_outcome':None,
        'canonical_admissions_applied':0,'runtime_activations':0,'authority_effect':'none','task_complete':False,'goal_complete':False,
        'files':[bind(HERE/'source-manifest.json'),bind(log),bind(wire)],
        'claim_ceiling':'Selected actual independently selected three-carrier reference checks and original-byte refusals only; no Machine, owner decision, canonical admission or full API qualification.'}
    path=receipts/f'carrier-reference-{args.scope}-checks-0001.json'
    with path.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'actual_cases':result.testsRun,'actual_public_calls':len(observations),
        'failures':report['failures'],'errors':report['errors'],'report_binding':bind(path)}),flush=True)
    return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
