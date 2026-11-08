"""Review-gated one-shot outer observer for the public-only sixth mount probe."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
SOURCE = LOCAL/'context-public-policy-namespace-probe-effect-0002'
SOURCE_FREEZE = SOURCE/'freeze.json'
SOURCE_REVIEW = LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0002/review.json'
SOURCE_REVIEW_MD = SOURCE_REVIEW.with_name('REVIEW.md')
RELEASE = LOCAL/'context-public-policy-namespace-probe-0003'
RELEASE_FREEZE = RELEASE/'freeze.json'
RELEASE_REVIEW = LOCAL/'context-public-policy-namespace-probe-independent-static-review-0003/review.json'
RELEASE_REVIEW_MD = RELEASE_REVIEW.with_name('REVIEW.md')
SELF_FREEZE = HERE/'freeze.json'
FUTURE_REVIEW = LOCAL/'context-public-policy-namespace-probe-effect-independent-static-review-0003/review.json'
SOURCE_FREEZE_SHA = 'cef4c593e57e994782bd999f04f73cae6fd488660faa1de0837097c28e52194c'
SOURCE_REVIEW_SHA = '5c2d0f2ff44fde54d43b79d9f735a567c7d67b296169c32f1d276372d62d92c6'
SOURCE_REVIEW_MD_SHA = '6c64c67727b70ecd25e9e01e5160229e3aa14ec90a54cde90a839961488ece5d'
RELEASE_FREEZE_SHA = 'ca9256d958c203dfc4d420d7492d7f35f13bd4cf4181fe30fa176f741b1e37b5'
RELEASE_REVIEW_SHA = '4d991c451192a4ba4c59813d4567c32473661ed8d91f2b35438165b2240729f6'
RELEASE_REVIEW_MD_SHA = '6d5fe399e37cf08b16a69bbeaa1bb960c5db39e642a3b82ea5358b7749367c57'
SOURCE_SHA = '175fe0148248f8e58539489c446e7074d2f57e6a2aa226e69f13f789cb94566e'
NAME = 'cal-context-public-policy-probe-20261020-0003'
RELEASE_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-public-policy-probe-20261020-0003')
INNER_OBSERVATION = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-policy-probe-20261020-0003')
OUTER_OBSERVATION = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/context-public-policy-probe-effect-20261020-0003')
PYTHON = '/usr/bin/python3.14'
PYTHON_SHA = '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
DIR_FLAGS = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
LEAF_FLAGS = os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC
EFFECT_ENABLED = False  # the future exact independent review digest is the runtime gate
MAX_OUTER_STREAM = 8192

class Refused(RuntimeError): pass

def need(ok,code):
    if not ok: raise Refused(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def wire(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def checked_bytes(path,expected=None,limit=2*1024*1024,mode=None):
    """Read one stable regular leaf through held nofollow physical ancestors."""
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts,'ABSOLUTE_PIN')
    fds=[os.open('/',DIR_FLAGS)]
    error=None
    try:
        for part in path.parent.parts[1:]:
            fds.append(os.open(part,DIR_FLAGS,dir_fd=fds[-1]))
        for fd in fds:
            st=os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'PIN_ANCESTOR')
        parent=fds[-1]
        before=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
             before.st_uid in (0,os.getuid()) and not(before.st_mode & 0o022) and
             0 <= before.st_size <= limit and
             (mode is None or stat.S_IMODE(before.st_mode)==mode),'PIN_LEAF')
        leaf=os.open(path.name,LEAF_FLAGS,dir_fd=parent)
        fds.append(leaf)
        ident=lambda st:(st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,
                         st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
        need(ident(os.fstat(leaf))==ident(before),'PIN_OPEN_DRIFT')
        raw=bytearray()
        while len(raw)<=before.st_size:
            block=os.read(leaf,min(65536,before.st_size+1-len(raw)))
            if not block: break
            raw.extend(block)
        named=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(len(raw)==before.st_size and
             ident(os.fstat(leaf))==ident(named)==ident(before) and
             (expected is None or sha(raw)==expected),'PIN_DRIFT')
        return bytes(raw)
    except BaseException as exc:
        error=exc
        raise
    finally:
        failures=[]
        for fd in reversed(fds):
            try: os.close(fd)
            except BaseException as exc: failures.append(exc)
        if failures:
            if error is not None:
                error.add_note('PIN_CLOSE_UNCERTAIN')
            else:
                raise Refused('PIN_CLOSE_UNCERTAIN') from failures[0]

def parse(raw):
    def unique(rows):
        value={}
        for key,item in rows:
            need(key not in value,'DUPLICATE_JSON_KEY')
            value[key]=item
        return value
    value=json.loads(raw,object_pairs_hook=unique,
        parse_constant=lambda _x: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    need(type(value) is dict,'JSON_OBJECT')
    return value

def basis():
    own_raw=checked_bytes(SELF_FREEZE,limit=65536)
    own=parse(own_raw)
    need(own['schema']=='context-public-policy-probe-effect-one-shot-freeze/v1' and
         own['effect_enabled'] is False and own['docker_effect']=='UNRUN' and
         own['source_freeze_sha256']==SOURCE_FREEZE_SHA and
         own['source_review_sha256']==SOURCE_REVIEW_SHA and
         own['release_freeze_sha256']==RELEASE_FREEZE_SHA and
         own['release_review_sha256']==RELEASE_REVIEW_SHA and
         own['name']==NAME and own['release_attempt']==str(RELEASE_ATTEMPT) and
         own['inner_observation']==str(INNER_OBSERVATION) and
         own['outer_observation']==str(OUTER_OBSERVATION) and
         set(own['members'])=={'wrapper.py','test_wrapper.py','run_tests.py','HANDOFF.md'},
         'SELF_FREEZE_SCOPE')
    for name,digest in own['members'].items(): checked_bytes(HERE/name,digest)
    source_freeze=parse(checked_bytes(SOURCE_FREEZE,SOURCE_FREEZE_SHA,limit=65536))
    release_freeze=parse(checked_bytes(RELEASE_FREEZE,RELEASE_FREEZE_SHA,limit=65536))
    source_review=parse(checked_bytes(SOURCE_REVIEW,SOURCE_REVIEW_SHA,limit=65536))
    release_review=parse(checked_bytes(RELEASE_REVIEW,RELEASE_REVIEW_SHA,limit=65536))
    checked_bytes(SOURCE_REVIEW_MD,SOURCE_REVIEW_MD_SHA,limit=262144)
    checked_bytes(RELEASE_REVIEW_MD,RELEASE_REVIEW_MD_SHA,limit=262144)
    need(source_freeze['effect_enabled'] is False and
         source_freeze['docker_effect']=='UNRUN' and
         source_freeze['selected_freeze_sha256']==RELEASE_FREEZE_SHA and
         source_freeze['name']==NAME and
         source_freeze['attempt']==str(RELEASE_ATTEMPT) and
         source_freeze['observation']==str(INNER_OBSERVATION) and
         source_freeze['members']['wrapper.py']==SOURCE_SHA and
         release_freeze['effect_enabled'] is False and
         release_freeze['docker_effect']=='UNRUN' and
         release_freeze['name']==NAME and
         release_freeze['attempt']==str(RELEASE_ATTEMPT) and
         release_freeze['observation']==str(INNER_OBSERVATION),
         'SELECTED_FREEZE_SCOPE')
    need(source_review['verdict']=='PASS_BOUNDED_EFFECT_DISABLED_WRAPPER_ONLY' and
         source_review['candidate_freeze_sha256']==SOURCE_FREEZE_SHA and
         source_review['selected_release_freeze_sha256']==RELEASE_FREEZE_SHA and
         source_review['selected_release_independent_review_sha256']==RELEASE_REVIEW_SHA and
         source_review['findings']==[] and
         release_review['verdict']=='PASS_BOUNDED_PUBLIC_ONLY_STATIC' and
         release_review['candidate_freeze_sha256']==RELEASE_FREEZE_SHA and
         release_review['findings']==[] and
         release_review['same_uid_ceiling']=='TRUSTED_SAME_UID_NOT_HOSTILE_SWAP_PROOF',
         'INDEPENDENT_PASS_SCOPE')
    for name,digest in source_freeze['members'].items():
        checked_bytes(SOURCE/name,digest)
    for name,digest in release_freeze['members'].items():
        checked_bytes(RELEASE/name,digest)
    source=checked_bytes(SOURCE/'wrapper.py',SOURCE_SHA)
    selected=types.ModuleType('selected_policy_probe_disabled_wrapper_0002')
    selected.__file__=str(SOURCE/'wrapper.py')
    exec(compile(source,selected.__file__,'exec'),selected.__dict__)
    need(selected.EFFECT_ENABLED is False and selected.NAME==NAME and
         selected.ATTEMPT==RELEASE_ATTEMPT and
         selected.OBSERVATION==INNER_OBSERVATION and
         selected.SELECTED_FREEZE_SHA==RELEASE_FREEZE_SHA,
         'SELECTED_WRAPPER_IDENTITY')
    release,observer,_=selected.basis()
    need(release.EFFECT_ENABLED is False and observer.EFFECT_ENABLED is False and
         release.docker_call.__globals__['bounded_capture'] is release.bounded_capture and
         release.host_preflight.__defaults__[0] is release.docker_call,
         'BOUNDED_SELECTED_RELEASE')
    return selected,release,observer,source,sha(own_raw)

def preflight(selection=None):
    selected,release,observer,_source,_freeze_sha = basis() if selection is None else selection
    selected_result=selected.preflight(selection=(release,observer,_source))
    need(selected_result['effect']=='NOT_RUN' and
         selected_result['docker_name']==NAME and
         selected_result['host']['name_absent'] is True and
         selected_result['host']['attempt_absent'] is True and
         not os.path.lexists(INNER_OBSERVATION) and
         not os.path.lexists(OUTER_OBSERVATION),'FRESH_SAME_STATE')
    fds=release.open_chain(OUTER_OBSERVATION.parent)
    try:
        st=os.fstat(fds[-1])
        need(st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,
             'OUTER_PRIVATE_PARENT')
    finally: release.close_all(fds)
    return {'schema':'context-public-policy-probe-effect-one-shot-preflight/v1',
            'status':'AWAITING_OWN_INDEPENDENT_STATIC_REVIEW',
            'effect':'NOT_RUN','source_freeze_sha256':SOURCE_FREEZE_SHA,
            'source_review_sha256':SOURCE_REVIEW_SHA,
            'release_freeze_sha256':RELEASE_FREEZE_SHA,
            'release_review_sha256':RELEASE_REVIEW_SHA,
            'name':NAME,'outer_observation':str(OUTER_OBSERVATION),
            'inner_observation':str(INNER_OBSERVATION),
            'host':selected_result['host'],'mounts':selected_result['mounts']}

def own_static_review(digest,freeze_sha):
    need(type(digest) is str and len(digest)==64 and
         all(c in '0123456789abcdef' for c in digest),'REVIEW_DIGEST')
    review=parse(checked_bytes(FUTURE_REVIEW,digest,limit=65536))
    need(review['schema']=='context-public-policy-probe-effect-one-shot-independent-static-review/v1' and
         review['verdict']=='PASS_BOUNDED_PUBLIC_ONLY_ONE_SHOT_STATIC' and
         review['candidate_freeze_sha256']==freeze_sha and
         review['findings']==[] and review['docker_effect']=='UNRUN' and
         review['same_uid_ceiling']=='TRUSTED_SAME_UID_NOT_HOSTILE_SWAP_PROOF',
         'OWN_STATIC_REVIEW_NOT_PASS')
    return digest

def child_argv(source,token):
    need(type(source) is bytes and sha(source)==SOURCE_SHA and
         type(token) is str and len(token)==32 and
         all(c in '0123456789abcdef' for c in token),'CHILD_SELECTION')
    payload=base64.b64encode(source).decode('ascii')
    program=(
        "import base64,hashlib,json,os,stat,sys,types\n"
        f"source=base64.b64decode({payload!r},validate=True)\n"
        f"hashlib.sha256(source).hexdigest()=={SOURCE_SHA!r} or "
        "(_ for _ in ()).throw(RuntimeError('SOURCE_BUFFER_DRIFT'))\n"
        f"token={token!r}\n"
        "os.environ.get('CAL_POLICY_OUTER_TOKEN')==token or "
        "(_ for _ in ()).throw(RuntimeError('PARENT_TOKEN'))\n"
        "os.environ.get('CAL_POLICY_OUTER_PID')==str(os.getppid()) or "
        "(_ for _ in ()).throw(RuntimeError('PARENT_PID'))\n"
        f"marker_path={str(OUTER_OBSERVATION/'consumed.json')!r}\n"
        "fd=os.open(marker_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)\n"
        "try:\n"
        " st=os.fstat(fd);body=os.read(fd,st.st_size+1);end=os.fstat(fd)\n"
        " (stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_uid==os.getuid() "
        "and stat.S_IMODE(st.st_mode)==0o600 and 0<st.st_size<=2048 and "
        "len(body)==st.st_size and "
        "(st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_size)=="
        "(end.st_dev,end.st_ino,end.st_mode,end.st_uid,end.st_size)) or "
        "(_ for _ in ()).throw(RuntimeError('OUTER_MARKER_SHAPE'))\n"
        "finally: os.close(fd)\n"
        f"json.loads(body)=={{'schema':'context-public-only-probe-consumed/v1',"
        f"'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW','name':{NAME!r},"
        f"'attempt':{str(OUTER_OBSERVATION)!r},'retry_allowed':False}} or "
        "(_ for _ in ()).throw(RuntimeError('OUTER_MARKER'))\n"
        f"source_path={str(SOURCE/'wrapper.py')!r}\n"
        "module=types.ModuleType('selected_policy_probe_effect_one_shot')\n"
        "module.__file__=source_path\n"
        "exec(compile(source,source_path,'exec'),module.__dict__)\n"
        "module.EFFECT_ENABLED=True\n"
        "result=module.observe_one_shot()\n"
        "print(json.dumps(result,sort_keys=True,separators=(',',':')))\n")
    need(len(program.encode())<65536,'CHILD_PROGRAM_BOUND')
    return [PYTHON,'-I','-B','-S','-c',program]

def outer_join(code,stdout,stderr,inner_record_raw):
    need(type(code) is int and code==0 and type(stdout) is bytes and
         0 < len(stdout)<=MAX_OUTER_STREAM and stderr==b'',
         'OUTER_OS_EXIT_OR_STREAMS')
    summary=parse(stdout)
    record=parse(inner_record_raw)
    need(stdout==wire(summary) and
         summary['overall']=='PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY' and
         summary['container_name_absent'] is True and
         summary['container_cid_absent'] is True and
         summary['retry_allowed'] is False and
         record['schema']=='context-public-only-probe-observer-record/v1' and
         record['status']=='PROVISIONAL_MATCH' and
         record['candidate']==summary and record['retry_allowed'] is False,
         'INNER_OUTER_JOIN')
    return {'schema':'context-public-policy-probe-outer-os-join/v1',
            'status':'PROVISIONAL_EXTERNAL_EFFECT_REVIEW_REQUIRED',
            'inner_candidate_sha256':sha(wire(summary)),
            'inner_record_sha256':sha(inner_record_raw),
            'outer_os_exit':code,'outer_stdout_sha256':sha(stdout),
            'outer_stderr_sha256':sha(stderr),
            'name':NAME,'retry_allowed':False}

def observe_one_shot(review_digest):
    # The frozen candidate is inert until its own exact independent PASS is
    # supplied from the fixed review path. A HOLD or absent review refuses.
    selection=basis()
    own_static_review(review_digest,selection[4])
    preflight(selection)
    selected,release,observer,source,_=selection
    token=os.urandom(16).hex()
    argv=child_argv(source,token)
    outer=release.Attempt(OUTER_OBSERVATION)
    process=None
    streams=(b'',b'')
    candidate=None
    error=None
    try:
        outer.claim()
        outer.write('intent.json',release.wire({
            'schema':'context-public-policy-probe-outer-intent/v1',
            'review_sha256':review_digest,'source_sha256':SOURCE_SHA,
            'source_freeze_sha256':SOURCE_FREEZE_SHA,
            'release_freeze_sha256':RELEASE_FREEZE_SHA,
            'argv':argv,'retry_allowed':False}))
        env=dict(selected.DOCKER_ENV,CAL_POLICY_OUTER_TOKEN=token,
                 CAL_POLICY_OUTER_PID=str(os.getpid()))
        process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,
            close_fds=True,start_new_session=True)
        streams=observer.capture_once(process,60)
        need(type(process.returncode) is int and process.returncode==0,
             'OUTER_CHILD_EXIT')
        inner_raw=checked_bytes(INNER_OBSERVATION/'observation.json',
                                limit=MAX_OUTER_STREAM,mode=0o600)
        candidate=outer_join(process.returncode,*streams,inner_raw)
    except BaseException as exc:
        error=exc
        if isinstance(exc,subprocess.TimeoutExpired):
            streams=(bytes(exc.output or b'')[:MAX_OUTER_STREAM],
                     bytes(exc.stderr or b'')[:MAX_OUTER_STREAM])
        elif isinstance(exc,observer.CaptureUnknown):
            streams=exc.streams
    finally:
        if process is not None:
            if process.poll() is None:
                error=error or Refused('OUTER_CHILD_UNREAPED')
                try:
                    os.killpg(process.pid,signal.SIGTERM)
                    process.wait(timeout=2)
                except BaseException as exc:
                    error=error or exc
                    try:
                        if process.poll() is None:
                            os.killpg(process.pid,signal.SIGKILL)
                            process.wait(timeout=2)
                    except BaseException as final_exc: error=error or final_exc
            for pipe in (process.stdout,process.stderr):
                if pipe is not None:
                    try: pipe.close()
                    except BaseException as exc: error=error or exc
            if process.poll() is None: error=error or Refused('OUTER_CHILD_UNREAPED')
        if outer.claimed:
            try:
                outer.write('stdout',streams[0])
                outer.write('stderr',streams[1])
                outer.write('observation.json',release.wire({
                    'schema':'context-public-policy-probe-outer-observation/v1',
                    'status':'PROVISIONAL_UNTIL_POSTCLOSE_OS_REVIEW' if error is None else
                             'UNKNOWN_PRESERVE_NO_RETRY',
                    'candidate':candidate if error is None else None,
                    'error_class':None if error is None else type(error).__name__,
                    'error_detail':None if error is None else str(error)[:160],
                    'retry_allowed':False}))
            except BaseException as exc: error=error or exc
        try: outer.close()
        except BaseException as exc: error=error or exc
    need(error is None and candidate is not None and outer.claimed,
         'OUTER_UNKNOWN_PRESERVE_NO_RETRY')
    expected=release.wire({'schema':'context-public-policy-probe-outer-observation/v1',
        'status':'PROVISIONAL_UNTIL_POSTCLOSE_OS_REVIEW','candidate':candidate,
        'error_class':None,'error_detail':None,'retry_allowed':False})
    need(checked_bytes(OUTER_OBSERVATION/'observation.json',sha(expected),mode=0o600)==expected,
         'OUTER_POSTCLOSE_READBACK')
    return candidate

def main(args):
    if args==['--preflight']:
        print(json.dumps(preflight(),sort_keys=True,separators=(',',':')))
    elif len(args)==3 and args[:2]==['--observe-reviewed-one-shot','--review-sha256']:
        print(json.dumps(observe_one_shot(args[2]),sort_keys=True,separators=(',',':')))
    else:
        raise SystemExit('expected --preflight or reviewed one-shot with review digest')

if __name__=='__main__': main(sys.argv[1:])
