"""Actual isolated kernel methods and owned journal persistence, no API transfer."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';PACKAGE=BASE/'workflow-transition-v1'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    output=RUN/'workflow-transition-kernel-qualification-0133.json';assert not output.exists()
    spec=importlib.util.spec_from_file_location('_cal_workflow_kernel_source_guard',BASE/'api-v93/guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    pin=bind(PACKAGE/'source-manifest.json')['sha256']
    # The guard implementation validates arbitrary independently bound rows;
    # its normal verify pin names its own API manifest. Keep package verification
    # explicit without changing either guard's original source or constants.
    manifest=json.loads((PACKAGE/'source-manifest.json').read_bytes());guard._verify_files(ROOT,manifest['files'])
    name='_cal_workflow_kernel_actual133';spec=importlib.util.spec_from_file_location(name,PACKAGE/'__init__.py',submodule_search_locations=[str(PACKAGE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    tests=__import__(name+'.test_kernel',fromlist=['*']);suite=unittest.TestSuite()
    for cls in (tests.Kernel,tests.OwnedJournal):suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    assert bind(PACKAGE/'source-manifest.json')['sha256']==pin;guard._verify_files(ROOT,manifest['files'])
    value={'schema_version':'lab-workflow-transition-kernel-qualification/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==15 else 'FAIL',
        'actual_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'runner_output':stream.getvalue(),
        'files':[bind(p) for p in [PACKAGE/'source-manifest.json',PACKAGE/'kernel.py',PACKAGE/'journal.py',PACKAGE/'fixtures.py',PACKAGE/'test_kernel.py',Path(__file__).resolve()]],
        'source_guarded_exit_completed':True,'public_handler_added':False,'actual_current_host_qualified':False,'whole_API_qualified':False,
        'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'15isolated schema-valid kernel methods and actual owned candidate journal/replay/retry/observed recovery only. Current authenticated source/host adapter, output producers and public workflow operation remain unimplemented.'}
    with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
