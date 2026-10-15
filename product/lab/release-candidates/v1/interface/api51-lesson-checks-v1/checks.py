"""Run complete real host checks, preserving original clocks and cleanup guards."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
API=HERE.parent/'api-v51'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-sha256',required=True)
    parser.add_argument('--profile-sha256',required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('_cal_API51_selected_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    name='_cal_API51_lesson_actual'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    package=__import__(name+'.protocol',fromlist=['Schemas'])
    assert package.source.sha((API/'contract-profile.json').read_bytes())==args.profile_sha256
    spec=importlib.util.spec_from_file_location('_cal_API51_actual_lesson_cases',HERE/'test_host.py')
    tests=importlib.util.module_from_spec(spec);sys.modules[spec.name]=tests;spec.loader.exec_module(tests)
    tests.PACKAGE=name;tests.PROFILE=args.profile_sha256
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.LessonChecks)
    assert suite.countTestCases()==3
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    guard.verify(args.source_sha256)
    output=HERE/'receipts';output.mkdir(exist_ok=False)
    log=output/'actual-0001.log'
    with log.open('x') as f:f.write(stream.getvalue())
    wire=output/'wire-0001.json'
    with wire.open('x') as f:json.dump(tests.LessonChecks.events,f,indent=2,sort_keys=True);f.write('\n')
    def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':package.source.sha(p.read_bytes())}
    good=result.wasSuccessful() and result.testsRun==3
    report={'schema_version':'lab-lesson-public-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,'actual_cases':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'actual_public_calls':len(tests.LessonChecks.events),
        'source_guarded_exit_completed':True,'full_selected_suite_completed':result.testsRun==3,
        'actual_live_Agent_Session_used':True,'nonempty_signed_source_qualified':False,
        'genuine_review_provided':False,'actual_owner_outcome':None,'authority_effect':'none',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
        'files':[bind(log),bind(wire),bind(API/'source-manifest.json'),bind(API/'contract-profile.json')],
        'claim_ceiling':'Three selected actual transport cases on the current zero-Lesson signed source only; no nonempty qualification, owner review, Application, complete API or plan.'}
    path=output/'checks-0001.json'
    with path.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':report['result'],'actual_cases':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'report_binding':bind(path),'task_complete':False}),flush=True)
    return 0 if good else 1


if __name__=='__main__':raise SystemExit(main())
