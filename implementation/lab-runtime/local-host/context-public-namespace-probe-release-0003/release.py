"""Effect-disabled successor PUBLIC-ONLY Context namespace probe."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import stat
import struct
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
CONTROLLER = LOCAL / 'context-successor-controller-path-0001/controller_path.py'
CONTROLLER_FREEZE = LOCAL / 'context-successor-controller-path-0001/freeze.json'
CONTROLLER_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-CONTROLLER-PATH-INDEPENDENT-STATIC-REVIEW-0001.md'
MOUNT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-MOUNT-RECONCILE-INDEPENDENT-STATIC-REVIEW-0001.md'
PREVIOUS_FREEZE = LOCAL / 'context-public-namespace-probe-release-0002/freeze.json'
PREVIOUS_REVIEW = LOCAL / 'CONTEXT-PUBLIC-NAMESPACE-PROBE-INDEPENDENT-STATIC-REVIEW-0002.md'
FAILED_EFFECT_REVIEW = LOCAL / 'context-public-namespace-probe-effect-independent-effect-review-0002/REVIEW.md'
FAILED_EFFECT_RECORD = LOCAL / 'context-public-namespace-probe-effect-independent-effect-review-0002/review.json'
CHILD = HERE / 'probe_child.py'
PINS = {
    CONTROLLER:'556bf30f0cbc10c259a1f731b8b2ca44ec9dfe76592457f5f5fe8a35ec6ba9a7',
    CONTROLLER_FREEZE:'7182cc196fe9a95ebb88d95cb6aea98bb11787fefc2210b6c54a439d8917c480',
    CONTROLLER_REVIEW:'499d7789cc72361cd27b057a36c9c8088944d1f8d112473ab6966ef89d87cb99',
    MOUNT_REVIEW:'f36d04e545dfa0e5a9028de9313d805b0c5fcd20e643f7b1d44f77cbb60eb7c2',
    PREVIOUS_FREEZE:'d16e9826ee9eb34aa2353b389e2a445772d0b1f8fba14e980418811cfb987068',
    PREVIOUS_REVIEW:'1548a2b439726af681a2020c2d83e19215ce72bd6852f2cbf58979469f296afc',
    FAILED_EFFECT_REVIEW:'31e081d42b94870a0f028dcf0630a6e4655eba3a04c06ee505496e6c4a43f03f',
    FAILED_EFFECT_RECORD:'839aeca6fc3d7c61b3affd4b452af185c13e920544bc6bbc4f650223f82d9640',
    CHILD:'34dd54aafa8abc421dc2810c4dc2a699b696301f7132909e642ee3d7658b1242',
}
DOCKER = '/usr/bin/docker'
DOCKER_SHA = '999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME = 'cal-context-public-only-probe-20261020-0003'
PARENT = Path('/home/vlad_/.local/state/cyberalchemy-lab')
ATTEMPT = PARENT / 'context-public-only-probe-20261020-0003'
ROLE = 'probe/public-only'
OUTPUT = ATTEMPT / 'stage' / ROLE / 'packages/0001/request.json'
REQUEST = b'{"public_probe":true,"ordinal":1}\n'
NATIVE_PLACEHOLDER = b'public-only probe placeholder; never executed\n'
EFFECT_ENABLED = False
FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
LEAF = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


class Refused(RuntimeError):
    pass


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       allow_nan=False) + '\n').encode()


def check_file(path, digest, max_size=2*1024*1024):
    fd = os.open(path, LEAF)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= max_size, 'PIN_SHAPE')
        chunks = []
        remaining = before.st_size+1
        while remaining:
            block = os.read(fd,min(1024*1024,remaining))
            if not block: break
            chunks.append(block)
            remaining -= len(block)
        raw = b''.join(chunks)
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev,before.st_ino,before.st_mode,before.st_size) ==
             (after.st_dev,after.st_ino,after.st_mode,after.st_size) and
             sha(raw) == digest, 'PIN_DRIFT')
        return raw
    finally:
        os.close(fd)


def basis(now=None):
    for path,digest in PINS.items():
        check_file(path,digest)
    failed = check_file(FAILED_EFFECT_REVIEW,PINS[FAILED_EFFECT_REVIEW])
    record = json.loads(check_file(FAILED_EFFECT_RECORD,PINS[FAILED_EFFECT_RECORD]))
    need(b'**Verdict: UNKNOWN, consumed, no retry.**' in failed and
         b'DIR_MODE_OR_OWNER' in failed and b'fresh' in failed and
         record['verdict'] == 'UNKNOWN_CONSUMED_NO_RETRY' and
         record['cause']['retained_code'] == 'DIR_MODE_OR_OWNER' and
         record['effect_success'] is False and record['no_retry'] is True,
         'FAILED_PREDECESSOR_EFFECT_REVIEW')
    freeze = json.loads(check_file(CONTROLLER_FREEZE,PINS[CONTROLLER_FREEZE]))
    need(freeze['effect_enabled'] is False and freeze['namespace_probe'] == 'UNRUN' and
         freeze['bindings']['controller_path.py'] == PINS[CONTROLLER] and
         freeze['bindings']['public_probe_child.py'] ==
         'be375306ec1b88ae2338161014e809fbac1f586334f9d0b8a22d83bc6779d7d6' and
         freeze['bindings']['public_probe_child.py'] != PINS[CHILD],
         'CONTROLLER_SELECTION')
    spec = importlib.util.spec_from_file_location('reviewed_context_public_probe_plan',CONTROLLER)
    need(spec is not None and spec.loader is not None,'CONTROLLER_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    selected = module.probe_argv('a'*32,now)
    need(module.EFFECT_ENABLED is False and selected['effect_enabled'] is False and
         selected['docker_invoked'] is False and selected['create_argv'].count('--mount') == 5,
         'REVIEWED_INERT_CONTROLLER')
    return module, selected


def projection(token, now=None):
    module, selected = basis(now)
    need(type(token) is str and len(token) == 32 and
         all(c in '0123456789abcdef' for c in token),'TOKEN')
    original = module.probe_argv(token,now)['create_argv']
    planned = module.plan(now)
    targets = ['/workspace','/control','/runner','/cache-disabled',
               '/attempt/input/lab-context-native-reader']
    sources = [ATTEMPT/'stage',ATTEMPT/'control',ATTEMPT/'runner-code',
               ATTEMPT/'cache-guard',ATTEMPT/'native/lab-context-native-reader']
    need([row['target'] for row in planned['mounts']] == targets and
         all(row['read_only'] is True for row in planned['mounts']) and
         ATTEMPT != Path(planned['path_adaptation']['public_stage_root']) and
         not str(ATTEMPT).startswith(str(module.LOCAL)) and
         ROLE != planned['path_adaptation']['logical_context_here'].removeprefix('/workspace/'),
         'DISPOSABLE_PUBLIC_PROJECTION')
    command = list(original)
    command[command.index('--name')+1] = NAME
    for i,target in enumerate(targets):
        old = f"type=bind,src={planned['mounts'][i]['source']},dst={target},readonly"
        new = f'type=bind,src={sources[i]},dst={target},readonly'
        need(command.count(old) == 1,'SOURCE_VECTOR_DRIFT')
        command[command.index(old)] = new
    need(command[-2] == module.PINS[module.CHILD],'ORIGINAL_CHILD_PIN_DRIFT')
    command[-2] = PINS[CHILD]
    need(command.count('--mount') == 5 and
         all(command[i+1].endswith(',readonly') for i,v in enumerate(command)
             if v == '--mount') and
         not any('dst=/workspace/' in v for v in command) and
         [command[i+1] for i,v in enumerate(command) if v == '--mount'] ==
         [f'type=bind,src={s},dst={t},readonly' for s,t in zip(sources,targets)],
         'PUBLIC_ONLY_FIVE_RO_BINDS')
    return {'schema':'context-public-only-probe-projection/v1',
            'status':'INERT_EXACT_DISPOSABLE_PROJECTION','effect_enabled':False,
            'attempt':str(ATTEMPT),'name':NAME,'image':IMAGE,
            'create_argv':command,'mounts':[
                {'source':str(s),'target':t,'read_only':True}
                for s,t in zip(sources,targets)],
            'role':ROLE,'request_sha256':sha(REQUEST),
            'original_context_stage_touched':False,
            'authority_or_private_touched':False}


def open_chain(path):
    """Physical nofollow traversal through trusted root/current-UID ancestors."""
    path = Path(path)
    need(path.is_absolute() and all(x not in ('.','..') for x in path.parts),
         'ABSOLUTE_CHAIN')
    fds = [os.open('/',FLAGS)]
    try:
        for component in path.parts[1:]:
            fds.append(os.open(component,FLAGS,dir_fd=fds[-1]))
        ids = []
        for fd in fds:
            st = os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'UNTRUSTED_ANCESTOR')
            ids.append((st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid))
        for n in range(1,len(fds)):
            st = os.stat(path.parts[n],dir_fd=fds[n-1],follow_symlinks=False)
            need((st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid) == ids[n],
                 'ANCESTOR_REATTACH')
        return fds
    except BaseException:
        for fd in reversed(fds):
            os.close(fd)
        raise


def close_all(fds):
    error = None
    for fd in reversed(fds):
        try: os.close(fd)
        except BaseException as exc: error = error or exc
    if error is not None:
        raise error


def write_file(parent_fd, name, raw, mode=0o600):
    need('/' not in name and name not in ('.','..') and len(raw) <= 65536,
         'LEAF_SHAPE')
    fd = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,
                 mode,dir_fd=parent_fd)
    try:
        view = memoryview(raw)
        while view:
            n = os.write(fd,view)
            need(n > 0,'SHORT_WRITE')
            view = view[n:]
        os.fchmod(fd,mode)
        os.fsync(fd)
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
             st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == mode and
             st.st_size == len(raw),'WRITTEN_LEAF_SHAPE')
    finally:
        os.close(fd)
    os.fsync(parent_fd)
    rd = os.open(name,LEAF,dir_fd=parent_fd)
    try:
        need(sha(os.read(rd,len(raw)+1)) == sha(raw),'LEAF_READBACK')
    finally:
        os.close(rd)
    return sha(raw)


class Attempt:
    def __init__(self, path=ATTEMPT):
        self.path = Path(path)
        self.ancestors = []
        self.fd = None
        self.claimed = False
        self.identity = None

    def claim(self):
        self.ancestors = open_chain(self.path.parent)
        parent = self.ancestors[-1]
        need(stat.S_IMODE(os.fstat(parent).st_mode) == 0o700 and
             os.fstat(parent).st_uid == os.getuid(),'OWNER_PRIVATE_PARENT')
        os.mkdir(self.path.name,0o700,dir_fd=parent)
        self.claimed = True  # successful exclusive mkdir consumes the attempt
        self.fd = os.open(self.path.name,FLAGS,dir_fd=parent)
        os.fchmod(self.fd,0o700)
        os.fsync(self.fd)
        os.fsync(parent)
        st = os.fstat(self.fd)
        self.identity = (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid)
        self.attached()
        write_file(self.fd,'consumed.json',wire({
            'schema':'context-public-only-probe-consumed/v1',
            'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW',
            'name':NAME,'attempt':str(self.path),'retry_allowed':False}))

    def attached(self):
        need(self.claimed and self.fd is not None,'UNCLAIMED_ATTEMPT')
        st = os.fstat(self.fd)
        named = os.stat(self.path.name,dir_fd=self.ancestors[-1],follow_symlinks=False)
        current = (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid)
        other = (named.st_dev,named.st_ino,named.st_mode,named.st_uid,named.st_gid)
        need(current == self.identity == other,'ATTEMPT_DETACHED')
        fresh = open_chain(self.path.parent)
        try:
            need((os.fstat(fresh[-1]).st_dev,os.fstat(fresh[-1]).st_ino) ==
                 (os.fstat(self.ancestors[-1]).st_dev,os.fstat(self.ancestors[-1]).st_ino),
                 'PARENT_DETACHED')
        finally:
            close_all(fresh)

    def mkdir(self, relative, mode=0o755):
        self.attached()
        parts = relative.split('/')
        need(parts and all(p and p not in ('.','..') for p in parts),'RELATIVE_DIR')
        fd = os.dup(self.fd)
        try:
            for part in parts:
                created = False
                try:
                    os.mkdir(part,mode,dir_fd=fd)
                    created = True
                except FileExistsError:
                    pass
                child = os.open(part,FLAGS,dir_fd=fd)
                try:
                    identity = lambda value:(value.st_dev,value.st_ino,
                        value.st_mode,value.st_uid,value.st_gid)
                    opening = os.fstat(child)
                    opening_named = os.stat(part,dir_fd=fd,follow_symlinks=False)
                    need(identity(opening) == identity(opening_named) and
                         opening.st_uid == os.getuid() and
                         stat.S_ISDIR(opening.st_mode),'DIR_OWNER_OR_ATTACH')
                    if created:
                        # mkdir's mode is filtered by inherited umask. Set and
                        # durably read back the selected exact mode through the
                        # held nofollow directory descriptor before contents.
                        # Establish owner/attachment before changing mode;
                        # pre-existing entries are never chmodded.
                        os.fchmod(child,mode)
                        os.fsync(child)
                    st = os.fstat(child)
                    named = os.stat(part,dir_fd=fd,follow_symlinks=False)
                    need(identity(st) == identity(named) and
                         (st.st_dev,st.st_ino) ==
                         (opening.st_dev,opening.st_ino) and
                         st.st_uid == os.getuid() and
                         stat.S_IMODE(st.st_mode) == mode and
                         stat.S_ISDIR(st.st_mode),'DIR_MODE_OR_OWNER')
                    os.fsync(fd)
                except BaseException:
                    os.close(child)
                    raise
                old = fd
                fd = child  # transfer ownership before ambiguous old close
                os.close(old)
        finally:
            os.close(fd)
        self.attached()

    def write(self, relative, raw, mode=0o600):
        self.attached()
        parts = relative.split('/')
        need(len(parts) >= 1 and all(p and p not in ('.','..') for p in parts),
             'RELATIVE_LEAF')
        fd = os.dup(self.fd)
        try:
            for part in parts[:-1]:
                child = os.open(part,FLAGS,dir_fd=fd)
                os.close(fd)
                fd = child
            result = write_file(fd,parts[-1],raw,mode)
        finally:
            os.close(fd)
        self.attached()
        return result

    def close(self):
        errors = []
        for fd in [self.fd] + list(reversed(self.ancestors)):
            if fd is not None:
                try: os.close(fd)
                except BaseException as exc: errors.append(exc)
        self.fd = None
        self.ancestors = []
        if errors: raise errors[0]


def docker_call(argv, timeout=10):
    result = subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,timeout=timeout,check=False)
    need(len(result.stdout) <= 65536 and len(result.stderr) <= 65536,
         'DOCKER_STREAM_BOUND')
    return result


def host_preflight(runner=docker_call):
    check_file(Path(DOCKER),DOCKER_SHA,64*1024*1024)
    image = runner([DOCKER,'image','inspect',IMAGE,
                    '--format','{{.Id}} {{.Architecture}}'])
    need(image.returncode == 0 and image.stderr == b'' and
         image.stdout == f'{IMAGE} amd64\n'.encode(),'IMAGE_ID_ARCH')
    name = runner([DOCKER,'ps','-a','--no-trunc','--filter',f'name=^{NAME}$',
                   '--format','{{.ID}}'])
    need(name.returncode == 0 and name.stdout == b'' and name.stderr == b'',
         'NAME_ALREADY_OCCUPIED')
    need(not os.path.lexists(ATTEMPT),'ATTEMPT_ALREADY_CONSUMED')
    return {'image':IMAGE,'docker_sha256':DOCKER_SHA,'name_absent':True,
            'attempt_absent':True}


def preflight(now=None, host=False):
    result = projection('a'*32,now)
    if host:
        result['host'] = host_preflight()
    return result


def send(sock,value):
    raw = wire(value)
    need(len(raw) <= 4096,'PACKET_BOUND')
    need(sock.send(raw) == len(raw),'SHORT_PACKET')


def recv(sock):
    raw = sock.recv(4097)
    need(0 < len(raw) <= 4096 and raw.endswith(b'\n'),'PACKET_BOUND')
    value = json.loads(raw)
    need(type(value) is dict,'PACKET_OBJECT')
    return value


def verify_inspect(raw,cid,expected,pid_required):
    value = json.loads(raw)
    need(type(value) is list and len(value) == 1,'INSPECT_SHAPE')
    row = value[0]
    need(row['Id'] == cid and row['Name'] == '/'+NAME and
         row['Image'] == IMAGE and row['HostConfig']['ReadonlyRootfs'] is True and
         row['HostConfig']['NetworkMode'] == 'none' and
         len(row['Mounts']) == 5,'INSPECT_IDENTITY')
    found = {(m['Source'],m['Destination'],m['Type'],m['RW'])
             for m in row['Mounts']}
    target = {(m['source'],m['target'],'bind',False) for m in expected['mounts']}
    need(found == target,'INSPECT_FIVE_EXACT_RO_BINDS')
    pid = row['State']['Pid']
    need(type(pid) is int and (pid > 0 if pid_required else pid >= 0),
         'INSPECT_PID')
    return pid


def cid_absent_result(result,cid):
    return (result.returncode == 1 and result.stdout == b'[]\n' and
            result.stderr ==
            f'Error response from daemon: No such container: {cid}\n'.encode())


def run_once():
    """Future reviewed effect body; this frozen cut never enters it."""
    need(EFFECT_ENABLED is True,'EFFECT_DISABLED_UNREVIEWED_PROBE')
    host_preflight()
    token = os.urandom(16).hex()
    selected = projection(token)
    attempt = Attempt()
    cid = None
    process = None
    listener = accepted = None
    unknown = True
    external = {'schema':'context-public-only-probe-terminal/v1',
                'status':'UNKNOWN_PRESERVE_NO_RETRY','name':NAME,
                'attempt':str(ATTEMPT),'retry_allowed':False}
    stop = {'requested':False}
    previous = {}
    def request_stop(_signal,_frame): stop['requested'] = True
    for signum in (signal.SIGINT,signal.SIGTERM):
        previous[signum] = signal.signal(signum,request_stop)
    try:
        attempt.claim()
        need(not stop['requested'],'STOP_AFTER_CLAIM')
        for directory,mode in [('stage',0o755),('stage/probe',0o755),
                               ('stage/'+ROLE,0o755),('control',0o755),
                               ('runner-code',0o755),('cache-guard',0o755),
                               ('native',0o755)]:
            attempt.mkdir(directory,mode)
        attempt.write('runner-code/public_probe_child.py',check_file(CHILD,PINS[CHILD]),0o444)
        attempt.write('native/lab-context-native-reader',NATIVE_PLACEHOLDER,0o444)
        attempt.write('admission.json',wire({'schema':'context-public-probe-admission/v1',
            'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_RETURN','name':NAME,
            'token':token,'argv':selected['create_argv'],
            'controller_freeze_sha256':PINS[CONTROLLER_FREEZE],
            'controller_review_sha256':PINS[CONTROLLER_REVIEW],
            'retry_allowed':False}))
        listener = socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        listener.bind(str(ATTEMPT/'control/ipc'))
        listener.listen(1)
        listener.settimeout(20)
        os.chmod(ATTEMPT/'control/ipc',0o600,follow_symlinks=False)
        created = docker_call(selected['create_argv'])
        need(created.returncode == 0 and created.stderr == b'', 'CREATE_UNKNOWN')
        cid = created.stdout.decode('ascii').strip()
        need(len(cid) == 64 and all(c in '0123456789abcdef' for c in cid),
             'CREATE_CID_UNKNOWN')
        process = subprocess.Popen([DOCKER,'start','-a',cid],stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   close_fds=True,start_new_session=True)
        deadline = time.monotonic()+25
        pid = 0
        while pid == 0:
            need(time.monotonic() < deadline and process.poll() is None and
                 not stop['requested'],'START_UNKNOWN')
            inspected = docker_call([DOCKER,'inspect','--type','container',cid])
            need(inspected.returncode == 0 and inspected.stderr == b'',
                 'INSPECT_UNKNOWN')
            pid = verify_inspect(inspected.stdout,cid,selected,False)
            if not pid: time.sleep(0.02)
        listener.settimeout(max(0.001,deadline-time.monotonic()))
        accepted,_ = listener.accept()
        accepted.settimeout(max(0.001,deadline-time.monotonic()))
        peer = struct.unpack('3i',accepted.getsockopt(socket.SOL_SOCKET,
                                                      socket.SO_PEERCRED,12))
        need(peer == (pid,os.getuid(),os.getgid()),'CHILD_PEER_IDENTITY')
        ready = recv(accepted)
        need(set(ready) == {'schema','token','out','output_absent',
                            'mountinfo_sha256','erofs_errno'} and
             ready['schema'] == 'context-public-probe-ready/v1' and
             ready['token'] == token and
             ready['out'] == '/workspace/'+ROLE+'/packages/0001' and
             ready['output_absent'] is True and
             ready['erofs_errno'] == 30 and
             type(ready['mountinfo_sha256']) is str and
             len(ready['mountinfo_sha256']) == 64 and
             not os.path.lexists(ATTEMPT/'stage'/ROLE/'packages') and
             not os.path.lexists(ATTEMPT/'stage'/ROLE/'.readonly-sentinel'),
             'READY_RO_EROFS_OUTPUT_ABSENT')
        send(accepted,{'schema':'context-public-probe-go/v1','token':token})
        attempt.mkdir('stage/'+ROLE+'/packages',0o755)
        attempt.mkdir('stage/'+ROLE+'/packages/0001',0o755)
        request_sha = attempt.write('stage/'+ROLE+'/packages/0001/request.json',
                                    REQUEST,0o444)
        need(request_sha == selected['request_sha256'],'PARENT_REQUEST_READBACK')
        send(accepted,{'schema':'context-public-probe-ack/v1','token':token,
                       'leaf':'request.json','sha256':request_sha})
        result = recv(accepted)
        need(result == {'schema':'context-public-probe-result/v1','token':token,
                        'child_readback_sha256':request_sha,
                        'mountinfo_sha256':ready['mountinfo_sha256'],
                        'erofs_errno':30},'CHILD_POST_ACK_VISIBILITY')
        stdout,stderr = process.communicate(timeout=max(0.001,deadline-time.monotonic()))
        need(process.returncode == 0 and stdout == b'' and stderr == b'',
             'CHILD_OS_RESULT_UNKNOWN')
        external.update({'status':'PROVISIONAL_PUBLIC_ONLY','cid':cid,
                         'child_pid':pid,'parent_peer':list(peer),
                         'mountinfo_sha256':ready['mountinfo_sha256'],
                         'request_sha256':request_sha,'erofs_errno':30,
                         'child_os_exit':process.returncode,
                         'child_stdout_sha256':sha(stdout),
                         'child_stderr_sha256':sha(stderr),
                         'five_read_only_mounts':True,
                         'nested_writable_or_private_mount':False,
                         'post_ack_visibility':True})
        unknown = False
    except BaseException as exc:
        external['error_class'] = type(exc).__name__
        external['error_code'] = str(exc)[:160]
        unknown = True
    finally:
        for sock in (accepted,listener):
            if sock is not None:
                try: sock.close()
                except BaseException: unknown = True
        if process is not None:
            try:
                if process.poll() is None:
                    process.terminate()
                process.communicate(timeout=2)
            except BaseException:
                unknown = True
                try: process.kill(); process.communicate(timeout=2)
                except BaseException: pass
            for pipe in (process.stdout,process.stderr):
                try: pipe.close()
                except BaseException: unknown = True
        if cid is not None:
            try:
                rm = docker_call([DOCKER,'rm','-f',cid])
                need(rm.returncode == 0 and rm.stderr == b'' and
                     rm.stdout.strip() == cid.encode(),'REMOVE_UNKNOWN')
                gone = docker_call([DOCKER,'inspect','--type','container',cid])
                need(cid_absent_result(gone,cid),'CID_ABSENCE_UNKNOWN')
                absent = docker_call([DOCKER,'ps','-a','--no-trunc','--filter',
                                      f'name=^{NAME}$','--format','{{.ID}}'])
                need(absent.returncode == 0 and absent.stdout == b'' and
                     absent.stderr == b'','NAME_ABSENCE_UNKNOWN')
                external['cid_absent'] = True
                external['name_absent'] = True
            except BaseException:
                unknown = True
        else:
            try:
                absent = docker_call([DOCKER,'ps','-a','--no-trunc','--filter',
                                      f'name=^{NAME}$','--format','{{.ID}}'])
                need(absent.returncode == 0 and absent.stdout == b'' and
                     absent.stderr == b'','NAME_ABSENCE_UNKNOWN')
                external['name_absent'] = True
            except BaseException:
                unknown = True
        if attempt.claimed:
            try:
                external['status'] = ('UNKNOWN_PRESERVE_NO_RETRY' if unknown else
                                      'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED')
                attempt.write('terminal.json',wire(external))
            except BaseException:
                unknown = True
        try: attempt.close()
        except BaseException: unknown = True
        for signum,prior in previous.items():
            signal.signal(signum,prior)
    need(not unknown and attempt.claimed,'PUBLIC_PROBE_UNKNOWN_NO_RETRY')
    raw = check_file(ATTEMPT/'terminal.json',sha(wire(external)))
    need(json.loads(raw)['status'] == 'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
         'TERMINAL_READBACK_UNKNOWN')
    return {'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
            'terminal_sha256':sha(raw),'attempt':str(ATTEMPT),
            'name':NAME,'retry_allowed':False}


def execute():
    need(EFFECT_ENABLED is True,
         'EFFECT_DISABLED_PENDING_INDEPENDENT_STATIC_REVIEW')
    result = run_once()
    print(json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(host=True),sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        execute()
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
