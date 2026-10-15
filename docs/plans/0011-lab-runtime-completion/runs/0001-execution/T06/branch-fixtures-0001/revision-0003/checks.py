"""Focused candidate-driver controls; no Lab runtime or Session is constructed."""
import base64
import copy
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_T06_driver_controls', HERE / 'drive_operator.py')
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)


def reject(callback):
    try:
        callback()
    except (ValueError, OSError):
        return
    raise AssertionError('selected control did not refuse')


def main():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    rows = []
    def check(name, callback):
        callback(); rows.append({'check': name, 'status': 'PASS'})
    def same(value, expected):
        if value != expected:
            raise AssertionError('independent expectation differs')
    refs = {'agent-instance': 'test:original-instance@1', 'agent-session': 'test:original-session@1'}
    old = {'instance': 'test:old-instance', 'session': 'test:old-session'}
    fresh = {'instance': 'test:fresh-instance', 'session': 'test:fresh-session'}
    status = {'runtime_handle_bindings': {refs['agent-instance']: old['instance'], refs['agent-session']: old['session']},
              'head': 'original-head', 'stopped': False, 'revoked_refs': [], 'periods': {'fixed': [1, 900]},
              'active_policy_refs': ['original-policy'], 'role_versions': {'original-role': 'original-role@1'},
              'gates': {'original-gate': False}, 'reached_stop_conditions': [], 'selected_work_ref': 'original-work'}
    source = {'schema_version': 'lab-action-owned-source/v1-candidate', 'refs': refs, 'runtime_bindings': old,
              'records': {'original-role@1': {'original_b64': 'b3JpZ2luYWwtcm9sZQ==', 'sha256': 'unchanged-byte-pin'}},
              'scope_ref': 'original-scope', 'initial_status': status, 'authority_effect': 'none', 'actual_owner_outcome': None}
    grant = {'source_sha256': 'old-pin', 'not_before': time.time() - 1, 'expires_at': time.time() + 600,
             'max_actions': 8, 'max_input_bytes': 4096, 'max_output_bytes': 4096, 'recovery_allowed': True,
             'scope_ref': 'original-scope', 'role_assignment_ref': 'original-assignment', 'allowed_operations': ['action.evaluate']}
    policy = {'source_binding': {'ref': 'old-source', 'sha256': 'old-pin'}, 'grant_binding': {'ref': 'old-grant', 'sha256': 'old-pin'},
              'expires_at': 'fixed-original-expiry', 'public_key': 'fixed-key', 'scope_ref': 'original-scope',
              'max_calls': 128, 'revoked': False, 'allowed_operations': ['action.evaluate'], 'authority_effect': 'none'}
    initial = {name: D.compact(value) for name, value in [('source.json', source), ('status.json', status),
                                                       ('grant.json', grant), ('channel-policy.json', policy)]}
    initial['ledger-pins.json'] = b'  {"unchanged":"ledger"}\n'
    signer = Ed25519PrivateKey.generate()
    snapshot = copy.deepcopy(initial); material = D.handoff_materials(initial, fresh, signer)
    check('original-input-bytes-remain-unchanged', lambda: same(initial, snapshot))
    expected_source = copy.deepcopy(source); expected_source['runtime_bindings'] = fresh
    handles = {refs['agent-instance']: fresh['instance'], refs['agent-session']: fresh['session']}
    expected_source['initial_status']['runtime_handle_bindings'] = handles
    check('only-exact-source-attribution-changes-no-record-role-scope-authority-change', lambda: same(D.parse(material['source.json']), expected_source))
    expected_status = copy.deepcopy(status); expected_status['runtime_handle_bindings'] = handles
    check('status-revocation-stop-gate-periods-preserved', lambda: same(D.parse(material['status.json']), expected_status))
    expected_grant = copy.deepcopy(grant); expected_grant['source_sha256'] = sha256(material['source.json']).hexdigest()
    check('grant-period-budget-scope-role-permission-unchanged', lambda: same(D.parse(material['grant.json']), expected_grant))
    expected_policy = copy.deepcopy(policy)
    expected_policy['source_binding'] = {'ref': 'action-source:' + sha256(material['source.json']).hexdigest(), 'sha256': sha256(material['source.json']).hexdigest()}
    expected_policy['grant_binding'] = {'ref': 'action-grant:' + sha256(material['grant.json']).hexdigest(), 'sha256': sha256(material['grant.json']).hexdigest()}
    check('policy-only-byte-links-change-current-permission-preserved', lambda: same(D.parse(material['operator-policy.json']), expected_policy))
    check('ledger-original-spacing-and-bytes-preserved', lambda: same(material['ledger-pins.json'], initial['ledger-pins.json']))
    check('source-signature-verifies-exact-new-raw-bytes-original-signer', lambda: signer.public_key().verify(base64.b64decode(material['source.signature'], validate=True), material['source.json']))
    check('missing-fresh-session-attribution-refuses', lambda: reject(lambda: D.handoff_materials(initial, {'instance': 'only'}, signer)))
    check('blank-fresh-session-attribution-refuses', lambda: reject(lambda: D.handoff_materials(initial, {**fresh, 'session': ''}, signer)))
    malformed = copy.deepcopy(initial); malformed_source = copy.deepcopy(source)
    malformed_source['initial_status']['runtime_handle_bindings']['extra'] = 'unselected'
    malformed['source.json'] = D.compact(malformed_source)
    check('extra-original-runtime-attribution-refuses', lambda: reject(lambda: D.handoff_materials(malformed, fresh, signer)))
    check('duplicate-control-key-refuses', lambda: reject(lambda: D.parse(b'{"x":1,"x":2}')))
    check('nonfinite-control-value-refuses', lambda: reject(lambda: D.parse(b'{"x":NaN}')))
    root = Path(tempfile.mkdtemp(prefix='cal-T06-branch-fixtures-controls-')); root.chmod(0o700)
    nested = root / 'nested'; nested.mkdir(mode=0o700)
    path = nested / 'selected.json'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(b'original-private-test-bytes')
    row = D.selector(path); root_id = D.identity(root.lstat())
    check('actual-nofollow-bounded-private-capture', lambda: same(D.protected(row, root, root_id), b'original-private-test-bytes'))
    check('private-size-budget-refuses-before-body-return', lambda: reject(lambda: D.protected(row, root, root_id, 4)))
    check('independent-private-digest-mismatch-refuses', lambda: reject(lambda: D.protected({**row, 'sha256': '0' * 64}, root, root_id)))
    check('independent-private-inode-mismatch-refuses', lambda: reject(lambda: D.protected({**row, 'identity': [row['identity'][0], row['identity'][1] + 1, *row['identity'][2:]]}, root, root_id)))
    # Retain the actual original directory; a different attached parent is not
    # allowed to borrow its identity even if it contains equal private bytes.
    renamed = root / 'retained-original'; nested.rename(renamed)
    nested.symlink_to(renamed, target_is_directory=True)
    check('actual-ancestor-symlink-refuses', lambda: reject(lambda: D.protected(row, root, root_id)))
    original = D.ROOT / 'product/lab/release-candidates/v1/interface/api-action-integration-v3/fixture.py'
    successor = HERE.parent / 'action_fixture_signer_retained_v1.py'
    check('producer-exact-one-statement-delta-no-original-change', lambda: same(successor.read_bytes().replace(b'  self.source_signer=signer\n', b'', 1), original.read_bytes()))
    result = {'schema_version': 'lab-T06-driver-focused-controls/v1-candidate', 'status': 'PASS', 'checks': rows,
              'check_count': len(rows), 'actual_runtime_constructor_executed': False, 'actual_Session_constructed': False,
              'actual_governing_authority': False, 'authority_effect': 'none', 'private_key_public_exported': False,
              'private_test_state_retained': True, 'whole_API_qualified': False}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
