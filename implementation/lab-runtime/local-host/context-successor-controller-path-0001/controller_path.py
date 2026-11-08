"""Effect-disabled durable Context controller path and public-probe argv adapter."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import types
from pathlib import Path

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
MOUNT = LOCAL / 'context-successor-mount-reconcile-0001/mount_vector.py'
MOUNT_FREEZE = LOCAL / 'context-successor-mount-reconcile-0001/freeze.json'
MOUNT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-MOUNT-RECONCILE-INDEPENDENT-STATIC-REVIEW-0001.md'
OLD_RUNNER = LOCAL / 'context-docker-runner-0001/runner.py'
CHILD = Path(__file__).with_name('public_probe_child.py')
PINS = {
    MOUNT:'ed04a32ce0d904f5d3f1303f99feb60b02b4ed59fb75b4944d8cc1b58006f95f',
    MOUNT_FREEZE:'31fd3ae4fdfc5afe2d635fbf2ad7f0be20aa5802d104717d192d947055d8fcdc',
    MOUNT_REVIEW:'f36d04e545dfa0e5a9028de9313d805b0c5fcd20e643f7b1d44f77cbb60eb7c2',
    OLD_RUNNER:'7140f6885b5bc3f796bbe46aaad8813ab3443de7c19a407503ce27417afbc0c5',
    CHILD:'be375306ec1b88ae2338161014e809fbac1f586334f9d0b8a22d83bc6779d7d6',
}
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME = 'cal-context-public-probe-20261020-0002'
DOCKER = '/usr/bin/docker'
BOOTSTRAP = ("import hashlib,sys; p='/runner/public_probe_child.py'; "
             "b=open(p,'rb').read(); "
             "hashlib.sha256(b).hexdigest()==sys.argv[1] or "
             "(_ for _ in ()).throw(RuntimeError('PROBE_CHILD_PIN')); "
             "sys.argv=[p,sys.argv[2]]; "
             "exec(compile(b,p,'exec'),{'__name__':'__main__','__file__':p})")
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path):
    need(path in PINS,'UNSELECTED_CONTROLLER_PREIMAGE')
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a = os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_nlink == 1 and
             0 < a.st_size <= 2*1024*1024,'CONTROLLER_PREIMAGE_SHAPE')
        raw = os.read(fd,a.st_size+1)
        b = os.fstat(fd)
        need(len(raw) == a.st_size and
             (a.st_dev,a.st_ino,a.st_mode,a.st_size) ==
             (b.st_dev,b.st_ino,b.st_mode,b.st_size) and
             sha(raw) == PINS[path],'CONTROLLER_PREIMAGE_DRIFT')
        return raw
    finally:
        os.close(fd)


def mounted_predecessor():
    for path in PINS:
        pinned(path)
    original = pinned(OLD_RUNNER)
    need(original.count(b"roots['public'] == root / 'public'") == 1 and
         original.count(b"for name in ('public', 'control'):") == 1 and
         original.count(b"here.mkdir(parents=True, mode=0o700)") == 1 and
         original.count(b"source_bytes = b'{\"synthetic_public_only\":true}\\n'") == 1,
         'OLD_ATTEMPT_LOCAL_PUBLIC_ASSUMPTION')
    module = types.ModuleType('cal_mount_vector_reviewed_0001')
    module.__file__ = str(MOUNT)
    exec(compile(pinned(MOUNT),str(MOUNT),'exec'),module.__dict__)
    return module


def plan(now=None):
    mount = mounted_predecessor()
    selected = mount.vector(now)
    root = mount.DOCKER_ATTEMPT
    public = mount.FAMILY/'context-attempt/root'
    need(selected['status'] == 'INERT_PARENT_WRITER_CHILD_RO_MOUNT_VECTOR' and
         selected['effect_enabled'] is False and
         selected['mounts'][0] ==
         {'source':str(public),'target':'/workspace','read_only':True} and
         selected['physical_output_root'] ==
         str(public/selected['context_role']/'packages/0001') and
         selected['child_nested_output_bind'] == 'ABSENT' and
         selected['authorization'] == 'UNMINTED' and
         selected['context_source_manifest'] == 'UNCREATED' and
         selected['docker'] == 'REFUSED' and
         public != root/'public' and public not in root.parents and
         root not in public.parents,
         'DURABLE_PUBLIC_SEPARATE_FROM_PROBE_ATTEMPT')
    controls = {
        'attempt_root':str(root),
        'public_stage_root':str(public),
        'control_dir':str(root/'control'),
        'runner_code_dir':str(root/'runner-code'),
        'cache_guard':str(root/'cache-guard'),
        'physical_context_here':str(public/selected['context_role']),
        'logical_context_here':'/workspace/'+selected['context_role'],
        'physical_output_root':selected['physical_output_root'],
        'logical_output_root':selected['logical_output_root'],
        'old_root_public_creation':'REMOVED_FROM_SUCCESSOR_DESIGN',
        'old_context_role_mkdir':'FORBIDDEN_STAGE_MUST_PREEXIST',
        'old_synthetic_source_manifest_write':'FORBIDDEN_CONTEXT_SOURCE_MUST_BE_REVIEWED',
    }
    need(len(selected['mounts']) == 5 and
         all(row['read_only'] is True for row in selected['mounts']) and
         not any(row['target'].startswith('/workspace/') for row in selected['mounts']) and
         selected['mounts'][1]['source'] == controls['control_dir'] and
         selected['mounts'][2]['source'] == controls['runner_code_dir'] and
         selected['mounts'][3]['source'] == controls['cache_guard'],
         'EXACT_DURABLE_CONTROLLER_MOUNT_PATHS')
    return {'status':'INERT_DURABLE_CONTROLLER_PUBLIC_PROBE_PLAN',
            'effect_enabled':False,'path_adaptation':controls,
            'mounts':selected['mounts'],'image':IMAGE,'docker_name':NAME,
            'uid':os.getuid(),'gid':os.getgid(),
            'probe_child_sha256':PINS[CHILD],
            'parent_writer':'HELD_RW_ONLY_AFTER_READY',
            'child_workspace':'RO_NO_NESTED_OUTPUT_BIND',
            'read_only_feasibility':
                'REQUIRE_REAL_MOUNTINFO_EROFS_READY_POST_ACK_PUBLIC_PROBE',
            'original_output_contract':'40_LEAVES_39_MANIFEST_RELEASE38_FINISH41',
            'terminal_contract':
                'EXTERNAL_OS_DAEMON_ZERO_EMPTY_STDERR_CID_NAME_ABSENT_READBACK',
            'uncertainty':'UNKNOWN_PRESERVE_ATTEMPT_STAGE_AUTH_PRIVATE_OUTPUT_NO_RETRY',
            'mapper':'UNSELECTED','stage_1571':'UNMATERIALIZED',
            'auth':'UNMINTED','docker':'REFUSED','private_cleanup':'REFUSED'}


def probe_argv(token,now=None):
    """Exact inert Docker create argv for a future selected public-only probe."""
    selected = plan(now)
    need(type(token) is str and len(token) == 32 and
         all(c in '0123456789abcdef' for c in token),
         'FRESH_PROBE_TOKEN_REQUIRED')
    config = {'token':token,'uid':selected['uid'],'gid':selected['gid']}
    command = [DOCKER,'create','--name',NAME,'--network','none','--read-only',
               '--user',f"{selected['uid']}:{selected['gid']}",
               '--userns','host','--cap-drop','ALL',
               '--security-opt','no-new-privileges','--pids-limit','8',
               '--memory','128m','--cpus','1','--ipc','none',
               '--entrypoint','/usr/local/bin/python3.14']
    for row in selected['mounts']:
        command += ['--mount',f"type=bind,src={row['source']},dst={row['target']},readonly"]
    command += [IMAGE,'-I','-B','-S','-X','pycache_prefix=/cache-disabled',
                '-c',BOOTSTRAP,PINS[CHILD],
                json.dumps(config,sort_keys=True,separators=(',',':'))]
    need(command.count('--mount') == 5 and
         all('readonly' in command[i+1] for i,value in enumerate(command)
             if value == '--mount') and
         not any('dst=/workspace/' in value for value in command) and
         '--userns' in command and '--read-only' in command and
         '--network' in command and 'none' in command,
         'EXACT_PUBLIC_PROBE_CREATE_ARGV')
    return {'status':'EXACT_ARGV_IN_MEMORY_UNRUN',
            'create_argv':command,'effect_enabled':False,
            'probe_child_sha256':PINS[CHILD],
            'external_os_observer':'REQUIRED_UNSELECTED',
            'docker_invoked':False}


def launch_public_probe(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_PUBLIC_DOCKER_PROBE')


def launch_context_or_cleanup(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_NO_CONTEXT_AUTH_OR_CLEANUP')
