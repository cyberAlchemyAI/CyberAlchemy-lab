"""Run all 74 unchanged predecessor checks and the new revision witness checks."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE))
import eligibility


def verify(pin):
    raw = (HERE / 'source-manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin: raise ValueError('selected authority successor pin differs')
    for b in json.loads(raw)['files']:
        p = ROOT / b['path']
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != b['sha256']: raise ValueError('frozen authority successor source changed')


def main(pin):
    verify(pin);suite = unittest.TestSuite()
    for name, path in [('regression', HERE.parent / 'session-authority-v1/test_eligibility_corrected.py'), ('revision', HERE / 'test_revision_witness.py')]:
        spec = importlib.util.spec_from_file_location('_R03_authority_v2_' + name, path)
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    expected = suite.countTestCases();tick = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite);verify(pin)
    value = {'schema_version': 'lab-session-authority-successor-tests/v1-candidate',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == expected else 'FAIL',
        'tests_run': result.testsRun, 'expected_tests': expected, 'failures': len(result.failures), 'errors': len(result.errors),
        'unchanged_predecessor_tests': 74, 'revision_witness_tests': 16, 'package_manifest_sha256': pin,
        'duration_seconds': time.monotonic() - tick, 'authority_effect': 'none', 'actual_owner_outcome': None,
        'public_API_operations_added': 0, 'active_Agents_created': 0, 'observed_at': datetime.now(timezone.utc).isoformat()}
    out = HERE / 'receipts/tests-result.json';out.parent.mkdir(exist_ok=True)
    if out.exists(): raise ValueError('test observation already exists')
    out.write_text(json.dumps(value, indent=2) + '\n');print(json.dumps(value), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser();p.add_argument('--package-sha256', required=True);a = p.parse_args();main(a.package_sha256)
