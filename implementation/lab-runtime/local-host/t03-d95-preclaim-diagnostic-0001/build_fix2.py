"""Disjoint successor repairing diagnostic try/except syntax."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0002'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
OLD_MANIFEST_SHA = '870444ae9fdf4f573c253d71b9500fb0e1ccefe7fe880dcdf7aad07d92147e28'
OLD_PROFILE_SHA = 'a5170a844693c5ca8ffa42c3eac913ebd946ec96bc71e11c7fd56754721f6d7a'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def replace_once(raw, old, new):
    if raw.count(old) != 1:
        raise ValueError('diagnostic repair anchor differs: ' + repr(old[:90]))
    return raw.replace(old, new)


def build():
    if row(OLD / 'source-manifest.json')['sha256'] != OLD_MANIFEST_SHA or row(OLD / 'contract-profile.json')['sha256'] != OLD_PROFILE_SHA:
        raise ValueError('diagnostic predecessor changed')
    if NEW.exists():
        raise ValueError('successor already exists')
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    own = [r for r in source['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 203 or len(source['files']) != 211:
        raise ValueError('predecessor selected closure differs')
    NEW.mkdir()
    for selected in own:
        path = ROOT / selected['path']
        if row(path) != selected:
            raise ValueError('predecessor own byte changed: ' + selected['path'])
        target = NEW / selected['path'][len(old_prefix):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    service = NEW / 'service.py'
    raw = service.read_text()
    raw = replace_once(raw,
        "        try:context=self.channel.guard()\n"
        "        diagnostic_deadline=context['limits']['deadline']\n"
        "        except Exception:\n",
        "        try:context=self.channel.guard()\n"
        "        except Exception:\n")
    raw = replace_once(raw,
        "            return transport('unauthenticated-channel',raw)\n"
        "        if len(raw)>context['limits']['max_request_bytes']:return transport('input-too-large',raw)\n",
        "            return transport('unauthenticated-channel',raw)\n"
        "        diagnostic_deadline=context['limits']['deadline']\n"
        "        if len(raw)>context['limits']['max_request_bytes']:return transport('input-too-large',raw)\n")
    compile(raw,str(service),'exec')
    service.write_text(raw)
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    profile['files'] = sorted((row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                               for r in profile['files']), key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = 'T03 bounded preclaim stage diagnosis only; no Lesson effect established.'
    write(NEW / 'contract-profile.json', profile)
    source['files'] = sorted((row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                              for r in source['files']), key=lambda r: r['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW / 'source-manifest.json', source)
    receipt = {'schema_version':'lab-T03-d95-preclaim-diagnostic-syntax-repair/v1-candidate',
               'predecessor_binding':row(OLD / 'source-manifest.json'),
               'successor_package':NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256':row(NEW / 'source-manifest.json')['sha256'],
               'successor_binding':row(NEW / 'source-manifest.json'),
               'successor_profile_binding':row(NEW / 'contract-profile.json'),
               'service_binding':row(service),'own_file_count':203,'external_file_count':8,
               'authority_effect':'none','lesson_applied':False,'lesson_assessed':False}
    write(NEW / 'rebind-receipt.json', receipt)
    return receipt


if __name__ == '__main__':
    print(json.dumps(build(),sort_keys=True,indent=2))
