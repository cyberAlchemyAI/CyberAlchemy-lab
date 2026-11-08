"""Fixed synthetic namespace runner; no controller/launch/host authority.

Only a separately selected future launcher may supply fd3 and readonly views.
The pure tests never invoke main or execute a builder.
"""
import hashlib
import json
import os
import socket
import stat
import sys
import time
import types

CAP=64*1024*1024
PACKAGE='/work/out/legacy-fixture-source/mapped/packages/0001'
MODEL_PATH='/work/control/mapper_namespace_package_model_0007.py'


def need(ok,code):
    if not ok:raise RuntimeError(code)


def read_exact(path,sha,size,cap=CAP):
    need(type(path)is str and type(size)is int and 0<=size<=cap,'READ_BOUND')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a=os.fstat(fd);need(stat.S_ISREG(a.st_mode) and a.st_size==size,'REGULAR_SIZE')
        data=bytearray()
        while len(data)<size:
            part=os.read(fd,min(1048576,size-len(data)));need(bool(part),'SHORT_READ');data.extend(part)
        b=os.fstat(fd)
        ident=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        need(ident(a)==ident(b) and hashlib.sha256(data).hexdigest()==sha,'BYTE_DRIFT')
        return bytes(data)
    finally:os.close(fd)


def bootstrap(ns,sock,raw,sha,selected,started):
    """Acquire originals now on this held socket; never accepts stored frames."""
    def remaining():
        left=started+60-time.monotonic();need(left>0,'DEADLINE');sock.settimeout(left)
    need(type(started) in (int,float) and 0<=time.monotonic()-started<60,'START_TIME')
    need(sock.family==socket.AF_UNIX and sock.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET,'SOCKET_TYPE')
    sock.set_inheritable(False);sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
    originals={};frames=[];remaining()
    challenge,peer=ns.recv_packet(sock);frames.append(challenge)
    body=ns.validate_frame(challenge,0,selected['nonce'],sha,None)
    ns.closed(body,'controller_pid controller_start controller_namespaces')
    ns.number(body['controller_pid'],1);ns.number(body['controller_start'],1)
    need(peer[0]==0,'NAMESPACE_CONTROLLER_VIEW')
    claim=ns.proc_observation(os.getpid(),originals,'self-before');need(claim['pid']==1,'PAYLOAD_PID')
    hello=ns.frame(1,selected['nonce'],sha,ns.sha(challenge),{'claim':claim,'controller_tuple':peer,
        'fd_census':ns.census(),'originals':ns.pack_child_originals(originals,'self-before',claim)})
    remaining();ns.send_packet(sock,hello);frames.append(hello)
    remaining();observation,peer2=ns.recv_packet(sock);frames.append(observation)
    b=ns.validate_frame(observation,2,selected['nonce'],sha,ns.sha(hello))
    ns.closed(b,'hello_sha256 join_sha256 join_summary claim')
    need(peer==peer2 and b['hello_sha256']==ns.sha(hello) and b['claim']=='fixed-source-consistency-only','OBSERVATION')
    joined=ns.verify_host_join_summary(b['join_summary'],claim,body,peer,ns.sha(hello),{'uid':65534,'gid':65534})
    need(joined==b['join_sha256'],'SUMMARY_DIGEST')
    after=ns.proc_observation(os.getpid(),originals,'self-after');need(after==claim,'SELF_DRIFT')
    receipt=ns.frame(3,selected['nonce'],sha,ns.sha(observation),{'observation_sha256':ns.sha(observation),
        'controller_tuple':peer2,'claim_sha256':ns.sha(ns.encode(after)),'fd_census':ns.census(),
        'originals':ns.pack_child_originals(originals,'self-after',after),'join_summary_sha256':joined})
    remaining();ns.send_packet(sock,receipt);frames.append(receipt)
    # Deliberately no EOF receive/close. Client owns this exact socket next.
    return frames


def role_inventory(selected):
    rows={r['id']:r for r in selected['files']}
    need('composition_model' in rows and rows['composition_model']['view']=='control'
         and rows['composition_model']['child_path']==MODEL_PATH,'MODEL_SELECTION')
    need('composition_model' not in selected['roles'].values(),'MODEL_ROLE_ALIAS')
    child=[r for r in selected['files'] if r['view']!='host-only']
    need(sum(r['size_bytes'] for r in child)<=256*1024*1024,'CLOSURE_BYTE_BOUND')
    return rows,child


def load_module(name,raw,path,extra=None):
    need(name not in sys.modules,'MODULE_COLLISION')
    m=types.ModuleType(name);m.__package__=name.rpartition('.')[0];m.__file__=path
    if extra:m.__dict__.update(extra)
    sys.modules[name]=m;exec(compile(raw,path,'exec'),m.__dict__);return m


def execute(raw,sha,started):
    need(hashlib.sha256(raw).hexdigest()==sha and len(raw)<=1048576,'SELECTION')
    preliminary=json.loads(raw);rows={r['id']:r for r in preliminary['files']}
    def row(role):return rows[preliminary['roles'][role]]
    need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
         and sys.pycache_prefix==row('cache')['child_path'],'RUNTIME_FLAGS')
    need(os.path.realpath(sys.executable)==os.path.realpath(row('interpreter')['child_path']),'INTERPRETER')
    # These exact selected bytes are supplied by the independently pinned manifest.
    for role in ('cache','interpreter','namespace_runner'):
        r=row(role);read_exact(r['child_path'],r['sha256'],r['size_bytes'])
    need(os.path.realpath(__file__)==os.path.realpath(row('namespace_runner')['child_path']),'RUNNER_ORIGIN')
    need('_mapper_namespace_runtime' not in sys.modules,'MODULE_COLLISION')
    pkg=types.ModuleType('_mapper_namespace_runtime');pkg.__path__=[];sys.modules[pkg.__name__]=pkg
    def selected_load(name,r,extra=None):return load_module(pkg.__name__+'.'+name,read_exact(r['child_path'],r['sha256'],r['size_bytes']),r['child_path'],extra)
    ns=selected_load('mapper_namespace_probe_common_0004',row('common'))
    selected_load('mapper_package_ipc_model_0004',row('wire'))
    need('composition_model' in rows,'MODEL_SELECTION')
    model=selected_load('mapper_namespace_package_model_0007',rows['composition_model'])
    selected=model.selection(raw,sha);rows,child=role_inventory(selected)
    originals={r['id']:read_exact(r['child_path'],r['sha256'],r['size_bytes']) for r in child}
    def role_raw(role):return originals[selected['roles'][role]]
    client=selected_load('mapper_namespace_package_client_0008',row('namespace_client'))
    bridge=selected_load('mapper_namespace_package_bridge_0008',row('bridge'))
    adapter=selected_load('adapter',row('adapter'))
    adapter.verify_postimage(role_raw('preimage'),role_raw('builder'),expected_preimage_sha256=row('preimage')['sha256'])
    # Require cold source origins, including loaded stdlib, before fd3 traffic.
    allowed={r['child_path'] for r in child}
    def guard():
        for r in child:read_exact(r['child_path'],r['sha256'],r['size_bytes'])
        for m in tuple(sys.modules.values()):
            p=getattr(m,'__file__',None)
            if p:need(p in allowed,'IMPORT_ORIGIN')
    guard();sock=socket.socket(fileno=3);c=None
    try:
        frames=bootstrap(ns,sock,raw,sha,selected,started)
        c=client.Client(sock,selection_raw=raw,selection_sha256=sha,bootstrap_frames=frames,attempt_started=started)
        c.activate();bridge.install(c,PACKAGE)
        need('_t35_external_runtime_capture' not in sys.modules,'BRIDGE_COLLISION')
        sys.modules['_t35_external_runtime_capture']=bridge
        need('_mapper_namespace_fixture' not in sys.modules,'MODULE_COLLISION')
        fixture=types.ModuleType('_mapper_namespace_fixture');fixture.__path__=[];sys.modules[fixture.__name__]=fixture
        # Detection only; readonly mount custody is a separate launcher obligation.
        def no_effect(event,args):
            if event=='open':
                mode,flags=args[1:3]
                need(not(isinstance(mode,str) and any(x in mode for x in 'wax+')) and not(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)),'DIRECT_WRITE')
            need(event not in {'os.mkdir','os.remove','os.rename','os.rmdir','os.link','os.symlink','os.chmod','os.chown','os.truncate','subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'},'DIRECT_EFFECT')
        sys.addaudithook(no_effect)
        load_module(fixture.__name__+'.base',role_raw('fixture_base'),row('fixture_base')['child_path'],{'FIXTURE_CONFIG':json.loads(role_raw('fixture_config'))})
        build=load_module(fixture.__name__+'.build',role_raw('builder'),row('builder')['child_path'])
        guard();build.build(selected['begin_pins']['mapper']);guard()
        need(c.step==61 and not c.failed,'INCOMPLETE_PROTOCOL')
        return {'schema':'mapper-namespace-runner-result/v1','synthetic_only':True,'actions':61,'host_qualified':False}
    finally:
        if c is not None:c.close()
        else:sock.close()


def main():
    started=time.monotonic()
    need(len(sys.argv)==3 and sys.argv[1]=='/work/control/selection.json','ARGV')
    # Exact size is unknown until fstat, but the manifest remains independently hashed.
    fd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and 0<s.st_size<=1048576,'SELECTION_BOUND');size=s.st_size
    finally:os.close(fd)
    raw=read_exact(sys.argv[1],sys.argv[2],size,1048576)
    print(json.dumps(execute(raw,sys.argv[2],started),sort_keys=True),flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:
        os.write(2,b'MAPPER_NAMESPACE_RUNNER_UNKNOWN\n');raise SystemExit(1)
