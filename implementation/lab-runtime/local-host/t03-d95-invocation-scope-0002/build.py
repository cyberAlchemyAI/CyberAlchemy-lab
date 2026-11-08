"""Disjoint selected API cut for measured pure Lesson selection/preflight work."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-invocation-scope-0002'
OLD_MANIFEST_SHA = '1b83e97f5cae120473ccc61d151d38bc0d99d2f1bb8a39f8a30ef8ceedb8184d'
OLD_PROFILE_SHA = '3a07464283b6f09aee1bb68ccaa6aa8022666f9ab23871da536947091bbc6413'


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
        raise ValueError('selected optimization anchor differs: ' + repr(old[:80]))
    return raw.replace(old, new)


def scoped_service(raw):
    raw = replace_once(raw, '''    def select_application(self,message,outer,key):
        if self.channel.policy['source_name']==source.CURRENT_SOURCE8_NAME:
            from .current_lesson_application import LessonApplication
        else:from .lesson_application import LessonApplication
        selected=self.channel.policy_guard().get('application_control')
        if selected is None:raise ApplicationError('closure-missing','Independently selected lesson application method and routing are unavailable.')
        path=HERE/'source-manifest.json'
        builder=LessonApplication(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
        builder.preflight(message,outer,key)
        return builder
''', '''    def select_application(self,message,outer,key):
        from .guarded_candidate import selection
        if self.channel.policy['source_name']==source.CURRENT_SOURCE8_NAME:
            from .current_lesson_application import LessonApplication
        else:from .lesson_application import LessonApplication
        # Source facts are borrowed only during this pure candidate selection.
        # The selected read_scope performs full source/producer entry and exit
        # verification; effect preparation and claim remain outside it.
        with selection(self):
            selected=self.channel.policy_guard().get('application_control')
            if selected is None:raise ApplicationError('closure-missing','Independently selected lesson application method and routing are unavailable.')
            path=HERE/'source-manifest.json'
            builder=LessonApplication(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
            builder.preflight(message,outer,key)
            return builder
''')
    return raw


def scoped_lesson(raw):
    return replace_once(raw, '''            with self.parent.sessions.mutex:
                self.guard()
                effective = min(effective, self.resource.expires)
                bridge = self.parent.sessions.bridge
                require(bridge.channel is self.parent.channel and self.resource.bridge is bridge,
                        'live Session parent reader channel differs')
                with self.C.BOUNDARIES.read_scope(self.source, self.C.EL, bridge, producer=self.C.D,
                        package_checks=[(self.C.D.preflight, self.C.DELIVERY_PIN)]):
                    self.peer.guard()
                    evaluated = self.calculate(message, request, outer)
''', '''            with self.parent.sessions.mutex:
                effective = min(effective, self.resource.expires)
                bridge = self.parent.sessions.bridge
                require(bridge.channel is self.parent.channel and self.resource.bridge is bridge,
                        'live Session parent reader channel differs')
                # The original source scope still verifies full signed facts,
                # producer and live policy at entry and exit. Move the first
                # pure host guard inside it to borrow only sealed source facts.
                # This scope ends before derived evidence materialization.
                with self.C.BOUNDARIES.read_scope(self.source, self.C.EL, bridge, producer=self.C.D,
                        package_checks=[(self.C.D.preflight, self.C.DELIVERY_PIN)]):
                    self.guard()
                    evaluated = self.calculate(message, request, outer)
''')


def build():
    if row(OLD/'source-manifest.json')['sha256'] != OLD_MANIFEST_SHA or row(OLD/'contract-profile.json')['sha256'] != OLD_PROFILE_SHA:
        raise ValueError('predecessor API changed')
    if NEW.exists():
        raise ValueError('successor already exists')
    source = json.loads((OLD/'source-manifest.json').read_bytes())
    profile = json.loads((OLD/'contract-profile.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix()+'/'
    own = [r for r in source['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 203 or len(source['files']) != 211:
        raise ValueError('selected closure differs')
    NEW.mkdir()
    for selected in own:
        path = ROOT/selected['path']
        if row(path) != selected:
            raise ValueError('predecessor byte changed: '+selected['path'])
        target = NEW/selected['path'][len(old_prefix):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    for name, transform in (('service.py', scoped_service), ('t03_lesson_host.py', scoped_lesson)):
        path = NEW/name
        raw = transform(path.read_text())
        compile(raw, str(path), 'exec')
        path.write_text(raw)
    new_prefix = NEW.relative_to(ROOT).as_posix()+'/'
    profile['files'] = sorted((row(NEW/r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                               for r in profile['files']), key=lambda r:r['path'])
    profile['integration_members_binding'] = row(NEW/'integration-members.json')
    profile['claim_ceiling'] = 'T03 invocation-local pure selection candidate; live Lesson effects remain unobserved.'
    write(NEW/'contract-profile.json', profile)
    source['files'] = sorted((row(NEW/r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                              for r in source['files']), key=lambda r:r['path'])
    source['profile_binding'] = row(NEW/'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD/'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW/'source-manifest.json', source)
    receipt = {'schema_version':'lab-T03-d95-invocation-scope-recut/v2-candidate',
        'predecessor_binding':row(OLD/'source-manifest.json'),
        'successor_package':NEW.relative_to(ROOT).as_posix(),
        'successor_manifest_sha256':row(NEW/'source-manifest.json')['sha256'],
        'successor_binding':row(NEW/'source-manifest.json'),
        'successor_profile_binding':row(NEW/'contract-profile.json'),
        'service_binding':row(NEW/'service.py'),
        'lesson_host_binding':row(NEW/'t03_lesson_host.py'),
        'own_file_count':203,'external_file_count':8,
        'authority_effect':'none','lesson_applied':False,'lesson_assessed':False}
    write(NEW/'rebind-receipt.json',receipt)
    return receipt


if __name__=='__main__':
    print(json.dumps(build(),sort_keys=True,indent=2))
