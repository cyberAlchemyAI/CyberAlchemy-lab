"""Cold-assess the retained API43 full34 readiness result without rerunning it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001'
PRIOR_SHA = '9eb6094ddb9b643c4d3295ade5f3edf0bcbe8d7e1e488734d53fb5c9a7272003'
RUNNER_SHA = '1402c6cd848b7cf958e5da84b05316c4cee30eb7a39f20ef51f4e7f27739e61e'
DRIVE_SHA = 'eb3c048c7e2ef0bc7749c5ba356c75cc9bdae6da9a58b5d83e40cffccacd7b7a'
API_SOURCE_SHA = '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560'
API_PROFILE_SHA = 'bc660fbd0ac6055dc49b008c9c46c4b09925e1e3cd8795940a0563348b04a2e6'
SDK_SHA = '39f3593f496dea3e86fb6c152a4853568c39b0bc4b46648bd80cadac965e194a'
BRANCH_SHA = '50572a2db800eb605f4b6f7d6704f55a32838850f157b4c2135da0da79a2d9a4'
WRONG_EXPECTATION_SHA = 'bb4eb9cdce92143ef8676e3b284a0bb50195f93b9bab089d0e7b211513341b9c'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(path, expected):
    state = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(state.st_mode) or sha(path.read_bytes()) != expected:
        raise ValueError('selected byte differs')
    return path.read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--control', required=True)
    args = parser.parse_args()
    prior_path = TASK / 'RUN-API43-PRODUCT-0001.json'
    prior = json.loads(exact(prior_path, PRIOR_SHA))
    if not (prior['entrypoint_sha256'] == RUNNER_SHA and prior['status'] == 'REFUSED' and
            prior['error_message_sha256'] == WRONG_EXPECTATION_SHA and
            prior['api_source_sha256'] == API_SOURCE_SHA and prior['api_profile_sha256'] == API_PROFILE_SHA and
            prior['sdk_manifest_sha256'] == SDK_SHA and prior['branch_selection_sha256'] == BRANCH_SHA):
        raise ValueError('initial harness refusal or selected cut differs')
    control = Path(args.control)
    state = control.lstat()
    if (control.parent != Path('/tmp') or not control.name.startswith('cal-T06-api43-product-') or
            control.is_symlink() or not stat.S_ISDIR(state.st_mode) or
            state.st_uid != os.getuid() or stat.S_IMODE(state.st_mode) != 0o700 or
            sha(str(control).encode()) != prior['control_locator_sha256']):
        raise ValueError('private retained control differs')
    drive_path = control / 'drive-stdout.bin'
    drive_state = drive_path.lstat()
    if drive_state.st_uid != os.getuid() or stat.S_IMODE(drive_state.st_mode) != 0o600:
        raise ValueError('private drive receipt mode differs')
    drive = json.loads(exact(drive_path, DRIVE_SHA))
    if not (drive['schema_version'] == 'lab-T06-actual-full34-startup/v1-candidate' and
            drive['status'] == 'PASS' and drive['process_exit_code'] == 0 and
            drive['authority_effect'] == 'none' and drive['actual_owner_outcome'] is None and
            drive['actual_admitted_provisioning'] is False and
            drive['private_credentials_public_exported'] is False and
            drive['whole_API_qualified'] is False and drive['dispatch_operations_executed'] == 0 and
            [row['event'] for row in drive['events']] ==
            ['lab-composite-fresh-session-request/v1-candidate', 'lab-composite-ready/v1-candidate'] and
            drive['events'][1]['catalog_operation_count'] == 34 and
            drive['events'][1]['composition'] == 'Base28+Action3+Governance3'):
        raise ValueError('actual full34 startup result differs')
    selected = [
        (ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001/source-manifest.json', API_SOURCE_SHA),
        (ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001/contract-profile.json', API_PROFILE_SHA),
        (ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api43-t22-0001/revision-0001/source-manifest.json', SDK_SHA),
        (ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api43-t22-0001/revision-0001/driver-selection.json', BRANCH_SHA),
        (TASK / 'run_api43_product.py', RUNNER_SHA),
    ]
    for path, digest in selected:
        exact(path, digest)
    result = {
        'schema_version': 'lab-T06-api43-full34-startup-assessment/v1-candidate',
        'status': 'PASS-bounded-startup', 'initial_harness_receipt_sha256': PRIOR_SHA,
        'initial_harness_refusal': 'incorrect seven-dispatch expectation after selected readiness-only driver',
        'drive_public_receipt_sha256': DRIVE_SHA,
        'api_source_sha256': API_SOURCE_SHA, 'api_profile_sha256': API_PROFILE_SHA,
        'sdk_manifest_sha256': SDK_SHA, 'branch_selection_sha256': BRANCH_SHA,
        'catalog_operation_count': 34, 'composition': 'Base28+Action3+Governance3',
        'dispatch_operations_executed': 0, 'owned_shutdown_exit_code': 0,
        'authority_effect': 'none', 'actual_admitted_provisioning': False,
        'whole_api_qualified': False, 'craft_native_dispatch_integration': False,
        'private_root_locator_sha256': prior['control_locator_sha256'],
        'claim_ceiling': 'Actual installed API43 full34 readiness and clean owned shutdown; no operation dispatch or authority effect.',
    }
    destination = TASK / 'RUN-API43-STARTUP-ASSESS-0001.json'
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'receipt': str(destination)}, sort_keys=True))


if __name__ == '__main__':
    main()
