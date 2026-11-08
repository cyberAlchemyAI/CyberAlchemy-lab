"""Fake-only, no-follow, one-shot copy proof; never copies a protected archive."""
from __future__ import annotations
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

ARCHIVE='product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/branch.snapshot'
REAL_SOURCE=Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
MAX_FILE=4*1024*1024
LOCAL=Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
PREDECESSOR={'context-stage-0001/freeze.json':'8e7194585a4a98ce4a6ed906ef349449457335aba2060229c1d105eac36021b8',
             'context-stage-0001/selection.json':'6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf',
             'CONTEXT-STAGE-INDEPENDENT-STATIC-REVIEW-0001.md':'2acfba6337613eb777d7c6b6c8ff1fd9cfbeb3cc06742cff95869516af1757de'}

class Refused(ValueError):pass
class CopyPoisoned(Refused):
    """No success or retry; preserve the whole fixture/stage for owner disposition."""
    def __init__(self,primary_error,cleanup_errors,created_inode,final_name_identity):
        self.primary_error=primary_error
        self.cleanup_errors=tuple(cleanup_errors)
        self.created_inode=created_inode
        self.final_name_identity=final_name_identity
        self.retry_allowed=False
        self.stage_poisoned=created_inode is not None or bool(cleanup_errors)
        super().__init__('exclusive copy failed or FD cleanup uncertain; no name-based unlink')

def require(ok,why):
    if not ok:raise Refused(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def _close_once(fd):os.close(fd)
def _write(fd,chunk):return os.write(fd,chunk)
def _fsync(fd):os.fsync(fd)

def verify_predecessor():
    for name,pin in PREDECESSOR.items():
        path=LOCAL/name
        fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
                    before.st_size<=MAX_FILE,'reviewed predecessor not bounded regular file')
            raw=bytearray()
            while len(raw)<before.st_size+1:
                part=os.read(fd,min(65536,before.st_size+1-len(raw)))
                if not part:break
                raw.extend(part)
            after=os.fstat(fd)
            require(identity(after)==identity(before) and len(raw)==before.st_size and
                    sha(raw)==pin,'reviewed predecessor digest differs')
            if name.endswith('selection.json'):
                selection=json.loads(raw)
        finally:_close_once(fd)
    require(selection['context_launch']=='REFUSED' and
            selection['future_root_file_count_if_protected_copied_under_separate_effect']==1570 and
            selection['protected_body_read'] is False and selection['effect']=='NOT_RUN',
            'reviewed static Context stage claim differs')
    return {'stage_file_plan':1570,'predecessor_review_sha256':
            PREDECESSOR['CONTEXT-STAGE-INDEPENDENT-STATIC-REVIEW-0001.md'],
            'protected_body_read':False,'effect':'NOT_RUN'}

def safe_name(name):
    require(type(name) is str and name and not name.startswith('/') and '\\' not in name and
            '//' not in name and PurePosixPath(name).as_posix()==name and
            all(part not in ('','.','..') for part in name.split('/')),
            'unsafe member path')
    require(name!=ARCHIVE,'protected archive body copy refused')
    return name

def fake_root(path):
    path=Path(path)
    require(path.is_absolute() and path.parent.name.startswith('cal-context-stage-fake-') and
            path.parent.parent==Path('/tmp') and path.name in ('src','dst') and
            path!=REAL_SOURCE and path.is_dir(),
            'disposable fake root required')
    return path

def own_directory_chain(path,owned):
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    owned.append(fd)
    for part in Path(path).parts[1:]:
        fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
        owned.append(fd)
    return fd

def descend(parent,components,owned):
    for part in components:
        parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        owned.append(parent)
    return parent

def identity(st):return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,st.st_nlink,st.st_size)
def inode(st):return (st.st_dev,st.st_ino)
def final_identity(parent,leaf):
    try:return inode(os.stat(leaf,dir_fd=parent,follow_symlinks=False))
    except FileNotFoundError:return None

def copy_fake_public(source_root,target_root,row):
    """Write only fake bytes; failures poison the root and never unlink by name."""
    require(os.getuid()==os.geteuid() and os.getgid()==os.getegid(),
            'fake copy runtime identity split')
    source_root=fake_root(source_root);target_root=fake_root(target_root)
    require(source_root.name=='src' and target_root.name=='dst' and
            source_root.parent==target_root.parent,'one disposable fixture family required')
    require(type(row) is dict and set(row)=={'path','sha256','mode'},'closed fake row required')
    name=safe_name(row['path'])
    pin=row['sha256'];mode=row['mode']
    require(type(pin) is str and len(pin)==64 and all(x in '0123456789abcdef' for x in pin) and
            mode in ('0400','0444','0600','0644'),'fake copy digest/mode differs')
    components=name.split('/');owned=[];created=None;target_parent=None;leaf=components[-1]
    primary=None;result=None
    try:
        source_parent=descend(own_directory_chain(source_root,owned),components[:-1],owned)
        target_parent=descend(own_directory_chain(target_root,owned),components[:-1],owned)
        source_fd=os.open(leaf,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,
                          dir_fd=source_parent)
        owned.append(source_fd)
        before=os.fstat(source_fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and
                0<=before.st_size<=MAX_FILE,'copy input must be bounded one-link regular file')
        target_fd=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,
                          int(mode,8),dir_fd=target_parent)
        owned.append(target_fd)
        os.fchmod(target_fd,int(mode,8))
        target_open=os.fstat(target_fd)
        created=inode(target_open)
        require(stat.S_ISREG(target_open.st_mode) and target_open.st_nlink==1,
                'exclusive target inode differs')
        copied=0;digest=hashlib.sha256()
        while True:
            chunk=os.read(source_fd,min(65536,before.st_size+1-copied))
            if not chunk:break
            copied+=len(chunk)
            require(copied<=before.st_size,'copy source grew')
            digest.update(chunk)
            view=memoryview(chunk)
            while view:
                count=_write(target_fd,view)
                require(type(count) is int and count>0,'copy output stalled')
                view=view[count:]
        after=os.fstat(source_fd)
        require(identity(after)==identity(before) and copied==before.st_size and
                digest.hexdigest()==pin,'copy source changed or digest differs')
        _fsync(target_fd)
        written=os.fstat(target_fd)
        require(inode(written)==created and written.st_size==copied and
                written.st_mode&0o777==int(mode,8) and written.st_nlink==1 and
                written.st_uid==os.geteuid() and written.st_gid==os.getegid(),
                'created target inode changed')
        require(final_identity(target_parent,leaf)==created,
                'created target name detached or replaced')
        check_fd=os.open(leaf,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,
                         dir_fd=target_parent)
        owned.append(check_fd)
        check_before=os.fstat(check_fd)
        require(inode(check_before)==created and check_before.st_size==copied and
                check_before.st_mode&0o777==int(mode,8) and check_before.st_nlink==1 and
                check_before.st_uid==os.geteuid() and check_before.st_gid==os.getegid(),
                'post-copy target inode differs')
        checked=0;check_hash=hashlib.sha256()
        while True:
            chunk=os.read(check_fd,min(65536,copied+1-checked))
            if not chunk:break
            checked+=len(chunk);require(checked<=copied,'target grew during verification')
            check_hash.update(chunk)
        require(identity(os.fstat(check_fd))==identity(check_before) and
                checked==copied and check_hash.hexdigest()==pin,
                'post-copy target bytes differ')
        _fsync(target_parent)  # Durable directory entry after file fsync.
        require(final_identity(target_parent,leaf)==created,
                'target name changed after directory fsync')
        result=copied
    except BaseException as exc:
        primary=exc
    observed=None
    if primary is not None and target_parent is not None:
        try:observed=final_identity(target_parent,leaf)
        except BaseException:pass
    cleanup=[]
    for fd in reversed(owned):
        try:_close_once(fd)  # Exactly one attempt per numeric FD, even after ambiguous failure.
        except BaseException as exc:cleanup.append((fd,exc))
    if primary is not None or cleanup:
        # A stat-then-unlink sequence is racy. Leave even an owned partial name
        # untouched, poison the exclusive fixture root, and forbid retry.
        raise CopyPoisoned(primary,cleanup,created,observed) from primary
    return result

def real_stage_copy(*_args,**_kwargs):raise Refused('protected stage effect requires separate review')
def launch_context(*_args,**_kwargs):raise Refused('Context effect disabled')
