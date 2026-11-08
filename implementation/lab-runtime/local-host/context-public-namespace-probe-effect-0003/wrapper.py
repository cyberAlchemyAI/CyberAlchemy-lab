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
PREVIOUS = LOCAL / 'context-public-namespace-probe-release-0003'
PREVIOUS_FREEZE = PREVIOUS / 'freeze.json'
PREVIOUS_REVIEW = LOCAL / 'CONTEXT-PUBLIC-NAMESPACE-PROBE-INDEPENDENT-STATIC-REVIEW-0003.md'
FREEZE = HERE / 'freeze.json'
SELF = HERE / 'wrapper.py'
PYTHON = '/usr/bin/python3.14'
DIST_PACKAGES = Path('/usr/lib/python3/dist-packages')
PREVIOUS_FREEZE_SHA = 'dbb060c109750ac31b3a2b0d25f4a4a3d753787c86077c066a423c90f6c34535'
PREVIOUS_REVIEW_SHA = 'f7bde43cd57eeacd149ca85f1b3e2f79d27d20578b13c371a58ef92d3402e342'
PREVIOUS_MEMBERS = {
    'release.py':'759faa86d6494802ad84a2818e80372d2a7929acf0ca6e622ffd66bd03d86be1',
    'observer.py':'45696584a9e8856fe44b45c33535179d10b7f7bddb98a4075c980be9ee4e0a1d',
    'probe_child.py':'34dd54aafa8abc421dc2810c4dc2a699b696301f7132909e642ee3d7658b1242',
    'test_release.py':'f9e22c66e1eb4d408741eb39a2162b0d53751f5b896366b6b6cf17e81ce4239f',
    'preflight.json':'19376990e4edd56e6bb6b6658860d6fb0d0fbb5e60f4601c705954732f4a0b7b',
    'HANDOFF.md':'496cc7abbf9db7343a08b580e8083b368f3807a212802cc07ccd2d3822d41c2b',
}
PREVIOUS_SIZES = {'release.py':27088,'observer.py':11641,
                  'probe_child.py':4749,'test_release.py':18648,
                  'preflight.json':3281,'HANDOFF.md':3155}
BOOTSTRAP_WRAPPER_FREEZE = LOCAL / 'context-public-namespace-probe-effect-0002/freeze.json'
BOOTSTRAP_WRAPPER_REVIEW = LOCAL / 'CONTEXT-PUBLIC-NAMESPACE-PROBE-EFFECT-INDEPENDENT-STATIC-REVIEW-0002.md'
BOOTSTRAP_WRAPPER_FREEZE_SHA = '57ed09a70c67da497bbfae7f5fe1b47ecb38cba849ff68d830e27b00dce34bd5'
BOOTSTRAP_WRAPPER_REVIEW_SHA = '25e6d58cb55bf963656197298fb944e8ab533025ead75ca9cb5f9f1f176d4763'
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
    bootstrap_freeze = json.loads(read_file(BOOTSTRAP_WRAPPER_FREEZE,
                                          BOOTSTRAP_WRAPPER_FREEZE_SHA))
    bootstrap_review = read_file(BOOTSTRAP_WRAPPER_REVIEW,
                                 BOOTSTRAP_WRAPPER_REVIEW_SHA)
    need(bootstrap_freeze['schema'] ==
         'lab-context-public-namespace-probe-effect-freeze/v1' and
         bootstrap_freeze['docker_effect'] == 'UNRUN' and
         b'**Verdict: PASS_BOUNDED_PUBLIC_ONLY_STATIC.**' in bootstrap_review and
         BOOTSTRAP_WRAPPER_FREEZE_SHA.encode() in bootstrap_review,
         'CHECKED_BUFFER_BOOTSTRAP_REVIEW')
    freeze_raw = read_file(FREEZE)
    freeze = json.loads(freeze_raw)
    need(freeze['schema'] == 'lab-context-public-namespace-probe-effect-freeze/v3' and
         freeze['effect_enabled'] is True and freeze['docker_effect'] == 'UNRUN' and
         freeze['predecessor_freeze_sha256'] == PREVIOUS_FREEZE_SHA and
         freeze['predecessor_review_sha256'] == PREVIOUS_REVIEW_SHA and
         freeze['bootstrap_wrapper_freeze_sha256'] == BOOTSTRAP_WRAPPER_FREEZE_SHA and
         freeze['bootstrap_wrapper_review_sha256'] == BOOTSTRAP_WRAPPER_REVIEW_SHA and
         set(freeze['bindings']) == {'HANDOFF.md','wrapper.py','test_wrapper.py'},
         'WRAPPER_FREEZE_CONTRACT')
    for name,digest in freeze['bindings'].items():
        read_file(HERE/name,digest)
    release_review = read_file(PREVIOUS_REVIEW,PREVIOUS_REVIEW_SHA)
    need(b'**Verdict: PASS_BOUNDED_RELEASE_ONLY_STATIC.**' in release_review and
         PREVIOUS_FREEZE_SHA.encode() in release_review,
         'RELEASE_INDEPENDENT_PASS')
    previous_raw = read_file(PREVIOUS_FREEZE,PREVIOUS_FREEZE_SHA)
    previous = json.loads(previous_raw)
    need(previous['schema'] == 'lab-context-public-only-namespace-probe-release-freeze/v3' and
         previous['effect_enabled'] is False and
         previous['docker_create_or_start'] == 'UNRUN' and
         previous['external_observer_effect'] == 'UNRUN' and
         previous['attempt'] == '/home/vlad_/.local/state/cyberalchemy-lab/context-public-only-probe-20261020-0003' and
         previous['observation'] == '/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-only-probe-20261020-0003' and
         previous['container_name'] == 'cal-context-public-only-probe-20261020-0003' and
         type(previous['file_bindings']) is list and
         previous['file_bindings'] == [
             {'path':str((PREVIOUS/name).relative_to(HERE.parents[3])),
              'size':PREVIOUS_SIZES[name],'sha256':digest}
             for name,digest in PREVIOUS_MEMBERS.items()],
         'PREVIOUS_FROZEN_SCOPE')
    selected = {name:read_file(PREVIOUS/name,digest)
                for name,digest in PREVIOUS_MEMBERS.items()}
    release = types.ModuleType('cal_public_probe_reviewed_release_0003')
    release.__file__ = str(PREVIOUS/'release.py')
    exec(compile(selected['release.py'],release.__file__,'exec'),release.__dict__)
    observer = types.ModuleType('cal_public_probe_reviewed_observer_0003')
    observer.__file__ = str(PREVIOUS/'observer.py')
    observer.__dict__['_SELECTED_RELEASE'] = release
    exec(compile(observer_projection(selected['observer.py']),observer.__file__,'exec'),
         observer.__dict__)
    del observer.__dict__['_SELECTED_RELEASE']
    need(observer.R is release,'OBSERVER_SELECTED_RELEASE')
    need(release.EFFECT_ENABLED is False and observer.EFFECT_ENABLED is False and
         release.NAME == 'cal-context-public-only-probe-20261020-0003' and
         release.ATTEMPT == Path('/home/vlad_/.local/state/cyberalchemy-lab/context-public-only-probe-20261020-0003') and
         observer.OBSERVATION == Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-only-probe-20261020-0003') and
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
    # the 0003 body's exclusive one-shot claim.
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
