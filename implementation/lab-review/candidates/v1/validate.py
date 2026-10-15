#!/usr/bin/env python3
"""Run full C10 authoring guards and retain numbered source-bound evidence."""
import argparse
import os
import sys
import time
import unittest
from review import *


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.checks = []; self.current_pass = False
    def startTest(self, test):
        self.current_pass = False; super().startTest(test)
    def addSuccess(self, test):
        self.current_pass = True; super().addSuccess(test)
    def stopTest(self, test):
        self.checks.append({'test': test.id(), 'result': 'PASS' if self.current_pass else 'FLAG'})
        super().stopTest(test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('preparation'); parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    path = Path(args.preparation).resolve().relative_to(ROOT).as_posix()
    value = validate_preparation(path, args.sha256)
    os.environ['C10_PREPARATION_PATH'] = path; os.environ['C10_PREPARATION_SHA256'] = args.sha256
    directory = PACKAGE / 'receipts/C10'; directory.mkdir(parents=True, exist_ok=True)
    index = 1
    while (directory / f'{index:04d}.json').exists(): index += 1
    log = directory / f'{index:04d}.log'
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / 'tests'))
    expected_count = suite.countTestCases(); started = time.perf_counter()
    with log.open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordingResult).run(suite)
    current = validate_preparation(path, args.sha256)
    files = [binding(p.relative_to(ROOT).as_posix()) for p in PACKAGE.glob('*.py')]
    files += [binding(p.relative_to(ROOT).as_posix()) for p in (PACKAGE / 'tests').glob('*.py')]
    files += [binding(str(PACKAGE.relative_to(ROOT)) + '/README.md'), binding(path), binding(log.relative_to(ROOT).as_posix())]
    files += [binding(p.relative_to(ROOT).as_posix()) for p in (ROOT / path).parent.iterdir() if p.is_file()]
    files += [binding(RUN + '/context-C10.json'), binding(RUN + '/CONTEXT-C10.md')]
    for row in value['members']: files += row['targets'] + row['evidence']
    passed = result.wasSuccessful() and result.testsRun == expected_count == 18 and len(result.checks) == expected_count
    receipt = {'schema_version': 'lab-C10-member-preparation-check/v1-candidate', 'task': 'C10',
        'result': 'PASS' if passed else 'FLAG', 'task_complete': passed, 'authority_effect': 'none',
        'tests': result.testsRun, 'checks': result.checks, 'duration_seconds': time.perf_counter() - started,
        'preparation': {'path': path, 'sha256': args.sha256}, 'independent_members': len(current['members']),
        'actual_owner_outcome': None, 'canonical_admissions': 0, 'runtime_activations': 0,
        'files': list({r['path']: r for r in files}.values()),
        'source_bindings': load(RUN + '/context-C10.json')['source_bindings'],
        'remaining_obligations': [] if passed else ['All exact preparation guards must pass.'],
        'claim_ceiling': 'Exact scoped C10 member preparation only. Final owner authority, complete final bundle and application remain R08/S02/A01 obligations.'}
    receipt_path = directory / f'{index:04d}.json'; receipt_path.write_bytes(encoded(receipt))
    print(json.dumps({'result': receipt['result'], 'tests': receipt['tests'], 'members': len(current['members']), 'receipt': receipt_path.relative_to(ROOT).as_posix()}))
    sys.exit(0 if passed else 1)
