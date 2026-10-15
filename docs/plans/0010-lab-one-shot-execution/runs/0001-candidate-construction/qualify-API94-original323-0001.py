"""Execute every declared inherited method exactly once, retaining assertions/clock."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v94'
SOURCE='309aef6ef048a4aab9964a009244a4f789225895a982229f260e02e474723bbf'
PROFILE='63e346d422b45cb6fedc1ae03d173b8e2c8815449f42b419ecfe65c13924af29'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    output=RUN/'API94-original323-0001.json';assert not output.exists()
    spec=importlib.util.spec_from_file_location('_cal_API94_full_original_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(SOURCE)
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    name='_cal_API94_original323_actual';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=[];modules=[];cases=[];suite=unittest.TestSuite()
    for path in sorted(API.glob('*.py')):
        groups=[]
        for node in ast.parse(path.read_text()).body:
            if isinstance(node,ast.ClassDef):
                methods=[n.name for n in node.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
                if methods:groups.append((node.name,methods))
        if not groups:continue
        imported=__import__(name+'.'+path.stem,fromlist=['*']);modules.append(imported)
        # These constants are independently selected fixture pins, never test
        # callbacks/assertions, timestamps or fake store authorization.
        if hasattr(imported,'PROFILE'):imported.PROFILE=PROFILE
        for cls,methods in groups:
            kind=getattr(imported,cls)
            for method in methods:suite.addTest(kind(method));selected.append(path.name+':'+cls+'.'+method)
    for key,loaded in list(sys.modules.items()):
        if key.startswith(name+'.') and hasattr(loaded,'PROFILE'):loaded.PROFILE=PROFILE
    assert len(selected)==suite.countTestCases()==323
    class Result(unittest.TextTestResult):
        def startTest(self,test):
            super().startTest(test);print('Running '+test.id(),flush=True)
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):
            super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
        def addError(self,test,error):
            super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    guard.verify(SOURCE)
    value={'schema_version':'lab-actual-original323-qualification/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==323 else 'FAIL',
        'actual_original_methods':result.testsRun,'selected_original_methods':selected,'cases':cases,
        'failures':len(result.failures),'errors':len(result.errors),'fixture_profile_pin':PROFILE,
        'original_assertions_changed':False,'original_clocks_or_callbacks_changed':False,
        'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
        'source_guarded_exit_completed':True,'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Every declared323inherited API method attempted exactly once with selected current profile fixture pins. Complete qualification requires all methods PASS and all original34operations/46tasks and current paths; no owner outcome or wholeLab inference.'}
    with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
