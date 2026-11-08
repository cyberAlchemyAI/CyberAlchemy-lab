"""One-shot namespace identity candidate. Static review before any invocation.

No run-on-import behavior. Actual run requires externally selected manifest and
separate preflight digest; an existing attempt root always refuses, never resets.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import selectors
import signal
import socket
import stat
import sys
import time
import types


C = None
WALL_SECONDS=10
CLEANUP_SECONDS=3
MAX_STREAM=8192
BWRAP_SHA='523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'


def argv(control,selection):
    return ['/usr/bin/bwrap','--die-with-parent','--unshare-all','--clearenv',
            '--as-pid-1','--sync-fd','3','--ro-bind','/usr','/usr',
            '--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
            '--ro-bind',control,'/work/control','--proc','/proc','--chdir','/',
            '--','/usr/bin/python3.14','-I','-B','-S','-X',
            'pycache_prefix=/work/control/cache','/work/control/payload',selection]


def directory(path):
    """Open every absolute component no-follow; retain terminal FD."""
    C.need(type(path) is str and path.startswith('/') and '\\' not in path,'DIRECTORY_PATH')
    parts=path.split('/')[1:];C.need(parts and all(p not in ('','.','..') for p in parts),'DIRECTORY_PATH')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
    try:
        for part in parts:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            os.close(fd);fd=child
        return fd
    except BaseException:
        os.close(fd);raise


def attached(fd,path):
    other=directory(path)
    try:return C.identity(os.fstat(fd))==C.identity(os.fstat(other))
    finally:os.close(other)


def write_new(fd,name,raw,mode=0o400):
    C.need(type(name) is str and '/' not in name and name not in ('','.','..'),'LEAF_NAME')
    out=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode,dir_fd=fd)
    try:
        view=memoryview(raw)
        while view:
            n=os.write(out,view);C.need(n>0,'WRITE_SHORT');view=view[n:]
        os.fchmod(out,mode);os.fsync(out)
    finally:os.close(out)
    os.fsync(fd)


def reserve(path,nonce,selection):
    parent,name=path.rsplit('/',1);p=directory(parent);fd=-1
    try:
        os.mkdir(name,0o700,dir_fd=p);os.fsync(p)
        fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=p)
        C.need(stat.S_IMODE(os.fstat(fd).st_mode)==0o700 and os.fstat(fd).st_uid==os.getuid(),'ROOT_MODE')
        os.fsync(fd);C.need(attached(fd,path),'ROOT_ATTACHMENT')
        write_new(fd,'attempt.pending',C.encode({'schema':'mapper-namespace-attempt/v1','nonce':nonce,'selection_sha256':selection}))
        result=fd;fd=-1;return result
    finally:
        if fd>=0:os.close(fd)
        os.close(p)


def group_members(pgid):
    result=[];count=0
    with os.scandir('/proc') as entries:
        for entry in entries:
            count+=1;C.need(count<=65536,'PROC_ENUM_BOUND')
            if not entry.name.isdecimal():continue
            try:
                raw,_=C.read_regular('/proc/'+entry.name+'/stat',4096);r=C.parse_stat(raw)
                if r['pgrp']==pgid:result.append(r)
            except (FileNotFoundError,ProcessLookupError):continue
    return result


def exited(pidfd):
    return os.waitid(os.P_PIDFD,pidfd,os.WEXITED|os.WNOHANG|os.WNOWAIT) is not None


def cleanup(pid,pidfd,established,terminate):
    end=time.monotonic()+CLEANUP_SECONDS
    # Direct child stays unreaped, anchoring its original PID until group check.
    if not established:
        try:established=os.getpgid(pid)==pid
        except ProcessLookupError:pass
    if terminate:
        try:
            if established:os.killpg(pid,signal.SIGKILL)
            else:signal.pidfd_send_signal(pidfd,signal.SIGKILL)
        except ProcessLookupError:pass
    while time.monotonic()<end:
        rows=group_members(pid) if established else []
        others=[r for r in rows if r['pid']!=pid]
        if exited(pidfd) and not others:
            waited,status=os.waitpid(pid,0);C.need(waited==pid,'REAP')
            return {'status':status,'reaped':True,'original_group_empty':established,
                    'group_observations':rows,'escaped_processes_excluded':False}
        if terminate and established and others:
            try:os.killpg(pid,signal.SIGKILL)
            except ProcessLookupError:pass
        time.sleep(0.02)
    raise C.Refusal('GROUP_CLEANUP_UNKNOWN')


def launch(args,exe,child_socket,null,out,err,ready):
    pid=os.fork()
    if pid==0:
        try:
            os.setsid()
            keep=fcntl.fcntl(exe,fcntl.F_DUPFD_CLOEXEC,10)
            os.dup2(null,0);os.dup2(out,1);os.dup2(err,2);os.dup2(child_socket,3)
            os.set_inheritable(3,True);os.write(ready,b'S')
            maximum=resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            if maximum==resource.RLIM_INFINITY:maximum=1048576
            os.closerange(4,keep);os.closerange(keep+1,maximum)
            os.execve('/proc/self/fd/'+str(keep),args,{})
        except BaseException:os._exit(111)
    return pid


def user_parent(pid):
    fd=os.open(f'/proc/{pid}/ns/user',os.O_RDONLY|os.O_CLOEXEC)
    parent=-1
    try:
        parent=fcntl.ioctl(fd,0xb702)  # Linux UAPI NS_GET_PARENT, _IO(0xb7,2).
        st=os.fstat(parent);return [st.st_dev,st.st_ino]
    finally:
        if parent>=0:os.close(parent)
        os.close(fd)


def census_valid(rows):
    C.need(type(rows) is list and len(rows)==4,'FD_CENSUS')
    expected=[[0,stat.S_IFCHR],[1,stat.S_IFIFO],[2,stat.S_IFIFO],[3,stat.S_IFSOCK]]
    C.need(C.encode(rows)==C.encode(expected),'FD_CENSUS')


def pump(sock,ready,out,err,pid,pidfd,controller,manifest_sha,nonce,exe_binding,deadline,originals,trace,state):
    sel=selectors.DefaultSelector();payload_fd=-1
    received=0;queued=None;previous=None;claim=None;hello=None;joined=None;before=None;wrapper=None
    streams={'stdout':bytearray(),'stderr':bytearray()}
    try:
        for fd,name in ((ready,'ready'),(out,'stdout'),(err,'stderr'),(sock.fileno(),'wire')):
            os.set_blocking(fd,False);sel.register(fd,selectors.EVENT_READ,name)
        while time.monotonic()<deadline:
            C.need(not exited(pidfd),'WRAPPER_EARLY_EXIT')
            for key,mask in sel.select(min(.02,max(0,deadline-time.monotonic()))):
                name=key.data
                if name in streams:
                    data=os.read(key.fd,4096)
                    if not data:sel.unregister(key.fd)
                    else:
                        streams[name].extend(data)
                        C.need(len(streams[name])<=MAX_STREAM and sum(map(len,streams.values()))<=16384,'STREAM_OVERFLOW')
                elif name=='ready':
                    C.need(os.read(ready,2)==b'S' and not state['established'],'READY')
                    state['established']=True;sel.unregister(ready)
                    r=C.parse_stat(C.read_regular(f'/proc/{pid}/stat',4096)[0])
                    C.need(r['pgrp']==pid and r['session']==pid,'SESSION')
                    wrapper={'pid':pid,'start':r['start']}
                    queued=C.frame(0,nonce,manifest_sha,None,{'controller_pid':controller['pid'],'controller_start':controller['start'],'controller_namespaces':controller['namespaces']})
                    sel.modify(sock.fileno(),selectors.EVENT_READ|selectors.EVENT_WRITE,'wire')
                elif name=='wire':
                    if mask & selectors.EVENT_WRITE and queued is not None:
                        try:C.send_packet(sock,queued)
                        except BlockingIOError:continue
                        trace.append({'direction':'controller','raw_hex':queued.hex()});previous=C.sha(queued);queued=None
                        sel.modify(sock.fileno(),selectors.EVENT_READ,'wire')
                    if mask & selectors.EVENT_READ:
                        C.need(state['established'] and queued is None,'UNEXPECTED_EARLY_FRAME')
                        raw,creds=C.recv_packet(sock);trace.append({'direction':'payload','raw_hex':raw.hex(),'credentials':creds})
                        C.need(sum(len(bytes.fromhex(t['raw_hex'])) for t in trace)<=49152 and len(trace)<=4,'WIRE_BUDGET')
                        if received==0:
                            b=C.validate_frame(raw,1,nonce,manifest_sha,previous);C.closed(b,'claim controller_tuple fd_census')
                            claim=b['claim'];census_valid(b['fd_census'])
                            C.need(type(b['controller_tuple']) is list and len(b['controller_tuple'])==3 and b['controller_tuple'][0]==0,'CONTROLLER_MEASUREMENT')
                            for x in b['controller_tuple']:C.number(x,0,(1<<32)-2)
                            # Host UID/GID mapping into child, including unmapped overflow IDs,
                            # is measured, not treated as authenticated controller authority.
                            state['controller_tuple']=b['controller_tuple']
                            C.number(creds[0],1,(1<<31)-1)
                            pre=C.parse_stat(C.read_regular(f'/proc/{creds[0]}/stat',4096)[0]);payload_fd=os.pidfd_open(creds[0])
                            post=C.parse_stat(C.read_regular(f'/proc/{creds[0]}/stat',4096)[0])
                            C.need(pre['start']==post['start'] and not select.select([payload_fd],[],[],0)[0],'PAYLOAD_PIDFD')
                            C.need(user_parent(creds[0])==controller['namespaces']['user'],'USER_PARENT')
                            before=C.ancestry(creds[0],wrapper,originals,'hello-before')
                            after=C.ancestry(creds[0],wrapper,originals,'hello-after')
                            C.need(before[0]['start']==pre['start'],'PAYLOAD_START')
                            joined=C.join(controller,before,after,claim,creds,exe_binding[0],exe_binding[1])
                            hello=C.sha(raw);state['payload_credentials']=creds
                            state['payload_before']=before;state['payload_claim']=claim
                            queued=C.frame(2,nonce,manifest_sha,hello,{'hello_sha256':hello,'join_sha256':joined,'claim':'fixed-source-consistency-only'})
                            received=1;sel.modify(sock.fileno(),selectors.EVENT_READ|selectors.EVENT_WRITE,'wire')
                        else:
                            C.need(received==1,'EXTRA_FRAME')
                            b=C.validate_frame(raw,3,nonce,manifest_sha,previous)
                            C.closed(b,'observation_sha256 controller_tuple claim_sha256 fd_census originals')
                            C.need(b['observation_sha256']==previous and b['controller_tuple']==state['controller_tuple']
                                   and b['claim_sha256']==C.sha(C.encode(claim)),'RECEIPT_JOIN')
                            census_valid(b['fd_census'])
                            C.need(type(b['originals']) is dict and len(b['originals'])<=16,'CHILD_ORIGINAL_BOUND')
                            for k,row in b['originals'].items():
                                C.need(type(k) is str and len(k)<=128,'CHILD_ORIGINAL_KEY');C.closed(row,'sha256 size_bytes')
                                C.hex64(row['sha256']);C.number(row['size_bytes'],0,65536)
                            C.need(not select.select([payload_fd],[],[],0)[0],'PAYLOAD_DEAD')
                            repeat=C.ancestry(creds[0],wrapper,originals,'receipt-after')
                            C.need(creds==state['payload_credentials'],'CREDENTIAL_DRIFT')
                            C.join(controller,before,repeat,claim,creds,exe_binding[0],exe_binding[1])
                            C.need(user_parent(creds[0])==controller['namespaces']['user'],'USER_PARENT_DRIFT')
                            current=C.proc_observation(os.getpid(),originals,'controller-after')
                            C.need(controller==current,'CONTROLLER_DRIFT')
                            # Child remains alive waiting for this EOF until all repeated joins pass.
                            sock.shutdown(socket.SHUT_RDWR)
                            state['received_complete']=True;state['join_sha256']=joined
                            state['child_original_bindings']=b['originals']
                            return streams
        raise C.Refusal('ATTEMPT_DEADLINE')
    finally:
        state['streams']={k:bytes(v).hex() for k,v in streams.items()}
        if payload_fd>=0:os.close(payload_fd)
        sel.close()


def selected_manifest(path,digest):
    C.hex64(digest);raw,_=C.read_regular(path,1048576);C.need(C.sha(raw)==digest,'SELECTION_DRIFT')
    m=C.decode(raw,1048576)
    C.closed(m,'schema evidence_root roles runtime_bindings selection_inputs')
    C.need(m['schema']=='mapper-namespace-stage2-selection/v1','SELECTION_SCHEMA')
    C.closed(m['roles'],'controller common payload model cache interpreter bwrap')
    C.need(type(m['runtime_bindings']) is list and len(m['runtime_bindings'])<=1024,'RUNTIME_BOUND')
    C.need(type(m['selection_inputs']) is list and len(m['selection_inputs'])<=1024,'INPUT_BOUND')
    for row in list(m['roles'].values())+m['runtime_bindings']+m['selection_inputs']:C.check_binding(row)
    C.need(m['roles']['bwrap']['path']=='/usr/bin/bwrap' and m['roles']['bwrap']['sha256']==BWRAP_SHA,'BWRAP')
    C.need(m['roles']['interpreter']['path']=='/usr/bin/python3.14','INTERPRETER')
    C.need(m['evidence_root'].endswith('/LC-U02-05/mapper-namespace-probe-evidence-0001'),'EVIDENCE_SELECTION')
    return m,raw


def bootstrap_read(path,maximum):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a=os.fstat(fd)
        if not stat.S_ISREG(a.st_mode) or a.st_size>maximum:raise RuntimeError('BOOTSTRAP_TYPE')
        out=bytearray()
        while True:
            block=os.read(fd,min(65536,maximum+1-len(out)))
            if not block:break
            out.extend(block)
            if len(out)>maximum:raise RuntimeError('BOOTSTRAP_BOUND')
        b=os.fstat(fd)
        if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise RuntimeError('BOOTSTRAP_DRIFT')
        return bytes(out)
    finally:os.close(fd)


def run(selection_path,selection_sha,preflight_path,preflight_sha):
    global C
    # External launcher hashes this controller and its imports before execution.
    # Bootstrap common bytes are selected by the externally pinned manifest.
    raw=bootstrap_read(selection_path,1048576)
    if len(raw)>1048576 or hashlib.sha256(raw).hexdigest()!=selection_sha:raise RuntimeError('SELECTION_DRIFT')
    role=json.loads(raw)['roles']['common'];code=bootstrap_read(role['path'],65536)
    if len(code)!=role['size_bytes'] or hashlib.sha256(code).hexdigest()!=role['sha256']:raise RuntimeError('COMMON_DRIFT')
    C=types.ModuleType('selected_namespace_common');exec(compile(code,role['path'],'exec'),C.__dict__)
    m,raw=selected_manifest(selection_path,selection_sha)
    pf,_=C.read_regular(preflight_path,131072);C.need(C.sha(pf)==preflight_sha,'PREFLIGHT_DRIFT')
    C.need(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
           and sys.pycache_prefix==m['roles']['cache']['path'],'RUNTIME_FLAGS')
    C.need(C.check_binding(m['roles']['controller'])[0]==bootstrap_read(__file__,65536),'CONTROLLER_SELECTION')
    with os.scandir('/proc/self/task') as entries:C.need(sum(1 for _ in entries)==1,'CONTROLLER_THREADS')
    # No actual probe is run during author/static tests. This body is reviewed code.
    nonce=os.urandom(32).hex();root=-1;control=-1;exe=-1;pid=None;pidfd=-1
    owned=[];sockets=[];trace=[];originals={};state={'established':False};group=None;failure=None;primary_failure=None
    try:
        root=reserve(m['evidence_root'],nonce,selection_sha)
        state['root_identity']=C.identity(os.fstat(root))
        deadline=time.monotonic()+WALL_SECONDS
        os.mkdir('control',0o700,dir_fd=root);os.fsync(root)
        control=os.open('control',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root)
        C.need(stat.S_IMODE(os.fstat(control).st_mode)==0o700,'CONTROL_MODE')
        for name in ('common','payload','model','cache'):
            data,_=C.check_binding(m['roles'][name]);write_new(control,name,data)
        write_new(control,'selection.json',raw);os.fsync(control)
        exe=os.open('/usr/bin/bwrap',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        C.need(C.identity(os.fstat(exe))==C.check_binding(m['roles']['bwrap'])[1],'BWRAP_INODE')
        interpreter_raw,interpreter_id=C.check_binding(m['roles']['interpreter'])
        controller=C.proc_observation(os.getpid(),originals,'controller-before')
        parent,child=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC);sockets=[parent,child]
        for sock in sockets:sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        ready_r,ready_w=os.pipe2(os.O_CLOEXEC);out_r,out_w=os.pipe2(os.O_CLOEXEC);err_r,err_w=os.pipe2(os.O_CLOEXEC)
        null=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC);owned=[ready_r,ready_w,out_r,out_w,err_r,err_w,null]
        args=argv(m['evidence_root']+'/control',selection_sha);state['argv']=args
        C.need(attached(root,m['evidence_root']) and attached(control,m['evidence_root']+'/control'),'ROOT_PRELAUNCH')
        selected_manifest(selection_path,selection_sha)
        pid=launch(args,exe,child.fileno(),null,out_w,err_w,ready_w);pidfd=os.pidfd_open(pid)
        for fd in (ready_w,out_w,err_w,null):os.close(fd);owned.remove(fd)
        child.close();sockets.remove(child)
        streams=pump(parent,ready_r,out_r,err_r,pid,pidfd,controller,selection_sha,nonce,
                     (C.sha(interpreter_raw),interpreter_id),deadline,originals,trace,state)
        group=cleanup(pid,pidfd,True,False);pid=None
        C.need(os.WIFEXITED(group['status']) and os.WEXITSTATUS(group['status'])==0,'CHILD_EXIT')
        # Drain residual bounded pipes after child reaping; no descendant held pipe can block.
        for fd,name in ((out_r,'stdout'),(err_r,'stderr')):
            while True:
                try:data=os.read(fd,4096)
                except BlockingIOError:raise C.Refusal('PIPE_NOT_CLOSED')
                if not data:break
                streams[name].extend(data);C.need(len(streams[name])<=MAX_STREAM,'STREAM_BOUND')
        C.need(not streams['stdout'] and not streams['stderr'],'UNEXPECTED_CHILD_OUTPUT')
        selected_manifest(selection_path,selection_sha)
        C.need(attached(root,m['evidence_root']) and attached(control,m['evidence_root']+'/control'),'ROOT_POST')
    except BaseException as exc:
        failure=str(exc) if type(exc) is C.Refusal else 'SETUP_OR_RUNTIME_UNKNOWN'
        primary_failure=failure
    finally:
        if pid is not None:
            try:
                if pidfd>=0:group=cleanup(pid,pidfd,state['established'],True)
                else:
                    os.kill(pid,signal.SIGKILL)
                    end=time.monotonic()+CLEANUP_SECONDS
                    while time.monotonic()<end:
                        if os.waitpid(pid,os.WNOHANG)[0]==pid:break
                        time.sleep(.02)
                    failure='PIDFD_OR_GROUP_UNKNOWN'
            except BaseException:failure='GROUP_CLEANUP_UNKNOWN'
        for sock in sockets:
            try:sock.close()
            except BaseException:failure='DESCRIPTOR_CLEANUP_UNKNOWN'
        for fd in owned+[control,exe,pidfd]:
            if fd>=0:
                try:os.close(fd)
                except BaseException:failure='DESCRIPTOR_CLEANUP_UNKNOWN'
    if root<0:raise C.Refusal('RESERVATION_OR_PREFLIGHT_UNKNOWN_NO_RETRY_IF_DIRECTORY_EXISTS')
    try:
        # Originals retained as hex in one bounded owned record; no private body inputs.
        record={'schema':'mapper-namespace-probe-originals/v1','proc':{k:v.hex() for k,v in originals.items()},
                'wire':trace,'state':state,'group':group,'failure':failure,'primary_failure':primary_failure,'selection_sha256':selection_sha,
                'preflight_sha256':preflight_sha,'nonce':nonce,'host_qualified':False,
                'claim':'fixed-source-consistency-only','candidate_result':'PASS' if failure is None else 'UNKNOWN'}
        before=attached(root,m['evidence_root']);data=C.encode(record)
        C.need(len(data)<=10*1024*1024,'RECORD_BOUND');write_new(root,'attempt.provisional.json',data)
        after=attached(root,m['evidence_root'])
        witness={'schema':'mapper-namespace-attachment/v1','provisional_sha256':C.sha(data),'attached_before':before,'attached_after':after,
                 'result':'PASS' if failure is None and before and after else 'UNKNOWN','held_identity':C.identity(os.fstat(root)),
                 'same_uid_excluded':False,'escaped_processes_excluded':False,'host_qualified':False}
        write_new(root,'attempt.attachment.json',C.encode(witness))
        C.need(attached(root,m['evidence_root']),'FINAL_ATTACHMENT_UNKNOWN')
        print(C.encode({'result':witness['result'],'evidence_root':m['evidence_root'],'host_qualified':False}).decode())
        return 0 if witness['result']=='PASS' else 1
    finally:os.close(root)


if __name__=='__main__':
    # This CLI is a candidate, not authority. External exact-byte review and one
    # independently selected invocation must precede this literal argument.
    if len(sys.argv)!=6 or sys.argv[1]!='--execute-one-shot-after-independent-review':
        raise SystemExit('STATIC_CANDIDATE_ONLY')
    raise SystemExit(run(*sys.argv[2:]))
