"""One-shot API44 cut selecting the same T22 native family and a T17 driver."""

import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v43-r03-0005-composite-0001'
NEW = BASE / 'api-integration-v44-r03-0005-coverage-0001'
OLD_SOURCE = '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560'
OLD_PROFILE = 'bc660fbd0ac6055dc49b008c9c46c4b09925e1e3cd8795940a0563348b04a2e6'
SDK = BASE / 'composite-operator-v1-current-api44-t17-0001/revision-0001'
BRANCH = (ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/'
          'branch-fixtures-current-api44-t17-0001/revision-0001')
SDK_MANIFEST = '22c70d2ff977741b5a7043fa826dfb754c50542be7b4d1f6477db7dcd3ef9bcd'
BRANCH_SELECTION = 'ea8e887427340cf52974c55b921c9fc1d405973a106e1742f6ea54283c4dd1f9'
OLD_SDK = BASE / 'composite-operator-v1-current-api43-t22-0001/revision-0001'
OLD_BRANCH = (ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/'
              'branch-fixtures-current-api43-t22-0001/revision-0001')
OLD_SDK_MANIFEST = '39f3593f496dea3e86fb6c152a4853568c39b0bc4b46648bd80cadac965e194a'
OLD_BRANCH_SELECTION = '50572a2db800eb605f4b6f7d6704f55a32838850f157b4c2135da0da79a2d9a4'
MEMBERS = '625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732'
CLAIM = ('T22 v4 current R03-0005 + one T17 same-child Base/Action/Governance '
         'coverage candidate; actual dispatch, native contest, Machine channel, '
         'authority effect, and Product qualification remain unproved.')


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def row(path, *, named=None):
    return {'path': relative(named or path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def preflight():
    if sha(OLD / 'source-manifest.json') != OLD_SOURCE or sha(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API43 predecessor differs')
    if sha(OLD / 'integration-members.json') != MEMBERS:
        raise ValueError('unchanged Action/Governance member selection differs')
    if sha(SDK / 'source-manifest.json') != SDK_MANIFEST or sha(BRANCH / 'driver-selection.json') != BRANCH_SELECTION:
        raise ValueError('T17 SDK or branch selection differs')
    if sha(OLD_SDK / 'source-manifest.json') != OLD_SDK_MANIFEST or sha(OLD_BRANCH / 'driver-selection.json') != OLD_BRANCH_SELECTION:
        raise ValueError('frozen API43 SDK or branch selection differs')
    sdk = json.loads((SDK / 'source-manifest.json').read_bytes())
    branch = json.loads((BRANCH / 'driver-selection.json').read_bytes())
    sdk_names = {'bootstrap.py', 'composite.py', 'control.py', 'framing.py', 'launch.py',
                 'composite.config.schema.json'}
    selected_sdk = {relative(SDK / name) for name in sdk_names}
    if (sdk['authority_effect'] != 'none' or
            {item['path'] for item in sdk['files']} != selected_sdk or len(sdk['files']) != 6 or
            any(sha(ROOT / item['path']) != item['sha256'] or
                (ROOT / item['path']).stat().st_size != item['size_bytes'] for item in sdk['files'])):
        raise ValueError('closed T06 SDK executable set differs')
    selected_branch = {relative(BRANCH / name) for name in ('prepare_branches.py', 'drive_operator.py')}
    if (branch['authority_effect'] != 'none' or len(branch['files']) != 7 or
            not selected_branch <= {item['path'] for item in branch['files']} or
            any(sha(ROOT / item['path']) != item['sha256'] for item in branch['files'])):
        raise ValueError('closed T06 branch producer/driver set differs')
    return [SDK / 'source-manifest.json', *(ROOT / item['path'] for item in sdk['files']),
            BRANCH / 'driver-selection.json', BRANCH / 'prepare_branches.py', BRANCH / 'drive_operator.py']


def main():
    additions = preflight()
    if NEW.exists():
        raise ValueError('versioned API44 successor already exists')
    old_manifest = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = relative(OLD) + '/'
    new_prefix = relative(NEW) + '/'
    own = [item for item in old_manifest['files'] if item['path'].startswith(old_prefix)]
    if len(own) != 201 or len(old_manifest['files']) != 207:
        raise ValueError('frozen API43 source inventory differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if actual != {item['path'][len(old_prefix):] for item in own}:
        raise ValueError('actual API43 local inventory differs')
    work = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/working/api44-build-stage'
    if work.exists():
        raise ValueError('disjoint API44 stage already exists')
    work.mkdir(parents=True, mode=0o700)
    try:
        for item in own:
            name = item['path'][len(old_prefix):]
            source = OLD / name
            if sha(source) != item['sha256']:
                raise ValueError('selected API43 source byte differs: ' + name)
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination, follow_symlinks=False)
        new_files = [row(work / item['path'][len(old_prefix):],
                         named=NEW / item['path'][len(old_prefix):])
                     if item['path'].startswith(old_prefix) else item for item in old_manifest['files']]
        old_manifest['files'] = sorted(new_files, key=lambda item: item['path'])
        old_sdk = json.loads((OLD_SDK / 'source-manifest.json').read_bytes())
        old_branch = json.loads((OLD_BRANCH / 'driver-selection.json').read_bytes())
        obsolete = {relative(OLD_SDK / 'source-manifest.json'),
                    *(item['path'] for item in old_sdk['files']),
                    relative(OLD_BRANCH / 'driver-selection.json'),
                    relative(OLD_BRANCH / 'prepare_branches.py'),
                    relative(OLD_BRANCH / 'drive_operator.py')}
        if len(obsolete) != 10 or not obsolete <= {item['path'] for item in old_profile['files']}:
            raise ValueError('exact predecessor T06 profile rows differ')
        new_profile_rows = []
        for item in old_profile['files']:
            if item['path'] in obsolete:
                continue
            if item['path'].startswith(old_prefix):
                name = item['path'][len(old_prefix):]
                new_profile_rows.append(row(work / name, named=NEW / name))
            else:
                new_profile_rows.append(item)
        additions_rows = [row(path) for path in additions]
        names = {item['path'] for item in new_profile_rows}
        if len(additions_rows) != 10 or names & {item['path'] for item in additions_rows}:
            raise ValueError('T17 profile replacement overlaps or is incomplete')
        old_profile['files'] = sorted(new_profile_rows + additions_rows, key=lambda item: item['path'])
        old_profile['integration_members_binding'] = row(work / 'integration-members.json',
                                                         named=NEW / 'integration-members.json')
        old_profile['claim_ceiling'] = CLAIM
        write(work / 'contract-profile.json', old_profile)
        profile_row = row(work / 'contract-profile.json', named=NEW / 'contract-profile.json')
        old_manifest['profile_binding'] = profile_row
        old_manifest['files'] = [profile_row if item['path'] == profile_row['path'] else item
                                 for item in old_manifest['files']]
        old_manifest['predecessor_source_manifest_binding'] = {'path': relative(OLD / 'source-manifest.json'),
                                                                'sha256': OLD_SOURCE}
        old_manifest['claim_ceiling'] = CLAIM
        write(work / 'source-manifest.json', old_manifest)
        receipt = {
            'schema_version': 'lab-API44-T22-T17-coverage-rebind/v1-candidate',
            'predecessor_source_manifest_binding': {'path': relative(OLD / 'source-manifest.json'),
                                                    'sha256': OLD_SOURCE},
            'successor_package': relative(NEW),
            'successor_manifest_sha256': sha(work / 'source-manifest.json'),
            'successor_source_manifest_binding': row(work / 'source-manifest.json',
                                                     named=NEW / 'source-manifest.json'),
            'successor_profile_binding': row(work / 'contract-profile.json',
                                             named=NEW / 'contract-profile.json'),
            't17_sdk_binding': row(SDK / 'source-manifest.json'),
            't17_branch_binding': row(BRANCH / 'driver-selection.json'),
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': CLAIM, 'actual_same_child_operation_pairs_tested': False,
        }
        write(work / 'rebind-receipt.json', receipt)
        os.rename(work, NEW)
    except BaseException:
        shutil.rmtree(work)
        raise
    print(json.dumps({'source_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_files': len(old_manifest['files']),
                      'profile_files': len(old_profile['files']),
                      'T06_new_profile_rows': len(additions_rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
