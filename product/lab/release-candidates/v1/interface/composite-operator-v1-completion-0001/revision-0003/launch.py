#!/usr/bin/env python3
"""Single maintained executable; public prechecks precede the selected runtime."""
import argparse,base64,fcntl,hashlib,json,os,re,stat,subprocess
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[6]
INSTALL=HERE.parents[1]/'runtime-dependencies-v2-completion-0001/installations/0004'
SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTION_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(value):
    if not value:raise ValueError('selected launcher bootstrap differs')
def _capture_exact(root, binding):
    """Capture <=64 MiB with exact SHA and fresh complete attachment checks."""
    def require(value, reason):
        if not value:
            raise ValueError(reason)
    require(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact capture binding required')
    name = binding['path']
    require(type(name) is str and bool(name) and '\\' not in name and '\x00' not in name,
            'unsafe capture path')
    path = PurePosixPath(name)
    require(path.as_posix() == name and '..' not in path.parts and name not in ('.', '/'), 'unsafe capture path')
    require(type(binding['sha256']) is str and re.fullmatch('[a-f0-9]{64}', binding['sha256']),
            'independent capture digest required')
    root = Path(root)
    require(root.is_absolute() and '..' not in root.parts, 'absolute capture root required')
    if not path.is_absolute():
        path = PurePosixPath(root.as_posix()) / path
    parts = path.parts[1:]
    directories = []
    file_handle = None
    links = []
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
                value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        directories.append(parent)
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=parent)
            directories.append(child)
            info = os.fstat(child)
            require(stat.S_ISDIR(info.st_mode) and info.st_mode & 0o111, 'unsafe capture ancestor')
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(attached.st_mode) and (attached.st_dev, attached.st_ino) ==
                    (info.st_dev, info.st_ino), 'capture ancestor changed during open')
            links.append((parent, part, child, info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid))
            parent = child
        file_handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                              dir_fd=parent)
        before = os.fstat(file_handle)
        require(stat.S_ISREG(before.st_mode) and before.st_mode & 0o444, 'regular readable capture required')
        require(before.st_size <= 64 * 1024 * 1024, 'capture metadata exceeds 64 MiB')
        size = 0
        digest = hashlib.sha256()
        chunks = []
        while True:
            chunk = os.read(file_handle, min(1024 * 1024, 64 * 1024 * 1024 - size + 1))
            if not chunk:
                break
            size += len(chunk)
            require(size <= 64 * 1024 * 1024, 'capture metadata grew beyond 64 MiB')
            digest.update(chunk)
            chunks.append(chunk)
        after = os.fstat(file_handle)
        attached = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(attached.st_mode) and size == before.st_size and
                identity(before) == identity(after) == identity(attached), 'capture file identity changed')
        require(digest.hexdigest() == binding['sha256'], 'capture digest differs')
        for ancestor, part, held, device, inode, mode, uid, gid in reversed(links):
            value = os.stat(part, dir_fd=ancestor, follow_symlinks=False)
            held_value = os.fstat(held)
            require(stat.S_ISDIR(value.st_mode) and
                    (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid) ==
                    (held_value.st_dev, held_value.st_ino, held_value.st_mode, held_value.st_uid, held_value.st_gid) ==
                    (device, inode, mode, uid, gid), 'capture ancestor attachment changed')
        require(identity(os.fstat(file_handle)) == identity(os.stat(parts[-1], dir_fd=parent,
                follow_symlinks=False)) == identity(before), 'capture file changed before return')
        return b''.join(chunks)
    except OSError as error:
        raise ValueError('capture unsafe/unreadable/missing attachment') from error
    finally:
        if file_handle is not None:
            os.close(file_handle)
        for handle in reversed(directories):
            os.close(handle)

CHILD_SEED = r"""
import base64,hashlib,importlib.abc,importlib.util,json,os,sys
try:
    fd=int(sys.argv[1]);expected=sys.argv[2];here=sys.argv[3];parts=[];size=0
    try:
        while True:
            chunk=os.read(fd,min(1024*1024,2*1024*1024-size+1))
            if not chunk:break
            size+=len(chunk)
            if size>2*1024*1024:raise ValueError('bounded bootstrap required')
            parts.append(chunk)
    finally:os.close(fd)
    packed=b''.join(parts)
    if hashlib.sha256(packed).hexdigest()!=expected:raise ValueError('bootstrap capsule differs')
    payload=json.loads(packed)
    if payload['root']!=here or set(payload['modules'])!={'bootstrap','control','framing','composite'}:raise ValueError('bootstrap origin differs')
    value=payload['modules']['bootstrap'];raw=base64.b64decode(value['source_base64'],validate=True)
    if value['path']!=here+'/bootstrap.py' or hashlib.sha256(raw).hexdigest()!=value['sha256']:raise ValueError('bootstrap body differs')
    class SeedLoader(importlib.abc.SourceLoader):
        def get_filename(self,fullname):return value['path']
        def get_data(self,path):
            if path!=value['path']:raise ValueError('bootstrap source locator differs')
            return raw
        def get_code(self,fullname):return compile(raw,value['path'],'exec',dont_inherit=True)
    spec=importlib.util.spec_from_file_location('_cal_captured_SDK_bootstrap',value['path'],loader=SeedLoader())
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    raise SystemExit(module.run(payload,sys.argv[4:]))
except Exception:
    print('{"schema_version":"lab-composite-startup-error/v1-candidate","code":"selected-bootstrap-refused","authority_effect":"none"}',flush=True)
    raise SystemExit(2)
"""

def main():
    p=argparse.ArgumentParser(description='Candidate full34 operator launcher; no network service')
    p.add_argument('--launcher-source-sha256',required=True);p.add_argument('--config',required=True);p.add_argument('--config-sha256',required=True)
    args=p.parse_args()
    try:
        manifest_path=HERE/'source-manifest.json';raw=_capture_exact(ROOT,{'path':str(manifest_path.relative_to(ROOT)),'sha256':args.launcher_source_sha256})
        raw_manifest=raw;manifest=json.loads(raw);need(manifest['authority_effect']=='none')
        captured={}
        for row in manifest['files']:
            relative=Path(row['path']);need(not relative.is_absolute() and '..' not in relative.parts)
            captured[row['path']]=_capture_exact(ROOT,{'path':row['path'],'sha256':row['sha256']})
        control_name=str((HERE/'control.py').relative_to(ROOT));need(control_name in captured)
        # Execute only this already captured, independently pinned control body.
        namespace={'__file__':str(HERE/'control.py'),'__name__':'_T06_verified_launch_control'}
        exec(compile(captured[control_name],str(HERE/'control.py'),'exec'),namespace)
        raw=namespace['public']({'path':str(SELECTION.relative_to(ROOT)),'sha256':SELECTION_SHA});value=json.loads(raw);need(len(value['inputs'])==720 and len(value['original_bindings'])==5)
        expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
        expected.update(value['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755;need(len(expected)==1010)
        namespace['installed'](INSTALL,expected)
        modules={}
        for name in ['bootstrap','control','framing','composite']:
            filename=str((HERE/(name+'.py')).relative_to(ROOT));need(filename in captured)
            body=captured[filename];need(len(body)<=1024*1024)
            modules[name]={'path':str(HERE/(name+'.py')),'sha256':sha(body),'source_base64':base64.b64encode(body).decode('ascii')}
        packet={'schema_version':'lab-captured-SDK-bootstrap/v1-candidate','root':str(HERE),'modules':modules,'manifest':{'path':str(manifest_path),'sha256':args.launcher_source_sha256,'source_base64':base64.b64encode(raw_manifest).decode('ascii')}}
        packed=json.dumps(packet,sort_keys=True,separators=(',',':'),allow_nan=False).encode();need(len(packed)<=2*1024*1024)
        fd=os.memfd_create('cal-T06-captured-public-SDK',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
        try:
            offset=0
            while offset<len(packed):offset+=os.write(fd,packed[offset:])
            os.lseek(fd,0,os.SEEK_SET);fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            cmd=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',CHILD_SEED,str(fd),sha(packed),str(HERE),'--config',args.config,'--config-sha256',args.config_sha256]
            result=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},pass_fds=(fd,))
        finally:os.close(fd)
        for row in manifest['files']:_capture_exact(ROOT,{'path':row['path'],'sha256':row['sha256']})
        namespace['installed'](INSTALL,expected)
        return result.returncode
    except Exception:
        print('{"schema_version":"lab-composite-startup-error/v1-candidate","code":"selected-bootstrap-refused","authority_effect":"none"}',flush=True);return 2
if __name__=='__main__':raise SystemExit(main())
