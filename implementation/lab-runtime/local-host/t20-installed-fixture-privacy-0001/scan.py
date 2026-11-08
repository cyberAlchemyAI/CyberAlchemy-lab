"""Cold privacy scan of the exact installed Docker fixture result and logs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRIVACY = ROOT / 'implementation/lab-runtime/local-host/t20-local-privacy-0001/scan.py'
PRIVACY_SHA = '8d01bcb71ade520f9fc8a168e4708bf3509a1a4cbdba1424ade2eddd0296e76b'
RUN = ROOT / 'implementation/lab-runtime/local-host/t25-runtime-docker-runner-0002/working-docker-0002'
RESULT_SHA = '312f9378750e585003881be4e071c3f634f46cd8f267fed5d699daeb922d3e87'
PHASES = ('installed-replay', 'fixture-context', 'docker-build',
          'chain-fixture', 'lab-fixture')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def selected(path: Path, expected: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError('selected privacy input absent or linked')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('selected privacy input bytes changed')
    return raw


def run() -> dict:
    source = selected(PRIVACY, PRIVACY_SHA)
    privacy = types.ModuleType('_cal_t20_selected_privacy')
    privacy.__file__ = str(PRIVACY)
    exec(compile(source, str(PRIVACY), 'exec'), privacy.__dict__)
    result = privacy.strict_json(selected(RUN / 'RESULT.json', RESULT_SHA))
    if (result.get('result') != 'PASS' or result.get('authority_effect') != 'none'
            or result.get('portable_api_closure_complete') is not False
            or [item.get('phase') for item in result.get('steps', [])] != list(PHASES)
            or result.get('image_cleanup', {}).get('exit_code') != 0):
        raise ValueError('selected Docker receipt does not establish bounded success')
    privacy.scan_json(result)
    scanned = []
    for item in [*result['steps'], result['image_cleanup']]:
        phase = item['phase']
        path = RUN / (phase + '.log')
        if item.get('log') != path.relative_to(ROOT).as_posix():
            raise ValueError('selected phase log path differs')
        raw = selected(path, item['log_sha256'])
        if (privacy.PRIVATE_BLOCK.search(raw) or privacy.SECRET_ASSIGNMENT.search(raw)
                or privacy.PRIVATE_LOCATOR.search(raw)):
            raise ValueError('private material, credential or locator in selected Docker log')
        if phase == 'lab-fixture':
            privacy.scan_runtime_log(raw)
        scanned.append({'phase': phase, 'sha256': sha(raw), 'bytes': len(raw)})
    return {'schema_version': 'lab-T20-installed-public-fixture-privacy/v1',
            'status': 'PASS-SELECTED-CLASSES',
            'docker_result_sha256': RESULT_SHA,
            'privacy_scanner_sha256': PRIVACY_SHA,
            'scanner_driver_sha256': sha(Path(__file__).read_bytes()),
            'logs_scanned': scanned,
            'private_key_blocks': 0, 'credential_assignments': 0,
            'original_api_service_scanned': False,
            'protected_source8_scanned': False,
            'full_privacy_qualified': False,
            'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
