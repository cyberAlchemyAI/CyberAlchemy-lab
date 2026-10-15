"""Run only an independently selected frozen focused T33 candidate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest


manifest_path, expected_sha, output = sys.argv[1:]
path = Path(manifest_path)
raw = path.read_bytes()
if hashlib.sha256(raw).hexdigest() != expected_sha:
    raise SystemExit('manifest does not match independently supplied SHA')
manifest = json.loads(raw)


def guard():
    for row in manifest['files']:
        source = Path(row['path'])
        if not source.is_file() or source.is_symlink():
            raise RuntimeError('selected source absent/nonregular: ' + row['path'])
        if hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
            raise RuntimeError('selected source changed: ' + row['path'])


guard()
root = Path(manifest['candidate_root'])
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('test_owner_ingress', root / 'test_owner_ingress.py')
tests = importlib.util.module_from_spec(spec); spec.loader.exec_module(tests)
suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
start = time.time()
result = unittest.TextTestRunner(verbosity=2).run(suite)
guard()
receipt = {'schema_version': 'lab-T33-focused-check/v1-candidate', 'authority_effect': 'none',
           'manifest_sha256': expected_sha, 'tests_run': result.testsRun,
           'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
           'elapsed_seconds': time.time() - start, 'outcome': 'PASS' if result.wasSuccessful() else 'FAIL',
           'actual_approving_outcome': None, 'actual_host_issuer_selected': False,
           'publisher_integrated': False, 'independent_contract_review': 'pending',
           'claim_ceiling': 'Focused technical fixtures only; no R08, admission or shared qualification.'}
Path(output).write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
