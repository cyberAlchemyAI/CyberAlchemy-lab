"""Cold-verify and seal the bounded five-method API52 fixture probe."""

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v52-t16-metadata-current-0001'
SOURCE_SHA = '060b501c32bb9cc3292f0e2a3124a89770ab5f69c6a749a823c466660dc96020'
PROFILE_SHA = '5da736d675d92e9fc72b1a197eea27d449610b2be8c621075aec81380fcb9c12'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
ROWS = {
    'challenge-grant': '4d0b7d091d223a67383ef9fb8c05f072179e8f292131f4ba15239f5b1cadb667',
    'challenge-positive': '257ac16e7d3c5f07e686f49a99ada479599402233936e32abf47bdd8dec4aa31',
    'expired': 'd79b020572ff1fc688e35f6f9237870fcfe6856aff304f58c3bfc38f87e9697f',
    'protected-body': 'adeef5e94239fd59c1a790402c7548937f2d85b6d90033cfcece5d346e64cca2',
    'protected-metadata': '3d6ba0f55d675e0cf2f2e2e219ba98e55c17762cd1d07d82b90328a7a9ad061d',
}
PREDECESSOR_NEGATIVES = {
    'api50_old_challenge_source': (
        'implementation/lab-runtime/local-host/t16-api50-fixture-recut-0001/working/challenge-grant-RESULT.json',
        '8fc4849fcdff66d266d0b1912f90e7890e57e31ee1be1e46c19140ba4d7d2c41',
        'independent source environment differs'),
    'api51_metadata_scope': (
        'implementation/lab-runtime/local-host/t16-api51-challenge-recut-0001/working/challenge-grant-RESULT.json',
        '8a9ac765d49cc424493c7d4a8ff99c218a55143250b9ea91ab430966c215b6bf',
        'metadata grant cannot claim original Agent participation or owner authority'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected(path, digest):
    raw = path.read_bytes()
    if sha(raw) != digest:
        raise ValueError('selected focused evidence changed: ' + str(path))
    return raw


def main():
    selected(API / 'source-manifest.json', SOURCE_SHA)
    selected(API / 'contract-profile.json', PROFILE_SHA)
    inventory = json.loads(selected(INVENTORY, INVENTORY_SHA))
    expected = {case for ids in inventory['buckets'].values() for case in ids}
    if len(expected) != 345:
        raise ValueError('inherited 345-case inventory differs')
    records = []
    for name, digest in ROWS.items():
        path = HERE / 'working' / (name + '-RESULT.json')
        result = json.loads(selected(path, digest))
        if (result['source_manifest_sha256'] != SOURCE_SHA or result['profile_sha256'] != PROFILE_SHA
                or result['inventory_sha256'] != INVENTORY_SHA or not result['entry_guard_pass']
                or not result['exit_guard_pass'] or not result['source_unchanged_during_run']
                or result['tests_run'] != 1 or result['selected_case_id'] not in expected):
            raise ValueError('focused case source/guard/identity differs: ' + name)
        wanted = 'REFUSED' if name == 'challenge-positive' else 'PASS'
        if result['status'] != wanted:
            raise ValueError('focused case verdict differs: ' + name)
        records.append({'name': name, 'path': path.relative_to(ROOT).as_posix(),
                        'sha256': digest, 'case_id': result['selected_case_id'],
                        'status': result['status']})
    if len({item['case_id'] for item in records}) != 5:
        raise ValueError('focused case IDs overlap')
    negatives = {}
    for name, (relative, digest, cause) in PREDECESSOR_NEGATIVES.items():
        result = json.loads(selected(ROOT / relative, digest))
        if result['status'] != 'REFUSED' or cause not in '\n'.join(result['errors']):
            raise ValueError('historical source refusal differs: ' + name)
        negatives[name] = {'path': relative, 'sha256': digest, 'cause': cause}
    result = {
        'schema_version': 'lab-T16-API52-focused-fixture-summary/v1',
        'api_source_manifest_sha256': SOURCE_SHA,
        'api_profile_sha256': PROFILE_SHA,
        'inherited_inventory_sha256': INVENTORY_SHA,
        'inherited_method_count': 345,
        'same_cut_method_results': records,
        'same_cut_passed': 4,
        'same_cut_failed': 1,
        'same_cut_without_terminal_result': 340,
        'predecessor_refusals': negatives,
        'positive_challenge_failure': 'challenge.submit returned invalid-contract after authenticated setup; no proposal or authority effect',
        'claim_ceiling': 'Focused fixture repair only; T15 and full 345-method T16 remain open.',
    }
    target = HERE / 'FOCUSED-SUMMARY-0001.json'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(sha(target.read_bytes()))


if __name__ == '__main__':
    main()
