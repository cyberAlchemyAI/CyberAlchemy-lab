"""Run all fourteen real Machine cases after independently pinned source freeze."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/api-v35'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha256',required=True)
    parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--fixture-source-sha256',required=True)
    args=parser.parse_args()
    fixture_source=RUN/'corrected-Machine-full14-inputs-0002.json'
    assert hashlib.sha256(fixture_source.read_bytes()).hexdigest()==args.fixture_source_sha256
    for row in json.loads(fixture_source.read_bytes())['files']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    spec=importlib.util.spec_from_file_location('_cal_api35_machine_guard',HERE/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    assert hashlib.sha256((HERE/'contract-profile.json').read_bytes()).hexdigest()==args.profile_sha256
    name='_cal_api35_corrected_actual_machine_checks_0002'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    original=__import__(name+'.test_custody_sessions',fromlist=['*'])
    original.PROFILE=args.profile_sha256
    tests=__import__(name+'.test_machine_transport',fromlist=['*'])
    cases=[]

    class Result(unittest.TextTestResult):
        def _exc_info_to_string(self,error,test):
            # No exception values or frame locals: Session notes and private
            # credentials may exist in fixture memory when an assertion fails.
            kind,_,traceback=error;frames=[]
            while traceback is not None:
                code=traceback.tb_frame.f_code
                path=Path(code.co_filename)
                if path.is_relative_to(HERE):
                    frames.append({'source':str(path.relative_to(HERE)),
                                   'function':code.co_name,'line':traceback.tb_lineno})
                traceback=traceback.tb_next
            return json.dumps({'exception_class':kind.__name__,'frames':frames})
        def addSuccess(self,test):
            super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error)
            print(self._exc_info_to_string(error,test),flush=True)
            cases.append({'test':test.id(),'result':'FAIL','diagnostic':self._exc_info_to_string(error,test)})
        def addError(self,test,error):
            super().addError(test,error)
            print(self._exc_info_to_string(error,test),flush=True)
            cases.append({'test':test.id(),'result':'ERROR','diagnostic':self._exc_info_to_string(error,test)})

    class CorrectedFixture(tests.MachineTransport):
        def setUp(self):
            super().setUp()
            # Session fixture authentication remains on the real ReaderChannel.
            # Its saved dictionary shadows this class's actual Machine helper.
            assert isinstance(self.__dict__.get('authenticated'),dict)
            del self.authenticated
    methods=[name for name in vars(tests.MachineTransport) if name.startswith('test_')]
    assert len(methods)==14 and all(getattr(CorrectedFixture,name) is getattr(tests.MachineTransport,name) for name in methods)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CorrectedFixture)
    assert suite.countTestCases()==14
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    guard.verify(args.source_sha256)
    success=result.wasSuccessful() and result.testsRun==14
    output=RUN/'corrected-Machine-full14-0002';output.mkdir(mode=0o700,exist_ok=False)
    value={'schema_version':'lab-actual-Machine-transport-checks/v1-candidate',
           'result':'PASS' if success else 'FAIL','tests_run':result.testsRun,
           'expected_tests':14,'cases':cases,'fixture_source_sha256':args.fixture_source_sha256,'original14test_methods_unchanged':True,'parent_fixture_dictionary_shadow_removed':True,'failures':len(result.failures),'errors':len(result.errors),
           'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,
           'source_callbacks_replaced':False,'clock_replaced':False,'time_bounds_extended':False,
           'current_Agent_qualified':False,'whole_API_qualified':False,'task_complete':False,
           'actual_owner_outcome':None,'authority_effect':'none',
           'claim_ceiling':'Actual selected fourteen Machine cases only; full inherited regression, independent audit and final owner checkpoint remain required.'}
    with (output/'machine-transport-checks.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    wire={'schema_version':'lab-actual-Machine-public-wire/v1-candidate',
          'source_sha256':args.source_sha256,'observations':CorrectedFixture.machine_events,
          'private_memory_exported':False,'authority_effect':'none','actual_owner_outcome':None}
    with (output/'machine-transport-wire.json').open('x') as stream:
        json.dump(wire,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'result':value['result'],'tests_run':result.testsRun}),flush=True)
    raise SystemExit(0 if success else 1)


if __name__=='__main__':main()
