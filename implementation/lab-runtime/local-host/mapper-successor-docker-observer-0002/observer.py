"""Effect-disabled exact external OS observer for one Mapper Docker release."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
RELEASE_DIR = LOCAL/'mapper-successor-docker-release-0001'
RELEASE = RELEASE_DIR/'release.py'
RELEASE_FREEZE = RELEASE_DIR/'freeze.json'
RELEASE_REVIEW = LOCAL/'MAPPER-SUCCESSOR-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'
PREDECESSOR_REVIEW = LOCAL/'MAPPER-SUCCESSOR-DOCKER-OBSERVER-INDEPENDENT-STATIC-REVIEW-0001.md'
FREEZE_SHA = 'ce6356ef776c20d89286cc116c1750eeae6df9fb7a640e6dc545634c5b656452'
REVIEW_SHA = '816fa66234f9ac8ccb69ca6d4d1f1657ad3f0c80e4babe644385df3ab4e94ea8'
PREDECESSOR_HOLD_SHA = '494e9d4368c212b143cb8199537d6c6e233efc8cbb6b4d9a88efeeef0faf45e0'
RELEASE_SHA = 'cf85a26da6166e96855050ae0f511d22ff260ce4f807b9c67a077391b01bf927'
CONTROLLER_FREEZE_SHA = '4cac02ffa93511633ccdd45f2b0562069225f0e6e7530399ef88f5d2e692da2b'
CONTROLLER_REVIEW_SHA = '253503d80afaf0d6af0caa2411f38acc96d50fc8b54e70b85dc7efebd84c7bd9'
STAGE_REVIEW_SHA = 'bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406'
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt/docker-attempt')
NAME = 'cal-mapper-only-20261020-0002-successor-0001'
OBSERVATION = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-release-0001')
COMMAND = ['/usr/bin/python3','-B',str(RELEASE),'--execute-reviewed-one-shot']
PREFLIGHT = ['/usr/bin/python3','-B',str(RELEASE),'--preflight']
MAX_STREAM = 1024*1024
EFFECT_ENABLED = False
DIR_FLAGS = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
LEAF_FLAGS = os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK


class Refused(RuntimeError): pass


def need(ok,code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def parse(raw):
    def pairs(rows):
        value = {}
        for key,item in rows:
            need(key not in value,'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    try:
        value = json.loads(raw,object_pairs_hook=pairs,
                           parse_constant=lambda _x: (_ for _ in ()).throw(
                               Refused('NONFINITE_JSON')))
    except (ValueError,UnicodeError,RecursionError) as exc:
        raise Refused('INVALID_JSON') from exc
    need(type(value) is dict,'JSON_OBJECT')
    return value


def read_regular(path,*,digest=None,limit=2*1024*1024,mode=None):
    """Nofollow physical ancestry and stable owned regular leaf read."""
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts,'ABSOLUTE_PATH')
    fds = [os.open('/',DIR_FLAGS)]
    try:
        for part in path.parent.parts[1:]:
            fds.append(os.open(part,DIR_FLAGS,dir_fd=fds[-1]))
        for fd in fds:
            st = os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'UNTRUSTED_ANCESTOR')
        parent = fds[-1]
        before = os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and 0 < before.st_size <= limit and
             (mode is None or stat.S_IMODE(before.st_mode) == mode) and
             not(before.st_mode & 0o022),'LEAF_SHAPE')
        leaf = os.open(path.name,LEAF_FLAGS,dir_fd=parent)
        fds.append(leaf)
        opening = os.fstat(leaf)
        ident = lambda st:(st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,
                           st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
        need(ident(opening) == ident(before),'LEAF_OPEN_DRIFT')
        chunks = []
        remaining = before.st_size+1
        while remaining:
            block = os.read(leaf,min(65536,remaining))
            if not block: break
            chunks.append(block)
            remaining -= len(block)
        raw = b''.join(chunks)
        after = os.fstat(leaf)
        named = os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(len(raw) == before.st_size and ident(after) == ident(before) == ident(named) and
             (digest is None or sha(raw) == digest),'LEAF_DRIFT')
        return raw
    finally:
        close_all(fds,sys.exception())


def basis():
    freeze = parse(read_regular(RELEASE_FREEZE,digest=FREEZE_SHA,limit=65536))
    review = read_regular(RELEASE_REVIEW,digest=REVIEW_SHA,limit=262144)
    hold = read_regular(PREDECESSOR_REVIEW,digest=PREDECESSOR_HOLD_SHA,
                        limit=262144)
    need(b'**Verdict: HOLD.**' in hold and b'R01' in hold and b'R02' in hold and
         b'R03' in hold,'PREDECESSOR_FINDINGS')
    need(b'**Verdict: PASS for the frozen release design;' in review and
         FREEZE_SHA.encode() in review,'INDEPENDENT_RELEASE_REVIEW')
    need(freeze == {
        'schema':'lab-mapper-successor-docker-one-shot-release-freeze/v1',
        'status':'READY_FOR_INDEPENDENT_STATIC_REVIEW_NO_EFFECT_YET',
        'effect':'NOT_RUN','effect_enabled':True,
        'attempt':str(ATTEMPT),'container_name':NAME,'no_retry':True,
        'controller_freeze_sha256':CONTROLLER_FREEZE_SHA,
        'controller_review_sha256':CONTROLLER_REVIEW_SHA,
        'stage_effect_review_sha256':STAGE_REVIEW_SHA,
        'external_exit_and_independent_effect_review_required':True,
        'normal_tests':6,'optimized_tests':6,
        'file_bindings':freeze.get('file_bindings')},'RELEASE_FREEZE_CONTRACT')
    rows = freeze['file_bindings']
    need(type(rows) is list and len(rows) == 3,'RELEASE_BINDINGS')
    expected_names = ('release.py','tests.py','HANDOFF.md')
    for row,name in zip(rows,expected_names):
        path = RELEASE_DIR/name
        need(type(row) is dict and row.get('path') == str(path.relative_to(REPO)) and
             type(row.get('size')) is int and 0 < row['size'] <= 2*1024*1024 and
             type(row.get('sha256')) is str and len(row['sha256']) == 64,
             'RELEASE_BINDING_ROW')
        raw = read_regular(path,digest=row['sha256'],limit=row['size'])
        need(len(raw) == row['size'],'RELEASE_BINDING_SIZE')
    need(rows[0]['sha256'] == RELEASE_SHA,'EXACT_RELEASE_ENTRYPOINT')
    return {'freeze_sha256':FREEZE_SHA,'review_sha256':REVIEW_SHA,
            'release_sha256':RELEASE_SHA,'attempt':str(ATTEMPT),'name':NAME}


def run_command(argv,timeout=60):
    return subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=timeout,check=False,
                          close_fds=True)


def preflight(runner=run_command):
    selected = basis()
    need(not os.path.lexists(OBSERVATION),'OBSERVER_ATTEMPT_CONSUMED')
    parent_fds = open_parent(OBSERVATION)
    try:
        p = os.fstat(parent_fds[-1])
        need(p.st_uid == os.getuid() and stat.S_IMODE(p.st_mode) == 0o700,
             'OBSERVER_PARENT_OWNER_0700')
    finally:
        close_all(parent_fds)
    result = runner(PREFLIGHT)
    need(type(result.returncode) is int and result.returncode == 0 and
         result.stderr == b'' and 0 < len(result.stdout) <= MAX_STREAM,
         'RELEASE_PREFLIGHT_OS')
    value = parse(result.stdout)
    need(value['schema'] == 'lab-mapper-successor-docker-release-predispatch/v1' and
         value['status'] == 'READY_FOR_INDEPENDENT_RELEASE_REVIEW_NO_EFFECT_YET' and
         value['effect'] == 'NOT_RUN' and value['attempt'] == str(ATTEMPT) and
         value['container_name'] == NAME and value['no_retry'] is True and
         value['stage_effect_review_sha256'] == STAGE_REVIEW_SHA and
         value['controller_freeze_sha256'] == CONTROLLER_FREEZE_SHA and
         value['controller_review_sha256'] == CONTROLLER_REVIEW_SHA and
         value['controller_preflight']['effect'] == 'NOT_RUN' and
         value['controller_preflight']['no_retry'] is True,
         'RELEASE_PREFLIGHT_JOIN')
    return {'schema':'lab-mapper-successor-docker-observer-predispatch/v1',
            'status':'READY_FOR_INDEPENDENT_OBSERVER_REVIEW_NO_EFFECT_YET',
            'effect':'NOT_RUN','observation':str(OBSERVATION),
            'release':selected,'preflight_stdout_sha256':sha(result.stdout),
            'preflight_stdout':result.stdout}


def open_parent(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts,'OBS_PARENT_PATH')
    fds = [os.open('/',DIR_FLAGS)]
    try:
        for part in path.parent.parts[1:]:
            fds.append(os.open(part,DIR_FLAGS,dir_fd=fds[-1]))
        for fd in fds:
            st = os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'OBS_PARENT_CUSTODY')
        return fds
    except BaseException:
        close_all(fds)
        raise


def close_all(fds,primary=None):
    """Close each owned number once, independently of every other close."""
    errors = []
    for fd in reversed(list(fds)):
        try: os.close(fd)
        except BaseException as exc: errors.append(exc)
    if primary is not None:
        for exc in errors:
            primary.add_note('owned descriptor cleanup: '+type(exc).__name__)
        return
    if errors:
        first = errors[0]
        for exc in errors[1:]:
            first.add_note('additional owned descriptor cleanup: '+type(exc).__name__)
        raise first


def close_streams(ledger):
    """Pop ownership before fsync/close; never reuse an ambiguous number."""
    errors = []
    while ledger:
        fd = ledger.pop(0)
        try: os.fsync(fd)
        except BaseException as exc: errors.append(exc)
        try: os.close(fd)
        except BaseException as exc: errors.append(exc)
    if errors:
        first = errors[0]
        for exc in errors[1:]:
            first.add_note('additional stream finalization: '+type(exc).__name__)
        raise first


def write_all(fd,raw):
    view = memoryview(raw)
    while view:
        count = os.write(fd,view)
        need(count > 0,'SHORT_WRITE')
        view = view[count:]


class Observation:
    def __init__(self,path=OBSERVATION):
        self.path = Path(path)
        self.parents = []
        self.fd = None
        self.claimed = False
        self.identity = None

    def claim(self):
        self.parents = open_parent(self.path)
        parent = self.parents[-1]
        need(os.fstat(parent).st_uid == os.getuid() and
             stat.S_IMODE(os.fstat(parent).st_mode) == 0o700,
             'OBS_PARENT_0700')
        os.mkdir(self.path.name,0o700,dir_fd=parent)
        self.claimed = True
        self.fd = os.open(self.path.name,DIR_FLAGS,dir_fd=parent)
        os.fchmod(self.fd,0o700)
        os.fsync(self.fd)
        os.fsync(parent)
        st = os.fstat(self.fd)
        self.identity = (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid)
        self.attached()
        self.write('consumed.json',wire({
            'schema':'lab-mapper-successor-docker-observer-consumed/v1',
            'status':'CONSUMED_UNKNOWN_UNTIL_OS_REAPED','observation':str(self.path),
            'attempt':str(ATTEMPT),'container_name':NAME,'no_retry':True}))

    def attached(self):
        need(self.claimed and self.fd is not None,'OBS_NOT_CLAIMED')
        st = os.fstat(self.fd)
        named = os.stat(self.path.name,dir_fd=self.parents[-1],follow_symlinks=False)
        identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid)
        need(identity(st) == identity(named) == self.identity,'OBS_DETACHED')
        fresh = open_parent(self.path)
        try:
            need(identity(os.fstat(fresh[-1])) ==
                 identity(os.fstat(self.parents[-1])),'OBS_PARENT_DETACHED')
        finally:
            close_all(fresh)

    def write(self,name,raw):
        self.attached()
        need(name and '/' not in name and name not in ('.','..') and
             len(raw) <= 2*1024*1024,'OBS_LEAF')
        fd = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|
                     os.O_CLOEXEC,0o600,dir_fd=self.fd)
        try:
            write_all(fd,raw)
            os.fchmod(fd,0o600)
            os.fsync(fd)
            st = os.fstat(fd)
            need(stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid() and
                 stat.S_IMODE(st.st_mode) == 0o600 and st.st_size == len(raw),
                 'OBS_WRITTEN_SHAPE')
        finally:
            close_all([fd],sys.exception())
        os.fsync(self.fd)
        self.attached()
        return sha(raw)

    def create_stream(self,name):
        self.attached()
        fd = None
        try:
            fd = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|
                         os.O_CLOEXEC,0o600,dir_fd=self.fd)
            os.fchmod(fd,0o600)
            os.fsync(self.fd)
            return fd
        except BaseException as primary:
            if fd is not None: close_all([fd],primary)
            raise

    def close(self):
        fds = ([self.fd] if self.fd is not None else [])+list(reversed(self.parents))
        error = None
        for fd in fds:
            try: os.close(fd)
            except BaseException as exc: error = error or exc
        self.fd = None
        self.parents = []
        if error is not None: raise error


def postclose_write(path,identity,name,raw):
    """Publish a success leaf only after all earlier held descriptors closed."""
    parents = open_parent(path)
    directory = None
    leaf = None
    try:
        directory = os.open(Path(path).name,DIR_FLAGS,dir_fd=parents[-1])
        st = os.fstat(directory)
        named = os.stat(Path(path).name,dir_fd=parents[-1],follow_symlinks=False)
        key = lambda item:(item.st_dev,item.st_ino,item.st_mode,item.st_uid,item.st_gid)
        need(key(st) == key(named) == identity and
             stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700,
             'POSTCLOSE_ROOT_DRIFT')
        leaf = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|
                       os.O_CLOEXEC,0o600,dir_fd=directory)
        write_all(leaf,raw)
        os.fchmod(leaf,0o600)
        os.fsync(leaf)
        done = os.fstat(leaf)
        need(stat.S_ISREG(done.st_mode) and done.st_uid == os.getuid() and
             stat.S_IMODE(done.st_mode) == 0o600 and done.st_size == len(raw),
             'POSTCLOSE_LEAF_SHAPE')
        os.fsync(directory)
        again = os.stat(Path(path).name,dir_fd=parents[-1],follow_symlinks=False)
        need(key(again) == identity,'POSTCLOSE_ROOT_DETACHED')
    finally:
        close_all(parents + ([directory] if directory is not None else []) +
                  ([leaf] if leaf is not None else []),sys.exception())


def read_final(path=ATTEMPT/'evidence/final.json'):
    return read_regular(path,limit=MAX_STREAM,mode=0o600)


def read_terminal(path=ATTEMPT/'evidence/terminal.json'):
    return read_regular(path,limit=65536,mode=0o600)


def strict_final_join(stdout,final_raw,terminal_raw):
    value = parse(stdout)
    final = parse(final_raw)
    terminal = parse(terminal_raw)
    output = final.get('output')
    need(stdout == (json.dumps(value,sort_keys=True,allow_nan=False)+'\n').encode() and
         final_raw == wire(final) and value == final and
         final['schema'] == 'lab-mapper-successor-docker-final/v1' and
         final['overall'] == 'OBSERVED_DOCKER_ONLY' and
         final['attempt'] == str(ATTEMPT) and
         final['stage_effect_review_sha256'] == STAGE_REVIEW_SHA and
         final['no_retry'] is True and
         final['authority_effect'] == 'none' and
         final['actual_owner_outcome'] is None and
         final['original_task_acceptance'] is False and
         final['requires_external_exit_zero_and_independent_effect_review'] is True and
         terminal_raw == (json.dumps(terminal,sort_keys=True,
                                     allow_nan=False)+'\n').encode() and
         final['terminal_sha256'] == sha(terminal_raw) and
         terminal['schema_version'] == 'lab-mapper-docker-one-shot-evidence/v2' and
         terminal['name'] == NAME and terminal['phase'] == 'TERMINAL' and
         terminal['overall'] == 'PASS' and terminal['cleanup'] == 'PASS' and
         terminal['container_absent'] is True and
         terminal['create_attempted'] is True and
         type(terminal['client_exit']) is int and terminal['client_exit'] == 0 and
         type(terminal['daemon_exit']) is int and terminal['daemon_exit'] == 0 and
         terminal['daemon_exit_consistent'] is True and
         type(terminal['container_id']) is str and
         re.fullmatch(r'[0-9a-f]{64}',terminal['container_id']) is not None and
         type(output) is dict and
         output['schema'] == 'lab-mapper-successor-output-verification/v1' and
         output['result'] == 'PASS_CANDIDATE_OUTPUT_ONLY' and
         type(output['manifest_sha256']) is str and
         len(output['manifest_sha256']) == 64 and
         output['files'] == 55 and output['semantic_leaves'] == 25 and
         output['governance_leaves'] == 25 and
         output['exact_governance_joins'] == 25 and
         output['authority_effect'] == 'none' and
         output['actual_owner_outcome'] is None and output['task_complete'] is False,
         'RELEASE_STDOUT_FINAL_JOIN')
    return sha(final_raw)


def capture_process(process,stdout_fd,stderr_fd,interrupted,*,limit=MAX_STREAM):
    """Drain to durable raw files until child exits/reaps; never kill on signal."""
    need(type(limit) is int and 0 < limit <= MAX_STREAM,'CAPTURE_LIMIT')
    counts = [0,0]
    retained = [0,0]
    digests = [hashlib.sha256(),hashlib.sha256()]
    overflow = False
    error_class = None
    pipe_tail_timeout = False
    child_exited_at = None
    with selectors.DefaultSelector() as selector:
        for i,pipe in enumerate((process.stdout,process.stderr)):
            need(pipe is not None,'CHILD_PIPE')
            os.set_blocking(pipe.fileno(),False)
            selector.register(pipe,selectors.EVENT_READ,i)
        while selector.get_map():
            for key,_ in selector.select(1.0):
                i = key.data
                try: raw = os.read(key.fileobj.fileno(),65536)
                except BlockingIOError: continue
                except OSError as exc:
                    error_class = type(exc).__name__
                    selector.unregister(key.fileobj)
                    continue
                if not raw:
                    selector.unregister(key.fileobj)
                    continue
                counts[i] += len(raw)
                room = max(0,limit-retained[i])
                held = raw[:room]
                if held:
                    try:
                        write_all((stdout_fd,stderr_fd)[i],held)
                        digests[i].update(held)
                        retained[i] += len(held)
                    except (OSError,Refused) as exc:
                        error_class = type(exc).__name__
                if len(raw) > room: overflow = True
            # Reap the direct child and allow a bounded tail for inherited pipes.
            # A signal only marks UNKNOWN; it never cancels the launched child.
            if interrupted['signals'] and process.poll() is None:
                interrupted['child_preserved_after_signal'] = True
            if process.poll() is not None:
                child_exited_at = child_exited_at or time.monotonic()
                if time.monotonic() - child_exited_at > 10:
                    pipe_tail_timeout = True
                    break
    exit_code = process.wait()
    need(type(exit_code) is int,'STRICT_OS_EXIT_UNAVAILABLE')
    return {'exit_code':exit_code,'counts':counts,'retained':retained,
            'stdout_sha256':digests[0].hexdigest(),
            'stderr_sha256':digests[1].hexdigest(),
            'overflow':overflow,'capture_error_class':error_class,
            'pipe_tail_timeout':pipe_tail_timeout,
            'signals':list(interrupted['signals']),
            'child_preserved_after_signal':interrupted['child_preserved_after_signal']}


def _run_once(*,observation=OBSERVATION,preflight_fn=preflight,spawn=subprocess.Popen,
              final_reader=read_final,terminal_reader=read_terminal):
    selected = preflight_fn()
    need(selected['effect'] == 'NOT_RUN' and
         selected['release']['freeze_sha256'] == FREEZE_SHA and
         selected['release']['review_sha256'] == REVIEW_SHA and
         selected['release']['release_sha256'] == RELEASE_SHA,
         'SAME_STATE_PREFLIGHT')
    owned = Observation(observation)
    process = None
    stream_fds = []
    interrupted = {'signals':[],'child_preserved_after_signal':False}
    old = {}
    def on_signal(signum,_frame): interrupted['signals'].append(signum)
    provisional = None
    fault = None
    capture = None
    try:
        owned.claim()
        owned.write('intent.json',wire({
            'schema':'lab-mapper-successor-docker-observer-intent/v1',
            'status':'CONSUMED_UNKNOWN_UNTIL_OS_REAPED',
            'argv':COMMAND,'release_freeze_sha256':FREEZE_SHA,
            'release_review_sha256':REVIEW_SHA,'release_entrypoint_sha256':RELEASE_SHA,
            'release_preflight_stdout_sha256':selected['preflight_stdout_sha256'],
            'attempt':str(ATTEMPT),'container_name':NAME,'no_retry':True}))
        stdout_fd = owned.create_stream('stdout')
        stream_fds.append(stdout_fd)
        stderr_fd = owned.create_stream('stderr')
        stream_fds.append(stderr_fd)
        for signum in (signal.SIGINT,signal.SIGTERM):
            old[signum] = signal.signal(signum,on_signal)
        process = spawn(COMMAND,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,close_fds=True,start_new_session=True)
        capture = capture_process(process,stdout_fd,stderr_fd,interrupted)
        close_streams(stream_fds)
        if (capture['exit_code'] == 0 and capture['counts'][1] == 0 and
            capture['overflow'] is False and capture['capture_error_class'] is None and
            capture['pipe_tail_timeout'] is False and
            not capture['signals']):
            stdout_raw = read_regular(Path(observation)/'stdout',
                                      limit=MAX_STREAM,mode=0o600)
            need(sha(stdout_raw) == capture['stdout_sha256'] and
                 len(stdout_raw) == capture['counts'][0],
                 'RAW_STDOUT_READBACK')
            final_sha = strict_final_join(stdout_raw,final_reader(),terminal_reader())
            provisional = {'schema':'lab-mapper-successor-docker-external-observation/v1',
                           'status':'PROVISIONAL_OS_ZERO_FINAL_JOIN',
                           'release_os_exit':0,'stdout_sha256':capture['stdout_sha256'],
                           'stderr_sha256':capture['stderr_sha256'],
                           'final_sha256':final_sha,'attempt':str(ATTEMPT),
                           'container_name':NAME,'no_retry':True,
                           'independent_effect_review':'PENDING'}
    except BaseException as exc:
        fault = exc
    finally:
        # Never cancel or abandon a launched child because of an interruption.
        if process is not None and process.poll() is None:
            try:
                if len(stream_fds) == 2:
                    capture = capture_process(process,*stream_fds,interrupted)
                else:
                    process.wait()
            except BaseException as exc:
                fault = fault or exc
        for signum,handler in old.items():
            signal.signal(signum,handler)
        for pipe in (() if process is None else (process.stdout,process.stderr)):
            try: pipe.close()
            except BaseException as exc: fault = fault or exc
        try: close_streams(stream_fds)
        except BaseException as exc: fault = fault or exc
        if owned.claimed:
            record = {'schema':'lab-mapper-successor-docker-observer-record/v1',
                      'status':'REAPED_PENDING_POSTCLOSE' if
                      fault is None and provisional is not None else
                      'UNKNOWN_PRESERVE_NO_RETRY',
                      'candidate':provisional if fault is None else None,
                      'capture':capture,'error_class':None if fault is None else
                      type(fault).__name__,'no_retry':True}
            try: owned.write('capture.json',wire(record))
            except BaseException as exc: fault = fault or exc
        try: owned.close()
        except BaseException as exc: fault = fault or exc
    need(fault is None and provisional is not None,'MAPPER_EXTERNAL_OBSERVER_UNKNOWN')
    postclose_write(observation,owned.identity,'observation.json',wire({
        'schema':'lab-mapper-successor-docker-observer-complete/v1',
        'status':'PROVISIONAL_OS_ZERO_FINAL_JOIN','candidate':provisional,
        'capture':capture,'no_retry':True,
        'independent_effect_review':'PENDING'}))
    observed = read_regular(Path(observation)/'observation.json',mode=0o600)
    need(parse(observed)['status'] == 'PROVISIONAL_OS_ZERO_FINAL_JOIN' and
         parse(observed)['candidate'] == provisional,
         'POSTCLOSE_OBSERVATION_READBACK')
    return {'status':'PROVISIONAL_OS_ZERO_FINAL_JOIN',
            'observation_sha256':sha(observed),'stdout_sha256':capture['stdout_sha256'],
            'stderr_sha256':capture['stderr_sha256'],'release_os_exit':0,
            'attempt':str(ATTEMPT),'observer_attempt':str(observation),
            'no_retry':True,'independent_effect_review':'PENDING'}


def execute():
    need(EFFECT_ENABLED is True,'EFFECT_DISABLED_PENDING_INDEPENDENT_STATIC_REVIEW')
    result = _run_once()
    print(json.dumps(result,sort_keys=True))
    return result


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        value = preflight()
        # Never print raw child or protected body; preflight stdout is metadata.
        print(json.dumps({k:v for k,v in value.items() if k != 'preflight_stdout'},
                         sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        execute()
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
