"""Independent checks of selected real Work outputs and public archive bytes."""
import base64
import copy
from tempfile import TemporaryDirectory
from episode import *
from lab_runtime.replay import ReplayPins


def verify_audit_exact(value):
    check_audit(value)
    current = review.validate_preparation(PREPARATION, PREPARATION_SHA)
    expected = {m['member_id']: m for m in current['members']}
    require(set(expected) == {m['member_id'] for m in value['members']}, 'audit selected different members')
    require(value['target'] == review.binding(PREPARATION), 'audit preparation binding differs')
    paths = {}
    for row in value['members']:
        original = expected[row['member_id']]
        for key in ['member_class', 'proposed_owner_roles', 'requested_effect', 'exclusions']:
            require(row[key] == original[key], 'audit changed exact member boundary')
        require(row['dependency_ids'] == original['dependencies'], 'audit changed member dependencies')
        checks = row['source_checks']
        require([(c['path'], c['expected_sha256']) for c in checks] == [(r['path'], r['sha256']) for r in original['targets'] + original['evidence']], 'audit omitted or substituted exact source check')
        for check in checks: paths[check['path']] = check['observed_sha256']
    require(paths == value['source_file_digests'] and len(paths) == value['unique_source_files_checked'], 'audit source inventory differs')
    require(value['owner_authority_gaps'] == [r['member_id'] for r in value['members']], 'audit omitted actual authority gap')
    require(value['performance_posture'] == current['retained_performance_posture'], 'performance limit disappeared')
    return True


def decode_archive(path, external_sha256):
    raw = path.read_bytes(); require(byte_digest(raw) == external_sha256, 'independent archive pin differs')
    value = json.loads(raw)
    require(value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None,
            'public candidate archive claims human authority')
    require(value['private_key_included'] is False and value['Session_memory_included'] is False, 'archive contains private scope')
    require(set(value['files']) == {'config.json', 'baseline.json', 'HEAD.json', 'transactions/0000000000.json', 'transactions/0000000001.json'}, 'unexpected archive closure')
    files = {}
    for name, row in value['files'].items():
        data = base64.b64decode(row['base64_original_bytes'], validate=True)
        require(byte_digest(data) == row['sha256'], 'archive original file bytes changed')
        require(b'PRIVATE KEY' not in data and b'C12 temporary audit hypothesis' not in data, 'private bytes entered public archive')
        files[name] = data
    return value, files


def restore_archive(path, external_sha256, destination):
    value, files = decode_archive(path, external_sha256)
    require(not destination.exists() and not destination.resolve().is_relative_to(ROOT), 'archive restore must use a new isolated path')
    destination.mkdir(mode=0o700)
    for name, raw in files.items():
        output = destination / name; output.parent.mkdir(exist_ok=True)
        output.write_bytes(raw)
    return full_replay(destination, ROOT, ROOT, ReplayPins(**value['project_pins']), require_current=True)
