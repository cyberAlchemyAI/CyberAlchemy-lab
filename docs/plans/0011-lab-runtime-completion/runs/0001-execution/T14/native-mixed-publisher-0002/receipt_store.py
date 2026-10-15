"""Private full-original staging and held-inode no-replace visibility commit.

Derived from frozen T14 v2 descriptor mechanics; no mutable source-name rename.
No canonical path or native effect is implicitly authorized.
"""
import ctypes,fcntl,os,stat
from pathlib import Path,PurePosixPath
from .contracts import Refusal,need,relative,sha,parse

def ident(st):return (st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode))
def stamp(st):return (*ident(st),st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)

class ReceiptStore:
    def __init__(self,root,root_identity,boundary):
        root=Path(root);need(root.is_absolute() and '..' not in root.parts,'exact selected owned root required')
        need(type(root_identity) is tuple and len(root_identity)==4,'independent owned root identity required')
        self.root=root;self.root_identity=root_identity;self.boundary=boundary
        self.fds=[];self.links=[];self.leaves=[];self.closed=False
        try:
            fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fds.append(fd)
            for name in root.parts[1:]:
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
                self.fds.append(child);self.links.append((fd,name,child,ident(os.fstat(child))));fd=child
            self.fd=fd;need(ident(os.fstat(fd))==root_identity and root_identity[2]==os.getuid()
                           and root_identity[3]==0o700,'owned root custody differs');self.check()
        except BaseException:self.close();raise
    def check(self):
        need(not self.closed,'publisher handles closed')
        for parent,name,held,expected in self.links:
            need(ident(os.stat(name,dir_fd=parent,follow_symlinks=False))==ident(os.fstat(held))==expected,
                 'owned directory attachment changed')
        for parent,name,expected in self.leaves:
            need(stamp(os.stat(name,dir_fd=parent,follow_symlinks=False))==expected,'selected owned leaf changed')
    def live_guard(self):
        self.boundary.guard();self.check()
    def directory(self,parent,name,*,create=False):
        need('/' not in name and name not in ('','.', '..'),'single directory component required')
        if create:
            try:os.mkdir(name,0o700,dir_fd=parent);os.fsync(parent)
            except FileExistsError:pass
        child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        self.fds.append(child);value=ident(os.fstat(child))
        need(value[2]==os.getuid() and value[3]==0o700,'owned child directory custody differs')
        self.links.append((parent,name,child,value));self.check();return child
    def read(self,parent,name):
        self.check();fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
        try:
            before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid()
                and stat.S_IMODE(before.st_mode)==0o600 and before.st_size<=16*1024*1024,'bounded private owned technical file required')
            parts=[];total=0
            while True:
                chunk=os.read(fd,min(1024*1024,before.st_size-total+1))
                if not chunk:break
                total+=len(chunk);need(total<=before.st_size and total<=16*1024*1024,'owned file grew');parts.append(chunk)
            raw=b''.join(parts)
            need(len(raw)==before.st_size and stamp(before)==stamp(os.fstat(fd))
                ==stamp(os.stat(name,dir_fd=parent,follow_symlinks=False)),'owned file changed during read')
            self.leaves.append((parent,name,stamp(before)));self.check();return raw
        finally:os.close(fd)
    def snapshot(self,base,expected_paths):
        expected={relative(path) for path in expected_paths};out={}
        def walk(fd,prefix):
            actual=set(os.listdir(fd));wanted={PurePosixPath(path[len(prefix):]).parts[0]
                                             for path in expected if path.startswith(prefix)}
            need(actual==wanted,'foreign or missing bundle residue retained')
            for name in sorted(actual):
                path=prefix+name;value=os.stat(name,dir_fd=fd,follow_symlinks=False)
                need(not stat.S_ISLNK(value.st_mode),'bundle symlink residue retained')
                if stat.S_ISDIR(value.st_mode):walk(self.directory(fd,name),path+'/')
                else:need(path in expected,'unselected owned file');out[path]=self.read(fd,name)
        walk(base,'');self.check();return out
    def write(self,base,path,raw):
        need(type(raw)is bytes and len(raw)<=16*1024*1024,'bounded exact original output required')
        parts=PurePosixPath(relative(path)).parts;parent=base
        for name in parts[:-1]:parent=self.directory(parent,name,create=True)
        self.check();fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.fsync(parent);self.check()
        except BaseException:raise
    def lock(self):
        # Rehearsal provisioner must independently create/select this leaf first.
        lock=os.open('publisher.lock',os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
        try:
            value=os.fstat(lock);need(stat.S_ISREG(value.st_mode) and value.st_uid==os.getuid()
                and stat.S_IMODE(value.st_mode)==0o600 and value.st_size==0 and value.st_nlink==1,'owned publisher lock custody differs')
            self.leaves.append((self.fd,'publisher.lock',stamp(value)));self.check()
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);return lock
        except BaseException:os.close(lock);raise
    def _commit_record(self,raw,name):
        """Publish the held anonymous inode, never rename a mutable source path."""
        need(type(raw)is bytes and len(raw)<=16*1024*1024 and type(name)is str and '/'not in name and name not in ('','.','..'),'bounded exact single-leaf commit required')
        need(hasattr(os,'O_TMPFILE'),'descriptor-bound receipt storage unavailable')
        receipt=os.open('.',os.O_RDWR|os.O_TMPFILE|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        linked=False
        try:
            value=os.fstat(receipt)
            need(stat.S_ISREG(value.st_mode) and value.st_uid==os.getuid()
                 and stat.S_IMODE(value.st_mode)==0o600 and value.st_nlink==0,'anonymous owned receipt custody differs')
            view=memoryview(raw)
            while view:
                written=os.write(receipt,view);need(written>0,'receipt write made no progress');view=view[written:]
            os.fsync(receipt);os.lseek(receipt,0,os.SEEK_SET);before=os.fstat(receipt)
            parts=[];total=0
            while True:
                piece=os.read(receipt,min(1024*1024,len(raw)-total+1))
                if not piece:break
                total+=len(piece);need(total<=len(raw) and total<=before.st_size,'anonymous receipt grew');parts.append(piece)
            observed=b''.join(parts)
            need(observed==raw and stamp(before)==stamp(os.fstat(receipt)),'selected anonymous receipt changed')
            self.live_guard();self.check()
            libc=ctypes.CDLL(None,use_errno=True);fn=getattr(libc,'linkat',None)
            need(fn is not None,'descriptor-bound no-replace commit unavailable')
            fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_int];fn.restype=ctypes.c_int
            # Linux AT_EMPTY_PATH binds the source to this still-held O_TMPFILE
            # descriptor. linkat never replaces an existing destination leaf.
            if fn(receipt,b'',self.fd,os.fsencode(name),0x1000):raise Refusal('descriptor-bound receipt commit refused; residue retained')
            linked=True;os.fsync(self.fd)
            need(stamp(os.fstat(receipt))==stamp(os.stat(name,dir_fd=self.fd,follow_symlinks=False)),
                 'linked receipt attachment changed')
            need(self.read(self.fd,name)==raw,'linked whole receipt changed');self.check()
            return True
        except BaseException:
            # Attempting the atomic syscall establishes uncertainty, including
            # interruption before Python records its return. No automatic retry.
            raise
        finally:os.close(receipt)
    def close(self):
        self.closed=True
        for fd in reversed(self.fds):
            try:os.close(fd)
            except OSError:pass
        self.fds=[]
