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

ATTEMPT='namespace-writer-0014'
SCRATCH='/tmp/lc-u02-05-mapper-writer-'+ATTEMPT
EVIDENCE='/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05/mapper-namespace-writer-evidence-0014'


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
        single_thread();self.path=Path(path);self.parent=HeldCanonicalDirectory(str(self.path.parent));self.fds={};self.files={};self.closed=False;self.uncertain=False
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
            os.fsync(fd);info=os.fstat(fd)
            observed={'sha256':ns.sha(raw),'size_bytes':len(raw),'identity':file_identity(info),'mount_id':writer.fd_mount_id(fd)}
        finally:os.close(fd)
        os.fsync(parent);self.attached();self.files[relative]=observed
    def snapshot(self):
        self.attached();need(all('/' not in name for name in self.files),'FLAT_EVIDENCE')
        info=os.fstat(self.fds[''])
        return {'path':str(self.path),'root_identity':directory_identity(info),'mount_id':writer.fd_mount_id(self.fds['']),'files':{k:dict(v) for k,v in self.files.items()}}
    def close(self):
        if self.closed:return
        self.closed=True
        for fd in reversed(list(self.fds.values())):
            try:os.close(fd)
            except BaseException:self.uncertain=True
        self.uncertain |= close_held(self.parent)


def directory_identity(info):return [info.st_dev,info.st_ino,info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode)]

def file_identity(info):return [info.st_dev,info.st_ino,info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode),info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns]


def close_held(held):
    """Attempt every owned ancestor FD once, even if an earlier close failed."""
    if not isinstance(held,HeldCanonicalDirectory):
        try:held.close();return False
        except BaseException:return True
    descriptors=list(held.fds);held.fds.clear();held.records.clear();uncertain=False
    for fd in reversed(descriptors):
        try:os.close(fd)
        except BaseException:uncertain=True
    return uncertain


def verify_closed_evidence(snapshot):
    """New no-follow held view, exact old root/file identities and stable bytes.

    All new read handles close before returning; no final PASS file is created.
    """
    need(snapshot['path']==EVIDENCE and {'admission.json','observations.json','terminal.json'}<=set(snapshot['files']) and len(snapshot['files'])<=32,'EVIDENCE_SNAPSHOT')
    held=HeldCanonicalDirectory(EVIDENCE);uncertain=False
    try:
        need(held.attached() and directory_identity(os.fstat(held.fd))==snapshot['root_identity']
             and writer.fd_mount_id(held.fd)==snapshot['mount_id'],'EVIDENCE_ROOT_DRIFT')
        names=set()
        with os.scandir(held.fd) as entries:
            for entry in entries:
                need(len(names)<32 and entry.name in snapshot['files'],'EVIDENCE_INVENTORY');names.add(entry.name)
        need(names==set(snapshot['files']),'EVIDENCE_MISSING')
        for name,expected in snapshot['files'].items():
            fd=os.open(name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=held.fd)
            try:
                before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and file_identity(before)==expected['identity']
                    and writer.fd_mount_id(fd)==expected['mount_id'] and 0<=expected['size_bytes']<=4*1024*1024,'EVIDENCE_FILE_DRIFT')
                data=bytearray()
                while len(data)<=expected['size_bytes']:
                    part=os.read(fd,min(65536,expected['size_bytes']+1-len(data)))
                    if not part:break
                    data.extend(part)
                need(len(data)==expected['size_bytes'] and ns.sha(data)==expected['sha256']
                    and file_identity(os.fstat(fd))==expected['identity']
                    and file_identity(os.stat(name,dir_fd=held.fd,follow_symlinks=False))==expected['identity'],'EVIDENCE_BYTES_DRIFT')
            finally:
                try:os.close(fd)
                except BaseException:uncertain=True
        need(held.attached(),'EVIDENCE_POSTREAD_DETACHED')
    finally:uncertain |= close_held(held)
    need(not uncertain,'EVIDENCE_READ_CLOSE_UNKNOWN')

