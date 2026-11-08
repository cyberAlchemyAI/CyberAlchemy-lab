"""Cold, sequential T02 evidence stitch; never describes one uninterrupted run."""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001'
V4 = BASE / 'source8-api30-rebind-0004'
V5 = BASE / 'source8-api30-rebind-0005'
V6 = BASE / 'source8-api30-rebind-0006'
V8 = BASE / 'source8-api30-rebind-0008'
PINS = {
    'v4_result': (V4 / 'working/whole-classes-result-0001.json',
                  '90c3c6ca270031930351485ff9a70660240d55b2186393abe46c32f55d26427f'),
    'v5_result': (V5 / 'working/remainder-result-0001.json',
                  '20b649f019253210123a4b345d9a6a8305a6cc5e7b11b158345e341ac307e143'),
    'v6_result': (V6 / 'working/machine-result-0001.json',
                  '076565b442d47bfa431b8ec228da4ac5f5243250f4bf9c2829acdb8b49797ecd'),
    'v8_result': (V8 / 'working/machine-split-result-0001.json',
                  'e423ddb82aa528c326dc857aa3b5e54b953d00c98f4bd1dd8d518f832263f0b9'),
    'v4_runner': (V4 / 'run_whole.py',
                  '03ef57c50c519375e99e656fcf885135f63f5b941ea295032ad6af8e3e170f0b'),
    'v5_runner': (V5 / 'run_remainder.py',
                  '0511ceca71d145c4753a469e56a8ac99655d1565b65ef91e57c35593421a02ea'),
    'v6_runner': (V6 / 'run_machine.py',
                  'caf8af0a0994ce936f606d5fcc39930ad7deafef1cba72b3fbc2d8458d60fe92'),
    'v8_runner': (V8 / 'run_machine_split.py',
                  '378dabe057de58c28e29614624deb9b52350f114a5cbc529c84f14f89586a9c2'),
    'source_manifest': (API / 'source-manifest.json',
                  'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'),
    'contract_profile': (API / 'contract-profile.json',
                  'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a'),
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(path):
    path = Path(path)
    return path.is_file() and all(not part.is_symlink() for part in (path, *path.parents))


def selected():
    captured = {}
    for name, (path, expected) in PINS.items():
        need(len(expected) == 64, name + ' pin absent')
        need(regular(path), name + ' path unavailable')
        raw = path.read_bytes()
        need(sha(raw) == expected, name + ' byte differs')
        captured[name] = raw
    manifest = json.loads(captured['source_manifest'])
    for row in manifest['files']:
        path = ROOT / row['path']
        need(regular(path) and
             sha(path.read_bytes()) == row['sha256'], 'selected API source row differs')
    return {name: json.loads(captured[name]) for name in
            ('v4_result', 'v5_result', 'v6_result', 'v8_result')}


def reconcile(a, b, failed, c):
    ids = a['selected_case_ids']
    need(len(ids) == 99 and len(set(ids)) == 99, 'selected 99-case inventory differs')
    need(a['class_case_counts'] == {'run_session_checks': 34, 'test_custody_sessions': 34,
                                   'test_current_controls': 11, 'test_termination_boundaries': 6,
                                   'test_machine_transport': 14}, 'whole-class counts differ')
    need(a['tests_run'] == 69 and len(a['case_rows']) == 69 and
         [x['test_id'] for x in a['case_rows']] == ids[:69] and
         all(x['result'] == 'PASS' for x in a['case_rows'][:68]) and
         a['case_rows'][68]['result'] == 'FAIL', 'v4 prefix evidence differs')
    need(len(a['failures']) == 1 and not a['errors'] and
         'selected R02 participation environment differs' in a['failures'][0][1],
         'v4 historical constructor refusal differs')
    need(a['wrong_origin_old_source_refused'] is True and
         all(a[k] is True for k in ('source_unchanged_during_run',
                                    'harness_unchanged_during_run',
                                    't06_operator_unchanged_during_run',
                                    'stable_native_executable_unchanged_during_run')),
         'v4 source or harness evidence differs')
    need(b['predecessor_result_sha256'] == PINS['v4_result'][1] and
         b['runner_sha256'] == PINS['v5_runner'][1] and
         b['source_manifest_sha256'] == PINS['source_manifest'][1] and
         b['profile_sha256'] == PINS['contract_profile'][1],
         'v5 selected predecessor differs')
    need(b['selected_case_ids'] == ids[68:] and b['tests_run'] == 17 and
         len(b['case_rows']) == 17 and
         [x['test_id'] for x in b['case_rows']] == ids[68:85] and
         all(x['result'] == 'PASS' for x in b['case_rows']) and
         not b['failures'] and len(b['errors']) == 1 and
         "NameError: name 'PROFILE' is not defined" in b['errors'][0][1] and
         b['source_unchanged_during_run'] is True,
         'v5 corrected negative/17-case evidence differs')
    need('test_01_expired_legacy_source_refuses_new_session_grant' in ids[68] and
         'policy period guard separately refuses expired Assignment' in b['expired_original_claim'],
         'corrected historical negative claim differs')
    need(failed['result'] == 'FAIL' and failed['tests_run'] == 2 and
         [row['result'] for row in failed['case_rows']] == ['PASS', 'ERROR'] and
         failed['selected_case_ids'] == ids[85:] and
         failed['source_unchanged_during_run'] is True,
         'v6 deadline diagnostic differs')
    need(c['result'] == 'PASS' and c['predecessor_v6_result_sha256'] == PINS['v6_result'][1] and
         c['runner_sha256'] == PINS['v8_runner'][1] and
         c['source_manifest_sha256'] == PINS['source_manifest'][1] and
         c['profile_sha256'] == PINS['contract_profile'][1] and
         c['source_unchanged_during_run'] is True and
         c['selected_case_ids'] == ids[85:] and c['tests_run'] == 14 and
         len(c['case_rows']) == 14 and
         [x['test_id'] for x in c['case_rows']] == ids[85:] and
         all(x['result'] == 'PASS' for x in c['case_rows']) and
         not c['failures'] and not c['errors'], 'v8 14-case evidence differs')
    split = c['split_seven_read_evidence']
    need(len(split) == 1 and split[0]['first_operations'] ==
         ['lab.status', 'catalog.get', 'artifact.query', 'artifact.inspect'] and
         split[0]['second_operations'] == ['context.get', 'session.inspect', 'operation.inspect'] and
         split[0]['first_session_ref_sha256'] != split[0]['second_session_ref_sha256'] and
         split[0]['fresh_second_context_delivery'] is True and
         split[0]['original_session_expiry_unchanged'] is True,
         'v8 real split-Session proof differs')
    expiry = datetime.fromisoformat(a['selected_source_period_expires_at'])
    need(datetime.fromisoformat(a['completed_at_utc']) <
         datetime.fromisoformat(b['started_at_utc']) <
         datetime.fromisoformat(b['completed_at_utc']) <
         datetime.fromisoformat(failed['started_at_utc']) <
         datetime.fromisoformat(failed['completed_at_utc']) <
         datetime.fromisoformat(c['started_at_utc']) <
         datetime.fromisoformat(c['completed_at_utc']) < expiry,
         'sequential source-period chronology differs')
    return {'result': 'PASS', 'scope': 'sequential-three-process-replay',
            'uninterrupted_99_case_run': False, 'selected_case_count': 99,
            'passed_case_count': 99, 'selected_source_manifest_sha256': PINS['source_manifest'][1],
            'selected_profile_sha256': PINS['contract_profile'][1],
            'v4_68_pass_case_ids': ids[:68], 'v5_17_pass_case_ids': ids[68:85],
            'v8_14_pass_case_ids': ids[85:],
            'historical_original_negative': 'constructor environment refusal; separate policy period refusal with source preflight disabled',
            'wrong_origin_old_source_refused': True,
            'current_source8_machine_extra_case': 'not included',
            'actual_per_case_lease_origin': 'not established by this stitch',
            'input_sha256': {name: value[1] for name, value in PINS.items()}}


def main():
    snapshots = selected()
    result = reconcile(snapshots['v4_result'], snapshots['v5_result'],
                       snapshots['v6_result'], snapshots['v8_result'])
    out = HERE / 'working'
    out.mkdir(mode=0o700, exist_ok=True)
    target = out / 'STITCH-0001.json'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(json.dumps(result, sort_keys=True, indent=2).encode() + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'result': 'PASS', 'passed_case_count': 99,
                      'scope': result['scope']}))


if __name__ == '__main__':
    main()
