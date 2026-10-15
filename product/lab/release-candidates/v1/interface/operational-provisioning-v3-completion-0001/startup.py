"""Externally pinned same-byte component startup; candidate effect ceiling only."""
import hashlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent

def require(v,m):
    if not v:raise ValueError(m)

def stamp(s):
    return (s.st_dev, s.st_ino, s.st_uid, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def directory_stamp(s): return (s.st_dev, s.st_ino, s.st_uid, s.st_mode)


def capture(path, digest, limit=128*1024*1024):
    path=Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'absolute canonical input required')
    fds=[]; ancestry=[]
    try:
        parent=os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW); fds.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW, dir_fd=parent)
            ancestry.append((parent, part, directory_stamp(os.fstat(child))))
            fds.append(child); parent=child
        fd=os.open(path.name, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK, dir_fd=parent); fds.append(fd)
        before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size<=limit, 'bounded regular software input required')
        parts=[]; total=0
        while True:
            block=os.read(fd, min(1024*1024, limit+1-total))
            if not block: break
            parts.append(block); total+=len(block); require(total<=limit, 'software input too large')
        raw=b''.join(parts)
        require(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False)), 'input attachment changed during capture')
        for p, name, selected in reversed(ancestry):
            require(directory_stamp(os.stat(name, dir_fd=p, follow_symlinks=False))==selected, 'input ancestor attachment changed during capture')
        require(hashlib.sha256(raw).hexdigest()==digest, 'independent software digest differs: '+str(path))
        return raw
    finally:
        for fd in reversed(fds): os.close(fd)


def main(pin, action, *args):
    manifest_raw=capture(HERE/'source-manifest.json',pin)
    manifest=json.loads(manifest_raw)
    require(manifest['authority_effect']=='none' and manifest['task_complete'] is False,'candidate source selection required')
    rows={row['path']:row for row in manifest['files']}
    require(len(rows)==len(manifest['files']),'duplicate selected source')
    selected={}
    for path,row in rows.items():
        raw=capture(ROOT/path,row['sha256'])
        if Path(path).parent==HERE.relative_to(ROOT) and Path(path).suffix=='.py':selected[Path(path).stem]=raw
    class Finder(importlib.abc.MetaPathFinder,importlib.abc.Loader):
        def find_spec(self,fullname,path=None,target=None):
            if fullname in selected:return importlib.util.spec_from_loader(fullname,self,origin=str(HERE/(fullname+'.py')))
        def create_module(self,spec):return None
        def exec_module(self,module):
            module.__file__=module.__spec__.origin
            exec(compile(selected[module.__name__],module.__file__,'exec'),module.__dict__)
    finder=Finder();sys.meta_path.insert(0,finder)
    try:
        if action=='qualify':
            import qualify
            qualify.main(pin,*args)
        elif action=='worker':
            import checks
            checks.SOURCE_PIN=pin
            checks.worker(*args)
        else:raise ValueError('unknown captured startup action')
    finally:
        sys.meta_path.remove(finder)
        for name in selected:sys.modules.pop(name,None)

if __name__=='__main__':main(*sys.argv[1:])
