"""Byte-backed, no-replace replay of the bounded T08 full technical boundary."""

import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
PRIOR = Path('implementation/lab-runtime/local-host/t08-current-mixed-boundary-0001')
HERE = Path(__file__).resolve().parent
WORK = HERE / 'working'
PINS = {
    PRIOR / 'run_boundary.py': 'd9f2bb14c7f5eb5f2a2decbc1ca71afce9c20f0f4ea358d9936d2927e4dd6311',
    PRIOR / 'execute.py': 'bf9865d5eaf852263ecd646d13869a3c0bddbd1b1dfb568dc9c967189403fac9',
    PRIOR / 'current_content.py': '47180629c3179d1a349b24c659d5fbbfe13adc8beb3859cf7738c729c6f4acaf',
    PRIOR / 'working/RESULT-0002.json': '669533df4a0e739d8a4c7a4c9ab680b6bef2dc24d9e29d549f856707a167a571',
    Path('product/lab/release-candidates/v1/interface/api-integration-v33-current-0001/source-manifest.json'):
        'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd',
    Path('product/lab/release-candidates/v1/interface/api-integration-v33-current-0001/contract-profile.json'):
        'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a',
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(relative, digest):
    need(not relative.is_absolute() and '..' not in relative.parts,
         'unsafe selected path')
    fd = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=fd)
            os.close(fd)
            fd = following
        leaf = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                       dir_fd=fd)
        try:
            need(stat.S_ISREG(os.fstat(leaf).st_mode), 'selected nonregular file')
            with os.fdopen(os.dup(leaf), 'rb') as source:
                raw = source.read(16 * 1024 * 1024 + 1)
            need(len(raw) <= 16 * 1024 * 1024 and sha(raw) == digest,
                 'selected byte origin differs')
            return raw
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


def byte_module(name, filename, raw):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / filename)
    sys.modules[name] = module
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def publish(name, data):
    fd = os.open(WORK / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def run():
    need(WORK.is_dir() and not WORK.is_symlink() and
         stat.S_IMODE(WORK.stat().st_mode) == 0o700,
         'private no-replace replay directory required')
    need(not any((WORK / name).exists() for name in
                 ('RUN-0002.log', 'RESULT-0002.json', 'REPLAY-ATTESTATION.json')),
         'replay output already exists')
    selected = {path: exact(path, digest) for path, digest in PINS.items()}
    runner = byte_module('run_boundary', PRIOR / 'run_boundary.py',
                         selected[PRIOR / 'run_boundary.py'])
    execute = byte_module('_cal_t08_pinned_positive_execute', PRIOR / 'execute.py',
                          selected[PRIOR / 'execute.py'])
    execute.WORK = WORK
    prior_args = sys.argv
    try:
        sys.argv = [str(PRIOR / 'execute.py'), '--serial', '0002']
        code = execute.main()
    finally:
        sys.argv = prior_args
    unchanged = all(exact(path, digest) == selected[path]
                    for path, digest in PINS.items())
    need(unchanged, 'selected runner/executor/source bytes changed during replay')
    result_raw = exact((WORK / 'RESULT-0002.json').relative_to(ROOT),
                       sha((WORK / 'RESULT-0002.json').read_bytes()))
    result = json.loads(result_raw)
    need(code == 0 and result['result'] == 'PASS-bounded-technical-full-boundary'
         and result['full_reader_entry_exit_verified_this_run'] is True
         and result['historical_content_verified_this_run'] is True
         and result['actual_semantic_graph_executed'] is True
         and result['original_full_proof_status'] == 'REFUSED'
         and result['historical_content']['original_locator_physical_closure'] == 'REFUSED',
         'replayed positive claim differs')
    attestation = {
        'schema_version': 'lab-T08-byte-backed-positive-replay/v1-candidate',
        'result': 'PASS-bounded-technical-replay',
        'runner_code_sha256': PINS[PRIOR / 'run_boundary.py'],
        'execute_code_sha256': PINS[PRIOR / 'execute.py'],
        'content_code_sha256': PINS[PRIOR / 'current_content.py'],
        'prior_positive_receipt_sha256': PINS[PRIOR / 'working/RESULT-0002.json'],
        'replay_receipt_sha256': sha(result_raw),
        'selected_pre_and_post_equal': unchanged,
        'source_sha256': PINS[next(k for k in PINS if k.name == 'source-manifest.json')],
        'profile_sha256': PINS[next(k for k in PINS if k.name == 'contract-profile.json')],
        'full_reader_entry_exit_verified': True,
        'historical_content_verified': True,
        'semantic_graph_executed': True,
        'original_locator_physical_closure': 'REFUSED',
        'original_full_proof_status': 'REFUSED',
        'installation_release_builder_used': False,
        'authority_effect': 'none', 'T08_complete': False,
    }
    publish('REPLAY-ATTESTATION.json',
            (json.dumps(attestation, sort_keys=True, indent=2) + '\n').encode())
    return attestation


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, allow_nan=False))
