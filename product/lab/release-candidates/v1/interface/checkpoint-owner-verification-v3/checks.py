"""Run selected owner join/custody checks against frozen exact sources."""
import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    name='_cal_checkpoint_owner_verification_v3'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    O=importlib.import_module(name+'.owners');tests=importlib.import_module(name+'.test_owners')
    assert O.source_guard()==args.source_sha256
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.OwnerChecks);assert suite.countTestCases()==49
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
        def addError(self,test,error):
            super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
    receipts=HERE/'receipts';receipts.mkdir(exist_ok=False);log=receipts/'actual-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    assert O.source_guard()==args.source_sha256
    def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':O.sha(p.read_bytes())}
    good=result.wasSuccessful() and result.testsRun==49
    value={'schema_version':'lab-checkpoint-owner-verification-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'source_sha256':args.source_sha256,'actual_cases':result.testsRun,'expected_cases':49,'cases':cases,
        'failures':len(result.failures),'errors':len(result.errors),'source_guarded_exit_completed':True,
        'synthetic_authority_records_only':True,'actual_private_file_custody_checks':True,
        'successful_native_owner_source_journey_qualified':False,'public_checkpoint_handler_qualified':False,
        'live_authority_verified':False,'actual_owner_outcome':None,'canonical_admissions_applied':0,
        'files':[bind(log),bind(HERE/'source-manifest.json')],
        'authority_effect':'none','task_complete':False,'goal_complete':False,
        'claim_ceiling':'Selected synthetic original-schema authority joins and real private temporary-file custody only; no successful native source journey, live authority, human owner outcome or public API handler.'}
    path=receipts/'checks-0001.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'actual_cases':result.testsRun,'failures':value['failures'],
        'errors':value['errors'],'report_binding':bind(path),'public_checkpoint_handler_qualified':False}),flush=True)
    return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
