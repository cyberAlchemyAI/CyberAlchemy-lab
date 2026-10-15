"""Fresh exact captures for this new margin adapter, no cached trust."""
import hashlib,json,os,stat
from pathlib import Path,PurePosixPath

def require(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def relative(value):
    require(type(value) is str and value and '\\' not in value and '\0' not in value,'relative path required')
    p=PurePosixPath(value);require(not p.is_absolute() and p.as_posix()==value and '..' not in p.parts and value!='.','exact relative path required');return value
def parse(raw):
    def pairs(rows):
        out={}
        for k,v in rows:require(k not in out,'duplicate JSON key');out[k]=v
        return out
    def constant(value):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
def identity(st):return (st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode))
def stamp(st):return (*identity(st),st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def capture(path,pin,*,control_root=None,root_identity=None,max_bytes=64*1024*1024):
    require(type(pin) is str and len(pin)==64 and all(c in '0123456789abcdef' for c in pin),'independent byte digest required')
    path=Path(path);require(path.is_absolute() and path.as_posix()==str(path) and '..' not in path.parts,'absolute exact capture path')
    if control_root is not None:
        control_root=Path(control_root);require(control_root.is_absolute() and control_root.parent==Path('/tmp')
            and control_root.name.startswith('cal-T03-margin-') and path.parent==control_root,'owned flat protected margin root required')
        require(type(root_identity) is tuple and len(root_identity)==4,'independent margin root identity required')
    fds=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
        for name in path.parts[1:-1]:
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(fd)
            links.append((parent,name,fd,identity(os.fstat(fd))));parent=fd
        if control_root is not None:require(identity(os.fstat(parent))==root_identity and root_identity[2]==os.getuid() and root_identity[3]==0o700,'protected margin root custody differs')
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size<=max_bytes,'bounded regular selected bytes required')
        if control_root is not None:require(before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600,'protected margin input custody differs')
        pieces=[];size=0
        while True:
            piece=os.read(fd,1024*1024)
            if not piece:break
            size+=len(piece);require(size<=before.st_size and size<=max_bytes,'capture grew');pieces.append(piece)
        raw=b''.join(pieces);require(size==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)),'selected leaf changed')
        for p,n,h,expected in links:require(identity(os.stat(n,dir_fd=p,follow_symlinks=False))==identity(os.fstat(h))==expected,'selected directory attachment changed')
        require(sha(raw)==pin,'selected digest differs');return raw
    finally:
        for fd in reversed(fds):os.close(fd)

def capture_binding(root,binding):
    require(type(binding) is dict and set(binding)=={'path','sha256'},'closed independent software binding')
    return capture(Path(root)/relative(binding['path']),binding['sha256'])


def membership(root,expected):
    """No-follow descriptor tree observation, no unknown body reads."""
    root=Path(root);require(root.is_absolute(),'absolute installation root required');fds=[];links=[];names=set()
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
        for name in root.parts[1:]:
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(child)
            links.append((parent,name,child,identity(os.fstat(child))));parent=child
        require(os.fstat(parent).st_uid==os.getuid() and stat.S_IMODE(os.fstat(parent).st_mode)==0o700,'installed root custody differs')
        def walk(fd,prefix):
            before=set(os.listdir(fd))
            for name in sorted(before):
                st=os.stat(name,dir_fd=fd,follow_symlinks=False);require(not stat.S_ISLNK(st.st_mode),'unselected installed symlink')
                path=prefix+name
                if stat.S_ISDIR(st.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);fds.append(child)
                    links.append((fd,name,child,identity(os.fstat(child))));walk(child,path+'/')
                else:require(stat.S_ISREG(st.st_mode),'unselected installation object');names.add(path)
            require(before==set(os.listdir(fd)),'installed membership changed')
        walk(parent,'')
        for p,n,h,expected_identity in links:require(identity(os.stat(n,dir_fd=p,follow_symlinks=False))==identity(os.fstat(h))==expected_identity,'installed attachment changed')
        require(names==set(expected) or names==set(expected)|{'installation.json'},'unselected installed membership')
        return len(names)
    finally:
        for fd in reversed(fds):os.close(fd)


class JournalBoundary:
    """Hold owned selected distinct directories and lock identities, no locks.

    Prevent own-lock recursion; original journal readers remain untouched and
    retain their independent path/body qualification obligations.
    """
    def __init__(self,journal,host):
        self.paths=(Path(journal),Path(host));self.fds=[];self.links=[];self.root_fds=[];self.lock_fds=[]
    def __enter__(self):
        try:
            for root in self.paths:
                require(root.is_absolute() and root.is_relative_to('/tmp') and root.as_posix()==str(root) and '..' not in root.parts,'owned canonical journal root required')
                parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fds.append(parent)
                for name in root.parts[1:]:
                    fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);self.fds.append(fd)
                    self.links.append((parent,name,fd,identity(os.fstat(fd))));parent=fd
                selected=identity(os.fstat(parent));require(selected[2:]==(os.getuid(),0o700),'journal root custody differs');self.root_fds.append(parent)
                fd=os.open('.lock',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);self.fds.append(fd)
                st=os.fstat(fd);require(stat.S_ISREG(st.st_mode) and identity(st)[2:]==(os.getuid(),0o600) and st.st_nlink==1,'journal lock custody differs');self.lock_fds.append(fd)
                self.links.append((parent,'.lock',fd,identity(st)))
            require(identity(os.fstat(self.root_fds[0]))[:2]!=identity(os.fstat(self.root_fds[1]))[:2],'assessment journal is its held Vault')
            require(identity(os.fstat(self.lock_fds[0]))[:2]!=identity(os.fstat(self.lock_fds[1]))[:2],'assessment journal shares held Vault lock')
            self.check();return self
        except BaseException:self.close();raise
    def check(self):
        for parent,name,fd,selected in self.links:
            require(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(fd))==selected,'journal selected attachment changed')
    def close(self):
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]
    def __exit__(self,*exc):
        try:self.check()
        finally:self.close()
