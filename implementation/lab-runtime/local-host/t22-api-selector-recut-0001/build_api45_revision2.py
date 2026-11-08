"""Select an Action v8 revision-2 and a T17 composite in a disjoint API45 revision-2 cut."""

import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = INTERFACE / 'api-integration-v45-r03-0005-coverage-0001'
NEW = INTERFACE / 'api-integration-v45-r03-0005-coverage-0002'
OLD_SOURCE = 'd5a57418f84729a085a5a4b335ddcf08ec65de912132a9e2327e66c65dae395d'
OLD_PROFILE = '5635f3d3b5f65852aae01cbd85268802aa42d92b3037fbc70a7694116ed4f205'
ACTION_OLD = INTERFACE / 'api-action-integration-v8-current-t17-0001'
ACTION_NEW = INTERFACE / 'api-action-integration-v8-current-t17-0002'
ACTION_OLD_SOURCE = '3b20c6bf6039c5ebf4e2ea056ac5651b465913b13bc133277e039ed60bc37d53'
ACTION_NEW_SOURCE = 'a0a4e8c21d8db94eac092d93bb06e6edabd1b564692df6cb9a9c97b2041e47cf'
ACTION_PROFILE = 'b3767b2b1ececc73ce24ea7d55924956feab8a5f3b563c3359391122a95b3576'
SDK_OLD = INTERFACE / 'composite-operator-v1-current-api45-t17-0001/revision-0001'
SDK_NEW = INTERFACE / 'composite-operator-v1-current-api45-t17-0002/revision-0001'
SDK_OLD_SHA = '39fd71bade1f31c74150f585bae368334b1cd775c2a6bd401c2ac3852bd79077'
BRANCH_OLD = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0001/revision-0001'
BRANCH_NEW = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0002/revision-0001'
BRANCH_OLD_SHA = 'd8fcbecb0697bf768b9c0a9380e3121496147f9ddd2409b0ae2ffa028de94d15'
CLAIM = ('Current T22 R03-0005 and Action v8/API45 T17 same-child fixture; '
         'actual operation pairs, contest, Lesson, authority effect and whole Product remain unproved.')


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected origin differs: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return path.relative_to(ROOT).as_posix()


def row(path, named=None):
    return {'path': ref(named or path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def replace_once(raw, old, new):
    if old not in raw:
        raise ValueError('selected predecessor token missing: ' + old)
    return raw.replace(old, new)


def check_predecessors():
    expected = ((OLD / 'source-manifest.json', OLD_SOURCE),
                (OLD / 'contract-profile.json', OLD_PROFILE),
                (ACTION_OLD / 'source-manifest.json', ACTION_OLD_SOURCE),
                (ACTION_NEW / 'source-manifest.json', ACTION_NEW_SOURCE),
                (ACTION_NEW / 'contract-profile.json', ACTION_PROFILE),
                (SDK_OLD / 'source-manifest.json', SDK_OLD_SHA),
                (BRANCH_OLD / 'driver-selection.json', BRANCH_OLD_SHA))
    if any(sha(path) != digest for path, digest in expected):
        raise ValueError('frozen API45 predecessor or Action v8 differs')
    if any(path.exists() for path in (SDK_NEW, BRANCH_NEW, NEW)):
        raise ValueError('API45 successor destination already exists')


def build_sdk():
    SDK_NEW.parent.mkdir(parents=True, exist_ok=False)
    SDK_NEW.mkdir(mode=0o700)
    selected = json.loads((SDK_OLD / 'source-manifest.json').read_bytes())
    names = {'bootstrap.py', 'composite.py', 'control.py', 'framing.py', 'launch.py',
             'composite.config.schema.json'}
    if len(selected['files']) != 6 or {Path(r['path']).name for r in selected['files']} != names:
        raise ValueError('old SDK executable closure differs')
    for item in selected['files']:
        name = Path(item['path']).name
        src = SDK_OLD / name
        if sha(src) != item['sha256']:
            raise ValueError('old SDK row changed')
        raw = src.read_bytes()
        if name in ('bootstrap.py', 'composite.py'):
            text = raw.decode()
            text = text.replace('api-integration-v45-r03-0005-coverage-0001', NEW.name)
            text = text.replace('current-api45-t17-0001', 'current-api45-t17-0002')
            text = text.replace('API44', 'API45').replace('api44', 'api45')
            raw = text.encode()
        (SDK_NEW / name).write_bytes(raw)
    selected['files'] = sorted([
        {'path': ref(SDK_NEW / name), 'sha256': sha(SDK_NEW / name),
         'size_bytes': (SDK_NEW / name).stat().st_size} for name in names
    ], key=lambda r: r['path'])
    selected['historical_sdk_binding'] = row(SDK_OLD / 'source-manifest.json')
    selected['schema_version'] = 'lab-T06-current-api45-t17-sdk-source/v1-candidate'
    write(SDK_NEW / 'source-manifest.json', selected)


def build_branch():
    BRANCH_NEW.parent.mkdir(parents=True, exist_ok=False)
    BRANCH_NEW.mkdir(mode=0o700)
    selected = json.loads((BRANCH_OLD / 'driver-selection.json').read_bytes())
    old_prefix = ref(BRANCH_OLD) + '/'
    new_prefix = ref(BRANCH_NEW) + '/'
    for name in ('prepare_branches.py', 'drive_operator.py'):
        src = BRANCH_OLD / name
        old_row = next((r for r in selected['files'] if r['path'] == old_prefix + name), None)
        if old_row is None or sha(src) != old_row['sha256']:
            raise ValueError('old branch code row differs')
        text = src.read_text()
        text = text.replace('api-integration-v45-r03-0005-coverage-0001', NEW.name)
        text = text.replace('current-api45-t17-0001', 'current-api45-t17-0002')
        text = text.replace('api-action-integration-v8-current-t17-0001', ACTION_NEW.name)
        text = text.replace('API44', 'API45').replace('api44', 'api45')
        (BRANCH_NEW / name).write_text(text)
    selected['files'] = sorted([
        row(BRANCH_NEW / item['path'][len(old_prefix):]) if item['path'].startswith(old_prefix)
        else item for item in selected['files']
    ], key=lambda r: r['path'])
    selected['predecessor_binding'] = row(BRANCH_OLD / 'driver-selection.json')
    selected['schema_version'] = 'lab-T06-current-api45-t17-branch-driver-selection/v1-candidate'
    write(BRANCH_NEW / 'driver-selection.json', selected)


def build_api():
    NEW.mkdir(mode=0o700)
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    prefix_old = ref(OLD) + '/'
    prefix_new = ref(NEW) + '/'
    own = [r for r in source['files'] if r['path'].startswith(prefix_old)]
    if len(own) != 201 or len(source['files']) != 207 or len(profile['files']) != 33434:
        raise ValueError('API44 selected inventory differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if actual != {r['path'][len(prefix_old):] for r in own}:
        raise ValueError('API44 own source closure differs')
    for item in own:
        name = item['path'][len(prefix_old):]
        src = OLD / name
        if sha(src) != item['sha256']:
            raise ValueError('API44 selected own source changed')
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target, follow_symlinks=False)
    members = json.loads((NEW / 'integration-members.json').read_bytes())
    action = members['members']['actions']
    if (action['directory'] != ACTION_OLD.name or action['source_sha256'] != ACTION_OLD_SOURCE
            or action['profile_sha256'] != ACTION_PROFILE):
        raise ValueError('API44 Action member premise differs')
    action['directory'] = ACTION_NEW.name
    action['source_sha256'] = ACTION_NEW_SOURCE
    write(NEW / 'integration-members.json', members)
    source['files'] = sorted([
        row(NEW / item['path'][len(prefix_old):]) if item['path'].startswith(prefix_old)
        else item for item in source['files']
    ], key=lambda item: item['path'])
    obsolete = {ref(SDK_OLD / 'source-manifest.json'),
                *(ref(SDK_OLD / Path(r['path']).name) for r in json.loads((SDK_OLD / 'source-manifest.json').read_bytes())['files']),
                ref(BRANCH_OLD / 'driver-selection.json'), ref(BRANCH_OLD / 'prepare_branches.py'),
                ref(BRANCH_OLD / 'drive_operator.py')}
    if len(obsolete) != 10 or not obsolete <= {r['path'] for r in profile['files']}:
        raise ValueError('old T06 profile selection differs')
    action_old_prefix = ref(ACTION_OLD) + '/'
    action_old_rows = [r for r in profile['files'] if r['path'].startswith(action_old_prefix)]
    if len(action_old_rows) != 17:
        raise ValueError('old Action profile closure differs')
    new_rows = []
    for item in profile['files']:
        path = item['path']
        if path in obsolete:
            continue
        if path.startswith(prefix_old):
            new_rows.append(row(NEW / path[len(prefix_old):]))
        elif path.startswith(action_old_prefix):
            new_rows.append(row(ACTION_NEW / path[len(action_old_prefix):]))
        else:
            new_rows.append(item)
    additions = [SDK_NEW / 'source-manifest.json',
                 *(SDK_NEW / Path(r['path']).name for r in json.loads((SDK_NEW / 'source-manifest.json').read_bytes())['files']),
                 BRANCH_NEW / 'driver-selection.json', BRANCH_NEW / 'prepare_branches.py', BRANCH_NEW / 'drive_operator.py']
    if len(additions) != 10:
        raise ValueError('new SDK/branch closure differs')
    profile['files'] = sorted(new_rows + [row(path) for path in additions], key=lambda r: r['path'])
    if len(profile['files']) != 33434 or len({r['path'] for r in profile['files']}) != 33434:
        raise ValueError('API45 profile path set differs')
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    write(NEW / 'contract-profile.json', profile)
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['files'] = [row(NEW / 'contract-profile.json') if r['path'] == ref(NEW / 'contract-profile.json')
                       else r for r in source['files']]
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    source['claim_ceiling'] = CLAIM
    write(NEW / 'source-manifest.json', source)
    # protocol.Schemas.guard requires this local binding even though the
    # selected source manifest deliberately excludes its own receipt.
    local_receipt = {
        'schema_version': 'lab-API45-T17-revision2-rebind/v1-candidate',
        'successor_package': ref(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': row(NEW / 'contract-profile.json'),
        'predecessor_source_manifest_binding': row(OLD / 'source-manifest.json'),
        'action_successor_binding': row(ACTION_NEW / 'source-manifest.json'),
        't17_sdk_binding': row(SDK_NEW / 'source-manifest.json'),
        't17_branch_binding': row(BRANCH_NEW / 'driver-selection.json'),
        'authority_effect': 'none',
        'actual_owner_outcome': None,
        'actual_same_child_operation_pairs_tested': False,
        'claim_ceiling': CLAIM,
    }
    write(NEW / 'rebind-receipt.json', local_receipt)
    receipt = {'schema_version': 'lab-API45-Action-v8-T17-revision2-rebind/v1-candidate',
               'predecessor_source_manifest_binding': row(OLD / 'source-manifest.json'),
               'action_successor_binding': row(ACTION_NEW / 'source-manifest.json'),
               'sdk_successor_binding': row(SDK_NEW / 'source-manifest.json'),
               'branch_successor_binding': row(BRANCH_NEW / 'driver-selection.json'),
               'api_source_binding': row(NEW / 'source-manifest.json'),
               'api_profile_binding': row(NEW / 'contract-profile.json'),
               'api_local_receipt_binding': row(NEW / 'rebind-receipt.json'),
               'authority_effect': 'none', 'actual_same_child_operation_pairs_tested': False}
    write(ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/API45R2-REBIND-RECEIPT.json', receipt)
    return receipt


def main():
    check_predecessors()
    build_sdk()
    build_branch()
    receipt = build_api()
    print(json.dumps({'api_source_sha256': receipt['api_source_binding']['sha256'],
                      'api_profile_sha256': receipt['api_profile_binding']['sha256'],
                      'action_source_sha256': ACTION_NEW_SOURCE,
                      'sdk_sha256': receipt['sdk_successor_binding']['sha256'],
                      'branch_sha256': receipt['branch_successor_binding']['sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
