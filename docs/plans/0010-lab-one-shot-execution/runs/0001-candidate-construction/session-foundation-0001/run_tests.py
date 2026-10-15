"""Run the frozen real context/custody tests and retain terminal observations."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
PACKAGE=ROOT/'implementation/lab-continuity/candidates/v2'

def check():
    manifest=json.loads((PACKAGE/'source-manifest.json').read_bytes())
    for row in manifest['files']:
        p=ROOT/row['path']
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('frozen source drift: '+row['path'])

def main():
    check();started=time.time()
    os.environ['R03_GENERATOR_SHA']='4dd5907dc1269e2b0f15a217cd1e60a277554b69889ea76f1e2e571e3fd3010e'
    if hashlib.sha256((PACKAGE/'packages/0001/generator-manifest.json').read_bytes()).hexdigest()!=os.environ['R03_GENERATOR_SHA']:
        raise ValueError('independent generator pin differs')
    spec=importlib.util.spec_from_file_location('foundation_tests',PACKAGE/'test_foundation.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    check()
    value={'schema_version':'lab-foundation-test-observation/v1-candidate','result':'PASS' if result.wasSuccessful() else 'FAIL',
        'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'duration_seconds':time.time()-started,'source_manifest_sha256':hashlib.sha256((PACKAGE/'source-manifest.json').read_bytes()).hexdigest(),
        'generator_manifest_sha256':os.environ['R03_GENERATOR_SHA'],'authority_effect':'none','actual_owner_outcome':None}
    output=HERE/'tests-terminal.json'
    if output.exists():raise ValueError('terminal evidence already exists')
    output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value),flush=True)
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':sys.exit(main())
