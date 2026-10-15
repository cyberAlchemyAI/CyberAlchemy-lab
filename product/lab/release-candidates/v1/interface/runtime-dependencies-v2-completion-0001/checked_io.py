"""Exact local dependency readiness; does not install or authorize an effect."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sqlite3
import stat
import sys

ROOT=Path(__file__).resolve().parents[6]
KINDS={'wheel','host-abi','native-executable','interpreter'}

def require(ok,message):
    if not ok:raise ValueError(message)

def parse(raw):
    def pairs(rows):
        out={}
        for key,value in rows:
            require(key not in out,'duplicate dependency field');out[key]=value
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite value')))

def digest(raw):return hashlib.sha256(raw).hexdigest()

def identity(value):
    return value.st_dev,value.st_ino,value.st_size,value.st_mode,value.st_uid,value.st_mtime_ns,value.st_ctime_ns

def directory_identity(value):
    return value.st_dev,value.st_ino,value.st_mode,value.st_uid

def anchored_read(path, *, expected_sha256, expected_size=None, expected_mode=None):
    path=Path(path)
    require(path.is_absolute() and str(path)==str(path.absolute()) and '..' not in path.parts,'canonical absolute dependency path required')
    require(path.suffix not in ('.pem','.key','.pyc') and not any(x=='.env' or x.startswith('.env.') for x in path.parts),'credential/cache dependency rejected')
    opened=[];stamps=[]
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);opened.append(fd)
        for part in path.parts[1:-1]:
            next_fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            stamps.append((fd,part,directory_identity(os.fstat(next_fd))));opened.append(next_fd);fd=next_fd
        handle=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd);opened.append(handle)
        before=os.fstat(handle);require(stat.S_ISREG(before.st_mode),'regular dependency required')
        require(expected_size is None or before.st_size==expected_size,'dependency size differs')
        require(expected_mode is None or stat.S_IMODE(before.st_mode)==expected_mode,'dependency mode differs')
        h=hashlib.sha256();total=0
        while block:=os.read(handle,1024*1024):h.update(block);total+=len(block)
        after=os.fstat(handle);current=os.stat(path.name,dir_fd=fd,follow_symlinks=False)
        require(identity(before)==identity(after)==identity(current) and total==before.st_size,'dependency changed during read')
        require(h.hexdigest()==expected_sha256,'dependency digest differs')
        for parent,name,expected in stamps:
            require(directory_identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==expected,'dependency ancestry changed')
        return {'path':str(path),'sha256':h.hexdigest(),'size_bytes':total,'mode':stat.S_IMODE(before.st_mode),'uid':before.st_uid,'device':before.st_dev,'inode':before.st_ino,'mtime_ns':before.st_mtime_ns,'ctime_ns':before.st_ctime_ns}
    finally:
        for fd in reversed(opened):os.close(fd)

def environment():
    exe=Path(sys.executable).resolve()
    return {'python_version':platform.python_version(),'implementation':platform.python_implementation(),'machine':platform.machine(),'system':platform.system(),'libc':list(platform.libc_ver()),'sqlite_version':sqlite3.sqlite_version,'interpreter_sha256':digest(exe.read_bytes())}

def verify(selected_path, expected_sha256):
    selected_path=Path(selected_path)
    require(not any(p.is_symlink() for p in [selected_path,*selected_path.parents]),'dependency selection symlink rejected')
    raw=selected_path.read_bytes();require(digest(raw)==expected_sha256,'independent dependency selection differs')
    selection=parse(raw)
    require(set(selection)=={'schema_version','environment','versions','inputs','original_bindings','supported_scope','authority_effect','actual_owner_outcome'},'closed dependency selection required')
    require(selection['schema_version']=='lab-runtime-dependency-preflight/v1-candidate' and selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'dependency selection cannot grant authority')
    require(environment()==selection['environment'],'exact local runtime environment differs')
    require({name:importlib.metadata.version(name) for name in selection['versions']}==selection['versions'],'selected package versions differ')
    require(len(selection['inputs'])==len({r['path'] for r in selection['inputs']}),'duplicate dependency path')
    counts={kind:0 for kind in KINDS};verified=[]
    for row in selection['inputs']:
        fields={'kind','path','sha256','size_bytes','mode'}|({'distribution','version'} if row['kind']=='wheel' else set())
        require(set(row)==fields and row['kind'] in KINDS,'closed typed dependency input required')
        counts[row['kind']]+=1;path=Path(row['path'])
        if row['kind']=='wheel':
            require(path.is_relative_to(ROOT/'product/lab/release-candidates/v1/packaging/R02') and path.suffix=='.whl' and selection['versions'].get(row['distribution'])==row['version'],'independently selected exact wheel required')
        elif row['kind']=='host-abi':require(path.name in {'ld-linux-x86-64.so.2','libgcc_s.so.1','libc.so.6'} and path.parent==Path('/usr/lib/x86_64-linux-gnu'),'declared host ABI library required')
        elif row['kind']=='native-executable':require(path.name=='lab-context-native-reader' and row['mode']==0o755,'selected executable locator/mode required')
        else:require(path==Path(sys.executable).resolve() and row['sha256']==selection['environment']['interpreter_sha256'],'selected interpreter differs')
        verified.append(anchored_read(path,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode']))
    require(counts=={'wheel':len(selection['versions']),'host-abi':3,'native-executable':1,'interpreter':1},'complete local execution dependency categories required')
    for row in selection['original_bindings']:
        require(set(row)=={'path','sha256'},'closed original input binding required')
        path=ROOT/row['path'];require(path.is_relative_to(ROOT) and '..' not in path.parts,'original input outside repository')
        anchored_read(path,expected_sha256=row['sha256'])
    require(selected_path.read_bytes()==raw,'selection changed during preflight')
    for row in verified:
        current=os.stat(row['path'],follow_symlinks=False)
        require((current.st_dev,current.st_ino,current.st_size,stat.S_IMODE(current.st_mode),current.st_uid,current.st_mtime_ns,current.st_ctime_ns)==(row['device'],row['inode'],row['size_bytes'],row['mode'],row['uid'],row['mtime_ns'],row['ctime_ns']),'dependency changed after preflight')
    return {'schema_version':'lab-runtime-dependency-preflight-result/v1-candidate','result':'PASS','selected_sha256':expected_sha256,'environment':selection['environment'],'verified_inputs':verified,'versions':selection['versions'],'native_executed':False,'native_installed':False,'source_locators_rewritten':False,'execution_authorized':False,'authority_effect':'none','claim_ceiling':'Exact selected current local dependency bytes/environment only; no installation, service readiness, permission, platform portability or runtime qualification.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection',type=Path,required=True);parser.add_argument('--selection-sha256',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    value=verify(args.selection,args.selection_sha256)
    with args.output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'verified_inputs':len(value['verified_inputs'])}));return 0

if __name__=='__main__':raise SystemExit(main())
