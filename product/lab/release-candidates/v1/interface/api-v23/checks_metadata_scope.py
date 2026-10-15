"""Current metadata/scope suite plus preserved original preparation and read guards."""
import argparse,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);a=p.parse_args();s=importlib.util.spec_from_file_location('_api21_source_guard',HERE/'guard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.verify(a.source_sha256)
    name='_cal_api_v23_metadata_checks';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    def imported(n):return __import__(name+'.'+n,fromlist=['*'])
    raw=imported('test_metadata_scope');prep=imported('test_preparation_corrected');reads=imported('test_guarded_reads');raw.PROFILE=prep.PROFILE=reads.PROFILE=a.profile_sha256
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(reads),unittest.defaultTestLoader.loadTestsFromTestCase(prep.CorrectedPreparation),unittest.defaultTestLoader.loadTestsFromModule(raw)]);count=suite.countTestCases();assert count==86;cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'FAIL','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
        def addError(self,t,e):super().addError(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'ERROR','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);g.verify(a.source_sha256);out=HERE/'receipts';out.mkdir(exist_ok=True,mode=0o700)
    for filename,value in [('metadata-scope-checks.json',{'result':'PASS' if result.wasSuccessful() and result.testsRun==86 else 'FAIL','tests_run':result.testsRun,'expected_tests':86,'cases':cases,'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'operations':12,'metadata_grant_operations':8,'original_operations':34,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'remaining_obligations':['Full current Agent episode/Session regression qualification','Public review owner coverage and22remainingAPIs/full46criteria/S02/R08']}),('metadata-scope-wire.json',{'events':raw.MetadataScopes.events,'public_nonce_witnesses':raw.MetadataScopes.public,'actual_owner_outcome':None,'authority_effect':'none'})]:
        with (out/filename).open('x') as f:json.dump(value,f,indent=2,sort_keys=True,ensure_ascii=False);f.write('\n')
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','methods':result.testsRun,'expected_tests':86}),flush=True);raise SystemExit(0 if result.wasSuccessful() and result.testsRun==86 else 1)
if __name__=='__main__':main()
