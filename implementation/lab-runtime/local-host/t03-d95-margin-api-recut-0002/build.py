"""Disjoint d95 API successor repairing live profile-binding correspondence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-margin-0005'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-margin-0006'
OLD_MANIFEST_SHA = '6433787ca0a06e4e708b0fc0f8007ffca264236d748b7f05425eed6e792fd431'
OLD_PROFILE_SHA = '25ee198490d5bf3ad336f0eca494b998e467e058f4e75f7061236fa4b94ef258'
METHODS = (BASE / 'lesson-application-v4-completion-0001/preparation.py',
           BASE / 'lesson-assessment-v2-action-0148/preparation.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def build():
    if row(OLD / 'source-manifest.json')['sha256'] != OLD_MANIFEST_SHA or row(OLD / 'contract-profile.json')['sha256'] != OLD_PROFILE_SHA:
        raise ValueError('predecessor source/profile changed')
    if NEW.exists():
        raise ValueError('successor already exists')
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    own = [r for r in source['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 203 or len(source['files']) != 211:
        raise ValueError('predecessor closure cardinality differs')
    external = {r['path'] for r in source['files'] if not r['path'].startswith(old_prefix)}
    if len(external) != 8 or not {p.relative_to(ROOT).as_posix() for p in METHODS} <= external:
        raise ValueError('selected external method closure differs')
    NEW.mkdir()
    for selected in own:
        path = ROOT / selected['path']
        if row(path) != selected:
            raise ValueError('predecessor own source changed: ' + selected['path'])
        target = NEW / selected['path'][len(old_prefix):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())

    observed = NEW / 'observed_margin.py'
    raw = observed.read_text()
    old = "    need(host.schemas is parent.schemas and host.schemas.profile_binding==config['profile_binding'])"
    new = "    need(host.schemas is parent.schemas and profile_correspondence(host.schemas.profile_binding,config['profile_binding']))"
    if raw.count(old) != 1:
        raise ValueError('live profile comparison site changed')
    raw = raw.replace(old, new)
    anchor = 'def period_correspondence(original,selected):'
    addition = """def profile_correspondence(original,selected):
    closed(original,('ref','sha256'));closed(selected,('path','sha256'))
    need(original['ref']==C.relative(selected['path']) and original['sha256']==selected['sha256'])
    return True

"""
    if raw.count(anchor) != 1:
        raise ValueError('profile helper insertion site changed')
    observed.write_text(raw.replace(anchor, addition + anchor))

    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    profile['files'] = sorted((row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                               for r in profile['files']), key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = ('D95 exact Lesson methods and live observed-margin profile correspondence; '
                                'no Lesson effect, admission or qualification claimed.')
    write(NEW / 'contract-profile.json', profile)
    source['files'] = sorted([row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                              for r in source['files']], key=lambda r: r['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW / 'source-manifest.json', source)
    receipt = {'schema_version': 'lab-T03-d95-margin-live-profile-recut/v1-candidate',
               'predecessor_binding': row(OLD / 'source-manifest.json'),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': row(NEW / 'source-manifest.json')['sha256'],
               'successor_binding': row(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'method_bindings': [row(p) for p in METHODS],
               'own_file_count': 203, 'external_file_count': 8,
               'authority_effect': 'none', 'lesson_applied': False, 'lesson_assessed': False}
    write(NEW / 'rebind-receipt.json', receipt)
    return receipt


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True, indent=2))
