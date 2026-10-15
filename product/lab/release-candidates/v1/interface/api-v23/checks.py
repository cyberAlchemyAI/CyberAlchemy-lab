"""Run full former and original-source API journeys from exact frozen sources."""
import argparse,hashlib,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);a=p.parse_args()
    spec=importlib.util.spec_from_file_location('_cal_api_v23_effect_guard',HERE/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.verify(a.source_sha256)
    assert hashlib.sha256((HERE/'contract-profile.json').read_bytes()).hexdigest()==a.profile_sha256
    name='_cal_api_v23_checks';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    modules=[__import__(name+'.'+n,fromlist=['*']) for n in ['test_preparation','test_preparation_corrected','run_session_checks','test_custody_sessions','test_custody_api','test_guarded_reads']]
    for module in modules:module.PROFILE=a.profile_sha256
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):
            super().addFailure(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'FAIL','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
        def addError(self,t,e):
            super().addError(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'ERROR','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(modules[5]),unittest.defaultTestLoader.loadTestsFromModule(modules[4]),unittest.defaultTestLoader.loadTestsFromTestCase(modules[1].CorrectedPreparation),unittest.defaultTestLoader.loadTestsFromModule(modules[2]),unittest.defaultTestLoader.loadTestsFromModule(modules[3])]);count=suite.countTestCases();assert count==146
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);g.verify(a.source_sha256)
    report={'schema_version':'lab-original-source-API-tests/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==count else 'FAIL','tests_run':result.testsRun,'expected_tests':count,'cases':cases,'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'operations':12,'original_operations':34,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    out=HERE/'receipts';out.mkdir(exist_ok=True,mode=0o700)
    def emit(path,v):
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2,sort_keys=True,ensure_ascii=False);f.write('\n')
    emit(out/'checks.json',report)
    observations={module.__name__:getattr(getattr(module,'Sessions',None),'events',[]) for module in modules}
    emit(out/'wire-observations.json',observations)
    print(json.dumps({'result':report['result'],'methods':result.testsRun,'expected_tests':count}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
