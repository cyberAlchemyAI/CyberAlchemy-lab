"""Fixed synthetic namespace runner; no controller/launch/host authority.

Only a separately selected future launcher may supply fd3 and readonly views.
The pure tests never invoke main or execute a builder.
"""
import hashlib
import json
import os
import re
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


# This validator executes no selected code and reads no selected file. It is
# deliberately fixed in the independently selected entrypoint, before the first
# selected common/wire/model compilation. The model later validates again.
ROLES=('namespace_runner','namespace_client','bridge','adapter','preimage','builder',
       'fixture_base','fixture_config','common','wire','cache','interpreter','bwrap',
       'mediator','writer','transport','source','source_input','reader')
BOOTSTRAP_PATHS={'namespace_runner':'/work/control/mapper_namespace_package_runner_0010.py',
    'common':'/work/control/mapper_namespace_probe_common_0004.py',
    'wire':'/work/control/mapper_package_ipc_model_0004.py'}


def admit_manifest(raw,sha):
    def closed(v,keys):need(type(v)is dict and set(v)==set(keys.split()),'ADMISSION_SCHEMA')
    def digest(v):need(type(v)is str and re.fullmatch('[0-9a-f]{64}',v) is not None,'ADMISSION_DIGEST')
    def under(p,root):return p==root or p.startswith(root+'/')
    def path(p):
        need(type(p)is str and p.startswith('/') and len(p)<=4096
             and '\\' not in p and '\0' not in p
             and all(x not in ('','.','..') for x in p.split('/')[1:]),'ADMISSION_PATH')
        return p
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'ADMISSION_DUPLICATE_KEY');out[k]=v
        return out
    digest(sha);need(type(raw)is bytes and 0<len(raw)<=1048576 and hashlib.sha256(raw).hexdigest()==sha,'ADMISSION_BYTES')
    try:
        v=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'ADMISSION_NUMBER'))
        need(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()==raw,'ADMISSION_CANONICAL')
        closed(v,'schema posture attempt_id nonce scratch_root roles files begin_pins')
        need(v['schema']=='mapper-namespace-package-selection/v1' and v['posture']=='synthetic-projection-only','ADMISSION_POSTURE')
        need(type(v['attempt_id'])is str and re.fullmatch('[a-z0-9-]{1,48}',v['attempt_id']) is not None,'ADMISSION_ATTEMPT')
        digest(v['nonce']);root='/tmp/lc-u02-05-mapper-writer-'+v['attempt_id'];need(v['scratch_root']==root,'ADMISSION_ROOT')
        closed(v['roles'],' '.join(ROLES));closed(v['begin_pins'],'mapper source reader adapter')
        for h in v['begin_pins'].values():digest(h)
        need(type(v['files'])is list and 20<=len(v['files'])<=2048,'ADMISSION_FILE_COUNT')
        ids={};hosts=set();children=set();total=0
        for r in v['files']:
            closed(r,'id host_path child_path sha256 size_bytes view')
            need(type(r['id'])is str and re.fullmatch('[a-z0-9_-]{1,64}',r['id']) is not None and r['id'] not in ids,'ADMISSION_ID')
            digest(r['sha256']);need(type(r['size_bytes'])is int and 0<=r['size_bytes']<=CAP,'ADMISSION_SIZE')
            h=path(r['host_path']);c=path(r['child_path']);view=r['view']
            need(h not in hosts and c not in children,'ADMISSION_LOCATOR_ALIAS');hosts.add(h);children.add(c)
            need(view in ('control','family','runtime','host-only'),'ADMISSION_VIEW')
            if view=='control':need(under(h,root+'/control') and c=='/work/control'+h[len(root+'/control'):],'ADMISSION_CONTROL_MAP')
            elif view=='family':need(under(h,root+'/output/legacy-fixture-source') and c=='/work/out/legacy-fixture-source'+h[len(root+'/output/legacy-fixture-source'):],'ADMISSION_FAMILY_MAP')
            elif view=='runtime':need(h==c and any(under(h,x) for x in ('/usr','/lib','/lib64')),'ADMISSION_RUNTIME_MAP')
            else:need(under(h,root+'/host') and c==h,'ADMISSION_HOST_MAP')
            need(not under(c,PACKAGE) and c!='/work/control/selection.json','ADMISSION_OUTPUT_ALIAS')
            if view!='host-only':total+=r['size_bytes'];need(total<=256*1024*1024,'ADMISSION_AGGREGATE')
            ids[r['id']]=r
        for name,key in v['roles'].items():need(type(key)is str and key in ids,'ADMISSION_ROLE')
        need(len(set(v['roles'].values()))==len(ROLES),'ADMISSION_ROLE_ALIAS')
        def row(name):return ids[v['roles'][name]]
        for name in ('namespace_runner','namespace_client','bridge','adapter','preimage','builder','fixture_base','fixture_config','common','wire','cache'):
            need(row(name)['view']=='control','ADMISSION_ROLE_VIEW')
        for name in ('mediator','writer','transport'):need(row(name)['view']=='host-only','ADMISSION_ROLE_VIEW')
        for name in ('source','source_input','reader'):need(row(name)['view']=='family','ADMISSION_ROLE_VIEW')
        for name,expected in (('interpreter','/usr/bin/python3.14'),('bwrap','/usr/bin/bwrap')):
            need(row(name)['view']=='runtime' and row(name)['child_path']==expected,'ADMISSION_RUNTIME_ROLE')
        need(row('source')['child_path']=='/work/out/legacy-fixture-source/mapped/source-manifest.json','ADMISSION_SOURCE')
        for name,pin in (('source','mapper'),('source_input','source'),('reader','reader'),('adapter','adapter')):
            need(row(name)['sha256']==v['begin_pins'][pin],'ADMISSION_ROLE_PIN')
        for name,expected in BOOTSTRAP_PATHS.items():need(row(name)['child_path']==expected,'ADMISSION_BOOTSTRAP_PATH')
        need('composition_model' in ids and 'composition_model' not in v['roles'].values(),'ADMISSION_MODEL_ALIAS')
        model=ids['composition_model'];need(model['view']=='control' and model['child_path']==MODEL_PATH,'ADMISSION_MODEL_PATH')
        return v
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):
        raise RuntimeError('ADMISSION_MALFORMED') from None


def execute(raw,sha,started):
    preliminary=admit_manifest(raw,sha);rows={r['id']:r for r in preliminary['files']}
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
    fixture=json.loads(role_raw('fixture_config'))
    need(type(fixture)is dict and set(fixture)=={'schema','leaves'} and fixture['schema']=='mapper-fixed-synthetic-leaves/v1','FIXTURE')
    leaves={k:bytes.fromhex(v) for k,v in fixture['leaves'].items()}
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
        # Fixed synthetic fixture only: no historical builder/base/preimage code.
        guard();emit_fixture(c,selected['begin_pins']['mapper'],leaves,model.wire,ns);guard()
        need(c.step==61 and not c.failed,'INCOMPLETE_PROTOCOL')
        left=started+60-time.monotonic();need(left>0,'DEADLINE');sock.settimeout(left)
        ended,_=ns.recv_packet(sock,allow_eof=True);need(ended is None,'PARENT_FINISH_EOF')
        return {'schema':'mapper-namespace-runner-result/v1','synthetic_only':True,'actions':61,'host_qualified':False}
    finally:
        if c is not None:c.close()
        else:sock.close()


def emit_fixture(c,pin,leaves,wire,ns):
    need(set(leaves)=={target for verb,target in wire.schedule() if verb=='EMIT'},'FIXTURE_LEAF_SET')
    for verb,target in wire.schedule():
        if verb=='BEGIN':c.begin(pin,PACKAGE)
        elif verb=='EMIT':c.emit(target,leaves[target])
        elif verb=='SEAL':
            value={'semantic':[],'governance':[]};value[target]=[{'fixture':i} for i in range(25)]
            c.seal((json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
        elif verb=='COLD_READ':c.cold([PACKAGE+'/'+x for x in ('semantic','governance','request.json')])
        elif verb=='FINISH':c.finish({'path':PACKAGE+'/manifest.json','sha256':ns.sha(leaves['manifest.json'])})
        else:raise RuntimeError('FIXTURE_VERB')


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
