#!/usr/bin/env python3
"""Freeze W05 dependencies, run full guards/regressions and retain actual controlled evidence."""
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from failures.episode import *

HERE = Path(__file__).resolve().parent
RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': byte_sha(path.read_bytes())}


class Recording(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checks = []
        self.passed = False

    def startTest(self, test):
        self.passed = False
        super().startTest(test)

    def addSuccess(self, test):
        self.passed = True
        super().addSuccess(test)

    def stopTest(self, test):
        self.checks.append({'test': test.id(), 'result': 'PASS' if self.passed else 'FLAG'})
        print(json.dumps(self.checks[-1]), flush=True)
        super().stopTest(test)


def main():
    started = time.perf_counter()
    context = upstream.read(RUN/'context-W05.json')
    files = list(context['source_bindings'])
    for p in [PREDECESSOR, PACKAGE/'receipts/action-boundaries/0004.json']:
        previous = upstream.read(p)
        require(previous['result'] == 'PASS', 'W05 prerequisite receipt not passed')
        files += previous['files'] + previous.get('source_bindings', []) + [binding(p)]
    own = list(HERE.glob('*.py')) + list((PACKAGE/'evidence').glob('*.py')) + list((PACKAGE/'challenges').glob('*.py'))
    own += [HERE/'README.md', RUN/'context-W05.json', RUN/'CONTEXT-W05.md']
    for kind in OUTPUT_KINDS | {'product-capability'}:
        own.append(ROOT/carrier(kind)[0]['schema_path'])
    for row in upstream.read(upstream.PAIRS)['exact_pairs']:
        if row['relation_kind_ref'] in {'relation.scopes-authority-over', 'relation.declares-effect-on', 'relation.evidence-bears-on',
            'relation.realizes', 'relation.produces', 'relation.affects', 'relation.occurs-during', 'relation.member-of',
            'relation.governed-by', 'relation.derives-from', 'relation.instance-of', 'relation.evaluates', 'relation.controls',
            'relation.challenges', 'relation.successor-of'}:
            own.append(ROOT/row['relation_binding']['path'])
    files += [binding(p) for p in own]
    selected = {}
    for row in files:
        require(row['path'] not in selected or selected[row['path']]['sha256'] == row['sha256'], 'conflicting W05 source pins')
        require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'], 'W05 source/prerequisite drift: '+row['path'])
        selected[row['path']] = {'path': row['path'], 'sha256': row['sha256']}
    files = list(selected.values())
    directory = HERE/'receipts'; directory.mkdir(exist_ok=True)
    number = 1
    while (directory/f'{number:04d}').exists() or (directory/f'{number:04d}.json').exists():
        number += 1
    output = directory/f'{number:04d}'; output.mkdir()
    (output/'manifest.json').write_bytes(encoded({'authority_effect': 'none', 'files': files}))
    print(json.dumps({'stage': 'sources-frozen', 'files': len(files), 'output': output.relative_to(ROOT).as_posix()}), flush=True)
    from failures import test_services
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_services)
    with (output/'W05-checks.log').open('w') as stream:
        guards = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recording).run(suite)
    sys.path.insert(0, str(PACKAGE/'receipts/action-boundaries'))
    import test_boundaries
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_boundaries)
    with (output/'W02-regression.log').open('w') as stream:
        regression = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recording).run(suite)
    episode = None; cold = None; error = None
    print(json.dumps({'stage': 'separate-actual-controlled-episode', 'synthetic_production_effects': False}), flush=True)
    try:
        e, _, refs, challenge = prepare_episode(output/'observed')
        try:
            p = e.output/'episode-index.json'
            result = subprocess.run([sys.executable, str(HERE/'episode.py'), '--cold', str(p), byte_sha(p.read_bytes())],
                capture_output=True, timeout=20)
            (output/'cold-stdout.json').write_bytes(result.stdout)
            (output/'cold-stderr.log').write_bytes(result.stderr)
            require(result.returncode == 0, 'actual episode cold verification failed')
            cold = parse(result.stdout)
            episode = upstream.read(p)
        finally:
            e.host.session.close()
    except Exception:
        error = traceback.format_exc()
        (output/'episode-error.log').write_text(error)
    drift = [r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes()) != r['sha256']]
    passed = guards.wasSuccessful() and guards.testsRun == 48 and regression.wasSuccessful() and regression.testsRun == 42
    passed = passed and episode is not None and episode['challenge_state'] == 'resolved' and cold is not None and cold['result'] == 'PASS' and not drift
    review_members = []
    if episode:
        for name in ['evidence_adapter', 'failure_adapter', 'challenge_adapter', 'probe_adapter']:
            ref = episode['selected_refs'][name]
            row = next(r for r in episode['records'] if r['version_ref'] == ref)
            path = output/'observed'/row['path']
            value = upstream.read(path)
            review_members.append({'identity_ref': value['node_id'], 'version_ref': ref, 'kind': 'implementation',
                'target': binding(path), 'scope': 'exact controlled candidate adapter source and evidence only',
                'owner_outcome': None, 'authority_effect': 'none'})
    receipt = {'schema_version': 'lab-W05-evidence-failure-challenge-suite/v1-candidate', 'task': 'W05', 'authority_effect': 'none',
        'result': 'PASS' if passed else 'FLAG', 'task_complete': bool(passed), 'tests': guards.testsRun+regression.testsRun,
        'W05_tests': guards.testsRun, 'regression_tests': regression.testsRun, 'checks': guards.checks+regression.checks,
        'duration_seconds': time.perf_counter()-started, 'source_drift': drift,
        'files': files+[binding(p) for p in output.rglob('*') if p.is_file()], 'source_bindings': context['source_bindings'],
        'cold_verification': cold, 'episode_error': error, 'review_members': review_members,
        'actual_owner_outcome': None, 'canonical_effects_applied': 0,
        'remaining_obligations': [] if passed else ['All 48 guards, 42 regressions and separate actual controlled episode/cold verification must pass.'],
        'downstream_model_gap': {'inventory_pair': 'authority-boundary -> decision-scope / scopes-authority-over',
            'current_typed_schema': 'pair absent', 'selected_supported_pair': 'authority-claim -> decision-scope',
            'route': 'O05/S02 exact model reconciliation; no extension inferred'},
        'claim_ceiling': 'Bounded candidate evidence/classification/failure/challenge adapters, original controlled historical builder rejection, independently validated successor and local fixture disposition only. Poison/timeout checks are synthetic fixtures. No original-environment, production Incident, confirmed cause, control effectiveness, canonical admission, actual R08 outcome or generic API completeness.'}
    path = directory/f'{number:04d}.json'; path.write_bytes(encoded(receipt))
    print(json.dumps({'result': receipt['result'], 'task_complete': receipt['task_complete'], 'tests': receipt['tests'],
        'receipt': path.relative_to(ROOT).as_posix(), 'actual_owner_outcome': None}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
