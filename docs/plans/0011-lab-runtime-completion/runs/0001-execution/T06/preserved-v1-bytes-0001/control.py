"""Closed independently selected public and protected control locators."""
import hashlib,json,os,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
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
def stamp(s):return [*ident(s),s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def closed(value,fields):need(type(value) is dict and set(value)==set(fields.split()),'closed control shape required')
def canonical(path):
    p=Path(path);need(p.is_absolute() and str(p)==os.path.normpath(str(p)),'canonical absolute locator required');return p
def directory(path,identity):
    p=canonical(path);fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in p.parts[1:]:
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
        need(ident(os.fstat(fd))==identity and identity[2:]==[os.getuid(),0o700],'owned directory preimage differs')
        return fd
    except BaseException:os.close(fd);raise
def public(binding):
    closed(binding,'path sha256');rel=Path(binding['path']);need(not rel.is_absolute() and '..' not in rel.parts,'safe public source locator required')
    path=ROOT/rel;need(path.is_file() and not any(p.is_symlink() for p in [path,*path.parents]),'public source unavailable')
    raw=path.read_bytes();need(sha(raw)==binding['sha256'],'public source bytes differ');return raw
def protected(selector,root,root_identity,limit=16*1024*1024):
    closed(selector,'path identity sha256');path=canonical(selector['path']);anchor=canonical(root)
    need(path.is_relative_to(anchor) and not anchor.is_relative_to(ROOT),'selected protected file outside owned external root')
    parent=directory(anchor,root_identity);parents=[parent]
    try:
        parts=path.relative_to(anchor).parts;need(parts,'protected file locator required')
        for part in parts[:-1]:
            parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);parents.append(parent)
            s=os.fstat(parent);need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,'protected nested directory mode differs')
        fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        try:
            before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and ident(before)==selector['identity'] and selector['identity'][2:]==[os.getuid(),0o600] and before.st_size<=limit,'protected input preimage/mode/type differs')
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(limit+1)
            need(len(raw)<=limit and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(parts[-1],dir_fd=parent,follow_symlinks=False)),'protected input changed during read')
            need(sha(raw)==selector['sha256'],'protected input digest differs')
        finally:os.close(fd)
        later=directory(anchor,root_identity);os.close(later);return raw
    finally:
        for fd in reversed(parents):os.close(fd)
