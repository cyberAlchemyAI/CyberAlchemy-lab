"""Run all original gate/obligation methods against the frozen resolver6 code."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v91';COMPONENT=BASE/'challenge-resolution-v6'
PIN='b007a3251489936135b1dcdbb3c46657706bbb651678d11fcaf2280fb09fc92e'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    output=RUN/'resolution-primitives-qualification-0131.json';assert not output.exists()
    spec=importlib.util.spec_from_file_location('_cal_API91_primitive_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(PIN)
    for name in ('gate.py','obligations.py','test_contracts.py'):
        assert (COMPONENT/name).read_bytes()==(BASE/'challenge-resolution-v1'/name).read_bytes()
    name='_cal_resolution_primitives6'
    spec=importlib.util.spec_from_file_location(name,COMPONENT/'__init__.py',submodule_search_locations=[str(COMPONENT)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    tests=__import__(name+'.test_contracts',fromlist=['Contracts'])
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.Contracts)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    guard.verify(PIN)
    value={'schema_version':'lab-resolution-primitives-qualification/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==15 else 'FAIL',
        'actual_original_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'runner_output':stream.getvalue(),
        'files':[bind(p) for p in [API/'source-manifest.json',COMPONENT/'gate.py',COMPONENT/'obligations.py',COMPONENT/'test_contracts.py',Path(__file__).resolve()]],
        'source_guarded_exit_completed':True,'current_host_resolution_qualified':False,'whole_API_qualified':False,
        'actual_owner_outcome':None,'task_complete':False,'goal_complete':False,'authority_effect':'none',
        'claim_ceiling':'All15original isolated signed-gate/response/composition methods executed against unchanged selected resolver6 primitives. Actual current source/host/public API and full qualification remain separate.'}
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)}))
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
