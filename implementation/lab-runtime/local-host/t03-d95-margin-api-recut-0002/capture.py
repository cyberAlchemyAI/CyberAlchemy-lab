"""Replay cold d95 margin checks and atomically record a bounded receipt."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
TARGET = HERE / 'PREFLIGHT-RESULT.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(argv: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=180,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    if result.returncode:
        raise RuntimeError('selected cold replay failed: ' + result.stderr[-3000:])
    return result


def main() -> dict:
    tests = HERE / 'test_margin.py'
    preflight = HERE / 'preflight.py'
    launcher = HERE / 'launch.py'
    normal_tests = checked([sys.executable, '-m', 'unittest', '-v', str(tests)])
    optimized_tests = checked([sys.executable, '-O', '-m', 'unittest', '-v', str(tests)])
    if 'Ran 10 tests' not in normal_tests.stderr or 'Ran 10 tests' not in optimized_tests.stderr:
        raise ValueError('focused causal test inventory changed')
    first = json.loads(checked([sys.executable, str(launcher), str(preflight)]).stdout)
    second = json.loads(checked([sys.executable, str(launcher), '--optimized', str(preflight)]).stdout)
    if first != second or not all(first[k] == 'PASS' for k in
                                  ('schema_guard', 'source_code_guard', 'installed_dependency_guard',
                                   'instrumentation_guard', 'live_profile_correspondence')) or first['live_profile_causal_negatives'] != 3:
        raise ValueError('normal/optimized selected cold preflight differs')
    result = {'schema_version': 'lab-T03-d95-margin-cold-preflight/v1-candidate',
              'selection': first, 'normal_causal_tests': 10, 'optimized_causal_tests': 10,
              'helper_sha256': sha(HERE / 'margin.py'),
              'launcher_sha256': sha(launcher),
              'preflight_sha256': sha(preflight),
              'test_sha256': sha(tests),
              'api_rebind_receipt_sha256': sha(margin_api_rebind()),
              'api_recut_result_sha256': sha(HERE / 'RESULT.json'),
              'owned_installation_receipt_sha256': sha(HERE / 'installation-receipt.json'),
              'runtime_executed': False, 'lesson_applied': False, 'lesson_assessed': False,
              'authority_effect': 'none'}
    raw = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
    with tempfile.NamedTemporaryFile(dir=HERE, prefix='.preflight-', delete=False) as output:
        temporary = Path(output.name)
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, TARGET)
    return result


def margin_api_rebind() -> Path:
    return ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-margin-0006/rebind-receipt.json'


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
