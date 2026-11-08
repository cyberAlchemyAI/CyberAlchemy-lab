"""Held-root, exclusive owned fixture installation with exact cleanup tokens.

This is not a privileged broker or host-custody enrollment implementation.
No restart adopts a stage: interrupted objects require independently retained
ownership evidence and a later selected recovery action.
"""
import ctypes,errno,os,stat,resource
from pathlib import Path
from lab_contracts.codec import Refusal,need,sha
from lab_selectors.anchors import RootAnchor,identity,relative,stamp

DIR=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC

def _created_directory(parent,name):
    # O_PATH can hold the just-created directory even under umask0777. chmod
    # follows only our held Linux proc-fd capability, never a mutable pathname.
    held=os.open(name,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
    try:
        before=os.fstat(held);need(before.st_uid==os.geteuid(),'INSTALL_DIRECTORY_OWNER')
        os.chmod('/proc/self/fd/'+str(held),0o700)
        fd=os.open('.',DIR,dir_fd=held)
        if identity(os.stat(name,dir_fd=parent,follow_symlinks=False))!=identity(os.fstat(fd)):
            os.close(fd);raise Refusal('INSTALL_DIRECTORY_DETACHED')
        return fd
    finally:os.close(held)

def _name(value):
    need(type(value)is str and 1<=len(value)<=80 and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in value),'INSTALL_NAME')
    return value

class Parent:
    def __init__(self,anchor):
        need(type(anchor)is RootAnchor,'INSTALL_PARENT')
        self.anchor=anchor;self.fds=[];self.links=[]
        try:
            self.fds,self.links=anchor.open();self.fd=self.fds[-1]
            need(anchor.expected['uid']==os.geteuid() and not anchor.expected['mode']&0o022,'INSTALL_PARENT_CUSTODY')
            self.check()
        except BaseException:self.close();raise
    def check(self):
        need(identity(os.fstat(self.fd))==self.anchor.expected,'INSTALL_PARENT_CHANGED')
        for parent,name,fd in self.links:
            need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(fd)),'INSTALL_ANCESTOR_CHANGED')
    def close(self):
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

class OwnedTree:
    def __init__(self,parent,name):
        self.parent=parent;self.name=_name(name);self.fds={};self.ids={};self.files={};self.file_fds={};self.closed=False
        parent.check();os.mkdir(name,0o700,dir_fd=parent.fd)
        try:
            fd=_created_directory(parent.fd,name);self.fds['']=fd
            os.fchmod(fd,0o700);self.ids['']=identity(os.fstat(fd));os.fsync(fd);os.fsync(parent.fd)
            self.check()
        except BaseException:
            # Without a completely established exact ownership token, retain.
            self.close();raise InstallFailure('unknown') from None
    @property
    def path(self):return Path(self.parent.anchor.path)/self.name
    def check(self):
        self.parent.check()
        need(not self.closed and identity(os.stat(self.name,dir_fd=self.parent.fd,follow_symlinks=False))==self.ids[''],'INSTALL_ROOT_CHANGED')
        for path,fd in self.fds.items():
            need(identity(os.fstat(fd))==self.ids[path],'INSTALL_DIRECTORY_CHANGED')
            if path:
                parts=relative(path);parent='/'.join(parts[:-1])
                need(identity(os.stat(parts[-1],dir_fd=self.fds[parent],follow_symlinks=False))==self.ids[path],'INSTALL_DIRECTORY_DETACHED')
    def write(self,name,raw,mode,hook):
        self.check();parts=relative(name)
        for i in range(1,len(parts)):
            sub='/'.join(parts[:i]);up='/'.join(parts[:i-1])
            if sub not in self.fds:
                os.mkdir(parts[i-1],0o700,dir_fd=self.fds[up])
                fd=_created_directory(self.fds[up],parts[i-1]);self.fds[sub]=fd
                os.fchmod(fd,0o700);self.ids[sub]=identity(os.fstat(fd));os.fsync(fd);os.fsync(self.fds[up]);hook('directory-fsync',self)
        parent='/'.join(parts[:-1]);fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode,dir_fd=self.fds[parent])
        self.file_fds[name]=fd
        try:
            os.fchmod(fd,mode);self.files[name]=identity(os.fstat(fd));hook('file-create',self)
            view=memoryview(raw)
            while view:
                n=os.write(fd,view);need(n>0,'INSTALL_SHORT_WRITE');view=view[n:]
            hook('file-write',self);os.fsync(fd);hook('file-fsync',self)
        finally:
            # Retain inode ownership without a writable FD that would prevent
            # executing the selected binary (ETXTBSY).
            held=os.open('/proc/self/fd/'+str(fd),os.O_PATH|os.O_CLOEXEC)
            self.file_fds[name]=held;os.close(fd)
        os.fsync(self.fds[parent]);hook('name-fsync',self);self.check()
    def verify(self,expected):
        self.check();actual=set()
        for path,fd in self.fds.items():
            listed=os.listdir(fd);need(len(listed)<=8192,'INSTALL_DIRECTORY_BOUND')
            for name in listed:
                rel=(path+'/' if path else '')+name
                st=os.stat(name,dir_fd=fd,follow_symlinks=False)
                if rel in self.fds:need(stat.S_ISDIR(st.st_mode) and identity(st)==self.ids[rel],'INSTALL_DIRECTORY_IDENTITY')
                else:
                    need(rel in expected and stat.S_ISREG(st.st_mode) and st.st_nlink==1,'INSTALL_UNSELECTED_MEMBER');actual.add(rel)
                    f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fd)
                    try:
                        before=os.fstat(f);held=os.fstat(self.file_fds[rel])
                        need(identity(before)==self.files[rel] and identity(held)==self.files[rel] and held.st_nlink==1,'INSTALL_FILE_CHANGED')
                        row=expected[rel];need(before.st_size==row['size_bytes'] and stat.S_IMODE(before.st_mode)==row['mode'],'INSTALL_MEMBER_METADATA')
                        data=b''
                        while len(data)<=row['size_bytes']:
                            part=os.read(f,min(1024*1024,row['size_bytes']+1-len(data)))
                            if not part:break
                            data+=part
                        need(sha(data)==row['sha256'] and stamp(before)==stamp(os.fstat(f)),'INSTALL_MEMBER_DRIFT')
                    finally:os.close(f)
        need(actual==set(expected),'INSTALL_MISSING_MEMBER');self.check()
    def cleanup(self):
        # Full identity/inventory pass before the first unlink. No adoption.
        self.check();seen=set()
        for path,fd in self.fds.items():
            for name in os.listdir(fd):
                rel=(path+'/' if path else '')+name;st=os.stat(name,dir_fd=fd,follow_symlinks=False)
                if rel in self.fds:need(identity(st)==self.ids[rel] and stat.S_ISDIR(st.st_mode),'CLEANUP_DIRECTORY_CHANGED')
                else:need(rel in self.files and identity(st)==self.files[rel] and stat.S_ISREG(st.st_mode) and st.st_nlink==1 and os.fstat(self.file_fds[rel]).st_nlink==1,'CLEANUP_FOREIGN_MEMBER');seen.add(rel)
        need(seen==set(self.files),'CLEANUP_MISSING_MEMBER')
        for rel in sorted(self.files,reverse=True):
            self.check();parts=relative(rel);fd=self.fds['/'.join(parts[:-1])]
            need(identity(os.stat(parts[-1],dir_fd=fd,follow_symlinks=False))==self.files[rel],'CLEANUP_CHANGED')
            os.unlink(parts[-1],dir_fd=fd);os.fsync(fd)
        for rel in sorted((r for r in self.fds if r),key=lambda x:x.count('/'),reverse=True):
            parts=relative(rel);fd=self.fds['/'.join(parts[:-1])]
            need(identity(os.stat(parts[-1],dir_fd=fd,follow_symlinks=False))==self.ids[rel],'CLEANUP_CHANGED')
            os.rmdir(parts[-1],dir_fd=fd);os.fsync(fd)
        self.parent.check();need(identity(os.stat(self.name,dir_fd=self.parent.fd,follow_symlinks=False))==self.ids[''],'CLEANUP_ROOT_CHANGED')
        os.rmdir(self.name,dir_fd=self.parent.fd);os.fsync(self.parent.fd);self.close()
    def close(self):
        for fd in self.file_fds.values():os.close(fd)
        self.file_fds={}
        for fd in reversed(list(self.fds.values())):os.close(fd)
        self.fds={};self.closed=True

class InstallFailure(Refusal):
    def __init__(self,cleanup):super().__init__('INSTALL_REFUSED');self.cleanup=cleanup

def _rename(parent,old,new):
    libc=ctypes.CDLL(None,use_errno=True)
    fn=libc.renameat2;fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];fn.restype=ctypes.c_int
    if fn(parent.fd,old.encode(),parent.fd,new.encode(),1)!=0:raise OSError(ctypes.get_errno(),'NOREPLACE_REFUSED')

def install(payload,expected_manifest_sha256,parent,name,stage,*,hook=lambda event,tree:None):
    """No probing, imports or executable dispatch occurs before full preflight.

    Returned OwnedTree is a live ownership token; close() preserves it, cleanup()
    removes only this exact tree. A killed process cannot reconstruct this token.
    """
    tree=None;published=False
    try:
        _name(name);_name(stage);need(name!=stage,'INSTALL_DISTINCT_STAGE');parent.check()
        raw=payload.verify();need(sha(raw)==expected_manifest_sha256,'INSTALL_MANIFEST_PIN');payload.recheck()
        directories={''}
        for path in payload.files:
            parts=relative(path)
            directories.update('/'.join(parts[:i]) for i in range(1,len(parts)))
        need(len(directories)<=4096 and resource.getrlimit(resource.RLIMIT_NOFILE)[0]-len(os.listdir('/proc/self/fd'))>=len(payload.files)+len(directories)+64,'INSTALL_DESCRIPTOR_CAPACITY')
        # Ordinary collisions refuse before any stage; rename handles races.
        for target in (name,stage):
            try:os.stat(target,dir_fd=parent.fd,follow_symlinks=False)
            except FileNotFoundError:continue
            raise Refusal('INSTALL_COLLISION')
        tree=OwnedTree(parent,stage);hook('stage-durable',tree)
        expected=dict(payload.manifest['members'])
        for path,data in sorted(payload.files.items()):tree.write(path,data,expected[path]['mode'],hook)
        from .selection import row
        tree.write('payload-manifest.json',raw,0o600,hook);expected['payload-manifest.json']=row(raw,0o600)
        tree.verify(expected);payload.recheck();need(sha(payload.verify())==expected_manifest_sha256,'INSTALL_PAYLOAD_DRIFT')
        hook('before-publish',tree);tree.verify(expected);_rename(parent,stage,name);tree.name=name;published=True
        hook('after-rename',tree);os.fsync(parent.fd);hook('publish-fsync',tree);tree.verify(expected)
        return tree,expected
    except Exception as failure:
        cleanup=failure.cleanup if isinstance(failure,InstallFailure) else 'clean'
        if tree is not None:
            if published:cleanup='retained-owned';tree.close()
            else:
                try:tree.cleanup()
                except Exception:cleanup='retained-owned';tree.close()
        raise InstallFailure(cleanup) from None
