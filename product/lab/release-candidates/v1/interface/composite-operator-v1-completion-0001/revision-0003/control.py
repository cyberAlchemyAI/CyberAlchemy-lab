"""Closed independently selected public and protected control locators."""
import hashlib,json,os,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(raw):
    def pairs(items):
        result={}
        for key,value in items:need(key not in result,'duplicate control key');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite control value'))
def ident(s):return [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]
def stamp(s):return [*ident(s),s.st_gid,s.st_nlink,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def closed(value,fields):need(type(value) is dict and set(value)==set(fields.split()),'closed control shape required')
def canonical(path):
    need(type(path) in (str,type(Path('/'))) and type(path) is not bytes,'text/path locator required')
    original=str(path);p=Path(original);need(p.is_absolute() and p.as_posix()==original and original==os.path.normpath(original),'canonical absolute locator required');return p
def directory(path,identity):
    p=canonical(path);fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in p.parts[1:]:
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
        need(ident(os.fstat(fd))==identity and identity[2:]==[os.getuid(),0o700],'owned directory preimage differs')
        return fd
    except BaseException:os.close(fd);raise
def _attachments(links):
    for parent,name,held,expected in reversed(links):
        current=os.stat(name,dir_fd=parent,follow_symlinks=False);actual=os.fstat(held)
        need(stat.S_ISDIR(current.st_mode) and ident(current)==ident(actual)==expected,
             'capture ancestor attachment changed')
def _read_exact(fd,limit):
    chunks=[];size=0
    while True:
        chunk=os.read(fd,min(1024*1024,limit-size+1))
        if not chunk:break
        size+=len(chunk);need(size<=limit,'selected input exceeds byte bound');chunks.append(chunk)
    return b''.join(chunks)
def capture(path,digest,*,limit=64*1024*1024,expected_identity=None,owner=None,mode=None,size=None,anchor=None,anchor_identity=None):
    """One exact bounded capture; held ancestors and leaf checked before return."""
    import re
    path=canonical(path);need(path.name not in ('','.') and type(digest) is str and re.fullmatch('[a-f0-9]{64}',digest),'exact selected file/digest required')
    if anchor is not None:
        anchor=canonical(anchor);need(path.is_relative_to(anchor) and path!=anchor,'selected file must be below owned root')
    handles=[];links=[];file_handle=None;current=Path('/')
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for name in path.parts[1:-1]:
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            current=current/name;value=os.fstat(child);identity=ident(value)
            need(stat.S_ISDIR(value.st_mode) and stat.S_IMODE(value.st_mode)&0o111,'unsafe capture ancestor')
            attached=os.stat(name,dir_fd=parent,follow_symlinks=False);need(ident(attached)==identity and stat.S_ISDIR(attached.st_mode),'capture ancestor changed during open')
            if anchor is not None and current.is_relative_to(anchor):
                need(identity[2:]==[os.getuid(),0o700],'owned capture directory mode/owner differs')
                if current==anchor:need(identity==anchor_identity,'owned capture root preimage differs')
            links.append((parent,name,child,identity));parent=child
        _attachments(links)
        file_handle=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
        before=os.fstat(file_handle);need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode)&0o444 and before.st_size<=limit,'bounded regular readable file required')
        need(expected_identity is None or ident(before)==expected_identity,'selected file identity differs')
        need(owner is None or before.st_uid==owner,'selected file owner differs')
        need(mode is None or stat.S_IMODE(before.st_mode)==mode,'selected file mode differs')
        need(size is None or before.st_size==size,'selected file size differs')
        attached=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(attached.st_mode) and stamp(attached)==stamp(before),'capture file changed before read')
        raw=_read_exact(file_handle,limit)
        attached=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(attached.st_mode) and len(raw)==before.st_size and stamp(before)==stamp(os.fstat(file_handle))==stamp(attached),'capture file changed during read')
        need(sha(raw)==digest,'selected file digest differs')
        _attachments(links)
        attached=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(attached.st_mode) and stamp(before)==stamp(os.fstat(file_handle))==stamp(attached),'capture file changed before return')
        return raw
    except OSError as error:raise ValueError('selected file unsafe/unreadable/missing attachment') from error
    finally:
        if file_handle is not None:os.close(file_handle)
        for handle in reversed(handles):os.close(handle)
def public(binding):
    closed(binding,'path sha256');rel=Path(binding['path'])
    need(type(binding['path']) is str and rel.as_posix()==binding['path'] and str(rel) not in ('','.') and not rel.is_absolute() and '..' not in rel.parts and '\\' not in binding['path'],'safe public source locator required')
    return capture(ROOT/rel,binding['sha256'])
def protected(selector,root,root_identity,limit=16*1024*1024):
    closed(selector,'path identity sha256');path=canonical(selector['path']);anchor=canonical(root)
    need(path.is_relative_to(anchor) and not anchor.is_relative_to(ROOT),'selected protected file outside owned external root')
    need(type(selector['identity']) is list and len(selector['identity'])==4 and all(type(v) is int and v>=0 for v in selector['identity']) and selector['identity'][2:]==[os.getuid(),0o600],'selected protected identity owner/mode differs')
    return capture(path,selector['sha256'],limit=limit,expected_identity=selector['identity'],owner=os.getuid(),mode=0o600,anchor=anchor,anchor_identity=root_identity)
def installed(root,expected):
    """Complete selected byte/mode closure, no-follow directory enumeration."""
    root=canonical(root)
    for name,row in expected.items():
        relative=Path(name);need(type(name) is str and relative.as_posix()==name and not relative.is_absolute() and '..' not in relative.parts,'safe installed locator required')
        capture(root/relative,row['sha256'],limit=row['size_bytes'],owner=os.getuid(),mode=row['mode'],size=row['size_bytes'])
    # Walk held descriptors; inspect links without following them and recheck all
    # ancestor attachments after a full closed inventory, including extras.
    handles=[];links=[];files=set()
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for name in root.parts[1:]:
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            links.append((parent,name,child,ident(os.fstat(child))));parent=child
        def visit(fd,prefix):
            for name in os.listdir(fd):
                row=os.stat(name,dir_fd=fd,follow_symlinks=False);relative=prefix+name
                if stat.S_ISDIR(row.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);handles.append(child)
                    need(ident(row)==ident(os.fstat(child)),'installed directory changed during open');links.append((fd,name,child,ident(row)));visit(child,relative+'/')
                else:need(stat.S_ISREG(row.st_mode),'unselected installed special file');files.add(relative)
        visit(parent,'');_attachments(links);need(files==set(expected)|{'installation.json'},'installed dependency closure differs')
    finally:
        for handle in reversed(handles):os.close(handle)
    # Inventory traversal cannot substitute for a second fresh byte check.
    for name,row in expected.items():capture(root/name,row['sha256'],limit=row['size_bytes'],owner=os.getuid(),mode=row['mode'],size=row['size_bytes'])
    return len(expected)
