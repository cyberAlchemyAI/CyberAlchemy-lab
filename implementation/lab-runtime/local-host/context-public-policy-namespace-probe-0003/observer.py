"""Effect-disabled external OS observer for the one-shot public-only probe."""
from __future__ import annotations

import hashlib
import base64
import types
import importlib.util
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RELEASE = HERE / 'release.py'
# Execute only the exact selected release buffer; never a second path loader.
RELEASE_SHA = '9afed2b3dad5851db0904e2b39956572ae4a270faaa82916bc83e958a66fcf8c'
raw = RELEASE.read_bytes()
if hashlib.sha256(raw).hexdigest() != RELEASE_SHA: raise RuntimeError('RELEASE_DRIFT')
R = types.ModuleType('public_policy_probe_release')
R.__file__ = str(RELEASE)
exec(compile(raw,str(RELEASE),'exec'),R.__dict__)
OBSERVATION = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations') / 'context-public-policy-probe-20261020-0003'
EFFECT_ENABLED = False
CAPTURE = 8192
PYTHON = '/usr/bin/python3.14'
PYTHON_SHA = '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'


class Refused(RuntimeError):
    pass


class CaptureUnknown(Refused):
    def __init__(self, code, streams):
        self.streams = streams
        super().__init__(code)


def need(ok,code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def checked_child_argv(mode):
    """Execute the captured checked release bytes; __file__ is identity only."""
    need(mode in ('--preflight','--execute-reviewed-one-shot'),
         'CHILD_MODE')
    payload = base64.b64encode(raw).decode('ascii')
    program = ("import base64,hashlib,sys\n"
               f"source=base64.b64decode({payload!r},validate=True)\n"
               f"hashlib.sha256(source).hexdigest()=={RELEASE_SHA!r} or "
               "(_ for _ in ()).throw(RuntimeError('RELEASE_BUFFER_DRIFT'))\n"
               f"source_path={str(RELEASE)!r}\n"
               f"sys.argv=[source_path,{mode!r}]\n"
               "exec(compile(source,source_path,'exec'),"
               "{'__name__':'__main__','__file__':source_path})\n")
    need(len(program.encode()) < 65536 and sha(raw) == RELEASE_SHA,
         'CHECKED_CHILD_PROGRAM')
    # -I excludes environment/current directory; -B avoids bytecode. The
    # reviewed distro runtime loads jsonschema, unlike the predecessor -S.
    return [PYTHON,'-I','-B','-c',program]


def join(os_exit,stdout,stderr,terminal_raw,output_raw,post_cid_result,
         post_name_result, mountinfo_raw, policy_raw):
    """Independent final oracle: exact subprocess, terminal, output and daemon join."""
    need(type(os_exit) is int and os_exit == 0 and
         type(stdout) is bytes and type(stderr) is bytes and stderr == b'' and
         0 < len(stdout) <= CAPTURE and len(stderr) <= CAPTURE,
         'EXTERNAL_OS_EXIT_OR_STREAMS')
    try:
        summary = json.loads(stdout)
        terminal = json.loads(terminal_raw)
    except (ValueError,TypeError) as exc:
        raise Refused('EXTERNAL_JSON_SHAPE') from exc
    need(stdout == R.wire(summary) and
         set(summary) == {'status','terminal_sha256','attempt','name','retry_allowed'} and
         summary['status'] == 'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED' and
         summary['terminal_sha256'] == sha(terminal_raw) and
         summary['attempt'] == str(R.ATTEMPT) and
         summary['name'] == R.NAME and summary['retry_allowed'] is False,
         'EXTERNAL_STDOUT_TERMINAL_JOIN')
    need(type(terminal) is dict and set(terminal) == {
         'schema','status','name','attempt','retry_allowed','cid','child_pid',
         'parent_peer','mountinfo_sha256','request_sha256','erofs_errno',
         'child_os_exit','child_stdout_sha256','child_stderr_sha256',
         'six_read_only_mounts','nested_writable_or_private_mount',
         'post_ack_visibility','cid_absent','name_absent','policy_sha256',
         'policy_erofs_errno','mountinfo_raw_retained'},
         'PUBLIC_ONLY_TERMINAL_FIELDS')
    need(terminal['schema'] == 'context-public-only-probe-terminal/v1' and
         terminal['status'] == 'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED' and
         terminal['name'] == R.NAME and terminal['attempt'] == str(R.ATTEMPT) and
         terminal['retry_allowed'] is False and
         type(terminal['cid']) is str and len(terminal['cid']) == 64 and
         type(terminal['child_pid']) is int and terminal['child_pid'] > 0 and
         terminal['parent_peer'] == [terminal['child_pid'],os.getuid(),os.getgid()] and
         terminal['erofs_errno'] == 30 and
         terminal['request_sha256'] == sha(R.REQUEST) and
         type(terminal['child_os_exit']) is int and terminal['child_os_exit'] == 0 and
         terminal['child_stdout_sha256'] == sha(b'') and
         terminal['child_stderr_sha256'] == sha(b'') and
         terminal['six_read_only_mounts'] is True and
         terminal['policy_sha256'] == sha(R.POLICY_PUBLIC) and
         type(terminal['policy_erofs_errno']) is int and terminal['policy_erofs_errno'] == 30 and
         terminal['mountinfo_raw_retained'] is True and
         terminal['nested_writable_or_private_mount'] is False and
         terminal['post_ack_visibility'] is True and
         terminal['cid_absent'] is True and terminal['name_absent'] is True and
         type(terminal['mountinfo_sha256']) is str and
         len(terminal['mountinfo_sha256']) == 64,
         'PUBLIC_ONLY_TERMINAL_CONTRACT')
    need(R.mountinfo_ro(mountinfo_raw) == terminal['mountinfo_sha256'] and
         policy_raw == R.POLICY_PUBLIC, 'POSTCLOSE_RAW_MOUNT_POLICY_JOIN')
    need(output_raw == R.REQUEST and sha(output_raw) == terminal['request_sha256'],
         'POSTCLOSE_PARENT_OUTPUT_READBACK')
    need(R.cid_absent_result(post_cid_result,terminal['cid']),
         'EXTERNAL_CID_ABSENCE')
    need(post_name_result.returncode == 0 and post_name_result.stdout == b'' and
         post_name_result.stderr == b'', 'EXTERNAL_NAME_ABSENCE')
    return {'schema':'context-public-only-probe-external-observation/v1',
            'overall':'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY',
            'terminal_sha256':sha(terminal_raw),
            'request_sha256':sha(output_raw),
            'child_mountinfo_sha256':terminal['mountinfo_sha256'],
            'child_erofs_errno':30,'six_child_read_only_mounts':True,
            'raw_mountinfo_retained':True,'public_policy_sha256':sha(policy_raw),
            'public_policy_erofs_errno':30,'policy_authority_qualification':False,
            'no_nested_writable_or_private_mount':True,
            'post_ack_parent_writer_visibility':True,
            'container_cid_absent':True,'container_name_absent':True,
            'release_os_exit':os_exit,'release_stderr_empty':True,
            'retry_allowed':False}


def capture_once(process, timeout):
    need(type(timeout) in (int,float) and 0 < timeout <= 60,
         'EXTERNAL_TIMEOUT_BOUND')
    # Read both pipes exactly once, bound bytes as they arrive, then reap.
    # This avoids communicate()'s cached-output semantics on repeated calls.
    deadline = time.monotonic()+timeout
    chunks = [bytearray(),bytearray()]
    with selectors.DefaultSelector() as selector:
        for index,pipe in enumerate((process.stdout,process.stderr)):
            need(pipe is not None,'EXTERNAL_PIPE_MISSING')
            os.set_blocking(pipe.fileno(),False)
            selector.register(pipe,selectors.EVENT_READ,index)
        while selector.get_map():
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(process.args,timeout,
                    output=bytes(chunks[0]),stderr=bytes(chunks[1]))
            for key,_ in selector.select(remaining):
                index = key.data
                try:
                    raw = os.read(key.fileobj.fileno(),4096)
                except BlockingIOError:
                    continue
                if not raw:
                    selector.unregister(key.fileobj)
                    continue
                if len(chunks[index])+len(raw) > CAPTURE:
                    chunks[index].extend(raw[:max(0,CAPTURE-len(chunks[index]))])
                    raise CaptureUnknown('EXTERNAL_STREAM_OVERFLOW',
                                         (bytes(chunks[0]),bytes(chunks[1])))
                chunks[index].extend(raw)
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired(process.args,timeout,
            output=bytes(chunks[0]),stderr=bytes(chunks[1]))
    try:
        process.wait(timeout=remaining)
    except subprocess.TimeoutExpired as exc:
        raise subprocess.TimeoutExpired(process.args,timeout,
            output=bytes(chunks[0]),stderr=bytes(chunks[1])) from exc
    need(process.poll() is not None,'EXTERNAL_PROCESS_UNREAPED')
    return bytes(chunks[0]),bytes(chunks[1])


def run_observer(*, spawn=subprocess.Popen, preflight=R.preflight,
                 read_file=R.check_file, docker_call=R.docker_call,
                 observation_path=OBSERVATION, timeout=60):
    need(EFFECT_ENABLED is True and R.EFFECT_ENABLED is True,
         'EXTERNAL_OBSERVER_EFFECT_DISABLED')
    # The observer's separate exclusive claim precedes the child release.
    R.check_file(Path(PYTHON),PYTHON_SHA,64*1024*1024)
    preflight(host=True)
    attempt = R.Attempt(observation_path)
    process = None
    streams = (b'',b'')
    candidate = None
    error = None
    try:
        attempt.claim()
        argv = checked_child_argv('--execute-reviewed-one-shot')
        attempt.write('intent.json',R.wire({'schema':'context-public-probe-observer-intent/v1',
                      'release_sha256':RELEASE_SHA,'argv':argv,
                      'retry_allowed':False}))
        process = spawn(argv,
                        stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,close_fds=True,
                        start_new_session=True)
        streams = capture_once(process,timeout)
        need(type(process.returncode) is int and process.returncode == 0 and
             streams[1] == b'' and streams[0] != b'',
             'EXTERNAL_RELEASE_EXIT_OR_STREAMS')
        terminal = read_file(R.ATTEMPT/'terminal.json',
                             json.loads(streams[0])['terminal_sha256'])
        output = read_file(R.OUTPUT,R.sha(R.REQUEST))
        cid = json.loads(terminal)['cid']
        gone = docker_call([R.DOCKER,'inspect','--type','container',cid])
        absent = docker_call([R.DOCKER,'ps','-a','--no-trunc','--filter',
                              f'name=^{R.NAME}$','--format','{{.ID}}'])
        mountinfo_raw = read_file(R.ATTEMPT/'child-mountinfo.txt',json.loads(terminal)['mountinfo_sha256'])
        policy_raw = read_file(R.POLICY_FILE,R.sha(R.POLICY_PUBLIC))
        candidate = join(process.returncode,*streams,terminal,output,gone,absent,mountinfo_raw,policy_raw)
    except BaseException as exc:
        error = exc
        if isinstance(exc,subprocess.TimeoutExpired):
            streams = (bytes(exc.output or b'')[:CAPTURE],
                       bytes(exc.stderr or b'')[:CAPTURE])
        elif isinstance(exc,CaptureUnknown):
            streams = exc.streams
    finally:
        if process is not None:
            try:
                if process.poll() is None:
                    error = error or Refused('EXTERNAL_PROCESS_UNREAPED')
                    os.killpg(process.pid,signal.SIGTERM)
                    process.wait(timeout=2)
            except BaseException as exc:
                error = error or exc
                try:
                    if process.poll() is None:
                        os.killpg(process.pid,signal.SIGKILL)
                        process.wait(timeout=2)
                except BaseException: pass
            for pipe in (process.stdout,process.stderr):
                try: pipe.close()
                except BaseException as exc: error = error or exc
        if attempt.claimed:
            try:
                attempt.write('stdout',streams[0])
                attempt.write('stderr',streams[1])
                attempt.write('observation.json',R.wire({
                    'schema':'context-public-only-probe-observer-record/v1',
                    'status':'PROVISIONAL_MATCH' if error is None else
                             'UNKNOWN_PRESERVE_NO_RETRY',
                    'candidate':candidate if error is None else None,
                    'error_class':None if error is None else type(error).__name__,
                    'error_detail':None if error is None else str(error)[:160],
                    'retry_allowed':False}))
            except BaseException as exc:
                error = error or exc
        try: attempt.close()
        except BaseException as exc: error = error or exc
    need(error is None and candidate is not None,'EXTERNAL_OBSERVER_UNKNOWN_NO_RETRY')
    expected = R.wire({'schema':'context-public-only-probe-observer-record/v1',
                       'status':'PROVISIONAL_MATCH','candidate':candidate,
                       'error_class':None,'error_detail':None,
                       'retry_allowed':False})
    raw = read_file(Path(observation_path)/'observation.json',R.sha(expected))
    need(raw == expected,'EXTERNAL_OBSERVATION_READBACK')
    return candidate


def execute():
    need(EFFECT_ENABLED is True,
         'EFFECT_DISABLED_PENDING_INDEPENDENT_STATIC_REVIEW')
    result = run_observer()
    print(json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__ == '__main__':
    if sys.argv[1:] == ['--execute-reviewed-one-shot']:
        execute()
    else:
        raise SystemExit('expected --execute-reviewed-one-shot')
