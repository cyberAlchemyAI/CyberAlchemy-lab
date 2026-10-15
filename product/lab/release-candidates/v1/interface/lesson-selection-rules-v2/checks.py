"""Run complete pure selection and immutable W06 suites with exact source guards."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

from rules import HERE, ROOT, encoded, sha, source_guard


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def main():
    source = source_guard()
    started = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_*.py')
    assert suite.countTestCases() == 61
    text = io.StringIO()
    result = unittest.TextTestRunner(stream=text, verbosity=2).run(suite)
    old = ROOT / 'implementation/lab-workflows/candidates/v1/learning'
    process = subprocess.run([sys.executable, '-B', '-m', 'unittest', '-v', 'test_learning'], cwd=old,
                             capture_output=True, timeout=300)
    original_text = process.stdout + process.stderr
    full_original = b'Ran 53 tests' in original_text and process.returncode == 0 and b'\nOK\n' in original_text
    unchanged = source_guard() == source
    output = HERE / 'receipts'
    output.mkdir(exist_ok=False)
    pure_log = output / 'pure-0001.log'
    original_log = output / 'W06-0001.log'
    with pure_log.open('x') as stream: stream.write(text.getvalue())
    with original_log.open('xb') as stream: stream.write(original_text)
    passed = result.wasSuccessful() and result.testsRun == 61 and full_original and unchanged
    report = {'schema_version': 'lab-lesson-selection-rules-checks/v1-candidate', 'result': 'PASS' if passed else 'FAIL',
              'source_sha256': source, 'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'pure_cases': result.testsRun, 'pure_failures': len(result.failures), 'pure_errors': len(result.errors),
              'original_W06_cases': 53 if full_original else None, 'original_W06_actual_exit_code': process.returncode,
              'original_W06_full_suite_completed': full_original, 'source_unchanged_before_and_after': unchanged,
              'actual_public_calls': 0, 'synthetic_unit_inputs': True, 'public_handler_integrated': False,
              'actual_live_Session_qualified': False, 'genuine_review_provided': False, 'applications_created': 0,
              'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False,
              'files': [bind(HERE/'source-manifest.json'), bind(pure_log), bind(original_log)],
              'claim_ceiling': '61 complete synthetic pure rule cases and 53 unchanged original W06 tests only; no public host, live Session, owner review, admission or plan completion.'}
    receipt = output / 'checks-0001.json'
    with receipt.open('x') as stream: json.dump(report, stream, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({'result': report['result'], 'report_binding': bind(receipt), 'pure_cases': result.testsRun,
                      'W06_cases': report['original_W06_cases'], 'task_complete': False}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
