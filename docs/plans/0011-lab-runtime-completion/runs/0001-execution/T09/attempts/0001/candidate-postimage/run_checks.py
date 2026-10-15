"""Independent source pins before/after actual owned R02 and dependency checks."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import time

manifest_path, independent_pin, output = sys.argv[1:]
path = Path(manifest_path); raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == independent_pin, 'independent T09 manifest pin mismatch'
manifest = json.loads(raw)


def guard():
    for row in manifest['files']:
        p = Path(row['path'])
        assert p.is_file() and not p.is_symlink(), 'missing/nonregular selected input ' + str(p)
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], 'input changed ' + str(p)


guard()
repo = Path(manifest['repository']); candidate = Path(manifest['candidate_root'])
dependencies = Path(manifest['dependency_installation'])
sys.path.insert(0, str(dependencies / 'deps'))
sys.path.insert(0, str(repo / 'product/lab/release-candidates/v1/interface'))
# Standard importlib imports the actual original package name/files. No module
# __file__, principal, runtime source, origin allocator or frozen input is aliased.
r02 = importlib.import_module('api-integration-v16.r02_installer')
original_guard = importlib.import_module('api-integration-v16.guard')
sys.path.insert(0, str(repo / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'))
dependency_api = importlib.import_module('closure_hardened_0003')
sys.path.insert(0, str(candidate))
spec = importlib.util.spec_from_file_location('test_environment', candidate / 'test_environment.py')
tests = importlib.util.module_from_spec(spec); spec.loader.exec_module(tests)
tests.REPOSITORY = repo; tests.RUN = Path(output).parent
tests.R02 = r02; tests.DEPENDENCIES = dependency_api; tests.ORIGINAL_GUARD = original_guard
tests.DESCRIPTOR = candidate / 'supported-composite-environment.json'
tests.DESCRIPTOR_PIN = manifest['composite_sha256']
start = time.monotonic()
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
guard()
origins = {name: str(Path(module.__file__).resolve()) for name, module in list(sys.modules.items())
           if getattr(module, '__file__', None) and not module.__file__.startswith('<')}
receipt = {'schema_version': 'lab-T09-focused-composite-check/v1-candidate', 'authority_effect': 'none',
           'manifest_sha256': independent_pin, 'composite_sha256': manifest['composite_sha256'],
           'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skipped': len(result.skipped), 'elapsed_seconds': time.monotonic() - start,
           'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'actual_module_origins': origins,
           'interpreter': sys.executable, 'full_shared_qualification': False, 'T09_complete': False,
           'original_full_proof_qualified': False, 'actual_owner_outcome': None,
           'claim_ceiling': 'Focused exact composite environment plus actual original R02 package install/upgrade/rollback. No full historical proof, API17 integration, release, service or admission.'}
Path(output).write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
