"""All twenty original mapping criteria and nine original-source/qualification criteria."""
import unittest
from .build import *
from . import test_original_mapping,test_raw_mapping
def main(pin,package_pin):
    guard(pin);require(package_pin is not None,'independent mapping package pin required')
    require(sha((HERE/'packages/0001/manifest.json').read_bytes())==package_pin,'independent mapping package differs')
    for module in [test_original_mapping,test_raw_mapping]:module.PIN=pin;module.PACKAGE=package_pin
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_original_mapping),unittest.defaultTestLoader.loadTestsFromModule(test_raw_mapping)])
    require(suite.countTestCases()==29,'all29originalandrawmapping methods required')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);guard(pin)
    report={'schema_version':'lab-original-source-native-mapping-tests/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==29 else 'FAIL',
        'tests_run':result.testsRun,'expected_tests':29,'original20assertions_changed':False,'raw_source_specific_methods_changed':2,'cases':cases,'source_sha256':pin,'package_sha256':package_pin,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    emit(HERE/'receipts/checks.json',report);print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt_binding':binding(HERE/'receipts/checks.json')}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
