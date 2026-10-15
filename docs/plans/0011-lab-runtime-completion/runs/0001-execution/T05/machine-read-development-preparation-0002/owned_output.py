"""Exclusive, descriptor-held public evidence outputs for one T05 attempt."""
import hashlib,json,os,re,stat
from pathlib import Path

def need(ok,why):
    if not ok:raise ValueError(why)
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def identity(st):return [st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]
class Output:
    def __init__(self,custody):
        need(type(custody)is dict and set(custody)=={'root','identity'},'closed output custody required')
        root=custody['root'];selected=custody['identity']
        need(type(root)is str and re.fullmatch('/tmp/cal-T05-[A-Za-z0-9_-]+',root),'explicit own T05 output root required')
        need(type(selected)is list and len(selected)==4 and all(type(v)is int for v in selected) and selected[2:]==[os.getuid(),0o700],'explicit owned0700 identity required')
        self.fds=[];self.links=[];self.observations=None;self.count=0
        try:
            parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fds.append(parent)
            for part in Path(root).parts[1:]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);self.fds.append(child)
                self.links.append((parent,part,child,identity(os.fstat(child))));parent=child
            self.fd=parent;self.selected=selected;self.check()
            need(os.listdir(self.fd)==[],'output root must be empty before any runtime effect')
            self.write('started.json',{'schema_version':'lab-T05-owned-attempt-start/v1','authority_effect':'none','runtime_started':False})
            os.mkdir('observations',0o700,dir_fd=self.fd)
            self.observations=os.open('observations',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
            self.obs_identity=identity(os.fstat(self.observations));os.fsync(self.fd)
        except BaseException:self.close();raise
    def check(self):
        need(identity(os.fstat(self.fd))==self.selected,'owned output identity changed')
        for parent,part,child,selected in self.links:
            need(identity(os.stat(part,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(child))==selected,'owned output ancestor detached')
        if self.observations is not None:
            need(identity(os.stat('observations',dir_fd=self.fd,follow_symlinks=False))==identity(os.fstat(self.observations))==self.obs_identity,'owned observations detached')
    def write(self,leaf,value,observed=False):
        need(type(leaf)is str and re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9._-]*',leaf),'flat output leaf required')
        self.check();parent=self.observations if observed else self.fd
        raw=encoded(value);fd=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
        try:
            before=os.fstat(fd);offset=0
            while offset<len(raw):offset+=os.write(fd,raw[offset:])
            os.fsync(fd);after=os.stat(leaf,dir_fd=parent,follow_symlinks=False)
            need((before.st_dev,before.st_ino)==(after.st_dev,after.st_ino) and stat.S_ISREG(after.st_mode) and stat.S_IMODE(after.st_mode)==0o600,'output leaf detached')
            self.check();os.fsync(parent)
        finally:os.close(fd)
        return hashlib.sha256(raw).hexdigest()
    def observe(self,value):
        self.count+=1;return self.write('call-%06d.json'%self.count,value,observed=True)
    def close(self):
        if self.observations is not None:os.close(self.observations);self.observations=None
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]
