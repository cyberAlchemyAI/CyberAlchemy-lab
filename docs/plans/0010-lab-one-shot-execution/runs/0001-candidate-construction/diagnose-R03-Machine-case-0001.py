"""Reproduce the original failed case; emit source locations, never frame values.

This diagnostic does not replace the live fourteen-case qualification suite.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v35'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--inputs-sha256',required=True)
    args=parser.parse_args()
    inputs=RUN/'Machine-case-diagnostic-inputs-0001.json'
    assert sha(inputs.read_bytes())==args.inputs_sha256
    selection=json.loads(inputs.read_bytes())
    for row in selection['files']:
        assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    spec=importlib.util.spec_from_file_location('_cal_machine_diagnostic_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(selection['API_source_sha256'])
    name='_cal_actual_machine_case_diagnostic_0001'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    original=__import__(name+'.test_custody_sessions',fromlist=['*'])
    original.PROFILE=selection['API_profile_sha256']
    tests=__import__(name+'.test_machine_transport',fromlist=['*'])
    rows=[]
    class Result(unittest.TextTestResult):
        def _exc_info_to_string(self,error,test):
            kind,_,traceback=error;frames=[]
            while traceback is not None:
                code=traceback.tb_frame.f_code;path=Path(code.co_filename)
                if path.is_relative_to(API):
                    frames.append({'source':str(path.relative_to(API)),
                                   'function':code.co_name,'line':traceback.tb_lineno})
                traceback=traceback.tb_next
            return json.dumps({'exception_class':kind.__name__,'frames':frames})
        def emit(self,test,outcome,error=None):
            row={'test':test.id(),'result':outcome,'observed_at':datetime.now(timezone.utc).isoformat()}
            if error is not None:row['diagnostic']=json.loads(self._exc_info_to_string(error,test))
            rows.append(row)
            print(json.dumps(row),flush=True)
        def addSuccess(self,test):super().addSuccess(test);self.emit(test,'PASS')
        def addFailure(self,test,error):super().addFailure(test,error);self.emit(test,'FAIL',error)
        def addError(self,test,error):super().addError(test,error);self.emit(test,'ERROR',error)
    suite=unittest.TestSuite([tests.MachineTransport('test_01_actual_identity_signature_and_shared_custody')])
    started=time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    guard.verify(selection['API_source_sha256'])
    proof={'schema_version':'lab-actual-Machine-single-case-diagnostic/v1-candidate',
           'result':'PASS' if result.wasSuccessful() else 'FAIL',
           'tests_run':result.testsRun,'cases':rows,'elapsed_seconds':time.perf_counter()-started,
           'inputs_sha256':args.inputs_sha256,'original_test_method_unchanged':True,
           'clock_replaced':False,'source_callbacks_replaced':False,'time_bounds_extended':False,
           'private_frame_values_inspected':False,'full_fourteen_case_suite_replaced':False,
           'runtime_qualified':False,'task_complete':False,'authority_effect':'none','actual_owner_outcome':None}
    with (RUN/'Machine-case-diagnostic-0001.json').open('x') as stream:
        json.dump(proof,stream,sort_keys=True,indent=2);stream.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__=='__main__':main()
