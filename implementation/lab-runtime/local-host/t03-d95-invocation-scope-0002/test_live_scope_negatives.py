"""Actual d95 policy-drift and effect-inside-read-scope refusals.

No signed source, selected API file, or original callback is modified. The
only mutation is to this test's owned private Reader policy, then it is
restored before cleanup. This does not claim a Lesson application effect.
"""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-invocation-scope-0002'
API_SHA='4e752f33caba970a1b5a169df5ae050e95b08aadd069e33b9561fe894ceaadad'
PROFILE_SHA='df87a7f569ae301ba7389d8909916231a6a3913b434a49e7dd54e3f16b1596fb'
PROVIDER=ROOT/'product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py'
PROVIDER_SHA='44152bf9496a98453be56c0eb7e302ea86b9fc7887c3cbcf5c9a0e69b7c4bf11'
MATERIALS=ROOT/'implementation/lab-runtime/local-host/t03-api33-native-v4-learning-0011/lesson_materials.py'
MATERIALS_SHA='68a093de7c27e0ccfaf6c885a840bd79e4bfc562acb0624dd4f5a015216715a5'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def selected(name,path,*,package=False):
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value

def snapshot(root):
    rows={}
    for directory in ('objects','journal'):
        path=root/directory
        if not path.is_dir() or path.is_symlink():raise ValueError('owned workspace directory unavailable')
        for leaf in sorted(path.rglob('*')):
            if leaf.is_symlink():raise ValueError('owned workspace link refused')
            if leaf.is_file():rows[str(leaf.relative_to(root))]=sha(leaf)
    return rows

def require_current(expiry):
    end=datetime.fromisoformat(expiry.replace('Z','+00:00'))
    if end.tzinfo is None or datetime.now(timezone.utc)>=end:
        raise ValueError('actual Reader policy expired before focused probe')

def main():
    if (sha(API/'source-manifest.json'),sha(API/'contract-profile.json'),sha(PROVIDER),sha(MATERIALS)) != (
        API_SHA,PROFILE_SHA,PROVIDER_SHA,MATERIALS_SHA):raise ValueError('selected executable changed')
    began={'utc':datetime.now(timezone.utc).isoformat(),'monotonic_ns':time.monotonic_ns()}
    package='_cal_t03_d95_scope_negative_api'
    selected(package,API/'__init__.py',package=True)
    provider=selected('_cal_t03_d95_scope_negative_provider',PROVIDER)
    materials=selected('_cal_t03_d95_scope_negative_materials',MATERIALS)
    M=provider.modules(package)
    S=importlib.import_module(package+'.source_bridge')
    C=importlib.import_module(package+'.current_context_sessions')
    B=importlib.import_module(package+'.guarded_candidate')
    F,P=M['fixtures'],M['protocol']
    root=None
    with ExitStack() as stack:
        view=stack.enter_context(S.replay_source(S.CURRENT_SOURCE8_NAME))
        if not S.current_source8_view(view):raise ValueError('current signed Source8 selection differs')
        material,plan=materials.prepare(M,C.D,view.custody_signed_sources)
        root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-t03-d95-scope-negative-',dir='/tmp')))
        root.chmod(0o700)
        key,policy_path,policy_sha=provider.provision(M,root,C.D,view.custody_signed_sources,
            S.CURRENT_SOURCE8_NAME,material)
        channel=M['auth'].ReaderChannel(policy_path,policy_sha,P.Schemas(PROFILE_SHA))
        stack.callback(channel.close)
        channel.authenticate(F.proof(key,channel.challenge))
        key=None
        host=M['service'].Service(view,channel,channel.schemas)
        stack.callback(host.close)
        original=Path(policy_path).read_bytes()
        before=snapshot(root)
        raw=P.compact(F.call(channel.context,'lab.status',M['handlers'].cut(view)))
        nested_refused=False
        inner_reply=None
        exit_refused=False
        require_current(channel.policy['expires_at'])
        try:
            with B.selection(host):
                require_current(channel.policy['expires_at'])
                try:
                    with B.selection(host):pass
                except ValueError as error:
                    if str(error)!='API dispatch and durable effects cannot run inside a pure fact scope':
                        raise
                    nested_refused=True
                inner_reply=host.call(raw)
                require_current(channel.policy['expires_at'])
                Path(policy_path).write_bytes(original+b' ')
        except ValueError as error:
            if str(error)!='reader policy revoked or changed':
                raise
            exit_refused=True
        finally:
            Path(policy_path).write_bytes(original)
        after=snapshot(root)
        if not nested_refused or not exit_refused:
            raise ValueError('nested scope or actual policy drift did not refuse')
        if inner_reply is None or inner_reply.get('code')!='unauthenticated-channel':
            raise ValueError('effect attempt inside read-only scope did not refuse')
        if before!=after:
            raise ValueError('owned objects/journal changed during read-only negative probes')
        channel.guard()
        require_current(channel.policy['expires_at'])
        restored_raw=P.compact(F.call(channel.context,'lab.status',M['handlers'].cut(view)))
        restored_reply=host.call(restored_raw)
        if restored_reply.get('kind')!='result':
            raise ValueError('restored Reader policy did not serve a normal status call')
        if snapshot(root)!=after:
            raise ValueError('restored status call changed owned objects/journal')
        ended={'utc':datetime.now(timezone.utc).isoformat(),'monotonic_ns':time.monotonic_ns()}
        result={'schema_version':'lab-T03-d95-invocation-scope-negatives/v1-candidate',
            'api_manifest_sha256':API_SHA,'profile_sha256':PROFILE_SHA,
            'provider_sha256':PROVIDER_SHA,'materials_sha256':MATERIALS_SHA,
            'beginning':began,'ending':ended,
            'nested_scope_refused':True,'actual_owned_policy_drift_at_scope_exit_refused':True,
            'effect_attempt_inside_read_scope_code':'unauthenticated-channel',
            'effect_attempt_reply_sha256':hashlib.sha256(P.compact(inner_reply)).hexdigest(),
            'restored_status_reply_sha256':hashlib.sha256(P.compact(restored_reply)).hexdigest(),
            'nested_scope_refusal_reason':'API dispatch and durable effects cannot run inside a pure fact scope',
            'policy_drift_refusal_reason':'reader policy revoked or changed',
            'owned_objects_and_journal_regular_files_unchanged':True,
            'owned_regular_file_count':len(after),
            'restored_policy_current':True,'private_root_removed':False,
            'lesson_selected':False,'lesson_applied':False,'lesson_assessed':False,
            'authority_effect':'none'}
    result['private_root_removed']=not root.exists()
    if not result['private_root_removed']:
        raise ValueError('private negative fixture survived cleanup')
    if (sha(API/'source-manifest.json'),sha(API/'contract-profile.json'),sha(PROVIDER),sha(MATERIALS)) != (
        API_SHA,PROFILE_SHA,PROVIDER_SHA,MATERIALS_SHA):raise ValueError('selected executable changed before exit')
    return result

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,indent=2),flush=True)
