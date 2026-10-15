"""Run actual isolated contract tests and retain their exact evidence ceiling."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/challenge-resolution-v1'


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    report=RUN/'challenge-resolution-contracts-0001.json'
    assert not report.exists(),'preserve prior observations'
    paths=[*sorted(COMPONENT.glob('*')),
           ROOT/'docs/proposals/0008-lab-api-contracts/operations/challenge.resolve.json',
           ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/challenge-resolution.schema.json',
           ROOT/'authority/artifact-types/challenge-contract/v1/schema.json',
           ROOT/'authority/artifact-types/challenge-event/v1/schema.json',RUN/'authorization.json',Path(__file__).resolve()]
    files=[binding(path) for path in paths if path.is_file()]
    for path in COMPONENT.glob('*.py'):ast.parse(path.read_text())
    name='_cal_challenge_resolution_contracts_0001'
    spec=importlib.util.spec_from_file_location(name,COMPONENT/'__init__.py',submodule_search_locations=[str(COMPONENT)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    tests=__import__(name+'.test_contracts',fromlist=['Contracts'])
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.Contracts)
    methods=[test.id().rsplit('.',1)[-1] for test in suite]
    assert len(methods)==15
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    assert files==[binding(ROOT/row['path']) for row in files],'source changed during qualification'
    value={'schema_version':'lab-isolated-challenge-contract-qualification/v1-candidate',
           'result':'PASS' if result.wasSuccessful() else 'FAIL','actual_cases':result.testsRun,
           'failures':len(result.failures),'errors':len(result.errors),'selected_methods':methods,'files':files,
           'fixture_inputs_are_current_source':False,'ephemeral_signers_exported':False,
           'public_handler_qualified':False,'source_guarded_exit_completed':True,
           'canonical_admissions':0,'actual_owner_outcome':None,'authority_effect':'none',
           'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual isolated signature, response-obligation and composition cases only; no public transport, actual current source recognition, journal or whole API qualification.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'actual_cases':result.testsRun,'report_binding':binding(report)}),flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
