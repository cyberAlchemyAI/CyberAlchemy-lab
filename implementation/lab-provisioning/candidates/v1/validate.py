#!/usr/bin/env python3
"""Freeze C11 authoring/runtime sources and run every provisioning case."""
import time
import unittest
from provision import *


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw); self.checks = []; self.ok = False
    def startTest(self, test): self.ok = False; super().startTest(test)
    def addSuccess(self, test): self.ok = True; super().addSuccess(test)
    def stopTest(self, test):
        self.checks.append({'test': test.id(), 'result': 'PASS' if self.ok else 'FLAG'}); super().stopTest(test)


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': byte_digest(path.read_bytes())}


if __name__ == '__main__':
    verify_inputs()
    files = [binding(p) for p in PACKAGE.glob('*.py')] + [binding(p) for p in (PACKAGE / 'tests').glob('*.py')]
    files += [binding(PACKAGE / name) for name in ('README.md', 'OPERATOR.md')]
    files += [binding(RUN / name) for name in ('context-C11.json', 'CONTEXT-C11.md')]
    files += load(BOOTSTRAP / 'packages/0004/PACKAGE-MANIFEST.json')['file_bindings']
    manifest = {'schema_version': 'lab-C11-source-manifest/v1-candidate', 'authority_effect': 'none', 'files': files}
    packages = PACKAGE / 'packages'; packages.mkdir(exist_ok=True); index = 1
    while (packages / f'{index:04d}').exists(): index += 1
    package = packages / f'{index:04d}'; package.mkdir()
    (package / 'manifest.json').write_bytes(encoded(manifest))
    receipts = PACKAGE / 'receipts/C11'; receipts.mkdir(parents=True, exist_ok=True)
    log = receipts / f'{index:04d}.log'
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / 'tests')); total = suite.countTestCases(); started = time.perf_counter()
    with log.open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordingResult).run(suite)
    import test_provision
    observed = test_provision.ProvisionTests.observed
    drift = [r['path'] for r in files if byte_digest((ROOT / r['path']).read_bytes()) != r['sha256']]
    verify_inputs()
    passed = result.wasSuccessful() and result.testsRun == total == 13 and len(result.checks) == total and observed is not None and not drift
    example = package / 'observed-public-provisioning.json'; example.write_bytes(encoded({'authority_effect': 'none', 'observations': observed, 'owned_fixture_closed': test_provision.ProvisionTests.branch.closed if hasattr(test_provision.ProvisionTests, 'branch') else None}))
    receipt = {'schema_version': 'lab-C11-provisioning-check/v1-candidate', 'task': 'C11',
        'authority_effect': 'none', 'result': 'PASS' if passed else 'FLAG', 'task_complete': passed,
        'tests': result.testsRun, 'checks': result.checks, 'duration_seconds': time.perf_counter() - started,
        'source_drift': drift, 'actual_owner_outcome': None, 'permanent_stores_provisioned': 0,
        'service_activations': 0, 'canonical_admissions': 0,
        'files': files + [binding(package / 'manifest.json'), binding(example), binding(log)],
        'source_bindings': load(RUN / 'context-C11.json')['source_bindings'],
        'remaining_obligations': [] if passed else ['All exact provisioning checks and public observations must pass.'],
        'claim_ceiling': 'Owned disposable candidate D75 Project genesis and independently signed catalog only. No permanent operator/store, Work-only trusted authority adapter, implementation adoption or admitted operation.'}
    path = receipts / f'{index:04d}.json'; path.write_bytes(encoded(receipt))
    print(json.dumps({'result': receipt['result'], 'tests': result.testsRun, 'receipt': path.relative_to(ROOT).as_posix(), 'source_drift': drift}), flush=True)
    sys.exit(0 if passed else 1)
