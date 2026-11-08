"""Bind a fresh Craft/AlchLang generated-behavior run to the live API40 cut."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t06-api40-rebind-0001'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api40-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api40-0001/revision-0001'
ENTRY = ROOT / 'implementation/lab-runtime/local-host/t06-composite-current-prerequisites-0001/entrypoint.py'
PINS = {
    API / 'source-manifest.json': '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219',
    API / 'contract-profile.json': 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614',
    SDK / 'source-manifest.json': 'f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e',
    BRANCH / 'driver-selection.json': '2709c559fdfe0ffca7bd684b7454903446367731170df63dd8243ca7076f4480',
    TASK / 'RUN-LIVE-EFFECTS-0002.json': '7bac9d32cad2aa5081ede012ac3d70b0f139b7c166482638954c9a83902f7d5b',
    ENTRY: 'a46ae15046c9b47c92de0ceb285d6ad5dfa319a280a575593a362045619c56b3',
    ROOT / 'implementation/lab-runtime/local-host/working/craft-api30-b0-bridge-inactive-0003/FREEZE.json':
        '79260d72298e33e74eb1da862aeb4eab7478f29f2aa4d1867d00060ca2a50582',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact(path, expected, *, external=False):
    observed = path.lstat()
    if (not stat.S_ISREG(observed.st_mode) or path.is_symlink() or
            any(parent.is_symlink() for parent in path.parents) or
            (not external and not path.resolve().is_relative_to(ROOT))):
        raise ValueError('selected origin differs')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('selected byte differs: ' + str(path.relative_to(ROOT)))
    return raw

def selection():
    for path, expected in PINS.items():
        exact(path, expected)
    source = json.loads((API / 'source-manifest.json').read_bytes())
    profile = json.loads((API / 'contract-profile.json').read_bytes())
    if source['profile_binding'] != {'path': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
                                     'sha256': PINS[API / 'contract-profile.json']}:
        raise ValueError('API40 source/profile link differs')
    if len(source['files']) != 207 or len(profile['files']) != 33424:
        raise ValueError('API40 selected closure count differs')
    for rows in (source['files'], profile['files']):
        if len({item['path'] for item in rows}) != len(rows):
            raise ValueError('duplicate selected row')
        for item in rows:
            path = Path(item['path'])
            exact(path if path.is_absolute() else ROOT / path, item['sha256'], external=path.is_absolute())
    live = json.loads((TASK / 'RUN-LIVE-EFFECTS-0002.json').read_bytes())
    if not (live['status'] == 'PASS' and live['process_exit_code'] == 0 and
            live['result']['dispatch_operations_executed'] == 7 and
            live['source_manifest_sha256'] == PINS[API / 'source-manifest.json'] and
            live['profile_sha256'] == PINS[API / 'contract-profile.json'] and
            live['sdk_manifest_sha256'] == PINS[SDK / 'source-manifest.json']):
        raise ValueError('same-cut native composite receipt differs')
    return live

def main():
    started = time.monotonic()
    before = selection()
    spec = importlib.util.spec_from_file_location('t06_api40_pinned_craft_entrypoint', ENTRY)
    entry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entry)
    craft = entry.craft_build()
    if not (craft['status'] == 'technical_candidate_validation_passed' and
            craft['generated_rule_rows'] == craft['generated_query_rows'] == 5 and
            'in-memory technical marker' in craft['generated_operation'] and
            craft['native_eligibility'] is False):
        raise ValueError('generated Craft behavior differs')
    selection()
    result = {
        'schema_version': 'lab-T06-api40-same-cut-craft/v1',
        'status': 'PASS', 'elapsed_seconds': round(time.monotonic() - started, 3),
        'api_source_sha256': PINS[API / 'source-manifest.json'],
        'api_profile_sha256': PINS[API / 'contract-profile.json'],
        'sdk_manifest_sha256': PINS[SDK / 'source-manifest.json'],
        'branch_selection_sha256': PINS[BRANCH / 'driver-selection.json'],
        'live_receipt_sha256': PINS[TASK / 'RUN-LIVE-EFFECTS-0002.json'],
        'live_dispatch_operations_executed': before['result']['dispatch_operations_executed'],
        'craft': craft,
        'craft_bridge_is_inactive_B0_fixture': True,
        'craft_native_dispatch_integration': False,
        'source8_closure': False,
        'whole_api_qualified': False,
        'authority_effect': 'none',
        'claim_ceiling': 'API40 seven-call composite and a separately generated Rule/Query/Operation Craft technical fixture on the same pinned local cut; the inactive B0 Craft marker is not a native API40 operation or Source8 qualification.',
    }
    path = TASK / 'RUN-CRAFT-SAME-CUT-0001.json'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
