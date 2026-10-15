"""Inventory the frozen Context closure without selecting public release bytes."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
CONTEXT = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v5'
PARENT = HERE.parent / '0002'

def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

R = imported('_cal_R06_transitive_scanner', PARENT / 'review.py')

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(R.read(path)).hexdigest()}

def put(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    path.chmod(0o600)

def freeze():
    output = HERE / 'source-manifest.json'
    assert not output.exists()
    parents = [PARENT / 'receipts/proof-0002.json', CONTEXT / 'source-manifest.json']
    rows = {}
    for path in parents:
        selected = json.loads(R.read(path))
        for row in selected['files']:
            row = {'path': row['path'], 'sha256': row['sha256']}
            assert rows.get(row['path'], row) == row
            assert bind(ROOT / row['path']) == row
            rows[row['path']] = row
        rows[bind(path)['path']] = bind(path)
    context = RUN / 'context-R06-transitive-0003.json'
    assert not context.exists()
    controls = [RUN / 'authorization.json',
                ROOT / 'docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/R06.md',
                PARENT / 'review.py', PARENT / 'checks.py', Path(__file__)]
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R06 partial frozen Context dependency privacy inventory',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(path) for path in parents + controls],
                  'constraints': ['Exact frozen Context sources and retained R06 evidence only.',
                                  'Read-only originals; no permission or source changes.',
                                  'No private values in findings or stdout.',
                                  'Inspection refusals remain explicit; absence of findings is not publication permission.',
                                  'Final API, workflow, ontology and release selection remain required.'],
                  'authority_effect': 'none', 'actual_owner_outcome': None})
    for path in controls + [context]:
        rows[bind(path)['path']] = bind(path)
    put(output, {'schema_version': 'lab-R06-transitive-source/v1-candidate',
                 'files': [rows[key] for key in sorted(rows)],
                 'context_binding': bind(context),
                 'context_source_binding': bind(CONTEXT / 'source-manifest.json'),
                 'retained_partial_binding': bind(parents[0]),
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'frozen_before_inventory_or_checks': True})
    print(json.dumps({'result': 'FROZEN', 'files': len(rows), 'source_binding': bind(output)}), flush=True)

def guard(pin):
    path = HERE / 'source-manifest.json'
    assert bind(path)['sha256'] == pin
    manifest = json.loads(R.read(path))
    for row in manifest['files']:
        assert bind(ROOT / row['path']) == row, row['path']
    return manifest

def classification(findings, refused=False):
    return ('inspection-blocked-exclude-pending-review' if refused else
            'private-field-review-required-exclude-pending-review' if findings else
            'unselected-final-release-source')

class AdditionalChecks(unittest.TestCase):
    def test_18_private_field_cannot_become_public(self):
        self.assertEqual(classification([{'reason': 'actual-private-or-session-field'}]),
                         'private-field-review-required-exclude-pending-review')
    def test_19_refusal_is_not_a_clean_inspection(self):
        self.assertEqual(classification([], refused=True), 'inspection-blocked-exclude-pending-review')
    def test_20_absent_findings_still_need_release_selection(self):
        self.assertEqual(classification([]), 'unselected-final-release-source')

def checks(pin):
    guard(pin)
    original = imported('_cal_R06_retained_checks', PARENT / 'checks.py')
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(original.Checks),
                               unittest.defaultTestLoader.loadTestsFromTestCase(AdditionalChecks)])
    assert suite.countTestCases() == 20
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL'})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR'})
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard(pin)
    success = result.wasSuccessful() and result.testsRun == 20
    put(HERE / 'receipts/checks-0001.json',
        {'result': 'PASS' if success else 'FAIL', 'tests_run': result.testsRun,
         'expected_tests': 20, 'cases': cases, 'source_binding': bind(HERE / 'source-manifest.json'),
         'original17checks_retained': True, 'authority_effect': 'none', 'actual_owner_outcome': None})
    raise SystemExit(0 if success else 1)

def inventory(pin):
    manifest = guard(pin)
    report = json.loads(R.read(HERE / 'receipts/checks-0001.json'))
    assert report['result'] == 'PASS' and report['tests_run'] == report['expected_tests'] == 20
    selected = json.loads(R.read(CONTEXT / 'source-manifest.json'))
    rows = []
    for row in selected['files']:
        path = ROOT / row['path']
        raw = R.read(path)
        assert R.sha(raw) == row['sha256']
        findings = []
        refused = False
        try:
            findings = R.scan(raw, row['path'])
        except (ValueError, UnicodeError, RecursionError):
            refused = True
        rows.append({'path': row['path'], 'sha256': row['sha256'], 'size_bytes': len(raw),
                     'source_location': 'external-dependency' if Path(row['path']).is_absolute() else 'repository',
                     'inspection': 'refused' if refused else 'completed',
                     'private_field_findings': findings,
                     'disposition': classification(findings, refused), 'public_body_export_allowed': False})
    assert len(rows) == len({row['path'] for row in rows}) == len(selected['files'])
    guard(pin)
    counts = {name: sum(row['disposition'] == name for row in rows) for name in
              ['inspection-blocked-exclude-pending-review',
               'private-field-review-required-exclude-pending-review', 'unselected-final-release-source']}
    assert sum(counts.values()) == len(rows)
    output = HERE / 'inventory.json'
    put(output, {'schema_version': 'lab-R06-transitive-privacy-inventory/v1-candidate',
                 'result': 'PASS-scoped-inventory', 'checked_at': datetime.now(timezone.utc).isoformat(),
                 'source_binding': bind(HERE / 'source-manifest.json'),
                 'rows': rows, 'files_accounted': len(rows), 'disposition_counts': counts,
                 'inspection_refusals': counts['inspection-blocked-exclude-pending-review'],
                 'public_release_selection_complete': False, 'publication_authorized': False,
                 'originals_and_permissions_changed': False, 'private_values_disclosed': False,
                 'R06_complete': False, 'task_complete': False, 'goal_complete': False,
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'claim_ceiling': 'Heuristic field inspection of the exact frozen Context closure only. Findings and refusals need selected privacy disposition. No final API or public release qualification.'})
    proof_rows = {row['path']: row for row in manifest['files']}
    for path in [HERE / 'source-manifest.json', HERE / 'receipts/checks-0001.json', output]:
        proof_rows[bind(path)['path']] = bind(path)
    proof = HERE / 'receipts/proof-0001.json'
    put(proof, {'schema_version': 'lab-R06-transitive-partial-proof/v1-candidate', 'result': 'PASS',
                'files': [proof_rows[key] for key in sorted(proof_rows)],
                'inventory_binding': bind(output), 'files_accounted': len(rows),
                'disposition_counts': counts, 'actual20checks_passed': True,
                'task_complete': False, 'goal_complete': False,
                'remaining_obligations': ['Final integrated API/workflow/ontology/release byte selection.',
                                          'Resolve actual privacy findings and inspection refusals before public selection.',
                                          'Complete R07 and S02 before actual single R08 owner checkpoint.'],
                'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'PASS-scoped-inventory', 'files_accounted': len(rows),
                      'disposition_counts': counts, 'proof_binding': bind(proof)}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze', 'checks', 'inventory'])
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze()
    else:
        assert args.source_sha256
        (checks if args.command == 'checks' else inventory)(args.source_sha256)
