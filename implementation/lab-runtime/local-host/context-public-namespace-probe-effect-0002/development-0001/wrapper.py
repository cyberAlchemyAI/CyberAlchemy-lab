"""One-shot PUBLIC-ONLY probe effect wrapper; dispatch only after static review."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
PREVIOUS = LOCAL / 'context-public-namespace-probe-release-0002'
PREVIOUS_FREEZE = PREVIOUS / 'freeze.json'
PREVIOUS_REVIEW = LOCAL / 'CONTEXT-PUBLIC-NAMESPACE-PROBE-INDEPENDENT-STATIC-REVIEW-0002.md'
FREEZE = HERE / 'freeze.json'
SELF = HERE / 'wrapper.py'
PYTHON = '/usr/bin/python3.14'
DIST_PACKAGES = Path('/usr/lib/python3/dist-packages')
PREVIOUS_FREEZE_SHA = 'd16e9826ee9eb34aa2353b389e2a445772d0b1f8fba14e980418811cfb987068'
PREVIOUS_REVIEW_SHA = '1548a2b439726af681a2020c2d83e19215ce72bd6852f2cbf58979469f296afc'
PREVIOUS_MEMBERS = {
    'HANDOFF.md':'9c0725c457dfc6b1acb81da6952d985b8cfff7f98ae2ed95734d046c7f367170',
    'release.py':'f2da0e4a4ab399f6882b551db675ea8ba17b301060d0be1549a10ff12bd79427',
    'observer.py':'940b5fb327530baa96351181c43f05741e0cc318034b02ba1a868caac84ca048',
    'probe_child.py':'34dd54aafa8abc421dc2810c4dc2a699b696301f7132909e642ee3d7658b1242',
    'test_release.py':'1c8d2bea955f1f54b4517ffc6248e9fc270f0e3266c3cefda9d2c4ff282a7853',
    'preflight.json':'93bd1e305086cc9b575e72d188baaf050dc513a32b2b9b5678b0ee72c454905b',
}
CORRECTION_REVIEW = LOCAL / 'CONTEXT-PUBLIC-NAMESPACE-PROBE-EFFECT-INDEPENDENT-STATIC-REVIEW-0001.md'
CORRECTION_REVIEW_SHA = '871395fc7052bcd1815c32c569cdd4ebae5ad206b03ee93adcc7c86fa92e3e8b'
EFFECT_ENABLED = True
MAX_MEMBER = 2*1024*1024
DOCKER_ENV = {'PATH':'/usr/bin:/bin','HOME':'/home/vlad_'}


class Refused(RuntimeError):
    pass


def need(ok,code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def read_file(path, expected=None, *, exact_mode=None, owner=None):
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
             0 < st.st_size <= MAX_MEMBER and
             (exact_mode is None or stat.S_IMODE(st.st_mode) == exact_mode) and
             (owner is None or st.st_uid == owner),'PIN_SHAPE')
        chunks = []
        remaining = st.st_size+1
        while remaining:
            block = os.read(fd,min(65536,remaining))
            if not block: break
            chunks.append(block)
            remaining -= len(block)
        raw = b''.join(chunks)
        end = os.fstat(fd)
        need(len(raw) == st.st_size and
             (st.st_dev,st.st_ino,st.st_mode,st.st_size) ==
             (end.st_dev,end.st_ino,end.st_mode,end.st_size) and
             (expected is None or sha(raw) == expected),'PIN_DRIFT')
        return raw
    finally:
        os.close(fd)


def selected_docker_call(argv, timeout=10):
    need(type(argv) is list and argv and argv[0] == '/usr/bin/docker' and
         type(timeout) in (int,float) and 0 < timeout <= 10,
         'SELECTED_DOCKER_CALL')
    result = subprocess.run(argv,stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            env=DOCKER_ENV,timeout=timeout,check=False)
    need(len(result.stdout) <= 65536 and len(result.stderr) <= 65536,
         'DOCKER_STREAM_BOUND')
    return result


def selected_python_imports():
    # -I -S excludes distro packages. The reviewed original validator needs
    # jsonschema; admit only the root-owned, non-writable distro package dir.
    st = os.stat(DIST_PACKAGES,follow_symlinks=False)
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == 0 and
         not(st.st_mode & 0o022), 'DIST_PACKAGES_CUSTODY')
    if str(DIST_PACKAGES) not in sys.path:
        sys.path.append(str(DIST_PACKAGES))


# Exact, reversible projection of the pinned observer bootstrap only. All
# function bodies and their definition-time defaults use the selected module.
OBSERVER_IMPORT_PREIMAGE = b"SPEC = importlib.util.spec_from_file_location('context_public_probe_release_inert',RELEASE)\nif SPEC is None or SPEC.loader is None:\n    raise RuntimeError('PUBLIC_PROBE_RELEASE_IMPORT')\nR = importlib.util.module_from_spec(SPEC)\nSPEC.loader.exec_module(R)"
OBSERVER_IMPORT_POSTIMAGE = b'R = _SELECTED_RELEASE'

def observer_projection(raw):
    need(type(raw) is bytes and sha(raw) == PREVIOUS_MEMBERS['observer.py'],
         'OBSERVER_PREIMAGE_PIN')
    need(raw.count(OBSERVER_IMPORT_PREIMAGE) == 1 and
         OBSERVER_IMPORT_POSTIMAGE not in raw, 'OBSERVER_IMPORT_PREIMAGE')
    result = raw.replace(OBSERVER_IMPORT_PREIMAGE, OBSERVER_IMPORT_POSTIMAGE, 1)
    need(result.replace(OBSERVER_IMPORT_POSTIMAGE, OBSERVER_IMPORT_PREIMAGE, 1) == raw,
         'OBSERVER_PROJECTION_INVERSE')
    return result


def basis():
    selected_python_imports()
    read_file(CORRECTION_REVIEW,CORRECTION_REVIEW_SHA)
    freeze_raw = read_file(FREEZE)
    freeze = json.loads(freeze_raw)
    need(freeze['schema'] == 'lab-context-public-namespace-probe-effect-freeze/v1' and
         freeze['effect_enabled'] is True and freeze['docker_effect'] == 'UNRUN' and
         freeze['predecessor_freeze_sha256'] == PREVIOUS_FREEZE_SHA and
         freeze['predecessor_review_sha256'] == PREVIOUS_REVIEW_SHA and
         freeze['correction_review_sha256'] == CORRECTION_REVIEW_SHA and
         set(freeze['bindings']) == {'HANDOFF.md','wrapper.py','test_wrapper.py'},
         'WRAPPER_FREEZE_CONTRACT')
    for name,digest in freeze['bindings'].items():
        read_file(HERE/name,digest)
    read_file(PREVIOUS_REVIEW,PREVIOUS_REVIEW_SHA)
    previous_raw = read_file(PREVIOUS_FREEZE,PREVIOUS_FREEZE_SHA)
    previous = json.loads(previous_raw)
    need(previous['effect_enabled'] is False and
         previous['docker_create_or_start'] == 'UNRUN' and
         previous['bindings'] == PREVIOUS_MEMBERS,
         'PREVIOUS_FROZEN_SCOPE')
    selected = {name:read_file(PREVIOUS/name,digest)
                for name,digest in PREVIOUS_MEMBERS.items()}
    release = types.ModuleType('cal_public_probe_reviewed_release_0002')
    release.__file__ = str(PREVIOUS/'release.py')
    exec(compile(selected['release.py'],release.__file__,'exec'),release.__dict__)
    observer = types.ModuleType('cal_public_probe_reviewed_observer_0002')
    observer.__file__ = str(PREVIOUS/'observer.py')
    observer.__dict__['_SELECTED_RELEASE'] = release
    exec(compile(observer_projection(selected['observer.py']),observer.__file__,'exec'),
         observer.__dict__)
    del observer.__dict__['_SELECTED_RELEASE']
    need(observer.R is release,'OBSERVER_SELECTED_RELEASE')
    need(release.EFFECT_ENABLED is False and observer.EFFECT_ENABLED is False and
         release.NAME == 'cal-context-public-only-probe-20261020-0002' and
         release.ATTEMPT == Path('/home/vlad_/.local/state/cyberalchemy-lab/context-public-only-probe-20261020-0002') and
         observer.OBSERVATION == Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-only-probe-20261020-0002') and
         release.CHILD == PREVIOUS/'probe_child.py' and
         release.PINS[release.CHILD] == PREVIOUS_MEMBERS['probe_child.py'],
         'PUBLIC_ONLY_SCOPE_DRIFT')
    selected_host_preflight = release.host_preflight
    def host_preflight():
        return selected_host_preflight(runner=selected_docker_call)
    release.docker_call = selected_docker_call
    release.host_preflight = host_preflight
    return release,observer


def preflight():
    release,observer = basis()
    host = release.preflight(host=True)
    need(host['effect_enabled'] is False and
         host['host']['name_absent'] is True and
         host['host']['attempt_absent'] is True and
         host['name'] == release.NAME and
         not os.path.lexists(observer.OBSERVATION),
         'PRE_DISPATCH_SCOPE_OCCUPIED')
    ancestor = release.open_chain(observer.OBSERVATION.parent)
    try:
        parent = os.fstat(ancestor[-1])
        need(parent.st_uid == os.getuid() and stat.S_IMODE(parent.st_mode) == 0o700,
             'OBSERVER_PARENT_CUSTODY')
    finally:
        release.close_all(ancestor)
    need(Path(PYTHON).is_file() and not Path(PYTHON).is_symlink(),
         'SELECTED_PYTHON_MISSING')
    return {'schema':'context-public-only-probe-effect-predispatch/v1',
            'status':'READY_FOR_INDEPENDENT_EFFECT_REVIEW',
            'effect':'NOT_RUN','predecessor_freeze_sha256':PREVIOUS_FREEZE_SHA,
            'predecessor_review_sha256':PREVIOUS_REVIEW_SHA,
            'docker_name':release.NAME,'attempt':str(release.ATTEMPT),
            'observer_attempt':str(observer.OBSERVATION),
            'selected_python':PYTHON,'host':host['host']}


def observer_spawn(argv,*,token,parent_pid,spawn=subprocess.Popen,**kwargs):
    need(argv == [PYTHON,'-I','-B','-S',str(SELF),'--execute-reviewed-one-shot'] and
         type(token) is str and len(token) == 32 and
         all(c in '0123456789abcdef' for c in token) and
         type(parent_pid) is int and parent_pid == os.getpid() and
         'env' not in kwargs and kwargs.get('start_new_session') is True and
         kwargs.get('close_fds') is True,
         'EXTERNAL_OBSERVER_CHILD_DISPATCH_ONLY')
    env = dict(DOCKER_ENV,CAL_PUBLIC_PROBE_PARENT_PID=str(parent_pid),
               CAL_PUBLIC_PROBE_PARENT_TOKEN=token)
    return spawn(argv,env=env,**kwargs)


def child_handoff(release,observer,environment=None,parent_pid=None):
    environment = os.environ if environment is None else environment
    parent_pid = os.getppid() if parent_pid is None else parent_pid
    token = environment.get('CAL_PUBLIC_PROBE_PARENT_TOKEN')
    pid = environment.get('CAL_PUBLIC_PROBE_PARENT_PID')
    need(type(token) is str and len(token) == 32 and
         all(c in '0123456789abcdef' for c in token) and
         pid == str(parent_pid) and type(parent_pid) is int and parent_pid > 1,
         'CHILD_REQUIRES_EXTERNAL_OBSERVER_PARENT')
    marker = read_file(observer.OBSERVATION/'consumed.json',
                       exact_mode=0o600,owner=os.getuid())
    value = json.loads(marker)
    need(value == {'schema':'context-public-only-probe-consumed/v1',
                   'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW',
                   'name':release.NAME,'attempt':str(observer.OBSERVATION),
                   'retry_allowed':False},
         'CHILD_OBSERVER_CLAIM')
    return token


def release_one_shot():
    release,observer = basis()
    child_handoff(release,observer)
    # The child always gets its own fresh host/name/attempt preflight before
    # the 0002 body's exclusive one-shot claim.
    release.preflight(host=True)
    release.EFFECT_ENABLED = True
    try:
        result = release.run_once()
    finally:
        release.EFFECT_ENABLED = False
    return result


def observe_one_shot():
    preflight()
    release,observer = basis()
    token = os.urandom(16).hex()
    def spawn(argv,**kwargs):
        return observer_spawn(argv,token=token,parent_pid=os.getpid(),**kwargs)
    observer.RELEASE = SELF
    observer.R = release
    observer.EFFECT_ENABLED = True
    release.EFFECT_ENABLED = True
    try:
        result = observer.run_observer(spawn=spawn,
            preflight=release.preflight,read_file=release.check_file,
            docker_call=release.docker_call,
            observation_path=observer.OBSERVATION,timeout=60)
    finally:
        observer.EFFECT_ENABLED = False
        release.EFFECT_ENABLED = False
    return result


def main(argv):
    if argv == ['--preflight']:
        print(json.dumps(preflight(),sort_keys=True,separators=(',',':')))
    elif argv == ['--observe-reviewed-one-shot']:
        print(json.dumps(observe_one_shot(),sort_keys=True,separators=(',',':')))
    elif argv == ['--execute-reviewed-one-shot']:
        print(json.dumps(release_one_shot(),sort_keys=True,separators=(',',':')))
    else:
        raise SystemExit('expected --preflight or --observe-reviewed-one-shot')


if __name__ == '__main__':
    main(sys.argv[1:])
