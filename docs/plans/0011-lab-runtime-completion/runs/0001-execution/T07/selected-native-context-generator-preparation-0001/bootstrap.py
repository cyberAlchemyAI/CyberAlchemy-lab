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
    parser.add_argument('--target',required=True,choices=['cold_probe','build_package','controls'])
    parser.add_argument('arguments',nargs=argparse.REMAINDER)
    args=parser.parse_args(argv)
    rel=(HERE/'source-manifest.json').relative_to(ROOT).as_posix()
    manifest=parse(capture({'path':rel,'sha256':args.manifest_sha256,'size_bytes':args.manifest_size}))
    need(set(manifest)=={'schema_version','status','authority_effect','files'} and manifest['schema_version']=='lab-C08-selected-native-preparation/v1-candidate'
         and manifest['status']=='frozen-authoring-only-unrun' and manifest['authority_effect']=='none','wrong candidate component')
    rows=manifest['files'];need(type(rows) is list and len({r['path'] for r in rows})==len(rows),'duplicate component origin')
    captures={r['path']:capture(r) for r in rows}
    if args.target!='controls':
        # Original full1010 installed-byte guard precedes dependency/Lab imports.
        control_path='product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py'
        dep_path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
        need(sha256(captures[dep_path]).hexdigest()=='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835','independent selected0004 dependency pin differs')
        dep=parse(captures[dep_path]);installation=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
        need(Path(sys.executable)==installation/'bin/python','selected0004 interpreter required')
        control=types.ModuleType('_cal_C08_actual_dependency_control_'+uuid.uuid4().hex);control.__file__=str(ROOT/control_path)
        exec(compile(captures[control_path],control.__file__,'exec'),control.__dict__)
        expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind']in{'interpreter','native-executable'}else 0o644}for r in dep['inputs']}
        expected.update(dep['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
        need(len(expected)==1010,'full original installed closure required');control.installed(installation,expected)
        sys.path[:0]=[str(installation/'deps'),str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation'),str(ROOT/'implementation/lab-context/candidates/v1'),str(ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001')]
    target=(HERE/(args.target+'.py')).relative_to(ROOT).as_posix();need(target in captures,'target not independently selected')
    name='_cal_T06_owned_'+uuid.uuid4().hex;need(name not in sys.modules,'unselected cached target')
    package_name=name+'_package';package=types.ModuleType(package_name);package.__file__=str(HERE/'__init__.py');package.__path__=[str(HERE)];sys.modules[package_name]=package
    exec(compile(captures[(HERE/'__init__.py').relative_to(ROOT).as_posix()],package.__file__,'exec'),package.__dict__)
    module=types.ModuleType(name);module.__file__=str(ROOT/target);module.__package__=package_name
    module.CAPTURED_COMPONENTS=types.MappingProxyType(captures);sys.modules[name]=module
    try:
        exec(compile(captures[target],module.__file__,'exec'),module.__dict__)
        forwarded=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
        return module.main(forwarded)
    finally:
        if args.target!='controls':control.installed(installation,expected)
        for row in rows:capture(row)
        if sys.modules.get(name) is module:del sys.modules[name]

if __name__=='__main__':raise SystemExit(main())
