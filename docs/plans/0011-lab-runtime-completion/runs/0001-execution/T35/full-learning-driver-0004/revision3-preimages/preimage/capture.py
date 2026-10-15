"""Qualification-only anchored metadata/software capture; no live effect authority."""
import hashlib,os,stat,sys,types
from pathlib import Path

def require(value,message):
    if not value:raise ValueError(message)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def stamp(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def directory_stamp(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode)

def _capture(path,pin,limit,owned=None):
    path=Path(path);require(path.is_absolute() and '..' not in path.parts,'canonical absolute input required')
    handles=[];links=[];owned_verified=False
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(fd)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            links.append((fd,part,directory_stamp(os.fstat(child))));handles.append(child);fd=child
            if owned is not None and Path('/').joinpath(*path.parts[1:len(handles)])==owned[0]:
                st=os.fstat(child)
                require([st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]==owned[1] and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,'owned root custody differs');owned_verified=True
        require(owned is None or owned_verified,'owned root was not selected before leaf open')
        leaf=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd);handles.append(leaf)
        before=os.fstat(leaf);require(stat.S_ISREG(before.st_mode) and before.st_size<=limit,'bounded regular source required')
        if owned is not None:require(before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600,'owned snapshot file custody differs')
        parts=[];size=0
        while True:
            block=os.read(leaf,min(1024*1024,limit+1-size))
            if not block:break
            parts.append(block);size+=len(block);require(size<=limit,'input exceeds bounded capture')
        raw=b''.join(parts)
        require(stamp(before)==stamp(os.fstat(leaf))==stamp(os.stat(path.name,dir_fd=fd,follow_symlinks=False)),'source leaf changed during capture')
        for parent,name,selected in reversed(links):require(directory_stamp(os.stat(name,dir_fd=parent,follow_symlinks=False))==selected,'source ancestor detached during capture')
        require(owned is not None or sha(raw)==pin,'independent source digest differs');return raw
    finally:
        for fd in reversed(handles):os.close(fd)

def read(path,pin,limit=128*1024*1024):
    import re
    require(type(pin) is str and re.fullmatch('[a-f0-9]{64}',pin) is not None,'independent exact software digest mandatory')
    return _capture(path,pin,limit)

def read_owned(path,root,selected_identity,limit=128*1024*1024):
    path=Path(path);root=Path(root)
    require(root.is_absolute() and root.is_relative_to('/tmp') and path.is_relative_to(root),'owned tmp snapshot path required')
    require(path.suffix not in {'.pem','.key','.der'} and not any(part=='.env' or part.startswith('.env.') for part in path.parts),'credential snapshot input excluded')
    require(type(selected_identity) is list and len(selected_identity)==4,'independent fresh owned root identity required')
    return _capture(path,None,limit,(root,selected_identity))

def module(name,path,raw,package=False):
    require(name not in sys.modules,'unselected cached module collision')
    result=types.ModuleType(name);result.__file__=str(path);result.__package__=name if package else name.rpartition('.')[0]
    if package:result.__path__=[str(Path(path).parent)]
    sys.modules[name]=result
    try:exec(compile(raw,str(path),'exec'),result.__dict__)
    except BaseException:sys.modules.pop(name,None);raise
    return result
