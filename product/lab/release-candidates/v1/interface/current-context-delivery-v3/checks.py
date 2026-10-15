"""Complete original38 Context criteria plus eight original-source criteria."""
from .build import *
from . import test_original_delivery,test_raw_delivery
import unittest
def main(pin,package_pin,mapped_pin):
    verify_source(pin);require(package_pin is not None,'independent Context package pin required')
    require(sha((HERE/'packages/0001/manifest.json').read_bytes())==package_pin,'independent Context package differs')
    for module in [test_original_delivery,test_raw_delivery]:module.PIN=pin;module.PACKAGE=package_pin;module.MAPPED_PACKAGE=mapped_pin
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_original_delivery),unittest.defaultTestLoader.loadTestsFromModule(test_raw_delivery)])
    require(suite.countTestCases()==47,'all46originalandrawpluslifetimeContext criteria required')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);verify_source(pin)
    report={'schema_version':'lab-original-source-context-tests/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==47 else 'FAIL',
        'tests_run':result.testsRun,'expected_tests':47,'cases':cases,'source_sha256':pin,'package_sha256':package_pin,'mapped_package_sha256':mapped_pin,
        'original38assertions_changed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    emit(HERE/'receipts/checks.json',report);print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt_binding':binding(HERE/'receipts/checks.json')}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
