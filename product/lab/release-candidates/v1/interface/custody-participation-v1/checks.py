"""Run every original branch criterion and added original-content guards."""
import unittest
from .base import *
from . import reader,test_original_branch,test_raw_source
def main(source_pin,package_pin):
    require(package_pin is not None,'independent package pin required');verify_source(source_pin);reader.package(source_pin,package_pin)
    for module in [test_original_branch,test_raw_source]:module.SOURCE_PIN=source_pin;module.PACKAGE_PIN=package_pin
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_original_branch),unittest.defaultTestLoader.loadTestsFromModule(test_raw_source)])
    expected=suite.countTestCases();require(expected==54,'all 22 original and 32 new source methods required')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);verify_source(source_pin);reader.package(source_pin,package_pin)
    report={'schema_version':'lab-custody-participation-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==expected else 'FAIL',
        'tests_run':result.testsRun,'expected_tests':expected,'original_methods':22,'new_methods':32,'cases':cases,'source_sha256':source_pin,'package_sha256':package_pin,
        'sources_unchanged':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'original_encoding_assertion_successor':'Exact original retrieval, distinct inherited encoding and parsed value parity; all other original methods retain their assertions.',
        'observations':test_raw_source.OBSERVATIONS}
    emit(HERE/'receipts/checks.json',report);print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt_binding':binding(HERE/'receipts/checks.json')}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
