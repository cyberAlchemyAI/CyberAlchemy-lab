"""Stage exact public execution bytes in a fresh owned directory; retain failures."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import zipfile
import preflight as P

def owned_directory(path, expected):
    path=Path(path)
    P.require(path.is_absolute() and '..' not in path.parts,'absolute owned installation parent required')
    handles=[]
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(fd)
        for part in path.parts[1:]:
            fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);handles.append(fd)
        info=os.fstat(fd)
        P.require((info.st_dev,info.st_ino)==expected,'installation parent identity differs')
        P.require(info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,'installation parent must be owned mode0700')
        return handles,fd
    except BaseException:
        for handle in reversed(handles):os.close(handle)
        raise

def selected_bytes(row):
    # Every original file is rechecked after reading the copied bytes.
    before=P.anchored_read(row['path'],expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
    fd=os.open(row['path'],os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        P.require((info.st_dev,info.st_ino)==(before['device'],before['inode']),'selected source identity changed')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(row['size_bytes']+1)
        P.require(len(raw)==row['size_bytes'] and P.digest(raw)==row['sha256'],'selected source bytes changed')
    finally:os.close(fd)
    after=P.anchored_read(row['path'],expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
    P.require(before==after,'selected source changed during copy')
    return raw

def wheel_files(raw):
    files={};total=0
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        P.require(len(archive.infolist())<=10000,'wheel entry budget exceeded')
        for entry in archive.infolist():
            name=entry.filename;parts=PurePosixPath(name).parts
            P.require(name and not name.startswith('/') and '\\' not in name and '..' not in parts and '.' not in parts,'unsafe wheel path')
            P.require(stat.S_IFMT(entry.external_attr>>16)!=stat.S_IFLNK,'wheel symlink refused')
            if entry.is_dir():continue
            P.require(name==PurePosixPath(name).as_posix() and '.data' not in parts and not name.endswith('.pth'),'wheel hook or noncanonical path refused')
            P.require(name not in files and entry.file_size<=32*1024*1024,'wheel duplicate or file budget exceeded')
            total+=entry.file_size;P.require(total<=128*1024*1024,'wheel expansion budget exceeded')
            files[name]=archive.read(entry)
    return files

def write_file(root,name,raw,mode):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
    with os.fdopen(fd,'wb') as stream:
        os.fchmod(stream.fileno(),mode);stream.write(raw);stream.flush();os.fsync(stream.fileno())

def install(selection_path,selection_sha256,parent,parent_identity,name):
    P.require(name and len(name)<=64 and name.replace('-','').isalnum(),'bounded installation name required')
    verified=P.verify(selection_path,selection_sha256)
    raw_selection=Path(selection_path).read_bytes()
    P.require(P.digest(raw_selection)==selection_sha256,'selection changed before staging')
    selection=P.parse(raw_selection)
    handles,parent_fd=owned_directory(parent,parent_identity)
    try:
        os.mkdir(name,mode=0o700,dir_fd=parent_fd) # Exclusive; existing generations are never adopted or replaced.
        child_fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent_fd);handles.append(child_fd)
        child_identity=P.directory_identity(os.fstat(child_fd))
        scoped=Path('/proc/self/fd')/str(child_fd)
        copied={}
        for row in selection['inputs']:
            if row['kind']=='host-abi':continue # Host ABI remains independently pinned, external and unmodified.
            raw=selected_bytes(row)
            if row['kind']=='wheel':
                names={'wheels/'+Path(row['path']).name:(raw,0o644)}
                names.update({'deps/'+n:(b,0o644) for n,b in wheel_files(raw).items()})
            else:names={'bin/'+('python' if row['kind']=='interpreter' else 'lab-context-native-reader'):(raw,0o755)}
            for relative,(value,mode) in names.items():
                P.require(relative not in copied,'dependency output collision')
                write_file(scoped,relative,value,mode)
                copied[relative]={'sha256':P.digest(value),'size_bytes':len(value),'mode':mode}
        # Validate via the canonical retained path; a moved/replaced parent fails closed.
        destination=Path(parent)/name
        current=os.stat(destination,follow_symlinks=False)
        P.require(P.directory_identity(current)==child_identity,'installation directory identity changed')
        for relative,row in copied.items():
            P.anchored_read(destination/relative,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
        code="import sys,json,platform,sqlite3,importlib.metadata;sys.path.insert(0,sys.argv[1]);print(json.dumps({'python_version':platform.python_version(),'sqlite_version':sqlite3.sqlite_version,'versions':{n:importlib.metadata.version(n) for n in json.loads(sys.argv[2])}}))"
        clean={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
        process=subprocess.run([str(destination/'bin/python'),'-I','-B','-c',code,str(destination/'deps'),json.dumps(list(selection['versions']))],capture_output=True,timeout=30,env=clean)
        P.require(process.returncode==0,'fresh dependency interpreter refused')
        probe=P.parse(process.stdout)
        P.require(probe=={'python_version':selection['environment']['python_version'],'sqlite_version':selection['environment']['sqlite_version'],'versions':selection['versions']},'fresh dependency versions differ')
        native=subprocess.run([str(destination/'bin/lab-context-native-reader')],capture_output=True,timeout=10,env=clean)
        P.require(native.returncode==1 and native.stdout==b'' and native.stderr==b'usage: lab-context-native-reader semantic-dir governance-dir request.json\n','native ABI/entrypoint probe differs')
        P.verify(selection_path,selection_sha256)
        for relative,row in copied.items():P.anchored_read(destination/relative,expected_sha256=row['sha256'],expected_size=row['size_bytes'],expected_mode=row['mode'])
        P.require(P.directory_identity(os.stat(destination,follow_symlinks=False))==child_identity,'installed generation changed')
        refreshed,_=owned_directory(parent,parent_identity)
        for fd in reversed(refreshed):os.close(fd)
        actual=set()
        for path in destination.rglob('*'):
            P.require(not path.is_symlink(),'unexpected installed symlink')
            if path.is_file():actual.add(path.relative_to(destination).as_posix())
        P.require(actual==set(copied),'unselected installed dependency file')
        report={'schema_version':'lab-runtime-dependency-install/v1-candidate','result':'PASS','selection_sha256':selection_sha256,'destination':str(destination),'directory_identity':list(child_identity),'installed_files':copied,'fresh_python_probe':probe,'native_abi_entrypoint_probe':{'exit_code':native.returncode,'expected_usage_observed':True},'original_preflight':verified,'native_history_replay_proven':False,'runtime_start_proven':False,'source_locators_rewritten':False,'host_stdlib_external':True,'authority_effect':'none','claim_ceiling':'Fresh owned public dependency staging and exact host ABI entrypoint only; full source/protected-input packaging and Lab operation remain unproven.'}
        write_file(scoped,'installation.json',(json.dumps(report,sort_keys=True,indent=2)+'\n').encode(),0o600)
        os.fsync(child_fd);os.fsync(parent_fd)
        return report
    finally:
        for fd in reversed(handles):os.close(fd)

def main():
    p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--sha256',required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--device',type=int,required=True);p.add_argument('--inode',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    result=install(a.selection,a.sha256,a.parent,(a.device,a.inode),a.name)
    print(json.dumps({'result':result['result'],'files':len(result['installed_files']),'destination':result['destination']}))

if __name__=='__main__':main()
