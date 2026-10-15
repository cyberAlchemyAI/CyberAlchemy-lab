"""Candidate own-component capture entry. Root must independently select this entry."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import sys
import types
import uuid
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent

def need(value,message):
    if not value:raise ValueError(message)

def parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            need(key not in value,'duplicate field');value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite'))

def stamp(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def capture(row):
    need(type(row) is dict and set(row)=={'path','sha256','size_bytes'},'closed component row')
    path=Path(row['path']);need(not path.is_absolute() and '..' not in path.parts and path.as_posix()==row['path'],'canonical public origin')
    path=ROOT/path;fds=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
    try:
        for part in path.parts[1:-1]:fds.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fds[-1]))
        fds.append(os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fds[-1]));before=os.fstat(fds[-1])
        need(stat.S_ISREG(before.st_mode) and before.st_size<=32*1024*1024,'bounded regular component')
        chunks=[]
        total=0
        while chunk:=os.read(fds[-1],min(1024*1024,32*1024*1024-total+1)):
            total+=len(chunk);need(total<=before.st_size and total<=32*1024*1024,'component grew beyond selected capture bound');chunks.append(chunk)
        raw=b''.join(chunks)
        need(len(raw)==row['size_bytes'] and sha256(raw).hexdigest()==row['sha256'] and stamp(before)==stamp(os.fstat(fds[-1])),'component bytes changed')
        for index,part in enumerate(path.parts[1:]):
            a=os.stat(part,dir_fd=fds[index],follow_symlinks=False);b=os.fstat(fds[index+1])
            need((a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid)==(b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid),'component detached')
        return raw
    finally:
        for fd in reversed(fds):os.close(fd)

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--manifest-size',required=True,type=int)
    parser.add_argument('--target',required=True,choices=['harness','controls'])
    parser.add_argument('arguments',nargs=argparse.REMAINDER)
    args=parser.parse_args(argv)
    rel=(HERE/'source-manifest.json').relative_to(ROOT).as_posix()
    manifest=parse(capture({'path':rel,'sha256':args.manifest_sha256,'size_bytes':args.manifest_size}))
    need(set(manifest)=={'schema_version','status','authority_effect','files'} and manifest['schema_version']=='lab-T06-development-harness-component/v2-candidate'
         and manifest['status']=='frozen-authoring-only-unrun' and manifest['authority_effect']=='none','wrong candidate component')
    rows=manifest['files'];need(type(rows) is list and len({r['path'] for r in rows})==len(rows),'duplicate component origin')
    captures={r['path']:capture(r) for r in rows}
    target=(HERE/(args.target+'.py')).relative_to(ROOT).as_posix();need(target in captures,'target not independently selected')
    name='_cal_T06_owned_'+uuid.uuid4().hex;need(name not in sys.modules,'unselected cached target')
    module=types.ModuleType(name);module.__file__=str(ROOT/target);module.__package__=None
    module.CAPTURED_COMPONENTS=types.MappingProxyType(captures);sys.modules[name]=module
    try:
        exec(compile(captures[target],module.__file__,'exec'),module.__dict__)
        forwarded=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
        return module.main(forwarded)
    finally:
        if sys.modules.get(name) is module:del sys.modules[name]

if __name__=='__main__':raise SystemExit(main())
