"""Same-byte source capture and scoped code loader; no effect authority."""
import hashlib
import importlib.abc
import importlib.util
import os
from pathlib import Path
import stat
import sys


def require(v, m):
    if not v: raise ValueError(m)


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


def execute(name, path, raw, package=False):
    spec=importlib.util.spec_from_loader(name, loader=None, origin=str(path), is_package=package)
    module=importlib.util.module_from_spec(spec); module.__file__=str(path)
    if package: module.__path__=[str(Path(path).parent)]
    sys.modules[name]=module
    try: exec(compile(raw, str(path), 'exec'), module.__dict__)
    except BaseException: sys.modules.pop(name, None); raise
    return module


class CapturedFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Only the unique engine namespace; compile captured selected byte strings."""
    def __init__(self, name, root, files): self.name=name; self.root=Path(root); self.files=files
    def find_spec(self, fullname, path=None, target=None):
        if fullname!=self.name and not fullname.startswith(self.name+'.'): return None
        rel=fullname[len(self.name):].lstrip('.').replace('.', '/')
        choices=[rel+'/__init__.py', rel+'.py'] if rel else ['__init__.py']
        for key in choices:
            if key in self.files:
                return importlib.util.spec_from_loader(fullname, self, origin=str(self.root/key), is_package=key.endswith('/__init__.py') or key=='__init__.py')
        return None
    def create_module(self, spec): return None
    def exec_module(self, module):
        key=Path(module.__spec__.origin).relative_to(self.root).as_posix()
        module.__file__=module.__spec__.origin
        if key.endswith('/__init__.py') or key=='__init__.py': module.__path__=[str(Path(module.__file__).parent)]
        exec(compile(self.files[key], module.__file__, 'exec'), module.__dict__)
