"""Run exact current control checks before the full integration suite."""
import argparse,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);ap.add_argument('--profile-sha256',required=True);a=ap.parse_args()
    s=importlib.util.spec_from_file_location('_cal_api29_controls_guard',HERE/'guard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.verify(a.source_sha256)
    assert hashlib.sha256((HERE/'contract-profile.json').read_bytes()).hexdigest()==a.profile_sha256
    name='_cal_api29_current_controls';s=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);p=importlib.util.module_from_spec(s);sys.modules[name]=p;s.loader.exec_module(p)
    module=__import__(name+'.test_current_controls',fromlist=['*']);module.PROFILE=a.profile_sha256;cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL','detail':self._exc_info_to_string(e,t)})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR','detail':self._exc_info_to_string(e,t)})
    suite=unittest.defaultTestLoader.loadTestsFromModule(module);assert suite.countTestCases()==7
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);g.verify(a.source_sha256)
    out=HERE/'receipts';out.mkdir(mode=0o700,exist_ok=True);v={'result':'PASS' if result.wasSuccessful() and result.testsRun==7 else 'FAIL','tests_run':result.testsRun,'expected_tests':7,'cases':cases,'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'current_Agent_qualified':False}
    with (out/'current-controls.json').open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':v['result'],'tests_run':result.testsRun}),flush=True);raise SystemExit(0 if v['result']=='PASS' else 1)
if __name__=='__main__':main()
