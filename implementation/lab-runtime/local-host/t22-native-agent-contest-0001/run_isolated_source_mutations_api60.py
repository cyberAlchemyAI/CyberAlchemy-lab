"""Exercise the selected physical capture verifier on isolated source copies.

The test copies one signed family member and one selected baseline material
under the same relative paths into a disposable root. No live repository
source, shared baseline, or private archive byte is changed.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v60-t22-pinned-family-source-0001'
SOURCE_SHA = 'a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c'
PROFILE_SHA = '7c263b912f56c7e5256ff8426d64f0325564038fad84a54f0f6a714ed568a34b'
RECEIPT = HERE / 'ISOLATED-SOURCE-MUTATIONS-API60-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode or RECEIPT.exists():
        raise ValueError('isolated no-replace source probe required')
    sys.path.insert(0, str(API.parent))
    package = API.name
    guard = importlib.import_module(package + '.guard')
    source_manifest = guard.verify(SOURCE_SHA)
    if source_manifest['profile_binding']['sha256'] != PROFILE_SHA:
        raise ValueError('selected API60 profile differs')
    test = importlib.import_module(package + '.test_custody_sessions')
    test.PROFILE = PROFILE_SHA
    cls = test.Sessions
    try:
        cls.setUpClass()
        view = cls.view
        producer = view.integrated_reader.adapter.source
        captured = producer.B.SOURCE_CAPTURE
        capture_pin = producer.B._CAPTURE_PIN
        baseline = view.data['baseline']['materials']
        baseline_ref = 'product/lab/release-candidates/v1/interface/api-v3/connection-corrections/agent-policy/record.json'
        if baseline_ref not in baseline:
            raise ValueError('selected baseline material not present')
        family_manifest = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d3537e8c3cb77a71/context/packages/0001/manifest.json'
        body = json.loads(family_manifest.read_bytes())
        family_row = next(row for row in body['files'] if row['path'].endswith('/artifacts/00.json'))
        baseline_row = {'path': baseline_ref, 'sha256': baseline[baseline_ref]}
        rows = [family_row, baseline_row]
        originals = {}
        with tempfile.TemporaryDirectory(prefix='cal-T22-API60-isolated-source-') as scratch:
            isolated = Path(scratch)
            isolated.chmod(0o700)
            for row in rows:
                raw = (ROOT / row['path']).read_bytes()
                if sha(raw) != row['sha256']:
                    raise ValueError('selected source has drifted before isolated copy')
                target = isolated / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                originals[row['path']] = raw
            check = lambda: captured.verify_all(isolated, rows, code_sha256=capture_pin)
            if check() != len(rows):
                raise ValueError('isolated selected capture did not accept exact copies')
            results = []
            for row in rows:
                target = isolated / row['path']
                original = originals[row['path']]
                try:
                    target.write_bytes(original + b' ')
                    try:
                        check()
                    except ValueError as error:
                        refusal = str(error)
                        if 'selected source input bytes changed' not in refusal:
                            raise ValueError('mutation refused for another reason: ' + refusal) from error
                    else:
                        raise ValueError('physical source mutation was accepted')
                finally:
                    target.write_bytes(original)
                if check() != len(rows):
                    raise ValueError('restored isolated source did not verify')
                results.append({'path': row['path'], 'selected_sha256': row['sha256'],
                                'isolated_mutation_refused': True,
                                'refusal': refusal, 'restored_copy_verified': True})
        result = {
            'schema_version': 'lab-T22-API60-isolated-source-mutations/v1-candidate',
            'result': 'PASS',
            'api_source_sha256': SOURCE_SHA,
            'api_profile_sha256': PROFILE_SHA,
            'capture_kernel_sha256': capture_pin,
            'selected_baseline_material_count': len(baseline),
            'members': results,
            'live_repository_source_mutated': False,
            'authority_effect': 'none',
        }
    finally:
        cls.doClassCleanups()
    raw = json.dumps(result, sort_keys=True, indent=2).encode() + b'\n'
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'result': 'PASS', 'sha256': sha(raw)}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
