"""Independent inert checks for frozen signed-scope Docker plan 0002."""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CAND = BASE / 'context-successor-signed-scope-docker-plan-0002'
FREEZE_SHA = '957671b00d3055ef23046571a59e1016b2e945290d77c214639092df11cde5fc'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(name):
    spec = importlib.util.spec_from_file_location('independent_' + name, CAND / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def refused(fn):
    try:
        fn()
    except Exception:
        return
    raise AssertionError('invalid input accepted')


def main():
    freeze_raw = (CAND / 'freeze.json').read_bytes()
    assert sha(freeze_raw) == FREEZE_SHA
    freeze = json.loads(freeze_raw)
    assert freeze['effect_enabled'] is False and freeze['real_effect'] == 'NOT_RUN'
    assert all(sha((CAND / name).read_bytes()) == digest
               for name, digest in freeze['members'].items())
    plan = module('plan')
    observer = module('observer')
    at = dt.datetime(2026, 10, 20, 18, 30, tzinfo=dt.timezone.utc)
    basis = plan.pinned_basis(at)
    assert basis['reader_manifest_sha256'] == plan.READER_MANIFEST_SHA
    assert basis['source_manifest_sha256'] == plan.SOURCE_MANIFEST_SHA
    assert basis['loader_freeze_sha256'] == plan.LOADER_FREEZE_SHA
    assert basis['controller_review_sha256'] == plan.CONTROLLER_REVIEW_SHA
    assert basis['portable_freeze_sha256'] == plan.PORTABLE_FREEZE_SHA
    assert not os.path.lexists(plan.CLAIM) and not os.path.lexists(plan.ATTESTATION)
    assert json.loads((plan.BUNDLE / 'manifest.json').read_bytes())['private_archive'] == 'NOT_COPIED'
    projected = plan.plan(at, 'b' * 32)
    argv = projected['create_argv']
    mounts = [argv[i + 1] for i, v in enumerate(argv) if v == '--mount']
    assert len(mounts) == 3 and mounts == [
        f'type=bind,src={plan.STAGE},dst={plan.STAGE},readonly',
        f'type=bind,src={plan.BUNDLE},dst=/bundle,readonly',
        f'type=bind,src={plan.CLAIM},dst=/control/attempt.claim,readonly']
    assert argv[-1].startswith('raise SystemExit("EFFECT_DISABLED')
    assert projected['effect_enabled'] is False and projected['docker_invoked'] is False
    for fn in (plan.execute, plan.create_claim, observer.dispatch, observer.publish_attestation):
        refused(fn)

    class Result:
        returncode = 0
        stderr = b''
        stdout = f'{plan.IMAGE} amd64 20001:20001 /attempt/root\n'.encode()

    class Absent:
        returncode = 1
        stdout = b'\n'
        stderr = ('Error response from daemon: No such container: ' + plan.NAME + '\n').encode()

    def runner(argv, **_):
        return Absent() if argv[1:3] == ['container', 'inspect'] else Result()

    assert plan.docker_readonly_observation(runner)['container_absent'] is True
    for malformed in (False, 0.0):
        Result.returncode = malformed
        refused(lambda: plan.docker_readonly_observation(runner))
    Result.returncode = 0
    for malformed in (True, 1.0):
        Absent.returncode = malformed
        refused(lambda: plan.docker_readonly_observation(runner))
    Absent.returncode = 1

    marker = 'f' * 64
    identity = {'dev': 1, 'ino': 2}
    terminal = {'cid': 'a' * 64, 'exit_code': 0, 'oom_killed': False}
    row = {'schema': 'context-signed-scope-child-attestation/v1',
           'status': 'PROVISIONAL_EXTERNAL_OBSERVER_ONLY',
           'scope_ref': basis['scope_expected'],
           'source_manifest_sha256': basis['source_manifest_sha256'],
           'reader_manifest_sha256': basis['reader_manifest_sha256'],
           'reader_code_sha256': basis['reader_code_sha256'],
           'loader_freeze_sha256': basis['loader_freeze_sha256'],
           'controller_freeze_sha256': basis['controller_freeze_sha256'],
           'source_period_sha256': basis['source_period_sha256'],
           'opened_at': '2026-10-20T18:30:00+00:00',
           'closed_at': '2026-10-20T18:31:00+00:00',
           'claim_marker_sha256': marker, 'claim_dev': 1, 'claim_ino': 2,
           'first_guard': True, 'final_guard': True, 'reader_guard': True,
           'close_ok': True, 'authority_effect': 'none',
           'actual_owner_outcome': None, 'retry_allowed': False}

    def raw(item):
        return (json.dumps(item, sort_keys=True, separators=(',', ':')) + '\n').encode()

    args = (basis, marker, identity, raw(row), b'', 0, terminal, True)
    assert observer.validate_fixture_envelope(*args)['status'] == 'SYNTHETIC_ENVELOPE_VALID_NO_EFFECT_CLAIM'
    count = 0
    for index in (5,):
        for bad in (False, 0.0):
            changed = list(args)
            changed[index] = bad
            refused(lambda changed=changed: observer.validate_fixture_envelope(*changed))
            count += 1
    for bad in (False, 0.0):
        changed = list(args)
        changed[6] = terminal | {'exit_code': bad}
        refused(lambda changed=changed: observer.validate_fixture_envelope(*changed))
        count += 1
    for key, bad in (('dev', True), ('dev', 1.0), ('ino', 2.0)):
        changed = list(args)
        changed[2] = identity | {key: bad}
        refused(lambda changed=changed: observer.validate_fixture_envelope(*changed))
        changed = list(args)
        changed[3] = raw(row | {'claim_' + key: bad})
        refused(lambda changed=changed: observer.validate_fixture_envelope(*changed))
        count += 2
    changed = list(args)
    changed[3] = raw(row | {'close_ok': False})
    refused(lambda: observer.validate_fixture_envelope(*changed))
    count += 1
    changed = list(args)
    changed[3] = b'{"schema":1,"schema":2}\n'
    refused(lambda: observer.validate_fixture_envelope(*changed))
    count += 1
    print(json.dumps({'freeze_sha256': FREEZE_SHA, 'independent_causal_refusals': count,
                      'public_basis': 'PASS', 'effect': 'NOT_RUN'}, sort_keys=True))


if __name__ == '__main__':
    main()
