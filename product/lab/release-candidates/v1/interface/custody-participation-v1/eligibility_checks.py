"""Preserve all original source, host grant, privacy and revision tests."""
import unittest
from .base import *
from . import test_eligibility,test_revision_witness
def main(source_pin,package_pin=None):
    verify_source(source_pin);cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):super().addFailure(test,err);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(err,test)})
        def addError(self,test,err):super().addError(test,err);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(err,test)})
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_eligibility),unittest.defaultTestLoader.loadTestsFromModule(test_revision_witness)])
    require(suite.countTestCases()==90,'all 74 original eligibility and 16 original revision methods required')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);verify_source(source_pin)
    report={'schema_version':'lab-original-participation-eligibility-tests/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==90 else 'FAIL',
        'tests_run':result.testsRun,'cases':cases,'source_sha256':source_pin,'original_assertions_preserved':True,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Pure source/permission/revision fixtures; no authentication, real host permission, Agent or signed authority from these fixtures.'}
    emit(HERE/'receipts/eligibility.json',report);print(json.dumps({'result':report['result'],'tests':result.testsRun,'receipt_binding':binding(HERE/'receipts/eligibility.json')}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
