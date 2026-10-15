"""Owned technical immutable byte bundles. No actual repository admissions.

Executable candidate for later independently scheduled filesystem rehearsal.
No constructor, lock, staging write or native syscall is invoked by pure tests.
"""
import ctypes,fcntl,os,stat
from pathlib import Path,PurePosixPath
from .typed_targets import Refusal,need,relative,sha,parse,verify_byte_bundle

def ident(st):return (st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode))
def stamp(st):return (*ident(st),st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)

class OwnedBytePublisher:
    """Private trusted bootstrap inputs; no public API constructs this class."""
    def __init__(self,root,root_identity,guard,guard_binding,*,purpose):
        need(purpose=='owned-technical-rehearsal','actual admission/runtime purpose is unavailable')
        root=Path(root);need(root.is_absolute() and root.parent==Path('/tmp')
                            and root.name.startswith('cal-T14-publisher-'),'fresh owned T14 root required')
        need(type(root_identity) is tuple and len(root_identity)==4,'independent owned root identity required')
        self.root=root;self.root_identity=root_identity;self.guard=guard;self.guard_binding=guard_binding
        need(callable(guard) and set(guard_binding)=={'path','sha256'},'independently selected full guard required')
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
        path=Path(self.guard_binding['path'])
        need(Path(self.guard.__code__.co_filename)==path,'unselected full guard origin')
        # Full guard input/code capture is a trusted bootstrap prerequisite.
        # This physical hash supplements it; it is not a closed software loader.
        need(not path.is_symlink() and sha(path.read_bytes())==self.guard_binding['sha256'],'full guard code changed')
        self.guard();self.check()
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
            raw=b''
            while True:
                chunk=os.read(fd,1024*1024)
                if not chunk:break
                raw+=chunk;need(len(raw)<=before.st_size,'owned file grew')
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
        parts=PurePosixPath(relative(path)).parts;parent=base
        for name in parts[:-1]:parent=self.directory(parent,name,create=True)
        self.check();fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.fsync(parent);self.check()
        except BaseException:raise  # preserve every partial owned stage
    def lock(self):
        # Rehearsal provisioner must independently create/select this leaf first.
        lock=os.open('publisher.lock',os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
        try:
            value=os.fstat(lock);need(stat.S_ISREG(value.st_mode) and value.st_uid==os.getuid()
                and stat.S_IMODE(value.st_mode)==0o600,'owned publisher lock custody differs')
            self.leaves.append((self.fd,'publisher.lock',stamp(value)));self.check()
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);return lock
        except BaseException:os.close(lock);raise
    def publish(self,prepared,expected_pins):
        """Stage exact bytes, fsync, one no-replace commit or preserve uncertainty."""
        need(prepared['pins']==expected_pins,'independently selected complete plan pins differ')
        verify_byte_bundle(prepared['files'],expected_pins)
        manifest=parse(prepared['files']['bundle.json']);name=manifest['bundle_id']
        need(type(name) is str and name and all(c.isalnum() or c=='-' for c in name),'flat bundle name required')
        lock=self.lock();committed=False;expected_paths=tuple(prepared['files'])
        try:
            try:os.stat(name,dir_fd=self.fd,follow_symlinks=False)
            except FileNotFoundError:pass
            else:
                base=self.directory(self.fd,name);verify_byte_bundle(self.snapshot(base,expected_paths),expected_pins)
                return {'state':'already-committed-technical-bytes','new_owner_response_required':False,
                        'canonical_admission':False,'authority_effect':'none','pins':expected_pins}
            self.live_guard();stage='.'+name+'-stage-'+expected_pins['bundle_sha256']
            try:os.stat(stage,dir_fd=self.fd,follow_symlinks=False)
            except FileNotFoundError:
                os.mkdir(stage,0o700,dir_fd=self.fd);os.fsync(self.fd);base=self.directory(self.fd,stage)
                for path,raw in sorted(prepared['files'].items()):self.write(base,path,raw)
                os.fsync(base);os.fsync(self.fd)
            else:base=self.directory(self.fd,stage)
            verify_byte_bundle(self.snapshot(base,expected_paths),expected_pins);self.live_guard();self.check()
            # Explicit versioned no-replace primitive, derived from original
            # transition._publish; no original callback is replaced or aliased.
            libc=ctypes.CDLL(None,use_errno=True);fn=getattr(libc,'renameat2',None)
            need(fn is not None,'atomic no-replace publication unavailable')
            fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];fn.restype=ctypes.c_int
            if fn(self.fd,os.fsencode(stage),self.fd,os.fsencode(name),1):raise Refusal('no-replace commit refused; owned residue retained')
            committed=True;os.fsync(self.fd)
            # Stage locator deliberately changed at the commit point. Reattach
            # the same retained directory inode under its new exact final name.
            self.links=[(p,name if p==self.fd and n==stage else n,h,e) for p,n,h,e in self.links]
            verify_byte_bundle(self.snapshot(base,expected_paths),expected_pins);self.check()
            return {'state':'committed-technical-bytes','canonical_admission':False,
                    'native_semantic_governance_replay':False,'authority_effect':'none','pins':expected_pins}
        except BaseException:
            return {'state':'uncertain-commit-inspection-required' if committed else 'uncommitted-residue-inspection-required',
                    'automatic_retry':False,'all_unknown_residue_preserved':True,'canonical_admission':False,
                    'authority_effect':'none','pins':expected_pins}
        finally:fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
    def inspect_committed(self,bundle_id,pins,expected_paths):
        """Cold exact byte verification; no expired owner/source reapproval."""
        need(type(bundle_id) is str and bundle_id and all(c.isalnum() or c=='-' for c in bundle_id),'flat bundle name required')
        lock=self.lock()
        try:
            base=self.directory(self.fd,bundle_id);result=verify_byte_bundle(self.snapshot(base,expected_paths),pins)
            return {**result,'new_owner_response_required':False,'native_history_replayed':False,'pins':pins}
        finally:fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
    def close(self):
        self.closed=True
        for fd in reversed(self.fds):
            try:os.close(fd)
            except OSError:pass
        self.fds=[]
