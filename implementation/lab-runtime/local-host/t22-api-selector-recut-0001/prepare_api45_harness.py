"""Prepare a disjoint captured API45 same-child harness from the API44 candidate."""

import hashlib
import json
from pathlib import Path


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001'
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = {
    'api_source': '70e23e3cb1b3abe32ac59803ed70fc00485cc0f3531c85eb3d5168331cac3d60',
    'api_profile': '28dbdca0d88a7b38e7e384a4f6ef48ecde3476cac8cf006a174197cd668d011f',
    'sdk': '22c70d2ff977741b5a7043fa826dfb754c50542be7b4d1f6477db7dcd3ef9bcd',
    'branch': 'ea8e887427340cf52974c55b921c9fc1d405973a106e1742f6ea54283c4dd1f9',
    'runner': '4ca7d56b4d1675827011c43f5827cf766d8b0a1c4ac892d8014548ccefdac64b',
    'launcher': '778cf9d4a3deee7242721da0c4813f7873a3a73243f3dfe72c6624846da95932',
}
NEW = {
    'api_source': 'd5a57418f84729a085a5a4b335ddcf08ec65de912132a9e2327e66c65dae395d',
    'api_profile': '5635f3d3b5f65852aae01cbd85268802aa42d92b3037fbc70a7694116ed4f205',
    'sdk': '39fd71bade1f31c74150f585bae368334b1cd775c2a6bd401c2ac3852bd79077',
    'branch': 'd8fcbecb0697bf768b9c0a9380e3121496147f9ddd2409b0ae2ffa028de94d15',
    'action': '3b20c6bf6039c5ebf4e2ea056ac5651b465913b13bc133277e039ed60bc37d53',
}


def digest(path):
    if not path.is_file() or path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('harness predecessor origin differs')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(path, expected):
    if digest(path) != expected:
        raise ValueError('harness predecessor bytes differ: ' + str(path))


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def main():
    old_api = INTERFACE / 'api-integration-v44-r03-0005-coverage-0001'
    new_api = INTERFACE / 'api-integration-v45-r03-0005-coverage-0001'
    old_sdk = INTERFACE / 'composite-operator-v1-current-api44-t17-0001/revision-0001'
    new_sdk = INTERFACE / 'composite-operator-v1-current-api45-t17-0001/revision-0001'
    old_branch = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api44-t17-0001/revision-0001'
    new_branch = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0001/revision-0001'
    action = INTERFACE / 'api-action-integration-v8-current-t17-0001/source-manifest.json'
    for path, pin in ((old_api/'source-manifest.json', OLD['api_source']),
                      (old_api/'contract-profile.json', OLD['api_profile']),
                      (old_sdk/'source-manifest.json', OLD['sdk']),
                      (old_branch/'driver-selection.json', OLD['branch']),
                      (TASK/'run_api44_pairs.py', OLD['runner']),
                      (TASK/'launch_api44_pairs.py', OLD['launcher']),
                      (new_api/'source-manifest.json', NEW['api_source']),
                      (new_api/'contract-profile.json', NEW['api_profile']),
                      (new_sdk/'source-manifest.json', NEW['sdk']),
                      (new_branch/'driver-selection.json', NEW['branch']),
                      (action, NEW['action'])):
        exact(path, pin)
    target_runner = TASK / 'run_api45_pairs.py'
    target_launcher = TASK / 'launch_api45_pairs.py'
    selection_path = TASK / 'API45-HARNESS-SELECTION-0001.json'
    if any(p.exists() for p in (target_runner, target_launcher, selection_path)):
        raise ValueError('API45 harness successor already exists')
    runner = (TASK/'run_api44_pairs.py').read_text()
    launcher = (TASK/'launch_api44_pairs.py').read_text()
    for old, new in (
        ('api-integration-v44-r03-0005-coverage-0001', new_api.name),
        ('composite-operator-v1-current-api44-t17-0001', 'composite-operator-v1-current-api45-t17-0001'),
        ('branch-fixtures-current-api44-t17-0001', 'branch-fixtures-current-api45-t17-0001'),
        (OLD['api_source'], NEW['api_source']),
        (OLD['api_profile'], NEW['api_profile']),
        (OLD['sdk'], NEW['sdk']),
        (OLD['branch'], NEW['branch']),
        ('API44', 'API45'), ('api44', 'api45'),
    ):
        runner = runner.replace(old, new)
        launcher = launcher.replace(old, new)
    runner = runner.replace("    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',",
                            "    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',\n    ACTION: '"+NEW['action']+"',")
    runner = runner.replace("PROVISION = ROOT /", "ACTION = ROOT / 'product/lab/release-candidates/v1/interface/api-action-integration-v8-current-t17-0001/source-manifest.json'\nPROVISION = ROOT /")
    launcher = launcher.replace("len(selection['files']) != 8", "len(selection['files']) != 9")
    launcher = launcher.replace("len(selected) != 8", "len(selected) != 9")
    if "ACTION: '"+NEW['action']+"'" not in runner or 'API44' in runner or 'api44' in runner:
        raise ValueError('API45 harness transform differs')
    target_runner.write_text(runner)
    target_launcher.write_text(launcher)
    rows = [binding(path) for path in (
        target_launcher, target_runner, TASK/'build_action_v8.py', TASK/'build_api45_action.py',
        new_api/'source-manifest.json', new_api/'contract-profile.json',
        new_sdk/'source-manifest.json', new_branch/'driver-selection.json', action)]
    selection = {'schema_version': 'lab-T17-api45-harness-selection/v1-candidate',
                 'authority_effect': 'none',
                 'claim_ceiling': 'Execution selection only; no API45 pairs qualified before live receipt.',
                 'files': rows}
    selection_path.write_text(json.dumps(selection, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'runner_sha256': digest(target_runner), 'launcher_sha256': digest(target_launcher),
                      'selection_sha256': digest(selection_path)}, sort_keys=True))


if __name__ == '__main__':
    main()
