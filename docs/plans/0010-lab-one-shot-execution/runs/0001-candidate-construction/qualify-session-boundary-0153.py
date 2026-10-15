"""Run selected declared methods with independent fixture pins and real guards."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
import unittest
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v7'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--profile',required=True)
    parser.add_argument('--selection',choices=['session-boundary'],required=True);args=parser.parse_args()
    output=RUN/'Session-boundary-0153.json';events=RUN/'Session-boundary-0153.events.jsonl'
    assert not output.exists() and not events.exists()
    def event(v):
        with events.open('a') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**v})+'\n');f.flush()
    event({'phase':'starting','pid':os.getpid(),'source_pin':args.source,'profile_pin':args.profile})
    spec=importlib.util.spec_from_file_location('_cal_API96_independent_guard',API/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(args.source)
    assert bind(API/'contract-profile.json')['sha256']==args.profile
    name='_cal_API3_actual_Session_boundary_0153';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=[];cases=[];suite=unittest.TestSuite();fixture_modules=[]
    chosen={'run_session_checks.py:Sessions.'+m for m in ['test_24_captured_source_corruption_disposes_on_inspection','test_26_private_policy_revocation_disposes','test_27_actual_expiry_timer_disposes','test_33_reply_profile_binding_does_not_mutate_host']}
    for path in sorted(API.glob('*.py')):
        groups=[]
        for node in ast.parse(path.read_text()).body:
            if isinstance(node,ast.ClassDef):
                methods=[n.name for n in node.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
                if methods:groups.append((node.name,methods))
        if not groups:continue
        imported=__import__(name+'.'+path.stem,fromlist=['*']);fixture_modules.append(imported)
        for cls,methods in groups:
            for method in methods:
                ident=path.name+':'+cls+'.'+method
                if ident in chosen:suite.addTest(getattr(imported,cls)(method));selected.append(ident)
    helper=__import__(name+'.export_test_base',fromlist=['*']);fixture_modules.append(helper)
    # Only test modules and their explicitly selected export fixture helper.
    # Missing imported globals are fixture setup defects, not production grants.
    pins=[]
    for loaded in fixture_modules:
        loaded.PROFILE=args.profile;loaded.SOURCE=args.source
        pins.append({'module':loaded.__name__,'source':args.source,'profile':args.profile})
    assert suite.countTestCases()==len(selected) and len(selected)==4
    class Result(unittest.TextTestResult):
        def startTest(self,test):super().startTest(test);event({'phase':'running','test':test.id()})
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'});event(cases[-1])
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)});event(cases[-1])
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)});event(cases[-1])
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    exit_error=None
    try:guard.verify(args.source)
    except Exception:exit_error=traceback.format_exc()
    passed=result.wasSuccessful() and result.testsRun==len(selected) and exit_error is None
    value={'schema_version':'lab-actual-declared-api-qualification/v1-candidate','result':'PASS' if passed else 'FAIL',
        'selected_methods':selected,'actual_methods':result.testsRun,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),
        'fixture_pins':pins,'fixture_assertion_revision':None,
        'original_assertions_changed':False,'original_clocks_or_callbacks_changed':False,'source_guarded_exit_completed':exit_error is None,'exit_guard_error':exit_error,
        'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
        'events_binding':bind(events),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Actual selected inherited API methods only. No new handler, human pilot, canonical admission, whole Lab or owner outcome inferred.'}
    with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    event({'phase':'terminal','result':value['result'],'actual_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)})
    print(json.dumps({'result':value['result'],'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)}),flush=True)
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
