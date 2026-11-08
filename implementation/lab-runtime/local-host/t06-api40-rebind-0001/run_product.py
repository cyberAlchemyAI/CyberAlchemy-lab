"""Run the installed API40 composite and pinned Craft behavior as one local product."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t06-api40-rebind-0001'
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-integration-v40-current-t06-0001'
SDK = INTERFACE / 'composite-operator-v1-current-api40-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api40-0001/revision-0001'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
ENTRY = ROOT / 'implementation/lab-runtime/local-host/t06-composite-current-prerequisites-0001/entrypoint.py'
PROVISION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json'
PINS = {
    API / 'source-manifest.json': '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219',
    API / 'contract-profile.json': 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614',
    API / 'integration-members.json': '625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732',
    SDK / 'source-manifest.json': 'f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e',
    BRANCH / 'driver-selection.json': '2709c559fdfe0ffca7bd684b7454903446367731170df63dd8243ca7076f4480',
    TASK / 'drive_effects_0002.py': 'ced8b82be6a6ca77562b1d900b7dca122e3e1ecefbd06e428a5e4c0bd50b7cec',
    TASK / 'run_craft_same_cut.py': 'dfd5f66fc95b21914e0f6de4a32d867c7fb63688e7a8394da88edb945ad5e95e',
    TASK / 'RUN-LIVE-EFFECTS-0002.json': '7bac9d32cad2aa5081ede012ac3d70b0f139b7c166482638954c9a83902f7d5b',
    TASK / 'RUN-CRAFT-SAME-CUT-0001.json': '8b46747e098f11016cb92151e3fc550feabc82bd12bc72cf8d2e692d42fbe9a9',
    ENTRY: 'a46ae15046c9b47c92de0ceb285d6ad5dfa319a280a575593a362045619c56b3',
    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',
    ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json':
        '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact(path, expected, *, external=False):
    state = path.lstat()
    if (not stat.S_ISREG(state.st_mode) or path.is_symlink() or
            any(parent.is_symlink() for parent in path.parents) or
            (not external and not path.resolve().is_relative_to(ROOT))):
        raise ValueError('selected origin differs')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('selected byte differs: ' + str(path))
    return raw

def verify_cut():
    for path, expected in PINS.items():
        exact(path, expected)
    source = json.loads((API / 'source-manifest.json').read_bytes())
    profile = json.loads((API / 'contract-profile.json').read_bytes())
    if source['profile_binding'] != {'path': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
                                     'sha256': PINS[API / 'contract-profile.json']}:
        raise ValueError('API40 profile binding differs')
    for rows, count in ((source['files'], 207), (profile['files'], 33424)):
        if len(rows) != count or len({item['path'] for item in rows}) != count:
            raise ValueError('API40 closed selection inventory differs')
        for item in rows:
            name = Path(item['path'])
            exact(name if name.is_absolute() else ROOT / name, item['sha256'], external=name.is_absolute())
    prior_live = json.loads((TASK / 'RUN-LIVE-EFFECTS-0002.json').read_bytes())
    prior_craft = json.loads((TASK / 'RUN-CRAFT-SAME-CUT-0001.json').read_bytes())
    if (prior_live['status'] != 'PASS' or prior_live['result']['dispatch_operations_executed'] != 7 or
            prior_craft['status'] != 'PASS' or prior_craft['live_receipt_sha256'] != PINS[TASK / 'RUN-LIVE-EFFECTS-0002.json'] or
            prior_craft['api_source_sha256'] != PINS[API / 'source-manifest.json']):
        raise ValueError('reviewed predecessor run receipt differs')
    return source, profile

def private_file(control, name, raw):
    path = control / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return path

def child(argv, control, name, timeout, env):
    started = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, env=env)
    private_file(control, name + '-stdout.bin', result.stdout)
    private_file(control, name + '-stderr.bin', result.stderr)
    return result, round(time.monotonic() - started, 3)

def run_product(control):
    loader = INSTALL / 'lib/abi/ld-linux-x86-64.so.2'
    installed = [str(loader), '--inhibit-cache', '--library-path', str(INSTALL / 'lib/abi'),
                 str(INSTALL / 'bin/python'), '-X', 'utf8', '-B', '-S']
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONNOUSERSITE': '1',
           'PYTHONDONTWRITEBYTECODE': '1',
           'PYTHONPATH': str(ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay') + ':' + str(INSTALL / 'deps')}
    selection_path = BRANCH / 'driver-selection.json'
    stage, stage_seconds = child([*installed, str(BRANCH / 'prepare_branches.py'), 'stage-keys',
                                  '--selection', str(selection_path), '--selection-sha256', PINS[selection_path]],
                                 control, 'stage', 120, env)
    if stage.returncode != 0:
        raise ValueError('fresh private key staging refused')
    private_root = Path(stage.stdout.decode().strip())
    identity = private_root.lstat()
    if (private_root.parent != Path('/tmp') or not private_root.name.startswith('cal-T06-branch-fixtures-') or
            not stat.S_ISDIR(identity.st_mode) or identity.st_uid != os.getuid() or
            stat.S_IMODE(identity.st_mode) != 0o700):
        raise ValueError('fresh private root differs')
    private_file(control, 'root.txt', (str(private_root) + '\n').encode())
    lock = control / 'lease.lock'
    prepare, prepare_seconds = child([*installed, str(BRANCH / 'prepare_branches.py'), 'prepare',
                                      '--selection', str(selection_path), '--selection-sha256', PINS[selection_path],
                                      '--root', str(private_root), '--source-sha256', PINS[API / 'source-manifest.json'],
                                      '--profile-sha256', PINS[API / 'contract-profile.json'], '--lease-lock', str(lock)],
                                     control, 'prepare', 900, env)
    if prepare.returncode != 0:
        raise ValueError('fresh three-branch preparation refused')
    selected = private_root / 'private-branch-selection.json'
    selected_state = selected.lstat()
    if not stat.S_ISREG(selected_state.st_mode) or selected_state.st_uid != os.getuid() or stat.S_IMODE(selected_state.st_mode) != 0o600:
        raise ValueError('private branch selection changed')
    selected_sha = sha(selected.read_bytes())
    record = json.loads(selected.read_bytes())
    action = Path(record['branches']['actions']['workspace_root'])
    grant = json.loads((action / 'grant.json').read_bytes())
    if grant['expires_at'] - time.time() < 300:
        raise ValueError('fresh Action lease too short')
    driver = TASK / 'drive_effects_0002.py'
    driver_args = [sys.executable, '-B', str(driver), '--branch-selection', str(selected),
                   '--branch-selection-sha256', selected_sha, '--sdk-directory', str(SDK),
                   '--sdk-source-sha256', PINS[SDK / 'source-manifest.json'],
                   '--provisioning-path', PROVISION.relative_to(ROOT).as_posix(),
                   '--provisioning-sha256', PINS[PROVISION], '--lease-lock', str(lock)]
    live, live_seconds = child(driver_args, control, 'drive', 900,
                               {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    if live.returncode != 0:
        raise ValueError('API40 seven-call composite refused')
    value = json.loads(live.stdout)
    events = value.get('events', [])
    observations = value.get('observations', [])
    if not (value.get('status') == 'PASS' and value.get('process_exit_code') == 0 and
            value.get('dispatch_operations_executed') == 7 and len(observations) == 7 and
            [event.get('event') for event in events] ==
            ['lab-composite-fresh-session-request/v1-candidate', 'lab-composite-ready/v1-candidate',
             'base-positive-reads', 'action-positive-inspection-wrong-scope', 'governance-positive-and-inspection'] and
            events[1]['catalog_operation_count'] == 34 and
            [(row['branch'], row['operation'], row['reply_kind']) for row in observations] ==
            [('base', 'lab.status', 'result'), ('base', 'catalog.get', 'result'),
             ('actions', 'action.dispatch', 'result'), ('actions', 'operation.inspect', 'result'),
             ('actions', 'action.dispatch', 'error'), ('governance', 'capability.adoption.prepare', 'result'),
             ('governance', 'operation.inspect', 'result')] and
            observations[2]['posture'] == observations[3]['posture'] == observations[6]['posture'] == 'completed' and
            observations[2]['counter_after'] == observations[3]['counter_after'] == observations[4]['counter_after'] == 1 and
            observations[4]['code'] == 'unauthorized' and observations[5]['target_count'] == 1):
        raise ValueError('seven-call public result differs')
    verify_cut()
    spec = importlib.util.spec_from_file_location('t06_api40_product_craft', ENTRY)
    entry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entry)
    old_consumer = os.environ.pop('ALCHLANG_CONSUMER', None)
    try:
        craft = entry.craft_build()
    finally:
        if old_consumer is not None:
            os.environ['ALCHLANG_CONSUMER'] = old_consumer
    if not (craft['status'] == 'technical_candidate_validation_passed' and
            craft['generated_rule_rows'] == craft['generated_query_rows'] == 5 and
            'in-memory technical marker' in craft['generated_operation'] and
            craft['native_eligibility'] is False):
        raise ValueError('same-cut Craft generated behavior refused')
    verify_cut()
    return {
        'stage_seconds': stage_seconds, 'prepare_seconds': prepare_seconds, 'live_seconds': live_seconds,
        'private_root_locator_sha256': sha(str(private_root).encode()),
        'private_branch_selection_sha256': selected_sha,
        'private_logs_sha256': {name: sha((control / name).read_bytes()) for name in
                                ('stage-stdout.bin', 'stage-stderr.bin', 'prepare-stdout.bin',
                                 'prepare-stderr.bin', 'drive-stdout.bin', 'drive-stderr.bin')},
        'live_result': value,
        'craft': craft,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    receipt = TASK / args.receipt
    if (receipt.parent != TASK or not receipt.name.startswith('RUN-PRODUCT-') or
            receipt.suffix != '.json' or receipt.exists()):
        raise ValueError('new task-local product receipt required')
    os.umask(0o077)
    own = TASK / 'run_product.py'
    own_sha = sha(exact(own, sha(own.read_bytes())))
    verify_cut()
    control = Path(tempfile.mkdtemp(prefix='cal-T06-api40-product-', dir='/tmp'))
    if stat.S_IMODE(control.stat().st_mode) != 0o700:
        raise ValueError('private control mode differs')
    started = time.monotonic()
    result = {
        'schema_version': 'lab-T06-api40-local-product/v1',
        'entrypoint_sha256': own_sha,
        'api_source_sha256': PINS[API / 'source-manifest.json'],
        'api_profile_sha256': PINS[API / 'contract-profile.json'],
        'sdk_manifest_sha256': PINS[SDK / 'source-manifest.json'],
        'branch_selection_sha256': PINS[BRANCH / 'driver-selection.json'],
        'seven_call_driver_sha256': PINS[TASK / 'drive_effects_0002.py'],
        'craft_entrypoint_sha256': PINS[ENTRY],
        'craft_harness_sha256': PINS[TASK / 'run_craft_same_cut.py'],
        'prior_live_receipt_sha256': PINS[TASK / 'RUN-LIVE-EFFECTS-0002.json'],
        'prior_craft_receipt_sha256': PINS[TASK / 'RUN-CRAFT-SAME-CUT-0001.json'],
        'control_locator_sha256': sha(str(control).encode()),
        'authority_effect': 'none', 'status': 'REFUSED',
        'source8_closure': False, 'whole_api_qualified': False,
        'craft_native_dispatch_integration': False,
    }
    try:
        result.update(run_product(control))
        result['status'] = 'PASS'
    except Exception as error:
        result['error_class'] = type(error).__name__
        result['error_message_sha256'] = sha(str(error).encode())
    finally:
        verify_cut()
        if sha(own.read_bytes()) != own_sha:
            raise ValueError('product entrypoint changed during run')
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['claim_ceiling'] = ('One runnable local entrypoint completed fresh API40 Base/Action/Governance seven-call dispatch and '
                                   'separate pinned Craft Rule/Query/Operation technical behavior; inactive B0 Craft is not '
                                   'a native API40 operation, Source8 closure or qualification of all 34 operations.')
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
            stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
