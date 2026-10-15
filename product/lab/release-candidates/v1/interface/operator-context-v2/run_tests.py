"""Observe actual guarded signed-source adapter tests with terminal evidence."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source_adapter


def main(pin):
    source_adapter.verify_package(pin)
    output = HERE / 'receipts/tests-result.json'
    if output.exists(): raise ValueError('test evidence already exists')
    spec = importlib.util.spec_from_file_location('_R03_signed_source_tests', HERE / 'test_source_adapter.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    expected = suite.countTestCases();tick = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    value = {'schema_version': 'lab-same-cut-source-tests/v1-candidate',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == expected else 'FAIL',
        'tests_run': result.testsRun, 'expected_tests': expected,
        'failures': len(result.failures), 'errors': len(result.errors),
        'duration_seconds': time.monotonic() - tick, 'package_manifest_sha256': pin,
        'source_name': 'reference-corrected', 'actual_signed_reader_used': True,
        'public_API_operations_added': 0, 'native_domain_mapping_supplied': False,
        'active_Agents_created': 0, 'authority_effect': 'none', 'actual_owner_outcome': None,
        'observed_at': datetime.now(timezone.utc).isoformat()}
    output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(value), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser();parser.add_argument('--package-sha256', required=True)
    args = parser.parse_args();main(args.package_sha256)
