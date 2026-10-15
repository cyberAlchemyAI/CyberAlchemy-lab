#!/usr/bin/env python3
import argparse
import os
import time
import unittest
from verification import *


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kw): super().__init__(*args, **kw); self.checks = []; self.ok = False
    def startTest(self, test): self.ok = False; super().startTest(test)
    def addSuccess(self, test): self.ok = True; super().addSuccess(test)
    def stopTest(self, test):
        self.checks.append({'test': test.id(), 'result': 'PASS' if self.ok else 'FLAG'}); super().stopTest(test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('package'); args = parser.parse_args()
    package = Path(args.package).resolve(); require(package.parent == PACKAGE / 'packages', 'exact numbered Work package required')
    check_context_sources(); verify_audit_exact(load(package / 'audit.json'))
    os.environ['C12_PACKAGE'] = package.relative_to(ROOT).as_posix()
    sources = [binding(p) for p in PACKAGE.glob('*.py')] + [binding(p) for p in (PACKAGE / 'tests').glob('*.py')] + [binding(PACKAGE / 'README.md')]
    sources += [binding(RUN / name) for name in ['context-C12.json', 'CONTEXT-C12.md']]
    outputs = [binding(p) for p in package.iterdir() if p.is_file()]
    receipts = PACKAGE / 'receipts/C12'; receipts.mkdir(parents=True, exist_ok=True); index = 1
    while (receipts / f'{index:04d}.json').exists(): index += 1
    log = receipts / f'{index:04d}.log'; started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / 'tests')); count = suite.countTestCases()
    with log.open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordingResult).run(suite)
    current = all(byte_digest((ROOT / r['path']).read_bytes()) == r['sha256'] for r in sources + outputs)
    check_context_sources()
    passed = result.wasSuccessful() and result.testsRun == count == 12 and len(result.checks) == count and current
    receipt = {'schema_version': 'lab-C12-real-Work-evidence-check/v1-candidate', 'task': 'C12',
        'authority_effect': 'none', 'result': 'PASS' if passed else 'FLAG', 'task_complete': passed,
        'tests': result.testsRun, 'checks': result.checks, 'duration_seconds': time.perf_counter() - started,
        'source_currentness': current, 'actual_bounded_development_Work': True,
        'actual_owner_outcome': None, 'repository_admissions_applied': 0, 'human_satisfaction_observed': False,
        'native_ontology_scope': 'explicit diagnostic fixture only; no domain Artifact mapping',
        'files': sources + outputs + [binding(log)], 'source_bindings': load(RUN / 'context-C12.json')['source_bindings'],
        'remaining_obligations': [] if passed else ['All actual Work source, local replay and selection checks must pass.'],
        'claim_ceiling': 'Actual bounded source audit, selected public evidence and candidate local Work only; no whole-plan completion, canonical Work admission, real human satisfaction or Product benefit.'}
    path = receipts / f'{index:04d}.json'; path.write_bytes(encoded(receipt))
    print(json.dumps({'result': receipt['result'], 'tests': result.testsRun, 'receipt': path.relative_to(ROOT).as_posix()}), flush=True)
    sys.exit(0 if passed else 1)
