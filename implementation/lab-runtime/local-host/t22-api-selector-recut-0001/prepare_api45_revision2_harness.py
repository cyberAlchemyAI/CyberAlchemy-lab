"""Pin a captured live harness for the disjoint API45 revision-2 cut."""

import hashlib
import json
from pathlib import Path
import re


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001'
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD_API = INTERFACE / 'api-integration-v45-r03-0005-coverage-0001'
NEW_API = INTERFACE / 'api-integration-v45-r03-0005-coverage-0002'
NEW_ACTION = INTERFACE / 'api-action-integration-v8-current-t17-0002'
NEW_SDK = INTERFACE / 'composite-operator-v1-current-api45-t17-0002/revision-0001'
NEW_BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0002/revision-0001'
SOURCE_SHA = '3f21cda1927c7479efb77059255118d8a171a2f4ee8e1c8086b0ddbb1268faeb'
PROFILE_SHA = '05edcf558bd7bc3974ed5d7da76367b32e8ebc8f45636a65734700800b9c86aa'
RECEIPT_SHA = '26bcefb0d678893b514913d9151ebfbc59ef141259bca253e03660a6fe7f10b4'
ACTION_SHA = 'a0a4e8c21d8db94eac092d93bb06e6edabd1b564692df6cb9a9c97b2041e47cf'
SDK_SHA = 'b8874f5998584d686e02187a2c3c66241c5c03da97f5c0064758fee281dd7db5'
BRANCH_SHA = '52177c62ed5ce303403399e23f26bb8000074068124a33c206f798b02e53f94e'
OLD_RUNNER_SHA = '8cbc98a7bb80aa37e1cbb0ece48eb139a49a5b9c3e10a0c3dc44b88c50ef56a0'
OLD_LAUNCHER_SHA = '035a9f8cf44c43d1e2b36fedba332eee94777863d7794b48392fc848f566c346'


def sha(path):
    if not path.is_file() or path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected harness origin differs')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def replace_tokens(raw, mapping):
    return re.sub('|'.join(re.escape(item) for item in sorted(mapping, key=len, reverse=True)),
                  lambda match: mapping[match.group()], raw)


def main():
    selected = (
        (TASK / 'run_api45_pairs.py', OLD_RUNNER_SHA),
        (TASK / 'launch_api45_pairs.py', OLD_LAUNCHER_SHA),
        (NEW_API / 'source-manifest.json', SOURCE_SHA),
        (NEW_API / 'contract-profile.json', PROFILE_SHA),
        (NEW_API / 'rebind-receipt.json', RECEIPT_SHA),
        (NEW_ACTION / 'source-manifest.json', ACTION_SHA),
        (NEW_SDK / 'source-manifest.json', SDK_SHA),
        (NEW_BRANCH / 'driver-selection.json', BRANCH_SHA),
    )
    if any(sha(path) != digest for path, digest in selected):
        raise ValueError('API45 revision-2 harness premise differs')
    runner = TASK / 'run_api45_revision2_pairs.py'
    launcher = TASK / 'launch_api45_revision2_pairs.py'
    selection_path = TASK / 'API45R2-HARNESS-SELECTION-0001.json'
    if any(path.exists() for path in (runner, launcher, selection_path)):
        raise ValueError('API45 revision-2 harness already exists')
    map_names = {
        OLD_API.name: NEW_API.name,
        'api-action-integration-v8-current-t17-0001': NEW_ACTION.name,
        'composite-operator-v1-current-api45-t17-0001': 'composite-operator-v1-current-api45-t17-0002',
        'branch-fixtures-current-api45-t17-0001': 'branch-fixtures-current-api45-t17-0002',
        'd5a57418f84729a085a5a4b335ddcf08ec65de912132a9e2327e66c65dae395d': SOURCE_SHA,
        '5635f3d3b5f65852aae01cbd85268802aa42d92b3037fbc70a7694116ed4f205': PROFILE_SHA,
        '3b20c6bf6039c5ebf4e2ea056ac5651b465913b13bc133277e039ed60bc37d53': ACTION_SHA,
        '39fd71bade1f31c74150f585bae368334b1cd775c2a6bd401c2ac3852bd79077': SDK_SHA,
        'd8fcbecb0697bf768b9c0a9380e3121496147f9ddd2409b0ae2ffa028de94d15': BRANCH_SHA,
        'run_api45_pairs.py': runner.name,
        'launch_api45_pairs.py': launcher.name,
        'API45-HARNESS-SELECTION-0001.json': selection_path.name,
        'RUN-API45-PAIRS-0001.json': 'RUN-API45R2-PAIRS-0001.json',
        'cal-T17-api45-pairs-': 'cal-T17-api45r2-pairs-',
        'lab-T17-api45-harness-selection/v1-candidate': 'lab-T17-api45-revision2-harness-selection/v1-candidate',
        'lab-T17-api45-same-child-coverage/v1-candidate': 'lab-T17-api45-revision2-same-child-coverage/v1-candidate',
    }
    runner_raw = replace_tokens((TASK / 'run_api45_pairs.py').read_text(), map_names)
    launcher_raw = replace_tokens((TASK / 'launch_api45_pairs.py').read_text(), map_names)
    runner_raw = runner_raw.replace("ACTION = ROOT /", "LOCAL_RECEIPT = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v45-r03-0005-coverage-0002/rebind-receipt.json'\nACTION = ROOT /")
    runner_raw = runner_raw.replace(f"    ACTION: '{ACTION_SHA}',",
                                    f"    ACTION: '{ACTION_SHA}',\n    LOCAL_RECEIPT: '{RECEIPT_SHA}',")
    launcher_raw = launcher_raw.replace("len(selection['files']) != 9", "len(selection['files']) != 10")
    launcher_raw = launcher_raw.replace("len(selected) != 9", "len(selected) != 10")
    if (f"LOCAL_RECEIPT: '{RECEIPT_SHA}'" not in runner_raw or
            "len(selection['files']) != 10" not in launcher_raw or
            'api-integration-v45-r03-0005-coverage-0001' in runner_raw + launcher_raw):
        raise ValueError('API45 revision-2 harness transform differs')
    runner.write_text(runner_raw)
    launcher.write_text(launcher_raw)
    rows = [binding(path) for path in (
        launcher, runner, TASK / 'build_action_v8_revision2.py', TASK / 'build_api45_revision2.py',
        NEW_API / 'source-manifest.json', NEW_API / 'contract-profile.json',
        NEW_API / 'rebind-receipt.json', NEW_ACTION / 'source-manifest.json',
        NEW_SDK / 'source-manifest.json', NEW_BRANCH / 'driver-selection.json')]
    selection = {'schema_version': 'lab-T17-api45-revision2-harness-selection/v1-candidate',
                 'authority_effect': 'none',
                 'claim_ceiling': 'Execution selection only; no revision-2 API45 pairs qualified before live receipt.',
                 'files': rows}
    selection_path.write_text(json.dumps(selection, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'runner_sha256': sha(runner), 'launcher_sha256': sha(launcher),
                      'selection_sha256': sha(selection_path)}, sort_keys=True))


if __name__ == '__main__':
    main()
