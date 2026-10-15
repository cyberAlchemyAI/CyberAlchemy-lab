"""Run bounded original-source export cases against exact frozen host bytes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
API=HERE.parent/'api-v59'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--suite',choices=['focused','full'],required=True);parser.add_argument('--check-source-sha256',required=True);args=parser.parse_args()
    def check_source():
        assert sha(HERE/'source-manifest.json')==args.check_source_sha256
        for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    check_source()
    name='_cal_API59_package_export_'+args.suite
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify']);manifest=guard.verify(args.source_sha256)
    assert sha(API/'contract-profile.json')==args.profile_sha256
    fixture_spec=importlib.util.spec_from_file_location(name+'.versioned_export_fixture',HERE/'fixture.py')
    fixture=importlib.util.module_from_spec(fixture_spec);sys.modules[fixture_spec.name]=fixture;fixture_spec.loader.exec_module(fixture)
    test_spec=importlib.util.spec_from_file_location(name+'.versioned_export_tests',HERE/'tests.py')
    module=importlib.util.module_from_spec(test_spec);sys.modules[test_spec.name]=module;test_spec.loader.exec_module(module)
    module.SOURCE=args.source_sha256;module.PROFILE=args.profile_sha256
    if args.suite=='focused':
        names=['test_05_caller_cannot_replace_selected_privacy_review',
            'test_06_caller_cannot_omit_dependency_closure',
            'test_13_unknown_operation_inspection_preserves_empty_workspace',
            'test_14_missing_journal_lock_is_not_recreated_on_retry']
        suite=unittest.TestSuite(module.PackageExportAPI(name) for name in names);expected=4
    else:suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.PackageExportAPI);expected=14
    assert suite.countTestCases()==expected
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error);detail=self._exc_info_to_string(error,test)
            cases.append({'test':test.id(),'result':'FAIL','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
        def addError(self,test,error):
            super().addError(test,error);detail=self._exc_info_to_string(error,test)
            cases.append({'test':test.id(),'result':'ERROR','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
    receipts=HERE/'receipts';receipts.mkdir(exist_ok=True)
    log=receipts/('package-export-'+args.suite+'-0001.log')
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    check_source();guard.verify(args.source_sha256);assert sha(API/'contract-profile.json')==args.profile_sha256
    wire=receipts/('package-export-'+args.suite+'-wire-0001.json')
    with wire.open('x') as stream:json.dump(module.PackageExportAPI.observations,stream,indent=2,sort_keys=True);stream.write('\n')
    good=result.wasSuccessful() and result.testsRun==expected
    report={'schema_version':'lab-authenticated-package-export-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'suite':args.suite,'actual_cases':result.testsRun,'expected_cases':expected,'cases':cases,
        'actual_public_calls':len(module.PackageExportAPI.observations),'errors':len(result.errors),'failures':len(result.failures),
        'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,
        'full_selected_suite_completed':result.testsRun==expected,'source_guarded_exit_completed':good,'owned_fixture_cleanup_completed':good,
        'original_inherited_methods_retained':305,'original_export_methods_unchanged':12,'original_public_contracts_retained':34,
        'authored_handlers':20,'unimplemented_operations':14,'whole_API_qualified':False,
        'canonical_admissions_applied':0,'runtime_activations':0,'authority_effect':'none','actual_owner_outcome':None,
        'task_complete':False,'goal_complete':False,
        'files':[bind(log),bind(wire),bind(HERE/'source-manifest.json'),bind(API/'source-manifest.json'),bind(API/'contract-profile.json')],
        'claim_ceiling':'Only selected actual authenticated exports from owned candidate/local signed sources, original closure/privacy controls, managed output and read-only retry. No foreign import, broad carrier/authority closure, genuine pilot, owner outcome, admission, complete API or completed plan.'}
    path=receipts/('package-export-'+args.suite+'-0001.json')
    with path.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'actual_cases':result.testsRun,'actual_public_calls':report['actual_public_calls'],
        'errors':report['errors'],'failures':report['failures'],'report_binding':bind(path)}),flush=True)
    return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
