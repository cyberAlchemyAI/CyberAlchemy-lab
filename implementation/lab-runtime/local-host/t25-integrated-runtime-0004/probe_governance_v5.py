"""Isolated current T12 governance source probe; no repository admission."""

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
GOVERNANCE = INTERFACE / 'api-governance-integration-v5-current-t12-0001'
sys.path.insert(0, str(INTERFACE))
GF = importlib.import_module(GOVERNANCE.name + '.fixture')
GS = importlib.import_module(GOVERNANCE.name + '.schemas')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def run(output):
    source = GOVERNANCE / 'source-manifest.json'
    profile = GOVERNANCE / 'contract-profile.json'
    source_pin = '8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337'
    profile_pin = '7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3'
    need(sha(source.read_bytes()) == source_pin and sha(profile.read_bytes()) == profile_pin,
         'current T12 governance source/profile differs')
    need(not output.exists() and output.parent.is_dir() and not output.is_relative_to(ROOT),
         'fresh private result outside repository required')
    with tempfile.TemporaryDirectory(prefix='cal-api76-governance-v5-') as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        fixture = GF.Fixture(root, GS.GovernanceSchemas())
        try:
            before = fixture.host.snapshot()['head']['transaction_digest']
            negative = fixture.checkpoint_call('api76:current-t12:negative')
            negative['caller_context_ref'] = 'context:foreign'
            negative_reply = fixture.service.call(GF.encoded(negative))
            need(negative_reply['kind'] == 'error' and negative_reply['message']['code'] == 'unauthorized',
                 'foreign authenticated context was not refused')
            need(fixture.host.snapshot()['head']['transaction_digest'] == before,
                 'refused governance call changed native head')
            positive = fixture.checkpoint_call('api76:current-t12:positive')
            positive_reply = fixture.service.call(GF.encoded(positive))
            need(positive_reply['kind'] == 'result' and positive_reply['operation'] == 'checkpoint.resolve',
                 'current T12 governance checkpoint did not return a native result')
            need(fixture.host.snapshot()['head']['transaction_digest'] == before,
                 'checkpoint qualification changed native repository head')
            after = fixture.host.snapshot()['head']['transaction_digest']
        finally:
            fixture.service.close()
            fixture.channel.close()
    need(sha(source.read_bytes()) == source_pin and sha(profile.read_bytes()) == profile_pin,
         'governance source/profile changed during probe')
    result = {'schema_version': 'lab-current-t12-governance-isolated-probe/v1',
              'result': 'PASS', 'source_sha256': source_pin, 'profile_sha256': profile_pin,
              'positive_operation': 'checkpoint.resolve', 'positive_kind': 'result',
              'negative_code': 'unauthorized', 'negative_effect': 'none',
              'native_head_unchanged': before == after, 'private_fixture_removed': not root.exists(),
              'common_api_dispatch_exercised': False, 'authority_effect': 'none'}
    raw = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
    handle = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(handle, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'result': 'PASS', 'receipt': str(output), 'sha256': sha(raw)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output.absolute()), sort_keys=True), flush=True)
