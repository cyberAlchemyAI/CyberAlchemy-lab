#!/usr/bin/env python3
"""Preserve actual bounded isolated C05 test evidence, including failed attempts."""
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest

PACKAGE = Path(__file__).resolve().parent; ROOT = PACKAGE.parents[3]
if len(sys.argv) > 1 and sys.argv[1] == '--worker':
    sys.path.insert(0, str(PACKAGE / 'tests'))
    import test_transition
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_transition.TransitionTests)
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    value = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
             'successful': result.wasSuccessful(), 'observed': test_transition.TransitionTests.observed,
             'log': output.getvalue()}
    Path(sys.argv[2]).write_text(json.dumps(value, indent=2) + '\n')
    print(output.getvalue(), flush=True); sys.exit(0 if result.wasSuccessful() else 1)

started = time.perf_counter(); directory = PACKAGE / 'receipts/C05'; directory.mkdir(parents=True, exist_ok=True)
index = 1
while (directory / f'{index:04d}.json').exists(): index += 1
with TemporaryDirectory(prefix='lab-transition-check-output-') as temp:
    out = Path(temp) / 'result.json'; error = None
    try:
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', str(out)],
                                 capture_output=True, text=True, timeout=300)
        stdout, stderr, returncode = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
        stderr = (exc.stderr or b'').decode() if isinstance(exc.stderr, bytes) else exc.stderr or ''
        returncode = 124; error = '300 second isolated verification budget exceeded'
    data = json.loads(out.read_text()) if out.exists() else {'successful': False, 'tests': 0, 'failures': 0, 'errors': 1, 'observed': None}
    log = directory / f'{index:04d}.log'; log.write_text(stdout + stderr)
    observation = None
    if data['successful'] and data['observed']:
        example_dir = PACKAGE / 'examples/transition' / f'{index:04d}'; example_dir.mkdir(parents=True)
        observation = example_dir / 'observed-isolated-transition.json'
        observation.write_text(json.dumps(data['observed'], indent=2, sort_keys=True) + '\n')
    files = [Path(__file__).resolve(), PACKAGE / 'tests/test_transition.py', PACKAGE / 'lab_runtime/transition.py',
             PACKAGE / 'lab_runtime/common.py', PACKAGE / 'lab_runtime/profiles.py', PACKAGE / 'lab_runtime/sources.py',
             PACKAGE / 'lab_runtime/replay.py', PACKAGE / 'lab_runtime/store.py', PACKAGE / 'schemas/branch-transition.schema.json',
             PACKAGE / 'design/branch-transition-contract.md', PACKAGE / 'design/contract-impact.json',
             ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-C05.json', log]
    files += list((PACKAGE / 'profiles').rglob('*.json'))
    files += list((ROOT / 'implementation/lab-runtime/v1/lab_runtime').glob('*.py'))
    files += [ROOT / 'implementation/lab-runtime/v1/profile.json', PACKAGE / 'design/legacy-runtime-bindings.json']
    if observation: files.append(observation)
    passed = returncode == 0 and data['successful'] and data['tests'] == 20 and data['observed'] is not None
    receipt = {'schema_version': 'lab-branch-transition-check/v1-candidate', 'task': 'C05',
        'result': 'PASS' if passed else 'FLAG', 'task_complete': passed, 'authority_effect': 'none',
        'duration_seconds': time.perf_counter() - started, 'tests': {k:data[k] for k in ['tests','failures','errors']},
        'error': error, 'returncode': returncode, 'environment': {'python': sys.version, 'platform': platform.platform()},
        'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))],
        'scope': 'Isolated actual signed D74 parent to independently selected D75 candidate successor; four-way review classification, exact approval, cold fresh-process replay, no-replace publication and interruption recovery. No general successor writer or semantic admission.',
        'real_operational_stores_provisioned': 0, 'repository_admissions_applied': 0, 'actual_owner_outcome': None}
    path = directory / f'{index:04d}.json'; path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k:receipt[k] for k in ['result','task_complete','tests','duration_seconds','error']}))
    print(path.relative_to(ROOT).as_posix()); sys.exit(0 if passed else 1)
