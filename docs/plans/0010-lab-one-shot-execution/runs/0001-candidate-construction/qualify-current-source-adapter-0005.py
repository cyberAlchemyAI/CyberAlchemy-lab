"""Run the unchanged twenty adapter cases without replacing a historical receipt."""
import hashlib,importlib.util,json,sys,unittest
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v4'
PIN='be0e1857cf667100ea2dd9c6b115d11032f28fbfdfba4e9234d94aff84f19fee'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def guard():
    assert bind(HERE/'source-manifest.json')['sha256']==PIN
    manifest=json.loads((HERE/'source-manifest.json').read_bytes())
    for row in manifest['files']:assert bind(ROOT/row['path'])==row,row['path']
    return manifest
def main():
    manifest=guard();historical=HERE/'checks-result-0001.json';old=bind(historical)
    name='_cal_source_adapter_v4_actual_checks_0005'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    checks=__import__(name+'.checks',fromlist=['*'])
    checks.Checks.adapter_pin=PIN
    checks.SOURCE_PIN=manifest['producer_source_binding']['sha256'];checks.PACKAGE_PIN=manifest['producer_package_binding']['sha256']
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL'})
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR'})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(checks.Checks);assert suite.countTestCases()==20
    log=RUN/'current-source-adapter-checks-0005.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    reader=__import__(name+'.reader',fromlist=['*']).SelectedReader(PIN,checks.SOURCE_PIN,checks.PACKAGE_PIN)
    reader.guard();guard();assert bind(historical)==old
    value={'schema_version':'lab-current-source-adapter-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==20 else 'FAIL',
        'tests_run':result.testsRun,'expected_tests':20,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),
        'source_binding':bind(HERE/'source-manifest.json'),'producer_source_binding':manifest['producer_source_binding'],
        'producer_package_binding':manifest['producer_package_binding'],'historical_copied_receipt_binding':old,
        'historical_copied_receipt_used_as_current_proof':False,'source_callbacks_replaced':False,
        'clock_replaced':False,'source_guarded_exit_completed':True,'current_Agent_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
        'files':[bind(HERE/'source-manifest.json'),bind(HERE/'checks.py'),bind(Path(__file__).resolve()),bind(log)]}
    path=RUN/'current-source-adapter-checks-0005.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'tests_run':result.testsRun,'report_binding':bind(path)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
