"""Fresh complete input verification with ancestry shared only inside one batch."""
import hashlib,os,re,stat,threading
from pathlib import Path,PurePosixPath
from contextlib import contextmanager
_ACTIVE=threading.local()
_KERNEL=Path(__file__).absolute()
def need(value,message):
    if not value:raise ValueError(message)
def identity(v):return (v.st_dev,v.st_ino,v.st_mode,v.st_uid,v.st_gid)
def stamp(v):return (*identity(v),v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
def selected(root,row,external):
    need(type(row) is dict and set(row)=={'path','sha256'},'closed source input required')
    name=row['path'];need(type(name) is str and bool(name) and '\\' not in name and '\0' not in name,'unsafe source input path')
    path=PurePosixPath(name);need(path.as_posix()==name and '..' not in path.parts and name not in ('.','/'),'canonical source input path required')
    need(type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}',row['sha256']),'independent source input digest required')
    if path.is_absolute():need(row in external,'external source input not selected')
    else:path=PurePosixPath(root)/path
    return path.parts[1:],row['sha256']
class Batch:
    def __init__(self,root,pin):
        self.pin=pin;self.entries=_CALLBACKS[:5]
        self.root=str(root);need(Path(root).is_absolute() and str(Path(root))==self.root and '..' not in Path(root).parts,'canonical absolute source root required')
        self.handles=[];self.directories={};self.links=[];self.leaves=[];self.closed=False
        self.directories[()]=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.handles.append(self.directories[()])
    def directory(self,parts):
        if parts in self.directories:return self.directories[parts]
        parent=self.entries[1](self,parts[:-1]);child=os.open(parts[-1],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        self.handles.append(child);expected=identity(os.fstat(child));attached=os.stat(parts[-1],dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISDIR(attached.st_mode) and identity(attached)==expected,'source ancestor changed during open')
        self.links.append((parent,parts[-1],child,expected));self.directories[parts]=child;return child
    def check(self):
        kernel_guard(self.pin)
        need(not self.closed and self.entries==_CALLBACKS[:5],'closed or changed source batch')
        for parent,name,held,expected in reversed(self.links):
            actual=os.stat(name,dir_fd=parent,follow_symlinks=False);value=os.fstat(held)
            need(stat.S_ISDIR(actual.st_mode) and identity(actual)==identity(value)==expected,'source ancestor attachment changed')
        for parent,name,expected in self.leaves:
            value=os.stat(name,dir_fd=parent,follow_symlinks=False)
            need(stat.S_ISREG(value.st_mode) and stamp(value)==expected,'source input changed before batch return')
    def read(self,parts,digest,retain=True):
        need(not self.closed,'closed source batch');parent=self.entries[1](self,parts[:-1]);name=parts[-1]
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
        try:
            before=os.fstat(fd);need(stat.S_ISREG(before.st_mode),'regular source input required')
            attached=os.stat(name,dir_fd=parent,follow_symlinks=False);need(stat.S_ISREG(attached.st_mode) and stamp(attached)==stamp(before),'source leaf changed during open')
            parts_raw=[];hash_value=hashlib.sha256();size=0
            while True:
                chunk=os.read(fd,1024*1024)
                if not chunk:break
                size+=len(chunk);need(size<=before.st_size,'source input grew during read');hash_value.update(chunk)
                if retain:parts_raw.append(chunk)
            attached=os.stat(name,dir_fd=parent,follow_symlinks=False)
            need(stat.S_ISREG(attached.st_mode) and size==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(attached),'source leaf changed during read')
            need(hash_value.hexdigest()==digest,'selected source input bytes changed')
            self.leaves.append((parent,name,stamp(before)));return b''.join(parts_raw) if retain else None
        finally:os.close(fd)
    def close(self):
        self.closed=True
        for fd in reversed(self.handles):os.close(fd)
        self.handles=[];self.directories.clear();self.leaves.clear();self.links.clear()
def kernel_guard(pin):
    if not (type(pin) is str and re.fullmatch('[a-f0-9]{64}',pin) and pin==_PIN):raise ValueError('independently selected source capture kernel differs')
    callbacks=lambda:(Batch.__init__,Batch.directory,Batch.check,Batch.read,Batch.close,need,identity,stamp,selected,kernel_guard,kernel_digest,scope,verify_all,capture_one)
    if callbacks()!=_CALLBACKS:raise ValueError('source capture callbacks changed')
    digest=kernel_digest()
    if digest!=pin or callbacks()!=_CALLBACKS:raise ValueError('source capture kernel or callbacks changed')
def kernel_digest():
    handles=[];fd=None
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent);links=[]
        for part in _KERNEL.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child);links.append((parent,part,child,identity(os.fstat(child))));parent=child
        fd=os.open(_KERNEL.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode),'source capture kernel not regular');h=hashlib.sha256();size=0
        while True:
            chunk=os.read(fd,1024*1024)
            if not chunk:break
            size+=len(chunk);need(size<=before.st_size,'source capture kernel grew');h.update(chunk)
        need(size==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(_KERNEL.name,dir_fd=parent,follow_symlinks=False)),'source capture kernel changed')
        for p,name,held,expected in links:need(identity(os.stat(name,dir_fd=p,follow_symlinks=False))==identity(os.fstat(held))==expected,'source capture kernel ancestor changed')
        return h.hexdigest()
    finally:
        if fd is not None:os.close(fd)
        for handle in reversed(handles):os.close(handle)
@contextmanager
def scope(root,code_sha256):
    need(not getattr(_ACTIVE,'value',False),'nested source batch forbidden');kernel_guard(code_sha256);batch=Batch(root,code_sha256);close=Batch.close;check=Batch.check;guard=kernel_guard;_ACTIVE.value=True
    try:
        check(batch);yield batch
    finally:
        try:guard(code_sha256);check(batch)
        finally:close(batch);_ACTIVE.value=False

def verify_all(root,rows,*,code_sha256,selected_external=()):
    """Every selected row read and hashed fresh, in its original order."""
    kernel_guard(code_sha256)
    selected_rows=[selected(str(root),row,selected_external) for row in rows]
    names=[parts for parts,digest in selected_rows];need(len(names)==len(set(names)),'duplicate/alias source input locator')
    read=_CALLBACKS[3]
    with scope(root,code_sha256) as batch:
        for parts,digest in selected_rows:read(batch,parts,digest,False)
    return len(selected_rows)
def capture_one(root,row,*,code_sha256,selected_external=()):
    kernel_guard(code_sha256)
    parts,digest=selected(str(root),row,selected_external)
    read=_CALLBACKS[3]
    with scope(root,code_sha256) as batch:raw=read(batch,parts,digest)
    return raw
_CALLBACKS=(Batch.__init__,Batch.directory,Batch.check,Batch.read,Batch.close,need,identity,stamp,selected,kernel_guard,kernel_digest,scope,verify_all,capture_one)

_PIN=getattr(getattr(globals().get('__spec__'),'loader',None),'selected_source_sha256',None)
need(type(_PIN) is str and re.fullmatch('[a-f0-9]{64}',_PIN),'independently selected captured loader metadata required')
