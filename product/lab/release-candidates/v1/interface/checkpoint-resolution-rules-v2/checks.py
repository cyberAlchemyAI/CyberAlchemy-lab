"""Verify all frozen pure rule cases, retaining any failed actual result."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    name='_cal_checkpoint_resolution_rules_v2'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    E=__import__(name+'.rules',fromlist=['source_guard'])
    assert E.source_guard()==args.source_sha256
    tests=__import__(name+'.test_rules',fromlist=['ResolutionRules'])
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.ResolutionRules);assert suite.countTestCases()==47
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
        def addError(self,test,error):
            super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
    receipts=HERE/'receipts';receipts.mkdir(exist_ok=False)
    log=receipts/'actual-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    assert E.source_guard()==args.source_sha256
    def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':E.sha(p.read_bytes())}
    good=result.wasSuccessful() and result.testsRun==47
    value={'schema_version':'lab-checkpoint-pure-rules-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'source_sha256':args.source_sha256,'actual_cases':result.testsRun,'expected_cases':47,
        'cases':cases,'failures':len(result.failures),'errors':len(result.errors),
        'source_guarded_exit_completed':True,'full_selected_suite_completed':result.testsRun==47,
        'actual_public_API_calls':0,'actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0,
        'fixtures_only':True,'private_signing_keys_persisted':False,'ephemeral_Agents_created':0,
        'all_three_channel_shapes_qualified_against_synthetic_facts':good,
        'actual_owner_recognition_qualified':False,'current_API_checkpoint_handler_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False,
        'files':[bind(log),bind(HERE/'source-manifest.json')],
        'claim_ceiling':'All selected pure consistency, native target/core and actual cryptographic rule cases on synthetic independent facts only. No authenticated host handler, actual owner recognition/outcome, live authority, admission or completed plan.'}
    p=receipts/'checks-0001.json'
    with p.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'actual_cases':result.testsRun,'failures':value['failures'],
        'errors':value['errors'],'report_binding':bind(p),'actual_public_API_calls':0,'task_complete':False}),flush=True)
    return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
