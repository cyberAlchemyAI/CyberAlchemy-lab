"""Complete current metadata/kernel/public-export candidate suite."""
import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_api24_frozen_guard', HERE / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    name = '_cal_api_v25_file_checks'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    def module(n):
        return __import__(name + '.' + n, fromlist=['*'])
    public, kernel, base, metadata, prep, reads = [module(n) for n in ('test_file_exports','test_export_kernel','export_test_base','test_metadata_scope','test_preparation_corrected','test_guarded_reads')]
    public.SOURCE = base.SOURCE = args.source_sha256
    public.PROFILE = base.PROFILE = metadata.PROFILE = prep.PROFILE = reads.PROFILE = args.profile_sha256
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(public),
                               unittest.defaultTestLoader.loadTestsFromModule(kernel),
                               unittest.defaultTestLoader.loadTestsFromModule(reads),
                               unittest.defaultTestLoader.loadTestsFromTestCase(prep.CorrectedPreparation),
                               unittest.defaultTestLoader.loadTestsFromModule(metadata)])
    assert suite.countTestCases() == 134
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):
            super().addSuccess(t)
            cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,error):
            super().addFailure(t,error)
            detail = self._exc_info_to_string(error,t)
            cases.append({'test':t.id(),'result':'FAIL','detail':detail})
            self.stream.write('\n'+detail)
            self.stream.flush()
        def addError(self,t,error):
            super().addError(t,error)
            detail = self._exc_info_to_string(error,t)
            cases.append({'test':t.id(),'result':'ERROR','detail':detail})
            self.stream.write('\n'+detail)
            self.stream.flush()
    result = unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    guard.verify(args.source_sha256)
    out = HERE / 'receipts'
    out.mkdir(mode=0o700,exist_ok=True)
    success = result.wasSuccessful() and result.testsRun == 134
    checks = {'schema_version':'lab-public-file-export-checks/v1-candidate','result':'PASS' if success else 'FAIL',
              'tests_run':result.testsRun,'expected_tests':134,'cases':cases,'source_sha256':args.source_sha256,
              'profile_sha256':args.profile_sha256,'implemented_operations':13,'export_grant_operations':9,'metadata_grant_operations':8,
              'original_v4_grant_operations':12,'original_operations':34,'current_Agent_qualified':False,
              'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    wire = {'events':public.FileExports.events,'public_nonce_witnesses':public.FileExports.public,
            'kernel_observations':kernel.Exports.observations,'metadata_events':metadata.MetadataScopes.events,
            'metadata_public_nonce_witnesses':metadata.MetadataScopes.public,'authority_effect':'none','actual_owner_outcome':None}
    for filename,value in [('file-export-checks.json',checks),('file-export-wire.json',wire)]:
        with (out / filename).open('x') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,ensure_ascii=False)
            stream.write('\n')
    print(json.dumps({'result':checks['result'],'tests_run':result.testsRun,'expected_tests':134}),flush=True)
    raise SystemExit(0 if success else 1)
if __name__ == '__main__':
    main()
