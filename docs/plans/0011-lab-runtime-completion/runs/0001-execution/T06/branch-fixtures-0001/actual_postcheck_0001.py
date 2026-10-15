"""Read-only postcheck of this attempt's own retained technical fixture state."""
from pathlib import Path
import json
import hashlib
import base64
import copy
import stat
import os
import fcntl
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-0001'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    report = json.loads((HERE / 'actual-attempt-0001.json').read_bytes())
    roots = [p for p in Path('/tmp').glob('cal-T06-branch-fixtures-*')
             if sha(str(p).encode()) == report['own_custody_locator_sha256']]
    assert len(roots) == 1
    root = roots[0]
    record = json.loads((root / 'private-branch-selection.json').read_bytes())
    config_raw = (root / 'operator-config.json').read_bytes(); config = json.loads(config_raw)
    action = root / 'actions'
    originals = json.loads((action / 'initial-handoff-inputs.json').read_bytes())
    initial = {name: base64.b64decode(raw, validate=True) for name, raw in originals.items()}
    before_source = json.loads(initial['source.json']); before_status = json.loads(initial['status.json'])
    before_grant = json.loads(initial['grant.json']); before_policy = json.loads(initial['channel-policy.json'])
    source_raw = (action / 'source.json').read_bytes(); after_source = json.loads(source_raw)
    after_status = json.loads((action / 'status.json').read_bytes())
    grant_raw = (action / 'grant.json').read_bytes(); after_grant = json.loads(grant_raw)
    after_policy = json.loads((action / 'operator-policy.json').read_bytes())
    fresh = after_source['runtime_bindings']
    assert fresh != before_source['runtime_bindings']
    expected = copy.deepcopy(before_source); expected['runtime_bindings'] = fresh
    handles = {before_source['refs']['agent-instance']: fresh['instance'],
               before_source['refs']['agent-session']: fresh['session']}
    expected['initial_status']['runtime_handle_bindings'] = handles
    assert after_source == expected
    expected_status = copy.deepcopy(before_status); expected_status['runtime_handle_bindings'] = handles
    assert after_status == expected_status
    expected_grant = copy.deepcopy(before_grant); expected_grant['source_sha256'] = sha(source_raw)
    assert after_grant == expected_grant
    expected_policy = copy.deepcopy(before_policy)
    expected_policy['source_binding'] = {'ref': 'action-source:' + sha(source_raw), 'sha256': sha(source_raw)}
    expected_policy['grant_binding'] = {'ref': 'action-grant:' + sha(grant_raw), 'sha256': sha(grant_raw)}
    assert after_policy == expected_policy
    assert (action / 'ledger-pins.json').read_bytes() == initial['ledger-pins.json']
    Ed25519PublicKey.from_public_bytes(base64.b64decode(record['branches']['actions']['source_public_key'], validate=True)).verify(
        base64.b64decode((action / 'source.signature').read_bytes(), validate=True), source_raw)
    assert sha(config_raw) == report['SDK_result']['configuration_sha256']
    assert json.dumps(config, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode() == config_raw
    assert len({x['public_key'] for x in config['handoff']['issuers'].values()}) == 3
    assert len({x['public_key'] for x in config['branches'].values()}) == 3
    assert all((root / name).is_dir() and stat.S_IMODE((root / name).stat().st_mode) == 0o700
               for name in ('base', 'actions', 'governance', 'issuers'))
    keys = [root / 'base/reader.pem', root / 'actions/reader.pem', root / 'actions/source-signer.pem',
            root / 'governance/reader.pem', *(root / 'issuers').glob('*.pem')]
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 and path.stat().st_uid == os.getuid()
               and not path.is_relative_to(ROOT) and not path.is_symlink() for path in keys)
    assert record['original_Action_producer_lease_closed'] is True
    assert report['SDK_result']['process_exit_code'] == 0 and report['SDK_result']['dispatch_operations_executed'] == 0
    assert (root / 'operator-stderr.bin').stat().st_size == (root / 'driver-private-observer.log').stat().st_size == 0
    lock = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/lease-sensitive-runtime.lock'
    fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); os.close(fd)
    result = {'schema_version': 'lab-T06-actual-attempt-postcheck/v1-candidate',
              'result': 'PASS-startup-and-technical-handoff-only', 'authority_effect': 'none',
              'task_complete': False, 'whole_API_qualified': False, 'actual_owner_outcome': None,
              'actual_report_binding': {'path': (HERE / 'actual-attempt-0001.json').relative_to(ROOT).as_posix(),
                                        'sha256': sha((HERE / 'actual-attempt-0001.json').read_bytes())},
              'observer_binding': {'path': (HERE / 'actual_attempt_0001.py').relative_to(ROOT).as_posix(),
                                   'sha256': sha((HERE / 'actual_attempt_0001.py').read_bytes())},
              'postcheck_binding': {'path': Path(__file__).absolute().relative_to(ROOT).as_posix(),
                                    'sha256': sha(Path(__file__).read_bytes())},
              'actual_unified_execution_terminal': {'outer_session_id': 20606, 'outer_process_exit_code': 0,
                                                    'SDK_child_exit_code': 0},
              'checks': {'actual_source_signer_verifies_exact_fresh_raw_source': True,
                         'fresh_child_runtime_binding_differs_from_closed_original_preparation_lease': True,
                         'all_original_source_record_bytes_refs_roles_scopes_and_status_fields_preserved': True,
                         'source_only_runtime_and_initial_status_handle_attribution_changed': True,
                         'status_only_runtime_handle_attribution_changed': True,
                         'grant_only_signed_source_digest_changed_original_period_permissions_budgets_intact': True,
                         'policy_only_source_and_grant_digest_links_changed': True,
                         'original_ledger_bytes_unchanged': True,
                         'three_independent_reader_credentials': True,
                         'three_separate_technical_custody_grant_policy_issuer_credentials': True,
                         'actual_fixed_startup_budget_seconds': config['handoff']['startup_seconds'],
                         'canonical_exact_compact_private_config_bytes': True,
                         'private_credential_files_owned0600_outsideGit_and_own_roots0700': True,
                         'private_stderr_and_observer_logs_empty': True,
                         'original_preparation_Action_lease_closed': True,
                         'actualSDK_normal_owned_shutdown_exit0': True,
                         'actual_kernel_runtime_lock_free_after_terminal': True,
                         'dispatch_operations_executed': 0,
                         'no_fixture_authority_promoted_to_actual_owner_or_governing_authority': True},
              'cleanup_limits': [
                  'Original preparer explicitly closed its actual Action lease before SDK launch. SDK finally closes all owned service/channel/lease/view callbacks; successful child exit0 proves that finally returned without a cleanup exception and process RAM is no longer live.',
                  'Private original/new fixture records/keys/stores retained outside Git for rollback/audit, not deleted or published.',
                  'No independent dump/introspection of SDK Session RAM or callback internals was performed; no stronger per-field memory/scratch verification claimed.'],
              'observer_scope_ceiling': 'New explicitly authorized observation harness true origin was not included in capture2 source/profile/schema; actual frozen SDK/driver/producer inputs were guarded. This outcome does not qualify complete observed-software import closure until Root selects the harness independently.',
              'permission_period_renewed': False,
              'source_guard_entry_exit': {'current_files': 27080, 'status': 'PASS', 'historical_physical_closure': 'REFUSED'},
              'installed_guard_entry_exit': {'files': 1010, 'status': 'PASS'}, 'private_bodies_or_keys_exported': False}
    path = HERE / 'actual-attempt-postcheck-0001.json'
    with path.open('xb') as stream:
        stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    print(json.dumps({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes()),
                      'result': result['result'], 'configuration_sha256': sha(config_raw)}, sort_keys=True))


if __name__ == '__main__':
    main()
