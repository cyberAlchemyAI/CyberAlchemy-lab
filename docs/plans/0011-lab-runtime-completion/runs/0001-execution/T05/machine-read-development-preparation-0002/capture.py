"""One captured byte string, held no-follow ancestors/leaf, exact stable origin."""
import hashlib,os,re,stat
from pathlib import Path

def need(ok,reason):
    if not ok:raise ValueError(reason)
def capture_path(path,expected_sha256=None,*,maximum=32*1024*1024,required_uid=None):
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts and path.as_posix()==str(path),'canonical absolute captured origin required')
    need(expected_sha256 is None or type(expected_sha256)is str and re.fullmatch('[a-f0-9]{64}',expected_sha256),'independent exact capture SHA required')
    need(type(maximum)is int and 0<maximum<=32*1024*1024,'bounded capture required')
    handles=[];links=[]
    def directory_identity(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
    def stamp(s):return (*directory_identity(s),s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            selected=directory_identity(os.fstat(child))
            need(directory_identity(os.stat(part,dir_fd=parent,follow_symlinks=False))==selected,'capture ancestor detached while opening')
            links.append((parent,part,child,selected));parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size<=maximum,'bounded regular captured input required')
        need(required_uid is None or before.st_uid==required_uid,'captured input owner differs')
        parts=[];total=0
        while block:=os.read(fd,min(1024*1024,maximum-total+1)):
            total+=len(block);need(total<=before.st_size and total<=maximum,'captured input grew');parts.append(block)
        raw=b''.join(parts)
        need(total==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)),'captured file changed/detached')
        need(expected_sha256 is None or hashlib.sha256(raw).hexdigest()==expected_sha256,'independent captured input digest differs')
        for parent,name,held,selected in links:
            need(directory_identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==directory_identity(os.fstat(held))==selected,'held capture ancestor detached')
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)),'capture leaf changed before return')
        return raw
    finally:
        for fd in reversed(handles):os.close(fd)
