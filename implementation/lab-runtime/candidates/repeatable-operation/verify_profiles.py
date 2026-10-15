#!/usr/bin/env python3
"""Execute C04 verification and bind real results to exact current candidate bytes."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    started = time.monotonic()
    command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE / 'tests'), '-p', 'test_profiles.py', '-v']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
    log = result.stdout + result.stderr
    cases = [line.split(' ', 1)[0] for line in log.splitlines() if line.startswith('test_') and line.endswith(' ... ok')]
    out = HERE / 'receipts/C04'
    out.mkdir(parents=True, exist_ok=True)
    number = 1
    while (out / f'{number:04d}.json').exists():
        number += 1
    log_path = out / f'{number:04d}.log'
    log_path.write_text(log)
    files = sorted([p for p in (HERE / 'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts]
                   + [HERE / 'lab.py', HERE / 'build_profiles.py', Path(__file__).resolve(), HERE / 'tests/test_profiles.py', HERE / 'schemas/source-profile.schema.json']
                   + list((HERE / 'profiles').rglob('*.json')))
    receipt = {'schema_version': 'lab-C04-verification/v1-candidate', 'authority_effect': 'none',
        'task': 'C04', 'result': 'PASS' if result.returncode == 0 and len(cases) == 23 else 'FAIL',
        'scope': 'Explicit selection/capture for real D74/D75 and isolated native fixtures; no authority channel or operational API is certified.',
        'command': command, 'returncode': result.returncode, 'duration_seconds': time.monotonic() - started,
        'test_count': len(cases), 'passed_cases': cases,
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'dependencies': {name: version(name) for name in ['jsonschema', 'referencing', 'cryptography']}},
        'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'size_bytes': p.stat().st_size} for p in files],
        'log': {'path': log_path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(log_path.read_bytes()).hexdigest()},
        'original_runtime_packages_modified': False, 'repository_admissions_applied': 0,
        'real_operational_stores_provisioned': 0, 'pilot_observations': 0}
    (out / f'{number:04d}.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ['files', 'passed_cases', 'command', 'environment']}, indent=2))
    if receipt['result'] != 'PASS':
        print(log)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
