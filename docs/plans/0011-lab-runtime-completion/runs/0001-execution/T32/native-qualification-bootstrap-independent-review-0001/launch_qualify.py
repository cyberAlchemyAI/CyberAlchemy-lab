"""Inactive Root launcher: selected vendor path precedes unchanged API guard.

Root must independently select these bytes and the external qualification packet.
This file has not launched a Lab/native episode during authoring or review.
"""
import argparse
import hashlib
import os
from pathlib import Path
import stat
import sys
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INSTALL = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
RUNNER = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-node-recovery-qualification-preparation-0001/qualify.py'
RUNNER_SHA = '8ef7402696a55aacfa05e327922ef68de41e3478b2393b4b5577a3e7ec32ccb2'

def capture(path, pin):
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('true absolute selected origin required')
    handles = []
    links = []
    identity = lambda s: (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        handles.append(parent)
        for part in path.parts[1:-1]:
            child = os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            handles.append(child)
            links.append((parent,part,child,identity(os.fstat(child))))
            parent = child
        fd = os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        handles.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= 1024*1024:
            raise ValueError('bounded regular selected launcher/runner required')
        chunks = []
        total = 0
        while total < before.st_size:
            chunk = os.read(fd,min(65536,before.st_size-total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        raw = b''.join(chunks)
        if len(raw) != before.st_size or os.read(fd,1) or identity(os.fstat(fd)) != identity(before):
            raise ValueError('selected code changed while captured')
        if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False)) != identity(before):
            raise ValueError('selected code attachment changed')
        for parent_fd,name,child,selected in links:
            if identity(os.stat(name,dir_fd=parent_fd,follow_symlinks=False)) != selected or identity(os.fstat(child)) != selected:
                raise ValueError('selected code ancestor changed')
        if hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError('independent selected code SHA differs')
        return raw
    finally:
        for fd in reversed(handles):
            os.close(fd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--launcher-sha256',required=True)
    parser.add_argument('--selection',required=True)
    parser.add_argument('--selection-sha256',required=True)
    args = parser.parse_args()
    if Path(sys.executable) != INSTALL/'bin/python' or not sys.dont_write_bytecode or not sys.flags.isolated or not sys.flags.no_site:
        raise ValueError('selected0004 -I -B -S Python required')
    own = Path(__file__).absolute()
    capture(own,args.launcher_sha256)
    raw = capture(RUNNER,RUNNER_SHA)
    # Qualification still performs its original complete current Source/installed
    # checks; this fixes only the original bare-launch metadata import ordering.
    sys.path.insert(0,str(INSTALL/'deps'))
    name = '_T32_independently_selected_qualification_runner'
    if name in sys.modules:
        raise ValueError('fresh runner namespace required')
    module = types.ModuleType(name)
    module.__file__ = str(RUNNER)
    sys.modules[name] = module
    try:
        exec(compile(raw,str(RUNNER),'exec'),module.__dict__)
        capture(RUNNER,RUNNER_SHA)
        sys.argv = [str(RUNNER),'--selection',args.selection,'--selection-sha256',args.selection_sha256]
        return module.main()
    finally:
        if sys.modules.get(name) is module:
            del sys.modules[name]

if __name__ == '__main__':
    raise SystemExit(main())
