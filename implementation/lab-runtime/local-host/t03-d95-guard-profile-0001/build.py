"""Disjoint exact-byte successor measuring current LessonHost guard costs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-guard-profile-0001'
OLD_MANIFEST_SHA = '1b83e97f5cae120473ccc61d151d38bc0d99d2f1bb8a39f8a30ef8ceedb8184d'
OLD_PROFILE_SHA = '3a07464283b6f09aee1bb68ccaa6aa8022666f9ab23871da536947091bbc6413'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def replace_once(raw,old,new):
    if raw.count(old)!=1:
        raise ValueError('selected host profile anchor differs: '+repr(old[:90]))
    return raw.replace(old,new)


def profile_host(raw):
    raw=replace_once(raw,'import sys\n','import sys\nimport json\nimport time\n')
    raw=replace_once(raw,'\n\nclass LessonHost:', '''\n\ndef _t03_profile(stage,began,ordinal=None):
    """Best-effort timings only; never changes a guard result or private output."""
    try:
        ended=time.monotonic_ns()
        sys.stderr.write(json.dumps({'kind':'T03-guard-profile','stage':stage,
            'ordinal':ordinal,'elapsed_ns':ended-began,'ended_monotonic_ns':ended},sort_keys=True)+'\\n')
        sys.stderr.flush()
    except Exception:
        pass


class LessonHost:''')
    raw=replace_once(raw,
        "        manifest = self.GUARD.verify(selected['sha256'])\n",
        "        _t03_began=time.monotonic_ns()\n"
        "        manifest = self.GUARD.verify(selected['sha256'])\n"
        "        _t03_profile('init-host-source-guard',_t03_began)\n")
    raw=replace_once(raw,
        "    def guard(self):\n        self.GUARD.verify(self.host_source['sha256'])\n        self.peer.guard()\n        self.host.schemas.guard()\n        self.host.vault.guard()\n",
        "    def guard(self):\n"
        "        ordinal=getattr(self,'_t03_guard_count',0)+1;self._t03_guard_count=ordinal\n"
        "        total=time.monotonic_ns();began=total\n"
        "        self.GUARD.verify(self.host_source['sha256'])\n"
        "        _t03_profile('host-source-guard',began,ordinal)\n"
        "        began=time.monotonic_ns();self.peer.guard();_t03_profile('machine-peer-guard',began,ordinal)\n"
        "        began=time.monotonic_ns();self.host.schemas.guard();_t03_profile('schema-guard',began,ordinal)\n"
        "        began=time.monotonic_ns();self.host.vault.guard();_t03_profile('vault-guard',began,ordinal)\n")
    raw=replace_once(raw,
        "        self.resource.guard()\n        row = self.parent.sessions.selected(self.peer.row['session_ref'])\n",
        "        began=time.monotonic_ns();self.resource.guard();_t03_profile('resource-guard',began,ordinal)\n"
        "        began=time.monotonic_ns();row = self.parent.sessions.selected(self.peer.row['session_ref'])\n"
        "        _t03_profile('session-selected',began,ordinal)\n")
    raw=replace_once(raw,
        "        require('lesson.select' in self.peer.policy['allowed_operations']\n"
        "                and 'lesson.select' in self.parent.channel.policy_guard()['allowed_operations'], 'parent has not explicitly granted lesson read')\n",
        "        began=time.monotonic_ns()\n"
        "        require('lesson.select' in self.peer.policy['allowed_operations']\n"
        "                and 'lesson.select' in self.parent.channel.policy_guard()['allowed_operations'], 'parent has not explicitly granted lesson read')\n"
        "        _t03_profile('parent-policy-guard',began,ordinal)\n")
    raw=replace_once(raw,
        "        return row\n\n    def read(self, selected):\n",
        "        _t03_profile('host-guard-total',total,ordinal)\n"
        "        return row\n\n    def read(self, selected):\n")
    return raw


def build():
    if row(OLD/'source-manifest.json')['sha256']!=OLD_MANIFEST_SHA or row(OLD/'contract-profile.json')['sha256']!=OLD_PROFILE_SHA:
        raise ValueError('predecessor API changed')
    if NEW.exists():raise ValueError('successor already exists')
    source=json.loads((OLD/'source-manifest.json').read_bytes())
    profile=json.loads((OLD/'contract-profile.json').read_bytes())
    old_prefix=OLD.relative_to(ROOT).as_posix()+'/'
    own=[r for r in source['files'] if r['path'].startswith(old_prefix)]
    if len(own)!=203 or len(source['files'])!=211:raise ValueError('selected closure differs')
    NEW.mkdir()
    for selected in own:
        path=ROOT/selected['path']
        if row(path)!=selected:raise ValueError('predecessor byte changed: '+selected['path'])
        target=NEW/selected['path'][len(old_prefix):]
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes())
    host=NEW/'t03_lesson_host.py'
    raw=profile_host(host.read_text())
    compile(raw,str(host),'exec')
    host.write_text(raw)
    new_prefix=NEW.relative_to(ROOT).as_posix()+'/'
    profile['files']=sorted((row(NEW/r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                             for r in profile['files']),key=lambda r:r['path'])
    profile['integration_members_binding']=row(NEW/'integration-members.json')
    profile['claim_ceiling']='T03 selected guard timing only; no Lesson effect or optimization claim.'
    write(NEW/'contract-profile.json',profile)
    source['files']=sorted((row(NEW/r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                            for r in source['files']),key=lambda r:r['path'])
    source['profile_binding']=row(NEW/'contract-profile.json')
    source['predecessor_source_manifest_binding']=row(OLD/'source-manifest.json')
    source['claim_ceiling']=profile['claim_ceiling']
    write(NEW/'source-manifest.json',source)
    receipt={'schema_version':'lab-T03-d95-guard-profile-recut/v1-candidate',
             'predecessor_binding':row(OLD/'source-manifest.json'),
             'successor_package':NEW.relative_to(ROOT).as_posix(),
             'successor_manifest_sha256':row(NEW/'source-manifest.json')['sha256'],
             'successor_binding':row(NEW/'source-manifest.json'),
             'successor_profile_binding':row(NEW/'contract-profile.json'),
             'host_binding':row(host),'own_file_count':203,'external_file_count':8,
             'authority_effect':'none','lesson_applied':False,'lesson_assessed':False}
    write(NEW/'rebind-receipt.json',receipt)
    return receipt


if __name__=='__main__':print(json.dumps(build(),sort_keys=True,indent=2))
