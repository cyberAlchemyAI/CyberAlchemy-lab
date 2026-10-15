"""Rebuild absent selected code, requiring exact historical executable bytes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SOURCE = ROOT / 'product/lab/release-candidates/v1/interface/mapped-native-v2'
BUILD = Path('/tmp/cal-R03-mapped-native-build-0002')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not BUILD.exists(), 'restore only an absent owned code root'
    manifest = SOURCE / 'source-manifest.json'
    assert sha(manifest) == '76b4d42aa43d9cd3f94010f65bf96d2269f6cc6f92a2cbca16eaf400adcafddb'
    selected = json.loads(manifest.read_bytes())
    for row in selected['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    BUILD.mkdir(mode=0o700)
    for row in selected['copies']:
        source = ROOT / row['binding']['path']
        assert sha(source) == row['binding']['sha256']
        target = BUILD / row['target']
        assert target.is_relative_to(BUILD)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    for name in ['reader', 'ontology']:
        shutil.copyfile(SOURCE / 'receipts' / (name + '-resolved-lock.toml'), BUILD / name / 'Cargo.lock')
    env = dict(os.environ)
    env['CARGO_TARGET_DIR'] = str(BUILD / 'target')
    command = ['cargo', 'build', '--offline', '--frozen', '--manifest-path', str(BUILD / 'reader/Cargo.toml')]
    with (RUN / 'native-code-restoration-0003.stdout').open('xb') as stdout, (RUN / 'native-code-restoration-0003.stderr').open('xb') as stderr:
        completed = subprocess.run(command, stdout=stdout, stderr=stderr, env=env)
    executable = BUILD / 'target/debug/lab-context-native-reader'
    expected = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
    actual = sha(executable) if executable.is_file() else None
    identity = completed.returncode == 0 and actual == expected
    result = {'schema_version': 'lab-code-restoration/v1-candidate', 'result': 'PASS' if identity else 'FAIL',
        'actual_exit_code': completed.returncode, 'command': command, 'expected_sha256': expected,
        'actual_sha256': actual, 'native_byte_identity': identity, 'original_receipts_unchanged': True,
        'no_existing_workspace_or_session_restored': True, 'authority_effect': 'none', 'task_complete': False}
    with (RUN / 'native-code-restoration-0003.json').open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(result), flush=True)
    return 0 if identity else 1


if __name__ == '__main__':
    raise SystemExit(main())
