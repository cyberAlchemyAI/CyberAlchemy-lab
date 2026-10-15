"""Closed independently selected public and protected control locators."""
import hashlib,json,os,stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')  # Explicit unchanged repository origin for this versioned staged module.
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
    """Versioned whole proof: two fresh leaf reads, one held directory graph.

    Every expected payload retains the original exact SHA/size/mode/uid and
    full attachment/stamp checks. Only directory handles are reused inside
    this synchronous call. No bytes, stat facts or proofs survive the call.
    Receipt content remains separately selected by the original caller; here
    installation.json must be one regular member of the complete closed set.
    Extra empty directories retain the original acceptance behavior.
    """
    import re
    root=canonical(root)
    selected=[]
    for name,row in expected.items():
        relative=Path(name)
        need(type(name)is str and relative.as_posix()==name and not relative.is_absolute()
             and '..'not in relative.parts and relative.parts,'safe installed locator required')
        need(type(row['sha256'])is str and re.fullmatch('[a-f0-9]{64}',row['sha256']),'exact selected file/digest required')
        selected.append((name,row['sha256'],row['size_bytes'],row['mode']))
    def _selection():
        need(selected==[(name,row['sha256'],row['size_bytes'],row['mode'])for name,row in expected.items()],
             'installed expected selection changed during proof')
    handles=[];links=[];directories={}
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        ancestry=[]
        for name in root.parts[1:]:
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            s=os.fstat(child);named=os.stat(name,dir_fd=parent,follow_symlinks=False)
            need(stat.S_ISDIR(named.st_mode)and ident(named)==ident(s),'installed ancestor changed during open')
            link=(parent,name,child,ident(s));links.append(link);ancestry.append(link);parent=child
        directories[()]=(parent,tuple(ancestry))
        _attachments(links)
        def _directory(parts):
            if parts in directories:return directories[parts]
            owner,chain=_directory(parts[:-1]);name=parts[-1]
            named=os.stat(name,dir_fd=owner,follow_symlinks=False)
            need(stat.S_ISDIR(named.st_mode),'installed selected parent is not a directory')
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=owner);handles.append(child)
            s=os.fstat(child);need(ident(named)==ident(s),'installed directory changed during open')
            link=(owner,name,child,ident(s));links.append(link)
            value=(child,chain+(link,));directories[parts]=value;return value
        def _prove_leaf(name,digest,limit,mode):
            relative=Path(name);parent,chain=_directory(relative.parts[:-1]);fd=None
            try:
                for _,_,held,_ in chain:
                    value=os.fstat(held)
                    need(stat.S_ISDIR(value.st_mode)and stat.S_IMODE(value.st_mode)&0o111,'unsafe capture ancestor')
                _attachments(chain)
                fd=os.open(relative.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
                before=os.fstat(fd)
                need(stat.S_ISREG(before.st_mode)and stat.S_IMODE(before.st_mode)&0o444 and before.st_size<=limit,
                     'bounded regular readable file required')
                need(before.st_uid==os.getuid(),'selected file owner differs')
                need(stat.S_IMODE(before.st_mode)==mode,'selected file mode differs')
                need(before.st_size==limit,'selected file size differs')
                named=os.stat(relative.name,dir_fd=parent,follow_symlinks=False)
                need(stat.S_ISREG(named.st_mode)and stamp(named)==stamp(before),'capture file changed before read')
                raw=_read_exact(fd,limit)
                named=os.stat(relative.name,dir_fd=parent,follow_symlinks=False)
                need(stat.S_ISREG(named.st_mode)and len(raw)==before.st_size
                     and stamp(before)==stamp(os.fstat(fd))==stamp(named),'capture file changed during read')
                need(sha(raw)==digest,'selected file digest differs')
                _attachments(chain)
                named=os.stat(relative.name,dir_fd=parent,follow_symlinks=False)
                need(stat.S_ISREG(named.st_mode)and stamp(before)==stamp(os.fstat(fd))==stamp(named),
                     'capture file changed before return')
            finally:
                if fd is not None:os.close(fd)
        def _inventory():
            files=set()
            def visit(parts):
                fd,chain=_directory(parts)
                for name in os.listdir(fd):
                    row=os.stat(name,dir_fd=fd,follow_symlinks=False);relative=parts+(name,)
                    if stat.S_ISDIR(row.st_mode):
                        child,child_chain=_directory(relative)
                        need(ident(row)==ident(os.fstat(child)),'installed directory changed during inventory')
                        visit(relative)
                    else:
                        need(stat.S_ISREG(row.st_mode),'unselected installed special file');files.add('/'.join(relative))
            visit(());_attachments(links)
            need(files=={r[0]for r in selected}|{'installation.json'},'installed dependency closure differs')
        for row in selected:_prove_leaf(*row)
        _selection();_inventory();_selection()
        # A new leaf FD and fresh read for every payload; no first-pass byte
        # result or open leaf is reused as second-pass evidence.
        for row in selected:_prove_leaf(*row)
        _selection();_inventory();_attachments(links)
        return len(selected)
    except OSError as error:
        raise ValueError('installed selected file/tree unsafe/unreadable/missing attachment')from error
    finally:
        for fd in reversed(handles):os.close(fd)
