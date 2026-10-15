"""Seven actual bounded source/schema/control cases, not full runtime proof."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v86'
SOURCE='03f8cbad5579f81d6ed6242ba0aee6e30b468e91b55c6984f73ab5a74064859f'
PROFILE='b06e97f5e56d24012b713c8e979e47eecd272a691414dd766c499d2305b9f7bc'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    args=parser.parse_args();assert args.source_sha256==SOURCE and args.profile_sha256==PROFILE
    report=RUN/'API86-source-controls-0001.json';assert not report.exists()
    spec=importlib.util.spec_from_file_location('_cal_API86_source_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(SOURCE);assert bind(API/'contract-profile.json')['sha256']==PROFILE
    name='_cal_API86_selected_controls'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    tests=__import__(name+'.test_current_controls',fromlist=['CurrentControls']);tests.PROFILE=PROFILE
    protocol=__import__(name+'.protocol',fromlist=['Schemas'])
    selected=[method for method in unittest.defaultTestLoader.getTestCaseNames(tests.CurrentControls)
              if method.startswith(('test_01_','test_02_','test_03_','test_04_','test_07_'))]
    assert len(selected)==5
    class ResolutionWiring(unittest.TestCase):
        def test_12_exact_closed_private_resolution_policy_and_method(self):
            value=json.loads((API/'authentication.schema.json').read_bytes())
            branches=[branch for branch in value['oneOf'] if branch.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-resolution-policy/v1-candidate']
            self.assertEqual(len(branches),1);branch=branches[0]
            self.assertFalse(branch['additionalProperties'])
            self.assertEqual(branch['properties']['allowed_operations']['const'],list(protocol.RESOLUTION_SUPPORTED))
            self.assertEqual(branch['properties']['session_control'],{'type':'null'})
            control=branch['properties']['resolution_control']
            self.assertFalse(control['additionalProperties'])
            self.assertEqual(set(control['required']),{'routing_binding','method_binding'})
            from importlib import import_module
            selected=import_module(name+'.challenge_resolution')
            self.assertEqual(Path(sys.modules[selected.ChallengeResolution.__module__].__file__).resolve(),
                             API.parent/'challenge-resolution-v1/preparation.py')
        def test_13_original_resolution_request_and_result_contracts_unchanged(self):
            schemas=protocol.Schemas(PROFILE)
            operation=json.loads((ROOT/'docs/proposals/0008-lab-api-contracts/operations/challenge.resolve.json').read_bytes())
            self.assertEqual(operation['effect_kind'],'candidate-write')
            self.assertFalse(operation['repository_admission_possible'])
            for field in ('request_schema','result_schema'):
                selected=operation[field]
                self.assertEqual(hashlib.sha256((ROOT/selected['ref']).read_bytes()).hexdigest(),selected['sha256'])
            self.assertEqual(schemas.operations['challenge.resolve'],operation)
            self.assertEqual(len(protocol.SUPPORTED),24)
            self.assertEqual(len(schemas.operations),34)
    suite=unittest.TestSuite([*(tests.CurrentControls(method) for method in selected),
                             *unittest.defaultTestLoader.loadTestsFromTestCase(ResolutionWiring)])
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','error_class':error[0].__name__})
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','error_class':error[0].__name__})
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    guard.verify(SOURCE)
    value={'schema_version':'lab-API-source-controls/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==7 else 'FAIL',
           'actual_cases':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'cases':cases,
           'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
           'files':[bind(path) for path in (API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve())],
           'source_guarded_exit_completed':True,'challenge_resolution_actual_runtime_qualified':False,
           'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'authority_effect':'none',
           'claim_ceiling':'Seven actual bounded original source/schema/control and new resolution wiring cases only; no positive public resolution, new current-source owner recognition or full API proof.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'actual_cases':result.testsRun,'report_binding':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
