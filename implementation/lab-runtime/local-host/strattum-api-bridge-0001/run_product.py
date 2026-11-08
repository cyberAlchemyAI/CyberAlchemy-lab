"""One-command local signed-cut Project State answer over the installed Reader.

The live mode launches the selected installed API75 Reader capture, then cold
verifies and composes two bounded answers. Existing-capture mode replays the
same composition without another Source scan. Output stays owner-private.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess

from verify_capture import canonical, digest, verify


ROOT = Path(__file__).resolve().parents[4]
COMPOSER = ROOT / 'product/lab/release-candidates/v1/interface/signed-cut-project-state-v1/composer.py'
CAPTURE = Path(__file__).with_name('capture.py')
SELECTED_PYTHON = Path('/home/vlad_/.local/share/cyberalchemy-lab/final-local-product-20261026-0003/installation/runtime/repository/implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_new(path, value):
    raw = canonical(value) + b'\n'
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return digest(raw)


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def composer_module():
    spec = importlib.util.spec_from_file_location('lab_strattum_signed_cut_composer', COMPOSER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(output, *, capture=None, private_snapshot=None, selected_python=SELECTED_PYTHON):
    output = Path(output).absolute()
    require(not output.exists() and output.parent.is_dir()
            and not any(part.is_symlink() for part in output.parents),
            'fresh private output under a real parent required')
    output.mkdir(mode=0o700)
    sync_dir(output.parent)
    write_new(output / 'INTENT.json', {'schema_version': 'lab-signed-cut-project-state-run-intent/v1',
                                      'mode': 'capture-replay' if capture else 'installed-reader-live',
                                      'status': 'started', 'authority_effect': 'none'})
    sync_dir(output)
    try:
        if capture is None:
            capture = output / 'capture'
            selected_python = Path(selected_python).absolute()
            require(selected_python.is_file(), 'selected installed Python unavailable')
            child = subprocess.run([str(selected_python), '-B', str(CAPTURE),
                                    '--output', str(capture)], capture_output=True,
                                   timeout=1800, check=False)
            require(child.returncode == 0, 'installed Reader capture failed: '
                    + str(child.returncode) + ' stderr-sha256=' + digest(child.stderr))
        capture = Path(capture).absolute()
        verified = verify(capture, private_snapshot)
        raw = (capture / 'CAPTURE.json').read_bytes()
        retained = json.loads(raw)
        composer = composer_module()
        answers = []
        for row in retained['reads']:
            answer = composer.compose_project_state(
                canonical(row['query_call']), canonical(row['query_reply']),
                canonical(row['inspect_call']), canonical(row['inspect_reply']),
                row['artifact'], row['source_cut'])
            require(answer['authority_effect'] == 'none' and answer['citations']
                    and answer['assessment'] == 'API30 discrepancy assessment pending',
                    'bounded answer requirements missing')
            answers.append(answer)
        require(len(answers) == 2 and answers[0]['source_cut'] != answers[1]['source_cut']
                and answers[0]['artifact'] != answers[1]['artifact'],
                'two distinct signed-cut states required')
        result = {'schema_version': 'lab-signed-cut-project-state-answers/v1-candidate',
                  'capture_sha256': digest(raw), 'composer_sha256': digest(COMPOSER.read_bytes()),
                  'verification': verified, 'answers': answers,
                  'date_mapping': 'not-claimed', 'per_record_acl': 'not-claimed',
                  'authority_effect': 'none'}
        answer_sha = write_new(output / 'ANSWERS.json', result)
        require(digest((output / 'ANSWERS.json').read_bytes()) == answer_sha,
                'answer cold read mismatch')
        write_new(output / 'COMPLETED.json', {
            'schema_version': 'lab-signed-cut-project-state-run-receipt/v1',
            'status': 'complete', 'answer_sha256': answer_sha,
            'capture_sha256': digest(raw),
            'cut_sha256s': [row['source_cut']['commit_sha256'] for row in retained['reads']],
            'authority_effect': 'none'})
        sync_dir(output)
        return {'result': 'PASS', 'output': str(output), 'answer_sha256': answer_sha,
                'cut_sequences': [row['source_cut']['commit_sequence'] for row in retained['reads']],
                'names': [(a['citations'][0]['value'] if not a['citations'][0]['truncated']
                           else a['citations'][0]['value_preview'] + '… [truncated]')
                          for a in answers],
                'reader_signature': verified['reader_signature'],
                'private_fixture_snapshot': verified['private_fixture_snapshot'],
                'authority_effect': 'none'}
    except Exception as exc:
        write_new(output / 'REFUSAL.json', {'schema_version': 'lab-signed-cut-project-state-refusal/v1',
                                            'status': 'refused', 'exception_type': type(exc).__name__,
                                            'reason': str(exc)[:300], 'authority_effect': 'none'})
        sync_dir(output)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--capture')
    choice.add_argument('--live', action='store_true')
    parser.add_argument('--private-snapshot')
    parser.add_argument('--selected-python', default=str(SELECTED_PYTHON))
    args = parser.parse_args()
    print(json.dumps(run(args.output, capture=args.capture,
                         private_snapshot=args.private_snapshot,
                         selected_python=args.selected_python), sort_keys=True))
