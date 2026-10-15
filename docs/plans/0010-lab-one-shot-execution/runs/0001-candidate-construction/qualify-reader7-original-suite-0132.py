"""Execute original20adapter methods with explicit exact current source fixture changes."""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';READER=BASE/'current-source-adapter-v7'
ADAPTER='78d8150086ed41f6f2c2218805a2387caab1e5931b2619a894330557cb30d23c'
SOURCE='cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36'
PACKAGE='c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def methods(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    output=RUN/'reader7-original-suite-qualification-0132.json';assert not output.exists()
    fixture=RUN/'reader7-original-checks-rebased-0132.py';original=BASE/'current-source-adapter-v4/checks.py'
    before=methods(original);after=methods(fixture)
    changed=[key for key in before if before[key]!=after[key]]
    assert len(before)==len(after)==20 and changed==['test_01_selected_new_episode','test_03_all23_original_bodies']
    name='_cal_reader7_original_suite132';spec=importlib.util.spec_from_file_location(name,READER/'__init__.py',submodule_search_locations=[str(READER)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    reader=__import__(name+'.reader',fromlist=['SelectedReader']).SelectedReader(ADAPTER,SOURCE,PACKAGE);reader.guard()
    spec=importlib.util.spec_from_file_location(name+'.checks',fixture);checks=importlib.util.module_from_spec(spec);sys.modules[name+'.checks']=checks;spec.loader.exec_module(checks)
    checks.Checks.adapter_pin=ADAPTER;checks.SOURCE_PIN=SOURCE;checks.PACKAGE_PIN=PACKAGE
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(checks.Checks)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    reader.guard()
    value={'schema_version':'lab-reader7-original-suite-qualification/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==20 else 'FAIL',
        'actual_original_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'runner_output':stream.getvalue(),
        'unchanged_method_ASTs':18,'explicit_fixture_scope_corrections':changed,
        'fixture_corrections':['Exact current Source8head is5 instead of Source5head2.','All105originalbyte/header/parsechecks; original23noncanonical assertions retained for the independently selected preserved Source5corpus.'],
        'files':[bind(p) for p in [READER/'source-manifest.json',BASE/'current-participation-v8/source-manifest.json',BASE/'current-participation-v8/packages/0001/manifest.json',original,fixture,Path(__file__).resolve()]],
        'source_guarded_exit_completed':True,'actual_Agent_qualified':False,'public_API_qualified':False,'whole_Lab_qualified':False,
        'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Actual original20adapter behavior methods with explicitly reviewed current fixture scope only; no new Agent Context, whole API, canonical admission or completeLab.'}
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'report_binding':bind(output)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
