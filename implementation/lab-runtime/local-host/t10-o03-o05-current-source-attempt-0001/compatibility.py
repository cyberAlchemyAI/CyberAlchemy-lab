"""Actual original-archive/current-T12 compatibility check for O05."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
ARCHIVE_SHA = '03850c8aa4cf7a994f3ce66c25cb68d4567c170ed38e40dc24e115a3e900f944'
CURRENT = ROOT / 'implementation/lab-runtime/local-host/t10-o03-current-engine-successor-0002/run-current-0002/RESULT.json'
CURRENT_SHA = 'c4da8c121facbbc859c000d3ae0f165681ee5777e2d38e95b49d97c9e8fa48f2'
OLD_LOOKUP = '8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12'
NEW_LOOKUP = '12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984'
SOURCE = 'authority/project-state-transitions/current.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def archive_inputs():
    raw = ARCHIVE.read_bytes()
    if sha(raw) != ARCHIVE_SHA:
        raise ValueError('original O05 archive changed')
    archive = json.loads(raw)
    if (archive['private_key_included'] is not False or archive['Session_memory_included'] is not False or
            archive['authority_effect'] != 'none' or archive['actual_owner_outcome'] is not None or
            set(archive['files']) != {'config.json', 'baseline.json', 'HEAD.json',
                                      'transactions/0000000000.json', 'transactions/0000000001.json'}):
        raise ValueError('original O05 archive closure/posture changed')
    files = {}
    for name, row in archive['files'].items():
        data = base64.b64decode(row['base64_original_bytes'], validate=True)
        if sha(data) != row['sha256']:
            raise ValueError('original O05 member bytes changed')
        files[name] = data
    baseline = json.loads(files['baseline.json'])
    if (baseline['materials'][SOURCE] != OLD_LOOKUP or
            baseline['profile']['current_selection']['lookup'] != {'path': SOURCE, 'sha256': OLD_LOOKUP} or
            archive['project_pins']['baseline_snapshot_digest'] != baseline['snapshot_digest']):
        raise ValueError('original archive does not select D75 baseline')
    return archive, files, baseline


def attempt():
    archive, files, baseline = archive_inputs()
    if sha((ROOT / SOURCE).read_bytes()) != NEW_LOOKUP or NEW_LOOKUP == OLD_LOOKUP:
        raise ValueError('current specialist lookup not selected')
    if sha(CURRENT.read_bytes()) != CURRENT_SHA:
        raise ValueError('current O03 receipt changed')
    sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/local-host/t10-o03-current-engine-successor-0002'))
    import query_run
    current = query_run.verify_result(CURRENT.parent)
    if current['scope'] != 'current-specialist-owner':
        raise ValueError('current O03 scope differs')
    sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'))
    from lab_runtime.replay import ReplayPins, full_replay
    from lab_runtime.common import RuntimeFault
    with tempfile.TemporaryDirectory(prefix='cal-O05-original-replay-') as temp:
        path = Path(temp)
        for name, raw in files.items():
            dest = path / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as out:
                out.write(raw)
        pins = ReplayPins(**archive['project_pins'])
        historical = full_replay(path, ROOT, ROOT, pins, require_current=False)
        if historical['head']['sequence'] != 1:
            raise ValueError('original historical replay sequence differs')
        try:
            full_replay(path, ROOT, ROOT, pins, require_current=True)
        except RuntimeFault as error:
            if str(error) != 'full replay rejected: stale repository sources: ' + SOURCE:
                raise ValueError('current replay refused for another reason') from error
        else:
            raise ValueError('old O05 archive unexpectedly accepted as current')
    return {'schema_version': 'lab-T10-O03-O05-original-current-compatibility/v1',
            'result': 'REFUSED-ORIGINAL-ARCHIVE-AS-CURRENT',
            'historical_replay': 'PASS', 'historical_head_sequence': 1,
            'historical_baseline_snapshot_digest': baseline['snapshot_digest'],
            'archived_lookup_sha256': OLD_LOOKUP, 'current_lookup_sha256': NEW_LOOKUP,
            'current_t12_query_receipt_sha256': CURRENT_SHA,
            'incompatibility': 'Pinned original baseline/profile requires D75 lookup bytes; current-source full replay rejects the T12 specialist lookup. A fresh signed source branch and translated O05 event package are required.',
            'query_executed': False, 'selected_governed_models': 0, 'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(attempt(), sort_keys=True))
