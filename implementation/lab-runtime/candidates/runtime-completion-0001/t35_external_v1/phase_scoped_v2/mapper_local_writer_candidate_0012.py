"""Unrun one-shot LOCAL writer fixture; no namespace/builder/native authority."""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import threading
import time
from . import mapper_namespace_probe_common_0004 as ns
from . import mapper_namespace_package_runner_0010 as runner
from . import mapper_namespace_package_model_0007 as model
from . import mapper_namespace_package_mediator_0011 as mediator
from . import mapper_package_ipc_model_0004 as wire
from . import mapper_package_transport_0001 as transport
from . import mapper_package_writer_0001 as writer
from ..held_paths import HeldCanonicalDirectory

ATTEMPT='local-writer-0012'
SCRATCH='/tmp/lc-u02-05-mapper-writer-'+ATTEMPT
EVIDENCE='/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05/mapper-local-writer-evidence-0012'


def need(ok,code):
    if not ok:raise RuntimeError(code)


def single_thread():need(threading.active_count()==1 and threading.current_thread() is threading.main_thread(),'SINGLE_THREAD')

def deadline(end):need(time.monotonic()<end,'SYNCHRONOUS_DEADLINE')

def pretty(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def planned_package(source_sha):
    leaves={name:pretty({'fixture_only':True,'leaf':name,'authority_effect':'none'}) for name in writer.SCHEDULE if name!='manifest.json'}
    manifest={'schema_version':'lab-mapped-context-package/v1-candidate','files':[{'path':model.PACKAGE+'/'+n,'sha256':ns.sha(leaves[n])} for n in sorted(leaves)],
        'source_manifest_binding':{'path':model.FAMILY+'/mapped/source-manifest.json','sha256':source_sha},'authority_effect':'none','actual_owner_outcome':None}
    leaves['manifest.json']=pretty(manifest)
    return leaves


def rebase_frames(history,selected,sha):
    bodies=[json.loads(bytes.fromhex(x['raw_hex']))['body'] for x in history['wire']];frames=[];previous=None
    for index,b in enumerate(bodies):
        if index==2:
            b['hello_sha256']=ns.sha(frames[1]);b['join_summary']['hello_sha256']=b['hello_sha256'];b['join_sha256']=ns.sha(ns.encode(b['join_summary']))
        if index==3:
            ob=json.loads(frames[2])['body'];b['observation_sha256']=ns.sha(frames[2]);b['join_summary_sha256']=ob['join_sha256']
        raw=ns.frame(index,selected['nonce'],sha,previous,b);frames.append(raw);previous=ns.sha(raw)
    return frames


def validate_plan(plan):
    ns.closed(plan,'schema scratch evidence manifest_raw_hex manifest_sha256 copies leaves frames')
    need(plan['schema']=='mapper-local-writer-plan/v1' and plan['scratch']==SCRATCH and plan['evidence']==EVIDENCE,'PLAN_DOMAIN')
    raw=bytes.fromhex(plan['manifest_raw_hex']);s=runner.admit_manifest(raw,plan['manifest_sha256'])
    need(s['attempt_id']==ATTEMPT and s['scratch_root']==SCRATCH,'PLAN_ROOT')
    need(type(plan['copies'])is list and len(plan['copies'])==len([r for r in s['files'] if r['view']!='runtime'])+1,'COPY_COUNT')
    expected={r['host_path']:(r['sha256'],r['size_bytes']) for r in s['files'] if r['view']!='runtime'}
    expected[SCRATCH+'/control/selection.json']=(ns.sha(raw),len(raw));seen=set()
    for row in plan['copies']:
        ns.closed(row,'path raw_hex');data=bytes.fromhex(row['raw_hex']);need(row['path'] not in seen and expected.get(row['path'])==(ns.sha(data),len(data)),'COPY_BYTES');seen.add(row['path'])
    leaves={n:bytes.fromhex(b) for n,b in plan['leaves'].items()}
    need(leaves==planned_package(s['begin_pins']['mapper']),'EXACT_PACKAGE')
    frames=[bytes.fromhex(b) for b in plan['frames']];m=model.Composition(raw,plan['manifest_sha256']);m.observe_synthetic(frames)
    return s,raw,leaves,frames


class OwnedTree:
    """No-replace owned tree; close only, never delete on failure."""
    def __init__(self,path):
        single_thread();self.path=Path(path);self.parent=HeldCanonicalDirectory(str(self.path.parent));self.fds={};self.closed=False;self.uncertain=False
        try:
            need(self.parent.attached(),'PARENT_DETACHED');self._mkdir(self.parent.fd,self.path.name,'')
        except BaseException:self.close();raise
    def _mkdir(self,parent,name,key):
        single_thread();old=os.umask(0o077)
        try:os.mkdir(name,0o700,dir_fd=parent)
        finally:os.umask(old)
        fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);self.fds[key]=fd
        os.fchmod(fd,0o700);os.fsync(fd);os.fsync(parent)
        a=os.fstat(fd);b=os.stat(name,dir_fd=parent,follow_symlinks=False)
        need((a.st_dev,a.st_ino)==(b.st_dev,b.st_ino) and a.st_uid==os.geteuid() and a.st_gid==os.getegid() and stat.S_IMODE(a.st_mode)==0o700,'OWNED_DIRECTORY')
    def attached(self):
        need(self.parent.attached(),'TREE_PARENT_DETACHED')
        for key,fd in self.fds.items():
            path=self.path if not key else self.path/key;a=os.fstat(fd);b=os.lstat(path)
            need(stat.S_ISDIR(b.st_mode) and (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino),'TREE_DETACHED')
    def write(self,relative,raw):
        need(type(relative)is str and all(x not in ('','.','..') for x in relative.split('/')) and not relative.startswith('/'),'RELATIVE')
        self.attached();parts=relative.split('/');key=''
        for name in parts[:-1]:
            nxt=(key+'/' if key else '')+name
            if nxt not in self.fds:self._mkdir(self.fds[key],name,nxt)
            key=nxt
        parent=self.fds[key];fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
        try:
            os.fchmod(fd,0o600);left=memoryview(raw)
            while left:n=os.write(fd,left);need(n>0,'SHORT_WRITE');left=left[n:]
            os.fsync(fd)
        finally:os.close(fd)
        os.fsync(parent);self.attached()
    def close(self):
        if self.closed:return
        self.closed=True
        for fd in reversed(list(self.fds.values())):
            try:os.close(fd)
            except BaseException:self.uncertain=True
        try:self.parent.close()
        except BaseException:self.uncertain=True


class LocalWriterMediator(mediator.Mediator):
    """Explicit local fixture peer mapping; real guard and real writer inherited."""
    def _transport_peer(self):return (os.getpid(),transport.process_start(os.getpid()),os.getuid(),os.getgid())


def preflight(plan):
    validate_plan(plan);single_thread()
    for path in (SCRATCH,EVIDENCE):need(not os.path.lexists(path),'ALREADY_CONSUMED')
    need(writer.SCHEDULE==tuple(n for v,n in wire.schedule() if v=='EMIT'),'LEAF_SCHEDULE')
    return {'eligible_for_independent_review':True,'effect_executed':False,'host_qualified':False}


def execute(plan):
    """Effect entrypoint. MUST NOT be called by static/pure tests."""
    preflight(plan);s,raw,leaves,frames=validate_plan(plan);start=time.monotonic();end=start+60
    evidence=OwnedTree(EVIDENCE);scratch=None;server=None;left=right=None;primary=None;records=[]
    try:
        evidence.write('admission.json',pretty({'plan_sha256':ns.sha(ns.encode(plan)),'fixture_only':True,'started_monotonic':start}))
        scratch=OwnedTree(SCRATCH)
        for row in plan['copies']:
            deadline(end);scratch.write(row['path'][len(SCRATCH)+1:],bytes.fromhex(row['raw_hex']))
        left,right=transport.socket_pair();m=model.Composition(raw,plan['manifest_sha256']);activation=m.observe_synthetic(frames)
        server=LocalWriterMediator(left,selection_raw=raw,selection_sha256=plan['manifest_sha256'],
            selection_binding={'path':SCRATCH+'/control/selection.json','sha256':plan['manifest_sha256'],'size_bytes':len(raw)},
            bootstrap_frames=frames,host_peer=m.peer,attempt_started=start)
        peer=server.transport_peer
        # Deliberately synchronous LOCAL harness: ACK prequeued, then exact
        # ACTIVATE checked. This is not the namespace client's handshake proof.
        transport.send_frame(right,ns.encode({'schema':'mapper-namespace-package-activation-ack/v1','activation_sha256':ns.sha(activation),'selection_sha256':plan['manifest_sha256']}))
        server.activate();need(transport.recv_frame(right,peer)==activation,'ACTIVATE_BYTES')
        def exchange(verb,payload):
            single_thread();deadline(end);scratch.attached();evidence.attached()
            request=wire.encode(wire.envelope(s['attempt_id'],plan['manifest_sha256'],server.model.protocol.ordinal,verb,payload))
            transport.send_frame(right,request);server.prepare_one();deadline(end)
            packets=server.pending['prepared']['packets'];need(sum(map(len,packets))<65536,'SYNCHRONOUS_REPLY_BOUND')
            server.send_pending()
            for packet in packets:deadline(end);need(transport.recv_frame(right,peer)==packet,'EXACT_REPLY')
            records.append({'verb':verb,'request_sha256':ns.sha(request),'reply_sha256':[ns.sha(p) for p in packets]})
        for verb,target in wire.schedule():
            if verb=='BEGIN':exchange('BEGIN',s['begin_pins'])
            elif verb in ('EMIT','SEAL'):
                if verb=='EMIT':data=leaves[target]
                else:
                    value={'semantic':[],'governance':[]};value[target]=[{'fixture':i} for i in range(25)];data=pretty(value)
                blob=server.model.protocol.ordinal
                exchange('BLOB_BEGIN',{'size_bytes':len(data),'sha256':ns.sha(data),'purpose':verb,'target':target})
                for offset in range(0,len(data),wire.CHUNK_MAX):exchange('BLOB_CHUNK',{'blob_id':blob,'offset':offset,'data':base64.b64encode(data[offset:offset+wire.CHUNK_MAX]).decode()})
                exchange('BLOB_END',{'blob_id':blob});exchange(verb,{'blob_id':blob,**({'leaf':target} if verb=='EMIT' else {})})
            elif verb=='COLD_READ':exchange(verb,{'index':target})
            else:exchange(verb,{'manifest_sha256':ns.sha(leaves['manifest.json'])})
        deadline(end);single_thread();scratch.attached();server.writer._scan()
        need(server.finished and server.writer.finished and server.writer.index==55 and not server.writer.unknown,'WRITER_FINISH')
        for name,data in leaves.items():runner.read_exact(SCRATCH+'/output/legacy-fixture-source/mapped/packages/0001/'+name,ns.sha(data),len(data))
        evidence.write('observations.json',pretty({'fixture_only':True,'actions':61,'leaves':55,'records':records,'package_sha256':{n:ns.sha(b) for n,b in leaves.items()},'host_qualified':False}))
    except BaseException as exc:
        primary=type(exc).__name__
        if server is not None:server.abort()
    finally:
        uncertain=False
        for resource in (server,right,left,scratch):
            if resource is not None:
                try:resource.close()
                except BaseException:uncertain=True
        uncertain |= bool(server and server.cleanup_uncertain) or bool(scratch and scratch.uncertain)
        try:evidence.write('terminal.json',pretty({'result':'PASS' if primary is None and not uncertain else 'UNKNOWN','primary_type':primary,'cleanup':'unknown' if uncertain else 'closed-retained','package_effect_consumed':True,'host_qualified':False}))
        finally:evidence.close()
        if evidence.uncertain:uncertain=True
    need(primary is None and not uncertain,'LOCAL_WRITER_UNKNOWN')
    return {'result':'PASS','fixture_only':True,'leaves':55,'host_qualified':False}
